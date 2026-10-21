import { describe, expect, it } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { Etapa1ResultView } from "./Etapa1ResultView";
import type { Etapa1Result, TestResultDetail } from "../../api/types";
import { makeAndersonConDesglose, makeChowConDesglose } from "../../test/etapa1Fixtures";

function testResult(overrides: Partial<TestResultDetail> = {}): TestResultDetail {
  return {
    prueba: "anderson",
    estadistico: 0.35734,
    valor_critico: 0.4,
    veredicto: "aprobada",
    warning_codigo: null,
    warning_nivel: null,
    n1: null,
    n2: null,
    valor_atipico: null,
    indice_atipico: null,
    explicacion: null,
    ...overrides,
  };
}

const ANDERSON_CON_EXPLICACION = testResult({
  prueba: "anderson",
  explicacion: {
    ecuacion: "III-1",
    terminos: { n: 40, k: 9, numerador: 4378.386, denominador: 12254.308, lags_fuera: 1, k_max: 14, tolerancia: 2 },
  },
});

const WALD_NO_EJECUTADA = testResult({
  prueba: "wald_wolfowitz",
  estadistico: null,
  valor_critico: null,
  veredicto: "no_ejecutada",
  warning_codigo: "TEST_NOT_EXECUTED_CONDITION",
  explicacion: null,
});

function makeResult(overrides: Partial<Etapa1Result> = {}): Etapa1Result {
  return {
    contract: { bloqueante: false, codigo_error: null, warnings: [] },
    descriptive: null,
    independencia: [ANDERSON_CON_EXPLICACION, WALD_NO_EJECUTADA],
    homogeneidad: [],
    tendencia: [],
    atipicos: [],
    nivel_independencia: "independiente",
    nivel_homogeneidad: "homogeneidad_ok",
    nivel_confianza: "validado",
    warnings: [],
    ...overrides,
  };
}

describe("Etapa1ResultView — Bloque D (plan post-avance, DECISIÓN 064)", () => {
  it("modo experto muestra la tabla compacta, sin fórmula ni interpretación", () => {
    render(<Etapa1ResultView result={makeResult()} modo="experto" />);

    expect(screen.getByRole("columnheader", { name: "Estadístico" })).toBeInTheDocument();
    expect(screen.queryByText(/Ec\. III-1/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Anderson manda/)).not.toBeInTheDocument();
  });

  it("modo paso a paso muestra la fórmula sustituida (KaTeX) y su interpretación", async () => {
    const { container } = render(
      <Etapa1ResultView result={makeResult()} modo="paso_a_paso" />,
    );

    // F3 (feedback Facundo 02/09) — las fórmulas se renderizan con KaTeX,
    // cargado con import() diná­mico (chunk aparte). Hasta que llega se ve
    // el fallback de texto plano; después, la notación real. El LaTeX crudo
    // (términos ya sustituidos) queda en el <annotation> MathML de KaTeX.
    await waitFor(() => {
      expect(container.querySelectorAll(".katex").length).toBeGreaterThan(0);
    });
    const latexCrudo = Array.from(
      container.querySelectorAll('.katex annotation[encoding="application/x-tex"]'),
    )
      .map((n) => n.textContent)
      .join(" ");
    expect(latexCrudo).toContain("4378{,}38600");
    expect(latexCrudo).toContain("12254{,}30800");
    expect(latexCrudo).toContain("r_{9} = 0{,}35734");

    expect(screen.getByText(/Ec\. III-1/)).toBeInTheDocument();
    expect(screen.getByText(/lags calculados caen fuera de las bandas/)).toBeInTheDocument();
  });

  it("modo paso a paso muestra la regla de decisión del grupo", () => {
    render(<Etapa1ResultView result={makeResult()} modo="paso_a_paso" />);
    expect(
      screen.getByText(/Anderson manda: si Anderson aprueba/),
    ).toBeInTheDocument();
  });

  it("atípicos (un solo test) no muestra ninguna regla de grupo", () => {
    render(
      <Etapa1ResultView
        result={makeResult({ atipicos: [testResult({ prueba: "chow" })] })}
        modo="paso_a_paso"
      />,
    );
    const grupoAtipicos = screen.getByText("Atípicos (Chow)").closest("details")!;
    expect(within(grupoAtipicos).queryByText(/manda/)).not.toBeInTheDocument();
  });

  it("una prueba no_ejecutada (sin explicacion) muestra el motivo en castellano, no una fórmula vacía", () => {
    render(<Etapa1ResultView result={makeResult()} modo="paso_a_paso" />);
    expect(
      screen.getByText("La prueba no se ejecutó: no se cumple una condición previa."),
    ).toBeInTheDocument();
  });

  // Bloque F (plan post-avance) — la fila de una prueba no_ejecutada dejó de
  // quedar en blanco: ahora explica el motivo real (ceros, condición previa,
  // muestra chica), no solo el código.
  it("modo experto también explica el motivo de una prueba no_ejecutada, no solo el código", () => {
    render(<Etapa1ResultView result={makeResult()} modo="experto" />);
    expect(
      screen.getByText(/La prueba no se ejecutó: no se cumple una condición previa\./),
    ).toBeInTheDocument();
    expect(screen.queryByText(/TEST_NOT_EXECUTED_CONDITION/)).not.toBeInTheDocument();
  });
});

describe("Etapa1ResultView — desglose paso a paso (ítems E/F, plan de feedback de directores)", () => {
  const conDesglose = makeResult({ independencia: [makeAndersonConDesglose()], atipicos: [makeChowConDesglose()] });

  it("modo paso a paso ofrece el desglose de Anderson y de Chow", () => {
    render(<Etapa1ResultView result={conDesglose} modo="paso_a_paso" />);
    expect(screen.getByText(/Ver los k pasos/)).toBeInTheDocument();
    expect(screen.getByText(/Ver el cálculo por observación/)).toBeInTheDocument();
  });

  it("modo experto no lo muestra: son resultados directos, sin explicaciones", () => {
    render(<Etapa1ResultView result={conDesglose} modo="experto" />);
    expect(screen.queryByText(/Ver los k pasos/)).not.toBeInTheDocument();
  });

  it("sin desglose en el payload (backend viejo o historial) la vista queda como antes", () => {
    render(<Etapa1ResultView result={makeResult()} modo="paso_a_paso" />);
    expect(screen.queryByText(/Ver los k pasos/)).not.toBeInTheDocument();
    expect(screen.getByText(/Ec\. III-1/)).toBeInTheDocument();
  });
});

describe("Etapa1ResultView — nivel de significancia (DECISIÓN 078)", () => {
  it("muestra el α con que corrió el análisis, sin destacar el 5 %", () => {
    render(<Etapa1ResultView result={makeResult({ alfa: 0.05 })} modo="experto" />);
    const linea = screen.getByText(/Nivel de significancia de la Etapa 1/);
    expect(linea).toHaveTextContent("α = 5 % (estándar en hidrología)");
    expect(linea.querySelector(".pill.warn")).toBeNull();
  });

  it("destaca un α distinto del 5 %", () => {
    render(<Etapa1ResultView result={makeResult({ alfa: 0.1 })} modo="paso_a_paso" />);
    const linea = screen.getByText(/Nivel de significancia de la Etapa 1/);
    expect(linea.querySelector(".pill.warn")).toHaveTextContent("α = 10 %");
  });

  it("un análisis anterior sin α registrado se muestra como el 5 % de entonces", () => {
    render(<Etapa1ResultView result={makeResult()} modo="experto" />);
    expect(screen.getByText(/Nivel de significancia de la Etapa 1/)).toHaveTextContent(
      "α = 5 % (el único disponible cuando se corrió)",
    );
  });

  it("paso a paso: las bandas de Anderson usan el α y el z del servidor, no 1,96 escrito a mano", async () => {
    const anderson = testResult({
      prueba: "anderson",
      explicacion: {
        ecuacion: "III-1",
        terminos: {
          ...ANDERSON_CON_EXPLICACION.explicacion!.terminos,
          alfa: 0.1,
          z_critico: 1.6449,
        },
      },
    });
    const { container } = render(
      <Etapa1ResultView
        result={makeResult({ alfa: 0.1, independencia: [anderson] })}
        modo="paso_a_paso"
      />,
    );
    await waitFor(() => expect(container.querySelector(".katex")).not.toBeNull());
    expect(container.textContent).toContain("90");
    expect(container.textContent).not.toContain("1,96");
  });
});


describe("Etapa1ResultView — partición de Cramer (D-18, revisión manual 21/10/2026)", () => {
  const conCramer = (n1: number, n2: number) =>
    makeResult({ homogeneidad: [testResult({ prueba: "cramer", n1, n2 })] });

  it("con la partición por defecto informa 60 % / 30 % y los tamaños del resultado", () => {
    render(<Etapa1ResultView result={conCramer(24, 12)} modo="experto" cramerParticion="default" />);
    expect(screen.getByText(/Partición de Cramer/)).toHaveTextContent(
      "Partición de Cramer: últimos 60 % y 30 % (n₁ = 24, n₂ = 12)",
    );
  });

  it("con una partición personalizada lo dice", () => {
    render(
      <Etapa1ResultView
        result={conCramer(28, 14)}
        modo="paso_a_paso"
        cramerParticion={{ n1_pct: 70, n2_pct: 35 }}
      />,
    );
    expect(screen.getByText(/Partición de Cramer/)).toHaveTextContent(
      "Partición de Cramer: personalizada: últimos 70 % y 35 % (n₁ = 28, n₂ = 14)",
    );
  });

  it("sin partición registrada (análisis viejo) no muestra nada en vez de inventarla", () => {
    render(<Etapa1ResultView result={conCramer(24, 12)} modo="experto" />);
    expect(screen.queryByText(/Partición de Cramer/)).not.toBeInTheDocument();
  });
});
