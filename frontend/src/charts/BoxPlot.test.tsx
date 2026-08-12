import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BoxPlot } from "./BoxPlot";
import type { BoxPlotCategory } from "./BoxPlot";

function categories(): BoxPlotCategory[] {
  return [
    { label: "Ene", stats: { min: 10, q1: 20, mediana: 25, q3: 30, max: 40 } },
    { label: "Feb", stats: null },
    { label: "Mar", stats: { min: 5, q1: 15, mediana: 18, q3: 22, max: 30 } },
  ];
}

describe("BoxPlot", () => {
  it("renders one box (rect) per category with stats, and skips categories without data", () => {
    const { container } = render(
      <BoxPlot categories={categories()} ariaLabel="Boxplot de prueba" yLabel="Valor" />,
    );

    expect(screen.getByRole("img", { name: "Boxplot de prueba" })).toBeInTheDocument();

    const conCaja = container.querySelector('g[data-category="Ene"]');
    expect(conCaja?.querySelector(".box-plot__box")).toBeInTheDocument();

    const sinDatos = container.querySelector('g[data-category="Feb"]');
    expect(sinDatos?.querySelector(".box-plot__box")).not.toBeInTheDocument();

    // Los tres labels de mes se muestran siempre, con o sin datos.
    expect(screen.getByText("Ene")).toBeInTheDocument();
    expect(screen.getByText("Feb")).toBeInTheDocument();
    expect(screen.getByText("Mar")).toBeInTheDocument();
  });

  it("shows the five statistics in a tooltip on hover", () => {
    const { container } = render(
      <BoxPlot categories={categories()} ariaLabel="Boxplot de prueba" yLabel="Valor" />,
    );

    const enero = container.querySelector('g[data-category="Ene"] .box-plot__hit') as Element;
    fireEvent.mouseEnter(enero);

    const tooltip = container.querySelector(".box-plot__tooltip-box");
    expect(tooltip).toBeInTheDocument();
    expect(tooltip?.textContent).toContain("máx = 40");
    expect(tooltip?.textContent).toContain("Q3 = 30");
    expect(tooltip?.textContent).toContain("mediana = 25");
    expect(tooltip?.textContent).toContain("Q1 = 20");
    expect(tooltip?.textContent).toContain("mín = 10");

    fireEvent.mouseLeave(enero);
    expect(container.querySelector(".box-plot__tooltip-box")).not.toBeInTheDocument();
  });

  it("renders without crashing when no category has data", () => {
    const vacias: BoxPlotCategory[] = [
      { label: "Ene", stats: null },
      { label: "Feb", stats: null },
    ];
    render(<BoxPlot categories={vacias} ariaLabel="Vacío" yLabel="Valor" />);

    expect(screen.getByRole("img", { name: "Vacío" })).toBeInTheDocument();
  });
});
