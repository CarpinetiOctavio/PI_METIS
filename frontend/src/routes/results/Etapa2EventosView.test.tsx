import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderPage } from "../../test/renderPage";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { Etapa2EventosView } from "./Etapa2EventosView";
import type { ContextoSerie } from "../../i18n/periodoRetorno";

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

function montar(contextoSerie?: ContextoSerie) {
  renderPage(
    <Etapa2EventosView
      eventos={EVENTOS}
      puntosEmpiricos={makeEtapa2().puntos_empiricos}
      contextoSerie={contextoSerie}
    />,
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

  // DECISIÓN 076: T queda en años (se ajusta la serie de máximos anuales); lo
  // que cambia con la carga es qué representa el valor y la nota que lo explica.
  it("con carga anual rotula el valor sin agregación y explica que T está en años", () => {
    montar({ resolucion: "anual", mesInicioAnio: 7 });

    expect(screen.getByText("Valor de diseño · T = 2 años")).toBeInTheDocument();
    expect(
      screen.getByText(/^La distribución se ajustó a la serie de máximos anuales, por eso T se mide en años/),
    ).toBeInTheDocument();
  });

  it("con carga mensual nombra el máximo mensual y explica por qué T no está en meses", () => {
    montar({ resolucion: "mensual", mesInicioAnio: 7 });

    expect(
      screen.getByText("Valor de diseño (valor mensual máximo del año) · T = 2 años"),
    ).toBeInTheDocument();
    expect(screen.getByText(/T se mide en años y no en meses/)).toBeInTheDocument();
    expect(screen.getAllByText("Período de retorno T (años, de julio a junio)").length).toBeGreaterThan(0);
  });

  it("con carga diaria de medias lo dice en el rótulo del valor", () => {
    montar({ resolucion: "diaria", mesInicioAnio: 1, variableDiaria: "media" });

    expect(
      screen.getByText("Valor de diseño (media diaria máxima del año) · T = 2 años"),
    ).toBeInTheDocument();
    expect(screen.getByText(/T se mide en años y no en días/)).toBeInTheDocument();
  });
});
