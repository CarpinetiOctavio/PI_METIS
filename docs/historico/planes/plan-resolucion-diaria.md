# Plan de implementación — resolución diaria como entrada

**Fecha:** 28/08/2026
**Revisión 2:** 28/08/2026 — revisión del plan contra el código. Ver §9 (Registro de revisión)
para el detalle de qué cambió y por qué. Los bloques R1.2, R2.1, R2.3, R3.3 y R3.4 cambiaron
de contenido, no solo de redacción: **no ejecutar la revisión 1 de este archivo.**
**Base:** `HEAD` al 28/08/2026
**Origen:** [`docs/informe-viabilidad-resoluciones-temporales.md`](informe-viabilidad-resoluciones-temporales.md), camino A.
**Precedente directo:** Bloque F del [plan de Etapa 2](plan-etapa2-implementacion.md) §7 — este plan hace
para diaria lo que ese bloque hizo para mensual, y reusa su arquitectura sin rediseñarla.

**Bloques `R1`–`R6`** (R de *resolución*) — prefijo nuevo para no colisionar con los bloques
A–H del plan post-avance ni con los 0/A–F del plan de Etapa 2.

---

## 0. Alcance — qué entra y qué no

**Entra:** aceptar `resolucion_temporal == "diaria"` como formato de entrada y agregarlo a
máximos anuales, con la misma regla de `mes_inicio_anio`, recorte de extremos y descarte de
hueco interior que ya rige para mensual.

**No entra, y se documenta explícitamente que no entra (R6):** correr la batería de Etapa 1 o
el ajuste de Etapa 2 sobre valores diarios sin agregar. Ver §4 del informe de viabilidad.

**No entra (revisión 2):** mover el chequeo de espaciado temporal antes del paso 0. La revisión
encontró que ese chequeo es estructuralmente inerte para cualquier serie agregada (R1.2), pero
arreglarlo cambiaría el comportamiento de warnings de series **mensuales ya auditadas**, que
está fuera de este alcance. Se registra en `pendientes-tecnicos.md` y se cierra aparte.

**Invariante que este plan no puede romper:** la batería estadística sigue corriendo sobre
`serie_efectiva`, una serie anual de n≈40. Ninguna de las 8 pruebas de Etapa 1 ni ninguna de
las 13 distribuciones se toca. Las 9 series de regresión de `docs/auditoria/regresion/` tienen
que dar bit a bit lo mismo antes y después de este plan — es el criterio de hecho más
importante de todos.

---

## R0 — Precondiciones: lo que hay que preguntar antes de cerrar (no antes de empezar)

Tres preguntas de dominio para `docs/auditoria/pendientes/pendientes-facundo.md`. **R0.1 y R0.3
se pueden implementar con posición provisoria documentada** —mismo patrón que el hueco interior
de DECISIÓN 057— pero el plan no se declara cerrado sin respuesta. **R0.2 es distinta: bloquea
la exposición de la funcionalidad, no su implementación** (ver su condición de salida).

**R0.1 — Umbral de completitud del año agregado desde diaria.**
Para mensual, "año completo" = 12/12 meses, regla limpia. Para diaria la regla análoga
(365/366 días) es más exigente, y hay que decidir a propósito si se relaja.

*Evidencia dentro del repo, re-verificada fila por fila el 28/08/2026:*
`docs/series prueba/serie_diaria_40anios.csv` tiene 14.600 filas de datos, cubre 1980–2019 y
**sí incluye días bisiestos** — 366 días en 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008,
2012 y 2016; 365 en el resto. El único año anómalo es **2019, con 355 días**, porque el archivo
termina el 2019-12-21.

> **Corrección a la revisión 1 de este plan.** La versión anterior afirmaba que el fixture tenía
> "365 × 40 filas exactas, sin bisiestos" y que "con criterio estricto el propio fixture se
> descartaría entero". Las dos afirmaciones son falsas. Con criterio estricto (100 %) el fixture
> da **39 años completos + 2019 descartado como `extremo_fin`**, que es exactamente lo que
> DECISIÓN 057 ya prescribe y funciona sin cambio alguno.
> **Consecuencia para este plan: el fixture NO es evidencia a favor de `cobertura_minima < 1.0`.**
> Si el umbral relajado se justifica, tiene que ser con registros reales de Facundo, no con el
> fixture sintético del repo.

**Pregunta:** en los registros reales con los que trabaja la tesis, ¿qué cobertura mínima de
días válidos hace aceptable el máximo de un año interior (100 %, ≥ 95 %, ≥ 90 %, "sin huecos en
la temporada húmeda")? *Adjuntar a la pregunta el conteo de días faltantes por año de al menos
un registro real suyo — sin eso la respuesta es una opinión, no un criterio.*
*Agrupar con la pregunta ya abierta de hueco interior mensual — es la misma a otra escala.*

**Posición provisoria propuesta:** `cobertura_minima_interior = 1.0` (estricto), con el
parámetro ya cableado y probado para aceptar valores menores. Es decir: **la capacidad de
relajar el umbral entra en este plan; el relajamiento efectivo no.** Razón: sin evidencia de
registros reales, bajar el umbral es introducir un sesgo declarado a cambio de nada verificable.

**R0.2 — Media diaria vs. pico instantáneo. (Bloqueante de exposición.)**
Un limnígrafo diario suele reportar **media diaria**, no el pico instantáneo del día. Si la
tesis construye sus máximos anuales a partir de picos, agregar desde medias diarias
**subestima sistemáticamente** la serie de máximos anuales, y el sesgo no se corrige en
software. Es la pregunta hidrológica más importante del plan.
**Pregunta:** ¿qué variable se espera en un archivo diario, y corresponde advertirlo?
**Si la respuesta es "puede ser cualquiera de las dos"**, el plan gana un alcance extra: un
campo nuevo en la configuración del análisis, persistido en `analyses.configuracion` junto a
`mes_inicio_anio` (misma razón de auditoría: cambia el resultado, sin él el historial no es
reproducible). *Esa rama no está estimada en §7 — es la única que puede agregar un PR.*

> **Se manda ANTES de abrir el PR 1, no junto con él** (cambio de la revisión 2). Su respuesta
> puede agregar una columna persistida, y descubrir eso con los PRs 1–3 ya mergeados significa
> una migración retroactiva sobre análisis diarios ya guardados sin el campo.
>
> **Condición de salida si no hay respuesta a tiempo:** los PRs 1–4 se mergean, pero la carga
> diaria **no se expone en la UI** — `resolucion_temporal == "diaria"` funciona en el backend y
> queda cubierta por tests, y el frontend sigue rechazando el archivo en la pantalla de carga.
> Es preferible a publicar una capacidad que puede estar produciendo máximos sesgados a la baja
> sin que ni el usuario ni el historial lo registren.

**R0.3 — ¿Diaria → anual directo, o encadenado diaria → mensual → anual?**
Cambia el resultado cuando hay meses parcialmente faltantes: el encadenado descarta el mes y
después evalúa el año sobre 11 meses; el directo evalúa la cobertura del año completo de una.
**Posición provisoria propuesta:** directo diaria → anual. Es lo que preserva la máxima
información y lo que hace que `mes_inicio_anio` opere sobre un solo nivel.
*Nota de coherencia (revisión 2):* si se elige la opción 2 de payload (R3.3), el sistema va a
**calcular** una agregación mensual intermedia para presentación. Esa agregación es solo para
graficar y **no** alimenta la serie anual — el camino estadístico sigue siendo directo. Hay que
decirlo explícitamente en la decisión de R6 para que nadie lo lea como el encadenado de R0.3.

> **R0.1 y R0.3 se mandan al abrir el PR 1. R0.2 antes.** Mismo criterio que el
> plan de Etapa 2 aplicó a las preguntas de F6, con la excepción ya explicada.

---

## R1 — El portón (`parser.py`) y un hallazgo sobre `contract.py`

### R1.1 — `_inferir_resolucion()`

Hoy:
```python
if moda_dias >= 300: return "anual"
if moda_dias >= 25:  return "mensual"
return None                       # ← diaria cae acá
```

Después:
```python
if moda_dias >= 300: return "anual"
if moda_dias >= 25:  return "mensual"
if moda_dias == 1:   return "diaria"
return None
```

**`== 1`, no `<= 24`, y a propósito.** Una moda de 7 días es un registro semanal; una de 15,
quincenal. Ninguno de los dos tiene regla de agregación en este plan, y devolver `"diaria"`
para ellos los haría entrar al pipeline con una noción de "año completo" que no les
corresponde. Se mantienen en `None` → `CONTRACT_NO_TEMPORAL_RESOLUTION`, que es honesto:
METIS no sabe procesarlos.

**El `== 1` también cubre lo sub-diario, y conviene decirlo** (revisión 2): `moda_dias` sale de
`(ts[1:] - ts[:-1]).days`, que **trunca**. Una serie horaria da deltas de 0 días → moda 0 →
`None` → bloqueo. Correcto y deseado, pero hoy es un efecto lateral no documentado de `.days`;
si alguien reescribe la inferencia con `total_seconds()` lo rompe sin darse cuenta. Va como
test explícito en R5 y como línea en el docstring.

La moda —no el promedio— ya protege el caso real: un registro diario con huecos sigue teniendo
moda 1 (es el argumento de F2.3, verificado en su momento para mensual).

### R1.2 — Hallazgo: el chequeo de espaciado es inerte para series agregadas (no se implementa)

> **Este bloque cambió por completo en la revisión 2.** La revisión 1 proponía agregar una rama
> `"diaria"` a `_espaciado_regular()` y después *suprimir* `CONTRACT_IRREGULAR_SPACING` para
> carga diaria. Verificado contra el código: **ninguna de las dos cosas tendría efecto.**

**Lo verificado (28/08/2026).** `validar_contrato()` tiene **un solo call site en producción**:
`pipeline_etapa1.py:162`, y corre **después** del paso 0, que ya hizo
`resolucion_temporal = "anual"` y reemplazó los timestamps por los años-etiqueta que
`agregar_a_maximos_anuales()` construye con `range()`. Consecuencias:

1. La rama `"mensual"` de `_espaciado_regular()` —agregada en el Bloque F2.2— **hoy es código
   muerto en el pipeline**. Solo la alcanzan los tests unitarios que llaman a la función
   directamente.
2. Una rama `"diaria"` nacería igual de muerta.
3. `CONTRACT_IRREGULAR_SPACING` **no se dispara con carga diaria**, porque lo que evalúa son
   años-etiqueta consecutivos por construcción. No hay ruido que suprimir.

Es el mismo patrón exacto que motivó el Bloque H3: `CONTRACT_WRONG_ORDER` era código muerto
post-agregación y hubo que moverlo antes del paso 0 para que sirviera de algo.

**Qué hace este plan:** nada en el código. La entrada **ya está registrada** en
`docs/pendientes-tecnicos.md` (28/08/2026, junto con esta revisión — ese archivo es un registro
vivo, no un entregable de PR). Dice, en resumen:

> `_espaciado_regular()` es inerte para toda serie agregada — `validar_contrato()` corre después
> del paso 0, que ya forzó `resolucion_temporal="anual"` y timestamps ascendentes por `range()`.
> La rama `"mensual"` de F2.2 solo la ejecutan los tests unitarios. **Bloquea:** ningún hueco
> temporal del archivo crudo se detecta como espaciado irregular; la historia la cuentan
> únicamente los warnings de agregación, a granularidad de año. **Quién lo cierra:** un PR propio
> que mueva el chequeo antes del paso 0, como se hizo con `CONTRACT_WRONG_ORDER` en el Bloque H3
> — cambia el comportamiento de warnings de series mensuales ya auditadas, así que no puede ir
> colgado de otro plan.

**Por qué no se arregla acá:** moverlo haría que series mensuales ya auditadas empiecen a emitir
un warning que hoy no emiten. Eso no altera ningún estadístico (las 9 series de regresión son
anuales y ni siquiera pasan por el paso 0), pero sí altera la salida visible de análisis ya
validados, y ese es un cambio que merece su propio PR y su propia verificación — no un renglón
dentro del plan de diaria.

**Va también a la decisión de R6**, como parte de "qué NO hace este plan y por qué".

---

## R2 — El corazón: generalizar `aggregation.py`

Hoy el módulo tiene el mes cableado en tres lugares: `_meses_esperados()` construye 12 pares
`(año, mes)`, la completitud es `set(presentes) == esperados`, y `PeriodoDescartado` cuenta
`meses_presentes` / `meses_faltantes`.

### R2.1 — Firma

```python
def agregar_a_maximos_anuales(
    serie: list,
    timestamps: list,
    mes_inicio: int,
    resolucion: str = "mensual",           # "mensual" | "diaria"
    cobertura_minima_interior: float = 1.0,  # R0.1 / R2.3 — SOLO años interiores
) -> AgregacionResult:
```

**Los dos parámetros nuevos tienen default que reproduce exactamente el comportamiento de hoy.**
Es lo que permite que el PR 2 no toque una sola línea del camino mensual ya auditado, y que la
regresión de las 9 estaciones sea trivialmente verde.

**El nombre del parámetro dice a qué años aplica** (cambio de la revisión 2). Se llama
`cobertura_minima_interior`, no `cobertura_minima`, porque **los años de los extremos siempre
exigen 100 %** — ver R2.3. Un nombre neutro invitaba a asumir lo contrario.

### R2.2 — Las tres piezas a generalizar

**`_periodo_de(anio, mes, mes_inicio)` — no se toca.** Depende solo de año y mes; una fecha
diaria cae en el mismo período que su mes. Es la razón de fondo por la que este cambio es
barato: `mes_inicio_anio` sigue operando en granularidad de mes sin importar la resolución
del dato.

**`_esperados(periodo, mes_inicio, resolucion)`** — reemplaza a `_meses_esperados()`:
- `"mensual"`: los 12 pares `(año, mes)` de hoy, sin cambios.
- `"diaria"`: generar con `pd.date_range(inicio, fin, freq="D")` entre el primer día del
  período y el último. **Los bisiestos salen gratis** — `date_range` los resuelve; no hay que
  escribir aritmética de calendario a mano, que es donde este tipo de código se rompe.
  Ojo con el caso que importa: con `mes_inicio ≠ 1` el febrero del período es el del **año
  siguiente** al año-etiqueta (el período que arranca en marzo de 2015 termina en febrero de
  2016 y espera 366 días). `date_range` lo resuelve solo; el test de R5 existe para que siga
  siendo así.

**La clave de agrupación** pasa de `(fecha.year, fecha.month)` a
`(fecha.year, fecha.month)` o `(fecha.year, fecha.month, fecha.day)` según resolución.

> **Trampa verificada (revisión 2), leer antes de tocar esta línea.** El cuerpo del loop hace
> `por_periodo.setdefault(periodo, {})[clave] = float(valor)` — **asigna, no maximiza**. Con
> datos mensuales da igual: hay un valor por clave. **Con datos diarios y la clave en
> granularidad de mes, el diccionario se queda con el último día de cada mes y descarta el
> resto en silencio** — no da error, no da warning, y el resultado es un número plausible pero
> incorrecto. De ahí que la clave TENGA que incluir el día cuando `resolucion == "diaria"`, y de
> ahí el criterio de DoD §8.7 (ninguna llamada con resolución implícita) y el test de R5
> ("el máximo anual ≠ el valor del último día del mes de ese año").

**La completitud** pasa de igualdad de conjuntos a cobertura, **con la regla asimétrica de R2.3**:
```python
cobertura = len(presentes) / len(esperados)
es_extremo = periodo in (periodo_inicio, periodo_fin)
umbral = 1.0 if es_extremo else cobertura_minima_interior
completo = cobertura >= umbral
```
Con `cobertura_minima_interior = 1.0` esto es **equivalente** a la igualdad de conjuntos de hoy
(`presentes ⊆ esperados` siempre, por construcción de la clave), así que no es un cambio de
semántica para mensual — es una generalización que lo contiene como caso particular. Vale la
pena dejarlo escrito en el docstring: es el mismo tipo de verificación de consistencia que
DECISIÓN 057 usó con `mes_inicio = 1`.

**`PeriodoDescartado`** — renombrar `meses_presentes`/`meses_faltantes` a
`unidades_presentes`/`unidades_faltantes` y agregar `unidades_esperadas`, para que el warning
no tenga que asumir 12. *El rename es breaking para los tests unitarios de `test_aggregation.py`
y para `_warnings_de_agregacion()`; los dos van en el mismo PR (PR 2).*

### R2.3 — La regla asimétrica de cobertura, y el sesgo que declara

> **Cambio de la revisión 2.** La revisión 1 proponía un umbral único para todos los años. Eso
> tiene una consecuencia que no estaba escrita: en el código, la rama es
> `if completo: aceptar; else: clasificar como extremo/hueco`. Con un umbral único de 0,95, un
> año **de borde** con 350/365 días pasaría a **aceptarse** en vez de recortarse — desactivando
> DECISIÓN 057 justo en los bordes, que es donde su argumento del sesgo a la baja es más fuerte
> y donde ya está defendido por escrito.

**La regla que adopta este plan:**

| Tipo de período | Cobertura exigida | Si no la alcanza |
|---|---|---|
| `periodo_inicio` (primer año del registro) | **100 %, siempre** | descartado, `MOTIVO_EXTREMO_INICIO` |
| `periodo_fin` (último año del registro) | **100 %, siempre** | descartado, `MOTIVO_EXTREMO_FIN` |
| Años interiores | `cobertura_minima_interior` | descartado, `MOTIVO_HUECO_INTERIOR` |

**Por qué asimétrica.** DECISIÓN 057 descarta los extremos parciales porque *"el máximo de un
año parcial está sesgado a la baja por construcción"*, y en un extremo la parcialidad es la
regla, no la excepción: el registro simplemente empieza o termina ahí. En el interior, en
cambio, un hueco del 2 % es una falla de instrumentación sobre un año que sí se midió entero.
Son dos situaciones distintas y la revisión 1 les daba el mismo tratamiento. **Con esta regla,
DECISIÓN 057 queda intacta y no hay que reabrirla** — este plan solo agrega una tolerancia
nueva donde antes no había ninguna regla escrita.

**El sesgo que igual queda declarado.** Aceptar un año interior con 95 % de días implica que su
máximo está sesgado a la baja: faltan días que podrían haber contenido el pico.
**Consecuencia obligatoria:** el warning de agregación tiene que decir, para cada año aceptado
por debajo del 100 %, cuántos días le faltaron. Un año aceptado con hueco no puede quedar
invisible — es la misma regla de "descartar no es borrar en silencio" de DECISIÓN 057, aplicada
a "aceptar con reservas".
**Código:** `CONTRACT_INCOMPLETE_YEARS_ACCEPTED`, nuevo, nivel `normal`.
Es el único código nuevo que este plan necesita (ver R4.2).

**Con la posición provisoria de R0.1 (`cobertura_minima_interior = 1.0`) este warning no se
emite nunca todavía** — pero el código, el catálogo, la traducción y el test entran igual, para
que habilitar el umbral cuando Facundo responda sea cambiar una constante y nada más.

---

## R3 — Pipeline, warnings y la decisión de payload

### R3.1 — `pipeline_etapa1.py`

```python
if resolucion_temporal in ("mensual", "diaria"):
    agregacion = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio_anio,
        resolucion=resolucion_temporal,
        cobertura_minima_interior=COBERTURA_MINIMA_INTERIOR[resolucion_temporal],
    )
```
El resto del paso 0 (forzar `resolucion_temporal = "anual"`, `serie_efectiva`,
`timestamps_efectivos`) queda **idéntico**. El paso 0a (orden cronológico, DECISIÓN 030) sigue
corriendo antes y sin cambios — verificado que está en `pipeline_etapa1.py:123`, antes del paso
0; su argumento de por qué va primero aplica igual a diaria, palabra por palabra, y de hecho más
fuerte: con 14.600 filas la probabilidad de desorden en un archivo real es mayor.

### R3.2 — `_warnings_de_agregacion()`

Hoy la descripción hardcodea `f"{p.anio} ({p.meses_presentes}/12 meses)"`. Pasa a usar
`unidades_presentes`/`unidades_esperadas` y una etiqueta de unidad (`"meses"` / `"días"`).
**Sin cambio de código de error** para los dos existentes — `CONTRACT_PARTIAL_YEARS_TRIMMED` y
`CONTRACT_INCOMPLETE_YEARS_DISCARDED` tienen nombres neutros a la resolución y siguen
significando exactamente lo mismo. Suma la emisión de `CONTRACT_INCOMPLETE_YEARS_ACCEPTED`
(R2.3), con el detalle de días faltantes por año aceptado.

### R3.3 — Payload: la decisión que hay que tomar a propósito

DECISIÓN 058 calculó el bloque `datos` de `result_etapa1` para el peor caso mensual
(1.200 ítems) en **~59 KB** y concluyó que estaba *"muy por debajo de cualquier límite
práctico"*. Medido para diaria-40-años sobre el fixture real del repo:

| Campo | Ítems | Medido |
|---|---|---|
| `serie_original` | 14.600 | 110 KB |
| `timestamps_originales` (`{"iso","anio"}`) | 14.600 | 528 KB |
| **Total bloque `datos`** | | **≈ 637 KB** |

**~11× el peor caso mensual**, por evento SSE y persistido en `analysis_results.etapa1` (JSONB)
en cada análisis de CU-01. No es catastrófico, pero **contradice el razonamiento explícito de
DECISIÓN 058** y no puede resolverse por omisión.

Tres opciones, con recomendación:

1. **No serializar `serie_original`/`timestamps_originales` con `"diaria"`.** Es el criterio que
   ya se aplica con carga anual (donde duplicarlos es "peso muerto"). Costo:
   `Etapa1BoxplotMensualChart` y `Etapa1SerieTemporalChart` se quedan sin datos con carga diaria
   — se degradan a no renderizar. Barato pero regresivo en UX.
2. **Serializar la agregación intermedia a máximos mensuales** en lugar de la serie diaria cruda
   (≈ 480 ítems para 40 años, ~24 KB — por debajo del caso mensual ya dimensionado).
   **← Recomendada**, con las dos condiciones obligatorias de más abajo. Es coherente con cómo
   razona el sistema: cada capa trabaja en su propio dominio, la serie diaria cruda no tiene por
   qué llegar al navegador.
3. **Aplanar `timestamps_originales` a strings ISO** (el `anio` es derivable en el cliente).
   Ahorra ~40 %, pero deja 380 KB y rompe el tipo `TimestampSerializado` del frontend para
   todas las resoluciones. Peor relación costo/beneficio.

> **La opción 2 NO es gratis en frontend — corrección de la revisión 2.** La revisión 1 decía que
> los dos gráficos seguirían funcionando *"sin tocar una línea de frontend"*. Mecánicamente es
> cierto: reciben la misma forma de dato y renderizan. **Semánticamente es falso.**
> `Etapa1BoxplotMensualChart` agrupa por mes los valores de `serie_original` y su propio
> docstring dice que consume *"la serie mensual CRUDA, no la agregada"*. Si con carga diaria
> recibe máximos mensuales, el gráfico pasa a mostrar **la distribución de los máximos
> mensuales** en vez de **la distribución de los valores mensuales** — mismo dibujo, otra
> estadística, sin ningún rótulo que lo diga. Un boxplot mal rotulado en la defensa es
> exactamente el tipo de error que este proyecto no se puede permitir.

**Las dos condiciones obligatorias de la opción 2** (dejan de ser "sugerencia a cerrar en R6" y
pasan a ser parte del alcance de los PRs 2 y 3):

- **(a) Campo nuevo `datos.resolucion_serie_original: "diaria" | "mensual" | "anual"`**, distinto
  de `resolucion_original` (que es la del archivo). Sin él, el nombre `serie_original` miente
  con carga diaria. Backend: PR 2. Tipo en `types.ts`: PR 3.
- **(b) El boxplot y la serie temporal usan ese campo para rotular.** Título y/o subtítulo del
  boxplot: "valores mensuales" cuando `resolucion_serie_original === "mensual"` y el archivo era
  mensual; "máximos mensuales (agregados desde datos diarios)" cuando el archivo era diario.
  Es trabajo de frontend real y está estimado como tal en §7 (PR 3).

### R3.4 — `_calcular_serie_calendario()`

`analysis_service.py` filtra hoy por `result.resolucion_original != "mensual"`. Pasa a
`not in ("mensual", "diaria")`. `hubo_agregacion` (misma función, más abajo) igual.

> **Corrección de la revisión 2 — este es el punto donde el plan producía un número mal sin
> síntoma.** La revisión 1 decía solamente que *"la segunda agregación con `mes_inicio=1` corre
> sobre la serie diaria cruda: ~14.600 ítems, una sola pasada, coste despreciable"* — hablaba del
> costo y no de la corrección. La llamada actual es:
>
> ```python
> agregacion = agregar_a_maximos_anuales(
>     result.serie_original, result.timestamps_originales, mes_inicio=1
> )
> ```
>
> Con los defaults de R2.1 eso corre **en modo `"mensual"` sobre datos diarios**: la clave de
> agrupación es `(año, mes)`, la asignación sobreescribe (ver la trampa de R2.2), y
> `serie_calendario` termina siendo **el máximo de los últimos días de cada mes**, no el máximo
> anual. Silencioso, plausible y equivocado.

**Lo que hay que escribir, explícitamente:**
```python
agregacion = agregar_a_maximos_anuales(
    result.serie_original,
    result.timestamps_originales,
    mes_inicio=1,
    resolucion=result.resolucion_original,                       # ← obligatorio
    cobertura_minima_interior=COBERTURA_MINIMA_INTERIOR[result.resolucion_original],
)
```

**Segundo punto de coherencia (opción 2 de R3.3).** Si `serie_original` en el **payload** pasa a
ser la agregación mensual, `result.serie_original` dentro de `Etapa1Result` **tiene que seguir
siendo la serie diaria cruda**, porque es lo que alimenta esta segunda agregación. Si se
reemplaza también ahí, `serie_calendario` quedaría calculada por el camino **encadenado
diaria → mensual → anual**, mientras la serie configurada usa el **directo** — dos series
comparadas en el mismo gráfico calculadas con métodos distintos, que es precisamente lo que R0.3
resolvió no hacer. **La transformación de la opción 2 ocurre solo en la serialización.**
Va como comentario en el código y como test de integración en R5.

---

## R4 — Frontend y catálogo de errores

### R4.1 — Tipos, condicionales y rótulos

| Archivo | Cambio | Trivial |
|---|---|---|
| `api/types.ts:147` | `"anual" \| "mensual" \| null` → `\| "diaria"` | sí |
| `api/types.ts` | campo nuevo `resolucion_serie_original` (R3.3a) | sí |
| `api/types.ts:150` | comentario: la condición de presencia ya no es solo mensual | sí |
| `Etapa1BoxplotMensualChart.tsx:48` | guard `!== "mensual"` → acepta también `"diaria"` | sí |
| `Etapa1BoxplotMensualChart.tsx` | **rótulo según `resolucion_serie_original`** (R3.3b) | **no** |
| `Etapa1SerieTemporalChart.tsx:25` | guard del toggle configurado/calendario → `∈ {"mensual","diaria"}` | sí |
| `Etapa1SerieTemporalChart.tsx` | **rótulo de la serie cruda** (R3.3b) | **no** |

Los dos rótulos son el trabajo real de este bloque; el resto son guards de una línea.

### R4.2 — Catálogo de errores (DECISIÓN 038, tres direcciones)

Un solo código nuevo: `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` (R2.3). Va a `api-contracts.md`
(sección de warnings no bloqueantes), a `frontend/src/i18n/errors.es.ts`, y lo emite
`_warnings_de_agregacion()` — **los tres en el mismo commit**. `./scripts/check-error-catalog.sh`
verde es criterio de hecho, no un chequeo posterior.

---

## R5 — Tests

**Unitarios de `agregar_a_maximos_anuales()` con `resolucion="diaria"`** — espejo de los que ya
existen para mensual en `tests/unit/core/validacion/test_aggregation.py`:

- año completo sin recorte (365 días, `mes_inicio=1`);
- **año bisiesto con `mes_inicio=1`**: 366 días exactos se acepta; 365 días en año bisiesto
  queda por debajo del 100 %;
- **año bisiesto con `mes_inicio ≠ 1` (el que de verdad rompe `_esperados()`)**: período
  `mes_inicio=3` que arranca en 2015 termina en febrero de **2016** y espera **366** días; el
  que arranca en 2014 espera 365. Es el caso que se rompe si alguien reescribe `_esperados()`
  con aritmética de calendario a mano, y el que la revisión 1 no cubría;
- **el máximo anual no es el valor del último día del mes** — serie diaria construida a
  propósito con el pico a mitad de mes y un valor bajo el día 31; detecta la trampa de R2.2 y
  la llamada sin `resolucion=` de R3.4;
- recorte de inicio, recorte de fin, los dos extremos a la vez;
- `mes_inicio = 1` reproduce el año calendario; `mes_inicio = 12` cruza el cambio de año;
- hueco interior → `CONTRACT_INCOMPLETE_YEARS_DISCARDED`;
- **asimetría de cobertura (R2.3)**: año **interior** al 96 % con
  `cobertura_minima_interior = 0.95` → **aceptado** con `CONTRACT_INCOMPLETE_YEARS_ACCEPTED`; el
  mismo año al 96 % en posición de **extremo** → **descartado** con `MOTIVO_EXTREMO_*` aunque el
  umbral interior lo permitiría; el interior al 96 % con `cobertura_minima_interior = 1.0` →
  descartado;
- el recorte deja n < 10 → `CONTRACT_SERIES_TOO_SHORT` bloqueante.

**Test de no-regresión (el más importante del plan):** `agregar_a_maximos_anuales()` con la
firma nueva y defaults (`resolucion="mensual"`, `cobertura_minima_interior=1.0`) devuelve
**exactamente** lo mismo que antes para todos los casos mensuales existentes. Los tests actuales
de `test_aggregation.py` que pasan sin modificarse **son** esa prueba — con la única excepción
del rename de `PeriodoDescartado` (R2.2), que es mecánico: si alguno necesita cambiar por
cualquier otro motivo, es señal de que la generalización rompió semántica.

**`test_parser.py`:** moda 1 → `"diaria"`; moda 7 y 15 → `None` (el caso semanal/quincenal, que
es lo que justifica el `== 1`); **serie horaria → moda 0 → `None`** (el efecto de `.days` que
R1.1 documenta).

**`test_contract.py`:** **sin cambios** (revisión 2). El bloque R1.2 ya no toca `contract.py`.
Se agrega en su lugar un test que fija el hallazgo: `validar_contrato()` invocada como la invoca
el pipeline (post-agregación, `resolucion_temporal="anual"`, timestamps año-etiqueta) **no**
emite `CONTRACT_IRREGULAR_SPACING` para una serie diaria con huecos — documenta la inercia para
que el día que se arregle, el test falle y obligue a mirarlo.

**Integración:** `tests/integration/test_stream_agregacion_diaria.py`, espejo de
`test_stream_agregacion_mensual.py` — incluidos:
- el caso que ese archivo cubre y que es fácil de volver a romper: **rechazar el atípico de Chow
  sobre una serie diaria agregada** mapea el índice contra `serie_efectiva` (n≈40) y no contra
  la serie diaria cruda (n≈14.600);
- **`serie_calendario` calculada por el camino directo** (R3.4): con `mes_inicio_anio ≠ 1` y
  carga diaria, el valor de cada año de `serie_calendario` coincide con el máximo de los valores
  **diarios** de ese año calendario, no con el máximo de los máximos mensuales.

**Regresión:** las 9 series de `docs/auditoria/regresion/` dan idéntico. Es el criterio de hecho
que decide si este plan se mergea.

---

## R6 — Documentación y decisiones

**`decision065.md` — Diaria como resolución de entrada.** Cubre las elecciones que este plan
toma y que no son derivables del código:
1. Diaria como resolución de entrada, agregada a máximos anuales (camino A), directo
   diaria → anual (R0.3).
2. `cobertura_minima_interior` como parámetro, **con su regla asimétrica** (100 % en los
   extremos, umbral en el interior), el valor provisorio 1.0, y el sesgo que declara (R2.3).
   Incluye por qué la asimetría deja DECISIÓN 057 intacta en vez de reabrirla.
3. La opción de payload elegida y por qué (R3.3), incluida la corrección al cálculo de
   DECISIÓN 058 y el campo `resolucion_serie_original` con su efecto en el rótulo del boxplot.
4. `== 1` y no `<= 24` en la inferencia de resolución, y el efecto de `.days` sobre lo
   sub-diario (R1.1).
5. **Lo que este plan NO hace y por qué:** el chequeo de espaciado inerte (R1.2), ya abierto
   en `pendientes-tecnicos.md`; moverlo cambiaría warnings de series mensuales ya auditadas.
6. **Corrección al registro:** la revisión 1 de este plan afirmaba que el fixture diario no
   tenía bisiestos y que se descartaría entero con criterio estricto. Es falso (R0.1). Se deja
   asentado porque el error viajó a la memoria del proyecto y podría reaparecer.

**`decision066.md` — El "no" del camino B.** Declara que *el dominio de análisis de METIS es la
serie de máximos anuales, cualquiera sea la resolución de entrada*, con las razones de §4 del
informe de viabilidad: la varianza de Mann-Kendall bajo autocorrelación, Chow/Grubbs-Beck
definido para picos anuales i.i.d., `T = (n+1)/m` en unidades del intervalo de muestreo, y
Fisher-Tippett aplicando a máximos de bloque. **Va en un archivo aparte y no depende de que este
plan se implemente** — es la que se defiende ante el tribunal, y vale por sí sola aunque el resto
se posponga.
*Antes de citar cualquier referencia bibliográfica en esa decisión, verificarla contra el
original — regla del proyecto. Las del informe (Hamed & Rao 1998; Hirsch/Slack/Smith 1982;
von Storch 1995; Langbein 1949; Cunnane 1973; Coles 2001) NO fueron verificadas.*

**Archivos a actualizar al cerrar:** `constraints.md` (sección de año hidrológico),
`statistical-pipeline.md` (paso 0), `api-contracts.md` (código nuevo + `resolucion_temporal` +
`resolucion_serie_original`), `pendientes-tecnicos.md` (verificar que la entrada de R1.2 sigue abierta), `CLAUDE.md` si cambia
el resumen del contrato, `pendientes-facundo.md` (R0.1–R0.3), `sprint.md`.

---

## 7. Orden de PRs

Tamaños relativos, no horas — la unidad de comparación es el Bloque F del plan de Etapa 2, que
fue **M**. Ajustar al ejecutar.

| PR | Bloque | Sale de | Depende de | Toca frontend | Tamaño | De dónde sale el tamaño |
|---|---|---|---|---|---|---|
| 0 | Mandar R0.2 a Facundo (no es código) | — | — | no | — | un mensaje, pero va **antes** del PR 1 |
| 1 | R1.1 — `parser.py` + tests de inferencia; mandar R0.1/R0.3 | `staging` | PR 0 enviado | no | **XS** | 3 líneas de código, 3 tests |
| 2 | R2 + R3 — `aggregation.py`, pipeline, warnings, payload, `_calcular_serie_calendario()` | `staging` | PR 1 | no | **M** | el grueso del plan; ~10 tests unitarios nuevos + 2 de integración |
| 3 | R4 — tipos, guards, código de error nuevo y **los dos rótulos** de R3.3b | `staging` | PR 2 | sí | **S** | 6 cambios triviales + 2 de copy/render con verificación en navegador |
| 4 | R6 — `decision065.md`, `decision066.md`, actualización de docs | `staging` | PR 3 | no | **S** | dos decisiones largas, sin código |

**R5 no es un PR:** los tests van en el PR que introduce el comportamiento que verifican.

**El PR 4 se puede adelantar en parte:** `decision066.md` (el "no" del camino B) no depende de
ninguno de los otros y se puede escribir hoy. Es además el entregable con mayor valor por
unidad de esfuerzo de todo el plan, porque se defiende aunque la implementación se posponga.

**Si R0.2 responde "puede ser cualquiera de las dos"**, aparece un **PR 2.5** (entre el 2 y el
3): campo nuevo en `analyses.configuracion` + migración + propagación al historial. Tamaño
estimado **S–M**; no está incluido en la tabla porque depende de una respuesta que todavía no
tenemos.

**Coordinación con Octavio — igual que en el Bloque F.** El PR 2 cambia la firma de
`agregar_a_maximos_anuales()` y renombra los campos de `PeriodoDescartado`. Aunque los defaults
preservan el comportamiento, sus fixtures de regresión de Etapa 2 la tocan indirectamente:
avisarle antes de mergear.

---

## 8. Definition of done

Además del DoD general del repo (§10 del plan de Etapa 2):

1. `pytest -m "unit or integration"`, `ruff check`, `ruff format --check` — **dentro del
   contenedor**, no contra el Python del host.
2. `npm run lint && npm test && npm run build`.
3. Los cuatro jobs de `ci.yml` verdes, incluido `error-catalog`.
4. **Las 9 series de regresión dan idéntico a antes del plan.** Sin esto no se mergea nada.
5. Verificación manual con `docs/series prueba/serie_diaria_40anios.csv`: el archivo atraviesa
   el pipeline completo y produce **39 años** (1980–2018 completos; 2019 descartado como
   `extremo_fin` con 355/365 días), y el warning de agregación dice exactamente eso.
   *Este número es una predicción verificable, no una aproximación: si el resultado no es 39,
   algo de R2 está mal.*
6. Verificación manual del tamaño real del evento SSE con carga diaria, **medido — no estimado**.
   Con la opción 2 de R3.3 el bloque `datos` tiene que quedar por debajo de los ~59 KB del peor
   caso mensual de DECISIÓN 058.
7. **Ninguna llamada a `agregar_a_maximos_anuales()` queda con resolución implícita.**
   Verificable por grep: toda invocación no-test pasa `resolucion=` explícito. Es el criterio
   que previene el error silencioso de R3.4 y la trampa de R2.2.
8. El boxplot mensual, con carga diaria, muestra un rótulo que dice que grafica máximos
   mensuales agregados — verificado en el navegador, no solo por test.

---

## 9. Registro de revisión

**Revisión 2 — 28/08/2026.** Revisión del plan contra el código del repo. Qué cambió:

| # | Bloque | Cambio |
|---|---|---|
| 1 | R0.1 | El fixture diario **sí tiene bisiestos** (re-contado fila por fila). La evidencia que sostenía `cobertura_minima < 1.0` era falsa; con criterio estricto el fixture da 39 años + 2019 recortado. Posición provisoria pasa a **1.0 estricto**, con el parámetro cableado pero sin habilitar. |
| 2 | R1.2 | Verificado que `validar_contrato()` corre **después** del paso 0 en su único call site: la rama `"mensual"` de `_espaciado_regular()` ya es código muerto y una `"diaria"` nacería igual. El bloque pasa de "implementar y suprimir el warning" a **hallazgo documentado** en `pendientes-tecnicos.md`. PR 1 se reduce a `parser.py`. |
| 3 | R2.2 / R3.4 | La clave de agrupación **asigna, no maximiza**. `_calcular_serie_calendario()` llamado sin `resolucion=` sobre datos diarios devuelve el máximo de los últimos días de cada mes — silencioso e incorrecto. Se documenta la trampa y se explicita la llamada correcta. |
| 4 | R2.1 / R2.3 | Cobertura **asimétrica**: 100 % obligatorio en los extremos, umbral solo en años interiores. El parámetro se renombra a `cobertura_minima_interior`. Deja DECISIÓN 057 intacta en vez de reabrirla en los bordes. |
| 5 | R3.3 / R4.1 | La opción 2 de payload **no** es transparente para el frontend: cambia la semántica del boxplot mensual sin rotularlo. `resolucion_serie_original` pasa de sugerencia a requisito, y los dos rótulos entran al alcance del PR 3. |
| 6 | R0.2 / §7 | R0.2 se manda **antes** del PR 1 (puede agregar una columna persistida) y gana condición de salida: sin respuesta, se mergea el backend pero no se expone la carga diaria en la UI. |
| 7 | R5 | Tests nuevos: bisiesto con `mes_inicio ≠ 1`, "el máximo no es el último día del mes", asimetría de cobertura extremo vs. interior, serie horaria → `None`, `serie_calendario` por camino directo. |
| 8 | §7 | Tabla con columna de tamaño relativo y su justificación; PR 0 explícito; PR 2.5 condicional a R0.2. |
| 9 | §8 | DoD 5 pasa de "~39-40 años" a **39, predicción verificable**; DoD 7 (grep de resolución explícita) y DoD 8 (rótulo del boxplot) nuevos. |
