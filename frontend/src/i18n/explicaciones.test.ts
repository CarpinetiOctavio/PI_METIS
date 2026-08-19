import { describe, expect, it } from "vitest";
import { formatearFormula, interpretar, REGLA_GRUPO } from "./explicaciones";
import type { TestResultDetail } from "../api/types";

function tr(overrides: Partial<TestResultDetail> = {}): TestResultDetail {
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

describe("formatearFormula", () => {
  it("devuelve null sin explicacion (rama no_ejecutada)", () => {
    expect(formatearFormula(tr({ explicacion: null }))).toBeNull();
  });

  it("anderson — reproduce el estadístico con numerador/denominador del lag reportado", () => {
    const resultado = tr({
      prueba: "anderson",
      estadistico: 0.35734,
      explicacion: {
        ecuacion: "III-1",
        terminos: { n: 40, k: 9, numerador: 4378.386, denominador: 12254.308 },
      },
    });
    const lineas = formatearFormula(resultado);
    expect(lineas).not.toBeNull();
    expect(lineas!.join(" ")).toContain("r₉");
    expect(lineas!.join(" ")).toContain("0,35734");
  });

  it("wald_wolfowitz — reproduce Z a partir de R, µ_R y σ_R", () => {
    const resultado = tr({
      prueba: "wald_wolfowitz",
      estadistico: 0.47555,
      explicacion: {
        ecuacion: "III-4",
        terminos: { n: 40, n1: 17, n2: 23, r: 22, mu_r: 20.55, sigma_r: 3.04939 },
      },
    });
    const [linea] = formatearFormula(resultado)!;
    expect(linea).toContain("Z = (R − µ_R) / σ_R");
    expect(linea).toContain("22");
    expect(linea).toContain("0,47555");
  });

  it("helmert — muestra S − C junto con el límite (valor_critico)", () => {
    const resultado = tr({
      prueba: "helmert",
      estadistico: -3,
      valor_critico: 6.245,
      explicacion: { ecuacion: "III-7", terminos: { n: 40, s: 18, c: 21 } },
    });
    const [linea] = formatearFormula(resultado)!;
    expect(linea).toContain("S − C = 18,00000 − 21,00000 = -3,00000");
    expect(linea).toContain("6,24500");
  });

  it("t_student — reconstruye el denominador Sp·√(1/n1+1/n2) para mostrarlo", () => {
    const resultado = tr({
      prueba: "t_student",
      estadistico: -1.14937,
      explicacion: {
        ecuacion: "III-8",
        terminos: { x1_barra: 152.31, x2_barra: 168.44, sp: 24.6, n1: 20, n2: 20, nu: 38 },
      },
    });
    const [linea] = formatearFormula(resultado)!;
    // El denominador no viaja en terminos — se reconstruye acá para
    // mostrarlo, coincide con sp*sqrt(1/n1+1/n2) ≈ 7.777.
    expect(linea).toContain("152,31000");
    expect(linea).toContain("168,44000");
    expect(linea).toContain("-1,14937");
  });

  it("cramer — muestra los DOS bloques, no solo el binding", () => {
    const resultado = tr({
      prueba: "cramer",
      estadistico: 0.78586,
      valor_critico: 2.02439,
      explicacion: {
        ecuacion: "III-15",
        terminos: {
          n: 40,
          n_w1: 24,
          n_w2: 12,
          tau_w1: 0.03122,
          tau_w2: 0.19317,
          t_w1: 0.23585,
          t_w2: 0.78586,
          vc_w1: 2.02439,
          vc_w2: 2.02439,
        },
      },
    });
    const lineas = formatearFormula(resultado)!;
    expect(lineas).toHaveLength(2);
    expect(lineas[0]).toContain("Bloque 60%");
    expect(lineas[0]).toContain("n_w₁=24");
    expect(lineas[1]).toContain("Bloque 30%");
    expect(lineas[1]).toContain("n_w₂=12");
  });

  it("mann_kendall — muestra S y Var(S), sin fabricar la corrección por empates", () => {
    const resultado = tr({
      prueba: "mann_kendall",
      estadistico: 0.7528,
      explicacion: { ecuacion: "A.55", terminos: { n: 40, s: 91, var_s: 14291.667 } },
    });
    const [linea] = formatearFormula(resultado)!;
    expect(linea).toContain("S = 91,00000");
    expect(linea).toContain("0,75280");
  });

  it("kolmogorov_smirnov — reproduce Z = D·√(n1·n2/(n1+n2))", () => {
    const resultado = tr({
      prueba: "kolmogorov_smirnov",
      estadistico: 0.63246,
      explicacion: { ecuacion: "A.57", terminos: { n1: 20, n2: 20, d: 0.2 } },
    });
    const [linea] = formatearFormula(resultado)!;
    expect(linea).toContain("D·√(n₁·n₂/(n₁+n₂))");
    expect(linea).toContain("0,63246");
  });

  it("chow — muestra K_N y el t Bonferroni-corregido", () => {
    const resultado = tr({
      prueba: "chow",
      estadistico: 2.1,
      valor_critico: 2.745,
      explicacion: {
        ecuacion: "Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
        terminos: { n: 30, media_log: 3.5, s_log: 0.4, nu: 28, t_bonferroni: 3.5 },
      },
    });
    const [linea] = formatearFormula(resultado)!;
    expect(linea).toContain("K_N");
    expect(linea).toContain("2,74500");
    expect(linea).toContain("t_{n−2,1−α/(2n)} = 3,50000");
  });
});

describe("interpretar", () => {
  it("devuelve null sin explicacion", () => {
    expect(interpretar(tr({ explicacion: null }))).toBeNull();
  });

  it("cambia de redacción según veredicto (t_student aprobada vs rechazada)", () => {
    const base = {
      prueba: "t_student",
      explicacion: { ecuacion: "III-8", terminos: { x1_barra: 1, x2_barra: 2, sp: 1, n1: 20, n2: 20, nu: 38 } },
    };
    const aprobada = interpretar(tr({ ...base, veredicto: "aprobada" }))!;
    const rechazada = interpretar(tr({ ...base, veredicto: "rechazada" }))!;
    expect(aprobada).toContain("no hay evidencia de");
    expect(rechazada).toContain("hay evidencia de");
    expect(aprobada).not.toBe(rechazada);
  });

  it("anderson — cita lags_fuera y k_max exactos", () => {
    const resultado = tr({
      prueba: "anderson",
      veredicto: "aprobada",
      explicacion: {
        ecuacion: "III-1",
        terminos: { lags_fuera: 1, k_max: 14, tolerancia: 2 },
      },
    });
    const texto = interpretar(resultado)!;
    expect(texto).toContain("1 de 14");
    expect(texto).toContain("no hay evidencia de dependencia serial");
  });

  it("cramer — distingue ambos bloques aprobados de al menos uno rechazado", () => {
    const ambosAprueban = tr({
      prueba: "cramer",
      explicacion: {
        ecuacion: "III-15",
        terminos: { t_w1: 0.2, t_w2: 0.3, vc_w1: 2.0, vc_w2: 2.0 },
      },
    });
    const unoRechaza = tr({
      prueba: "cramer",
      explicacion: {
        ecuacion: "III-15",
        terminos: { t_w1: 0.2, t_w2: 3.0, vc_w1: 2.0, vc_w2: 2.0 },
      },
    });
    expect(interpretar(ambosAprueban)).toContain("Los dos bloques");
    expect(interpretar(unoRechaza)).toContain("Al menos uno");
  });

  it("chow — menciona el valor atípico solo cuando fue detectado", () => {
    const sinAtipico = tr({ prueba: "chow", veredicto: "aprobada", valor_atipico: null, explicacion: { ecuacion: "x", terminos: {} } });
    const conAtipico = tr({
      prueba: "chow",
      veredicto: "rechazada",
      valor_atipico: 950.0,
      explicacion: { ecuacion: "x", terminos: {} },
    });
    expect(interpretar(sinAtipico)).not.toContain("950");
    expect(interpretar(conAtipico)).toContain("950,00000");
  });
});

describe("REGLA_GRUPO", () => {
  it("independencia y homogeneidad tienen jerarquía explícita ('manda')", () => {
    expect(REGLA_GRUPO.independencia).toContain("Anderson manda");
    expect(REGLA_GRUPO.homogeneidad).toContain("Cramer manda");
  });

  it("atipicos no tiene regla de grupo (un solo test, nada que jerarquizar)", () => {
    expect(REGLA_GRUPO.atipicos).toBeNull();
  });
});
