// Mismo riesgo que DotFieldBackground/GridScanBackground (fuga de rAF bajo
// StrictMode) + una guarda propia de este componente: WebGL no está
// garantizado (GPU deshabilitada, navegador viejo, o jsdom mismo — ver
// ThreadsBackground.tsx). Sin esa guarda, `new THREE.WebGLRenderer()` tira
// y rompe el render de la puerta de entrada entera.
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render } from "@testing-library/react";
import { ThreadsBackground } from "./ThreadsBackground";

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
  const cafSpy = vi
    .spyOn(window, "cancelAnimationFrame")
    .mockImplementation((id: number) => {
      canceled.push(id);
    });
  return { rafSpy, cafSpy, requested, canceled };
}

function mockReducedMotion(reduce: boolean) {
  vi.spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: reduce && query === "(prefers-reduced-motion: reduce)",
      }) as MediaQueryList,
  );
}

describe("ThreadsBackground — sin WebGL (jsdom real, sin mockear three)", () => {
  beforeEach(() => {
    mockReducedMotion(false);
  });

  it("no rompe el render cuando WebGLRenderer tira (jsdom no tiene WebGL real)", () => {
    const { requested } = mockRaf();

    expect(() => render(<ThreadsBackground />)).not.toThrow();
    // La guarda corta ANTES de pedir cualquier rAF — no hay loop que limpiar.
    expect(requested).toHaveLength(0);
  });

  it("con prefers-reduced-motion tampoco rompe ni pide rAF", () => {
    mockReducedMotion(true);
    const { rafSpy } = mockRaf();

    expect(() => render(<ThreadsBackground />)).not.toThrow();
    expect(rafSpy).not.toHaveBeenCalled();
  });
});
