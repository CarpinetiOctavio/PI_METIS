import katex from "katex";
import { describe, expect, it } from "vitest";
import {
  formatearFormula,
  formatearFormulaLatex,
  interpretar,
  REGLA_GRUPO,
} from "./explicaciones";
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

type Terminos = Record<string, number | null>;

interface CasoBase {
  estadistico: number;
  valor_critico?: number;
  ecuacion: string;
  terminos: Terminos;
}

// Un resultado representativo por prueba, definido UNA sola vez: antes cada
// test repetía su propio literal (los mismos `terminos` copiados 3 veces) y
// SonarCloud lo marcaba como código duplicado. Cada test parte de acá y
// cambia solo lo que su caso necesita (ver `caso()`).
const CASOS: Record<string, CasoBase> = {
  anderson: {
    estadistico: 0.35734,
    ecuacion: "III-1",
    terminos: {
      n: 40,
      k: 9,
      numerador: 4378.386,
      denominador: 12254.308,
      k_max: 14,
      lags_fuera: 1,
      tolerancia: 2,
    },
  },
  wald_wolfowitz: {
    estadistico: 0.47555,
    ecuacion: "III-4",
    terminos: { n: 40, n1: 17, n2: 23, r: 22, mu_r: 20.55, sigma_r: 3.04939 },
  },
  helmert: {
    estadistico: -3,
    valor_critico: 6.245,
    ecuacion: "III-7",
    terminos: { n: 40, s: 18, c: 21 },
  },
  t_student: {
    estadistico: -1.14937,
    ecuacion: "III-8",
    terminos: { x1_barra: 152.31, x2_barra: 168.44, sp: 24.6, n1: 20, n2: 20, nu: 38 },
  },
  cramer: {
    estadistico: 0.78586,
    valor_critico: 2.02439,
    ecuacion: "III-15",
    terminos: {
      n: 40,
      n_w1: 24,
      n_w2: 12,
      media_global: 150.25,
      s_global: 31.5,
      tau_w1: 0.03122,
      tau_w2: 0.19317,
      t_w1: 0.23585,
      t_w2: 0.78586,
      vc_w1: 2.02439,
      vc_w2: 2.02439,
    },
  },
  mann_kendall: {
    estadistico: 0.7528,
    ecuacion: "A.55",
    terminos: { n: 40, s: 91, var_s: 14291.667 },
  },
  kolmogorov_smirnov: {
    estadistico: 0.63246,
    ecuacion: "A.57",
    terminos: { n1: 20, n2: 20, d: 0.2 },
  },
  chow: {
    estadistico: 2.1,
    valor_critico: 2.745,
    ecuacion: "Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
    terminos: { n: 30, media_log: 3.5, s_log: 0.4, nu: 28, t_bonferroni: 3.5 },
  },
};

/** Resultado de `prueba` con su fixture base. `overrides` pisa campos del
 * resultado (estadístico, veredicto, ...) y `terminos` pisa solo los
 * términos que ese test necesita cambiar. */
function caso(
  prueba: string,
  overrides: Partial<TestResultDetail> = {},
  terminos: Terminos = {},
): TestResultDetail {
  const { ecuacion, terminos: base, ...resto } = CASOS[prueba];
  return tr({
    prueba,
    ...resto,
    explicacion: { ecuacion, terminos: { ...base, ...terminos } },
    ...overrides,
  });
}

describe("formatearFormula", () => {
  it("devuelve null sin explicacion (rama no_ejecutada)", () => {
    expect(formatearFormula(tr({ explicacion: null }))).toBeNull();
  });

  it("anderson — reproduce el estadístico con numerador/denominador del lag reportado", () => {
    const lineas = formatearFormula(caso("anderson"));
    expect(lineas).not.toBeNull();
    expect(lineas!.join(" ")).toContain("r₉");
    expect(lineas!.join(" ")).toContain("0,35734");
  });

  it("wald_wolfowitz — reproduce Z a partir de R, µ_R y σ_R", () => {
    const [linea] = formatearFormula(caso("wald_wolfowitz"))!;
    expect(linea).toContain("Z = (R − µ_R) / σ_R");
    expect(linea).toContain("22");
    expect(linea).toContain("0,47555");
  });

  it("helmert — muestra S − C junto con el límite (valor_critico)", () => {
    const [linea] = formatearFormula(caso("helmert"))!;
    expect(linea).toContain("S − C = 18,00000 − 21,00000 = -3,00000");
    expect(linea).toContain("6,24500");
  });

  it("t_student — reconstruye el denominador Sp·√(1/n1+1/n2) para mostrarlo", () => {
    const [linea] = formatearFormula(caso("t_student"))!;
    // El denominador no viaja en terminos — se reconstruye acá para
    // mostrarlo, coincide con sp*sqrt(1/n1+1/n2) ≈ 7.777.
    expect(linea).toContain("152,31000");
    expect(linea).toContain("168,44000");
    expect(linea).toContain("-1,14937");
  });

  it("cramer — muestra los DOS bloques, no solo el binding", () => {
    const lineas = formatearFormula(caso("cramer"))!;
    expect(lineas).toHaveLength(2);
    // Sin "60%"/"30%": con partición personalizada (DECISIÓN 036) serían falsos.
    expect(lineas[0]).toContain("Bloque 1");
    expect(lineas[0]).toContain("n_w₁=24");
    expect(lineas[1]).toContain("Bloque 2");
    expect(lineas[1]).toContain("n_w₂=12");
    expect(lineas.join(" ")).not.toContain("%");
  });

  it("mann_kendall — muestra S, Var(S) y Z = (S − sgn(S))/√Var(S), sin atribuir a A.55 la corrección por empates", () => {
    const [linea] = formatearFormula(caso("mann_kendall"))!;
    expect(linea).toContain("S = 91,00000");
    expect(linea).toContain("Z = (S − sgn(S)) / √Var(S)");
    expect(linea).toContain("0,75280");
    expect(linea).not.toContain("Kendall 1975");
  });

  it("kolmogorov_smirnov — reproduce Z = D·√(n1·n2/(n1+n2))", () => {
    const [linea] = formatearFormula(caso("kolmogorov_smirnov"))!;
    expect(linea).toContain("D·√(n₁·n₂/(n₁+n₂))");
    expect(linea).toContain("0,63246");
  });

  it("chow — muestra K_N y el t Bonferroni-corregido", () => {
    const [linea] = formatearFormula(caso("chow"))!;
    expect(linea).toContain("K_N");
    expect(linea).toContain("2,74500");
    expect(linea).toContain("t_{n−2,1−α/(2n)} = 3,50000");
    // α = 0,10, no el 0,05 del resto de Etapa 1
    expect(linea).toContain("α = 0,10");
  });
});

describe("formatearFormulaLatex", () => {
  it("devuelve null sin explicacion (rama no_ejecutada)", () => {
    expect(formatearFormulaLatex(tr({ explicacion: null }))).toBeNull();
  });

  it("cada paso trae latex y su fallback de texto plano", () => {
    const pasos = formatearFormulaLatex(caso("anderson"))!;
    expect(pasos.length).toBe(3);
    for (const paso of pasos) {
      expect(typeof paso.latex).toBe("string");
      expect(paso.latex.length).toBeGreaterThan(0);
      expect(typeof paso.fallback).toBe("string");
      expect(paso.fallback.length).toBeGreaterThan(0);
    }
  });

  it("anderson — sustituye numerador/denominador y reproduce el estadístico en LaTeX", () => {
    const [simbolica, sustitucion, resultado] = formatearFormulaLatex(caso("anderson"))!;
    expect(simbolica.latex).toContain("\\dfrac");
    // coma decimal es-AR escapada como {,}, sin separador de miles
    expect(sustitucion.latex).toContain("\\dfrac{4378{,}38600}{12254{,}30800}");
    expect(resultado.latex).toBe("r_{9} = 0{,}35734");
  });

  it("anderson — el paso simbólico incluye las bandas de III-3 y la regla del 10%; la sustitución cita los lags fuera", () => {
    const pasos = formatearFormulaLatex(caso("anderson"))!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("r_{k}(95\\%) = \\dfrac{-1 \\pm 1{,}96\\sqrt{n-k-1}}{n-k}");
    expect(pasos[0].latex).toContain("no más del 10\\% de los");
    expect(pasos[1].latex).toContain("\\text{Lags fuera de las bandas: } 1 \\text{ de } 14");
    expect(pasos[1].latex).toContain("\\text{tolerancia: } 2");
  });

  it("wald_wolfowitz — R entero, µ_R y σ_R con decimales, Z del estadístico", () => {
    const pasos = formatearFormulaLatex(caso("wald_wolfowitz"))!;
    expect(pasos[0].latex).toContain("\\dfrac{R - \\mu_R}{\\sigma_R}");
    expect(pasos[1].latex).toContain("\\dfrac{22 - 20{,}55000}{3{,}04939}");
    expect(pasos[2].latex).toBe("Z = 0{,}47555");
  });

  it("wald_wolfowitz — define µ_R y σ_R (III-5/III-6) y los sustituye con los valores de core", () => {
    const pasos = formatearFormulaLatex(caso("wald_wolfowitz"))!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("\\mu_R = \\dfrac{2\\,n_1 n_2}{n} + 1");
    expect(pasos[0].latex).toContain("\\sigma_R = \\sqrt{\\dfrac{(\\mu_R-1)(\\mu_R-2)}{n-1}}");
    expect(pasos[1].latex).toContain("\\mu_R = \\dfrac{2\\cdot 17\\cdot 23}{40} + 1 = 20{,}55000");
    expect(pasos[1].latex).toContain("= 3{,}04939");
  });

  it("helmert — S − C contra √(n−1), con enteros en la sustitución", () => {
    const pasos = formatearFormulaLatex(caso("helmert"))!;
    expect(pasos[1].latex).toContain("S - C = 18 - 21");
    expect(pasos[1].latex).toContain("\\sqrt{n-1} = 6{,}24500");
    expect(pasos[2].latex).toBe("S - C = -3{,}00000");
  });

  it("t_student — reconstruye el denominador Sp·√(1/n1+1/n2) en el paso de sustitución", () => {
    const pasos = formatearFormulaLatex(caso("t_student"))!;
    // 24.6 * sqrt(1/20 + 1/20) = 24.6 * sqrt(0.1) ≈ 7.77920
    expect(pasos[1].latex).toContain("152{,}31000 - 168{,}44000");
    expect(pasos[1].latex).toContain("7{,}77920");
    expect(pasos[2].latex).toBe("t = -1{,}14937");
  });

  it("t_student — define S_p² y aclara qué varianza usa", () => {
    const pasos = formatearFormulaLatex(caso("t_student"))!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("S_p^{2} = \\dfrac{n_1 s_1^{2} + n_2 s_2^{2}}{n_1+n_2-2}");
    expect(pasos[0].latex).toContain("varianza muestral (divisor }n_i-1");
    expect(pasos[1].latex).toContain("S_p = 24{,}60000");
  });

  it("cramer — tres pasos: fórmula genérica + los DOS bloques con su signo", () => {
    // Bloque 2 rechaza: t_w2 (3.0) > vc_w2 (2.02439) → signo ">"
    const pasos = formatearFormulaLatex(
      caso("cramer", { estadistico: 3.0 }, { tau_w2: 0.5, t_w2: 3.0 }),
    )!;
    expect(pasos).toHaveLength(3);
    expect(pasos[1].latex).toContain("Bloque 1");
    expect(pasos[1].latex).toContain("t_{w_1} = 0{,}23585 \\le 2{,}02439");
    expect(pasos[2].latex).toContain("Bloque 2");
    // Rótulos por n_w, nunca por porcentaje (partición personalizada, DECISIÓN 036)
    expect(pasos[1].latex).not.toContain("\\%");
    expect(pasos[2].latex).not.toContain("\\%");
    expect(pasos[2].latex).toContain("t_{w_2} = 3{,}00000 > 2{,}02439");
  });

  it("cramer — define τ_w y S_Q, y muestra la media y el desvío globales", () => {
    const pasos = formatearFormulaLatex(caso("cramer"))!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("\\tau_w = \\dfrac{\\bar{Q}_w - \\bar{Q}}{S_Q}");
    expect(pasos[0].latex).toContain("S_Q = \\sqrt{\\dfrac{1}{n-1}");
    expect(pasos[1].latex).toContain("\\bar{Q} = 150{,}25000");
    expect(pasos[1].latex).toContain("S_Q = 31{,}50000");
  });

  it("mann_kendall — muestra S, Var(S) y la tipificación Z, sin atribuir a A.55 la corrección por empates", () => {
    const pasos = formatearFormulaLatex(caso("mann_kendall"))!;
    expect(pasos[1].latex).toContain("S = 91{,}00000");
    expect(pasos[1].latex).toContain("\\operatorname{Var}(S) = 14291{,}66700");
    expect(pasos[2].latex).toContain("Z = 0{,}75280");
    // Paso simbólico: Var(S) sin empates (A.55) y la tipificación con corrección de continuidad
    expect(pasos[0].latex).toContain("\\dfrac{n(n-1)(2n+5)}{18}");
    expect(pasos[0].latex).toContain("\\dfrac{S-\\operatorname{sgn}(S)}{\\sqrt{\\operatorname{Var}(S)}}");
    expect(pasos[2].latex).toContain("corrección de continuidad");
    expect(pasos.map((p) => p.latex).join(" ")).not.toContain("Kendall 1975");
  });

  it("kolmogorov_smirnov — Z = D·√(n1·n2/(n1+n2)) con la suma sustituida", () => {
    const pasos = formatearFormulaLatex(caso("kolmogorov_smirnov"))!;
    expect(pasos[0].latex).toContain("D\\sqrt");
    expect(pasos[1].latex).toContain("\\dfrac{20\\cdot 20}{40}");
    expect(pasos[2].latex).toBe("Z = 0{,}63246");
  });

  it("kolmogorov_smirnov — define D (A.56)", () => {
    const pasos = formatearFormulaLatex(caso("kolmogorov_smirnov"))!;
    expect(pasos[0].latex).toContain("D = \\max_i");
    expect(pasos[0].latex).toContain("\\dfrac{RS(i)}{n_1} - \\dfrac{RI(i)}{n_2}");
  });

  it("chow — K_N y el t Bonferroni-corregido, resultado = valor_critico", () => {
    const pasos = formatearFormulaLatex(caso("chow"))!;
    expect(pasos[0].latex).toContain("K_N = \\dfrac{n-1}{\\sqrt{n}}");
    expect(pasos[1].latex).toContain("t_{\\,n-2,\\;1-\\alpha/(2n)} = 3{,}50000");
    expect(pasos[1].latex).toContain("n = 30");
    expect(pasos[2].latex).toBe("K_N = 2{,}74500");
  });

  it("chow — rotula α = 0,10 (no el 0,05 del resto de Etapa 1)", () => {
    const pasos = formatearFormulaLatex(caso("chow"))!;
    expect(pasos[1].latex).toContain("\\alpha = 0{,}10");
    expect(pasos[1].latex).toContain("0{,}05");
  });

  it("todos los pasos de las 8 pruebas compilan con KaTeX real (sin error de sintaxis)", () => {
    for (const prueba of Object.keys(CASOS)) {
      const pasos = formatearFormulaLatex(caso(prueba))!;
      expect(pasos, prueba).toHaveLength(3);
      for (const paso of pasos) {
        // throwOnError: un LaTeX inválido haría caer la pantalla al fallback de texto
        expect(
          () => katex.renderToString(paso.latex, { displayMode: true, throwOnError: true }),
          `${prueba}: ${paso.latex}`,
        ).not.toThrow();
      }
    }
  });
});

describe("interpretar", () => {
  it("devuelve null sin explicacion", () => {
    expect(interpretar(tr({ explicacion: null }))).toBeNull();
  });

  it("cambia de redacción según veredicto (t_student aprobada vs rechazada)", () => {
    const aprobada = interpretar(caso("t_student", { veredicto: "aprobada" }))!;
    const rechazada = interpretar(caso("t_student", { veredicto: "rechazada" }))!;
    expect(aprobada).toContain("no hay evidencia de");
    expect(rechazada).toContain("hay evidencia de");
    expect(aprobada).not.toBe(rechazada);
  });

  it("anderson — cita lags_fuera y k_max exactos", () => {
    const texto = interpretar(caso("anderson", { veredicto: "aprobada" }))!;
    expect(texto).toContain("1 de 14");
    expect(texto).toContain("no hay evidencia de dependencia serial");
  });

  it("cramer — distingue ambos bloques aprobados de al menos uno rechazado", () => {
    const ambosAprueban = caso("cramer");
    const unoRechaza = caso("cramer", {}, { t_w2: 3.0 });
    expect(interpretar(ambosAprueban)).toContain("Los dos bloques");
    expect(interpretar(unoRechaza)).toContain("Al menos uno");
  });

  it("chow — menciona el valor atípico solo cuando fue detectado", () => {
    const sinAtipico = caso("chow", { veredicto: "aprobada", valor_atipico: null });
    const conAtipico = caso("chow", { veredicto: "rechazada", valor_atipico: 950.0 });
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
