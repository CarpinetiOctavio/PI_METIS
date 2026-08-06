import { describe, expect, it, vi } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import { gsap } from "gsap";
import { Magnet } from "./Magnet";

function mockReducedMotion(reduce: boolean) {
  vi.spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: reduce && query === "(prefers-reduced-motion: reduce)",
      }) as MediaQueryList,
  );
}

describe("Magnet", () => {
  it("renderiza los hijos sin envolverlos en ningún elemento con foco propio", () => {
    const { getByRole } = render(
      <Magnet>
        <button type="button">Ingresar</button>
      </Magnet>,
    );

    expect(getByRole("button", { name: "Ingresar" })).toBeInTheDocument();
  });

  it("con prefers-reduced-motion, moverse cerca del elemento no llama a gsap.to", () => {
    mockReducedMotion(true);
    const gsapToSpy = vi.spyOn(gsap, "to");

    const { container } = render(
      <Magnet>
        <button type="button">Ingresar</button>
      </Magnet>,
    );
    fireEvent.mouseMove(container.firstChild as Element, { clientX: 10, clientY: 10 });

    expect(gsapToSpy).not.toHaveBeenCalled();
  });

  it("sin prefers-reduced-motion, moverse cerca del elemento llama a gsap.to", () => {
    mockReducedMotion(false);
    const gsapToSpy = vi.spyOn(gsap, "to");

    const { container } = render(
      <Magnet>
        <button type="button">Ingresar</button>
      </Magnet>,
    );
    // jsdom da getBoundingClientRect() = todo 0 — cualquier punto cae
    // "dentro" del radio, alcanza para disparar la rama que llama a gsap.
    fireEvent.mouseMove(container.firstChild as Element, { clientX: 10, clientY: 10 });

    expect(gsapToSpy).toHaveBeenCalled();
  });

  it("al salir, vuelve a x:0/y:0 con gsap.to", () => {
    mockReducedMotion(false);
    const gsapToSpy = vi.spyOn(gsap, "to");

    const { container } = render(
      <Magnet>
        <button type="button">Ingresar</button>
      </Magnet>,
    );
    fireEvent.mouseLeave(container.firstChild as Element);

    expect(gsapToSpy).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ x: 0, y: 0 }),
    );
  });
});
