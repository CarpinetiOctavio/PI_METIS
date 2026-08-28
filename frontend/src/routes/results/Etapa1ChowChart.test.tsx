import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Etapa1ChowChart } from "./Etapa1ChowChart";
import type { Etapa1Datos, TestResultDetail } from "../../api/types";

function datosSinAtipico(): Etapa1Datos {
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

function datosConAtipico(): Etapa1Datos {
  return {
    ...datosSinAtipico(),
    serie_efectiva: [94.71, 89.83, 500.0],
    indice_atipico: 2,
  };
}

function chowConFajas(
  overrides: Partial<TestResultDetail> = {},
): TestResultDetail {
  return {
    prueba: "chow",
    estadistico: 1.41,
    valor_critico: 1.15,
    veredicto: "rechazada",
    warning_codigo: "TEST_WARNING_OUTLIER_DETECTED",
    warning_nivel: "normal",
    n1: null,
    n2: null,
    valor_atipico: 500.0,
    indice_atipico: 2,
    explicacion: {
      ecuacion: "Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
      terminos: {
        n: 3,
        media_log: 4.7,
        s_log: 0.3,
        nu: 1,
        t_bonferroni: 12.7,
      },
    },
    ...overrides,
  };
}

describe("Etapa1ChowChart", () => {
  it("draws every point as a normal marker when there is no outlier", () => {
    const { container } = render(<Etapa1ChowChart datos={datosSinAtipico()} />);

    expect(screen.getByRole("img", { name: /Gráfico de Chow/ })).toBeInTheDocument();
    const normales = container.querySelector('g[data-series="normales"]');
    expect(normales?.querySelectorAll("circle")).toHaveLength(3);
    expect(container.querySelector('g[data-series="atipico"]')).not.toBeInTheDocument();
  });

  it("marks the outlier separately and excludes it from the normal markers", () => {
    const { container } = render(<Etapa1ChowChart datos={datosConAtipico()} />);

    const normales = container.querySelector('g[data-series="normales"]');
    expect(normales?.querySelectorAll("circle")).toHaveLength(2);

    const atipico = container.querySelector('g[data-series="atipico"]');
    expect(atipico?.querySelectorAll("circle")).toHaveLength(1);

    // La línea sigue incluyendo TODOS los puntos, atípico incluido — no
    // se rompe la continuidad de la serie.
    const linea = container.querySelector('path[data-series="linea"]');
    expect(linea?.getAttribute("d")).toBeTruthy();
  });

  it("paints the outlier marker with the --crit token (stands out in light mode)", () => {
    const { container } = render(<Etapa1ChowChart datos={datosConAtipico()} />);

    const circulo = container.querySelector(
      'g[data-series="atipico"] circle',
    ) as SVGCircleElement | null;
    expect(circulo?.style.fill).toBe("var(--crit)");
  });

  it("draws the máximos/mínimos bands as dashed reference lines when Chow ran", () => {
    const { container } = render(
      <Etapa1ChowChart datos={datosConAtipico()} chow={chowConFajas()} />,
    );

    const fajaMax = container.querySelector('path[data-series="faja-max"]');
    const fajaMin = container.querySelector('path[data-series="faja-min"]');
    expect(fajaMax?.getAttribute("d")).toBeTruthy();
    expect(fajaMin?.getAttribute("d")).toBeTruthy();
    // Punteadas — no se confunden con la serie de datos.
    expect((fajaMax as SVGPathElement).style.strokeDasharray).not.toBe("");
    expect((fajaMin as SVGPathElement).style.strokeDasharray).not.toBe("");
  });

  it("does not draw bands when Chow was not executed (no explicacion)", () => {
    const { container } = render(
      <Etapa1ChowChart
        datos={datosSinAtipico()}
        chow={chowConFajas({
          veredicto: "no_ejecutada",
          estadistico: null,
          valor_critico: null,
          explicacion: null,
        })}
      />,
    );

    expect(container.querySelector('path[data-series="faja-max"]')).not.toBeInTheDocument();
    expect(container.querySelector('path[data-series="faja-min"]')).not.toBeInTheDocument();
  });

  it("does not draw bands when no chow prop is passed", () => {
    const { container } = render(<Etapa1ChowChart datos={datosConAtipico()} />);

    expect(container.querySelector('path[data-series="faja-max"]')).not.toBeInTheDocument();
    expect(container.querySelector('path[data-series="faja-min"]')).not.toBeInTheDocument();
  });

  it("never shows a calendario/configurado toggle — Chow is an apartamiento parcial of the two-version rule", () => {
    render(<Etapa1ChowChart datos={datosConAtipico()} />);
    // "Restablecer zoom" (del propio InteractiveChart) es el único botón —
    // nunca "Configurado"/"Calendario".
    expect(screen.queryByRole("button", { name: "Configurado" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Calendario" })).not.toBeInTheDocument();
  });

  it("shows the criterio de año note only when mesInicioAnio is provided", () => {
    const { rerender } = render(<Etapa1ChowChart datos={datosSinAtipico()} />);
    expect(screen.queryByText(/Criterio de año/)).not.toBeInTheDocument();

    rerender(<Etapa1ChowChart datos={datosSinAtipico()} mesInicioAnio={7} />);
    expect(screen.getByText(/Criterio de año: julio/)).toBeInTheDocument();
  });

  it("renders nothing when there are no effective timestamps", () => {
    const datos: Etapa1Datos = { ...datosSinAtipico(), timestamps_efectivos: null };
    const { container } = render(<Etapa1ChowChart datos={datos} />);

    expect(container).toBeEmptyDOMElement();
  });
});
