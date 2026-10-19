import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Etapa1ChowChart } from "./Etapa1ChowChart";
import type { Etapa1Datos, TestResultDetail } from "../../api/types";

function datosSinAtipico(): Etapa1Datos {
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

    // DECISIÓN 079 — el atípico va con rombo, no solo con otro color.
    const atipico = container.querySelector('g[data-series="atipico"]');
    expect(atipico?.querySelectorAll('path[data-shape="diamond"]')).toHaveLength(1);

    // La línea sigue incluyendo TODOS los puntos, atípico incluido — no
    // se rompe la continuidad de la serie.
    const linea = container.querySelector('path[data-series="linea"]');
    expect(linea?.getAttribute("d")).toBeTruthy();
  });

  it("paints the outlier marker with the --crit token (stands out in light mode)", () => {
    const { container } = render(<Etapa1ChowChart datos={datosConAtipico()} />);

    const marcador = container.querySelector(
      'g[data-series="atipico"] .interactive-chart__point',
    ) as SVGElement | null;
    expect(marcador?.style.fill).toBe("var(--crit)");
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

  // DECISIÓN 079 — todos los valores fuera de los umbrales, no solo el más extremo.
  it("marks every value of valores_atipicos and draws the bands the server sent", () => {
    const datos: Etapa1Datos = {
      ...datosSinAtipico(),
      serie_efectiva: [5.0, 94.71, 500.0],
      indice_atipico: 2,
    };
    const chow = chowConFajas({
      valores_atipicos: [
        { indice: 2, valor: 500.0, z: 1.3, lado: "alto" },
        { indice: 0, valor: 5.0, z: -1.2, lado: "bajo" },
      ],
      explicacion: {
        ecuacion: "Bulletin 17B",
        terminos: { n: 3, media_log: 4.7, s_log: 0.3, limite_inferior: 60, limite_superior: 160 },
      },
    });
    const { container } = render(<Etapa1ChowChart datos={datos} chow={chow} />);

    const atipicos = container.querySelectorAll('g[data-series="atipico"] path[data-shape="diamond"]');
    expect(atipicos).toHaveLength(2);
    expect(container.querySelectorAll('g[data-series="normales"] circle')).toHaveLength(1);
    expect(screen.getByRole("img", { name: /2 atípicos marcados/ })).toBeInTheDocument();
    expect(screen.getByText(/umbrales de Bulletin 17B/)).toHaveTextContent("2 valores marcados");
  });

  // Revisión 19/10/2026 de la DECISIÓN 073 — Chow no ejecutada: el gráfico
  // dice por qué y marca los valores que lo impidieron, sin franjas.
  function chowNoEjecutada(
    codigo: string,
    valores: { indice: number; valor: number }[] | undefined,
  ): TestResultDetail {
    return chowConFajas({
      veredicto: "no_ejecutada",
      estadistico: null,
      valor_critico: null,
      warning_codigo: codigo,
      valor_atipico: null,
      indice_atipico: null,
      explicacion: null,
      valores_no_validos: valores,
    });
  }
  const datosConNegativos = (): Etapa1Datos => ({
    ...datosSinAtipico(),
    serie_efectiva: [-0.74, 0.5, -0.2],
  });

  it("Chow no ejecutada por negativos en caudal: lo explica, marca los negativos con un cuadrado y no dibuja franjas", () => {
    const chow = chowNoEjecutada("TEST_NOT_EXECUTED_NEGATIVES", [
      { indice: 0, valor: -0.74 },
      { indice: 2, valor: -0.2 },
    ]);
    const { container } = render(
      <Etapa1ChowChart datos={datosConNegativos()} chow={chow} tipoVariable="caudal_precipitacion" />,
    );

    const aviso = screen.getByText(/La prueba de Chow no se ejecutó/);
    expect(aviso).toHaveTextContent("hay 2 valores negativos");
    expect(aviso).toHaveTextContent("físicamente imposible en una serie de caudal o precipitación");
    expect(aviso).toHaveTextContent("podés excluirlos abajo y recalcular");

    expect(container.querySelectorAll('g[data-series="no-validos"] path[data-shape="square"]')).toHaveLength(2);
    expect(container.querySelectorAll('g[data-series="normales"] circle')).toHaveLength(1);
    expect(container.querySelector('g[data-series="atipico"]')).not.toBeInTheDocument();
    expect(container.querySelector('path[data-series="faja-max"]')).not.toBeInTheDocument();
    expect(screen.getByRole("img", { name: /la prueba no se ejecutó, con 2 valores no válidos marcados/ })).toBeInTheDocument();
    expect(screen.getByText(/2 valores no válidos para Chow/)).toHaveTextContent("no son atípicos");
  });

  it("con tipo Otro no dice 'físicamente imposible' ni sugiere excluir los negativos", () => {
    const chow = chowNoEjecutada("TEST_NOT_EXECUTED_NEGATIVES", [{ indice: 0, valor: -0.74 }]);
    render(<Etapa1ChowChart datos={datosConNegativos()} chow={chow} tipoVariable="otro" />);

    const aviso = screen.getByText(/Chow no se ejecutó porque la serie tiene 1 valor negativo/);
    expect(aviso).toHaveTextContent("la prueba trabaja sobre logaritmos");
    expect(aviso).not.toHaveTextContent("físicamente");
    expect(aviso).not.toHaveTextContent("excluir");
  });

  it("con ceros en caudal explica el logaritmo de cero, sin llamarlos físicamente imposibles", () => {
    const datos = { ...datosSinAtipico(), serie_efectiva: [0, 94.71, 105.13] };
    const chow = chowNoEjecutada("TEST_NOT_EXECUTED_ZEROS", [{ indice: 0, valor: 0 }]);
    const { container } = render(
      <Etapa1ChowChart datos={datos} chow={chow} tipoVariable="caudal_precipitacion" />,
    );

    const aviso = screen.getByText(/La prueba de Chow no se ejecutó/);
    expect(aviso).toHaveTextContent("hay 1 cero en la serie");
    expect(aviso).toHaveTextContent("el logaritmo de cero no existe");
    expect(aviso).not.toHaveTextContent("físicamente");
    expect(container.querySelectorAll('g[data-series="no-validos"] path[data-shape="square"]')).toHaveLength(1);
  });

  it("un análisis anterior sin valores_no_validos avisa que no corrió, sin marcas", () => {
    const { container } = render(
      <Etapa1ChowChart
        datos={datosConNegativos()}
        chow={chowNoEjecutada("TEST_NOT_EXECUTED_NEGATIVES", undefined)}
        tipoVariable="caudal_precipitacion"
      />,
    );

    expect(screen.getByText(/no hay umbrales que dibujar/)).toBeInTheDocument();
    expect(container.querySelector('g[data-series="no-validos"]')).not.toBeInTheDocument();
  });

  it("renders nothing when there are no effective timestamps", () => {
    const datos: Etapa1Datos = { ...datosSinAtipico(), timestamps_efectivos: null };
    const { container } = render(<Etapa1ChowChart datos={datos} />);

    expect(container).toBeEmptyDOMElement();
  });
});
