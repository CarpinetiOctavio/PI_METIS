# DECISIÓN 061 — Default "tolerar y advertir" ante ceros en Exponencial x0-β, Generalizada de Pareto y Generalizada Exponencial (Momentos/ML)

**Fecha:** 17 de Agosto de 2026
**Estado:** APLICADA — ver verificación en sección correspondiente
**Origen:** Continuación de la auditoría dirigida de restricciones de dominio
en Etapa 2 — `docs/auditoria/hallazgos/restricciones-dominio-etapa2.md`.
Decisión tomada por Octavio a partir del hallazgo de asimetría reportado por
Code.

## Qué pregunta resuelve esta decisión — y cuál NO

**Resuelve:** cuál es el default de implementación de METIS mientras se
espera la confirmación de Facundo sobre si un cero tiene sentido físico para
estas variables.

**NO resuelve:** si un cero tiene sentido físico para estas variables. Esa
pregunta sigue exactamente donde estaba, abierta, en `pendientes-facundo.md`
— sección "Etapa 2 — comportamiento ante ceros de 5 distribuciones". Si
Facundo confirma en el futuro que un cero no tiene sentido para alguna de
estas distribuciones, esto se resuelve **endureciendo la advertencia** (o
bloqueando explícitamente) en ese momento — no reabriendo esta decisión como
si hubiera sido un error de implementación. No fue un error: fue la decisión
correcta con la información disponible hoy.

### Contexto

`PENDING_ZEROS_CONFIRMATION` está definido de forma idéntica (`bool = True`,
mismo texto de docstring) en 5 módulos — pero el comportamiento real en
código, antes de esta decisión, no era uniforme:

| Distribución | ¿Bloqueaba cero antes de esta decisión? |
|---|---|
| Gamma 3p | No (nunca lo bloqueó) |
| Log-Normal 3p | No (nunca lo bloqueó) |
| Exponencial (x0, β) | Sí, los 2 métodos |
| Generalizada de Pareto | Sí, los 4 métodos |
| Generalizada Exponencial | Sí, los 3 métodos |

La asimetría no tenía ninguna base matemática — se verificó, método por
método, cuál realmente necesita bloquear (Code, 17/08/2026):

| Distribución/método | ¿Aplica `log(xi)` sobre datos crudos? | ¿Cero rompe el cálculo? |
|---|---|---|
| Exponencial x0-β — Momentos, MV | No | No |
| Generalizada de Pareto — Momentos, MV, MC, MPP | No (MC usa `log(1-fi)` con `fi` por posición de ploteo/rango, no por valor de xi) | No |
| Gen. Exponencial — Momentos, ML | No (digamma/trigamma de α, medias ponderadas) | No |
| Gen. Exponencial — MV | Sí — `log(1-e^(-λ·xi))`, y en x=0: `1-e^0=0` → `log(0)=-∞` | **Sí, genuino** |

De 3 distribuciones + 9 combinaciones método, **solo 1 (Gen. Exponencial/MV)
tiene una necesidad matemática real de bloquear.** Las otras 8 bloqueaban
por un default sin justificación documentada más allá de "hasta confirmar".

### Decisión

1. **Tolerar donde la fórmula lo permite.** `exponencial_x0_beta.py` (los 2
   métodos) y `gen_pareto.py` (los 4 métodos) dejan de bloquear
   incondicionalmente ante cero. `gen_exponencial.py` acota el bloqueo
   (`STATUS_DISABLED_ZEROS`) solo al método MV — Momentos y ML calculan
   igual.
2. **Advertencia obligatoria, no cómputo silencioso.** Cuando cualquiera de
   estos métodos calcula con un cero presente, se emite `DIST_ZEROS_TOLERATED`
   (nivel `normal`) en `Etapa2Result.warnings` — mismo mecanismo ya usado por
   `DIST_HIGH_EEA` (`pipeline_etapa2.py`), sin inventar infraestructura
   nueva. Se dispara solo cuando `tiene_ceros=True` (flag de pipeline, no
   recomputado desde el array — mismo criterio que ya usa
   `DISABLED_WITH_ZEROS`) y el ajuste dio `status="ok"`, condición que
   excluye naturalmente a Gen. Exponencial/MV (nunca es `ok` con cero
   presente, así que nunca dispara la advertencia).
3. **La pregunta de dominio (`PENDING_ZEROS_CONFIRMATION`) no se toca** — se
   documenta con más precisión (frozenset `TOLERA_CEROS_CON_ADVERTENCIA` en
   `distributions/__init__.py`, subconjunto del anterior) para separar
   explícitamente las dos preguntas que antes vivían mezcladas en una sola
   bandera.

### Por qué es una decisión válida, no una desviación sin fundamento

Categoría 2 del framework de ambigüedad del proyecto para la parte de
"cuándo bloquear por cálculo" — sin ambigüedad matemática, verificado
formula por fórmula. La parte de "qué default mientras se espera
confirmación de dominio" es una decisión de política de implementación de
METIS explícitamente tomada por Octavio, no una inferencia de Code — mismo
patrón de autoría que el resto de decisiones de este archivo que involucran
juicio de producto (ej. DECISIÓN 048, DECISIÓN 050).

Coherente con el principio de negocio central de METIS (`CLAUDE.md`): "METIS
detecta y advierte, pero no bloquea" — la única excepción absoluta
documentada es la serie con menos de 10 datos. Bloquear una distribución
completa porque *podría* haber un problema de dominio, cuando la fórmula
demuestra que no hay ningún problema de cálculo, iba en contra de ese
principio sin necesidad.

### Verificación

**Contra las 9 series reales de la tesis, cero inyectado reemplazando el
mínimo de cada una** (`docs/auditoria/regresion/regresion-unitaria/est_0X-*.md`):

```
exponencial_x0_beta/mv:        ok en las 9 (nunca disabled_zeros)
exponencial_x0_beta/momentos:  ok o no_aplicable en las 9 (el guard de
                                dominio de DECISIÓN 060 sigue aplicando —
                                correcto, es una restricción distinta)
gen_pareto/momentos:           ok o no_aplicable en las 9
gen_pareto/mv, mc:             no_converge en las 9 (ya era así sin cero —
                                MV/MC "frecuentemente no converge" según la
                                tesis, sin relación con el cero)
gen_pareto/mpp:                ok en las 9 (nunca disabled_zeros)
gen_exponencial/momentos, ml:  ok en las 9 (nunca disabled_zeros)
gen_exponencial/mv:            disabled_zeros en las 9 (sin cambios,
                                correcto — necesidad matemática)
```

Ningún crash, ningún NaN, ningún warning de numpy en ninguna combinación —
consistente con la verificación de fórmula (ninguna aplica `log` a datos
crudos salvo el caso ya excluido).

**Advertencia end-to-end**, verificado con `est_03` (La Tapa) + cero
inyectado, `tiene_ceros=True`:
```
4 warnings DIST_ZEROS_TOLERATED emitidas — exponencial_x0_beta/mv,
gen_pareto/mpp, gen_exponencial/momentos, gen_exponencial/ml.
gen_exponencial/mv: status=disabled_zeros, sin warning — confirmado.
Las 4 distribuciones DISABLED_WITH_ZEROS (LN2p, LP3, Gamma2p, ExpBeta):
sin cambios, siguen bloqueadas sin ninguna advertencia nueva.
```

**Camino completo hasta el usuario, verificado sin escribir código nuevo de
frontend:** `analysis_service.py::_serializar_etapa2()` ya serializa
`Etapa2Result.warnings` al JSON de `result_etapa2_ranking` (mismo campo que
usa `DIST_HIGH_EEA`); `Etapa2RankingView.tsx` ya renderiza genéricamente
cualquier `WarningItem` agrupado por código
(`agruparWarnings()`/`nivel="normal"`). Solo hizo falta agregar el texto en
`frontend/src/i18n/errors.es.ts` — no un componente nuevo.

**Catálogo de errores:** `DIST_ZEROS_TOLERATED` agregado a
`api-contracts.md` y a `errors.es.ts`. `bash scripts/check-error-catalog.sh`
→ sincronizado en las tres direcciones.

**Tests:** agregados/actualizados —
`test_exponencial_x0_beta.py` (guard de dominio Momentos + tolerancia a
cero en los 2 métodos), `test_gen_pareto.py` (guard de dominio Momentos +
tolerancia a cero en los 4 métodos, parametrizado), `test_gen_exponencial.py`
(nuevo — no existía ningún test de este módulo antes; alcance acotado a
este cambio, no backfill de cobertura completa de IV-77 a IV-89),
`test_pipeline_etapa2.py` (emisión de `DIST_ZEROS_TOLERATED`, exclusión de
gen_exponencial/mv, ausencia de la advertencia sin ceros).

`pytest -m "unit or integration"`: 297 passed, 1 skipped (mismo skip
preexistente de `gen_pareto/mc`, sin relación) — de 273 antes de esta
sesión a 297, +24 tests nuevos, cero regresiones. `ruff check metis/` +
`ruff format --check metis/`: limpio.

### Archivos modificados
- `metis/core/etapa2/distributions/__init__.py` — nuevo frozenset
  `TOLERA_CEROS_CON_ADVERTENCIA`; comentario de `PENDING_ZEROS_CONFIRMATION`
  corregido (ya no dice "se tratan como disabled_zeros", nunca fue cierto
  para gamma3p/lognormal3p y ahora tampoco para las otras 3)
- `metis/core/etapa2/distributions/exponencial_x0_beta.py` — quita el
  bloqueo incondicional de cero
- `metis/core/etapa2/distributions/gen_pareto.py` — ídem
- `metis/core/etapa2/distributions/gen_exponencial.py` — acota el bloqueo
  a la rama `mv`
- `metis/core/pipeline/pipeline_etapa2.py` — emite `DIST_ZEROS_TOLERATED`
- `.claude/rules/architecture/api-contracts.md` — catálogo actualizado
- `frontend/src/i18n/errors.es.ts` — traducción del código nuevo
- `tests/unit/core/etapa2/distributions/test_exponencial_x0_beta.py`,
  `test_gen_pareto.py`, `test_gen_exponencial.py` (nuevo),
  `tests/unit/core/pipeline/test_pipeline_etapa2.py`
- `docs/auditoria/hallazgos/restricciones-dominio-etapa2.md` — referenciado,
  no modificado por esta decisión (agrega su propia entrada fechada aparte)
