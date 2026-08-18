# Contratos de API y Catálogo de Errores

## Estructura de error estándar — todos los endpoints

```json
{
  "error": {
    "codigo": "CODIGO_ESTANDARIZADO",
    "mensaje": "Descripción legible para el usuario",
    "detalle": {}
  }
}
```

| HTTP | Cuándo |
|------|--------|
| 400 | Contrato de datos inválido |
| 401 | Sin auth donde se requiere |
| 403 | Auth válida pero sin acceso (mail no es @ucc.edu.ar) |
| 404 | Recurso no encontrado |
| 422 | Validación Pydantic fallida — FastAPI lo lanza automáticamente |
| 500 | Error interno inesperado |

Para SSE: los errores son eventos `error`, no respuestas HTTP de error.

---

## Contratos por endpoint

### POST /api/v1/auth/register

**Request:** `{"email": "legajo@ucc.edu.ar", "password": "...", "nombre": "..."}`
**Validaciones:** email debe terminar en @ucc.edu.ar, password mínimo 8 caracteres
**Auth:** Sin auth
**Response 201:** `{"ok": true, "mensaje": "Cuenta creada. Revisá tu mail para verificar la dirección."}`
**Errores:** 400 AUTH_EMAIL_ALREADY_REGISTERED, 422 validación Pydantic, 500 AUTH_VERIFICATION_EMAIL_FAILED

---

### POST /api/v1/auth/verify

**Request:** `{"token": "..."}`
**Auth:** Sin auth
**Response 200:** `{"ok": true}`
**Errores:** 400 AUTH_INVALID_TOKEN, 404 AUTH_USER_NOT_FOUND

---

### POST /api/v1/auth/login

**Request:** `{"email": "...", "password": "..."}`
**Auth:** Sin auth
**Response 200:** `{"ok": true}` + HttpOnly Cookie `access_token`
**Errores:** 401 AUTH_INVALID_CREDENTIALS, 403 AUTH_EMAIL_NOT_VERIFIED

---

### POST /api/v1/auth/logout

**Auth:** Sin auth (borra la cookie aunque no haya sesión activa)
**Response 200:** `{"ok": true}` + borra Cookie `access_token`

---

### GET /api/v1/auth/me

**Auth:** JWT en HttpOnly Cookie (requerido)
**Response 200:** `{"id": "uuid", "email": "...", "nombre": "...", "email_verified": true}`
**Errores:** 401 sin auth

---

### POST /api/v1/analysis/stream

**Request (multipart/form-data):**
```json
{
  "archivo": "<file CSV o Excel>",
  "columna_x": "nombre_o_indice",
  "columna_y": "nombre_o_indice",
  "tipo_variable": "caudal_precipitacion | otro",
  "etapas": [1] | [1, 2],
  "modo": "paso_a_paso | experto",
  "cramer_particion": "default | {n1_pct: 60, n2_pct: 30}",
  "mes_inicio_anio": 1 | 2 | ... | 12
}
```

**Auth:** JWT en HttpOnly Cookie (opcional — sin JWT = CU-02, con JWT = CU-01)

**Response:** `text/event-stream`

**Comportamiento según JWT:**
- Con JWT válido (@ucc.edu.ar): persiste análisis, habilita exportación
- Sin JWT: sesión efímera, sin persistencia

**Nota de implementación — `cramer_particion` personalizada no implementada.**
El contrato de arriba documenta `{n1_pct, n2_pct}` como valor válido, pero el
endpoint real (`api/v1/analysis.py`) declara el campo como `Form(str)`.
**Corrección 05/08/2026 (DECISIÓN 036, Bloque D):** cualquier valor distinto
del literal `"default"` ahora responde 400 `CONTRACT_CRAMER_PARTICION_UNSUPPORTED`
en el borde del endpoint, **antes** de llegar a
`core/etapa1/homogeneity.py::calcular_cramer` — ya no produce un `TypeError`
no manejado / 500. Esto no implementa la partición personalizada (sigue sin
existir ninguna de las tres opciones evaluadas en la decisión), solo cierra
el 500. Hoy el frontend nunca envía otra cosa que `"default"`. Ver
`docs/decisiones/decision036.md` — DECISIÓN 036.

**Cerrado 09/08/2026 (DECISIÓN 054, Bloque A del plan de Etapa 2) —
`etapas` cableado de punta a punta.** La nota anterior de esta sección
afirmaba que `etapas: str = Form("1")` se recibía y se descartaba sin
llegar nunca a `services/`. Ya no: se parsea a `list[int]` en el borde del
endpoint (`api/v1/analysis.py`), solo se aceptan los literales `"1"` y
`"1,2"` — cualquier otro valor responde 400 `CONTRACT_ETAPAS_INVALID`. La
función de `services/` se renombró de `stream_etapa1()` a
`stream_analysis()` en el mismo cambio. `schemas/analysis.py::AnalysisRequest`
se borró — código muerto que ninguna ruta importaba, ver DECISIÓN 037
(cerrada por DECISIÓN 054). **La orquestación real de Etapa 2** (llamar
`ejecutar_etapa2()`, emitir `result_etapa2_ranking`, pausar) todavía no
está implementada — `etapas` se acepta y valida, pero con `etapas=1,2` el
stream hoy corre exactamente igual que con `etapas=1`. Queda para el
Bloque A5 del plan de Etapa 2.

**Agregado 12/08/2026 (DECISIÓN 057, Bloque F3 del plan de Etapa 2) —
`mes_inicio_anio: int = Form(7)`.** Mes de inicio del año hidrológico,
`[1..12]`, validado en el borde del endpoint → 400
`CONTRACT_MES_INICIO_INVALID` fuera de rango. Default `7` (julio) — el año
hidrológico de la región centro, conservado como default razonable, no como
regla universal (`constraints.md` lo describía antes como una constante del
sistema; ver la corrección en esa sección). Solo tiene efecto cuando la
resolución temporal de la serie subida es `"mensual"`
(`core/validacion/aggregation.py::agregar_a_maximos_anuales()`, llamado
dentro de `ejecutar_etapa1()`); con una serie ya anual el valor se acepta y
valida igual, pero no cambia nada. Se persiste en `analyses.configuracion`
para CU-01 — no es opcional, dos análisis con `mes_inicio_anio` distinto
sobre el mismo archivo dan resultados distintos.

**Errores:** 400 `PARSE_FILE_TOO_LARGE` si `archivo` supera 10 MB — DECISIÓN
050. Excepción a la regla general de esta sección: como el archivo se lee
completo (en chunks, con corte temprano) **antes** de construir el
`StreamingResponse`, este código nunca llega como evento SSE — es una
respuesta HTTP 400 estándar, igual que cualquier otro 400 de este catálogo.
El resto de los errores de parseo/contrato sí llegan como eventos SSE
(ver "Stream / sesión" en el catálogo, más abajo).

---

### POST /api/v1/analysis/outlier-decision

**Request:**
```json
{
  "session_id": "uuid-de-sesion-activa",
  "decision": "rechazar | aceptar",
  "dato_atipico": 245.7
}
```

**Auth:** JWT opcional (mismo que el stream activo)

**Response:**
```json
{"ok": true, "pipeline_continua": true}
```

**Solo para CU-01 y CU-02. CU-03 no usa este endpoint.**

---

### POST /api/v1/analysis/preview-columns

**Agregado en DECISIÓN 047 (pasada 4, Bloque D)** — previsualización de
columnas para poblar los dropdowns de `ConfigPage`, reusando el mismo
parser que `POST /analysis/stream` (`core/validacion/parser.py`).

**Request (multipart/form-data):**
```json
{"archivo": "<file CSV o Excel>"}
```

**Auth:** Sin dependencia de usuario — no hay diferencia de comportamiento
según quién llama, así que no inspecciona la cookie en absoluto (a
diferencia de `/analysis/stream`, que sí declara `get_optional_user`).

**Completamente stateless.** No genera `session_id`, no toca
`session_store`, no escribe en BD.

**Response 200:**
```json
{
  "columnas": [
    {"nombre": "anio", "indice": 0, "muestra": ["1980", "1981", "1982"]},
    {"nombre": "caudal", "indice": 1, "muestra": ["94.71", "89.83", "105.13"]}
  ],
  "filas": 40
}
```

**Errores:** 400 `PARSE_ERROR` para cualquier archivo no parseable
(incluido vacío — `pandas.errors.EmptyDataError` es subclase de
`ValueError`, capturado por el mismo `except`). No hay un segundo código
para "sin columnas utilizables": verificado que pandas no puede devolver
un DataFrame con cero columnas sin haber lanzado antes — ver DECISIÓN 047,
addendum. 400 `PARSE_FILE_TOO_LARGE` si `archivo` supera 10 MB — DECISIÓN 050,
el mismo cap que `/analysis/stream`.

---

### GET /api/v1/history/

**Agregado el parámetro `archivados` en DECISIÓN 048 (pasada 4, Bloque E)** —
por defecto excluye los análisis archivados; `?archivados=true` los incluye.
Cada item del array ahora expone `archivado_at` (`null` si no está archivado).

**Agregados `nombre_archivo` y `serie_preview` en el PR 4 del plan de fixes
pre-reunión (F7a/F7b, 14/08/2026)** — antes la lista solo exponía
`tipo_variable`, indistinguible entre análisis del mismo tipo de variable.
`nombre_archivo` vive en `analyses.configuracion` (JSONB, sin migración —
mismo campo que `cramer_particion`/`mes_inicio_anio`), poblado desde el
`filename` real que ya recibía `stream_analysis()`. `serie_preview` reusa
`analyses.serie` tal cual (~40 valores típicos, no cambia el orden de
magnitud del payload) para una sparkline decorativa en cada fila — sin
timestamps ni ejes, ese detalle vive solo en `GET /history/{id}`.

**Sin backfill** (mismo criterio que `timestamps`, DECISIÓN 058 §4):
`nombre_archivo` es `null` para cualquier análisis persistido antes de este
PR — el frontend degrada explícitamente a mostrar `tipo_variable` en ese
caso, no oculta la fila ni la rompe.

**Auth:** JWT en HttpOnly Cookie (requerido)

**Response 200:**
```json
[
  {
    "id": "uuid",
    "tipo_variable": "otro",
    "modo": "experto",
    "etapas": ["1"],
    "created_at": "2026-07-31T01:19:27.556471",
    "archivado_at": null,
    "nombre_archivo": "estacion_04.csv",
    "serie_preview": [94.71, 89.83, 105.13]
  }
]
```

---

### GET /api/v1/history/{id}

**Documentado por primera vez en el PR 3 del plan de cierre de pendientes
no-test (DECISIÓN 058)** — el endpoint ya existía (`history.py::get_history_item`,
`services/analysis_service.py::get_analysis_by_id()`), esta sección nunca se
había escrito. Al mismo tiempo gana tres campos nuevos: `serie`,
`timestamps`, `configuracion` — cierran el hueco que el PR 9 del plan de
Etapa 2 dejó anotado (`mes_inicio_anio` ya se persistía desde DECISIÓN 057,
pero el endpoint no lo devolvía, así que la nota de criterio de año nunca
llegaba a `HistoryDetailPage`).

**Bloque C2 del plan post-avance (14/08/2026)** — dos campos más:

- **`decisiones`** — el registro de auditoría de CU-01 ya se persistía
  (`analysis_results.decisiones`, ver `architecture.md`) pero este endpoint
  nunca lo devolvía. `{}` (nunca `null`) para un análisis sin ninguna pausa
  resuelta — `_persistir()` siempre recibe al menos `{}`.
- **`etapa2.seleccion`** — `_serializar_etapa2()` gana un bloque opcional con
  la distribución+método elegidos y sus resultados
  (`{distribucion, metodo, periodos_retorno, eventos_diseno, curva_ajuste}`),
  para que el historial pueda mostrar la elección sin recalcular nada.
  `null` cuando `etapa2` no es `null` pero no se llegó a elegir ninguna
  distribución (stream abandonado en la pausa — ver B4, plan post-avance,
  todavía sin resolver) — mismo criterio sin backfill que `timestamps`
  (DECISIÓN 058 §4).

**Auth:** JWT en HttpOnly Cookie (requerido). Verifica pertenencia
(`user_id`) — un análisis ajeno responde 404, no 403.

**Response 200:**
```json
{
  "id": "uuid",
  "tipo_variable": "otro",
  "modo": "experto",
  "etapas": ["1"],
  "created_at": "2026-07-31T01:19:27.556471",
  "etapa1": { "...": "ver payload de result_etapa1 en statistical-pipeline.md" },
  "etapa2": {
    "ranking": ["...", "ver DECISIÓN 055 — la grilla completa, sin aplanar"],
    "warnings": ["..."],
    "puntos_empiricos": ["..."],
    "seleccion": {
      "distribucion": "gve",
      "metodo": "ml",
      "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500],
      "eventos_diseno": [{"periodo_retorno": 2, "valor": 107.5625}],
      "curva_ajuste": [{"periodo_retorno": 1.05, "valor": 61.2}]
    }
  },
  "decisiones": {
    "chow": {"accion": "rechazar", "dato": 950.0},
    "distribucion": {"distribucion": "gve", "metodo": "ml", "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500]}
  },
  "serie": [94.71, 89.83],
  "timestamps": [{"iso": "1980-01-01", "anio": 1980}],
  "configuracion": {"cramer_particion": "default", "mes_inicio_anio": 7}
}
```

`serie`/`timestamps`/`configuracion` son la entrada tal como se subió y
configuró (`analyses`, DECISIÓN 058 §1) — no el resultado del análisis, que
ya viaja dentro de `etapa1.datos`. `timestamps` es `null` para cualquier
análisis persistido antes de la migración `005` (sin backfill, ver
DECISIÓN 058 §4) — el frontend degrada explícitamente para esos casos en
vez de reconstruir datos.

**Errores:** 404 si el análisis no existe o no pertenece al usuario

---

### POST /api/v1/history/{id}/archive

**Agregado en DECISIÓN 048 (pasada 4, Bloque E)** — soft-delete de un
análisis: marca `archivado_at` con la fecha/hora actual. No borra la fila
— ver `docs/decisiones/decision048.md` para la justificación (trazabilidad
de auditoría, `constraints.md`).

**Auth:** JWT en HttpOnly Cookie (requerido). Verifica pertenencia
(`user_id`) igual que `GET /history/{id}` — un análisis ajeno responde 404,
no 403 (no se revela si el id existe).

**Response 200:** `{"ok": true}`
**Errores:** 404 si el análisis no existe o no pertenece al usuario

---

### POST /api/v1/history/{id}/unarchive

**Agregado en DECISIÓN 048 (pasada 4, Bloque E)** — inverso de `/archive`:
limpia `archivado_at` (vuelve a `null`).

**Auth:** JWT en HttpOnly Cookie (requerido). Misma verificación de
pertenencia que `/archive`.

**Response 200:** `{"ok": true}`
**Errores:** 404 si el análisis no existe o no pertenece al usuario

---

### POST /api/v1/analysis/design-events — REEMPLAZADO por `distribution-decision`

**Reemplazado 09/08/2026 (DECISIÓN 052, Bloque A del plan de Etapa 2).**
Este contrato se documentó pero nunca se implementó — el router real nunca
tuvo esta ruta. Con Etapa 2 cableada al mismo stream SSE que Etapa 1
(DECISIÓN 052), un endpoint sincrónico que devuelve los eventos calculados
deja de tener sentido: el cliente ya tiene una conexión SSE abierta
esperando el ranking. Se reemplaza por
[`POST /analysis/distribution-decision`](#post-apiv1analysisdistribution-decision-decisión-052)
— misma forma que `outlier-decision`, el cliente manda una decisión, no
recibe un resultado en la misma respuesta. Se conserva esta entrada, sin
borrar, por trazabilidad — no se implementa el contrato tal como está
escrito abajo.

**Request:**
```json
{
  "session_id": "uuid-de-sesion-activa",
  "distribucion": "gumbel",
  "metodo": "momentos | mv | me | ml | mpp | mc",
  "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500]
}
```

**Auth:** JWT opcional

**Response:**
```json
{
  "distribucion": "gumbel",
  "metodo": "momentos",
  "parametros": {"mu": 142.5, "sigma": 38.2},
  "eventos_diseno": [
    {"periodo_retorno": 2, "valor": 138.4},
    {"periodo_retorno": 100, "valor": 312.7}
  ],
  "grafico_ajuste": "<base64 o url>",
  "analysis_id": "uuid | null"
}
```

---

### POST /api/v1/analysis/distribution-decision (DECISIÓN 052)

**Agregado 09/08/2026** — reemplaza a `design-events` (arriba). Misma forma
que `outlier-decision`: el cliente manda la decisión, el resultado (eventos
de diseño, evento `result_etapa2_eventos`) viaja por el stream SSE ya
abierto, no en la respuesta de este endpoint.

**Request:**
```json
{
  "session_id": "uuid-de-sesion-activa",
  "distribucion": "gumbel",
  "metodo": "momentos",
  "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500]
}
```

**Auth:** JWT opcional (mismo que el stream activo)

**Validación en el borde** (no con restricciones Pydantic — necesita
devolver el código propio, no un 422 genérico de FastAPI):
`distribucion` y `metodo` no vacíos; `periodos_retorno` con entre 1 y 20
elementos, todos `> 1` (`F = 1 - 1/T` necesita `T > 1` para caer en
`(0,1)` — mismo guard que `cuantil()` en `core/`, duplicado acá para
devolver un 400 legible en vez de un 500). Cualquier violación → 400
`DIST_SELECTION_INVALID`, evaluado antes de tocar `session_store`.

**Response 200:**
```json
{"ok": true, "pipeline_continua": true}
```

**Errores:** 404 `SESSION_NOT_FOUND` (la sesión no existe o ya expiró — a
diferencia de `outlier-decision`, que no valida existencia de sesión, este
endpoint sí lo hace explícitamente por mandato de DECISIÓN 052), 400
`DIST_SELECTION_INVALID`.

**Estado de implementación (09/08/2026, cierre del Bloque A1-A6 del plan de
Etapa 2):** cableado de punta a punta y verificado. El stream pausa de
verdad en `result_etapa2_ranking`, este endpoint la desbloquea, y el
stream calcula los eventos de diseño reales (`core/etapa2/design_events.py`,
Bloque A4) y persiste `analysis_results.etapa2` para CU-01 (Bloque A5).
Verificado con `tests/integration/test_etapa2_stream_distribution_decision.py`
(stream completo, sin red) y con un smoke test manual contra el backend real
vía HTTP — CU-01 con `etapas=1,2`, `distribution-decision` real, y
`psql` confirmando `analysis_results.etapa2` con las 13 distribuciones.
Ver `.claude/rules/core/statistical-pipeline.md` para la secuencia SSE
completa.

**Solo para CU-01 y CU-02. CU-03 no usa este endpoint** — mismo alcance
que `outlier-decision`.

---

### POST /api/v1/analysis/{id}/design-events (DECISIÓN 062, Bloque C2c)

**Agregado 18/08/2026** — historial interactivo: recálculo **stateless** de
eventos de diseño para una distribución+método distintos de los elegidos
durante el stream original, sin reajustar nada. Los `parametros` de las 28
combinaciones ya viven en `analysis_results.etapa2.ranking` (DECISIÓN 055)
— este endpoint solo busca la fila que corresponde y llama
`calcular_eventos_diseno()`, la misma función pura que usa el stream.

No confundir con `POST /analysis/distribution-decision`: ese endpoint
resuelve una pausa real de un stream en curso, con `session_id`; este no
tiene ninguna sesión de por medio, opera directo sobre un análisis ya
persistido por su `id`.

**Request:**
```json
{
  "distribucion": "gve",
  "metodo": "ml",
  "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500]
}
```

**Auth:** JWT en HttpOnly Cookie (requerido) — a diferencia de
`distribution-decision` (JWT opcional, sigue al stream activo), este
endpoint siempre requiere sesión: solo CU-01 tiene historial. Verifica
pertenencia igual que `GET /history/{id}` — un análisis ajeno o inexistente
responde 404 sin distinguir los dos casos.

**Validación en el borde:** misma función que `distribution-decision`
(`distribucion`/`metodo` no vacíos, `periodos_retorno` entre 1 y 20
elementos todos `> 1`) → 400 `DIST_SELECTION_INVALID` — la forma del
request es idéntica, el destino de la decisión es lo único que cambia.

**Response 200:**
```json
{
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
Mismo formato que `result_etapa2_eventos` del stream (`curva_ajuste`: 60
puntos en escala logarítmica, no los `periodos_retorno` pedidos — ver
`statistical-pipeline.md`). `valor` puede ser `null` para un período
puntual si `cuantil()` falla para esa distribución+método, igual que en el
stream.

**Errores:**
- 404 `ANALYSIS_NOT_FOUND` — el análisis no existe, no pertenece al
  usuario, o no tiene Etapa 2 ejecutada (`analysis_results.etapa2` es
  `null`). Los tres casos responden igual, sin revelar cuál aplica.
- 400 `DIST_SELECTION_INVALID` — forma del request inválida (ver arriba).
- 400 `DIST_METHOD_NOT_FITTED` — la combinación pedida no aparece en el
  ranking persistido, o aparece con `status != "ok"` (no convergió, no
  aplicable, deshabilitada por ceros) — no hay `parametros` de los que
  partir. Distinto de `DIST_SELECTION_INVALID`: ese código es sobre la
  forma del request, este es sobre si la combinación bien formada tiene
  algo que recalcular.

**No toca `session_store`, no persiste nada, no altera
`analysis_results.decisiones`** — DECISIÓN 062, "explorar no es decidir".
El registro de auditoría de CU-01 sigue reflejando exactamente lo que se
decidió durante el análisis, nunca una exploración posterior desde el
historial.

**Solo para CU-01.** CU-02 no tiene historial que explorar; CU-03 no usa
este router.

---

### POST /api/v1/validate/ (CU-03)

**Request (multipart/form-data):**
```json
{
  "client_id": "identificador-sistema-externo",
  "archivo": "<file CSV o Excel>",
  "columna_x": "nombre_o_indice",
  "columna_y": "nombre_o_indice",
  "tipo_variable": "caudal_precipitacion | otro"
}
```

**Auth:** Header `X-API-Key: <key>`

**Response JSON completo:**
```json
{
  "client_id": "string",
  "nivel_confianza": "validado | con_warnings | rechazado",
  "timestamp": "ISO8601",
  "contrato": {
    "estado": "aprobado | aprobado_con_warnings | rechazado",
    "problemas": [
      {"campo": "serie", "codigo": "CONTRACT_LENGTH_WARNING", "descripcion": "...", "accion": "continua"}
    ]
  },
  "estadistica_descriptiva": {
    "n": 35,
    "media": 142.5,
    "mediana": 138.2,
    "desvio_estandar": 38.1,
    "coef_variacion": 0.267,
    "coef_asimetria": 0.84,
    "minimo": 72.3,
    "maximo": 312.7
  },
  "etapa_1": {
    "independencia": {
      "nivel": "independiente | dependiente",
      "anderson": {"estadistico": 0.23, "valor_critico": 0.37, "veredicto": "aprobada"},
      "wald_wolfowitz": {"estadistico": 0.37, "valor_critico": 1.96, "veredicto": "aprobada", "warning": null}
    },
    "homogeneidad": {
      "nivel": "homogeneidad_ok | homogeneidad_warning | homogeneidad_critica",
      "helmert": {"estadistico": 2.1, "valor_critico": 4.8, "veredicto": "aprobada"},
      "t_student": {"estadistico": -1.76, "valor_critico": 2.07, "veredicto": "aprobada", "grados_libertad": 22},
      "cramer": {"tau60": 0.183, "tau30": 0.352, "valor_critico": 2.07, "veredicto": "aprobada", "n1": 21, "n2": 11}
    },
    "tendencia": {
      "mann_kendall": {"estadistico": 1.12, "valor_critico": 1.96, "veredicto": "sin_tendencia"},
      "kolmogorov_smirnov": {"estadistico": 0.89, "valor_critico": 1.358, "veredicto": "sin_tendencia"}
    },
    "atipicos": {
      "chow": {"estadistico": null, "valor_critico": null, "veredicto": "no_ejecutada", "codigo": "TEST_NOT_EXECUTED_ZEROS"}
    },
    "warnings": [
      {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "descripcion": "Serie con 28 datos — resultados no certificables"}
    ]
  }
}
```

---

## Catálogo completo de códigos estandarizados

### Auth
```
AUTH_EMAIL_ALREADY_REGISTERED     Email ya registrado (register)
AUTH_VERIFICATION_EMAIL_FAILED    Fallo al enviar mail de verificación (register)
AUTH_INVALID_TOKEN                Token de verificación inválido o expirado (verify)
AUTH_USER_NOT_FOUND               Usuario no encontrado (verify)
AUTH_INVALID_CREDENTIALS          Email o contraseña incorrectos (login)
AUTH_EMAIL_NOT_VERIFIED           Email sin verificar (login)
```

### Contrato — bloqueantes
```
CONTRACT_SERIES_TOO_SHORT        Serie con menos de 10 datos
CONTRACT_NO_TEMPORAL_RESOLUTION  Resolución temporal no declarada
```

### Contrato — warnings
```
CONTRACT_LENGTH_WARNING          Entre 10 y 29 datos
CONTRACT_NEGATIVE_VALUES         Valores negativos en caudal_precipitacion
CONTRACT_MISSING_VALUES          Valores faltantes o celdas vacías
CONTRACT_DUPLICATE_TIMESTAMPS    Duplicados temporales
CONTRACT_WRONG_ORDER             Orden cronológico incorrecto
CONTRACT_IRREGULAR_SPACING       Espaciado temporal irregular
CONTRACT_NON_NUMERIC_VALUES      Valores no numéricos mezclados
CONTRACT_PARTIAL_YEARS_TRIMMED   Agregación mensual (Bloque F4): años parciales recortados en los extremos del registro
CONTRACT_INCOMPLETE_YEARS_DISCARDED  Agregación mensual (Bloque F4): año incompleto descartado dentro del registro (no en un extremo)
```
`CONTRACT_PARTIAL_YEARS_TRIMMED` y `CONTRACT_INCOMPLETE_YEARS_DISCARDED` los
emite `core/pipeline/pipeline_etapa1.py::_warnings_de_agregacion()`, no
`core/validacion/contract.py` — son resultado de
`core/validacion/aggregation.py::agregar_a_maximos_anuales()`, que corre
antes de `validar_contrato()` cuando `resolucion_temporal == "mensual"`
(DECISIÓN 057). Se agrupan acá por dominio (contrato de datos temporal), no
por el módulo que los emite — mismo criterio que ya aplica el resto de esta
sección.

### Contrato — parámetros de request (no de la serie)
```
CONTRACT_CRAMER_PARTICION_UNSUPPORTED  cramer_particion distinto de "default" (DECISIÓN 036)
CONTRACT_ETAPAS_INVALID                etapas fuera de {"1", "1,2"} (DECISIÓN 054)
CONTRACT_MES_INICIO_INVALID            mes_inicio_anio fuera de [1..12] (DECISIÓN 057)
```
A diferencia de los dos grupos de arriba (series de datos), estos códigos validan
un parámetro del request en `POST /analysis/stream` antes de tocar el archivo
subido o el pipeline — 400, no bloquean una serie válida, bloquean una opción
inválida o todavía no implementada.

### Etapa 1 — pruebas
```
TEST_CRITICAL_INDEPENDENCE       Anderson rechaza — CRÍTICO
TEST_CRITICAL_HOMOGENEITY        Cramer rechaza — CRÍTICO
TEST_WARNING_TREND               Mann-Kendall o KS detectan tendencia
TEST_WARNING_HOMOGENEITY         Helmert o t de Student rechazan
TEST_WARNING_SMALL_SAMPLE        Wald-Wolfowitz con n ≤ 40, o Mann-Kendall con 10 ≤ n ≤ 30 (*)
TEST_WARNING_OUTLIER_DETECTED    Chow detecta atípico — decisión pendiente
TEST_OUTLIER_REJECTED_BY_USER    Usuario rechazó el dato atípico
TEST_OUTLIER_ACCEPTED_BY_USER    Usuario aceptó el dato como parte de la población
TEST_NOT_EXECUTED_ZEROS          Chow no ejecutado por ceros en caudal_precipitacion
TEST_NOT_EXECUTED_CONDITION      Prueba con condición no cumplida
TEST_NOT_EXECUTED_MIN_SAMPLES    Mann-Kendall no ejecutado — serie con n < 10
```

(*) `core/etapa1/independence.py::determinar_warnings_independencia` promueve el
`warning_codigo` de Wald-Wolfowitz a `result.warnings` correctamente.
`core/etapa1/trend.py::determinar_warnings_tendencia` **no** hace lo mismo con el
de Mann-Kendall — el `TestResult` individual lo lleva, pero nunca llega a la lista
agregada de warnings. Gap encontrado y documentado, no corregido — ver
`docs/decisiones/decision038.md` — DECISIÓN 038.

### Etapa 2 — distribuciones
```
DIST_NOT_APPLICABLE              Combinación sin sentido matemático para esos datos
DIST_NOT_CONVERGED               Método iterativo sin solución estable
DIST_HIGH_EEA                    EEA supera el 5% de la media
DIST_DISABLED_ZEROS              Distribución deshabilitada por ceros en caudal_precipitacion
DIST_ZEROS_TOLERATED             Serie con ceros, ajuste calculado igual — pendiente confirmación
                                  de dominio con Facundo (DECISIÓN 061). Solo exponencial_x0_beta,
                                  gen_pareto y gen_exponencial/momentos+ml — ver
                                  TOLERA_CEROS_CON_ADVERTENCIA en distributions/__init__.py
DIST_SELECTION_INVALID           distribucion/metodo vacíos o periodos_retorno inválido (DECISIÓN 052) —
                                  compartido entre distribution-decision y POST /analysis/{id}/design-events
DIST_METHOD_NOT_FITTED           La combinación distribución+método pedida en POST /analysis/{id}/design-events
                                  no aparece en el ranking persistido, o su status != "ok" (DECISIÓN 062)
```
`DIST_SELECTION_INVALID` y `DIST_METHOD_NOT_FITTED` no son estados de
ajuste de una distribución como los otros cinco — son validaciones de
request (respuesta HTTP 400, no un campo de `DistResult`). Se agrupan acá
por prefijo/dominio, igual que `CONTRACT_ETAPAS_INVALID` se agrupa con los
códigos de contrato pese a validar un parámetro de request y no la serie.

### Stream / sesión
```
PARSE_ERROR                      No se pudo parsear el archivo subido (evento SSE "error")
SESSION_TIMEOUT                  Se agotó el tiempo de espera de decisión ante un atípico (evento SSE "error")
PARSE_FILE_TOO_LARGE             El archivo supera el límite de subida — respuesta HTTP 400, no evento SSE
SESSION_NOT_FOUND                session_id no existe o ya expiró — respuesta HTTP 404, no evento SSE (DECISIÓN 052)
ANALYSIS_NOT_FOUND               El análisis de POST /analysis/{id}/design-events no existe, no es del
                                  usuario, o no tiene Etapa 2 — respuesta HTTP 404, sin sesión de por medio (DECISIÓN 062)
```
`PARSE_ERROR` y `SESSION_TIMEOUT` son eventos SSE `error`, no respuestas HTTP
de error — ver nota general al principio de este archivo. Emitidos por
`services/analysis_service.py`. Agregados al catálogo en
`docs/decisiones/decision038.md` — DECISIÓN 038, que también deja la regla:
todo código nuevo emitido por `core/` o `services/` se agrega acá en el mismo
commit que lo introduce.

`PARSE_FILE_TOO_LARGE` es la excepción del grupo: se detecta en `api/v1/analysis.py`
**antes** de que exista un stream SSE (en `/analysis/stream`) o directamente en un
endpoint sincrónico (`/analysis/preview-columns`), así que siempre es una respuesta
HTTP 400 estándar — DECISIÓN 050. Se agrupa acá por dominio (falla al ingerir el
archivo subido), no por transporte.

`SESSION_NOT_FOUND` es la misma excepción por el mismo motivo: `distribution-decision`
es un endpoint sincrónico aparte del stream (igual que `outlier-decision`), así
que responde HTTP 404 estándar, nunca un evento SSE — DECISIÓN 052.

`ANALYSIS_NOT_FOUND` se agrupa acá por dominio (identifica qué análisis no se
pudo resolver, mismo motivo que agrupa a `SESSION_NOT_FOUND`) aunque
`POST /analysis/{id}/design-events` no tiene ningún `session_id` ni stream
de por medio — es un recálculo stateless sobre un análisis ya persistido
(DECISIÓN 062).

### Códigos originados en el frontend
```
VALIDATION_ERROR          Sintetizado por api/client.ts ante un 422 genérico de
                           FastAPI/Pydantic sin código propio — no lo manda el backend.
STREAM_CONNECTION_ERROR   Sintetizado por api/sse.ts::onerror ante una falla de red/
                           conexión del stream SSE — condición client-side, el
                           backend nunca la ve ni la emite.
STREAM_CLOSED_EARLY       Sintetizado por api/sse.ts::onclose cuando el servidor
                           cierra la conexión sin haber emitido `complete` antes —
                           sin esto la fase quedaba en "streaming"/"waiting_outlier"
                           para siempre y en silencio (F1, informe-diagnostico-ui-rota.md).
SESSION_NOT_ESTABLISHED   Sintetizado por auth/AuthProvider.tsx::login cuando
                           POST /auth/login respondió 200 pero el GET /auth/me
                           posterior no pudo confirmar la sesión — antes login()
                           resolvía igual sin lanzar, y el botón se veía "muerto"
                           (F3, informe-diagnostico-ui-rota.md).
```
Estos cuatro no tienen contraparte en `core/`/`services/` porque describen condiciones
que solo el cliente puede detectar (fallo de red, 422 sin `codigo` propio del
backend, cierre de conexión sin `complete`, login aceptado sin sesión confirmada) — no es un gap de sincronización, es
el catálogo reconociendo que no todo código de error se origina en el servidor.
Los dos primeros se agregaron en el addendum del 29/07/2026 de
`docs/decisiones/decision038.md` — DECISIÓN 038, que también deja la regla
explícita en esta dirección: todo código nuevo que el frontend invente para una
condición client-side se agrega acá en el mismo commit que lo introduce, igual
que los de `core/`/`services/`.
