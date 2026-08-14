import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MotionProvider, useMotion } from "./MotionProvider";

function mockReducedMotion(reduce: boolean) {
  vi.spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: reduce && query === "(prefers-reduced-motion: reduce)",
      }) as MediaQueryList,
  );
}

function Consumer() {
  const { level, effectiveLevel, setLevel, systemForcesReduced } = useMotion();
  return (
    <div>
      <span data-testid="level">{level}</span>
      <span data-testid="effective">{effectiveLevel}</span>
      <span data-testid="forced">{String(systemForcesReduced)}</span>
      <button onClick={() => setLevel("media")}>media</button>
      <button onClick={() => setLevel("off")}>off</button>
    </div>
  );
}

describe("MotionProvider", () => {
  it("defaults to 'alta' when there is no stored preference", () => {
    render(
      <MotionProvider>
        <Consumer />
      </MotionProvider>,
    );
    expect(screen.getByTestId("level")).toHaveTextContent("alta");
    expect(screen.getByTestId("effective")).toHaveTextContent("alta");
    expect(document.documentElement.dataset.motion).toBe("alta");
  });

  it("changes level and persists the choice to localStorage", () => {
    render(
      <MotionProvider>
        <Consumer />
      </MotionProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "media" }));

    expect(screen.getByTestId("level")).toHaveTextContent("media");
    expect(document.documentElement.dataset.motion).toBe("media");
    expect(localStorage.getItem("metis-motion-level")).toBe("media");
  });

  it("reads a stored preference on mount", () => {
    localStorage.setItem("metis-motion-level", "off");

    render(
      <MotionProvider>
        <Consumer />
      </MotionProvider>,
    );

    expect(screen.getByTestId("level")).toHaveTextContent("off");
  });

  // A2 (plan post-avance) — el sistema operativo manda: el nivel efectivo
  // es "off" sin importar lo elegido/guardado, y el provider expone
  // `systemForcesReduced` para que el selector pueda explicarlo.
  it("forces effectiveLevel to 'off' when the OS prefers reduced motion, regardless of the stored level", () => {
    localStorage.setItem("metis-motion-level", "alta");
    mockReducedMotion(true);

    render(
      <MotionProvider>
        <Consumer />
      </MotionProvider>,
    );

    expect(screen.getByTestId("level")).toHaveTextContent("alta");
    expect(screen.getByTestId("effective")).toHaveTextContent("off");
    expect(screen.getByTestId("forced")).toHaveTextContent("true");
    expect(document.documentElement.dataset.motion).toBe("off");
  });
});

describe("useMotion sin <MotionProvider>", () => {
  // A diferencia de useTheme() (lanza si falta el provider), useMotion()
  // degrada a "alta" — lo consumen ampliamente SpotlightCard/Magnet/
  // SpecularHighlight y los tres fondos animados, y sin proveedor debe
  // comportarse exactamente como antes de que este feature existiera.
  it("defaults to 'alta' without throwing", () => {
    expect(() => render(<Consumer />)).not.toThrow();
    expect(screen.getByTestId("level")).toHaveTextContent("alta");
    expect(screen.getByTestId("effective")).toHaveTextContent("alta");
  });
});
