import { describe, expect, it } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import { SpecularHighlight } from "./SpecularHighlight";

describe("SpecularHighlight", () => {
  it("renderiza los hijos", () => {
    const { getByRole } = render(
      <SpecularHighlight>
        <button type="button">Ingresar</button>
      </SpecularHighlight>,
    );

    expect(getByRole("button", { name: "Ingresar" })).toBeInTheDocument();
  });

  it("actualiza --spec-x/--spec-y en mousemove", () => {
    const { container } = render(
      <SpecularHighlight>
        <button type="button">Ingresar</button>
      </SpecularHighlight>,
    );
    const wrapper = container.firstChild as HTMLElement;

    fireEvent.mouseMove(wrapper, { clientX: 20, clientY: 8 });

    // jsdom no calcula layout real (getBoundingClientRect da 0), así que el
    // valor exacto depende de eso — lo que importa es que las custom
    // properties se setean, no el número preciso (eso se verificó en vivo
    // contra un navegador real, ver PR).
    expect(wrapper.style.getPropertyValue("--spec-x")).not.toBe("");
    expect(wrapper.style.getPropertyValue("--spec-y")).not.toBe("");
  });
});
