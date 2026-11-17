import { describe, expect, it } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import { SpotlightCard } from "./SpotlightCard";

describe("SpotlightCard", () => {
  it("renderiza los hijos dentro de un .card real, con la clase extra pedida", () => {
    const { container, getByText } = render(
      <SpotlightCard className="history-item">
        <p>Contenido de la tarjeta</p>
      </SpotlightCard>,
    );

    expect(getByText("Contenido de la tarjeta")).toBeInTheDocument();
    const card = container.querySelector(".card");
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass("history-item", "spotlight-card");
  });

  it("el brillo es un <div> real, no un ::before que .card ya usa para el corchete decorativo", () => {
    // Bug encontrado en la exploración (ronda 1): .card::before ya existe
    // (global.css, corchete de esquina) — si el brillo hubiera reutilizado
    // ese pseudo-elemento, el width/height fijo del corchete le hubiera
    // ganado al del brillo. Este test protege contra reintroducir ese bug.
    const { container } = render(
      <SpotlightCard>
        <p>Contenido</p>
      </SpotlightCard>,
    );

    expect(container.querySelector(".spotlight-card__glow")).toBeInTheDocument();
  });

  it("actualiza --spot-x/--spot-y en mousemove", () => {
    const { container } = render(
      <SpotlightCard>
        <p>Contenido</p>
      </SpotlightCard>,
    );
    const card = container.querySelector(".card") as HTMLElement;

    fireEvent.mouseMove(card, { clientX: 30, clientY: 12 });

    expect(card.style.getPropertyValue("--spot-x")).not.toBe("");
    expect(card.style.getPropertyValue("--spot-y")).not.toBe("");
  });
});
