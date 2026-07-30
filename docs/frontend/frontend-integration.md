# Referencia de Integración Frontend — METIS

**Propósito.** Documento de referencia para construir el frontend (React + TypeScript,
tema "Instrumento") contra el backend REAL tal como existe hoy en `backend/metis/`.
Todo lo escrito acá surge de leer el código, no de `api-contracts.md` — donde el código
y el contrato documentado difieren, se marca explícitamente con **⚠️ DISCREPANCIA**.

**Fecha del relevamiento.** 22/07/2026.
**Alcance del backend relevado:** `feature/services-sse` + `feature/auth-refactor` mergeados
a `staging`. Etapa 2 (`feature/core-etapa2`) existe como motor en `metis/core/etapa2/` pero
**no está expuesta por ningún endpoint todavía** — ver sección "Gaps" antes de diseñar
cualquier pantalla que dependa de ranking de distribuciones o eventos de diseño.

---

## 1. Cómo correr el backend en local

### Opción A — Docker Compose completo

```bash
docker-compose up --build
```

Backend queda en `http://localhost:8000` (mapeo `ports: ["8000:8000"]` en
`docker-compose.yml` — necesario porque el frontend en desarrollo corre en el host,
fuera de la red Docker). Postgres en `localhost:5432`.

`nginx` y `frontend` también están declarados en `docker-compose.yml`, pero
`frontend/` **no tiene todavía ningún proyecto React** (no existe `package.json`) —
su build fallará. Para desarrollo de frontend, no levantar esos dos servicios:

```bash
docker-compose up --build backend postgres
```

### Opción B — Backend suelto con uvicorn (sin Docker)

```bash
cd backend
pip install -r requirements.txt
uvicorn metis.main:app --reload --port 8000
```

Requiere Postgres accesible en `localhost:5432` (podés levantar solo el
contenedor `postgres` con `docker-compose up postgres` y dejar el backend corriendo
directo en el host).

### Variables de entorno mínimas (`.env` en la raíz del repo)

Copiar `.env.example` → `.env`. Los valores relevantes para el frontend:

```
FRONTEND_ORIGIN=http://localhost:5173   # CORS — debe ser EXACTO (protocolo+host+puerto)
FRONTEND_URL=http://localhost:5173      # usado para armar el link de verificación de mail
ENV=development                          # cookie JWT sin flag Secure (permite HTTP)
JWT_SECRET_KEY=<cualquier string largo>
DATABASE_URL=postgresql+asyncpg://metis_user:metis_pass@postgres:5432/metis
POSTGRES_USER=metis_user
POSTGRES_PASSWORD=metis_pass
POSTGRES_DB=metis
```

`.env.example` asume Vite en el puerto **5173** (no Create React App / 3000).
Si el frontend se scaffoldea con otra herramienta o puerto, hay que actualizar
`FRONTEND_ORIGIN` — si no coincide carácter por carácter, **todas** las requests
del frontend fallan por CORS (`main.py` solo permite un único origen, ver §4).

Sin SMTP configurado (`SMTP_HOST/USER/PASSWORD/FROM_ADDRESS`), `POST /auth/register`
devuelve `500 AUTH_VERIFICATION_EMAIL_FAILED` — para probar el flujo de auth completo
localmente hace falta el App Password real (ver `sprint.md`, sección auth), o mockear
`auth/email.py` del lado de quien prueba.

### Migraciones (si la base está vacía)

```bash
DATABASE_URL=postgresql+asyncpg://metis_user:metis_pass@localhost:5432/metis \
  alembic upgrade head
```
(ejecutar desde `backend/`, con Postgres accesible en `localhost` — ver
`architecture.md` sección "DATABASE_URL — diferencia entre Docker y host").

### Endpoint de salud

`GET /ping` → `{"status": "ok"}`, sin auth ni prefijo `/api/v1`. Útil para
verificar que el backend está arriba antes de cablear el frontend.

---

## 2. Auth — mecánica real y CORS

### Cookie JWT

- Nombre: **`access_token`** (constante en `auth/router.py` y `auth/dependencies.py`).
- Flags: `HttpOnly=True`, `SameSite=Lax`, `Secure` = `True` solo si `ENV=production`
  (en desarrollo es `False`, por eso funciona sobre `http://localhost`).
- **No se setea `Max-Age`/`Expires` explícito en la cookie** — es una cookie de sesión
  de navegador. El JWT interno expira a los `JWT_EXPIRE_MINUTES` (default 60), pero
  si el navegador se cierra, la cookie puede perderse antes de esos 60 minutos según
  el navegador. No asumir persistencia entre reinicios del browser.
- El JWT firma `{"sub": <email>, "exp": <...>}` — el frontend nunca necesita leer el
  payload (la cookie es HttpOnly, JS no puede acceder de todas formas).

### CORS

`main.py`:
```python
allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Implicancia directa para el frontend:** todo `fetch`/`axios` debe mandar
`credentials: "include"` (fetch) o `withCredentials: true` (axios), si no la cookie
nunca viaja. Y el origen debe matchear `FRONTEND_ORIGIN` exactamente — un solo
origen permitido, no hay wildcard con credentials (FastAPI/Starlette lo rechaza
igual que el spec de CORS).

### Flujo register → verify → login → me → logout

Idéntico a lo documentado en `api-contracts.md`, con estas precisiones del código real:

- `POST /api/v1/auth/register` — valida `@ucc.edu.ar` y password ≥ 8 chars a nivel
  Pydantic (`schemas/auth.py`, `field_validator`) → **422** si falla eso (no 400).
  El 400 `AUTH_EMAIL_ALREADY_REGISTERED` es sólo para email duplicado.
  El mail de verificación se manda **antes** de commitear el usuario en BD — si
  falla el envío, no queda usuario huérfano (ver `docs/decisiones/decision032.md`).
- `POST /api/v1/auth/verify` — el token vive en un **dict en memoria del proceso**
  (`_pending_tokens` en `auth/router.py`), no en BD. Un restart del backend invalida
  todos los tokens de verificación pendientes. No hay expiración de token programada
  (dura hasta que se usa o hasta que el proceso reinicia).
- `POST /api/v1/auth/login` — setea la cookie. Actualiza `last_login`.
- `GET /api/v1/auth/me` — requiere cookie válida, 401 sin ella. Devuelve
  `{id, email, nombre, email_verified}` (`UserMe` en `schemas/auth.py`) — coincide
  con `api-contracts.md`.
- `POST /api/v1/auth/logout` — borra la cookie, responde `{"ok": true}` incluso sin
  sesión activa (no valida nada antes de borrar).

### CU-02 (anónimo)

No hay endpoint ni mecanismo especial: simplemente no se manda la cookie (o no
existe). `GET /api/v1/analysis/{id}` y `/history/*` **exigen** `get_current_user`
(401 sin cookie) — son exclusivos de CU-01. `POST /analysis/stream` y
`/analysis/outlier-decision` usan `get_optional_user` — funcionan con o sin cookie.

---

## 3. Catálogo de endpoints — request/response REALES

Prefijo base para todo excepto auth y `/ping`: **`/api/v1`**. Auth tiene su propio
prefijo `/api/v1/auth` declarado en el propio router (no en `main.py`).

### POST `/api/v1/auth/register`

Ver `schemas/auth.py::RegisterRequest`.
```ts
interface RegisterRequest {
  email: string;    // debe terminar en @ucc.edu.ar (422 si no)
  password: string; // mínimo 8 caracteres (422 si no)
  nombre?: string | null;
}
```
`201` → `{ ok: true, mensaje: string }`
Errores: `400 AUTH_EMAIL_ALREADY_REGISTERED`, `422` (Pydantic), `500 AUTH_VERIFICATION_EMAIL_FAILED`.

### POST `/api/v1/auth/verify`
```ts
interface VerifyRequest { token: string; }
```
`200` → `{ ok: true }` · Errores: `400 AUTH_INVALID_TOKEN`, `404 AUTH_USER_NOT_FOUND`.

### POST `/api/v1/auth/login`
```ts
interface LoginRequest { email: string; password: string; }
```
`200` → `{ ok: true }` + cookie `access_token`.
Errores: `401 AUTH_INVALID_CREDENTIALS`, `403 AUTH_EMAIL_NOT_VERIFIED`.

### POST `/api/v1/auth/logout`
Sin body. `200` → `{ ok: true }`.

### GET `/api/v1/auth/me`
```ts
interface UserMe {
  id: string;          // uuid
  email: string;
  nombre: string | null;
  email_verified: boolean;
}
```
`401` sin cookie válida.

---

### POST `/api/v1/analysis/stream`

⚠️ **DISCREPANCIA con `api-contracts.md`:** el endpoint real **no usa** el schema
`AnalysisRequest` de `schemas/analysis.py` (ese schema existe en el código pero no
está conectado a ningún endpoint — ver §5, Gaps). Los campos llegan como `Form(...)`
sueltos, todos `str`, sin la validación `Literal` que sugiere el schema:

```python
# metis/api/v1/analysis.py — firma real
archivo: UploadFile
columna_x: str
columna_y: str
tipo_variable: str        # NO validado contra Literal — cualquier string pasa acá
etapas: str = "1"          # ⚠️ recibido pero NUNCA usado — ver Gaps
modo: str = "experto"      # NO validado — cualquier string pasa acá
cramer_particion: str = "default"  # ⚠️ ver nota crítica abajo
```

**Request real (multipart/form-data):**
```ts
interface AnalysisStreamFormData {
  archivo: File;             // .csv o .xlsx/.xls
  columna_x: string;         // nombre de columna O índice numérico como string
  columna_y: string;
  tipo_variable: "caudal_precipitacion" | "otro"; // no forzado por el backend, pero core sí lo espera así
  etapas?: string;           // aceptado por el form pero ignorado — Etapa 2 nunca se ejecuta acá
  modo?: "paso_a_paso" | "experto"; // solo afecta lo que se persiste (columna `modo`), no cambia el output del stream
  cramer_particion?: string; // SOLO "default" funciona de forma confiable — ver nota
}
```

**⚠️ Nota crítica — `cramer_particion` custom está roto en el wiring actual.**
`calcular_cramer()` (`core/etapa1/homogeneity.py`) espera `particion` como
`dict` con claves `n1_pct`/`n2_pct`, o el string literal `"default"`. El endpoint
HTTP recibe `cramer_particion` como `Form(str)` y lo pasa **sin parsear** hasta
`ejecutar_etapa1()`. Si el frontend manda cualquier valor que no sea exactamente
`"default"` (p. ej. un JSON serializado `'{"n1_pct":60,"n2_pct":30}'`), Python
intenta `"...json string..."["n1_pct"]`, que **falla en runtime** (TypeError,
no un 400 controlado) porque un string no es indexable por clave. **No hay
soporte funcional para partición de Cramer personalizada desde HTTP todavía** —
si la UI necesita el campo "Personalizada" (variante H de carga, ver
`frontend-design/metis-wireframes-fase1-decisiones.md`), hay que resolver esto
en el backend antes (deserializar JSON y pasar dict) o mockear esa opción como
deshabilitada/"próximamente" en el frontend mientras tanto.

**Response:** `text/event-stream` — ver catálogo completo de eventos en §4.
Headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no`.

`current_user` se resuelve con `get_optional_user` (cookie opcional) — con
cookie válida, el análisis se persiste al final y `complete` trae `analysis_id`
no nulo; sin cookie, `analysis_id` es siempre `null`.

---

### POST `/api/v1/analysis/outlier-decision`

Coincide con `api-contracts.md`:
```ts
interface OutlierDecisionRequest {
  session_id: string;   // uuid — el mismo que llegó en el evento outlier_detected
  decision: "rechazar" | "aceptar";
  dato_atipico: number;
}
interface OutlierDecisionResponse {
  ok: boolean;
  pipeline_continua: boolean; // siempre true en la implementación actual
}
```
⚠️ Nota de nombres: el campo que llega en el evento SSE `outlier_detected` se llama
`valor_atipico`, pero el campo de este request se llama `dato_atipico` — mismo
concepto, nombre distinto entre el evento y el request. El backend real **no
valida** que `dato_atipico` coincida con el valor que efectivamente detectó Chow —
`registrar_outlier_decision()` ignora ese campo por completo, solo usa
`session_id` y `decision`. Igual conviene que el frontend lo mande con el valor
recibido en `outlier_detected`, por si se agrega validación después.

Sin auth: `get_optional_user`, igual que `/stream`.

---

### POST `/api/v1/analysis/design-events`

**⚠️ NO IMPLEMENTADO.** No existe en `metis/api/v1/analysis.py` ni en ningún otro
router. `api-contracts.md` lo documenta, pero es aspiracional — corresponde a
Etapa 2, que según `sprint.md` todavía no está expuesta por API (el motor de
cálculo en `core/etapa2/` sí existe y está bastante avanzado, pero nada lo llama
desde `services/` ni desde `api/`). El frontend debe **mockear este endpoint
completo** — ver §5.

---

### GET `/api/v1/analysis/{analysis_id}`

```ts
interface AnalysisDetail {
  id: string;
  tipo_variable: string;
  modo: string | null;
  etapas: string[] | null;   // ej. ["1"] — siempre etapas=["1"] hoy, ver nota
  created_at: string;        // ISO8601
  etapa1: Etapa1Result | null;  // ver §4 para el shape exacto
  etapa2: null;              // SIEMPRE null hoy — Etapa 2 nunca se persiste
}
```
`404` si no existe o no pertenece al `user_id` de la cookie. Requiere auth
(`get_current_user`, no opcional) — a diferencia de `/stream` y
`/outlier-decision`, este si exige login.

Nota: `_persistir()` en `analysis_service.py` graba `etapas=["1"]` siempre,
hardcodeado — el campo `etapas` del form nunca llega a influir en lo persistido.

---

### GET `/api/v1/history/`

```ts
type HistoryList = HistoryItem[];
interface HistoryItem {
  id: string;
  tipo_variable: string;
  modo: string | null;
  etapas: string[] | null;
  created_at: string;
}
```
Ordenado por `created_at` descendente. Requiere auth.

⚠️ Discrepancia menor de forma: `api-contracts.md` no especifica si la respuesta
es un array plano o un objeto envolvente — el código devuelve **un array plano**,
sin envoltura `{items: [...]}` ni paginación.

### GET `/api/v1/history/{analysis_id}`

Mismo shape que `GET /api/v1/analysis/{analysis_id}` (llama a la misma función
`get_analysis_by_id`). Requiere auth. `404` si no es del usuario.

---

### GET `/api/v1/export/{id}` (PDF)

**⚠️ NO IMPLEMENTADO.** No hay router de exportación en el backend. Mockear en
el frontend — el botón "Exportar PDF" no tiene backend real todavía.

### POST `/api/v1/validate/` (CU-03)

**⚠️ NO IMPLEMENTADO.** Tampoco existe el modelo de auth por API Key en ningún
dependency (`api_clients` existe solo como tabla SQLAlchemy en
`db/models/api_client.py`, sin router ni lógica de hash/verificación de
`X-API-Key`). Si el alcance de esta sesión de frontend incluye CU-03, todo ese
flujo es 100% mock por ahora. Confirmado también por `sprint.md`
("Fuera de alcance en este sprint" / "sprint posterior").

---

## 4. Stream SSE — catálogo real de eventos

Framing real (`_sse()` en `analysis_service.py`):
```
event: <tipo>\ndata: <json>\n\n
```
Estándar — cualquier cliente `EventSource`/parser SSE estándar lo procesa sin
adaptación especial.

**Nota transversal:** casi todos los eventos de progreso de pruebas llevan un
campo `iteracion` (1 o 2) que **no está documentado en `api-contracts.md`**.
`iteracion=1` es la corrida original; `iteracion=2` aparece solo si Chow detectó
un atípico y el usuario decidió `"rechazar"` — en ese caso Etapa 1 se re-ejecuta
completa sobre la serie sin el dato atípico, y se re-emiten `contract_warning` /
`descriptive_stats` / `progress` / `test_result` con `iteracion: 2`. El frontend
debe usar `iteracion` para no duplicar visualmente los resultados de la primera
corrida cuando llega la segunda (reemplazar, no acumular).

### `contract_error` (bloqueante — termina el stream)
```ts
interface ContractErrorEvent {
  codigo: "CONTRACT_SERIES_TOO_SHORT" | "CONTRACT_NO_TEMPORAL_RESOLUTION";
  iteracion: number;
}
```
⚠️ **DISCREPANCIA:** `api-contracts.md` sugiere un payload con `mensaje`/`datos`/
`minimo`. El código real **solo manda `codigo` e `iteracion`** — sin mensaje
legible ni detalle numérico (cuántos datos tiene la serie, etc.). El frontend
tiene que resolver el texto para el usuario mapeando `codigo` → mensaje, en el
propio frontend (no viene del backend). Después de este evento el backend manda
`complete` con `analysis_id: null` y cierra.

### `contract_warning` (no bloqueante, se emite 0..N veces)
```ts
interface ContractWarningEvent {
  codigo: string;   // ej. "CONTRACT_LENGTH_WARNING", "CONTRACT_NEGATIVE_VALUES", etc.
  nivel: "normal";  // los warnings de contrato son siempre "normal" en la práctica
  iteracion: number;
}
```
Mismo caso: sin `mensaje`/`descripcion` en el evento — el frontend arma el texto
localmente (o lo saca del array `warnings` del evento `result_etapa1`, que sí trae
`descripcion` por warning).

### `descriptive_stats`
```ts
interface DescriptiveStatsEvent {
  n: number;
  media: number;
  mediana: number;
  desvio_estandar: number;
  coef_variacion: number;
  coef_asimetria: number;
  minimo: number;
  maximo: number;
  iteracion: number;
}
```
Nota: el core (`DescriptiveStats` en `core/types.py`) calcula más campos
(`rango`, `varianza_sesgada/no_sesgada`, `curtosis_sesgada/no_sesgada`, `suma_log`,
`mpp_m0..m3`) pero **el evento SSE no los incluye** — se pierden en la
serialización (`_serializar_etapa1`/`_emitir_resultado` sólo mapean los 8 campos
de arriba). Si el frontend necesita curtosis o los MPP en pantalla, hoy no
llegan por ningún canal — ver Gaps.

### `progress` (se emite antes de cada `test_result`)
```ts
interface ProgressEvent {
  paso: string;     // nombre de la prueba: "anderson" | "wald_wolfowitz" | "helmert" | "t_student" | "cramer" | "mann_kendall" | "kolmogorov_smirnov" | "chow"
  etapa: 1;
  completado: number; // 1..8, incluye contrato+descriptiva en el conteo
  total: 8;
  iteracion: number;
}
```
`total` está hardcodeado en 8 (contrato, descriptiva, y las 6 pruebas restantes:
anderson, wald, helmert+t_student+cramer cuentan como 3 pasos de homogeneidad,
mann_kendall+ks como 2 de tendencia, chow como 1 — la cuenta real de "pasos" no
es 1:1 con "pruebas": son 8 total sumando contrato(1) + descriptiva(1) +
anderson(1) + wald(1) + helmert(1) + t_student(1) + cramer(1) + mk(1) + ks(1) +
chow(1) = en realidad son **10 incrementos de `completado`** en el código pero
`total` queda fijo en 8 — **⚠️ el contador puede superar el `total` declarado**
(completado llega hasta 8 pruebas individuales, sin contar contrato/descriptiva
que no emiten `progress`, así que en la práctica sí cierra en 8). No usar
`total` como fuente de verdad absoluta para una barra de progreso sin probarlo
contra una corrida real — más seguro contar los `test_result` recibidos.

### `test_result` (uno por cada prueba de Etapa 1, 8 en total: anderson, wald_wolfowitz, helmert, t_student, cramer, mann_kendall, kolmogorov_smirnov, chow)
```ts
interface TestResultEvent {
  prueba: string;
  estadistico: number | null;
  valor_critico: number | null;
  veredicto: "aprobada" | "rechazada" | "no_ejecutada" | null;
  warning_codigo: string | null;
  warning_nivel: "critico" | "normal" | null;
  n1: number | null;   // solo t_student y cramer
  n2: number | null;
  valor_atipico: number | null; // solo chow, cuando detecta atípico
  iteracion: number;
}
```
⚠️ Este shape real difiere del `TestResultEvent` declarado en
`schemas/analysis.py`: el schema Pydantic **no incluye `valor_atipico` ni
`iteracion`** — ese schema quedó desactualizado y de hecho no se usa para
validar/serializar nada (ver §5). Usar el shape de arriba (extraído de
`_emitir_resultado` en `analysis_service.py`), no el de `schemas/analysis.py`.

### `outlier_detected` (pausa el stream — solo si Chow detectó un atípico)
```ts
interface OutlierDetectedEvent {
  session_id: string;
  valor_atipico: number;
}
```
El stream queda esperando hasta 300 segundos (`SESSION_TIMEOUT` en
`session_store.py`) una llamada a `POST /analysis/outlier-decision` con ese
`session_id`. Si se cumple el timeout sin decisión, el backend manda un evento
`error` (`codigo: "SESSION_TIMEOUT"`) y cierra el stream sin persistir nada.

### `result_etapa1` (una sola vez, resultado final consolidado)
```ts
interface Etapa1Result {
  contract: {
    bloqueante: boolean;       // siempre false acá (si fuera true, ya habría cortado antes)
    codigo_error: string | null;
    warnings: WarningItem[];
  };
  descriptive: {
    n: number; media: number; mediana: number; desvio_estandar: number;
    coef_variacion: number; coef_asimetria: number; minimo: number; maximo: number;
  } | null;
  independencia: TestResultDetail[];   // [anderson, wald_wolfowitz]
  homogeneidad: TestResultDetail[];    // [helmert, t_student, cramer]
  tendencia: TestResultDetail[];       // [mann_kendall, kolmogorov_smirnov]
  atipicos: TestResultDetail[];        // [chow]
  nivel_independencia: "independiente" | "dependiente" | null;
  nivel_homogeneidad: "homogeneidad_ok" | "homogeneidad_warning" | "homogeneidad_critica" | null;
  nivel_confianza: "validado" | "con_warnings" | "rechazado";
  warnings: WarningItem[];   // acumulado de TODOS los warnings del análisis, con descripcion legible
}

interface TestResultDetail {
  prueba: string;
  estadistico: number | null;
  valor_critico: number | null;
  veredicto: string | null;
  warning_codigo: string | null;
  warning_nivel: "critico" | "normal" | null;
  n1: number | null;
  n2: number | null;
  valor_atipico: number | null;
}

interface WarningItem {
  codigo: string;
  nivel: "critico" | "normal";
  descripcion: string;   // acá SÍ viene el texto legible — usar este array para mostrar mensajes, no los eventos contract_error/contract_warning sueltos
}
```
⚠️ **`nivel_confianza` nunca puede ser `"rechazado"` en este evento** — si la
serie fuera rechazada, el stream habría cortado antes en `contract_error` con
`complete{analysis_id: null}` y este evento nunca se emite. La lógica de
`ejecutar_etapa1()` en el core sí contempla `"rechazado"` como valor posible del
tipo, pero solo lo asigna en la rama bloqueante — que nunca llega a serializarse
como `result_etapa1`. Es dead code defensivo, no algo que el frontend deba
manejar acá (sí sigue aplicando para `GET /analysis/{id}` si se persistiera un
caso así, cosa que tampoco ocurre porque `_persistir` solo se llama después de
pasar el contrato).

Este es el evento con el shape más rico — conviene que sea la fuente única de
verdad para la pantalla de "Resultados de Etapa 1" (variante E), en vez de ir
acumulando los `test_result` individuales.

### `complete` (siempre el último evento del stream, salvo error/timeout)
```ts
interface CompleteEvent {
  analysis_id: string | null;  // uuid si hubo cookie válida (CU-01), null si no (CU-02)
}
```

### `error` (puede llegar en dos casos distintos)
```ts
interface ErrorEvent {
  codigo: "PARSE_ERROR" | "SESSION_TIMEOUT";
  mensaje: string;
}
```
`PARSE_ERROR` — el archivo no se pudo parsear (columna inexistente, formato
inválido, etc.) — cualquier excepción de `parse_file()` cae acá con
`str(exc)` como mensaje (mensaje de error de pandas/Python crudo, no
necesariamente legible para un usuario final — el frontend debería mostrar un
mensaje genérico propio y opcionalmente loguear el `mensaje` real).
`SESSION_TIMEOUT` — se agotaron los 300s esperando la decisión sobre el atípico.

---

## 5. Catálogo de códigos de error (confirmado contra el código real)

### Auth — todos implementados y coinciden con `api-contracts.md`
```
AUTH_EMAIL_ALREADY_REGISTERED     400
AUTH_VERIFICATION_EMAIL_FAILED    500
AUTH_INVALID_TOKEN                400
AUTH_USER_NOT_FOUND               404
AUTH_INVALID_CREDENTIALS          401
AUTH_EMAIL_NOT_VERIFIED           403
```
Estructura real del body de error, confirmada en `auth/router.py`:
```json
{"error": {"codigo": "...", "mensaje": "..."}}
```
Coincide con `ErrorResponse`/`ErrorDetail` de `schemas/common.py`, salvo que
`detalle` (el dict opcional del schema) **nunca se completa** en ningún endpoint
real hoy — siempre viene ausente o vacío.

### Contrato — bloqueantes y warnings
Los códigos existen y se generan correctamente en `core/validacion/contract.py`:
```
CONTRACT_SERIES_TOO_SHORT        (bloqueante)
CONTRACT_NO_TEMPORAL_RESOLUTION  (bloqueante)
CONTRACT_LENGTH_WARNING
CONTRACT_NEGATIVE_VALUES
CONTRACT_MISSING_VALUES
CONTRACT_DUPLICATE_TIMESTAMPS
CONTRACT_WRONG_ORDER
CONTRACT_IRREGULAR_SPACING
CONTRACT_NON_NUMERIC_VALUES
```
Pero — como se detalla en §4 — el **evento SSE no trae `descripcion`/`mensaje`**
para estos códigos individualmente (sólo en el array `warnings` del
`result_etapa1` final). El frontend necesita su propio diccionario
código→texto para mostrar algo en el momento en que llega `contract_warning`
durante el stream, si se quiere feedback inmediato antes de `result_etapa1`.

### Etapa 1 — pruebas (todos generados por el core, confirmado)
```
TEST_WARNING_TREND
TEST_WARNING_HOMOGENEITY
TEST_WARNING_SMALL_SAMPLE
TEST_WARNING_OUTLIER_DETECTED
TEST_NOT_EXECUTED_ZEROS
TEST_NOT_EXECUTED_CONDITION
```
`TEST_CRITICAL_INDEPENDENCE` y `TEST_CRITICAL_HOMOGENEITY` — no se generan como
`WarningItem` con ese código exacto en el código actual; el nivel crítico se
refleja en `nivel_independencia`/`nivel_homogeneidad` (`"dependiente"` /
`"homogeneidad_critica"`) y en `warning_nivel: "critico"` dentro del
`TestResult` correspondiente (Anderson o Cramer), no como un código de warning
adicional separado. `TEST_OUTLIER_REJECTED_BY_USER` /
`TEST_OUTLIER_ACCEPTED_BY_USER` tampoco se emiten como códigos — la decisión del
usuario queda en el campo `decisiones.chow.accion` del análisis persistido
(`"rechazar"`/`"aceptar"`), no como un `WarningItem` nuevo.

### Etapa 2 — catálogo entero no aplicable todavía
```
DIST_NOT_APPLICABLE / DIST_NOT_CONVERGED / DIST_HIGH_EEA / DIST_DISABLED_ZEROS
```
Existen como constantes en `core/etapa2/types.py` (motor interno), pero como no
hay ningún endpoint que exponga Etapa 2 (§3), estos códigos no salen del core
todavía por ningún canal HTTP.

---

## 6. Gaps / a mockear en el frontend

Lista concreta de lo que el frontend debe tratar como **no disponible** y
mockear con datos de ejemplo, marcando visualmente que es una función pendiente
si corresponde:

1. **`POST /api/v1/analysis/design-events`** — no implementado. Necesario para
   la pantalla "Eventos de diseño" (variante B). Mockear con un ranking/eventos
   de ejemplo basados en el shape de `api-contracts.md`.
2. **Etapa 2 completa en el stream** — el campo `etapas` del form se ignora;
   nunca se emite `result_etapa2_ranking`; nunca se persiste `etapa2` (siempre
   `null` en `GET /analysis/{id}`). La pantalla "Ranking de distribuciones"
   (variante D) no tiene datos reales para consumir todavía.
3. **`GET /api/v1/export/{id}`** (PDF) — no implementado. Botón de exportación
   sin backend.
4. **`POST /api/v1/validate/`** (CU-03) y auth por `X-API-Key` — no
   implementados. Fuera de alcance de esta fase según `sprint.md`.
5. **Partición de Cramer personalizada** — el campo existe en el form pero está
   roto en el wiring real (§3). Tratar la opción "Personalizada" de la variante
   H como deshabilitada/mock hasta que se corrija en el backend, o coordinarlo
   como fix de backend antes de habilitar esa UI.
6. **Mensajes legibles en `contract_error`/`contract_warning`/`test_result`
   durante el stream** — el backend no los manda; el frontend necesita su
   propio diccionario código→texto en español para el feedback en vivo (sí
   están disponibles al final, en el array `warnings` de `result_etapa1`).
7. **Campos descriptivos extendidos** (`rango`, `curtosis_sesgada/no_sesgada`,
   `varianza_sesgada/no_sesgada`, `suma_log`, `mpp_m0..m3`) — calculados en el
   core pero no serializados a ningún evento SSE ni a lo persistido. Si el
   diseño de la pantalla de resultados los necesita, es un gap de backend, no
   solo de frontend.
8. **Paginación de `GET /history/`** — no existe, devuelve todo el historial
   del usuario en un array plano. Para un usuario con muchos análisis, el
   frontend debe paginar/filtrar client-side o pedir paginación al backend.
9. **Los schemas Pydantic `AnalysisRequest`, `ProgressEvent`, `TestResultEvent`,
   `ContractProblem`** en `schemas/analysis.py` están declarados pero
   **desconectados** de los endpoints reales — no confiar en ellos como fuente
   de verdad del contrato; usar los shapes de este documento (extraídos de
   `analysis_service.py` y `api/v1/analysis.py` directamente).

---

## 7. Resumen ejecutivo para quien arranca el frontend

- Base URL backend: `http://localhost:8000`, prefijo `/api/v1` (auth incluida).
- Todo request debe ir con `credentials: "include"`/`withCredentials: true`.
- CU-01 vs CU-02 se decide client-side simplemente por si hay o no una sesión
  logueada — el mismo `POST /analysis/stream` sirve para ambos.
- El modo (paso a paso/experto) se manda una vez en el form de `/stream` y no
  se puede cambiar a mitad de análisis (coincide con la Decisión A de
  `frontend-design/metis-wireframes-fase1-decisiones.md`).
- Etapa 2 (ranking, eventos de diseño, exportación PDF, CU-03) es **mock puro**
  en esta fase — el motor de cálculo existe pero no está expuesto por HTTP.
- El shape real de los eventos SSE está en §4 de este documento — no coincide
  1:1 con `api-contracts.md` en varios detalles menores (campos `iteracion`,
  ausencia de `mensaje`/`descripcion` en eventos intermedios, nombres de campo
  entre `valor_atipico`/`dato_atipico`). Priorizar este documento sobre
  `api-contracts.md` para lo que ya está implementado; usar `api-contracts.md`
  como aspiracional para lo que falta (Etapa 2, export, CU-03).
