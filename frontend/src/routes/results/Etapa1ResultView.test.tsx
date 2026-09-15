import { describe, expect, it } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { Etapa1ResultView } from "./Etapa1ResultView";
import type { Etapa1Result, TestResultDetail } from "../../api/types";

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
