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
    // Sin "60%"/"30%": con partición personalizada (DECISIÓN 036) serían falsos.
    expect(lineas[0]).toContain("Bloque 1");
    expect(lineas[0]).toContain("n_w₁=24");
    expect(lineas[1]).toContain("Bloque 2");
    expect(lineas[1]).toContain("n_w₂=12");
    expect(lineas.join(" ")).not.toContain("%");
  });

  it("mann_kendall — muestra S, Var(S) y Z = (S − sgn(S))/√Var(S), sin atribuir a A.55 la corrección por empates", () => {
    const resultado = tr({
      prueba: "mann_kendall",
      estadistico: 0.7528,
      explicacion: { ecuacion: "A.55", terminos: { n: 40, s: 91, var_s: 14291.667 } },
    });
    const [linea] = formatearFormula(resultado)!;
    expect(linea).toContain("S = 91,00000");
    expect(linea).toContain("Z = (S − sgn(S)) / √Var(S)");
    expect(linea).toContain("0,75280");
    expect(linea).not.toContain("Kendall 1975");
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
    // α = 0,10, no el 0,05 del resto de Etapa 1
    expect(linea).toContain("α = 0,10");
  });
});

describe("formatearFormulaLatex", () => {
  it("devuelve null sin explicacion (rama no_ejecutada)", () => {
    expect(formatearFormulaLatex(tr({ explicacion: null }))).toBeNull();
  });

  it("cada paso trae latex y su fallback de texto plano", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "anderson",
        estadistico: 0.35734,
        explicacion: {
          ecuacion: "III-1",
          terminos: { n: 40, k: 9, numerador: 4378.386, denominador: 12254.308 },
        },
      }),
    )!;
    expect(pasos.length).toBe(3);
    for (const paso of pasos) {
      expect(typeof paso.latex).toBe("string");
      expect(paso.latex.length).toBeGreaterThan(0);
      expect(typeof paso.fallback).toBe("string");
      expect(paso.fallback.length).toBeGreaterThan(0);
    }
  });

  it("anderson — sustituye numerador/denominador y reproduce el estadístico en LaTeX", () => {
    const [simbolica, sustitucion, resultado] = formatearFormulaLatex(
      tr({
        prueba: "anderson",
        estadistico: 0.35734,
        explicacion: {
          ecuacion: "III-1",
          terminos: { n: 40, k: 9, numerador: 4378.386, denominador: 12254.308 },
        },
      }),
    )!;
    expect(simbolica.latex).toContain("\\dfrac");
    // coma decimal es-AR escapada como {,}, sin separador de miles
    expect(sustitucion.latex).toContain("\\dfrac{4378{,}38600}{12254{,}30800}");
    expect(resultado.latex).toBe("r_{9} = 0{,}35734");
  });

  it("wald_wolfowitz — R entero, µ_R y σ_R con decimales, Z del estadístico", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "wald_wolfowitz",
        estadistico: 0.47555,
        explicacion: {
          ecuacion: "III-4",
          terminos: { n: 40, n1: 17, n2: 23, r: 22, mu_r: 20.55, sigma_r: 3.04939 },
        },
      }),
    )!;
    expect(pasos[0].latex).toContain("\\dfrac{R - \\mu_R}{\\sigma_R}");
    expect(pasos[1].latex).toContain("\\dfrac{22 - 20{,}55000}{3{,}04939}");
    expect(pasos[2].latex).toBe("Z = 0{,}47555");
  });

  it("t_student — reconstruye el denominador Sp·√(1/n1+1/n2) en el paso de sustitución", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "t_student",
        estadistico: -1.14937,
        explicacion: {
          ecuacion: "III-8",
          terminos: { x1_barra: 152.31, x2_barra: 168.44, sp: 24.6, n1: 20, n2: 20, nu: 38 },
        },
      }),
    )!;
    // 24.6 * sqrt(1/20 + 1/20) = 24.6 * sqrt(0.1) ≈ 7.77920
    expect(pasos[1].latex).toContain("152{,}31000 - 168{,}44000");
    expect(pasos[1].latex).toContain("7{,}77920");
    expect(pasos[2].latex).toBe("t = -1{,}14937");
  });

  it("cramer — tres pasos: fórmula genérica + los DOS bloques con su signo", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "cramer",
        estadistico: 3.0,
        valor_critico: 2.02439,
        explicacion: {
          ecuacion: "III-15",
          terminos: {
            n: 40,
            n_w1: 24,
            n_w2: 12,
            tau_w1: 0.03122,
            tau_w2: 0.5,
            t_w1: 0.23585,
            t_w2: 3.0,
            vc_w1: 2.02439,
            vc_w2: 2.02439,
          },
        },
      }),
    )!;
    expect(pasos).toHaveLength(3);
    expect(pasos[1].latex).toContain("Bloque 1");
    expect(pasos[1].latex).toContain("t_{w_1} = 0{,}23585 \\le 2{,}02439");
    expect(pasos[2].latex).toContain("Bloque 2");
    // Rótulos por n_w, nunca por porcentaje (partición personalizada, DECISIÓN 036)
    expect(pasos[1].latex).not.toContain("\\%");
    expect(pasos[2].latex).not.toContain("\\%");
    // t_w2 (3.0) > vc_w2 (2.02439) → signo ">"
    expect(pasos[2].latex).toContain("t_{w_2} = 3{,}00000 > 2{,}02439");
  });

  it("mann_kendall — muestra S, Var(S) y la tipificación Z, sin atribuir a A.55 la corrección por empates", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "mann_kendall",
        estadistico: 0.7528,
        explicacion: { ecuacion: "A.55", terminos: { n: 40, s: 91, var_s: 14291.667 } },
      }),
    )!;
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
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "kolmogorov_smirnov",
        estadistico: 0.63246,
        explicacion: { ecuacion: "A.57", terminos: { n1: 20, n2: 20, d: 0.2 } },
      }),
    )!;
    expect(pasos[0].latex).toContain("D\\sqrt");
    expect(pasos[1].latex).toContain("\\dfrac{20\\cdot 20}{40}");
    expect(pasos[2].latex).toBe("Z = 0{,}63246");
  });

  it("chow — K_N y el t Bonferroni-corregido, resultado = valor_critico", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "chow",
        estadistico: 2.1,
        valor_critico: 2.745,
        explicacion: {
          ecuacion: "Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
          terminos: { n: 30, media_log: 3.5, s_log: 0.4, nu: 28, t_bonferroni: 3.5 },
        },
      }),
    )!;
    expect(pasos[0].latex).toContain("K_N = \\dfrac{n-1}{\\sqrt{n}}");
    expect(pasos[1].latex).toContain("t_{\\,n-2,\\;1-\\alpha/(2n)} = 3{,}50000");
    expect(pasos[1].latex).toContain("n = 30");
    expect(pasos[2].latex).toBe("K_N = 2{,}74500");
  });

  it("anderson — el paso simbólico incluye las bandas de III-3 y la regla del 10%; la sustitución cita los lags fuera", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "anderson",
        estadistico: 0.35734,
        explicacion: {
          ecuacion: "III-1",
          terminos: { n: 40, k: 9, numerador: 4378.386, denominador: 12254.308, k_max: 14, lags_fuera: 1, tolerancia: 2 },
        },
      }),
    )!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("r_{k}(95\\%) = \\dfrac{-1 \\pm 1{,}96\\sqrt{n-k-1}}{n-k}");
    expect(pasos[0].latex).toContain("no más del 10\\% de los");
    expect(pasos[1].latex).toContain("\\text{Lags fuera de las bandas: } 1 \\text{ de } 14");
    expect(pasos[1].latex).toContain("\\text{tolerancia: } 2");
  });

  it("wald_wolfowitz — define µ_R y σ_R (III-5/III-6) y los sustituye con los valores de core", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "wald_wolfowitz",
        estadistico: 0.47555,
        explicacion: {
          ecuacion: "III-4",
          terminos: { n: 40, n1: 17, n2: 23, r: 22, mu_r: 20.55, sigma_r: 3.04939 },
        },
      }),
    )!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("\\mu_R = \\dfrac{2\\,n_1 n_2}{n} + 1");
    expect(pasos[0].latex).toContain("\\sigma_R = \\sqrt{\\dfrac{(\\mu_R-1)(\\mu_R-2)}{n-1}}");
    expect(pasos[1].latex).toContain("\\mu_R = \\dfrac{2\\cdot 17\\cdot 23}{40} + 1 = 20{,}55000");
    expect(pasos[1].latex).toContain("= 3{,}04939");
  });

  it("t_student — define S_p² y aclara qué varianza usa", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "t_student",
        estadistico: -1.14937,
        explicacion: {
          ecuacion: "III-8",
          terminos: { x1_barra: 152.31, x2_barra: 168.44, sp: 24.6, n1: 20, n2: 20, nu: 38 },
        },
      }),
    )!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("S_p^{2} = \\dfrac{n_1 s_1^{2} + n_2 s_2^{2}}{n_1+n_2-2}");
    expect(pasos[0].latex).toContain("varianza muestral (divisor }n_i-1");
    expect(pasos[1].latex).toContain("S_p = 24{,}60000");
  });

  it("cramer — define τ_w y S_Q, y muestra la media y el desvío globales", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "cramer",
        estadistico: 0.78586,
        valor_critico: 2.02439,
        explicacion: {
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
      }),
    )!;
    expect(pasos).toHaveLength(3);
    expect(pasos[0].latex).toContain("\\tau_w = \\dfrac{\\bar{Q}_w - \\bar{Q}}{S_Q}");
    expect(pasos[0].latex).toContain("S_Q = \\sqrt{\\dfrac{1}{n-1}");
    expect(pasos[1].latex).toContain("\\bar{Q} = 150{,}25000");
    expect(pasos[1].latex).toContain("S_Q = 31{,}50000");
  });

  it("kolmogorov_smirnov — define D (A.56)", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "kolmogorov_smirnov",
        estadistico: 0.63246,
        explicacion: { ecuacion: "A.57", terminos: { n1: 20, n2: 20, d: 0.2 } },
      }),
    )!;
    expect(pasos[0].latex).toContain("D = \\max_i");
    expect(pasos[0].latex).toContain("\\dfrac{RS(i)}{n_1} - \\dfrac{RI(i)}{n_2}");
  });

  it("chow — rotula α = 0,10 (no el 0,05 del resto de Etapa 1)", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "chow",
        estadistico: 2.1,
        valor_critico: 2.745,
        explicacion: {
          ecuacion: "Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
          terminos: { n: 30, media_log: 3.5, s_log: 0.4, nu: 28, t_bonferroni: 3.5 },
        },
      }),
    )!;
    expect(pasos[1].latex).toContain("\\alpha = 0{,}10");
    expect(pasos[1].latex).toContain("0{,}05");
  });

  it("todos los pasos de las 8 pruebas compilan con KaTeX real (sin error de sintaxis)", () => {
    const casos: TestResultDetail[] = [
      tr({ prueba: "anderson", estadistico: 0.35, explicacion: { ecuacion: "III-1", terminos: { n: 40, k: 9, numerador: 4378.3, denominador: 12254.3, k_max: 14, lags_fuera: 1, tolerancia: 2 } } }),
      tr({ prueba: "wald_wolfowitz", estadistico: 0.47, explicacion: { ecuacion: "III-4", terminos: { n: 40, n1: 17, n2: 23, r: 22, mu_r: 20.55, sigma_r: 3.05 } } }),
      tr({ prueba: "helmert", estadistico: -3, valor_critico: 6.2, explicacion: { ecuacion: "III-7", terminos: { n: 40, s: 18, c: 21 } } }),
      tr({ prueba: "t_student", estadistico: -1.1, explicacion: { ecuacion: "III-8", terminos: { x1_barra: 152.3, x2_barra: 168.4, sp: 24.6, n1: 20, n2: 20, nu: 38 } } }),
      tr({ prueba: "cramer", estadistico: 0.78, valor_critico: 2.02, explicacion: { ecuacion: "III-15", terminos: { n: 40, n_w1: 24, n_w2: 12, media_global: 150.2, s_global: 31.5, tau_w1: 0.03, tau_w2: 0.19, t_w1: 0.23, t_w2: 0.78, vc_w1: 2.02, vc_w2: 2.02 } } }),
      tr({ prueba: "mann_kendall", estadistico: 0.75, explicacion: { ecuacion: "A.55", terminos: { n: 40, s: 91, var_s: 14291.6 } } }),
      tr({ prueba: "kolmogorov_smirnov", estadistico: 0.63, explicacion: { ecuacion: "A.57", terminos: { n1: 20, n2: 20, d: 0.2 } } }),
      tr({ prueba: "chow", estadistico: 2.1, valor_critico: 2.745, explicacion: { ecuacion: "Bulletin 17B", terminos: { n: 30, media_log: 3.5, s_log: 0.4, nu: 28, t_bonferroni: 3.5 } } }),
    ];
    for (const caso of casos) {
      const pasos = formatearFormulaLatex(caso)!;
      expect(pasos, caso.prueba).toHaveLength(3);
      for (const paso of pasos) {
        // throwOnError: un LaTeX inválido haría caer la pantalla al fallback de texto
        expect(
          () => katex.renderToString(paso.latex, { displayMode: true, throwOnError: true }),
          `${caso.prueba}: ${paso.latex}`,
        ).not.toThrow();
      }
    }
  });

  it("helmert — S − C contra √(n−1), con enteros en la sustitución", () => {
    const pasos = formatearFormulaLatex(
      tr({
        prueba: "helmert",
        estadistico: -3,
        valor_critico: 6.245,
        explicacion: { ecuacion: "III-7", terminos: { n: 40, s: 18, c: 21 } },
      }),
    )!;
    expect(pasos[1].latex).toContain("S - C = 18 - 21");
    expect(pasos[1].latex).toContain("\\sqrt{n-1} = 6{,}24500");
    expect(pasos[2].latex).toBe("S - C = -3{,}00000");
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
