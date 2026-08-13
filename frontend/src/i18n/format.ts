/**
 * Formateo numérico consistente para toda la UI (D3, pasada de mejora 2;
 * subido a 5 decimales en F4, pasada de mejora 3 — decisión de Kevin).
 *
 * Criterio de decimales — 5, no elegido al azar: es la precisión con la que
 * la tesis de Facundo imprime sus propios resultados de referencia (ver
 * `.claude/rules/core/formulas-etapa1.md` §6 — `tau_w1=0.18289`,
 * `tau_w2=0.35206`, `t_w1=1.13970`, `t_w2=1.08774`), que es contra lo que un
 * docente va a comparar la pantalla a mano. El criterio anterior (4
 * decimales, tolerancia `abs=1e-4` de los tests de regresión de
 * `testing.md`) era válido pero medía la precisión equivocada: la de cuándo
 * el backend considera "igual" a dos resultados internamente, no la de cómo
 * la fuente bibliográfica primaria reporta los suyos — y esa segunda es el
 * criterio que rige el resto del proyecto (ninguna fórmula se implementa sin
 * referencia explícita a la tesis). Separador decimal es-AR (coma) —
 * convención local (UCC, Córdoba).
 *
 * Limitación aceptada, no resuelta acá: con decimales fijos, un valor mucho
 * menor que `1e-5` (ej. un `r_k` de Anderson muy chico) se muestra como
 * `0,00000`. Si el relleno de ceros molesta visualmente en las tablas
 * reales, `minimumFractionDigits: 0` lo elimina sin tocar el tope de 5 — es
 * un cambio de un carácter, no una razón para no subir la precisión ahora.
 *
 * `null`/`undefined`/`NaN` se muestran como "—" (em dash), el placeholder
 * que ya usaba el código antes de esta normalización.
 */
const DECIMALS = 5;

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

// Ejes de gráficos: los 5 decimales de formatNum() son para tablas de
// resultados, donde el docente compara contra la tesis. En un eje solo
// roban ancho y obligan a un margen enorme.
const axisFormatter = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 2,
});

export function formatAxis(value: number): string {
  return axisFormatter.format(value);
}
