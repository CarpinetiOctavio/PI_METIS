import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Etapa1SerieTemporalChart } from "./Etapa1SerieTemporalChart";
import type { Etapa1Datos } from "../../api/types";

function datosAnual(): Etapa1Datos {
  return {
    resolucion_original: "anual",
    serie_efectiva: [94.71, 89.83, 105.13],
    timestamps_efectivos: [
      { iso: "1980-01-01", anio: 1980 },
      { iso: "1981-01-01", anio: 1981 },
      { iso: "1982-01-01", anio: 1982 },
    ],
    serie_original: null,
    timestamps_originales: null,
    indice_atipico: null,
    serie_calendario: null,
  };
}

function datosMensualConCalendario(): Etapa1Datos {
  return {
    resolucion_original: "mensual",
    serie_efectiva: [94.71, 89.83],
    timestamps_efectivos: [
      { iso: "2000-01-01", anio: 2000 },
      { iso: "2001-01-01", anio: 2001 },
    ],
    serie_original: [1, 2, 3],
    timestamps_originales: [{ iso: "2000-01-01", anio: 2000 }],
    indice_atipico: null,
    serie_calendario: {
      serie: [90, 95, 100],
      timestamps: [
        { iso: "2000-01-01", anio: 2000 },
        { iso: "2001-01-01", anio: 2001 },
        { iso: "2002-01-01", anio: 2002 },
      ],
    },
  };
}

describe("Etapa1SerieTemporalChart", () => {
  it("renders the effective series without a toggle when the upload was annual", () => {
    const { container } = render(<Etapa1SerieTemporalChart datos={datosAnual()} />);

    expect(screen.getByRole("img", { name: /Serie temporal/ })).toBeInTheDocument();
    expect(screen.queryByText("Criterio de año")).not.toBeInTheDocument();
    const puntos = container.querySelector('g[data-series="puntos"]');
    expect(puntos?.querySelectorAll("circle")).toHaveLength(3);
  });

  it("shows the toggle only when the upload was monthly and serie_calendario is present, and switching it swaps the plotted series", () => {
    const { container } = render(
      <Etapa1SerieTemporalChart datos={datosMensualConCalendario()} />,
    );

    expect(screen.getByRole("button", { name: "Configurado" })).toBeInTheDocument();
    const calendarioBtn = screen.getByRole("button", { name: "Calendario" });
    expect(calendarioBtn).toBeInTheDocument();

    // Por default, la vista "configurada" — 2 puntos (serie_efectiva).
    let puntos = container.querySelector('g[data-series="puntos"]');
    expect(puntos?.querySelectorAll("circle")).toHaveLength(2);
    expect(
      screen.queryByText(/Vista comparativa/),
    ).not.toBeInTheDocument();

    fireEvent.click(calendarioBtn);

    // serie_calendario tiene 3 puntos, distinto largo de serie_efectiva —
    // exactamente el caso que motivó que viaje con sus propios timestamps.
    puntos = container.querySelector('g[data-series="puntos"]');
    expect(puntos?.querySelectorAll("circle")).toHaveLength(3);
    expect(screen.getByText(/Vista comparativa/)).toBeInTheDocument();
  });

  it("does not render a toggle for a monthly upload without serie_calendario (mes_inicio_anio already 1)", () => {
    const datos: Etapa1Datos = { ...datosMensualConCalendario(), serie_calendario: null };
    render(<Etapa1SerieTemporalChart datos={datos} />);

    expect(screen.queryByText("Criterio de año")).not.toBeInTheDocument();
  });

  it("renders nothing when there are no effective timestamps", () => {
    const datos: Etapa1Datos = { ...datosAnual(), timestamps_efectivos: null };
    const { container } = render(<Etapa1SerieTemporalChart datos={datos} />);

    expect(container).toBeEmptyDOMElement();
  });
});
