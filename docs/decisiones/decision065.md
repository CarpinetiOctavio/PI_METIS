# DECISIÓN 065 — Resolución diaria como formato de entrada

**Fecha:** 28 de Agosto de 2026
**Estado:** Decidida y aplicada (backend #77/#78, frontend #79 — plan
[`docs/plan-resolucion-diaria.md`](../plan-resolucion-diaria.md), bloques R1–R4)

### Contexto

[DECISIÓN 057](decision057.md) cerró el bug F2.1 para series **mensuales**:
antes, una serie mensual corría toda la batería de Etapa 1 y el ajuste de
Etapa 2 sobre los valores mensuales crudos, como si cada mes fuera un
máximo anual. La solución fue agregar a máximos anuales en el paso 0 de
`ejecutar_etapa1()`, con `mes_inicio_anio` configurable.

**Diaria quedó afuera.** `parser.py::_inferir_resolucion()` devolvía `None`
para una serie diaria (moda de deltas = 1 día), y `validar_contrato()`
trata `resolucion_temporal is None` como bloqueante —
`CONTRACT_NO_TEMPORAL_RESOLUTION`. El
[informe de viabilidad](../informe-viabilidad-resoluciones-temporales.md)
(28/08/2026) confirmó que **aceptar diaria por el mismo camino que mensual
(camino A) es barato, aditivo y sin riesgo de regresión**: la batería
estadística sigue corriendo sobre `serie_efectiva`, una serie anual de
n≈40; ninguna de las 8 pruebas de Etapa 1 ni ninguna de las 13
distribuciones se toca. El "no" al camino B (analizar los valores diarios
sin agregar) es una decisión aparte — [DECISIÓN 066](decision066.md).

### Decisión

**Diaria es un formato de entrada más, agregado a máximos anuales por el
camino A.** No cambia el dominio de análisis de METIS (la serie de máximos
anuales); cambia dónde ocurre la derivación de esa serie — hoy la hace el
usuario en Excel antes de subir, ahora la hace METIS con una regla
explícita, auditada y configurable.

Las elecciones que este plan toma y que no son derivables del código:

#### 1. Diaria → anual **directo**, no encadenado diaria → mensual → anual

Cambia el resultado cuando hay meses parcialmente faltantes: el encadenado
descartaría el mes y evaluaría el año sobre 11 meses; el directo evalúa la
cobertura del año completo de una. Se elige el **directo** — preserva la
máxima información y hace que `mes_inicio_anio` opere sobre un solo nivel.

`_periodo_de(anio, mes, mes_inicio)` no cambió: depende solo de año y mes,
y una fecha diaria cae en el mismo período que su mes. Es la razón de fondo
por la que este cambio es barato — `mes_inicio_anio` sigue operando en
granularidad de mes sin importar la resolución del dato.

> **Nota de coherencia.** Con carga diaria el sistema **calcula** una
> agregación a máximos mensuales para presentación (ver punto 3), pero esa
> agregación NO alimenta la serie anual — el camino estadístico sigue
> siendo directo. La segunda agregación de `_calcular_serie_calendario()`
> (`mes_inicio=1`, solo comparativa) también corre directa sobre la serie
> diaria cruda, con `resolucion="diaria"` explícito.

#### 2. `cobertura_minima_interior` — parámetro con regla asimétrica

Para mensual, "año completo" = 12/12 meses, regla limpia. Para diaria la
regla análoga (365/366 días) es más exigente; con registros reales ningún
limnígrafo de 40 años tiene cero días faltantes.

**La regla es asimétrica** (`agregar_a_maximos_anuales(...,
cobertura_minima_interior)`):

| Tipo de período | Cobertura exigida | Si no la alcanza |
|---|---|---|
| Primer año del registro (`periodo_inicio`) | **100 %, siempre** | descartado, `CONTRACT_PARTIAL_YEARS_TRIMMED` |
| Último año del registro (`periodo_fin`) | **100 %, siempre** | descartado, `CONTRACT_PARTIAL_YEARS_TRIMMED` |
| Años interiores | `cobertura_minima_interior` | descartado, `CONTRACT_INCOMPLETE_YEARS_DISCARDED` |

**Por qué asimétrica.** DECISIÓN 057 descarta los extremos parciales porque
*"el máximo de un año parcial está sesgado a la baja por construcción"*, y
en un extremo la parcialidad es la regla, no la excepción: el registro
empieza o termina ahí. En el interior, un hueco del 2 % es una falla de
instrumentación sobre un año que sí se midió entero. **Con esta regla,
DECISIÓN 057 queda intacta y no hay que reabrirla** — este plan solo agrega
una tolerancia nueva donde antes no había ninguna regla escrita. Un umbral
único para todos los años habría desactivado DECISIÓN 057 justo en los
bordes, que es donde su argumento del sesgo es más fuerte.

**El sesgo que igual queda declarado.** Aceptar un año interior con < 100 %
de cobertura implica que su máximo está sesgado a la baja: faltan días que
podrían haber contenido el pico. Código nuevo
`CONTRACT_INCOMPLETE_YEARS_ACCEPTED` (nivel `normal`), que el warning de
agregación emite con cuántos días le faltaron a cada año aceptado —
"aceptar con reservas" no puede quedar invisible, misma regla de "descartar
no es borrar en silencio" de DECISIÓN 057.

**Valor provisorio: `cobertura_minima_interior = 1.0` (estricto).** El
parámetro está cableado y probado para aceptar valores menores, pero
relajarlo introduce un sesgo declarado a cambio de nada verificable
mientras no haya evidencia de registros reales de Facundo — ver R0.1 en
`pendientes-facundo.md`. Con `1.0` el código es **equivalente** a la
igualdad de conjuntos del código mensual original (`presentes ⊆ esperados`
siempre, por construcción de la clave), así que no cambia la semántica para
mensual — la contiene como caso particular. `CONTRACT_INCOMPLETE_YEARS_ACCEPTED`
por lo tanto **no se emite nunca todavía**; el código, el catálogo, la
traducción y el test entran igual para que habilitar el umbral sea cambiar
la constante `COBERTURA_MINIMA_INTERIOR` en `aggregation.py` y nada más.

#### 3. Payload — se serializa la agregación mensual, no la serie diaria cruda

[DECISIÓN 058](decision058.md) dimensionó el bloque `datos` de
`result_etapa1` para el peor caso mensual (1.200 ítems ≈ 59 KB) y concluyó
que estaba *"muy por debajo de cualquier límite práctico"*. Medido para
diaria-40-años sobre el fixture real: `serie_original` 14.600 ítems ≈
110 KB, `timestamps_originales` ≈ 528 KB, **total ≈ 637 KB** — ~11× el peor
caso mensual, por evento SSE y persistido en `analysis_results.etapa1`
(JSONB) en cada análisis de CU-01. **Contradice el razonamiento explícito
de DECISIÓN 058 y no puede resolverse por omisión.**

**Elegida: opción 2 — serializar la agregación a máximos MENSUALES**
(`agregar_a_maximos_mensuales()`, ~480 ítems para 40 años, por debajo del
caso mensual ya dimensionado) en lugar de la serie diaria cruda. Es
coherente con cómo razona el sistema: cada capa trabaja en su propio
dominio, la serie diaria cruda no tiene por qué llegar al navegador.
`Etapa1Result.serie_original` **no se toca** — sigue siendo la serie diaria
cruda que alimenta `_calcular_serie_calendario()`; la transformación ocurre
solo en la serialización (`_serializar_etapa1()`).

**La opción 2 no es transparente para el frontend.** `Etapa1BoxplotMensualChart`
agrupa por mes los valores de `serie_original`; con carga diaria recibe
**máximos mensuales** en vez de **valores mensuales** — mismo dibujo, otra
estadística. Dos consecuencias obligatorias, parte del alcance:

- **Campo nuevo `datos.resolucion_serie_original`** (`"diaria" | "mensual" |
  "anual" | null`), distinto de `resolucion_original` (la del archivo): con
  carga diaria vale `"mensual"`. Sin él, el nombre `serie_original` miente.
- **El boxplot y la serie temporal rotulan según ese campo y
  `resolucion_original`:** "máximos mensuales agregados desde datos diarios"
  cuando el archivo era diario, "valores mensuales del registro" cuando era
  mensual. Un boxplot mal rotulado en la defensa es el tipo de error que
  este proyecto no se puede permitir.

Opciones descartadas: **(1)** no serializar `serie_original` con carga
diaria — barato pero deja el boxplot y la serie temporal sin datos, UX
regresiva; **(3)** aplanar `timestamps_originales` a strings ISO — ahorra
~40 % pero deja 380 KB y rompe el tipo `TimestampNormalizado` del frontend
para todas las resoluciones.

#### 4. `moda_dias == 1`, no `<= 24`, en la inferencia de resolución

`_inferir_resolucion()` devuelve `"diaria"` **solo** cuando la moda de los
deltas es exactamente 1 día. Una moda de 7 días es un registro semanal;
15, quincenal. Ninguno tiene regla de agregación en METIS, y devolver
`"diaria"` para ellos los haría entrar al pipeline con una noción de "año
completo" que no les corresponde — quedan en `None` →
`CONTRACT_NO_TEMPORAL_RESOLUTION`, que es honesto: METIS no sabe
procesarlos.

Lo sub-diario también cae en `None`, por un efecto de `.days`: `(ts[1:] -
ts[:-1]).days` **trunca**. Una serie horaria da deltas de 0 días → moda 0
→ `None`. Es el bloqueo correcto y deseado, pero hoy es un efecto lateral
de `.days`; va como test explícito y como línea en el comentario de la
función para que un refactor a `total_seconds()` no lo rompa en silencio.

La moda —no el promedio— ya protege el caso real: un registro diario con
huecos (corte de energía, faja perdida) sigue teniendo moda 1 (mismo
argumento que F2.3 de DECISIÓN 057 para mensual).

### Lo que este plan NO hace, y por qué

#### El chequeo de espaciado temporal es inerte para toda serie agregada

`validar_contrato()` tiene un solo call site en producción
(`pipeline_etapa1.py`) y corre **después** del paso 0, que ya forzó
`resolucion_temporal = "anual"` y reemplazó los timestamps por los
años-etiqueta que `agregar_a_maximos_anuales()` construye con `range()` —
ascendentes por construcción. Consecuencia: la rama `"mensual"` de
`_espaciado_regular()` (Bloque F2.2 de DECISIÓN 057) ya es código muerto en
el pipeline, y una rama `"diaria"` nacería igual de muerta. Ningún hueco
temporal del archivo crudo se detecta como espaciado irregular en una serie
mensual o diaria — la historia la cuentan solo los warnings de agregación,
a granularidad de año.

Es el mismo patrón que motivó el Bloque H3 (`CONTRACT_WRONG_ORDER` era
código muerto post-agregación y hubo que moverlo antes del paso 0). **No se
arregla acá:** moverlo haría que series **mensuales ya auditadas** empiecen
a emitir `CONTRACT_IRREGULAR_SPACING` donde hoy no emiten nada — no cambia
ningún estadístico (las 9 series de regresión son anuales y no pasan por el
paso 0), pero sí la salida visible de análisis ya validados, y eso merece
su propio PR y su propia verificación. Registrado en
`docs/pendientes-tecnicos.md` como entrada abierta.

#### Exposición en la UI — bloqueada por R0.2, no por este plan

R0.2 (media diaria vs. pico instantáneo, `pendientes-facundo.md`) es la
pregunta hidrológica más importante: si la tesis construye sus máximos
anuales a partir de picos instantáneos, agregar desde medias diarias
**subestima sistemáticamente** la serie, y el sesgo no se corrige en
software. **Condición de salida:** los PRs se mergean y diaria funciona en
el backend con tests, pero el frontend no agrega ningún selector ni copy
que la anuncie hasta tener respuesta. El frontend nunca eligió resolución
(la infiere el backend), así que "no exponer" es no promocionarla, no un
rechazo explícito nuevo; si se quiere ese rechazo, es un cambio aparte que
necesita que el backend señale la resolución antes de abrir el stream.

### Corrección al registro del proyecto

La revisión 1 del plan afirmaba que el fixture
`docs/series prueba/serie_diaria_40anios.csv` tenía "365 × 40 filas
exactas, sin bisiestos" y que "con criterio estricto el propio fixture se
descartaría entero". **Las dos afirmaciones son falsas.** Re-contado fila
por fila (28/08/2026): 14.600 filas, 1980–2019, **con** bisiestos (366
días en 1980, 1984, …, 2016; 365 en el resto; 2019 con 355 porque el
archivo termina el 2019-12-21). Con criterio estricto (100 %) el fixture da
**39 años completos + 2019 descartado como `extremo_fin`** — exactamente lo
que DECISIÓN 057 ya prescribe, sin cambio alguno. **El fixture NO es
evidencia a favor de `cobertura_minima_interior < 1.0`.** Se deja asentado
porque el error viajó a la memoria del proyecto y podría reaparecer.

### Criterio de hecho

- `agregar_a_maximos_anuales(..., resolucion="diaria")` con tests
  unitarios: año completo sin recorte, bisiesto con `mes_inicio_anio = 1`,
  **bisiesto con `mes_inicio_anio ≠ 1`** (el período que arranca en marzo
  espera 366 días si su febrero es de un año bisiesto — el caso que se
  rompe si alguien reescribe `_esperados()` con aritmética de calendario a
  mano), "el máximo anual no es el valor del último día del mes" (la trampa
  de la clave de agrupación: asigna, no maximiza), recortes de inicio/fin,
  `mes_inicio_anio = 1` reproduce el año calendario, asimetría de cobertura
  extremo vs. interior, el recorte deja n < 10.
- `test_stream_agregacion_diaria.py` (integración, espejo del mensual):
  rechazar el atípico de Chow sobre la serie diaria agregada mapea el
  índice contra `serie_efectiva` (n≈15), no contra la serie diaria cruda;
  `serie_calendario` calculada por el camino directo.
- Los tests mensuales de `test_aggregation.py` pasan con el solo rename
  mecánico de `PeriodoDescartado` (`meses_*` → `unidades_*`) — son la
  prueba de no-regresión.
- **Pendiente de cierre del plan (DoD, no lo cubre CI):** las 9 series de
  regresión de `docs/auditoria/regresion/` dan idéntico; smoke test manual
  con `serie_diaria_40anios.csv` → 39 años; tamaño real del evento SSE
  diario medido, por debajo de los ~59 KB de DECISIÓN 058.

**Ver también:** [DECISIÓN 057](decision057.md) (agregación mensual, el
precedente directo — este plan hace para diaria lo que ese bloque hizo para
mensual), [DECISIÓN 058](decision058.md) (qué serie se expone dónde — el
cálculo de payload que este plan corrige), [DECISIÓN 066](decision066.md)
(el "no" al camino B), [DECISIÓN 038](decision038.md) (regla de catálogo de
errores que rige `CONTRACT_INCOMPLETE_YEARS_ACCEPTED`).
`docs/auditoria/pendientes/pendientes-facundo.md` — R0.1 (umbral de
cobertura), R0.2 (media diaria vs. pico, bloqueante de exposición), R0.3
(directo vs. encadenado).
