// Escrito ANTES del componente (plan pasada4 §4 B5) — el fondo animado es el
// lugar más probable de reintroducir una fuga de efecto tipo F1
// (docs/frontend/informe-diagnostico-ui-rota.md), y esta vez sería silenciosa:
// la app seguiría funcionando, solo con el doble de loops de rAF corriendo
// para siempre. Mismo patrón que StreamPage.lifecycle.test.tsx.
import { describe, expect, it, vi, beforeEach } from "vitest";
import { StrictMode } from "react";
import { render } from "@testing-library/react";
import { DotFieldBackground } from "./DotFieldBackground";

function mockRaf() {
  let nextId = 0;
  const requested: number[] = [];
  const canceled: number[] = [];
  const rafSpy = vi
    .spyOn(window, "requestAnimationFrame")
    .mockImplementation(() => {
      nextId += 1;
      requested.push(nextId);
      // Deliberadamente no se invoca el callback — un frame real dispararía
      // otro requestAnimationFrame en cascada. Lo que importa acá es cuántos
      // loops quedan PEDIDOS y sin cancelar tras el ciclo de montaje, no
      // simular la animación en sí.
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

describe("DotFieldBackground — ciclo de vida bajo StrictMode", () => {
  beforeEach(() => {
    mockReducedMotion(false);
  });

  it("deja exactamente un loop vivo tras el doble montaje de StrictMode", () => {
    const { requested, canceled } = mockRaf();

    render(
      <StrictMode>
        <DotFieldBackground />
      </StrictMode>,
    );

    expect(requested.length - canceled.length).toBe(1);
  });

  it("cancela el loop al desmontar — cero loops vivos", () => {
    const { requested, canceled } = mockRaf();

    const { unmount } = render(
      <StrictMode>
        <DotFieldBackground />
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
        <DotFieldBackground />
      </StrictMode>,
    );

    expect(rafSpy).not.toHaveBeenCalled();
  });
});
