# DECISIÓN 057 — Agregación temporal por año hidrológico configurable
**Fecha:** 12 de Agosto de 2026
**Estado:** Decidida — implementación en curso (Bloque F del [plan de implementación de Etapa 2](../plan-etapa2-implementacion.md))

### Contexto

`.claude/rules/architecture/constraints.md` y `.claude/rules/core/statistical-pipeline.md`
fijan el año hidrológico como **1 julio → 30 junio** del año siguiente, escrito
como si fuera una constante del sistema. Al escribir el Bloque F del plan de
Etapa 2 se encontraron dos huecos reales del contrato de datos:

1. **Ninguna regla de agregación existe.** `ParsedData.resolucion_temporal`
   puede valer `"mensual"` (`core/types.py`), pero nada en el pipeline
   consume ese valor más allá de `if resolucion_temporal is None` — una serie
   mensual entra a Etapa 1 y corre Anderson, Wald-Wolfowitz, Cramer, Chow y el
   ajuste de las 13 distribuciones de Etapa 2 sobre los **valores mensuales
   crudos**, como si cada mes fuera un máximo anual. No falla ni advierte:
   devuelve un resultado con la forma correcta y sin sentido hidrológico —
   peor, la estacionalidad rompe independencia/homogeneidad por construcción,
   así que el usuario ve warnings críticos que son un artefacto del bug, no
   una propiedad real de sus datos (`docs/plan-etapa2-implementacion.md`,
   F2.1).
2. **"1 julio → 30 junio" es el valor de una región, no una regla universal.**
   Es el año hidrológico de la región centro de Argentina, donde están las 9
   estaciones de la tesis de Facundo — pero un registro del NOA, de la cuenca
   del Plata o de la Patagonia arranca la temporada húmeda en otro mes.
   Documentarlo como constante del sistema es una simplificación que no
   sobrevive el primer registro fuera de esa región.

### Opciones evaluadas

1. **Dejar el año hidrológico como constante fija (julio-junio) y solo cerrar
   el bug de agregación.** Descartada: resuelve F2.1 pero deja escrito un
   comportamiento que no es cierto para el resto del país — el próximo que
   suba un registro patagónico va a obtener máximos anuales mal construidos
   sin ningún error que lo avise, exactamente el mismo tipo de falla
   silenciosa que este bloque está cerrando en primer lugar.
2. **Toggle calendario / hidrológico**, la forma en que la maqueta original de
   Etapa 2 (pasada 4) lo presentaba: una opción binaria por gráfico. Descartada
   — es la causa raíz de por qué ese control nunca pudo funcionar (bug D5 de
   la pasada 2, cerrado por eliminación en el Bloque C de este mismo plan, ver
   `sprint.md`): la diferencia entre "calendario" e "hidrológico" no es una
   opción de presentación aguas abajo, es una regla de agregación aguas
   arriba que decide qué valor cae en qué año — y con solo dos opciones no
   cubre ninguna región del país cuyo año hidrológico no sea exactamente
   julio-junio.
3. **Un parámetro único, `mes_inicio_anio ∈ [1..12]`, configurable antes de
   correr el análisis.** Elegida.

### Decisión

**El mes de inicio del año se configura, no se fija.** No hay dos
"modalidades" con un toggle entre ellas — hay un solo parámetro,
`mes_inicio_anio`, con doce valores posibles. El año calendario es
simplemente el caso `mes_inicio_anio = 1`, no un modo aparte. Default `7`
(julio) — el valor de la región centro donde están las 9 estaciones de la
tesis, conservado como default razonable, no como regla universal.

**Parámetro de punta a punta:**

| Capa | Cambio |
|---|---|
| `POST /analysis/stream` | `mes_inicio_anio: int` (`Form`, default `7`), validado en `[1..12]` en el borde del endpoint → 400 `CONTRACT_MES_INICIO_INVALID` si está fuera de rango |
| `core/validacion/aggregation.py` | Módulo nuevo, función pura `agregar_a_maximos_anuales()` |
| `core/pipeline/pipeline_etapa1.py::ejecutar_etapa1()` | Llama la agregación al principio, antes de `validar_contrato()` — no en `services/` |
| `analyses.configuracion` (JSONB) | `mes_inicio_anio` se guarda junto a `cramer_particion` — sin migración, la columna ya existe |
| `ConfigPage` (frontend) | Selector de mes — Bloque F5, PR aparte |

`mes_inicio_anio` **no es opcional en el registro de auditoría**: dos
análisis sobre el mismo archivo con meses de inicio distintos producen series
anuales distintas y resultados distintos. Sin guardarlo, el historial de
CU-01 muestra un resultado que no se puede volver a reproducir.

### Regla de recorte en los extremos

El registro casi nunca arranca justo en el mes de inicio ni termina justo en
el mes de cierre. Los datos que sobran en cualquiera de los dos extremos **se
descartan** — el registro se recorta a años completos:

- Con `mes_inicio_anio = 6` y un registro que arranca en marzo de 2001, los
  meses marzo-mayo de 2001 no forman un año completo: se descartan. El primer
  año del análisis es junio 2001 – mayo 2002.
- Si el mismo registro termina en agosto de 2010, junio-agosto de 2010 no
  llegan a cerrar el año: se descartan. El último año del análisis es junio
  2009 – mayo 2010.

No se completa, no se interpola, no se acepta un año parcial "casi lleno" en
los extremos — `constraints.md` ya es explícito en que METIS no corrige
datos, y el máximo de un año parcial está sesgado a la baja por construcción.
Se emite un warning no bloqueante, `CONTRACT_PARTIAL_YEARS_TRIMMED`, con
cuántos meses se descartaron en cada extremo y cuál es el período efectivo
resultante — descartar en silencio no es aceptable, el usuario tiene que ver
qué se recortó.

**Etiquetado.** Un año junio 2001 – mayo 2002 se etiqueta con el año
calendario en que **empieza** (2001). Con `mes_inicio_anio = 1` esto degenera
exactamente en el año calendario — es la verificación de consistencia del
propio algoritmo.

**El recorte ocurre antes del conteo de la regla de n.** Un registro de 12
años que pierde los dos extremos entra a Etapa 1 con n=10; si eso lo deja
bajo el piso, bloquea con `CONTRACT_SERIES_TOO_SHORT` como cualquier otra
serie corta — coherente con la regla existente, no una excepción nueva.

**Dónde se llama.** Al principio de `ejecutar_etapa1()`, antes de
`validar_contrato()` — no en `services/`. Así el conteo de n opera ya sobre
la serie agregada, `services/` no gana lógica de dominio nueva, y se respeta
"el pipeline siempre arranca por Etapa 1".

### Hueco interior — descartado, código distinto del recorte de extremos

Un año del medio al que le faltan meses (una estación fuera de servicio seis
meses en 2007) no es lo mismo que un extremo parcial — recortarlo partiría el
registro en dos. Se descarta con `CONTRACT_INCOMPLETE_YEARS_DISCARDED`,
código distinto de `CONTRACT_PARTIAL_YEARS_TRIMMED` porque significa otra
cosa: hay un agujero en el registro, no un borde natural de los datos
disponibles. La serie resultante queda con un salto temporal, que
`contract.py` ya detecta como `CONTRACT_IRREGULAR_SPACING` — los tres
warnings juntos cuentan la historia completa sin que ninguno mienta.

Si se descarta cualquier año interior incompleto sin excepción, o si hay un
umbral de meses mínimos por debajo del cual recién corresponde descartarlo,
es una pregunta de dominio — va a `docs/auditoria/pendientes/pendientes-facundo.md`.
Implementado con la posición "se descarta el que no tenga los 12 meses"
mientras se espera esa confirmación; no bloquea el resto de esta decisión.

### Función de agregación

Máximo por año — es lo que corresponde al análisis de frecuencia de eventos
extremos y lo que hace la tesis, para `caudal_precipitacion`. Para
`tipo_variable == "otro"` el máximo puede no ser la agregación correcta;
también es pregunta de dominio, en el mismo archivo de pendientes.

Un valor faltante o no numérico dentro de un mes cuenta como si ese mes no
estuviera presente — rompe la completitud del período exactamente igual que
un mes ausente del registro.

### Consecuencia para el mapeo de índice de Chow (services/)

Con la agregación llamada dentro de `ejecutar_etapa1()` (no en `services/`),
el índice que reporta Chow (`indice_atipico`) pasa a referirse a una posición
en la serie **agregada** cuando la resolución de entrada era "mensual" — no
en la serie mensual cruda que subió el usuario.
`services/analysis_service.py::_mapear_indice_a_serie_original()` (usado para
traducir ese índice y construir `serie_filtrada` cuando el usuario rechaza el
atípico) operaba hasta ahora directamente sobre `serie_original` (la serie
cruda tal como se subió) — con una serie mensual agregada, mapear un índice
de la serie anual contra la serie mensual cruda habría borrado el dato
mensual equivocado.

Se agregan `serie_efectiva`/`timestamps_efectivos` a `Etapa1Result`: la serie
y los timestamps sobre los que `ejecutar_etapa1()` realmente corrió la
batería estadística — iguales a la entrada si la resolución era "anual"
(nada que agregar), o los máximos anuales agregados si era "mensual".
`services/` usa `result.serie_efectiva` (no `serie_original`) para el mapeo
de índice de Chow y para todo lo que corre después de Etapa 1 (Etapa 2). El
campo `serie` que se persiste en `analyses.serie` sigue siendo la serie cruda
tal como se subió — es otro campo, con otro propósito (auditoría de lo que
el usuario subió, no de lo que se analizó).

### Tres códigos de error nuevos

`CONTRACT_MES_INICIO_INVALID`, `CONTRACT_PARTIAL_YEARS_TRIMMED`,
`CONTRACT_INCOMPLETE_YEARS_DISCARDED` — van a `api-contracts.md` y a
`frontend/src/i18n/errors.es.ts` en el mismo commit que los introduce, misma
regla de [DECISIÓN 038](decision038.md). Los dos últimos son warnings no
bloqueantes (eventos SSE `test_result`/`contract_warning`, no HTTP 4xx); el
primero es un 400 estándar en el borde del endpoint, mismo tratamiento que
`CONTRACT_ETAPAS_INVALID` (DECISIÓN 054).

### Lo que esta decisión NO cubre — Bloque F5

El selector de mes en `ConfigPage` y la visualización del período efectivo
junto a la estadística descriptiva son el Bloque F5, PR aparte — esta
decisión cubre el parámetro de punta a punta a nivel de contrato (backend)
más la agregación en sí, no la interfaz que lo consume.

### Criterio de hecho

- `core/validacion/aggregation.py::agregar_a_maximos_anuales()` con tests
  unitarios: años completos sin recorte, recorte de inicio, recorte de fin,
  los dos extremos a la vez, `mes_inicio_anio=1` reproduce el año calendario,
  `mes_inicio_anio=12` (el año cruza el cambio de año calendario), el recorte
  deja n < 10, año interior incompleto.
- `mes_inicio_anio` fuera de `[1..12]` → 400 `CONTRACT_MES_INICIO_INVALID`.
- `analyses.configuracion` guarda `mes_inicio_anio`; verificado con `psql` en
  un análisis de CU-01.
- Los tres códigos de error en `api-contracts.md` y en
  `frontend/src/i18n/errors.es.ts`; `./scripts/check-error-catalog.sh` verde.
- Con `resolucion_temporal == "anual"` el pipeline se comporta exactamente
  como antes de esta decisión — la agregación no toca ese camino.
- Verificación manual: el mismo archivo mensual analizado con
  `mes_inicio_anio = 1` y con `mes_inicio_anio = 7` produce series anuales
  distintas, y el warning de recorte dice qué meses se descartaron en cada
  caso.

**Ver también:** [DECISIÓN 038](decision038.md) — la regla de catálogo de
errores en las tres direcciones que rige los tres códigos nuevos.
`docs/auditoria/pendientes/pendientes-facundo.md`, sección "Bloque F del plan
de Etapa 2" — las tres preguntas de dominio que esta decisión deja abiertas
sin bloquear su propia implementación.
