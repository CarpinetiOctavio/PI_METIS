import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { InteractiveChart } from "./InteractiveChart";
import type { ChartSeries } from "./InteractiveChart";
import { mockChartRect } from "../test/chartRect";

const MARGIN_LEFT = 60;

function series(): ChartSeries[] {
  return [
    {
      id: "curva",
      kind: "line",
      label: "Curva ajustada",
      colorVar: "--acc",
      data: [
        { x: 10, y: 20 },
        { x: 100, y: 80 },
      ],
    },
    {
      id: "marcadores",
      kind: "points",
      label: "Períodos pedidos",
      colorVar: "--acc2",
      data: [
        { x: 30, y: 40 },
        { x: 70, y: 65 },
      ],
    },
  ];
}

// Calculado a mano contra scaleLog().domain([9.5238, 105]).range([0, 564])
// (VIEW_W=640, MARGIN.left=60, MARGIN.right=16) — ver InteractiveChart.tsx.
const PLOT_X_30 = 269.6;
const PLOT_X_70 = 468.7;

function clientXFor(plotX: number): number {
  return MARGIN_LEFT + plotX;
}

describe("InteractiveChart", () => {
  beforeEach(() => {
    mockChartRect();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the line and the point markers as real SVG elements", () => {
    const { container } = render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    expect(
      screen.getByRole("img", { name: "Gráfico de prueba" }),
    ).toBeInTheDocument();

    const path = container.querySelector('path[data-series="curva"]');
    expect(path).toBeInTheDocument();
    expect(path?.getAttribute("d")).toBeTruthy();

    const markerGroup = container.querySelector('g[data-series="marcadores"]');
    expect(markerGroup?.querySelectorAll("circle")).toHaveLength(2);
  });

  it("F4 — highlight() marks exactly one point bigger and with --acc-hi, defaults untouched", () => {
    const base = series();
    const withHighlight: ChartSeries[] = [
      base[0],
      { ...base[1], highlight: (p) => p.x === 70 },
    ];
    const { container } = render(
      <InteractiveChart
        series={withHighlight}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const circles = Array.from(
      container.querySelectorAll('g[data-series="marcadores"] circle'),
    ) as SVGCircleElement[];
    const resaltados = circles.filter(
      (c) => c.getAttribute("data-highlighted") === "true",
    );
    expect(resaltados).toHaveLength(1);

    const normal = circles.find((c) => !c.hasAttribute("data-highlighted"))!;
    expect(Number(resaltados[0].getAttribute("r"))).toBeGreaterThan(
      Number(normal.getAttribute("r")),
    );
    // el punto normal conserva su colorVar; el resaltado usa --acc-hi
    expect(normal.style.fill).toBe("var(--acc2)");
    expect(resaltados[0].style.fill).toBe("var(--acc-hi)");
  });

  it("renders a dashed line series with stroke-dasharray, solid ones without", () => {
    const { container } = render(
      <InteractiveChart
        series={[
          { id: "datos", kind: "line", label: "Datos", colorVar: "--acc", data: [
            { x: 10, y: 20 },
            { x: 100, y: 80 },
          ] },
          { id: "umbral", kind: "line", label: "Umbral", colorVar: "--mut", dashed: true, data: [
            { x: 10, y: 50 },
            { x: 100, y: 50 },
          ] },
        ]}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const solida = container.querySelector('path[data-series="datos"]') as SVGPathElement;
    const punteada = container.querySelector('path[data-series="umbral"]') as SVGPathElement;
    expect(solida.style.strokeDasharray).toBe("");
    expect(punteada.style.strokeDasharray).not.toBe("");
  });

  it("shows a tooltip with the exact (x, y) of the nearest point on hover", () => {
    const { container } = render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const capture = container.querySelector(".interactive-chart__capture");
    expect(capture).toBeInTheDocument();
    fireEvent.mouseMove(capture as Element, { clientX: clientXFor(PLOT_X_30) });

    const tooltip = container.querySelector(".interactive-chart__tooltip");
    expect(tooltip).toBeInTheDocument();
    expect(within(tooltip as HTMLElement).getByText("T = 30")).toBeInTheDocument();
    expect(
      within(tooltip as HTMLElement).getByText("valor = 40"),
    ).toBeInTheDocument();
  });

  it("wheel zoom narrows the domain, and the reset button reverts it", () => {
    render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const svg = screen.getByRole("img", { name: "Gráfico de prueba" });
    const reset = screen.getByRole("button", { name: "Restablecer zoom" });
    expect(reset).toBeDisabled();

    fireEvent.wheel(svg, { clientX: clientXFor(PLOT_X_30), deltaY: -100 });
    expect(reset).toBeEnabled();

    fireEvent.click(reset);
    expect(reset).toBeDisabled();
  });

  it("drag-select over the capture surface zooms to the selected range", () => {
    const { container } = render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const capture = container.querySelector(".interactive-chart__capture") as Element;
    const reset = screen.getByRole("button", { name: "Restablecer zoom" });
    expect(reset).toBeDisabled();

    fireEvent.mouseDown(capture, { clientX: clientXFor(PLOT_X_30) });
    fireEvent.mouseMove(capture, { clientX: clientXFor(PLOT_X_70) });
    fireEvent.mouseUp(capture);

    expect(reset).toBeEnabled();
  });

  it("a short drag (below the pixel threshold) does not trigger a zoom", () => {
    const { container } = render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const capture = container.querySelector(".interactive-chart__capture") as Element;
    const reset = screen.getByRole("button", { name: "Restablecer zoom" });

    fireEvent.mouseDown(capture, { clientX: clientXFor(PLOT_X_30) });
    fireEvent.mouseMove(capture, { clientX: clientXFor(PLOT_X_30) + 2 });
    fireEvent.mouseUp(capture);

    expect(reset).toBeDisabled();
  });

  it("ArrowRight/ArrowLeft move the tooltip between markers, sorted by x", () => {
    const { container } = render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const svg = screen.getByRole("img", { name: "Gráfico de prueba" });

    fireEvent.keyDown(svg, { key: "ArrowRight" });
    let tooltip = container.querySelector(".interactive-chart__tooltip");
    expect(within(tooltip as HTMLElement).getByText("T = 30")).toBeInTheDocument();

    fireEvent.keyDown(svg, { key: "ArrowRight" });
    tooltip = container.querySelector(".interactive-chart__tooltip");
    expect(within(tooltip as HTMLElement).getByText("T = 70")).toBeInTheDocument();

    fireEvent.keyDown(svg, { key: "ArrowLeft" });
    tooltip = container.querySelector(".interactive-chart__tooltip");
    expect(within(tooltip as HTMLElement).getByText("T = 30")).toBeInTheDocument();
  });

  it("Home/End jump to the first/last marker", () => {
    const { container } = render(
      <InteractiveChart
        series={series()}
        ariaLabel="Gráfico de prueba"
        xLabel="T"
        yLabel="Valor"
      />,
    );

    const svg = screen.getByRole("img", { name: "Gráfico de prueba" });

    fireEvent.keyDown(svg, { key: "End" });
    let tooltip = container.querySelector(".interactive-chart__tooltip");
    expect(within(tooltip as HTMLElement).getByText("T = 70")).toBeInTheDocument();

    fireEvent.keyDown(svg, { key: "Home" });
    tooltip = container.querySelector(".interactive-chart__tooltip");
    expect(within(tooltip as HTMLElement).getByText("T = 30")).toBeInTheDocument();
  });

  it("renders without crashing when a series has no data", () => {
    const empty: ChartSeries[] = [
      { id: "curva", kind: "line", label: "Curva", colorVar: "--acc", data: [] },
      { id: "marcadores", kind: "points", label: "Marcadores", colorVar: "--acc2", data: [] },
    ];
    render(
      <InteractiveChart series={empty} ariaLabel="Vacío" xLabel="T" yLabel="Valor" />,
    );

    expect(screen.getByRole("img", { name: "Vacío" })).toBeInTheDocument();
  });

  // PR 4 del plan de cierre de pendientes no-test — xScale="linear" para
  // los gráficos de Etapa 1 con eje de año. Años reales están MUY cerca en
  // términos de razón (2010/2000 ≈ 1.005, muy por debajo de MIN_SPAN_RATIO
  // = 1.05): el guard de span mínimo de la escala log, aplicado sin
  // querer a un eje lineal, habría rechazado CUALQUIER zoom por selección
  // sobre un rango de años — incluso el dominio completo. Este test falla
  // si spanTooSmall() no se bifurca por escala.
  describe("xScale=\"linear\"", () => {
    function serieAnual(): ChartSeries[] {
      return [
        {
          id: "serie",
          kind: "points",
          label: "Serie",
          colorVar: "--acc",
          data: [
            { x: 2000, y: 10 },
            { x: 2010, y: 20 },
          ],
        },
      ];
    }

    it("renders with a linear x-axis and shows the exact year in the tooltip", () => {
      const { container } = render(
        <InteractiveChart
          series={serieAnual()}
          xScale="linear"
          ariaLabel="Serie anual"
          xLabel="Año"
          yLabel="Valor"
        />,
      );

      // Dominio con padding lineal: [1999.5, 2010.5], span=11.
      // plotX(2000) = (2000-1999.5)/11 * 564 ≈ 25.6
      const capture = container.querySelector(".interactive-chart__capture") as Element;
      fireEvent.mouseMove(capture, { clientX: clientXFor(25.6) });

      const tooltip = container.querySelector(".interactive-chart__tooltip");
      expect(tooltip).toBeInTheDocument();
      expect(within(tooltip as HTMLElement).getByText("T = 2000")).toBeInTheDocument();
    });

    it("drag-select over a close-together year range still zooms (ratio-based guard would reject it)", () => {
      const { container } = render(
        <InteractiveChart
          series={serieAnual()}
          xScale="linear"
          ariaLabel="Serie anual"
          xLabel="Año"
          yLabel="Valor"
        />,
      );

      const capture = container.querySelector(".interactive-chart__capture") as Element;
      const reset = screen.getByRole("button", { name: "Restablecer zoom" });
      expect(reset).toBeDisabled();

      // Selección de casi todo el ancho del plot — en escala log, la razón
      // hi/lo de este rango de años (≈1.005) está muy por debajo de 1.05 y
      // el zoom quedaría siempre rechazado.
      fireEvent.mouseDown(capture, { clientX: clientXFor(10) });
      fireEvent.mouseMove(capture, { clientX: clientXFor(550) });
      fireEvent.mouseUp(capture);

      expect(reset).toBeEnabled();
    });
  });
});

// Ítem A (excluir atípicos): activar un marcador con clic o con el teclado, y
// dibujar como huecos los marcados.
describe("InteractiveChart — activar y marcar puntos", () => {
  // El componente convierte clientX/clientY al viewBox con los márgenes reales
  // (left 88, top 12 — InteractiveChart.tsx); el rect mockeado es 1:1.
  const MARGEN = { left: 88, top: 12 };

  beforeEach(() => {
    mockChartRect();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  function serieAnualConIds(): ChartSeries[] {
    return [
      {
        id: "puntos",
        kind: "points",
        label: "Serie",
        colorVar: "--acc",
        data: [
          { x: 2000, y: 10, id: 0 },
          { x: 2005, y: 50, id: 1 },
          { x: 2010, y: 20, id: 2 },
        ],
      },
    ];
  }

  function montar(props: Partial<React.ComponentProps<typeof InteractiveChart>> = {}) {
    const onPointActivate = vi.fn();
    const { container } = render(
      <InteractiveChart
        series={serieAnualConIds()}
        xScale="linear"
        ariaLabel="Serie anual"
        xLabel="Año"
        yLabel="Valor"
        onPointActivate={onPointActivate}
        {...props}
      />,
    );
    const capture = container.querySelector(".interactive-chart__capture") as Element;
    const circulos = Array.from(container.querySelectorAll("circle.interactive-chart__point"));
    // Posición en pantalla del marcador i-ésimo: su cx/cy (coordenadas del
    // gráfico) más el margen del viewBox.
    const posicion = (i: number) => ({
      clientX: MARGEN.left + Number(circulos[i].getAttribute("cx")),
      clientY: MARGEN.top + Number(circulos[i].getAttribute("cy")),
    });
    return { container, capture, circulos, posicion, onPointActivate };
  }

  it("un clic sobre un marcador llama a onPointActivate con ese punto (y su id) y su serie", () => {
    const { capture, posicion, onPointActivate } = montar();

    fireEvent.mouseDown(capture, posicion(1));
    fireEvent.mouseUp(capture, posicion(1));

    expect(onPointActivate).toHaveBeenCalledTimes(1);
    const [punto, serie] = onPointActivate.mock.calls[0];
    expect(punto).toEqual({ x: 2005, y: 50, id: 1 });
    expect(serie.id).toBe("puntos");
  });

  it("un clic lejos de todo marcador no activa nada", () => {
    const { capture, posicion, onPointActivate } = montar();
    const { clientX, clientY } = posicion(1);

    fireEvent.mouseDown(capture, { clientX, clientY: clientY + 90 });
    fireEvent.mouseUp(capture, { clientX, clientY: clientY + 90 });

    expect(onPointActivate).not.toHaveBeenCalled();
  });

  it("un arrastre para hacer zoom no cuenta como clic sobre el marcador", () => {
    const { capture, posicion, onPointActivate } = montar();

    fireEvent.mouseDown(capture, posicion(0));
    fireEvent.mouseMove(capture, posicion(2));
    fireEvent.mouseUp(capture, posicion(2));

    expect(onPointActivate).not.toHaveBeenCalled();
  });

  it.each([["Enter"], [" "]])(
    "con el marcador enfocado por teclado, %j lo activa; sin foco no hace nada",
    (tecla) => {
      const { onPointActivate } = montar();
      const svg = screen.getByRole("img", { name: "Serie anual" });

      fireEvent.keyDown(svg, { key: tecla });
      expect(onPointActivate).not.toHaveBeenCalled();

      fireEvent.keyDown(svg, { key: "ArrowRight" });
      fireEvent.keyDown(svg, { key: "ArrowRight" });
      fireEvent.keyDown(svg, { key: tecla });
      expect(onPointActivate).toHaveBeenCalledTimes(1);
      expect(onPointActivate.mock.calls[0][0]).toMatchObject({ x: 2005, id: 1 });
    },
  );

  it("sin onPointActivate el clic no rompe nada", () => {
    const { capture, posicion } = montar({ onPointActivate: undefined });

    expect(() => {
      fireEvent.mouseDown(capture, posicion(0));
      fireEvent.mouseUp(capture, posicion(0));
    }).not.toThrow();
  });

  it("marked() dibuja hueco solo los puntos marcados, con el anillo del color de la serie", () => {
    const serie = serieAnualConIds();
    serie[0].marked = (p) => p.id === 1;
    const { circulos } = montar({ series: serie });

    expect(circulos.map((c) => c.hasAttribute("data-marked"))).toEqual([false, true, false]);
    const hueco = circulos[1] as SVGCircleElement;
    expect(hueco.style.fill).toBe("var(--surf2)");
    expect(hueco.style.stroke).toBe("var(--acc)");
    expect((circulos[0] as SVGCircleElement).style.fill).toBe("var(--acc)");
  });
});
