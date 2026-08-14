// Mismo riesgo que DotFieldBackground/GridScanBackground (fuga de rAF bajo
// StrictMode) + una guarda propia de este componente: un contexto 2D no
// está garantizado (navegador sin soporte de canvas, o directamente el
// mock global de vitest.setup.ts deshabilitado a mano — ver el primer test
// de abajo). Sin esa guarda (`if (!ctx) return`), el resto del efecto
// asumiría un contexto válido y rompería el render de la app entera en vez
// de degradar a "sin Threads, los otros fondos siguen andando encima".
//
// DECISIÓN 051: este archivo se conserva sin modificar sus aserciones —
// solo lo que era específico de WebGL (el try/catch de
// `new THREE.WebGLRenderer()`, que tiraba solo porque jsdom no implementa
// WebGL) se adapta a la guarda equivalente de Canvas 2D
// (`getContext("2d")` devolviendo null).
import { describe, expect, it, vi, beforeEach } from "vitest";
import { StrictMode } from "react";
import { render } from "@testing-library/react";
import { ThreadsBackground } from "./ThreadsBackground";
import { MotionProvider } from "../MotionProvider";

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

describe("ThreadsBackground — sin contexto 2D (jsdom real, sin el mock global)", () => {
  beforeEach(() => {
    mockReducedMotion(false);
  });

  it("no rompe el render cuando getContext(\"2d\") devuelve null", () => {
    // vitest.setup.ts mockea getContext("2d") globalmente para que los tres
    // fondos animados no ensucien stderr en el resto de la suite — este
    // test necesita el caso contrario (contexto no disponible) para
    // ejercitar la guarda real del componente, así que lo pisa localmente.
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
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

// Guardas 2 (StrictMode monta dos veces, debe quedar un solo loop vivo) y 4
// (cleanup completo al desmontar) — cubiertas hoy en DotFieldBackground.lifecycle.test.tsx
// y GridScanBackground.lifecycle.test.tsx, pero faltaban acá (B6 del brief
// las exige para los cuatro fondos). Acá el contexto 2D SÍ está disponible
// (el mock global de vitest.setup.ts, sin pisar), así que el componente
// recorre el camino real de dibujo y pide rAF como en producción.
describe("ThreadsBackground — ciclo de vida bajo StrictMode", () => {
  beforeEach(() => {
    mockReducedMotion(false);
  });

  it("deja exactamente un loop vivo tras el doble montaje de StrictMode", () => {
    const { requested, canceled } = mockRaf();

    render(
      <StrictMode>
        <ThreadsBackground />
      </StrictMode>,
    );

    expect(requested.length - canceled.length).toBe(1);
  });

  it("cancela el loop al desmontar — cero loops vivos", () => {
    const { requested, canceled } = mockRaf();

    const { unmount } = render(
      <StrictMode>
        <ThreadsBackground />
      </StrictMode>,
    );
    unmount();

    expect(requested.length - canceled.length).toBe(0);
  });
});

// A2/A3 (plan post-avance) — RootLayout ya no monta este fondo con nivel
// "off" (ver RootLayout.test.tsx), pero el hook subyacente también trata
// motionLevel === "off" como reduced-motion por las suyas (defensa en
// profundidad, ver useCanvasAnimationLoop.ts) — se verifica acá
// directamente, sin pasar por RootLayout.
describe("ThreadsBackground — nivel de movimiento 'off' (defensa en profundidad)", () => {
  beforeEach(() => {
    mockReducedMotion(false);
    localStorage.setItem("metis-motion-level", "off");
  });

  it("no arranca ningún loop aunque el sistema no pida movimiento reducido", () => {
    const { rafSpy } = mockRaf();

    render(
      <StrictMode>
        <MotionProvider>
          <ThreadsBackground />
        </MotionProvider>
      </StrictMode>,
    );

    expect(rafSpy).not.toHaveBeenCalled();
  });
});
