# tests/ — Estado y hallazgos, snapshot al cierre de la sesión de reorganización
## Fecha: 17/07/2026 
## Estado: Por completarse una vez finalizado auth

Este README no es documentación de cómo correr los tests (eso está en
`.claude/rules/testing.md`). Es un snapshot de diagnóstico: qué se
encontró al auditar la suite existente, qué quedó pendiente, y qué hay
que tener presente al retomar el tema en una sesión dedicada. El
objetivo es no perder este contexto entre ahora y esa sesión.

## Estructura (post-reorganización)
tests/unit/core/
├── estadistica_descriptiva/   test_descriptive.py
├── etapa1/                    test_homogeneity.py, test_independence.py, test_trend.py, test_outliers.py
├── etapa2/
│   └── distributions/         13 archivos — 8 existentes + 5 pendientes de escribir
├── pipeline/                  test_pipeline_etapa1.py, test_pipeline_etapa2.py, test_full_pipeline.py
└── validacion/                 test_contract.py

## Dos capas de testing, no dependen una de la otra

1. **Unit tests de comportamiento** (`tests/unit/`) — no dependen de
   ningún dato externo de Facundo. Verifican que el código hace lo que
   la fórmula documentada dice.
2. **Tests de regresión contra el Excel de Facundo** (`tests/regression/`)
   — dependen de que Facundo entregue series reales en formato digital.
   Bloqueados externamente, correctamente separados.

## Hallazgo central — desvío del criterio original en los 8 tests existentes de Etapa 2

El criterio establecido para la capa 1 era: series **sintéticas**,
construidas ad hoc, con el valor esperado calculado a mano por
construcción matemática directa — trazable, sin depender de ningún dato
real.

Al auditar los 8 archivos existentes (`exponencial_x0_beta`, `gamma2p`,
`gamma3p`, `gen_pareto`, `gumbel`, `gve`, `lognormal3p`, `logpearson3`),
se encontró que **7 de los 8 usan `serie_facundo` — una serie real de
caudales anuales 1980-2019, no sintética — en casi todos sus tests.**

Contexto importante sobre `serie_facundo`: es una serie real que Facundo
entregó específicamente para tener un dato verdadero de respaldo, **no
está validada/calculada contra el Excel de Facundo para esa estación
puntual** — `conftest.py` lo documenta explícitamente ("PENDIENTE:
resultado de Anderson no validado contra Excel de Facundo").

Esto significa que el desvío **no es regresión matemática disfrazada**
en sentido estricto — en ningún test se compara contra un resultado
publicado por Facundo para esa estación. El problema real es distinto:
se usó una serie real como si fuera arbitraria, cuando el criterio
pedía una serie construida para que la cuenta fuera trazable a mano sin
depender de ningún dato externo.

Consecuencia práctica: los ~20 valores hardcodeados en estos 8 archivos
dependen todos de una única fixture compartida. Si `serie_facundo`
cambiara alguna vez, se rompen todos simultáneamente sin que ningún
test lo explique — acoplamiento fuerte a un solo punto de fallo.

**El patrón correcto ya existe en el propio repo** — `test_gve.py`,
caso `test_gve_momentos_g_en_rango_iv204_usa_polinomio_correcto`: serie
sintética construida específicamente para caer en el rango correcto,
valor esperado recomputado inline con la fórmula documentada, sin
depender de dato real ni de correr el código dos veces. Es la referencia
a seguir para los tests nuevos y para cualquier retrofit futuro.

## Bug activo — no es cuestión de estilo, es un falso positivo

`test_logpearson3_directo_alpha_hat_formula` **pasa en verde sin
verificar nada.** La serie con `seed=42` no cae en el rango B∈(3.5,6]
que el test asume — cae en `STATUS_NO_APLICABLE`, no en `STATUS_OK` — y
el `assert` vive dentro de un `if status == STATUS_OK:` que nunca se
ejecuta. Documentado por primera vez en Fase 3, sigue sin corregir.
**Esto no es parte de la discusión de sintético vs. real — es un test
que finge cobertura inexistente y debería corregirse con prioridad al
retomar el tema.**

## Gaps de cobertura real — sin ningún test, ni bueno ni malo

- `gamma3p.py` método `mv` (IV-140 a IV-143) — sin test.
- `lognormal3p.py` método `mv` — sin test.
- `logpearson3.py` método `mv` (sistema iterativo IV-257 a IV-259) — sin test.

## Pendiente — los 5 tests faltantes de Etapa 2

`exponencial_beta`, `lognormal2p`, `normal`, `uniforme` — fórmulas
cerradas, no iterativas, sin la ambigüedad de convención de `g` que
contaminó los 6 archivos que auditó Fase 3. Se prestan naturalmente a
series 100% sintéticas con expectativa derivada inline — sin ninguna
excusa para usar `serie_facundo`.

`gen_exponencial` es la excepción: `sprint.md` ya documenta que la
fórmula de Momentos (IV-77) tiene una ambigüedad sin resolver ("la
ecuación como escrita no tiene solución válida, se implementa
CV-matching"). El test para este caso debe documentar esa incertidumbre
explícitamente, no fingir precisión que no existe.

## Decisión pendiente para la sesión dedicada — tres opciones, no excluyentes

- **(A)** No tocar los 8 existentes — ya están verificados (por Fase 3
  o independientemente), pasan, y "usar una serie real" no es lo mismo
  que "estar mal". Riesgo: quedan permanentemente desalineados del
  criterio que el propio proyecto define como estándar.
- **(B)** Retrofit mínimo — agregar, por archivo, al menos un test
  100% sintético adicional para el método iterativo/con ambigüedad de
  convención (mismo patrón que ya existe en `gve` y `logpearson3` para
  casos puntuales), sin tocar los tests existentes con `serie_facundo`.
- **(C)** Cerrar los gaps de cobertura reales primero (el test vacío +
  los 3 métodos `mv` sin test) — más urgente que la cuestión de estilo,
  porque ahí no hay ningún test, ni bueno ni malo.

Ninguna decisión tomada todavía. Prioridad sugerida al retomar: C
primero (son huecos objetivos, no de estilo), B si se quiere alinear
metodología, A como piso si el tiempo no da — a decidir en la sesión
dedicada, no en esta.