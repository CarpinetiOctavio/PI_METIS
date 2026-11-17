# DECISIÓN 058 — Qué serie se expone, en qué versiones y por qué

**Fecha:** 12 de Agosto de 2026
**Estado:** Decidida — implementación en curso (PR 2 del [plan de cierre de
pendientes no-test](../plan-cierre-pendientes-no-test.md))

### Contexto

Tres gráficos con eje temporal (serie temporal, gráfico de Chow, boxplot
mensual) están pendientes en `docs/pendientes-tecnicos.md` bajo la entrada
FE-16, que hoy dice *«`Etapa1Result` no expone la serie cruda»*. Esa
afirmación dejó de ser cierta el 12/08/2026 con el PR 8 del plan de Etapa 2
(DECISIÓN 057): `Etapa1Result` ya tiene `serie_efectiva` y
`timestamps_efectivos` (`backend/metis/core/types.py`).

El bloqueo real es otro, y son tres huecos distintos, verificados contra el
código real antes de escribir esta decisión:

1. `_serializar_etapa1()` (`services/analysis_service.py`) no incluye
   `serie_efectiva` ni `timestamps_efectivos` en el payload de
   `result_etapa1` ni en la fila `analysis_results.etapa1` — se calculan y
   se descartan.
2. `test_result_dict()` (misma función) no serializa `indice_atipico`, que
   ya existe en `TestResult` (`core/types.py`) — sin él, el gráfico de Chow
   no puede marcar cuál punto es el atípico.
3. La serie mensual cruda no viaja a ningún lado, ni sus timestamps.
   `analyses.serie` la persiste, pero `analyses` no tiene columna de
   timestamps y `GET /history/{id}` no devuelve ni `serie` ni
   `configuracion`. El boxplot mensual la necesita: para una carga mensual,
   `serie_efectiva` son los **máximos anuales**, no los meses.

Esta decisión resuelve **qué** se expone y **por qué**, antes de que el PR 3
(código) lo implemente — mismo patrón que el Bloque A0 del plan de Etapa 2
(decisiones 052-055 en su propio PR, antes del código).

### 1. Qué datos se exponen y dónde vive cada uno

**Partición decidida:**

| Vive en | Qué es | Ejemplos |
|---|---|---|
| `analyses.serie` + `analyses.timestamps` (columna nueva) + `analyses.configuracion` | Lo que el usuario **subió y configuró** — auditoría de la entrada | Serie mensual cruda de 40 años, sus fechas, `mes_inicio_anio` |
| `analysis_results.etapa1.{serie_efectiva, timestamps_efectivos, indice_atipico}` | Lo que se **analizó** — resultado, no entrada | Máximos anuales agregados, el índice del atípico de Chow ya mapeado |

Esta distinción es la misma que el Bloque F tuvo que introducir para no
mapear el índice de Chow contra la serie mensual cruda equivocada (DECISIÓN
057, "Consecuencia para el mapeo de índice de Chow") — se generaliza acá al
resto del contrato en vez de quedar implícita en un solo módulo.

**Alternativa descartada:** meter todo en el JSONB de `etapa1` y no migrar
`analyses` (agregar `timestamps` solo del lado del resultado). Se descarta
porque duplica `analyses.serie` (ya persistida aparte) y confunde entrada
con resultado — exactamente la distinción que esta sección fija.

**Regla de peso muerto.** `serie_original`/`timestamps_originales` viajan en
`result_etapa1` **solo** si hubo agregación (`resolucion_original ==
"mensual"`). Con carga anual, `serie_original` es idéntica a
`serie_efectiva` — duplicarla en el payload no aporta nada, el frontend usa
los campos `_efectiva` en ese caso.

### 2. La regla de las dos versiones, acotada

`constraints.md` ("Gráficos con eje temporal") dice hoy que los tres
gráficos (serie temporal, boxplot mensual, gráfico de Chow) llevan las dos
versiones (calendario e hidrológico/configurado) sin distinción, y los da
por bloqueados por FE-16. Ambas afirmaciones quedan corregidas por esta
decisión:

- **Se mantiene** para serie temporal y boxplot mensual — son gráficos
  descriptivos, la agregación calendario es una vista comparativa legítima.
- **No aplica al gráfico de Chow.** Chow corrió sobre `serie_efectiva` — la
  agregación con el `mes_inicio_anio` configurado. El atípico es un punto
  **de esa** serie; en la agregación calendario ese punto puede no existir,
  o existir con otro valor y otro año, porque el criterio de agrupación
  cambió. El gráfico de Chow se dibuja **solo** sobre la serie analizada,
  sin toggle, con la nota de criterio de año que ya produce
  `etiquetaSelectorMes()`/`notaCriterioAnio()`
  (`frontend/src/i18n/mesInicioAnio.ts`, PR 9). El toggle aplica a
  descripción de la muestra, no al resultado de una prueba.
- **No aplica a los dos gráficos de Etapa 2** (`Etapa2AjusteChart`,
  `Etapa2EventosChart`) — ya retirado en DECISIÓN 056, sin cambios acá.
- **Solo se realiza con carga mensual.** Si el usuario subió una serie
  **anual**, el criterio de año lo fijó él al armar el archivo — METIS no
  puede reagrupar máximos anuales en otro año calendario, esa información
  ya se perdió al agregar. El toggle calendario/configurado se renderiza
  **solo** si `resolucion_original == "mensual"`; con carga anual no se
  muestra deshabilitado, directamente no se muestra, con una nota al pie
  que explica por qué — mismo criterio con que el Bloque C retiró el toggle
  por tarjeta: no exhibir un control que no representa una elección real.

Esto es un apartamiento parcial de `constraints.md` respecto de lo que ese
archivo afirma hoy (los tres gráficos con las dos versiones sin excepción) —
queda documentado acá, no resuelto en silencio dentro de un componente. La
sección "Gráficos con eje temporal" de `constraints.md` se corrige en el
mismo PR que esta decisión para reflejarlo.

### 3. La versión calendario se calcula en `core/`, nunca en TypeScript

`agregar_a_maximos_anuales()` (`core/validacion/aggregation.py`) es una
función pura con reglas no triviales: recorte de años parciales en los
extremos, descarte del hueco interior con un código de warning distinto, y
etiquetado del año por el mes en que empieza el período (DECISIÓN 057).
Reimplementarla en TypeScript duplicaría lógica de dominio en un lenguaje
sin tests de regresión contra la tesis — exactamente el tipo de decisión que
el tribunal de ISI va a mirar.

El backend la llama **dos veces** cuando la carga es mensual: una con el
`mes_inicio_anio` elegido (la que ya corre dentro de `ejecutar_etapa1()`,
produce `serie_efectiva`) y otra con `mes_inicio=1`, **solo para
presentación**, que produce `serie_calendario`. La segunda llamada no toca
`Etapa1Result` ni ninguna prueba estadística — corre aparte, en
`services/`, después de que Etapa 1 ya terminó.

**Consecuencia que tiene que quedar escrita en la UI, no solo en el
código:** la serie calendario es una vista comparativa. Ningún estadístico,
veredicto ni warning de la pantalla corresponde a ella. Si esto no queda
escrito en pantalla (PR 4), el gráfico miente — muestra una agregación que
nadie validó estadísticamente como si fuera equivalente a la analizada.

### 4. Qué pasa con los análisis ya persistidos — sin backfill

Los análisis persistidos antes de esta migración no tienen `timestamps`
recuperable con el criterio de año correcto — `analyses` no tenía esa
columna, y sin ella no hay forma de reconstruir qué timestamp correspondía
a cada valor de la serie ya guardada.

**Decisión: no hay backfill.** El frontend degrada explícitamente — la
sección de gráficos no se renderiza para un análisis del historial anterior
a esta migración, y una nota indica que es anterior a esta versión de
METIS.

**Por qué no se intenta reconstruir:** fabricar timestamps para una fila
vieja (por ejemplo, asumir espaciado regular desde `created_at` hacia atrás)
sería inventar datos en un sistema cuyo propósito explícito es auditoría de
lo que el usuario subió y analizó (`architecture.md`, esquema de
`analyses`). Un timestamp inventado que coincide por casualidad es peor que
una sección vacía con una nota — no hay forma de que el usuario distinga
uno de otro en pantalla.

### 5. Tope de payload — calculado, no estimado

Peor caso realista de este dominio (ver también DECISIÓN 050, que ya midió
tamaños de archivo de subida para el mismo tipo de series): carga mensual
de **100 años = 1.200 valores mensuales**, con `mes_inicio_anio != 1` (así
se emiten los cinco campos del bloque `datos`, no solo los `_efectiva`).

| Campo | Puntos | Bytes/punto (JSON) | Subtotal |
|---|---|---|---|
| `serie_original` (floats, ej. `94.71`) | 1.200 | ~7 B | ~8,4 KB |
| `timestamps_originales` (`{"iso": "1980-01-01", "anio": 1980}`) | 1.200 | ~38 B | ~45,6 KB |
| `serie_efectiva` (máximos anuales) | 100 | ~7 B | ~0,7 KB |
| `timestamps_efectivos` | 100 | ~38 B | ~3,8 KB |
| `serie_calendario` (mismo orden que `serie_efectiva`) | 100 | ~7 B | ~0,7 KB |
| `indice_atipico` | 1 | — | despreciable |

**Total del bloque `datos`: ~59 KB.** Sumado al resto de `result_etapa1`
(contrato, descriptiva, las pruebas de las cuatro baterías — ya en producción
hoy, del orden de pocos KB), el evento SSE completo queda en el orden de
**decenas de KB**, muy por debajo de cualquier límite práctico de tamaño de
mensaje SSE, y comprimible con gzip (JSON repetitivo) si nginx lo aplica en
el proxy. El cap de subida de 10 MB (DECISIÓN 050) es sobre el archivo de
**entrada**, no sobre este payload de salida — no hay relación directa entre
ambos números, se citan juntos acá solo para confirmar que ninguno de los
dos se acerca al otro.

### Índice_atípico — mapeado, no crudo

El índice que viaja en `datos.indice_atipico` es el que ya devuelve
`_mapear_indice_a_serie_original()` en `services/analysis_service.py` —
posición sobre `serie_efectiva`, no el índice crudo de `calcular_chow()`
sobre `valores_numericos` filtrados. En la iteración 2 del stream (el
usuario rechazó el atípico) no hay atípico: el campo va en `null`, y el
gráfico de Chow dibuja la serie sin marcador — el detalle de implementación
completo queda en el PR 3, esta decisión solo fija que el contrato expone el
índice ya traducido, nunca el crudo.

### Lo que esta decisión NO cubre

- La implementación de `_serializar_etapa1()`, la migración Alembic y el
  endpoint `GET /history/{id}` — PR 3.
- Los componentes de gráfico en sí (`Etapa1SerieTemporalChart`,
  `Etapa1ChowChart`, boxplot mensual) — PR 4 y PR 5.
- La normalización de tipos heterogéneos de `timestamps_efectivos` según
  hubo agregación o no (`str`/`int`/`pd.Timestamp` vs. `list[int]`) — regla
  ya fijada en el propio plan de cierre de pendientes (§4.4), implementada
  en el PR 3 vía `parsear_timestamps()`.

### Criterio de hecho

- `docs/pendientes-tecnicos.md`, fila FE-16, reescrita con el diagnóstico de
  los tres huecos de la sección "Contexto" de esta decisión — no se cierra
  todavía, se corrige antes de que el PR 3 la resuelva.
- `.claude/rules/architecture/constraints.md`, sección "Gráficos con eje
  temporal", corregida para excluir a Chow y condicionar el toggle a carga
  mensual.
- El PR 3 verifica que `result_etapa1` trae el bloque `datos` con la forma
  de la sección 1, y que `serie_original`/`timestamps_originales` no viajan
  cuando la carga fue anual.
- El PR 5 verifica la degradación real: un análisis del historial creado
  antes de la migración (o archivado a propósito con ese fin) no rompe
  `HistoryDetailPage`, muestra la nota de "anterior a esta versión" en vez
  de gráficos vacíos o un error.

**Ver también:** [DECISIÓN 057](decision057.md) — el mismo criterio de
separación entrada/resultado, aplicado primero al mapeo de índice de Chow.
[DECISIÓN 056](decision056.md) — por qué los gráficos de Etapa 2 no llevan
esta regla de dos versiones. [DECISIÓN 050](decision050.md) — el otro
cálculo de tamaño de payload de este dominio, usado acá como referencia de
orden de magnitud.
