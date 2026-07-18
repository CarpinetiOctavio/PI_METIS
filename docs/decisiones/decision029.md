# DECISIÓN 029 — GVE ML: error de orden de serie en IV-243/244
**Fecha:** 19 de Mayo de 2026
**Estado:** IMPLEMENTADO — bug de implementación corregido

**Nota de procedencia (agregada 18/07/2026, migración a archivos individuales):**
este bloque vivió sin número de decisión desde su creación (título original
"RESUELTO — GVE ML...") hasta esta migración. La fecha de arriba (19 de
mayo de 2026) es la del fix real, preservada tal cual — es la
semánticamente relevante. El bloque en sí se agregó a `decisions-log.md`
el 18 de junio de 2026 (commit `b0b9196`), casi un mes después del fix,
junto con el trabajo de regresión de est_02 — confirmado con
`git log -S` sobre el texto del header original.

No era inconsistencia en la tesis sino error de implementación.
La tesis p.81 especifica explícitamente que la serie debe ordenarse
DE MAYOR A MENOR para IV-243 y IV-244. El código ordenaba de menor
a mayor. Con orden descendente, (2·M̂(1) - M̂(0)) resulta positivo,
C > 0, α̂ > 0.
Fix: `xs = np.sort(serie)[::-1]` en `_momentos_L()`.

Smoke test post-fix (serie_facundo, n=40):
- ml: nu=89.50, alpha=20.61, beta=0.071, Q100=170.44, EEA=46.71 ✓
