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

// Los tests de formato son dirigidos por datos: cada fila declara, por línea o
// paso de la salida, los textos que debe contener (`contiene`), los que debe
// ser exactamente (`igual`) y los que ninguna pieza puede contener (`ausente`).
// Tests consecutivos con la misma estructura (`const [x] = f(caso(..)); expect
// (x).toContain(..)`) son "código duplicado" para SonarCloud aunque cambien los
// literales — una tabla y un solo cuerpo de test lo evitan sin perder cobertura.
interface CasoFormato {
  nombre: string;
  prueba: string;
  overrides?: Partial<TestResultDetail>;
  terminos?: Terminos;
  contiene: string[][];
  igual?: Record<number, string>;
  ausente?: string[];
}

function verificar(piezas: string[], esperado: CasoFormato) {
  expect(piezas).toHaveLength(esperado.contiene.length);
  esperado.contiene.forEach((textos, i) => {
    for (const texto of textos) expect(piezas[i]).toContain(texto);
  });
  for (const [i, texto] of Object.entries(esperado.igual ?? {})) {
    expect(piezas[Number(i)]).toBe(texto);
  }
  for (const texto of esperado.ausente ?? []) {
    for (const pieza of piezas) expect(pieza).not.toContain(texto);
  }
}

// formatearFormula(): texto plano, una entrada por línea.
const FORMULAS_PLANAS: CasoFormato[] = [
  {
    nombre: "anderson — reproduce el estadístico con numerador/denominador del lag reportado",
    prueba: "anderson",
    contiene: [["r₉", "0,35734"]],
  },
  {
    nombre: "wald_wolfowitz — reproduce Z a partir de R, µ_R y σ_R",
    prueba: "wald_wolfowitz",
    contiene: [["Z = (R − µ_R) / σ_R", "22", "0,47555"]],
  },
  {
    nombre: "helmert — muestra S − C junto con el límite (valor_critico)",
    prueba: "helmert",
    contiene: [["S − C = 18,00000 − 21,00000 = -3,00000", "6,24500"]],
  },
  {
    // El denominador no viaja en terminos — se reconstruye acá para
    // mostrarlo, coincide con sp*sqrt(1/n1+1/n2) ≈ 7.777.
    nombre: "t_student — reconstruye el denominador Sp·√(1/n1+1/n2) para mostrarlo",
    prueba: "t_student",
    contiene: [["152,31000", "168,44000", "-1,14937"]],
  },
  {
    // Sin "60%"/"30%": con partición personalizada (DECISIÓN 036) serían falsos.
    nombre: "cramer — muestra los DOS bloques, no solo el binding",
    prueba: "cramer",
    contiene: [
      ["Bloque 1", "n_w₁=24"],
      ["Bloque 2", "n_w₂=12"],
    ],
    ausente: ["%"],
  },
  {
    nombre:
      "mann_kendall — muestra S, Var(S) y Z = (S − sgn(S))/√Var(S), sin atribuir a A.55 la corrección por empates",
    prueba: "mann_kendall",
    contiene: [["S = 91,00000", "Z = (S − sgn(S)) / √Var(S)", "0,75280"]],
    ausente: ["Kendall 1975"],
  },
  {
    nombre: "kolmogorov_smirnov — reproduce Z = D·√(n1·n2/(n1+n2))",
    prueba: "kolmogorov_smirnov",
    contiene: [["D·√(n₁·n₂/(n₁+n₂))", "0,63246"]],
  },
  {
    // α = 0,10, no el 0,05 del resto de Etapa 1
    nombre: "chow — muestra K_N, el t Bonferroni-corregido y α = 0,10",
    prueba: "chow",
    contiene: [["K_N", "2,74500", "t_{n−2,1−α/(2n)} = 3,50000", "α = 0,10"]],
  },
];

// formatearFormulaLatex(): tres pasos (simbólica → sustitución → resultado).
const FORMULAS_LATEX: CasoFormato[] = [
  {
    // coma decimal es-AR escapada como {,}, sin separador de miles
    nombre: "anderson — sustituye numerador/denominador y reproduce el estadístico en LaTeX",
    prueba: "anderson",
    contiene: [["\\dfrac"], ["\\dfrac{4378{,}38600}{12254{,}30800}"], []],
    igual: { 2: "r_{9} = 0{,}35734" },
  },
  {
    nombre:
      "anderson — el paso simbólico incluye las bandas de III-3 y la regla del 10%; la sustitución cita los lags fuera",
    prueba: "anderson",
    contiene: [
      [
        "r_{k}(95\\%) = \\dfrac{-1 \\pm 1{,}96\\sqrt{n-k-1}}{n-k}",
        "no más del 10\\% de los",
      ],
      ["\\text{Lags fuera de las bandas: } 1 \\text{ de } 14", "\\text{tolerancia: } 2"],
      [],
    ],
  },
  {
    nombre: "wald_wolfowitz — R entero, µ_R y σ_R con decimales, Z del estadístico",
    prueba: "wald_wolfowitz",
    contiene: [
      ["\\dfrac{R - \\mu_R}{\\sigma_R}"],
      ["\\dfrac{22 - 20{,}55000}{3{,}04939}"],
      [],
    ],
    igual: { 2: "Z = 0{,}47555" },
  },
  {
    nombre: "wald_wolfowitz — define µ_R y σ_R (III-5/III-6) y los sustituye con los valores de core",
    prueba: "wald_wolfowitz",
    contiene: [
      [
        "\\mu_R = \\dfrac{2\\,n_1 n_2}{n} + 1",
        "\\sigma_R = \\sqrt{\\dfrac{(\\mu_R-1)(\\mu_R-2)}{n-1}}",
      ],
      ["\\mu_R = \\dfrac{2\\cdot 17\\cdot 23}{40} + 1 = 20{,}55000", "= 3{,}04939"],
      [],
    ],
  },
  {
    nombre: "helmert — S − C contra √(n−1), con enteros en la sustitución",
    prueba: "helmert",
    contiene: [[], ["S - C = 18 - 21", "\\sqrt{n-1} = 6{,}24500"], []],
    igual: { 2: "S - C = -3{,}00000" },
  },
  {
    // 24.6 * sqrt(1/20 + 1/20) = 24.6 * sqrt(0.1) ≈ 7.77920
    nombre: "t_student — reconstruye el denominador Sp·√(1/n1+1/n2) en el paso de sustitución",
    prueba: "t_student",
    contiene: [[], ["152{,}31000 - 168{,}44000", "7{,}77920"], []],
    igual: { 2: "t = -1{,}14937" },
  },
  {
    nombre: "t_student — define S_p² y aclara qué varianza usa",
    prueba: "t_student",
    contiene: [
      [
        "S_p^{2} = \\dfrac{n_1 s_1^{2} + n_2 s_2^{2}}{n_1+n_2-2}",
        "varianza muestral (divisor }n_i-1",
      ],
      ["S_p = 24{,}60000"],
      [],
    ],
  },
  {
    // Bloque 2 rechaza: t_w2 (3.0) > vc_w2 (2.02439) → signo ">". Rótulos por
    // n_w, nunca por porcentaje (partición personalizada, DECISIÓN 036).
    nombre: "cramer — tres pasos: fórmula genérica + los DOS bloques con su signo",
    prueba: "cramer",
    overrides: { estadistico: 3.0 },
    terminos: { tau_w2: 0.5, t_w2: 3.0 },
    contiene: [
      [],
      ["Bloque 1", "t_{w_1} = 0{,}23585 \\le 2{,}02439"],
      ["Bloque 2", "t_{w_2} = 3{,}00000 > 2{,}02439"],
    ],
    ausente: ["\\%"],
  },
  {
    nombre: "cramer — define τ_w y S_Q, y muestra la media y el desvío globales",
    prueba: "cramer",
    contiene: [
      ["\\tau_w = \\dfrac{\\bar{Q}_w - \\bar{Q}}{S_Q}", "S_Q = \\sqrt{\\dfrac{1}{n-1}"],
      ["\\bar{Q} = 150{,}25000", "S_Q = 31{,}50000"],
      [],
    ],
  },
  {
    // Paso simbólico: Var(S) sin empates (A.55) y la tipificación con
    // corrección de continuidad.
    nombre:
      "mann_kendall — muestra S, Var(S) y la tipificación Z, sin atribuir a A.55 la corrección por empates",
    prueba: "mann_kendall",
    contiene: [
      [
        "\\dfrac{n(n-1)(2n+5)}{18}",
        "\\dfrac{S-\\operatorname{sgn}(S)}{\\sqrt{\\operatorname{Var}(S)}}",
      ],
      ["S = 91{,}00000", "\\operatorname{Var}(S) = 14291{,}66700"],
      ["Z = 0{,}75280", "corrección de continuidad"],
    ],
    ausente: ["Kendall 1975"],
  },
  {
    nombre: "kolmogorov_smirnov — Z = D·√(n1·n2/(n1+n2)) con la suma sustituida",
    prueba: "kolmogorov_smirnov",
    contiene: [["D\\sqrt"], ["\\dfrac{20\\cdot 20}{40}"], []],
    igual: { 2: "Z = 0{,}63246" },
  },
  {
    nombre: "kolmogorov_smirnov — define D (A.56)",
    prueba: "kolmogorov_smirnov",
    contiene: [["D = \\max_i", "\\dfrac{RS(i)}{n_1} - \\dfrac{RI(i)}{n_2}"], [], []],
  },
  {
    nombre: "chow — K_N y el t Bonferroni-corregido, resultado = valor_critico",
    prueba: "chow",
    contiene: [
      ["K_N = \\dfrac{n-1}{\\sqrt{n}}"],
      ["t_{\\,n-2,\\;1-\\alpha/(2n)} = 3{,}50000", "n = 30"],
      [],
    ],
    igual: { 2: "K_N = 2{,}74500" },
  },
  {
    nombre: "chow — rotula α = 0,10 (no el 0,05 del resto de Etapa 1)",
    prueba: "chow",
    contiene: [[], ["\\alpha = 0{,}10", "0{,}05"], []],
  },
];

describe("formatearFormula", () => {
  it("devuelve null sin explicacion (rama no_ejecutada)", () => {
    expect(formatearFormula(tr({ explicacion: null }))).toBeNull();
  });

  it.each(FORMULAS_PLANAS)("$nombre", (esperado) => {
    const lineas = formatearFormula(caso(esperado.prueba, esperado.overrides, esperado.terminos));
    expect(lineas).not.toBeNull();
    verificar(lineas!, esperado);
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

  it.each(FORMULAS_LATEX)("$nombre", (esperado) => {
    const pasos = formatearFormulaLatex(caso(esperado.prueba, esperado.overrides, esperado.terminos));
    expect(pasos).not.toBeNull();
    verificar(
      pasos!.map((p) => p.latex),
      esperado,
    );
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
