// Ver el comentario largo en CountUp.tsx: el texto real (accesible,
// testeable) tiene que mostrar el valor final YA, sin esperar ningún frame
// de animación — dos tests reales de StreamPage.integration.test.tsx
// chequean texto formateado de forma síncrona, sin waitFor, y un conteo que
// reemplazara el texto los rompería siempre por carrera de tiempos. Este
// archivo prueba esa propiedad directamente, más el mismo riesgo de fuga de
// rAF que los fondos animados (B5).
import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { CountUp } from "./CountUp";

function mockRaf() {
  let nextId = 0;
  const requested: number[] = [];
  const canceled: number[] = [];
  vi.spyOn(window, "requestAnimationFrame").mockImplementation(() => {
    nextId += 1;
    requested.push(nextId);
    return nextId;
  });
  vi.spyOn(window, "cancelAnimationFrame").mockImplementation((id: number) => {
    canceled.push(id);
  });
  return { requested, canceled };
}

function mockReducedMotion(reduce: boolean) {
  vi.spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: reduce && query === "(prefers-reduced-motion: reduce)",
      }) as MediaQueryList,
  );
}

describe("CountUp", () => {
  it("muestra el valor final formateado de inmediato, antes de cualquier frame", () => {
    mockReducedMotion(false);
    mockRaf();

    const { container } = render(<CountUp value={0.22} />);

    // Sin await, sin waitFor — exactamente la forma en que
    // StreamPage.integration.test.tsx lo chequea de verdad.
    expect(container).toHaveTextContent("0,22000");
  });

  it("con null/undefined muestra el placeholder de ausencia, sin arrancar rAF", () => {
    mockReducedMotion(false);
    const { requested } = mockRaf();

    const { container } = render(<CountUp value={null} />);

    expect(container).toHaveTextContent("—");
    expect(requested).toHaveLength(0);
  });

  it("con prefers-reduced-motion no arranca ningún loop", () => {
    mockReducedMotion(true);
    const { requested } = mockRaf();

    render(<CountUp value={245.7} />);

    expect(requested).toHaveLength(0);
  });

  it("cancela el loop al desmontar — cero loops vivos", () => {
    mockReducedMotion(false);
    const { requested, canceled } = mockRaf();

    const { unmount } = render(<CountUp value={245.7} />);
    unmount();

    expect(requested.length - canceled.length).toBe(0);
  });
});
