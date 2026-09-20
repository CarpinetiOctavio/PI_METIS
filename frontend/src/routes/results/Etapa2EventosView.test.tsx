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
  const { container } = renderPage(
    <Etapa2EventosView eventos={EVENTOS} puntosEmpiricos={makeEtapa2().puntos_empiricos} />,
  );
  return container;
}

describe("Etapa2EventosView", () => {
  it("muestra el valor de diseño del período elegido y lo cambia al elegir otro chip", async () => {
    const user = userEvent.setup();
    montar();

    expect(screen.getByText(/T = 2 años/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "100" }));
    expect(screen.getByText(/T = 100 años/)).toBeInTheDocument();
  });

  // El apilado (móvil) o el lado a lado (escritorio, ≥ 1100px) lo decide el CSS
  // con una media query, que jsdom no evalúa: acá se fija la estructura que ese
  // CSS necesita — los dos gráficos hermanos dentro de UN mismo contenedor de
  // grilla, y la card marcada como ensanchable en escritorio.
  it("agrupa los dos gráficos en un solo contenedor de grilla, para que el CSS los ponga lado a lado en escritorio", () => {
    const contenedor = montar().querySelector(".etapa2-eventos__graficos");

    expect(contenedor).not.toBeNull();
    const columnas = contenedor!.querySelectorAll(":scope > .etapa2-eventos__grafico");
    expect(columnas).toHaveLength(2);
    expect(columnas[0]).toHaveTextContent("Gráfico de ajuste");
    expect(columnas[1]).toHaveTextContent("Gráfico de eventos de diseño");
  });

  it("la card se puede ensanchar en escritorio (clase etapa2-ancho)", () => {
    expect(montar().querySelector(".etapa2-eventos")).toHaveClass("etapa2-ancho");
  });
});
