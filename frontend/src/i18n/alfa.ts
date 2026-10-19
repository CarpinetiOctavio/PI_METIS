import type { Alfa } from "../api/types";

// DECISIÓN 078 — los tres niveles de significancia de la Etapa 1. El 5 % es el
// estándar en hidrología (Facundo Ganancias Martínez, 18/10/2026).
export const ALFA_DEFECTO: Alfa = 0.05;

export const NIVELES_ALFA: readonly { valor: Alfa; rotulo: string }[] = [
  { valor: 0.01, rotulo: "1 %" },
  { valor: 0.05, rotulo: "5 % · estándar en hidrología" },
  { valor: 0.1, rotulo: "10 %" },
];

/** "5 %", "10 %", "1 %": α como porcentaje, con coma decimal si la tuviera. */
export function formatAlfa(alfa: number): string {
  return `${String(Math.round(alfa * 1000) / 10).replace(".", ",")} %`;
}

/** Nivel de confianza 1 − α ("95 %"); los análisis anteriores a la DECISIÓN 078
 * no traen α y corrieron con 5 %. */
export function formatConfianza(alfa: number | null | undefined): string {
  return formatAlfa(1 - (alfa ?? ALFA_DEFECTO));
}

/** α de un análisis ya corrido. Sin α registrado (anterior a la DECISIÓN 078),
 * el análisis corrió con 5 %, el único nivel disponible entonces. */
export function textoAlfaAnalisis(alfa: number | null | undefined): string {
  if (alfa == null) return `${formatAlfa(ALFA_DEFECTO)} (el único disponible cuando se corrió)`;
  return alfa === ALFA_DEFECTO ? `${formatAlfa(alfa)} (estándar en hidrología)` : formatAlfa(alfa);
}

/** Un α distinto del 5 % se muestra destacado: cambia qué rechaza cada prueba. */
export function alfaDestacado(alfa: number | null | undefined): boolean {
  return alfa != null && alfa !== ALFA_DEFECTO;
}
