import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { InteractiveChart } from "./InteractiveChart";
import type { ChartSeries } from "./InteractiveChart";

// jsdom no calcula layout real — getBoundingClientRect() da todo 0 por
// default (mismo obstáculo que Magnet.test.tsx). Acá sí importa el tamaño
// real porque el componente convierte clientX a coordenadas del viewBox
// (640×320) proporcionalmente al rect — se mockea 1:1 con VIEW_W/height
// para poder calcular a mano el clientX de cada punto.
function mockChartRect() {
  vi.spyOn(Element.prototype, "getBoundingClientRect").mockReturnValue({
    left: 0,
    top: 0,
    width: 640,
    height: 320,
    right: 640,
    bottom: 320,
    x: 0,
    y: 0,
    toJSON() {
      return this;
    },
  } as DOMRect);
}

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
});
