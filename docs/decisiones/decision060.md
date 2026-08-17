# DECISIÓN 060 — Guard de dominio x0/µ ≥ min(serie) en Exponencial x0-β y Generalizada de Pareto (Momentos)

**Fecha:** 17 de Agosto de 2026
**Estado:** APLICADA — ver verificación en sección correspondiente
**Origen:** Segunda pasada de auditoría dirigida a restricciones de dominio en
Etapa 2, en paralelo con una sesión de auditoría dedicada ("Chat") — ver
`docs/auditoria/hallazgos/restricciones-dominio-etapa2.md`, entradas
13/08/2026 y 17/08/2026, para el detalle completo de cómo se encontró.

### Contexto

`exponencial_x0_beta.py::ajustar("momentos")` y `gen_pareto.py::ajustar("momentos")`
no verificaban que el parámetro de posición estimado (`x0` en el primer
caso, `µ` en el segundo) quedara por debajo del mínimo de la serie —
a diferencia de `gamma3p.py` y `lognormal3p.py`, que sí lo hacen para su
propio parámetro `x0` (`gamma3p.py:133-136`, `lognormal3p.py:159`).

Las cuatro distribuciones comparten la misma restricción de fondo: el
soporte de la fórmula exige `x > x0` (Exponencial, IV-68/69; Gamma 3p,
IV-136; Log-Normal 3p, IV-110) o `x ≥ µ` (Generalizada de Pareto,
IV-145/146) — matemáticamente equivalente a `x0 < min(serie)` (o `µ` para
Gen. Pareto). Sin el guard, el módulo podía devolver `STATUS_OK` con un
ajuste que viola el soporte que la propia distribución declara.

**Verificado contra las 9 series reales de la tesis, no solo de forma
sintética** (extraídas de `docs/auditoria/regresion/regresion-unitaria/est_0X-*.md`):

- Exponencial x0-β, Momentos: **6 de 9 estaciones** violaban
  (est_01, est_04, est_06, est_07, est_08, est_09).
- Generalizada de Pareto, Momentos: **3 de 9 estaciones** violaban
  (est_04, est_07, est_08).

MV, MC y MPP de Generalizada de Pareto (y MV de Exponencial x0-β) ya eran
estructuralmente seguros por construcción — verificado, no solo asumido —
y no se tocaron.

### Decisión

Agregar, en la rama `momentos` de ambos módulos, el mismo guard que ya usan
Gamma 3p y Log-Normal 3p:

```python
if x0 >= float(np.min(serie)):   # o `mu`, según el módulo
    return MetodoResult(metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE)
```

Ubicado inmediatamente después de calcular el parámetro de posición
(`x0 = xbar - S` en `exponencial_x0_beta.py`, IV-71; `mu = xbar - sigma / (1.0 + eps)`
en `gen_pareto.py`, IV-147 despejado), antes de retornar `STATUS_OK`.

### Por qué es una decisión válida, no una desviación sin fundamento

Categoría 2 del framework de ambigüedad del proyecto: sin ambigüedad de
fórmula — la restricción de soporte está explícita en la propia ecuación
de la tesis (IV-68/69, IV-145/146), no es una interpretación. No requirió
consulta a Facundo, a diferencia de "¿tolera cero la serie?" (pregunta de
intención genuinamente abierta, sigue en `pendientes-facundo.md`) — acá no
hay alternativa matemática válida si `x0 ≥ min(serie)`. Mismo tipo de
cambio que DECISIÓN020, DECISIÓN023 y DECISIÓN025: guard de dominio
agregado por exigencia de la fórmula, no por hallazgo de Facundo.

**Nota deliberadamente no resuelta acá:** por qué el Excel de Facundo no
marcó esta violación en ninguna de las 9 estaciones (a diferencia de Gamma
3p, donde sí la marca con `EEA=NO_APLICABLE`) queda como hipótesis sin
verificar en `restricciones-dominio-etapa2.md` — no se afirma como hecho
en esta decisión.

### Verificación

Guards aplicados en `exponencial_x0_beta.py:47-64` y `gen_pareto.py:118-136`.
Corridos contra las 9 series reales (mismas extraídas de
`regresion-unitaria/`, no un subconjunto):

**Exponencial x0-β, Momentos, post-fix:**
```
est_01: min=15.0   → no_aplicable   (antes: x0=28.60, ok — sin marcar)
est_02: min=42.0   → ok, x0=33.868  (sin cambio — no violaba)
est_03: min=2.0    → ok, x0=-14.835 (sin cambio — no violaba)
est_04: min=2.0    → no_aplicable   (antes: x0=4.328, ok — sin marcar)
est_05: min=0.9    → ok, x0=-1.355  (sin cambio — no violaba)
est_06: min=14.0   → no_aplicable   (antes: x0=16.34, ok — sin marcar)
est_07: min=11.8   → no_aplicable   (antes: x0=24.34, ok — sin marcar)
est_08: min=39.2   → no_aplicable   (antes: x0=68.48, ok — sin marcar)
est_09: min=10.99  → no_aplicable   (antes: x0=18.22, ok — sin marcar)
```

**Generalizada de Pareto, Momentos, post-fix:**
```
est_01: min=15.0   → ok, mu=-7.702   (sin cambio — no violaba)
est_02: min=42.0   → ok, mu=27.134   (sin cambio — no violaba)
est_03: min=2.0    → ok, mu=-3.411   (sin cambio — no violaba)
est_04: min=2.0    → no_aplicable    (antes: mu=4.090, ok — sin marcar)
est_05: min=0.9    → ok, mu=-2.052   (sin cambio — no violaba)
est_06: min=14.0   → ok, mu=10.954   (sin cambio — no violaba)
est_07: min=11.8   → no_aplicable    (antes: mu=16.980, ok — sin marcar)
est_08: min=39.2   → no_aplicable    (antes: mu=45.703, ok — sin marcar)
est_09: min=10.99  → ok, mu=3.608    (sin cambio — no violaba)
```

Confirmado: el fix es estrictamente aditivo sobre los casos que violaban —
ninguna estación que antes daba parámetros válidos (no violatorios) cambió
de resultado. Los parámetros de las estaciones que siguen en `ok` son
idénticos a los reportados antes del fix (ej. est_02 x0=33.868, ya
verificado contra tesis en `regresion-e2e-coreEstadistico/est_02-e2e.md`).

**Suite de tests:** `pytest -m unit` → 273 passed, 1 skipped, 7 deselected
— mismo conteo que la baseline previa al fix, cero tests nuevos rotos.
`ruff check` y `ruff format --check` sobre los dos archivos → limpio.

### Archivos modificados
- `metis/core/etapa2/distributions/exponencial_x0_beta.py` — método
  `momentos`: guard `x0 >= min(serie)` + nota en docstring
- `metis/core/etapa2/distributions/gen_pareto.py` — método `momentos`:
  guard `mu >= min(serie)` + nota en docstring
- `docs/auditoria/hallazgos/restricciones-dominio-etapa2.md` — referenciado
  desde el comentario inline de ambos guards, no modificado por esta
  decisión (el hallazgo ya estaba documentado antes de aplicar el fix)
