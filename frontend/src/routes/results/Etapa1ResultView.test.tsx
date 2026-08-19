import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";
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

  it("modo paso a paso muestra la fórmula sustituida y su interpretación", () => {
    render(<Etapa1ResultView result={makeResult()} modo="paso_a_paso" />);

    expect(screen.getByText(/r₉ = 4\.378,38600 \/ 12\.254,30800/)).toBeInTheDocument();
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

  it("una prueba no_ejecutada (sin explicacion) muestra el motivo, no una fórmula vacía", () => {
    render(<Etapa1ResultView result={makeResult()} modo="paso_a_paso" />);
    expect(
      screen.getByText(/No ejecutada — TEST_NOT_EXECUTED_CONDITION/),
    ).toBeInTheDocument();
  });
});
