import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Etapa1SerieTemporalChart } from "./Etapa1SerieTemporalChart";
import type { Etapa1Datos } from "../../api/types";

function datosAnual(): Etapa1Datos {
  return {
    resolucion_original: "anual",
    resolucion_serie_original: "anual",
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
    resolucion_serie_original: "mensual",
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

  it("for a daily upload: shows the toggle and a note that the series is annual maxima from daily data", () => {
    const datos: Etapa1Datos = {
      ...datosMensualConCalendario(),
      resolucion_original: "diaria",
      resolucion_serie_original: "mensual",
    };
    render(<Etapa1SerieTemporalChart datos={datos} />);

    expect(screen.getByText("Criterio de año")).toBeInTheDocument();
    expect(
      screen.getByText(/Máximos anuales agregados desde los datos diarios/),
    ).toBeInTheDocument();
  });

  it("renders nothing when there are no effective timestamps", () => {
    const datos: Etapa1Datos = { ...datosAnual(), timestamps_efectivos: null };
    const { container } = render(<Etapa1SerieTemporalChart datos={datos} />);

    expect(container).toBeEmptyDOMElement();
  });
});

// Bloque G (revisión manual 21/10/2026, D-19): el tooltip rotula el año, no "T"
// (período de retorno), y con un mes de inicio distinto de enero muestra el año
// hidrológico completo en la vista configurada.
function tooltip(container: HTMLElement): string {
  fireEvent.keyDown(screen.getByRole("img", { name: /Serie temporal/ }), { key: "ArrowRight" });
  return container.querySelector(".interactive-chart__tooltip-box")?.textContent ?? "";
}

describe("Etapa1SerieTemporalChart — tooltip del año (D-19)", () => {
  it("con carga anual rotula 'Año = 1980', aunque el mes de inicio configurado no sea enero", () => {
    const { container } = render(<Etapa1SerieTemporalChart datos={datosAnual()} mesInicioAnio={7} />);
    expect(tooltip(container)).toMatch(/^Año = 1980valor = /);
  });

  it("vista configurada con julio: 'Año = 2000-01'; vista calendario: 'Año = 2001'", () => {
    const { container } = render(
      <Etapa1SerieTemporalChart datos={datosMensualConCalendario()} mesInicioAnio={7} />,
    );
    expect(tooltip(container)).toMatch(/^Año = 2000-01valor = /);

    // El foco de teclado sigue al punto siguiente (2001): en calendario, sin sufijo.
    fireEvent.click(screen.getByRole("button", { name: "Calendario" }));
    expect(tooltip(container)).toMatch(/^Año = 2001valor = /);
  });

  it("aclara bajo el selector por qué las dos vistas dan valores distintos", () => {
    render(<Etapa1SerieTemporalChart datos={datosMensualConCalendario()} mesInicioAnio={7} />);
    expect(
      screen.getByText(
        "Cada vista toma el máximo de doce meses distintos, así que un mismo año puede tener valores distintos en una y otra.",
      ),
    ).toBeInTheDocument();
  });
});
