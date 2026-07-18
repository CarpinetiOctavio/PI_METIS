# DECISIÓN 011 — Fórmula de Cramer: partición y grados de libertad
**Fecha:** 16 de Junio de 2026
**Estado:** IMPLEMENTADO — verificado numéricamente contra tesis Facundo est_02 y est_04

### Contexto
Durante los tests de regresión de est_02 (Vado de Río Seco, n=24) se detectaron
dos divergencias en la prueba de Cramer respecto de los resultados del sheet de Facundo.

### Divergencia 1 — Tamaño del subgrupo n_w2

**Corrección inicial (est_02):** `n_w2 = floor(n × 0.30)` → para n=24: n_w2=7
→ subgrupo = serie[-7:] → tau_w2=0.35206 ✓

Nota: para n=24, floor(7.2)=7 y round(7.2)=7 — coinciden. La ambigüedad no era
detectable con una sola estación.

**Corrección revisada (est_04):** `n_w2 = round(n × 0.30)` → para n=36: n_w2=11
→ subgrupo = serie[-11:] → tau_w2=-0.23676 ✓ (tesis)
floor(36×0.30) = floor(10.8) = 10 → tau_w2=-0.15877 ✗

La regla correcta es `round()`, no `floor()`. Confirmado con dos estaciones.

n_w1 usa `ceil` (correcto, confirmado con est_02 tau_w1=0.18289 ✓ y est_04 tau_w1=-0.186 ✓).

PENDIENTE: confirmación formal de Facundo sobre la función de redondeo en Excel.
Ver pendientes-facundo.md.

### ADDENDUM — 18 de Julio de 2026 — "confirmado" (n_w1) quedó desactualizado
La afirmación de arriba ("n_w1 usa `ceil`, correcto, confirmado") se apoyaba
solo en est_02 y est_04 — y est_04 (n=36) no discrimina entre `ceil` y
`round` para n_w1 (`ceil(21.6)=22`, `round(21.6)=22`, coinciden). Auditoría
de Fase 4 (est_07, est_09) sumó dos estaciones que sí discriminan, con
resultado contradictorio: est_07 (n=19) reproduce la tesis con
`round`/`floor` (n_w1=11), no con `ceil` (que da 12). Censo completo contra
las 4 estaciones que efectivamente discriminan entre las dos reglas:
est_02 y est_05 confirman `ceil`; est_07 y est_09 confirman `round`/`floor`.
**Empate real 2 a 2** — no hay preferencia estadística entre las dos
convenciones para n_w1. Detalle completo, censo estación por estación, en
`pendientes-facundo.md`. El código no cambió (`ceil` sigue siendo la regla
implementada — no tiene más respaldo que la alternativa, pero tampoco menos).
La palabra "confirmado" de la Divergencia 1 debe leerse con esta salvedad.

### Divergencia 2 — Grados de libertad del valor crítico

**Comportamiento anterior:** `ν_w = n + n_w - 2`
→ ν_w1=36 (crit≈2.026), ν_w2=29 (crit≈2.042) — no coincide con sheet

**Corrección:** `ν = n - 2` para ambos subgrupos
→ ν=22 (crit=2.0739) para est_02 ✓; ν=34 (crit=2.0322) para est_04 ✓

La tesis escribe "ν = n₁ + n₂ - 2" en p.51, pero los resultados numéricos
del sheet de Facundo (est_02, est_03, est_04) son consistentes con ν = n - 2.
Ante discrepancia texto/práctica, se prioriza la práctica numérica de la
fuente bibliográfica primaria.

PENDIENTE: confirmación formal de Facundo sobre la fórmula de ν.

### Archivos modificados
- `metis/core/homogeneity.py` — calcular_cramer: ceil→round para n_w2, nu=n-2
- `.claude/rules/formulas-etapa1.md` — sección Cramer actualizada con esta decisión
