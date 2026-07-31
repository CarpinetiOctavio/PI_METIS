// Mismo riesgo que DotFieldBackground (ver ese archivo) — no lo asume el
// plan explícitamente para este componente, pero es la misma clase de bug
// (fuga de rAF bajo StrictMode) y el mismo costo de escribirlo.
import { describe, expect, it, vi, beforeEach } from "vitest";
import { StrictMode } from "react";
import { render } from "@testing-library/react";
import { GridScanBackground } from "./GridScanBackground";

function mockRaf() {
  let nextId = 0;
  const requested: number[] = [];
  const canceled: number[] = [];
  const rafSpy = vi
    .spyOn(window, "requestAnimationFrame")
    .mockImplementation(() => {
      nextId += 1;
      requested.push(nextId);
      return nextId;
    });
  vi.spyOn(window, "cancelAnimationFrame").mockImplementation((id: number) => {
    canceled.push(id);
  });
  return { rafSpy, requested, canceled };
}

function mockReducedMotion(reduce: boolean) {
  vi.spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: reduce && query === "(prefers-reduced-motion: reduce)",
      }) as MediaQueryList,
  );
}

describe("GridScanBackground — ciclo de vida bajo StrictMode", () => {
  beforeEach(() => {
    mockReducedMotion(false);
  });

  it("deja exactamente un loop vivo tras el doble montaje de StrictMode", () => {
    const { requested, canceled } = mockRaf();

    render(
      <StrictMode>
        <GridScanBackground />
      </StrictMode>,
    );

    expect(requested.length - canceled.length).toBe(1);
  });

  it("cancela el loop al desmontar — cero loops vivos", () => {
    const { requested, canceled } = mockRaf();

    const { unmount } = render(
      <StrictMode>
        <GridScanBackground />
      </StrictMode>,
    );
    unmount();

    expect(requested.length - canceled.length).toBe(0);
  });

  it("con prefers-reduced-motion no arranca ningún loop", () => {
    mockReducedMotion(true);
    const { rafSpy } = mockRaf();

    render(
      <StrictMode>
        <GridScanBackground />
      </StrictMode>,
    );

    expect(rafSpy).not.toHaveBeenCalled();
  });
});
