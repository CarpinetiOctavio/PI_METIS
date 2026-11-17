import type { MetodoStatus } from "../api/types";

// Rótulo de cada status de una combinación distribución+método de Etapa 2.
export const STATUS_LABEL: Record<MetodoStatus, string> = {
  ok: "ajustado",
  no_converge: "no converge",
  no_aplicable: "no aplicable",
  disabled_zeros: "deshabilitada por ceros",
  disabled_negatives: "no aplica: la serie tiene valores negativos",
};

/**
 * Por qué una combinación no tiene eventos de diseño sin los puntos excluidos
 * (`seleccion.estado` de POST /analysis/simulate-exclusion, revisión de
 * DECISIÓN 071 del 18/10/2026). Mismo tono que el aviso de "no hay Etapa 2 que
 * recalcular".
 */
export function textoSinAjusteSimulado(
  distribucion: string,
  metodo: string,
  estado: MetodoStatus,
  aniosExcluidos: string,
): string {
  return (
    `Sin los años ${aniosExcluidos}, ${distribucion} · ${metodo} no se puede ajustar ` +
    `(${STATUS_LABEL[estado]}), así que no hay eventos de diseño que mostrar en esta vista.`
  );
}
