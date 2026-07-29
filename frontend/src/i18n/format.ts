/**
 * Formateo numérico consistente para toda la UI (D3, pasada de mejora).
 *
 * Criterio de decimales — 4, no elegido al azar: es la misma precisión
 * (`abs=1e-4`) que usan los tests de regresión matemática del backend contra
 * la tesis de Facundo (ver `.claude/rules/testing.md`). Si esa es la
 * precisión que el propio proyecto considera significativa para decidir si
 * un resultado es correcto, mostrar más decimales sería falsa precisión, y
 * mostrar menos escondería diferencias que el proyecto sí le importan.
 * Separador decimal es-AR (coma) — convención local (UCC, Córdoba).
 *
 * `null`/`undefined`/`NaN` se muestran como "—" (em dash), el placeholder
 * que ya usaba el código antes de esta normalización.
 */
const DECIMALS = 4;

const numberFormatter = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: DECIMALS,
  maximumFractionDigits: DECIMALS,
});

const intFormatter = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 0,
});

export function formatNum(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return numberFormatter.format(value);
}

// Para conteos (n, n1, n2) — nunca decimales, aunque compartan el mismo
// placeholder de ausencia que formatNum.
export function formatInt(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return intFormatter.format(value);
}
