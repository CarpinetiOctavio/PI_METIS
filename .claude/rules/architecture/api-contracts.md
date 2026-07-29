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
  "cramer_particion": "default | {n1_pct: 60, n2_pct: 30}"
}
```

**Auth:** JWT en HttpOnly Cookie (opcional — sin JWT = CU-02, con JWT = CU-01)

**Response:** `text/event-stream`

**Comportamiento según JWT:**
- Con JWT válido (@ucc.edu.ar): persiste análisis, habilita exportación
- Sin JWT: sesión efímera, sin persistencia

**Nota de implementación — `cramer_particion` personalizada no implementada.**
El contrato de arriba documenta `{n1_pct, n2_pct}` como valor válido, pero el
endpoint real (`api/v1/analysis.py`) declara el campo como `Form(str)` — cualquier
valor distinto del literal `"default"` llega como string a
`core/etapa1/homogeneity.py::calcular_cramer` y produce un `TypeError` no
manejado, no un 400 controlado. Hoy el frontend nunca envía otra cosa que
`"default"`. Ver `docs/decisiones/decision036.md` — DECISIÓN 036.

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

### POST /api/v1/analysis/design-events

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
```

### Etapa 1 — pruebas
```
TEST_CRITICAL_INDEPENDENCE       Anderson rechaza — CRÍTICO
TEST_CRITICAL_HOMOGENEITY        Cramer rechaza — CRÍTICO
TEST_WARNING_TREND               Mann-Kendall o KS detectan tendencia
TEST_WARNING_HOMOGENEITY         Helmert o t de Student rechazan
TEST_WARNING_SMALL_SAMPLE        Wald-Wolfowitz con n ≤ 40
TEST_WARNING_OUTLIER_DETECTED    Chow detecta atípico — decisión pendiente
TEST_OUTLIER_REJECTED_BY_USER    Usuario rechazó el dato atípico
TEST_OUTLIER_ACCEPTED_BY_USER    Usuario aceptó el dato como parte de la población
TEST_NOT_EXECUTED_ZEROS          Chow no ejecutado por ceros en caudal_precipitacion
TEST_NOT_EXECUTED_CONDITION      Prueba con condición no cumplida
```

### Etapa 2 — distribuciones
```
DIST_NOT_APPLICABLE              Combinación sin sentido matemático para esos datos
DIST_NOT_CONVERGED               Método iterativo sin solución estable
DIST_HIGH_EEA                    EEA supera el 5% de la media
DIST_DISABLED_ZEROS              Distribución deshabilitada por ceros en caudal_precipitacion
```
