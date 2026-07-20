# DECISIÓN 016 — Anderson: k_max = ceil(n/3), no floor(n/3)
**Fecha:** 9 de Julio de 2026
**Estado:** IMPLEMENTADO — verificado contra 6 estaciones del dataset de regresión (est_02 a est_07)

### Contexto
Durante la Auditoría Fase 1, Bloque 2.1 (Independencia), se detectó que
`calcular_anderson` usa `k_max = n // 3` (floor) desde el primer commit
de `independence.py` (db67490, 5 de mayo de 2026) — nunca fue modificado.
La auditoría de regresión (pendientes-facundo.md, sección "Correcciones
pendientes post-auditoría — 09/07/2026") había verificado contra dos
Excels de Facundo que la convención correcta es `ceil(n/3)`, pero el fix
quedó explícitamente diferido ("Aplicar: al cierre de la auditoría de
regresión") y nunca se aplicó al código.

### Naturaleza de esta decisión — distinta de [DECISIÓN 013](decision013.md)
[DECISIÓN 013](decision013.md) (asimetría g, ddof) resuelve un conflicto entre una fórmula
escrita en la tesis (IV-4/IV-5, ddof=0) y el comportamiento del Excel de
Facundo (SKEW(), ddof=1) — ahí la tesis manda porque es la fuente
autoritativa y el Excel contradice una fórmula explícita.

Este caso es distinto: la tesis define "k = 1,2,...,n_j/3" sin especificar
ninguna convención de redondeo. No hay una fórmula escrita que el Excel
contradiga — es una ambigüedad genuina del texto, no un conflicto
tesis-vs-Excel. Ante dos convenciones matemáticamente válidas (floor y
ceil, ninguna corrige un error demostrable de la otra), se adopta
`ceil(n/3)` porque es la convención documentada del autor de la tesis, y
en ausencia de un criterio matemático superior comprobable, replicar su
convención minimiza discrepancias contra el dataset de referencia sin
sacrificar corrección.

**Esto NO es precedente para tratar el Excel de Facundo como autoritativo
en general** — sigue sin serlo cuando contradice una fórmula escrita
(ver [DECISIÓN 013](decision013.md)). Aplica únicamente a ambigüedades genuinas del texto
donde no hay fórmula explícita que arbitrar.

### Casos no reproducibles (excepciones conocidas, no bloqueantes)
pendientes-facundo.md documenta dos casos donde ni floor ni ceil
reproducen el k_max que Facundo aparentemente usó a mano: n=24 (Facundo
usó k=9; floor=ceil=8) y n=39 (Facundo usó k=14; floor=ceil=13).
Marcados como posible error manual de Facundo, pendiente de confirmación
formal. No afectan el veredicto en ninguna estación auditada.

### Verificación tras aplicar el fix
Se corrió `calcular_anderson()` (código real, no cálculo paralelo) contra
las 6 estaciones disponibles del dataset de regresión:

| Estación | n | floor(n/3) | ceil(n/3) | veredicto METIS | veredicto tesis |
|----------|---|------------|-----------|------------------|------------------|
| est_02   | 24| 8          | 8         | aprobada         | aprobada         |
| est_03   | 41| 13         | 14        | aprobada         | aprobada         |
| est_04   | 36| 12         | 12        | aprobada         | aprobada         |
| est_05   | 39| 13         | 13        | aprobada         | aprobada         |
| est_06   | 38| 12         | 13        | aprobada         | aprobada         |
| est_07   | 19| 6          | 7         | aprobada         | aprobada         |

6/6 coinciden. est_03, est_06 y est_07 son casos reales donde floor≠ceil;
en los tres, el lag adicional que agrega `ceil` queda dentro de banda —
no cambia `lags_fuera`, `estadistico` ni `valor_critico` respecto de floor,
pero corrige la definición de `k_max` en sí para cuando sí importe.

### Interacción con [DECISIÓN 012](decision012.md) (umbral 10% del veredicto)
[DECISIÓN 012](decision012.md) (`aprobada = lags_fuera <= math.ceil(k_max * 0.10)`) fue
validada originalmente con est_02 (n=24), donde floor=ceil=8 — ese caso
no discrimina entre las dos convenciones de `k_max`. Se revalidó el
criterio compuesto completo (`ceil(n/3)` + `ceil(k_max*0.10)`) contra
est_03 (floor≠ceil, k_max=14): `ceil(14*0.10)=2`, `lags_fuera=1 ≤ 2` →
aprobada, coincide con la tesis. El criterio compuesto sigue siendo
correcto tras el cambio de `k_max`.

### Archivos modificados
- `metis/core/etapa1/independence.py` — `calcular_anderson`:
  `k_max = n // 3` → `k_max = math.ceil(n / 3)`
- `tests/unit/core/test_independence.py`:
  - `test_anderson_un_lag_fuera_aprueba_tolerancia_10pct` — actualizado
    de `k_max = n // 3` a `k_max = math.ceil(n / 3)` (serie_facundo, n=40:
    k_max pasa de 13 a 14; lags_fuera se mantiene en 1, veredicto no cambia)
  - `test_anderson_k_max_ceil_no_floor_est03` — nuevo, usa la serie real
    de est_03 (n=41, floor≠ceil) para verificar el valor de `k_max` y el
    veredicto contra un cálculo independiente con `ceil(n/3)`
- `.claude/rules/regression/pendientes-facundo.md` — sección "Anderson
  k_max — ceil(n/3)" marcada como aplicada, ya no pendiente
