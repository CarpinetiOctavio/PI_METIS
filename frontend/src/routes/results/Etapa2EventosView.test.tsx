import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderPage } from "../../test/renderPage";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { Etapa2EventosView } from "./Etapa2EventosView";

const EVENTOS = {
  distribucion: "gumbel",
  metodo: "momentos",
  eventos_diseno: [
    { periodo_retorno: 2, valor: 108.4 },
    { periodo_retorno: 100, valor: 312.7 },
  ],
  curva_ajuste: [
    { periodo_retorno: 1.05, valor: 55.0 },
    { periodo_retorno: 100, valor: 312.7 },
  ],
};

function montar() {
  renderPage(
    <Etapa2EventosView eventos={EVENTOS} puntosEmpiricos={makeEtapa2().puntos_empiricos} />,
  );
}

describe("Etapa2EventosView", () => {
  it("muestra el valor de diseño del período elegido y lo cambia al elegir otro chip", async () => {
    const user = userEvent.setup();
    montar();

    expect(screen.getByText(/T = 2 años/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "100" }));
    expect(screen.getByText(/T = 100 años/)).toBeInTheDocument();
  });
});
