import type { CramerParticion } from "../api/types";

/**
 * Bloque F de la revisión manual del 21/10/2026 (D-18, #140): con qué
 * partición corrió Cramer, como ya lo dice el PDF. Los tamaños n₁/n₂ salen del
 * resultado de la prueba: la interfaz no los calcula. Sin partición registrada
 * (análisis viejo, o una sesión que no la trae) no se muestra nada: mejor eso
 * que inventar el 60/30.
 */
export function textoParticionCramer(
  particion: CramerParticion | null | undefined,
  n1: number | null | undefined,
  n2: number | null | undefined,
): string | null {
  if (particion === null || particion === undefined) return null;
  const tamanos = n1 != null && n2 != null ? ` (n₁ = ${n1}, n₂ = ${n2})` : "";
  if (particion === "default") return `últimos 60 % y 30 %${tamanos}`;
  return `personalizada: últimos ${particion.n1_pct} % y ${particion.n2_pct} %${tamanos}`;
}
