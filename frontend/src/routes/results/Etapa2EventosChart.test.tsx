import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Etapa2EventosChart } from "./Etapa2EventosChart";

describe("Etapa2EventosChart", () => {
  it("renders one marker per período de retorno pedido y descarta valores null", () => {
    const { container } = render(
      <Etapa2EventosChart
        eventosDiseno={[
          { periodo_retorno: 2, valor: 90 },
          { periodo_retorno: 500, valor: null },
        ]}
        curvaAjuste={[
          { periodo_retorno: 1.5, valor: 60 },
          { periodo_retorno: 500, valor: 400 },
        ]}
      />,
    );

    expect(
      screen.getByRole("img", { name: /eventos de diseño/i }),
    ).toBeInTheDocument();

    const markers = container.querySelector('g[data-series="eventos"]');
    // El evento con valor null (T=500 falló para esta distribución) no se
    // dibuja — core/etapa2/design_events.py ya lo registra como null y acá
    // no se lo puede plotear.
    expect(markers?.querySelectorAll("circle")).toHaveLength(1);

    const path = container.querySelector('path[data-series="curva"]');
    expect(path?.getAttribute("d")).toBeTruthy();
  });

  it("F4 — resalta el marcador del período de retorno seleccionado y lo anuncia en el aria-label", () => {
    const { container } = render(
      <Etapa2EventosChart
        eventosDiseno={[
          { periodo_retorno: 2, valor: 90 },
          { periodo_retorno: 10, valor: 140 },
          { periodo_retorno: 100, valor: 210 },
        ]}
        curvaAjuste={[
          { periodo_retorno: 1.5, valor: 60 },
          { periodo_retorno: 500, valor: 400 },
        ]}
        periodoResaltado={10}
      />,
    );

    const marcadores = Array.from(
      container.querySelectorAll('g[data-series="eventos"] circle'),
    );
    const resaltados = marcadores.filter(
      (c) => c.getAttribute("data-highlighted") === "true",
    );
    expect(resaltados).toHaveLength(1);

    const normal = Number(
      marcadores.find((c) => !c.hasAttribute("data-highlighted"))?.getAttribute("r"),
    );
    const resaltado = Number(resaltados[0].getAttribute("r"));
    expect(resaltado).toBeGreaterThan(normal);
    expect(
      (resaltados[0] as SVGElement).style.fill.includes("--acc-hi"),
    ).toBe(true);

    expect(
      screen.getByRole("img", { name: /resaltado: T = 10 años/i }),
    ).toBeInTheDocument();
  });
});
