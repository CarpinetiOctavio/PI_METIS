# DECISIÓN 025 — Log-Normal 3p MV: guard de ausencia de óptimo finito
**Fecha:** 15 de Julio de 2026
**Estado:** APLICADA — verificado sin regresión contra las 9 estaciones
**Origen:** Auditoría Fase 4 (E2E), est_09 (n=7) — verificación cruzada Octavio↔Code

### Contexto
`lognormal3p.py::mv` convergía, para est_09, a `x0=-176.5565` — un valor
físicamente implausible (muy por debajo del mínimo de la serie, 10.99),
mientras la tesis reporta NO_CONVERGE para el mismo caso.

El diagnóstico de causa raíz requirió dos rondas de verificación cruzada
(ver `regresion-e2e/est_09-e2e.md`, Hallazgo B, y `pendientes-facundo.md`):
una primera hipótesis (Code) atribuía el problema a una falsa convergencia
de borde inferior, análoga a [DECISIÓN 019](decision019.md) — **refutada por evidencia
directa** (Octavio, evaluando la función en puntos muy cercanos a
`xi_min`): la verosimilitud perfilada **diverge sin límite hacia -∞**
acercándose al mínimo muestral (`hi`), no hacia `lo`. Confirmado además
(Code, instrumentando la llamada real a `ajustar()`) que `minimize_scalar`,
con el dominio completo, nunca evalúa puntos a menos de 71 unidades de
`hi` para esta serie — converge en una región casi plana cerca de `lo` por
su criterio de tolerancia, sin haber visto nunca la parte del dominio
donde la función realmente colapsa.

### Naturaleza del problema — distinta a los dos guards ya existentes
- [DECISIÓN 019](decision019.md) (`logpearson3.py::mv`): detecta **falsa convergencia en un
  borde** — el óptimo genuino existe, está cerca de un borde específico,
  y el guard verifica proximidad a ese borde.
- [DECISIÓN 023](decision023.md) (`gamma3p.py::mv`): detecta una **raíz espuria de un
  residuo** (no un óptimo de verosimilitud) por magnitud de una cantidad
  intermedia (S2).
- Este caso: la función **no tiene mínimo finito en absoluto** en el
  dominio de búsqueda — no es "el óptimo está en el borde equivocado", es
  "no hay óptimo que encontrar", y el optimizador se detiene en un punto
  arbitrario por su tolerancia de convergencia, no por haber encontrado
  algo.

### Opciones evaluadas
1. **Detectar ausencia de óptimo finito con escaneo grueso** (la elegida).
   Mismo mecanismo de escaneo ya usado en [DECISIÓN 023](decision023.md) — verificar que el
   escaneo tenga un mínimo interior genuino (la función decrece y vuelve
   a subir en algún punto del dominio) antes de aceptar el resultado de
   `minimize_scalar`. Si el mínimo del escaneo cae en el primer o último
   punto finito, no hay evidencia de giro — `NO_CONVERGE`.
2. **Angostar `hi` con un margen fijo** (`hi = xi_min - ε·S`, ε mayor que
   `1e-9`). Descartada: es un parámetro sin respaldo en la tesis, no
   resuelve la ausencia de óptimo (solo aleja la búsqueda de donde
   diverge, sin garantizar que exista un mínimo genuino en el nuevo
   rango), y caería en la categoría de "ambigüedad genuina" del framework
   de 3 categorías del proyecto — necesitaría convención explícita de
   Facundo para justificar el valor de ε.
3. **Cambiar el estimador de x0 a Momentos-L**. Descartada por ser la más
   invasiva: cambia qué se resuelve, no solo cómo se verifica el
   resultado, con riesgo de dejar de ser fiel a "Máxima Verosimilitud" tal
   como la define la tesis (IV-117 a IV-119).

Opción 1 elegida por ser la menos invasiva (no cambia qué fórmula se
resuelve, solo agrega una verificación de forma sobre el resultado) y por
tener precedente directo de mecanismo (escaneo grueso) ya establecido en
[DECISIÓN 023](decision023.md) — aunque el criterio de aceptación/rechazo es distinto al de
esa decisión (acá se busca evidencia de giro, no se valida la magnitud de
una cantidad intermedia).

### Diseño descartado durante el desarrollo del prototipo
Un primer diseño del guard (probado antes de llegar al criterio final)
verificaba que el mínimo del escaneo tuviera un margen porcentual fijo
respecto de los bordes (2% de los puntos del escaneo desde cada extremo).
**Ese diseño fallaba la verificación de regresión**: marcaba 6 de las 8
estaciones donde `lognormal3p/mv` converge correctamente hoy (est_01,
est_02, est_03, est_04, est_05, est_06) como "sin óptimo interior" —
falso positivo. Causa: `hi = xi_min - 1e-9` es, en sí mismo, un punto
cercano a la singularidad de la log-normal de 3 parámetros para
*cualquier* serie (no solo est_09) — el mínimo genuino de varias de esas
6 series cae legítimamente muy cerca de `hi` (en el penúltimo o
antepenúltimo punto de un escaneo de 200), y un margen porcentual fijo
las rechazaba de más solo por estar cerca del borde, sin importar que
hubiera un giro genuino ahí.

El criterio que sí pasó la verificación no depende de *cuán* cerca del
borde esté el mínimo — solo de si existe al menos un punto de
recuperación (la función vuelve a subir) antes de llegar al borde mismo.
De ahí el chequeo final: "el índice del mínimo no es exactamente el
primero ni el último punto finito del escaneo", sin margen porcentual.
Se deja este diseño descartado documentado explícitamente para no
repetir el mismo camino en un guard futuro similar.

### Mecánica del guard aplicado
```python
_N_SCAN_OPTIMO = 200

def _tiene_optimo_interior(neg_profile_ll, lo, hi) -> bool:
    scan = np.linspace(lo, hi, _N_SCAN_OPTIMO)
    vals = np.array([neg_profile_ll(float(x)) for x in scan])
    finite_mask = np.isfinite(vals)
    if np.sum(finite_mask) < 3:
        return False
    vals_f = vals[finite_mask]
    argmin_local = int(np.argmin(vals_f))
    return argmin_local != 0 and argmin_local != len(vals_f) - 1
```
Se aplica después de que `minimize_scalar` reporta éxito, antes de
aceptar `result.x` — si no hay óptimo interior detectado, se devuelve
`STATUS_NO_CONVERGE` en lugar de los parámetros de `result.x`.

### Verificación de regresión
Prototipo corrido contra las 8 series reales de est_01 a est_08 (las
estaciones donde `lognormal3p/mv` converge hoy), con densidades de
escaneo 50, 100, 200, 500 y 1000 puntos — el mínimo del escaneo cae en un
índice interior en las 8 estaciones, en las 5 densidades probadas. Para
est_09, el mínimo cae exactamente en el último punto finito en las 5
densidades probadas.

**Verificación post-aplicación, con el código ya modificado, llamando a
`ajustar()` real (no el prototipo aislado):**

| Estación | status | x0 | µy | σy | ¿Coincide con el valor pre-fix? |
|---|---|---|---|---|---|
| est_01 | ok | 7.1097 | 4.4516 | 1.0829 | Sí — sin cambio |
| est_02 | ok | 38.4692 | 4.0031 | 1.2927 | Sí — sin cambio |
| est_03 | ok | -3.8932 | 3.7935 | 0.8703 | Sí — sin cambio |
| est_04 | ok | -1.9285 | 3.0031 | 0.7266 | Sí — sin cambio |
| est_05 | ok | -2.1576 | 3.3327 | 1.1133 | Sí — sin cambio |
| est_06 | ok | 11.6541 | 3.0942 | 0.9308 | Sí — sin cambio |
| est_07 | ok | -13.7086 | 4.1110 | 0.4150 | Sí — sin cambio |
| est_08 | ok | -0.4715 | 4.9014 | 0.5705 | Sí — sin cambio |
| est_09 | **no_converge** | — | — | — | Antes: `ok` con x0 implausible. Ahora coincide con NO_CONVERGE de la tesis |

`pytest tests/` → 109 passed, 1 failed (el mismo failing preexistente de
`test_gen_pareto_mc_q100_serie_facundo`, documentado en Fase 3, sin
relación con este cambio — mismo conteo que la baseline previa).
`ruff check metis/core/etapa2/distributions/lognormal3p.py` → All checks
passed.

### Archivos modificados
- `metis/core/etapa2/distributions/lognormal3p.py`:
  - Docstring de cabecera, método `mv` — referencia al guard nuevo.
  - Constante `_N_SCAN_OPTIMO` y función `_tiene_optimo_interior` (nuevas).
  - Método `mv`: guard aplicado entre `minimize_scalar` y la aceptación
    de `result.x`.
