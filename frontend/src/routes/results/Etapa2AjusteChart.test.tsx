import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Etapa2AjusteChart } from "./Etapa2AjusteChart";

describe("Etapa2AjusteChart", () => {
  it("renders one marker per punto empírico and a curve point per valor no nulo", () => {
    const { container } = render(
      <Etapa2AjusteChart
        distribucion="gumbel"
        metodo="momentos"
        puntosEmpiricos={[
          { valor: 142.5, periodo_retorno: 41, probabilidad: 0.9756 },
          { valor: 98.1, periodo_retorno: 20.5, probabilidad: 0.9512 },
        ]}
        curvaAjuste={[
          { periodo_retorno: 2, valor: 90 },
          { periodo_retorno: 10, valor: 120 },
          { periodo_retorno: 100, valor: null },
        ]}
      />,
    );

    expect(
      screen.getByRole("img", {
        name: /Gráfico de ajuste.*gumbel.*momentos/,
      }),
    ).toBeInTheDocument();

    const markers = container.querySelector('g[data-series="empiricos"]');
    expect(markers?.querySelectorAll("circle")).toHaveLength(2);

    // El punto con valor null se descarta antes de llegar al generador de
    // curva — d3-shape no debe intentar dibujar un punto sin valor.
    const path = container.querySelector('path[data-series="curva"]');
    expect(path?.getAttribute("d")).toBeTruthy();
  });

  it("does not crash with an empty curve or empty empirical points", () => {
    render(
      <Etapa2AjusteChart
        distribucion="gumbel"
        metodo="momentos"
        puntosEmpiricos={[]}
        curvaAjuste={[]}
      />,
    );

    expect(screen.getByRole("img")).toBeInTheDocument();
  });
});
