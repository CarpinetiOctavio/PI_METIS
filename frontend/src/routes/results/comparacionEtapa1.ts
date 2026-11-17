import type { Etapa1Result, TestResultDetail, WarningItem } from "../../api/types";

/**
 * Comparación entre el resultado original de Etapa 1 y el simulado sin los
 * puntos excluidos (ítem A, A2 del plan de feedback de directores). Lógica
 * pura de presentación: no calcula estadística, solo alinea por prueba lo que
 * `core/` ya devolvió en cada corrida y señala qué cambió.
 */

export const GRUPOS_ETAPA1 = [
  { clave: "independencia", etiqueta: "Independencia" },
  { clave: "homogeneidad", etiqueta: "Homogeneidad" },
  { clave: "tendencia", etiqueta: "Tendencia" },
  { clave: "atipicos", etiqueta: "Atípicos (Chow)" },
] as const;

export interface FilaComparacion {
  grupo: string;
  prueba: string;
  original: TestResultDetail | null;
  simulado: TestResultDetail | null;
  /** El veredicto cambió entre las dos corridas. */
  cambio: boolean;
}

/** Una fila por prueba, en el orden de los grupos. Una prueba que existe en una
 * sola de las corridas también aparece (con `null` del otro lado) y cuenta como
 * cambio: por ejemplo, Chow deja de ejecutarse si la serie queda con un cero. */
export function compararPruebas(original: Etapa1Result, simulado: Etapa1Result): FilaComparacion[] {
  return GRUPOS_ETAPA1.flatMap(({ clave, etiqueta }) => {
    const antes = original[clave];
    const despues = simulado[clave];
    const nombres = [...new Set([...antes, ...despues].map((t) => t.prueba))];
    return nombres.map((prueba) => {
      const o = antes.find((t) => t.prueba === prueba) ?? null;
      const s = despues.find((t) => t.prueba === prueba) ?? null;
      return { grupo: etiqueta, prueba, original: o, simulado: s, cambio: o?.veredicto !== s?.veredicto };
    });
  });
}

/** Avisos de la corrida simulada que la original no tenía — típicamente
 * `CONTRACT_IRREGULAR_SPACING` al quitar un año del medio. */
export function avisosNuevos(original: Etapa1Result, simulado: Etapa1Result): WarningItem[] {
  const previos = new Set(original.warnings.map((w) => w.codigo));
  return simulado.warnings.filter((w) => !previos.has(w.codigo));
}
