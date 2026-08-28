# Pipeline Estadístico — Lógica de Negocio

## IMPORTANTE: Esta lógica vive en core/ — no en api/ ni services/

El motor estadístico no sabe que existe HTTP. Recibe datos Python, devuelve resultados Python.
Services/ orquesta el pipeline y emite eventos SSE. Core/ solo calcula.

---

## Etapa 1 — Pipeline de validación estadística

### Orden de ejecución (fijo, no configurable)

```
0a. Orden cronológico (Bloque H3)          ← sobre timestamps crudos, bloqueante, antes de TODO lo demás
0. Agregación temporal (Bloque F4 / DEC 065)  ← solo si resolucion_temporal ∈ {"mensual","diaria"}, antes del contrato
1. Validación del contrato de datos        ← primera barrera, puede ser bloqueante
2. Estadística descriptiva                 ← automática, siempre, antes de cualquier prueba
3. Independencia: Anderson + Wald-Wolfowitz
4. Homogeneidad: Helmert + t de Student + Cramer
5. Tendencia: Mann-Kendall + Kolmogorov-Smirnov
6. Atípicos: Chow                          ← pausa para decisión del usuario en CU-01/CU-02
```

**α = 5% fijo en toda la V1.0. No es configurable.**

### Paso 0a — Orden cronológico (DECISIÓN 030, Bloque H3 del plan post-avance)

Segunda excepción real a "detecta y advierte, no bloquea" (la primera es
`CONTRACT_SERIES_TOO_SHORT`). `ejecutar_etapa1()` evalúa
`core/validacion/contract.py::timestamps_desordenados(timestamps)` sobre
los timestamps **crudos**, antes de cualquier otra cosa — incluida la
agregación mensual del paso 0. Si están desordenados, bloquea con
`CONTRACT_WRONG_ORDER` (`nivel_confianza="rechazado"`, mismo tratamiento
que `CONTRACT_SERIES_TOO_SHORT`) sin llegar a tocar `validar_contrato()` ni
`agregar_a_maximos_anuales()`. `timestamps=None` no evalúa nada (CU-03 sin
columna de fecha, por ejemplo).

**Por qué tiene que evaluarse ANTES del paso 0, no después:**
`agregar_a_maximos_anuales()` construye sus propios timestamps con
`range(periodo_inicio, periodo_fin + 1)` — siempre ascendentes por
construcción. Evaluar el orden sobre esa salida (como hacía
`validar_contrato()` antes de este bloque) es código muerto para
*cualquier* serie mensual: nunca puede detectar nada. Peor: esa misma
función toma `timestamps[0]`/`timestamps[-1]` como el dato más
antiguo/reciente del registro para fijar qué períodos agregar — con un
archivo desordenado puede **excluir períodos reales del registro en
silencio**, sin warning ni error. Verificado antes de implementar: 3 años
completos (36 meses reales) con dos bloques anuales invertidos entre sí
agregaban solo 2 años, con `periodos_descartados=[]` — el tercer año
desaparecía sin ningún rastro. `tests/unit/core/pipeline/test_pipeline_etapa1.py`
tiene el test que reproduce exactamente este caso.

Verificado, antes de volver esto bloqueante, que ninguna de las 9 series
de referencia de la auditoría (Fase 4,
`docs/auditoria/regresion/regresion-unitaria/`) tiene desorden cronológico
— este cambio no invalida ningún resultado ya auditado y cerrado. Ver
`docs/decisiones/decision030.md`.

**Datos faltantes NO son desorden.** Un valor `None`/vacío en una fecha
presente y en orden sigue su tratamiento actual
(`CONTRACT_MISSING_VALUES`, warning no bloqueante) — la distinción es
exclusivamente sobre el orden temporal, no sobre la completitud.

### Paso 0 — Agregación temporal (DECISIÓN 057 mensual, DECISIÓN 065 diaria)

Si `resolucion_temporal in ("mensual", "diaria")`, `ejecutar_etapa1()` llama
a `core/validacion/aggregation.py::agregar_a_maximos_anuales(serie,
timestamps, mes_inicio_anio, resolucion=resolucion_temporal,
cobertura_minima_interior=COBERTURA_MINIMA_INTERIOR[resolucion_temporal])`
**antes** de `validar_contrato()` — no en `services/`. El resto del pipeline
(contrato, las seis pruebas, Chow, Etapa 2) corre sobre la serie de máximos
anuales ya agregada, exactamente como si el usuario hubiera subido una serie
anual — `resolucion_temporal` se fuerza a `"anual"` internamente después de
agregar. Con carga diaria el camino es **directo** diaria→anual (no
encadenado diaria→mensual→anual) — ver DECISIÓN 065, punto 1.

`mes_inicio_anio ∈ [1..12]` (default `7`, `POST /analysis/stream`) define el
mes de inicio del año — el año calendario es el caso `mes_inicio_anio = 1`,
no un modo aparte (ver `constraints.md`, sección "Año hidrológico —
configurable, no una constante"). La unidad de completitud de un año es de
12 meses (`resolucion="mensual"`) o 365/366 días (`resolucion="diaria"`,
bisiestos y el febrero del año siguiente resueltos por `pd.date_range`).

**Recorte de extremos, hueco interior y cobertura asimétrica:** las
unidades parciales en los dos extremos del registro se descartan (warning
`CONTRACT_PARTIAL_YEARS_TRIMMED`, no bloqueante) — los extremos **siempre**
exigen 100 %. Un año **interior** incompleto se descarta con
`CONTRACT_INCOMPLETE_YEARS_DISCARDED` si su cobertura no alcanza
`cobertura_minima_interior`; si la alcanza pero está por debajo del 100 %,
se acepta y se emite `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` (nivel normal,
DECISIÓN 065 R2.3) con cuántas unidades faltaron. Valor provisorio
`cobertura_minima_interior = 1.0` (estricto) mientras R0.1 espera a Facundo
— con `1.0`, `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` no se emite todavía y el
comportamiento es idéntico al mensual pre-DECISIÓN 065. El recorte ocurre
**antes** del conteo de la regla de n: un registro que queda con menos de
10 años agregados bloquea con `CONTRACT_SERIES_TOO_SHORT`, igual que
cualquier otra serie corta.

**`Etapa1Result.serie_efectiva`/`timestamps_efectivos`** — la serie y los
timestamps sobre los que la batería estadística realmente corrió: iguales a
la entrada si no hubo agregación, o los máximos anuales si la hubo.
`services/analysis_service.py` usa estos campos (no `serie_original`, la
serie cruda subida) para todo lo que corre después de Etapa 1 — el mapeo del
índice de Chow cuando el usuario rechaza un atípico, y la entrada de Etapa 2.
Sin esto, rechazar un atípico sobre una serie mensual agregada habría
mapeado el índice contra la serie mensual cruda (mucho más larga) y borrado
un dato mensual sin relación con el atípico real — bug real encontrado al
escribir esta parte del Bloque F, cubierto por
`tests/integration/test_stream_agregacion_mensual.py`.

### Contrato de datos — validaciones en orden

```python
# BLOQUEANTE — evaluado antes que cualquier otra cosa, incluida la
# agregación mensual (paso 0a, sobre timestamps crudos — ver arriba)
if timestamps is not None and timestamps_desordenados(timestamps):
    emit("contract_error", {"codigo": "CONTRACT_WRONG_ORDER"})
    return

# BLOQUEANTE — detiene el pipeline completamente (validar_contrato(), post-agregación)
if len(serie) < 10:
    emit("contract_error", {"codigo": "CONTRACT_SERIES_TOO_SHORT", "datos": len(serie), "minimo": 10})
    return  # nada más se ejecuta

if resolución_temporal is None:
    emit("contract_error", {"codigo": "CONTRACT_NO_TEMPORAL_RESOLUTION"})
    return

# NO BLOQUEANTES — el pipeline continúa con warning
if len(serie) < 30:
    emit("contract_warning", {"codigo": "CONTRACT_LENGTH_WARNING", "datos": len(serie)})

if tipo_variable == "caudal_precipitacion" and any(v < 0 for v in serie):
    emit("contract_warning", {"codigo": "CONTRACT_NEGATIVE_VALUES"})

# ... resto de validaciones (faltantes, duplicados, espaciado, no numéricos)
```

### Pruebas de independencia

**Anderson (principal)**
- Calcula coeficiente de autocorrelación serial para k = 1, 2, ..., n/3
- Valor crítico: fórmula analítica de la tesis de Facundo (no tabla)
- Si Anderson acepta → serie es independiente aunque Wald-Wolfowitz rechace
- Produce correlograma como output gráfico

**Wald-Wolfowitz (verificación)**
- Para n > 40: valor crítico de distribución normal estándar (Z = ±1.96 para α=5%)
- Para n ≤ 40: ejecutar CON advertencia explícita `TEST_WARNING_SMALL_SAMPLE` — no omitir
- Si Anderson acepta y Wald-Wolfowitz rechaza: resultado = INDEPENDIENTE con nota de Wald

**Jerarquía:** Anderson manda. Wald-Wolfowitz es verificación, no co-decisor.

### Pruebas de homogeneidad

**Helmert**
- Resultado directo, sin tabla

**t de Student**
- Tabla con ν = n₁ + n₂ − 2 grados de libertad, α = 5%

**Cramer (principal de homogeneidad)**
- Distribución t de Student
- El resultado SIEMPRE incluye n₁ y n₂ empleados en la partición
- Partición configurable: default = últimos 60% y últimos 30%
- CU-01/CU-02: usuario configura partición desde la interfaz
- CU-03: partición viene de configuración del client_id

**Niveles de homogeneidad:**
```
homogeneidad_ok       → todas aprobaron
homogeneidad_warning  → Cramer aprobó pero Helmert o t de Student rechazaron
homogeneidad_critica  → Cramer rechazó → WARNING CRÍTICO
```

### Pruebas de tendencia

**Mann-Kendall**
- n > 10: fórmula analítica A.55 del apéndice de Carlos
- n ≤ 10: Tabla A.4

**Kolmogorov-Smirnov (tendencia)**
- Z_crit = 1.358 para α = 0.05 (Tabla A.5)

### Detección de atípicos: Chow

- Aplica sobre **logaritmos** de la serie — CRÍTICO
- Si hay ceros en caudal_precipitacion: marcar como `TEST_NOT_EXECUTED_ZEROS`, continuar
- Fuente primaria: Grubbs-Beck / Bulletin 17B — DECISIÓN 018 (docs/decisiones/decision018.md),
  provisorio. Escalante Sandoval & Reyes Chávez (2005) citado previamente
  acá pero con fórmula distinta no verificada — pendiente confirmación.
- Chow **nunca** genera warning Crítico — siempre es warning normal
- Si detecta atípico: emitir `TEST_WARNING_OUTLIER_DETECTED` y pausar stream
  - CU-01/CU-02: esperar decisión del usuario via POST /analysis/outlier-decision
  - CU-03: registrar warning y continuar automáticamente (sin pausa)

### Distribuciones deshabilitadas ante ceros en caudal_precipitacion

```python
DISABLED_WITH_ZEROS = [
    "log_normal_2p",
    "log_pearson_3",
    "gamma_2p",
    "exponencial_beta",
    # "chow" ya manejado arriba
]
# Pendiente confirmar con Facundo: gamma_3p, exponencial_x0_beta,
# generalizada_pareto, log_normal_3p, generalizada_exponencial
```

### Niveles de warning

```
CRÍTICO:
  - Anderson rechaza independencia
  - Cramer rechaza homogeneidad (homogeneidad_critica)

NORMAL:
  - Tendencia detectada (Mann-Kendall o KS)
  - Chow detecta atípico
  - Wald-Wolfowitz rechaza
  - Helmert o t de Student rechazan
  - Cualquier problema del contrato no bloqueante
  - Wald-Wolfowitz con n ≤ 40
```

---

## Estado de confianza global del resultado

```python
# Se determina al finalizar el pipeline completo
if len(serie) < 10 or serie_vacía:
    nivel = "rechazado"        # único estado que detiene el pipeline
elif any(warning.nivel == "critico" for warning in warnings):
    nivel = "con_warnings"     # advertencia prominente en UI
elif len(warnings) > 0:
    nivel = "con_warnings"     # advertencia estándar
else:
    nivel = "validado"
```

---

## Eventos SSE del stream — estructura

Todos los eventos siguen este esquema:

```python
# Formato de cada evento SSE
f"event: {tipo}\ndata: {json.dumps(payload)}\n\n"

# Tipos de eventos:
"contract_error"          # bloqueante, stream termina
"contract_warning"        # no bloqueante, stream continúa
"descriptive_stats"       # estadística descriptiva calculada
"progress"                # avance del pipeline
"test_result"             # resultado de una prueba individual
"outlier_detected"        # pausa para decisión del usuario (CU-01/CU-02)
"result_etapa1"           # resultados completos de Etapa 1
"result_etapa2_ranking"   # ranking EEA completo (pausa para selección de distribución+método)
"result_etapa2_eventos"   # eventos de diseño de la distribución elegida
"complete"                # pipeline terminado
"error"                   # error interno inesperado
```

Payload mínimo de `progress`:
```json
{"paso": "anderson", "etapa": 1, "completado": 2, "total": 8}
```

Payload de `test_result`:
```json
{
  "prueba": "anderson",
  "estadistico": 0.23,
  "valor_critico": 0.37,
  "veredicto": "aprobada",
  "warning_codigo": null,
  "warning_nivel": null,
  "n1": null,
  "n2": null,
  "indice_atipico": null
}
```
`indice_atipico` agregado en el PR 3 del plan de cierre de pendientes
no-test (DECISIÓN 058), en paralelo con `test_result_dict()` — mismo campo
que ya existía en `TestResult`, nunca se serializaba en ninguno de los dos
caminos.

**Bloque D del plan post-avance (DECISIÓN 064) no toca este evento.** El
campo nuevo `explicacion` (ver más abajo, payload de `result_etapa1`) solo
se serializa en `test_result_dict()` — el evento `test_result` de arriba
alimenta el timeline transitorio de `StreamPage` (una tabla compacta,
idéntica en los dos modos mientras el stream corre), no `Etapa1ResultView`
— ahí no hay nada que renderizar de forma distinta según paso a paso vs.
experto todavía, así que agregarlo acá sería payload sin consumidor.

**Payload de `result_etapa1`** — agregado el bloque `datos` en el PR 3 del
plan de cierre de pendientes no-test (DECISIÓN 058). Antes de este PR el
evento llevaba `contract`/`descriptive`/las cuatro baterías de pruebas/los
niveles/`warnings` (ver `_serializar_etapa1()` en
`services/analysis_service.py`) pero nunca la serie en sí — el bloqueo real
detrás de FE-16. `analysis_results.etapa1` persiste exactamente el mismo
payload para CU-01.

```json
{
  "contract": { "...": "..." },
  "descriptive": { "...": "..." },
  "independencia": [
    {
      "...": "...",
      "indice_atipico": null,
      "explicacion": {
        "ecuacion": "III-1",
        "terminos": {"n": 40, "k": 1, "media": 42.5, "numerador": 3120.4, "denominador": 18904.2, "k_max": 14, "lags_fuera": 1, "tolerancia": 2}
      }
    }
  ],
  "homogeneidad": [ "..." ],
  "tendencia": [ "..." ],
  "atipicos": [ { "...": "...", "indice_atipico": 17 } ],
  "nivel_independencia": "independiente",
  "nivel_homogeneidad": "homogeneidad_ok",
  "nivel_confianza": "con_warnings",
  "warnings": [ "..." ],
  "datos": {
    "resolucion_original": "mensual",
    "resolucion_serie_original": "mensual",
    "serie_efectiva": [94.71, 89.83],
    "timestamps_efectivos": [{"iso": "1980-01-01", "anio": 1980}],
    "serie_original": [12.1, 15.7],
    "timestamps_originales": [{"iso": "1980-01-01", "anio": 1980}],
    "indice_atipico": 17,
    "serie_calendario": null
  }
}
```

**`datos.resolucion_serie_original`** (`"anual" | "mensual" | "diaria" |
null`) — agregado en DECISIÓN 065 (punto 3): a qué resolución está
`datos.serie_original` en **este** payload, distinto de `resolucion_original`
(la del archivo subido). Con carga diaria el backend **no** serializa la
serie diaria cruda (~14.600 ítems, ~637 KB — contradecía el
dimensionamiento de DECISIÓN 058); serializa la agregación a máximos
mensuales (`agregar_a_maximos_mensuales()`, ~480 ítems), así que
`resolucion_serie_original == "mensual"` aunque `resolucion_original ==
"diaria"`. `Etapa1Result.serie_original` no se toca — sigue siendo la diaria
cruda que alimenta `_calcular_serie_calendario()`. El frontend usa este
campo para rotular el boxplot mensual ("máximos mensuales agregados desde
datos diarios" vs. "valores mensuales del registro").

Cada `TestResult` (en `independencia`/`homogeneidad`/`tendencia`/`atipicos`)
gana `indice_atipico` — ya existía en `core/types.py::TestResult`, nunca se
serializaba. Distinto de `datos.indice_atipico`: éste último ya viene
mapeado a posición en `datos.serie_efectiva` (`_extraer_indice_atipico()`,
que en la práctica coincide con el índice crudo de Chow porque
`valores_numericos` ES `serie_efectiva` dentro de `ejecutar_etapa1()` — ver
DECISIÓN 058 §5), mientras que el de cada `TestResult` individual es el que
calculó la prueba en su propio espacio, sin traducir.

`datos.serie_original`/`datos.timestamps_originales` solo viajan si
`resolucion_original in ("mensual", "diaria")` — con carga anual son
idénticos a los `_efectiva`, duplicarlos es peso muerto. Con carga diaria
son la agregación a máximos mensuales, no la diaria cruda (DECISIÓN 065,
punto 3 — ver `resolucion_serie_original` arriba). `datos.serie_calendario`
se puebla con carga mensual **o diaria** y `mes_inicio_anio != 1` — con
carga diaria se calcula por el camino directo diaria→anual con `mes_inicio=1`
(`_calcular_serie_calendario()` pasa `resolucion=` explícito; sin eso
correría en modo mensual sobre datos diarios y devolvería el máximo de los
últimos días de cada mes, silencioso y mal). Ver DECISIÓN 058 §§1-3 para la
partición completa (qué vive en `analyses` vs. en `analysis_results.etapa1`)
y el cálculo de tamaño de payload.

**`explicacion` — agregado en el Bloque D del plan post-avance (DECISIÓN
064).** Cada `TestResult` de las 8 pruebas de Etapa 1 (Anderson,
Wald-Wolfowitz, Helmert, t de Student, Cramer, Mann-Kendall,
Kolmogorov-Smirnov, Chow) gana `explicacion: {ecuacion, terminos} | null` —
`null` en cualquier prueba con `veredicto == "no_ejecutada"` (nada que
sustituir). `terminos` son los valores intermedios que la prueba ya calculó
de todos modos (`core/etapa1/*.py`), no una segunda fuente de verdad
matemática: el frontend en modo paso a paso (`Etapa1ResultView`, Bloque D3)
solo renderiza — sustituye `terminos` en una plantilla y arma una
interpretación en castellano — nunca recalcula ni deriva un estadístico
nuevo. `ecuacion` referencia `.claude/rules/core/formulas-etapa1.md` (ej.
`"III-8"`), o, para Chow, la fuente real de su valor crítico (Bulletin 17B,
no un número de ecuación de la tesis — DECISIÓN 018). Cramer es la única
prueba donde `terminos` lleva más datos que `estadistico`/`valor_critico`
por sí solos explican: los dos bloques (60%/30%, `t_w1`/`t_w2`) viajan
siempre, no solo el "binding" que `calcular_cramer()` ya reportaba — el
docente necesita ver por qué `aprobada` exige que los dos aprueben, no solo
el reportado. `analysis_results.etapa1` persiste el mismo payload para
CU-01 — `explicacion` llega igual al historial.

---

## Secuencia real del stream con Etapa 2 (DECISIÓN 052, cerrado 09/08/2026)

Implementada de punta a punta en `services/analysis_service.py::stream_analysis()`
— Bloque A del plan de implementación de Etapa 2. Simétrica con la pausa de
Chow, mismo mecanismo (`session_store`), sin transporte nuevo:

```
… → result_etapa1 → progress(etapa 2) → result_etapa2_ranking → [PAUSA] → result_etapa2_eventos → complete
                                                  ↑
                        POST /analysis/distribution-decision → session_store.resolve_session()
```

**Condiciones para entrar a Etapa 2**, evaluadas en este orden:

1. `etapas == [1, 2]` (parseado y validado en el borde del endpoint —
   DECISIÓN 054). Con `etapas == [1]` el stream termina en `result_etapa1` →
   `complete`, exactamente como si Etapa 2 no existiera.
2. `result_final.nivel_confianza != "rechazado"` — el único estado que
   bloquea. Con warnings, incluso críticos, Etapa 2 corre igual
   (RF-GEN-P-03).

Etapa 2 corre sobre la misma serie que produjo el veredicto final de
Etapa 1 — si el atípico de Chow fue rechazado, sobre la serie ya filtrada,
no sobre la original.

**Payload de `result_etapa2_ranking`:** `{"session_id", "ranking", "warnings",
"puntos_empiricos", "seleccion"}`, donde `ranking` es la grilla completa
serializada por `_serializar_etapa2()` (las 13 distribuciones, todos sus
métodos con `status`/`eea`/`parametros`, `mejor_eea`, `mejor_metodo`) — sin
aplanar a un top-3, ver DECISIÓN 055. **`puntos_empiricos`** — agregado en el
Bloque C del plan de Etapa 2 (gráficos interactivos, DECISIÓN 056) — es la
posición de ploteo Weibull de cada dato observado (`{valor, periodo_retorno,
probabilidad}`, `core/etapa2/types.py::PuntoEmpirico`,
`core/etapa2/empirical.py::probabilidades_weibull`): propiedad de la muestra,
no del ajuste, así que viaja antes de que el usuario elija ninguna
distribución. Insumo del gráfico de ajuste (`Etapa2AjusteChart`).
**`seleccion`** — agregado en el Bloque C2a del plan post-avance
(14/08/2026) — siempre `null` en este evento en particular: se emite
**antes** de que exista ninguna elección, el campo solo se puebla en lo que
queda persistido (`analysis_results.etapa2`, ver `api-contracts.md` §
`GET /history/{id}`), no en este evento transitorio.

**`POST /analysis/distribution-decision`** (reemplaza al `design-events`
documentado y nunca implementado — DECISIÓN 052, ver `api-contracts.md`)
resuelve la pausa con `{distribucion, metodo, periodos_retorno}`.

**Payload de `result_etapa2_eventos`:**
```json
{
  "distribucion": "gumbel",
  "metodo": "momentos",
  "eventos_diseno": [
    {"periodo_retorno": 2, "valor": 138.4},
    {"periodo_retorno": 100, "valor": 312.7}
  ],
  "curva_ajuste": [
    {"periodo_retorno": 1.05, "valor": 61.2},
    {"periodo_retorno": 1.11, "valor": 68.9}
  ]
}
```
`valor` puede ser `null` para un período de retorno puntual si `cuantil()`
falla para esa distribución+método — no tumba el resto de los eventos
(`core/etapa2/design_events.py`, DECISIÓN mencionada arriba).

**`curva_ajuste`** — agregado en el Bloque C (gráficos interactivos,
DECISIÓN 056). No son los `periodos_retorno` que pidió el usuario: es un
muestreo denso de 60 puntos en escala logarítmica, entre T=1.05 y el mayor
valor entre el T pedido por el usuario y el T empírico máximo de la muestra
— para que la curva del gráfico de ajuste cubra el mismo rango que los
`puntos_empiricos`. Se calcula con la misma función que `eventos_diseno`
(`calcular_eventos_diseno()`), solo que con un `periodos_retorno` distinto —
no hay lógica de curva nueva en `core/`. No se persiste: a diferencia de
`puntos_empiricos` (parte de `Etapa2Result`, persistido en
`analysis_results.etapa2`), `curva_ajuste` depende de la distribución+método
elegidos y solo viaja por el evento transitorio — el gráfico de ajuste y el
de eventos de diseño solo están disponibles durante la sesión interactiva
(`StreamPage`, y de ahí a `ResultsPage` vía router state), no en
`HistoryDetailPage`.

**Implementación técnica no obvia:** el mismo `asyncio.Event` de
`SessionState` (DECISIÓN 053) se reutiliza para las dos pausas posibles de
una misma sesión (Chow y luego distribución) — un `Event` no se
"des-setea" solo tras `.set()`, así que `stream_analysis()` lo limpia
(`.clear()`) antes de la segunda espera. Sin esto, la segunda pausa
devolvería de inmediato sin esperar la decisión real si Chow ya se
resolvió antes en el mismo stream.

---

## Etapa 2 — Motor de análisis de frecuencia

### Solo se ejecuta si Etapa 1 fue completada primero — siempre

### 13 distribuciones con hasta 6 métodos de estimación

El ajuste es **automático y exhaustivo** — sin intervención del usuario.

| Distribución | Métodos aplicables |
|---|---|
| Uniforme | Momentos, MV |
| Normal | Momentos, MV, ML |
| Gumbel | Momentos, MV, ML, ME |
| GVE | Momentos, MV, ML |
| Log-Normal 2p | Momentos, MV |
| Log-Normal 3p | Momentos, MV |
| Log-Pearson III | Momentos (directo e indirecto), MV |
| Gamma 2p | Momentos, MV, ML |
| Gamma 3p | Momentos, MV |
| Exponencial (β) | Momentos, MV |
| Exponencial (x₀, β) | Momentos, MV |
| Generalizada de Pareto | Momentos, MV, MC |
| Generalizada Exponencial | Momentos, MV, ML |

> **Nota sobre Pearson III:** no existe como distribución independiente en la tesis
> de Facundo — no tiene sección propia ni fórmulas propias. La distribución Gamma 3p
> (β, α, x₀) es matemáticamente equivalente a Pearson III en escala original.
> Log-Pearson III aplica la misma lógica sobre yi = ln(xi).
> Fuente: confirmado por Octavio — Tesis Facundo Cap. IV.

> **Nota sobre métodos ME y MC:** ME = Máxima Entropía, MC = Mínimos Cuadrados.
> Confirmados solo para las distribuciones donde aparecen en la tabla.
> Pendiente confirmar con Facundo si aplican a otras distribuciones.
> Fuente: formulas-etapa2.md — Gumbel IV-190/IV-198, Gen. Pareto IV-153/IV-155.

**GVE con Momentos-L:** usar aproximación de Hosking (1985) para estimar κ (IV-234 a IV-242).

### Casos especiales de Etapa 2

```python
"no_converge"    # método iterativo no encontró solución estable → registrar, continuar
"no_aplicable"   # combinación sin sentido matemático para esos datos → registrar, continuar
"high_eea"       # EEA > 5% de la media → warning DIST_HIGH_EEA
"disabled_zeros" # distribución deshabilitada por ceros → registrar, continuar
```

**Ningún caso especial detiene el pipeline de Etapa 2.**

### Criterio de rankeo: EEA (Error Estándar de Ajuste)

- Menor EEA → mejor ajuste → posición 1 en el ranking
- **METIS no sugiere ganadora** — presenta el ranking y el usuario decide
- Fórmula de Weibull para períodos de retorno empíricos: T = (n+1)/m

### Selección de distribución

- CU-01 y CU-02: el usuario selecciona manualmente desde la tabla rankeada
- CU-03: selección automática por EEA (la de menor EEA)
- Después de la selección → calcular eventos de diseño via POST /analysis/design-events

### Año hidrológico

Todo gráfico con eje temporal produce **dos versiones**:
- Año calendario: 1 enero → 31 diciembre
- Año hidrológico: 1 julio → 30 junio del año siguiente

Ambas versiones son **obligatorias**, no opcionales. Aplica a: gráfico de Chow, gráfico de ajuste, gráfico de eventos de diseño, serie temporal, boxplot mensual.
