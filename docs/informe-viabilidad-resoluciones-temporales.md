# Informe de viabilidad — procesamiento de series diarias y mensuales

**Fecha:** 28/08/2026
**Estado:** relevamiento e investigación. **No es una decisión** — es el insumo para tomarla.
**Autor del relevamiento:** sesión de asistencia sobre el repo, a pedido de Kevin.
**Base:** `HEAD` al 28/08/2026, código real de `backend/metis/`, `.claude/rules/` y `docs/decisiones/`.

---

## 0. Resumen ejecutivo

La pregunta "¿que METIS procese series diarias y mensuales?" esconde **dos preguntas
distintas** que tienen respuestas opuestas:

| | Trabajo | Compatibilidad | Riesgo académico |
|---|---|---|---|
| **A. Aceptar diaria/mensual como resolución de *entrada*, agregando a máximos anuales** | Bajo (1–2 PRs, tamaño de un bloque) | **Alta** — la costura ya existe | Nulo. Es el flujo hidrológico estándar |
| **B. Correr Etapa 1 y Etapa 2 *sobre* los valores diarios/mensuales sin agregar** | Alto (motor estadístico nuevo) | **Baja** | **Alto** — invalida el marco teórico de la tesis |

**Mensual ya está implementado por el camino A** (DECISIÓN 057). Lo que falta es **diaria**,
y es barato. El camino B, para mensual, es exactamente el bug F2.1 que DECISIÓN 057 cerró
a propósito.

---

## 1. Estado real del código — qué hay hoy

### 1.1 Mensual: ya funciona, por el camino A

`core/pipeline/pipeline_etapa1.py::ejecutar_etapa1()`, paso 0:

```python
if resolucion_temporal == "mensual":
    agregacion = agregar_a_maximos_anuales(serie, timestamps, mes_inicio_anio)
    serie = agregacion.serie
    timestamps = agregacion.timestamps
    resolucion_temporal = "anual"   # el resto del pipeline no sabe que hubo agregación
```

Toda la infraestructura de granularidad ya está construida y auditada:

- `core/validacion/aggregation.py` — agregación a máximos anuales con `mes_inicio_anio ∈ [1..12]`,
  recorte de extremos parciales (`CONTRACT_PARTIAL_YEARS_TRIMMED`) y descarte de hueco interior
  (`CONTRACT_INCOMPLETE_YEARS_DISCARDED`).
- `Etapa1Result.resolucion_original` / `serie_efectiva` / `timestamps_efectivos` — la partición
  entre "lo que subió el usuario" y "lo que se analizó" (DECISIÓN 057 + 058).
- `contract.py::_espaciado_regular()` ya tiene una rama por resolución.
- Frontend: `resolucion_original` tipado, selector de mes en `ConfigPage`, `Etapa1BoxplotMensualChart`
  con el toggle calendario/configurado.
- `services/analysis_service.py` mapea el índice de Chow contra `serie_efectiva`, no contra la cruda.

**Esta es la costura que hace barato agregar "diaria".** Alguien ya pagó ese costo.

### 1.2 Diaria: hoy se bloquea, y de forma silenciosa-ish

El único portón es `parser.py::_inferir_resolucion()`:

```python
if moda_dias >= 300: return "anual"
if moda_dias >= 25:  return "mensual"
return None                       # ← diaria cae acá
```

Y `validar_contrato()` trata `resolucion_temporal is None` como **bloqueante**
(`CONTRACT_NO_TEMPORAL_RESOLUTION`).

**Verificado empíricamente** contra `docs/series prueba/serie_diaria_40anios.csv`
(el fixture que ya existe en el repo, generado para DECISIÓN 050):

```
n = 14600 → moda_dias = 1 → resolucion inferida = None → CONTRACT_NO_TEMPORAL_RESOLUTION
```

Dato relevante: **el límite de subida de 10 MB ya fue dimensionado contemplando el caso diario**
(DECISIÓN 050 midió diaria-40-años en 337 KB `.xlsx` / 445 KB `.csv`, y hasta el caso horario
en 7,68 MB). La infraestructura de transporte ya está preparada; lo que no está es la regla
de agregación.

---

## 2. La distinción que decide todo

> **Resolución de entrada ≠ dominio de análisis.**

METIS no es un analizador de series temporales genérico: es un motor de **análisis de frecuencia
de eventos extremos**. Su unidad de análisis es la **serie de máximos anuales**, y eso no es una
limitación de implementación — es lo que hace que el resultado (el evento de diseño de
T = 100 años) signifique algo.

La resolución del archivo que sube el usuario es otra cosa: es el formato en que el registro
existe en la realidad. Un limnígrafo entrega datos diarios; la serie de máximos anuales es un
**derivado** de ese registro, no un archivo distinto.

Aceptar diaria por el camino A no cambia el dominio de análisis: cambia dónde ocurre la
derivación (hoy la hace el usuario en Excel antes de subir; mañana la hace METIS, con la regla
explícita y auditada). Esto es **defendible sin fisuras** ante el tribunal y de hecho mejora
la propuesta de valor original del proyecto —"automatizar lo que Facundo hace a mano en Excel"—
porque la construcción de la serie de máximos anuales es precisamente uno de esos pasos manuales.

---

## 3. Camino A — diaria como resolución de entrada

### 3.1 Qué hay que tocar

| Capa | Cambio | Tamaño |
|---|---|---|
| `core/validacion/parser.py` | rama `moda_dias == 1 → "diaria"` en `_inferir_resolucion()` | trivial |
| `core/validacion/aggregation.py` | generalizar: hoy `_meses_esperados()` hardcodea 12 meses. Necesita una noción de "período completo" por resolución | **el trabajo real** |
| `core/validacion/contract.py` | rama `"diaria"` en `_espaciado_regular()` (`to_period("D")`) | trivial |
| `core/pipeline/pipeline_etapa1.py` | `if resolucion_temporal == "mensual"` → `in ("mensual", "diaria")` | trivial |
| `services/analysis_service.py` | **decisión de payload** (ver 3.3) | medio |
| `schemas/`, `api-contracts.md`, `errors.es.ts` | código de warning nuevo si la regla de completitud diaria lo amerita — regla de DECISIÓN 038, en las tres direcciones | bajo |
| `frontend/src/api/types.ts` | `"anual" \| "mensual" \| null` → agregar `"diaria"`; condición del boxplot mensual | bajo |
| Tests | unitarios de agregación diaria (bisiestos, recorte, año incompleto) + integración espejo de `test_stream_agregacion_mensual.py` | medio |
| `docs/decisiones/decisionNNN.md` | decisión numerada nueva | bajo |

**Estimación honesta: comparable al Bloque F de Etapa 2** — que es exactamente el precedente,
porque hace lo mismo para mensual. Uno o dos PRs apilados.

### 3.2 El único problema de diseño real: ¿qué es un "año completo" en diaria?

Para mensual, "completo" = los 12 meses presentes. Es una regla limpia y sin ambigüedad.

Para diaria, la regla análoga sería "los 365 (o 366) días presentes". **Esa regla es
impracticable con registros reales.** Ningún limnígrafo de 40 años tiene cero días faltantes:
se corta la energía, se pierde la faja, la estación queda fuera de servicio una semana.
Aplicar el criterio estricto descartaría casi todo el registro, con `periodos_descartados`
lleno y una serie que no llega a n=10.

> **CORRECCIÓN 28/08/2026 — este párrafo decía lo contrario y era falso.**
> La versión original afirmaba que el fixture `serie_diaria_40anios.csv` tenía "14.600 filas,
> o sea 365 × 40 exactas, **sin días bisiestos**", y que con criterio estricto "el fixture que
> el propio proyecto generó para representar el caso diario sería rechazado".
> **Re-contado fila por fila:** el fixture tiene 14.600 filas de datos, cubre 1980–2019 y **sí
> incluye días bisiestos** — 366 días en 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012 y
> 2016; 365 en el resto. El único año anómalo es **2019, con 355 días**, porque el archivo
> termina el 2019-12-21.
> Con criterio estricto (100 %) el fixture da **39 años completos + 2019 descartado como
> `extremo_fin`** — exactamente lo que DECISIÓN 057 ya prescribe, sin cambio alguno.
> **El fixture NO es evidencia a favor de relajar el umbral.** El argumento de los párrafos
> anterior y siguiente (los registros reales sí tienen días faltantes, y el umbral es una
> pregunta de dominio) sigue en pie por sí solo — lo que cae es esta supuesta confirmación
> dentro del repo. Si el umbral relajado se justifica, tiene que ser con registros reales de
> Facundo. Ver `docs/plan-resolucion-diaria.md` §R0.1 y §9.

Esto **no es un bug a resolver en código**: es una pregunta de dominio, hermana exacta de la
que ya está abierta en `pendientes-facundo.md` ("Hueco interior — ¿se descarta siempre, o hay
un umbral de meses?"). La práctica hidrológica habitual usa un umbral de completitud
(típicamente ≥ 90–95 % de días, o "sin huecos durante la temporada húmeda"), pero **quién fija
ese umbral es Facundo, no nosotros** — y conviene preguntarlo junto con la de hueco interior
mensual, porque son la misma pregunta a dos escalas.

Consecuencia práctica: **el camino A para diaria no se puede cerrar sin esa respuesta.**
Se puede implementar con una posición provisoria documentada (como se hizo con el hueco interior),
pero no se puede afirmar que está cerrado.

### 3.3 Segundo problema, este sí de ingeniería: el payload

DECISIÓN 058 calculó el tamaño del bloque `datos` de `result_etapa1` para el peor caso mensual
(100 años = 1.200 valores): **~59 KB**, y concluyó que estaba "muy por debajo de cualquier
límite práctico".

Recalculado para diaria-40-años con el fixture real del repo, con los mismos supuestos por ítem:

| Campo | Ítems | Tamaño medido |
|---|---|---|
| `serie_original` | 14.600 | **110 KB** |
| `timestamps_originales` (`{"iso", "anio"}`) | 14.600 | **528 KB** |
| **Bloque `datos` total** | | **≈ 637 KB** |

**~11× el peor caso mensual**, por evento SSE y **persistido en `analysis_results.etapa1` (JSONB)
en cada análisis de CU-01**. No es catastrófico, pero contradice el razonamiento explícito de
DECISIÓN 058 y hay que resolverlo a propósito, no por omisión. Opciones:

1. No serializar `serie_original`/`timestamps_originales` con `resolucion_original == "diaria"`
   (el mismo criterio que ya se aplica hoy con carga anual, donde duplicarlos es "peso muerto").
   Costo: el boxplot mensual y la vista de serie temporal se quedan sin la serie cruda.
2. Agregar a **mensual** para la vista descriptiva y serializar eso (1.200 ítems ≈ el caso ya
   dimensionado) — la serie diaria cruda no vuelve nunca al frontend.
3. Serializar los timestamps como lista de strings ISO plana en vez de objetos
   `{"iso", "anio"}` — el `anio` es derivable en el cliente. Ahorra ~40 %.

La opción 2 es la que más se parece a lo que el sistema ya hace conceptualmente
(cada capa razona en su propio dominio), pero es una decisión de producto, no una obviedad.

### 3.4 Lo que **no** hay que tocar (y por qué la compatibilidad es alta)

La batería estadística completa —las 8 pruebas de Etapa 1, las 13 distribuciones, EEA,
eventos de diseño— **no se toca en absoluto**. Corre sobre `serie_efectiva`, que sigue siendo
una serie anual de n≈40. Cero riesgo de regresión sobre las 9 estaciones auditadas
(`docs/auditoria/regresion/`), cero impacto en performance, cero fórmulas nuevas que justificar
en `formulas-etapa1.md` / `formulas-etapa2.md`.

Ese es el argumento fuerte: **el camino A es aditivo, no invasivo.**

---

## 4. Camino B — analizar la serie en su propia resolución

Acá está la pregunta que Kevin planteó: *"algunas fórmulas según la teoría solo funcionan para
las series anuales"*. Es correcto, y es más grave de lo que suena. El detalle, prueba por prueba.

### 4.0 Advertencia previa: para mensual, esto ya se decidió — y se decidió que no

DECISIÓN 057, sección "Contexto", punto 1, describe el estado previo del sistema:

> *"una serie mensual entra a Etapa 1 y corre Anderson, Wald-Wolfowitz, Cramer, Chow y el ajuste
> de las 13 distribuciones de Etapa 2 sobre los **valores mensuales crudos**, como si cada mes
> fuera un máximo anual. No falla ni advierte: devuelve un resultado con la forma correcta y
> **sin sentido hidrológico** — peor, la estacionalidad rompe independencia/homogeneidad por
> construcción, así que el usuario ve warnings críticos que son un artefacto del bug, no una
> propiedad real de sus datos."*

Eso **era el bug F2.1**, y el proyecto ya lo cerró con una decisión numerada. "Procesar series
mensuales como mensuales" es literalmente reabrirlo. Cualquier propuesta en esa dirección tiene
que explicar primero por qué DECISIÓN 057 estaba equivocada — y en mi lectura no lo está.

### 4.1 Etapa 1 — qué se rompe

**Independencia (Anderson III-1/III-3, Wald-Wolfowitz).**
En una serie diaria de caudales la autocorrelación no es una hipótesis a testear: es una
certeza física (recesión del hidrograma + estacionalidad). Anderson va a rechazar
prácticamente siempre. El test no está *mal calculado* — está *mal aplicado*: responde
"¿tiene correlación serial?" con un sí garantizado de antemano, y el usuario recibe un
warning CRÍTICO que no informa nada.
Nota secundaria: `k_max = n // 3` con n = 14.600 son ~4.866 lags → cálculo O(n²), ~71 M
operaciones. Problema de performance real, pero es el menor de los dos.

**Homogeneidad (Helmert, t de Student, Cramer).**
- Cramer particiona el último 60 % y 30 % de la serie. Sobre datos diarios esas particiones
  **cortan a mitad de temporada**: se compara un tramo que arranca en estiaje contra el total.
  La no-homogeneidad detectada sería estacional, no de régimen.
- Helmert cuenta cambios de signo respecto de la media: sobre datos diarios cuenta **ciclos
  estacionales**, no cambios de régimen.
- t de Student asume normalidad e independencia de las dos submuestras. Ambas violadas de forma
  masiva con datos diarios.

**Tendencia (Mann-Kendall, Kolmogorov-Smirnov).**
Este es el caso más citable de la literatura. La varianza del estadístico S de Mann-Kendall,
`Var(S) = n(n−1)(2n+5)/18`, **asume observaciones independientes**. Con autocorrelación positiva
—la norma en series diarias y mensuales— la varianza queda subestimada y el test **rechaza
"sin tendencia" mucho más de lo que corresponde**: el error de tipo I real supera ampliamente
al α = 5 % nominal. Es un resultado clásico y bien documentado; las correcciones estándar son
la varianza modificada de Hamed & Rao (1998), el *pre-whitening* (von Storch, 1995) y, para
estacionalidad, el **Seasonal Mann-Kendall** de Hirsch, Slack & Smith (1982), que calcula S por
mes y los suma.
→ Implementar cualquiera de esas es **agregar una prueba nueva al motor**, con su propia entrada
en `formulas-etapa1.md`, su propia fuente bibliográfica y su propia regresión. No es un ajuste.

**Atípicos (Chow / Grubbs-Beck).**
La prueba supone una muestra i.i.d. log-normal, y el Bulletin 17B la define **específicamente
para series de picos anuales**. Sobre una serie diaria, cada crecida es un "atípico": el test
marcaría cientos de puntos. Además rompe la UX del pipeline, que pausa el stream esperando una
decisión del usuario **por un atípico**, no por trescientos.

### 4.2 Etapa 2 — se rompe el marco completo, no una fórmula

**El período de retorno cambia de unidad, en silencio.**
`empirical.py` usa Weibull, `T = (n+1)/m`. Ese T está **en unidades del intervalo de muestreo**.
Con máximos anuales, T = 100 significa 100 años. Con una serie diaria, T = 100 significa
**100 días**. El número que el sistema calcula seguiría siendo aritméticamente correcto y el
rótulo de la interfaz seguiría diciendo "años" — es el modo de falla más peligroso posible:
un resultado plausible, bien formateado y equivocado por un factor de 365.

**Las 13 distribuciones dejan de ser un modelo de valores extremos.**
El teorema de Fisher–Tippett–Gnedenko justifica ajustar GVE/Gumbel a **máximos de bloque**.
Ajustar Gumbel a una serie diaria cruda no es análisis de frecuencia de extremos: es ajustar una
distribución a la curva de duración de caudales completa, donde dominan los caudales bajos.
El ranking por EEA se calcularía igual y sería igual de intrascendente.

**El marco que sí existe para esto es otro: series de duración parcial / POT.**
Analizar eventos sub-anuales tiene una teoría propia y madura —*peaks-over-threshold*, con
Poisson-GPD, criterios de independencia entre picos, selección de umbral, y la relación de
Langbein para convertir el T de la serie parcial al T anual—, y **no es la teoría de la tesis
de Facundo**. Referencias de entrada: Langbein (1949), Cunnane (1973), Coles (2001).

→ Implementar el camino B *bien* significa construir un **segundo motor de Etapa 2** con su
propio marco teórico, sus propias fórmulas, su propia bibliografía y su propia auditoría de
regresión. Eso no es una feature: es la mitad de otro proyecto integrador.

---

## 5. Riesgo académico

Este es, en mi lectura, el argumento decisivo — más que el volumen de trabajo.

METIS se defiende ante un tribunal de ISI, pero su núcleo estadístico se audita contra la tesis
de Facundo. Todo el aparato de trazabilidad del proyecto —`formulas-etapa1.md`,
`formulas-etapa2.md`, la regla de que ninguna fórmula se implementa sin referencia explícita,
las 9 estaciones de regresión, `pendientes-facundo.md`— está construido sobre **una** fuente
primaria, que trabaja con **series anuales de máximos**.

- El **camino A no toca nada de eso**. Amplía el formato de entrada y deja el motor intacto.
  Se defiende en una frase: *"METIS analiza series de máximos anuales; acepta el registro en
  la resolución en que existe y construye la serie de máximos con una regla explícita, auditable
  y configurable."*
- El **camino B rompe la trazabilidad**: cada prueba de Etapa 1 necesitaría una variante
  documentada con fuente propia, y Etapa 2 necesitaría un marco teórico que la tesis no cubre.
  Ante una pregunta del tribunal del tipo *"¿por qué corren Mann-Kendall sobre datos
  autocorrelacionados?"* no hay respuesta buena.

Hay además un tercer camino, **el peor de todos y el más fácil de tomar por inercia**:
habilitar la entrada diaria/mensual sin agregar y sin advertir. El sistema devolvería
resultados con la forma correcta y sin sentido — exactamente el bug F2.1, ahora como feature
declarada. **Eso sí sería un hallazgo grave en la defensa.**

---

## 6. Preguntas para Facundo (bloquean el camino A, no lo invalidan)

Se sugiere agregarlas a `docs/auditoria/pendientes/pendientes-facundo.md`:

1. **Umbral de completitud para agregar un año desde datos diarios.** ¿Se exige el 100 % de
   los días (365/366), o hay un umbral (≥ 90 %, ≥ 95 %, "sin huecos en la temporada húmeda")?
   *Agrupar con la pregunta ya abierta de hueco interior en mensual — es la misma a otra escala.*
2. **¿Se acepta encadenar la agregación (diaria → mensual → anual) o siempre diaria → anual
   directo?** Cambia el resultado cuando hay meses parcialmente faltantes.
3. **¿El máximo diario del registro es el máximo del evento?** Un limnígrafo diario suele
   reportar media diaria, no pico instantáneo. Si la tesis trabaja con picos instantáneos,
   agregar desde medias diarias **subestima sistemáticamente** la serie de máximos anuales.
   Esta es la pregunta hidrológica más importante de todo el informe y no tiene solución
   en software: hay que saber qué variable trae el archivo. Puede requerir un campo nuevo
   en la configuración del análisis.
4. **¿Qué hacer si `tipo_variable == "otro"` con resolución diaria?** Ya está abierta para
   mensual; la respuesta debería ser la misma.

---

## 7. Recomendación

1. **Hacer el camino A para diaria.** Barato, aditivo, sin riesgo de regresión, y refuerza la
   propuesta de valor original (automatizar un paso que hoy es manual en Excel). Cerrar antes
   la pregunta 1 y 3 de la sección 6, y resolver a propósito la decisión de payload (3.3).
2. **No hacer el camino B, y documentar por qué.** Escribir una decisión numerada que declare
   explícitamente que *el dominio de análisis de METIS es la serie de máximos anuales,
   cualquiera sea la resolución de entrada*, con las razones de la sección 4 y sus referencias.
   **Una decisión bien argumentada de no implementar vale más ante el tribunal que una
   implementación a medias** — y convierte una posible pregunta incómoda en una fortaleza
   demostrada del proceso de diseño.
3. **Si queda tiempo y se quiere valor visible del dato sub-anual**, la extensión segura es
   **descriptiva, no inferencial**: boxplot mensual y curva de duración a partir del registro
   diario. No toca ninguna prueba de hipótesis, no toca Etapa 2, no requiere fórmula nueva de
   la tesis. Es la única forma de "mostrar la serie diaria" sin comprometer nada.

---

## Anexo — verificaciones hechas para este informe

| Afirmación | Cómo se verificó |
|---|---|
| Diaria hoy bloquea con `CONTRACT_NO_TEMPORAL_RESOLUTION` | Ejecutada la lógica de `_inferir_resolucion()` sobre `docs/series prueba/serie_diaria_40anios.csv` → `moda_dias = 1` → `None` |
| Payload diario ≈ 637 KB | Serializado a JSON el bloque `datos` con el fixture real (14.600 ítems), mismos supuestos de DECISIÓN 058 |
| ~~El fixture diario no tiene bisiestos~~ **FALSA — corregida 28/08/2026** | El conteo original estaba mal leído. Re-verificado: 10 años con 366 días (1980, 1984, ..., 2016), 29 con 365, y 2019 con 355 (el archivo termina el 2019-12-21). Con criterio estricto el fixture da 39 años completos + 2019 recortado como `extremo_fin`, no un rechazo total. Ver §4.1 y `plan-resolucion-diaria.md` §R0.1 |
| Mensual ya agrega por el camino A | `pipeline_etapa1.py:153-158`, `aggregation.py`, DECISIÓN 057 |
| El límite de 10 MB ya contempla diaria | DECISIÓN 050, tabla de casos medidos |
| F2.1 era el bug de correr la batería sobre mensual crudo | DECISIÓN 057, sección "Contexto", punto 1 (citado textual en 4.0) |

**Advertencia de rigor:** las referencias bibliográficas de la sección 4 (Hamed & Rao 1998;
Hirsch, Slack & Smith 1982; von Storch 1995; Langbein 1949; Cunnane 1973; Coles 2001) provienen
del conocimiento general del área y **no fueron verificadas contra los originales en esta
sesión**. Antes de que cualquiera de ellas entre a `formulas-etapa1.md`, a una decisión numerada
o al documento de tesis, hay que chequearlas contra la fuente, siguiendo la regla del proyecto
de no aceptar afirmaciones sin verificación cruzada.
