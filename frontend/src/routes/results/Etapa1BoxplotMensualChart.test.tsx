import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Etapa1BoxplotMensualChart } from "./Etapa1BoxplotMensualChart";
import type { Etapa1Datos } from "../../api/types";

function datosMensuales(): Etapa1Datos {
  // 2 años de datos mensuales (2000-2001), valores crecientes por mes
  // para poder distinguir el orden en el eje sin ambigüedad.
  const serie_original: number[] = [];
  const timestamps_originales: Etapa1Datos["timestamps_originales"] = [];
  for (const anio of [2000, 2001]) {
    for (let mes = 1; mes <= 12; mes++) {
      serie_original.push(mes * 10 + (anio - 2000));
      timestamps_originales!.push({
        iso: `${anio}-${String(mes).padStart(2, "0")}-01`,
        anio,
      });
    }
  }
  return {
    resolucion_original: "mensual",
    serie_efectiva: [120, 121],
    timestamps_efectivos: [
      { iso: "2000-01-01", anio: 2000 },
      { iso: "2001-01-01", anio: 2001 },
    ],
    serie_original,
    timestamps_originales,
    indice_atipico: null,
    serie_calendario: null,
  };
}

function datosAnuales(): Etapa1Datos {
  return {
    resolucion_original: "anual",
    serie_efectiva: [94.71, 89.83],
    timestamps_efectivos: [
      { iso: "1980-01-01", anio: 1980 },
      { iso: "1981-01-01", anio: 1981 },
    ],
    serie_original: null,
    timestamps_originales: null,
    indice_atipico: null,
    serie_calendario: null,
  };
}

describe("Etapa1BoxplotMensualChart", () => {
  it("renders nothing for an annual upload — there are no months to group", () => {
    const { container } = render(<Etapa1BoxplotMensualChart datos={datosAnuales()} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders twelve boxes, one per month, grouping two years of data", () => {
    const { container } = render(<Etapa1BoxplotMensualChart datos={datosMensuales()} />);

    expect(
      screen.getByRole("img", { name: "Boxplot mensual de la serie cruda" }),
    ).toBeInTheDocument();

    const boxes = container.querySelectorAll(".box-plot__box");
    expect(boxes).toHaveLength(12);
  });

  it("shows the calendario/configurado order toggle only when mesInicioAnio is set and different from 1", () => {
    const { rerender } = render(<Etapa1BoxplotMensualChart datos={datosMensuales()} />);
    expect(screen.queryByText("Orden de meses")).not.toBeInTheDocument();

    rerender(<Etapa1BoxplotMensualChart datos={datosMensuales()} mesInicioAnio={1} />);
    expect(screen.queryByText("Orden de meses")).not.toBeInTheDocument();

    rerender(<Etapa1BoxplotMensualChart datos={datosMensuales()} mesInicioAnio={7} />);
    expect(screen.getByText("Orden de meses")).toBeInTheDocument();
  });

  it("switching the order toggle reorders the axis without changing the grouped data (still 12 boxes)", () => {
    const { container } = render(
      <Etapa1BoxplotMensualChart datos={datosMensuales()} mesInicioAnio={7} />,
    );

    // .box-plot__tick lo comparten los ticks numéricos del eje Y y los
    // labels de mes — se acota a los <text> dentro de g[data-category].
    function mesesEnOrden(): string[] {
      return Array.from(container.querySelectorAll("g[data-category] > text")).map(
        (t) => t.textContent,
      ) as string[];
    }

    // Por default (mesInicioAnio=7, vista "configurada"): el eje arranca en julio.
    expect(mesesEnOrden()[0]).toBe("Jul");

    fireEvent.click(screen.getByRole("button", { name: "Calendario" }));

    expect(mesesEnOrden()[0]).toBe("Ene");

    // Los datos siguen siendo los mismos 12 meses agrupados, solo cambió
    // el orden — no una re-agregación (a diferencia de serie_calendario).
    expect(container.querySelectorAll(".box-plot__box")).toHaveLength(12);
  });
});
