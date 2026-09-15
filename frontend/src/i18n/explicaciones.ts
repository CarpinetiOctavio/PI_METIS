import type { TestResultDetail } from "../api/types";
import { formatInt, formatNum } from "./format";

/**
 * Bloque D del plan post-avance (DECISIÓN 064) — modo paso a paso deja de
 * ser un acordeón vacío. `core/` ya calculó y expone los términos
 * intermedios de cada prueba (`TestResultDetail.explicacion`); este módulo
 * SOLO renderiza — sustituye esos términos en una plantilla de texto y arma
 * una interpretación en castellano. Nunca deriva un estadístico nuevo: la
 * única aritmética que hace (ej. el denominador de t de Student) es
 * cosmética, para mostrar un número que `core/` ya usó para llegar a
 * `estadistico`, no para producir un resultado distinto.
 *
 * Renderizado — F3 (feedback de Facundo, 02/09/2026), addendum a DECISIÓN
 * 064: `formatearFormulaLatex()` devuelve la fórmula en tres pasos LaTeX
 * (expresión simbólica → sustitución numérica → resultado) para renderizar
 * con KaTeX en bloque. `formatearFormula()` (texto plano de una línea) se
 * conserva sin cambios: es el `fallback` de cada paso si KaTeX no puede
 * parsearlo. Ninguna de las dos deriva un estadístico nuevo — la única
 * aritmética que hacen es cosmética (el denominador de t de Student).
 */

const SUBSCRIPT_DIGITS = "₀₁₂₃₄₅₆₇₈₉";

function subscript(n: number): string {
  return String(n)
    .split("")
    .map((d) => SUBSCRIPT_DIGITS[Number(d)] ?? d)
    .join("");
}

function fmt(v: number | null | undefined): string {
  return formatNum(v);
}

type FormulaFn = (tr: TestResultDetail) => string[];

const FORMULAS: Record<string, FormulaFn> = {
  anderson: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      `r${subscript(t.k ?? 0)} = ${fmt(t.numerador)} / ${fmt(t.denominador)} = ${fmt(tr.estadistico)}`,
    ];
  },
  wald_wolfowitz: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      `Z = (R − µ_R) / σ_R = (${fmt(t.r)} − ${fmt(t.mu_r)}) / ${fmt(t.sigma_r)} = ${fmt(tr.estadistico)}`,
    ];
  },
  helmert: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      `S − C = ${fmt(t.s)} − ${fmt(t.c)} = ${fmt(tr.estadistico)}  (límite √(n−1) = ${fmt(tr.valor_critico)})`,
    ];
  },
  t_student: (tr) => {
    const t = tr.explicacion!.terminos;
    const denom =
      t.sp !== null && t.n1 !== null && t.n2 !== null
        ? t.sp * Math.sqrt(1 / t.n1 + 1 / t.n2)
        : null;
    return [
      `t = (x̄₁ − x̄₂) / (Sp·√(1/n₁+1/n₂)) = (${fmt(t.x1_barra)} − ${fmt(t.x2_barra)}) / ${fmt(denom)} = ${fmt(tr.estadistico)}`,
    ];
  },
  cramer: (tr) => {
    const t = tr.explicacion!.terminos;
    const signo1 = (t.t_w1 ?? 0) <= (t.vc_w1 ?? 0) ? "≤" : ">";
    const signo2 = (t.t_w2 ?? 0) <= (t.vc_w2 ?? 0) ? "≤" : ">";
    return [
      `Bloque 60% (n_w₁=${t.n_w1}): τ_w₁ = ${fmt(t.tau_w1)}, t_w₁ = ${fmt(t.t_w1)} ${signo1} ${fmt(t.vc_w1)}`,
      `Bloque 30% (n_w₂=${t.n_w2}): τ_w₂ = ${fmt(t.tau_w2)}, t_w₂ = ${fmt(t.t_w2)} ${signo2} ${fmt(t.vc_w2)}`,
    ];
  },
  mann_kendall: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      `S = ${fmt(t.s)}, Var(S) = ${fmt(t.var_s)} → Z (aproximación normal con corrección por empates, Kendall 1975) = ${fmt(tr.estadistico)}`,
    ];
  },
  kolmogorov_smirnov: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      `Z = D·√(n₁·n₂/(n₁+n₂)) = ${fmt(t.d)}·√(${t.n1}·${t.n2}/(${(t.n1 ?? 0) + (t.n2 ?? 0)})) = ${fmt(tr.estadistico)}`,
    ];
  },
  chow: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      `K_N = (n−1)/√n · √(t²/(n−2+t²)) = ${fmt(tr.valor_critico)}  (t = t_{n−2,1−α/(2n)} = ${fmt(t.t_bonferroni)}, n=${t.n})`,
    ];
  },
};

/** Líneas de la fórmula sustituida, o `null` si la prueba no tiene
 * `explicacion` (no_ejecutada — nada que sustituir) o no está mapeada.
 * Texto plano de una línea — hoy solo se usa como `fallback` de cada paso
 * LaTeX (ver `formatearFormulaLatex`), no se renderiza directo. */
export function formatearFormula(tr: TestResultDetail): string[] | null {
  if (!tr.explicacion) return null;
  return FORMULAS[tr.prueba]?.(tr) ?? null;
}

/** Un paso de la fórmula: LaTeX para KaTeX + su equivalente en texto plano
 * (fallback si KaTeX no puede renderizar el LaTeX). */
export interface PasoFormula {
  latex: string;
  fallback: string;
}

// Número para LaTeX: sin separador de miles (roba legibilidad en notación
// matemática), coma decimal es-AR escapada como `{,}` para que KaTeX no le
// aplique el espaciado de lista. "—" si no hay valor.
function ltx(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "\\text{—}";
  return formatNum(v).replace(/\./g, "").replace(",", "{,}");
}

// Conteos (n, k, n1, n2, ...): enteros, sin `.00000`.
function ltxInt(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "\\text{—}";
  return formatInt(v).replace(/\./g, "");
}

type FormulaLatexFn = (tr: TestResultDetail) => PasoFormula[];

const FORMULAS_LATEX: Record<string, FormulaLatexFn> = {
  anderson: (tr) => {
    const t = tr.explicacion!.terminos;
    const k = ltxInt(t.k ?? 0);
    return [
      {
        latex: `r_{k} = \\dfrac{\\sum_{i=1}^{n-k}(x_i-\\bar{x})(x_{i+k}-\\bar{x})}{\\sum_{i=1}^{n}(x_i-\\bar{x})^{2}}`,
        fallback: "r_k = Σ(xi−x̄)(x_{i+k}−x̄) / Σ(xi−x̄)²",
      },
      {
        latex: `r_{${k}} = \\dfrac{${ltx(t.numerador)}}{${ltx(t.denominador)}}`,
        fallback: `r${subscript(t.k ?? 0)} = ${fmt(t.numerador)} / ${fmt(t.denominador)}`,
      },
      {
        latex: `r_{${k}} = ${ltx(tr.estadistico)}`,
        fallback: `r${subscript(t.k ?? 0)} = ${fmt(tr.estadistico)}`,
      },
    ];
  },
  wald_wolfowitz: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      {
        latex: `Z = \\dfrac{R - \\mu_R}{\\sigma_R}`,
        fallback: "Z = (R − µ_R) / σ_R",
      },
      {
        latex: `Z = \\dfrac{${ltxInt(t.r)} - ${ltx(t.mu_r)}}{${ltx(t.sigma_r)}}`,
        fallback: `Z = (${fmt(t.r)} − ${fmt(t.mu_r)}) / ${fmt(t.sigma_r)}`,
      },
      { latex: `Z = ${ltx(tr.estadistico)}`, fallback: `Z = ${fmt(tr.estadistico)}` },
    ];
  },
  helmert: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      {
        latex: `S - C \\quad \\text{contra} \\quad \\sqrt{n-1}`,
        fallback: "S − C  contra  √(n−1)",
      },
      {
        latex: `S - C = ${ltxInt(t.s)} - ${ltxInt(t.c)} \\qquad \\sqrt{n-1} = ${ltx(tr.valor_critico)}`,
        fallback: `S − C = ${fmt(t.s)} − ${fmt(t.c)}   (límite √(n−1) = ${fmt(tr.valor_critico)})`,
      },
      {
        latex: `S - C = ${ltx(tr.estadistico)}`,
        fallback: `S − C = ${fmt(tr.estadistico)}`,
      },
    ];
  },
  t_student: (tr) => {
    const t = tr.explicacion!.terminos;
    const denom =
      t.sp !== null && t.n1 !== null && t.n2 !== null
        ? t.sp * Math.sqrt(1 / t.n1 + 1 / t.n2)
        : null;
    return [
      {
        latex: `t = \\dfrac{\\bar{x}_1 - \\bar{x}_2}{S_p\\sqrt{\\tfrac{1}{n_1}+\\tfrac{1}{n_2}}}`,
        fallback: "t = (x̄₁ − x̄₂) / (Sp·√(1/n₁+1/n₂))",
      },
      {
        // El denominador no viaja en `terminos` — se reconstruye acá para
        // mostrarlo (misma aritmética cosmética que ya hacía la versión de
        // texto, DECISIÓN 064). No es un estadístico nuevo.
        latex: `t = \\dfrac{${ltx(t.x1_barra)} - ${ltx(t.x2_barra)}}{${ltx(denom)}}`,
        fallback: `t = (${fmt(t.x1_barra)} − ${fmt(t.x2_barra)}) / ${fmt(denom)}`,
      },
      { latex: `t = ${ltx(tr.estadistico)}`, fallback: `t = ${fmt(tr.estadistico)}` },
    ];
  },
  cramer: (tr) => {
    const t = tr.explicacion!.terminos;
    const signo1 = (t.t_w1 ?? 0) <= (t.vc_w1 ?? 0) ? "\\le" : ">";
    const signo2 = (t.t_w2 ?? 0) <= (t.vc_w2 ?? 0) ? "\\le" : ">";
    const asciiSigno1 = (t.t_w1 ?? 0) <= (t.vc_w1 ?? 0) ? "≤" : ">";
    const asciiSigno2 = (t.t_w2 ?? 0) <= (t.vc_w2 ?? 0) ? "≤" : ">";
    return [
      {
        latex: `t_w = \\sqrt{\\dfrac{n_w\\,(n-2)}{\\,n - n_w\\,(1+\\tau_w^{2})}}\\;\\lvert\\tau_w\\rvert`,
        fallback: "t_w = √[ n_w·(n−2) / (n − n_w·(1+τ_w²)) ] · |τ_w|",
      },
      {
        latex: `\\text{Bloque 60\\%}\\;(n_{w_1}=${ltxInt(t.n_w1)}):\\quad \\tau_{w_1} = ${ltx(t.tau_w1)},\\quad t_{w_1} = ${ltx(t.t_w1)} ${signo1} ${ltx(t.vc_w1)}`,
        fallback: `Bloque 60% (n_w₁=${t.n_w1}): τ_w₁ = ${fmt(t.tau_w1)}, t_w₁ = ${fmt(t.t_w1)} ${asciiSigno1} ${fmt(t.vc_w1)}`,
      },
      {
        latex: `\\text{Bloque 30\\%}\\;(n_{w_2}=${ltxInt(t.n_w2)}):\\quad \\tau_{w_2} = ${ltx(t.tau_w2)},\\quad t_{w_2} = ${ltx(t.t_w2)} ${signo2} ${ltx(t.vc_w2)}`,
        fallback: `Bloque 30% (n_w₂=${t.n_w2}): τ_w₂ = ${fmt(t.tau_w2)}, t_w₂ = ${fmt(t.t_w2)} ${asciiSigno2} ${fmt(t.vc_w2)}`,
      },
    ];
  },
  mann_kendall: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      {
        latex: `S = \\sum_{i<j}\\operatorname{sgn}(x_j - x_i)`,
        fallback: "S = Σ_{i<j} sgn(xj − xi)",
      },
      {
        latex: `S = ${ltx(t.s)},\\qquad \\operatorname{Var}(S) = ${ltx(t.var_s)}`,
        fallback: `S = ${fmt(t.s)}, Var(S) = ${fmt(t.var_s)}`,
      },
      {
        // Sin fórmula inventada para la tipificación con corrección por
        // empates (DECISIÓN 064) — se nombra en prosa, Z viene de `core/`.
        latex: `Z = ${ltx(tr.estadistico)} \\quad \\text{(aprox. normal con corrección por empates, Kendall 1975)}`,
        fallback: `Z (aproximación normal con corrección por empates, Kendall 1975) = ${fmt(tr.estadistico)}`,
      },
    ];
  },
  kolmogorov_smirnov: (tr) => {
    const t = tr.explicacion!.terminos;
    const suma = (t.n1 ?? 0) + (t.n2 ?? 0);
    return [
      {
        latex: `Z = D\\sqrt{\\dfrac{n_1\\,n_2}{n_1 + n_2}}`,
        fallback: "Z = D·√(n₁·n₂/(n₁+n₂))",
      },
      {
        latex: `Z = ${ltx(t.d)}\\,\\sqrt{\\dfrac{${ltxInt(t.n1)}\\cdot ${ltxInt(t.n2)}}{${ltxInt(suma)}}}`,
        fallback: `Z = ${fmt(t.d)}·√(${t.n1}·${t.n2}/(${suma}))`,
      },
      { latex: `Z = ${ltx(tr.estadistico)}`, fallback: `Z = ${fmt(tr.estadistico)}` },
    ];
  },
  chow: (tr) => {
    const t = tr.explicacion!.terminos;
    return [
      {
        latex: `K_N = \\dfrac{n-1}{\\sqrt{n}}\\sqrt{\\dfrac{t^{2}}{\\,n-2+t^{2}}}`,
        fallback: "K_N = (n−1)/√n · √(t²/(n−2+t²))",
      },
      {
        latex: `t = t_{\\,n-2,\\;1-\\alpha/(2n)} = ${ltx(t.t_bonferroni)},\\qquad n = ${ltxInt(t.n)}`,
        fallback: `t = t_{n−2,1−α/(2n)} = ${fmt(t.t_bonferroni)}, n=${t.n}`,
      },
      {
        latex: `K_N = ${ltx(tr.valor_critico)}`,
        fallback: `K_N = ${fmt(tr.valor_critico)}`,
      },
    ];
  },
};

/** Fórmula sustituida en pasos LaTeX (simbólica → sustitución → resultado),
 * o `null` si la prueba no tiene `explicacion` (no_ejecutada) o no está
 * mapeada. Cada paso trae su `fallback` de texto plano. */
export function formatearFormulaLatex(tr: TestResultDetail): PasoFormula[] | null {
  if (!tr.explicacion) return null;
  return FORMULAS_LATEX[tr.prueba]?.(tr) ?? null;
}

type InterpretadorFn = (tr: TestResultDetail) => string;

const INTERPRETACIONES: Record<string, InterpretadorFn> = {
  anderson: (tr) => {
    const t = tr.explicacion!.terminos;
    const aprobada = tr.veredicto === "aprobada";
    return `${t.lags_fuera} de ${t.k_max} lags calculados caen fuera de las bandas de independencia — ${aprobada ? "dentro" : "por encima"} de la tolerancia del 10% (máximo ${t.tolerancia}), así que ${aprobada ? "no hay evidencia de dependencia serial" : "hay evidencia de dependencia serial"}.`;
  },
  wald_wolfowitz: (tr) => {
    const dentro = tr.veredicto === "aprobada";
    return `El estadístico (${fmt(tr.estadistico)}) está ${dentro ? "dentro" : "fuera"} del rango crítico (±${fmt(tr.valor_critico)}) — ${dentro ? "consistente con independencia" : "sugiere dependencia en el orden de los datos"}. Wald-Wolfowitz es una verificación: Anderson manda en el veredicto final, aunque los dos discrepen.`;
  },
  helmert: (tr) => {
    const dentro = tr.veredicto === "aprobada";
    return `|S − C| está ${dentro ? "dentro" : "fuera"} del límite √(n−1) (${fmt(tr.valor_critico)}) — ${dentro ? "sin evidencia de" : "con evidencia de"} un cambio de régimen en el orden de signos de la serie.`;
  },
  t_student: (tr) => {
    const dentro = tr.veredicto === "aprobada";
    return `El estadístico (${fmt(tr.estadistico)}) está ${dentro ? "dentro" : "fuera"} del rango crítico (±${fmt(tr.valor_critico)}), así que ${dentro ? "no hay evidencia de" : "hay evidencia de"} un cambio de media entre las dos mitades del registro.`;
  },
  cramer: (tr) => {
    const t = tr.explicacion!.terminos;
    const b1 = (t.t_w1 ?? 0) <= (t.vc_w1 ?? 0);
    const b2 = (t.t_w2 ?? 0) <= (t.vc_w2 ?? 0);
    if (b1 && b2) {
      return `Los dos bloques (60% y 30%) aprueban — ninguno supera el valor crítico (${fmt(t.vc_w1)}) — sin evidencia de cambio de media en ningún tramo reciente del registro.`;
    }
    return `Al menos uno de los dos bloques supera el valor crítico (${fmt(t.vc_w1)}) — alcanza con que uno falle para que Cramer rechace homogeneidad, y Cramer manda sobre Helmert y t de Student.`;
  },
  mann_kendall: (tr) => {
    const dentro = tr.veredicto === "aprobada";
    return `El estadístico Z (${fmt(tr.estadistico)}) está ${dentro ? "dentro" : "fuera"} del rango crítico (±${fmt(tr.valor_critico)}), así que ${dentro ? "no se detecta" : "se detecta"} tendencia monotónica en la serie.`;
  },
  kolmogorov_smirnov: (tr) => {
    const dentro = tr.veredicto === "aprobada";
    return `Z (${fmt(tr.estadistico)}) está ${dentro ? "por debajo" : "por encima"} del valor crítico de tabla (${fmt(tr.valor_critico)}), así que ${dentro ? "no hay evidencia de" : "hay evidencia de"} tendencia al comparar las dos mitades del registro.`;
  },
  chow: (tr) => {
    if (tr.veredicto === "aprobada") {
      return `El desvío estandarizado máximo (${fmt(tr.estadistico)}) no supera K_N (${fmt(tr.valor_critico)}) — ningún dato se marca como atípico.`;
    }
    return `El desvío estandarizado máximo (${fmt(tr.estadistico)}) supera K_N (${fmt(tr.valor_critico)}) — el dato ${fmt(tr.valor_atipico)} queda marcado como atípico, a la espera de tu decisión.`;
  },
};

/** Interpretación en castellano, o `null` si la prueba no tiene
 * `explicacion` o no está mapeada. */
export function interpretar(tr: TestResultDetail): string | null {
  if (!tr.explicacion) return null;
  return INTERPRETACIONES[tr.prueba]?.(tr) ?? null;
}

/** Regla de decisión del grupo — "cuando aplica" (D1): grupos de un solo
 * test (atípicos) no tienen jerarquía que explicar. */
export const REGLA_GRUPO: Record<string, string | null> = {
  independencia:
    "Anderson manda: si Anderson aprueba, el resultado es INDEPENDIENTE aunque Wald-Wolfowitz rechace.",
  homogeneidad:
    "Cramer manda: si Cramer rechaza, el resultado es CRÍTICO — sin importar lo que digan Helmert o t de Student.",
  tendencia:
    "Alcanza con que una rechace: si Mann-Kendall o Kolmogorov-Smirnov detectan tendencia, se advierte — no hace falta que coincidan las dos.",
  atipicos: null,
};
