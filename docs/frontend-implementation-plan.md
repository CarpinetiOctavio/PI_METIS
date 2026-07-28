# Plan de Implementación — Frontend METIS

**Propósito.** Plan de trabajo para construir el frontend de METIS (React + TypeScript,
tema visual **"Instrumento"**) contra el backend REAL descrito en
[`docs/frontend-integration.md`](./frontend-integration.md). Este documento **no contiene
código de producción** — describe qué construir, en qué orden, con qué criterios de "hecho"
y qué se prueba contra el backend real vs. qué queda mockeado.

**Fecha.** 22/07/2026 · Autores: Kevin / Octavio.
**Depende de:**
- [`docs/frontend-integration.md`](./frontend-integration.md) — contrato REAL del backend (fuente de verdad para lo implementado).
- `frontend/frontend-design/metis-wireframes-fase1-decisiones.md` — variantes elegidas (★) y Decisiones A / C / D.
- `frontend/frontend-design/metis-prototipo-fase3.html` — identidad visual; tema "Instrumento" (claro y oscuro).
- `.claude/rules/` (architecture, constraints, api-contracts, statistical-pipeline, sprint) y `CLAUDE.md`.

**Regla de precedencia.** Ante conflicto entre `api-contracts.md` y `frontend-integration.md`
para algo YA implementado, gana `frontend-integration.md`. `api-contracts.md` se usa como
referencia aspiracional para lo que todavía no existe (Etapa 2, export, CU-03).

---

## 0. Corrección técnica central — SSE sobre POST

`POST /api/v1/analysis/stream` es **multipart/form-data** (sube un archivo). El `EventSource`
nativo del navegador **solo soporta GET y no permite headers ni body**, por lo que **no se puede
usar para este stream**. Todo el consumo de SSE se implementa con:

- **`fetch()` + `ReadableStream`** (`response.body.getReader()`), decodificando UTF-8 y parseando
  los frames SSE a mano (`event:` / `data:` separados por `\n\n`), **o**
- **`@microsoft/fetch-event-source`** — librería que encapsula exactamente ese patrón (fetch con
  body + parseo SSE + reconexión configurable). **Decisión tomada (22/07/2026):** se usa
  `@microsoft/fetch-event-source` para no reimplementar el buffering de frames. El reader manual
  queda como fallback documentado (§2.3) por si se decide eliminar la dependencia más adelante.

Esta decisión atraviesa toda la capa de streaming — ver §2.3 y la lista de riesgos §9.

---

## 1. Tooling y estructura de carpetas

### 1.1 Stack de tooling

| Herramienta | Elección | Notas |
|---|---|---|
| Bundler/dev server | **Vite** | `.env.example` ya asume puerto **5173** (Vite), y `FRONTEND_ORIGIN` está seteado a `http://localhost:5173`. Cambiar el puerto obliga a cambiar `FRONTEND_ORIGIN` en el `.env` del backend. |
| Framework | React 18 + TypeScript (strict) | Stack fijado en `CLAUDE.md` / `constraints.md` — no negociable. |
| Ruteo | **React Router v6** | SPA con rutas por pantalla; guards de auth (§3). |
| Estado servidor | **TanStack Query** (react-query) para REST (auth, history) | El stream SSE NO usa react-query — es un hook propio (§2.3). Query cubre `/me`, `/history`, `/analysis/{id}`. |
| Estado UI | Context API (auth, tema, modo de análisis) | No hace falta Redux para este alcance. |
| Estilos | **CSS variables + CSS Modules** (o vanilla-extract) | Los tokens del tema son CSS vars (§4); componentes toman color de las vars. Evitar librerías de UI pesadas que impongan su propio look (choca con "Instrumento"). |
| Linting | **ESLint** (config del repo) + Prettier | `constraints.md` exige ESLint; alinear con `cd frontend && npm run lint` que ya está referenciado en `CLAUDE.md`. |
| Testing | Vitest + React Testing Library; MSW para mocks de red | Ver §9. |

### 1.2 Estructura de carpetas propuesta (`frontend/`)

> Hoy `frontend/` solo contiene `frontend-design/` (wireframes/identidad, sin proyecto React).
> El scaffold de Vite convive con esa carpeta sin tocarla.

```
frontend/
├── frontend-design/            # EXISTENTE — no tocar (wireframes, identidad, prototipo)
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts              # proxy /api → localhost:8000 en dev (alternativa a CORS, ver §3.4)
├── .eslintrc.cjs               # alineado con el ESLint del repo
├── public/
└── src/
    ├── main.tsx
    ├── App.tsx                 # router + providers (Auth, Theme, Query)
    ├── routes/                 # una carpeta por pantalla (las 8 ★ + auth)
    │   ├── entry/              # 1. Puerta de entrada (login/registro/anónimo) — var. A
    │   ├── config/            # 2. Carga y configuración — var. H
    │   ├── stream/            # 3. Análisis en vivo — var. A
    │   ├── results/           # 4. Resultados Etapa 1 — var. E (+ acordeón var. D)
    │   ├── ranking/           # 6. Ranking distribuciones — var. D (MOCK)
    │   ├── design-events/     # 7. Eventos de diseño — var. B (MOCK)
    │   └── history/           # 8. Historial — var. B
    ├── api/
    │   ├── types.ts           # interfaces 1:1 con frontend-integration.md (§2.1)
    │   ├── client.ts          # fetch wrapper con credentials:'include' (§2.2)
    │   ├── auth.ts            # register/verify/login/logout/me
    │   ├── analysis.ts        # get_analysis, outlier-decision
    │   ├── history.ts        # list/get history
    │   └── sse.ts            # hook useAnalysisStream (SSE-sobre-fetch) (§2.3)
    ├── auth/
    │   ├── AuthProvider.tsx   # context + estado de sesión (§3)
    │   ├── useAuth.ts
    │   └── guards.tsx         # RequireAuth, RedirectIfAuthed
    ├── theme/
    │   ├── tokens.instrumento.css   # CSS vars claro/oscuro (§4)
    │   ├── tokens.ts               # mismos tokens como objeto TS tipado
    │   ├── ThemeProvider.tsx       # toggle claro/oscuro + persistencia
    │   └── global.css              # tratamientos "Instrumento" (grid, HUD, glow)
    ├── mocks/                 # capa de datos falsos para lo NO implementado (§6)
    │   ├── etapa2.mock.ts
    │   ├── designEvents.mock.ts
    │   └── PendingBadge.tsx   # marca visual "pendiente / mock"
    ├── i18n/
    │   └── errors.es.ts       # diccionario código→texto español (§7)
    └── components/            # UI compartida (Card HUD, TestRow, KPI, StatusPill, etc.)
```

---

## 2. Capa de API tipada

### 2.1 `types.ts` — derivado de `frontend-integration.md`

Interfaces 1:1 con el contrato real. Fuente: §3 y §4 de `frontend-integration.md`. Extracto de
las clave (el archivo completo las incluye todas):

```ts
// --- Auth ---
export interface RegisterRequest { email: string; password: string; nombre?: string | null; }
export interface LoginRequest { email: string; password: string; }
export interface VerifyRequest { token: string; }
export interface UserMe { id: string; email: string; nombre: string | null; email_verified: boolean; }

// --- Análisis (form multipart, todos string salvo el File) ---
export type TipoVariable = "caudal_precipitacion" | "otro";
export type Modo = "paso_a_paso" | "experto";
export interface AnalysisStreamForm {
  archivo: File;
  columna_x: string;
  columna_y: string;
  tipo_variable: TipoVariable;
  etapas?: string;            // IGNORADO por el backend hoy — Etapa 2 no corre
  modo?: Modo;                // solo afecta lo persistido, no el output del stream
  cramer_particion?: "default"; // custom ROTO en el wiring — ver §6
}

// --- Outlier decision ---
export interface OutlierDecisionRequest {
  session_id: string;
  decision: "rechazar" | "aceptar";
  dato_atipico: number;       // OJO: en el evento SSE se llama valor_atipico
}
export interface OutlierDecisionResponse { ok: boolean; pipeline_continua: boolean; }

// --- Etapa1Result (shape del evento result_etapa1 y de GET /analysis/{id}) ---
export type Veredicto = "aprobada" | "rechazada" | "no_ejecutada";
export type WarningNivel = "critico" | "normal";
export interface WarningItem { codigo: string; nivel: WarningNivel; descripcion: string; }
export interface TestResultDetail {
  prueba: string;
  estadistico: number | null;
  valor_critico: number | null;
  veredicto: Veredicto | null;
  warning_codigo: string | null;
  warning_nivel: WarningNivel | null;
  n1: number | null;
  n2: number | null;
  valor_atipico: number | null;
}
export interface Etapa1Result {
  contract: { bloqueante: boolean; codigo_error: string | null; warnings: WarningItem[]; };
  descriptive: DescriptiveStats | null;
  independencia: TestResultDetail[];   // [anderson, wald_wolfowitz]
  homogeneidad: TestResultDetail[];    // [helmert, t_student, cramer]
  tendencia: TestResultDetail[];       // [mann_kendall, kolmogorov_smirnov]
  atipicos: TestResultDetail[];        // [chow]
  nivel_independencia: "independiente" | "dependiente" | null;
  nivel_homogeneidad: "homogeneidad_ok" | "homogeneidad_warning" | "homogeneidad_critica" | null;
  nivel_confianza: "validado" | "con_warnings" | "rechazado"; // "rechazado" nunca llega en este evento
  warnings: WarningItem[];   // acumulado con descripcion legible — fuente única de texto
}

// --- Eventos SSE (union discriminada por `type`) ---
export type SseEvent =
  | { type: "contract_error"; codigo: string; iteracion: number }
  | { type: "contract_warning"; codigo: string; nivel: "normal"; iteracion: number }
  | { type: "descriptive_stats"; iteracion: number } & DescriptiveStats
  | { type: "progress"; paso: string; etapa: 1; completado: number; total: number; iteracion: number }
  | { type: "test_result"; iteracion: number } & TestResultDetail & { prueba: string }
  | { type: "outlier_detected"; session_id: string; valor_atipico: number }
  | { type: "result_etapa1"; result: Etapa1Result }   // envuelto al parsear (data = Etapa1Result crudo)
  | { type: "complete"; analysis_id: string | null }
  | { type: "error"; codigo: "PARSE_ERROR" | "SESSION_TIMEOUT"; mensaje: string };
```

> Nota: los schemas Pydantic de `metis/schemas/analysis.py` NO son fuente de verdad (están
> desconectados de los endpoints — ver §5/§6 de `frontend-integration.md`). `types.ts` se deriva
> de los shapes reales documentados, no de esos schemas.

### 2.2 `client.ts` — cliente fetch

- Base URL desde `import.meta.env.VITE_API_BASE` (default `http://localhost:8000`).
- **Todas** las requests con `credentials: "include"` — sin esto la cookie `access_token` no viaja
  (§4/§2 de `frontend-integration.md`).
- Helper que normaliza el body de error real `{ error: { codigo, mensaje } }` a un `ApiError`
  tipado (con `status` HTTP + `codigo` del catálogo). Manejar el caso 422 de Pydantic aparte
  (validación de email/password en register → el body tiene forma distinta, la de FastAPI).
- Sin `Authorization` header — la auth es 100% cookie.

### 2.3 `useAnalysisStream` — hook de SSE-sobre-fetch

Responsabilidad: correr un análisis de Etapa 1 y exponer su progreso como estado React.

**Firma conceptual:**
```ts
function useAnalysisStream(): {
  start: (form: AnalysisStreamForm) => void;
  state: {
    fase: "idle" | "streaming" | "waiting_outlier" | "done" | "error";
    contractWarnings: WarningItem[];   // por código, dedupe por iteracion
    descriptive: DescriptiveStats | null;
    tests: Record<string, TestResultDetail>;  // key = prueba, sobrescrita por iteracion mayor
    progress: { completado: number; total: number };
    outlier: { session_id: string; valor_atipico: number } | null;
    result: Etapa1Result | null;
    analysisId: string | null;
    error: { codigo: string; mensaje: string } | null;
  };
  resolveOutlier: (decision: "rechazar" | "aceptar") => Promise<void>;
  abort: () => void;
}
```

**Mecánica (con `@microsoft/fetch-event-source` — decisión tomada, §0):**

1. `start()` arma el `FormData` (archivo + campos) y abre **una** conexión `fetch` POST a
   `/api/v1/analysis/stream` con `credentials:"include"`. Se mantiene un `AbortController` para
   `abort()`.
2. Cada frame SSE se parsea a un `SseEvent` y se reduce sobre el estado:
   - `contract_error` → `fase="error"` (mostrar mensaje del diccionario §7); el server manda
     luego `complete{analysis_id:null}` y cierra.
   - `contract_warning` → acumular (dedupe por `codigo`).
   - `descriptive_stats` → set `descriptive`.
   - `progress` → set `progress` (**no** confiar en `total` para el %; ver §9 — mejor contar
     `test_result` recibidos, se esperan 8).
   - `test_result` → `tests[prueba] = detalle`. **Manejo de `iteracion`:** si llega un
     `test_result` con `iteracion` mayor al ya visto para esa prueba, **reemplaza** (no acumula).
     Esto ocurre en la re-ejecución tras rechazar un atípico.
   - `outlier_detected` → `fase="waiting_outlier"`, guardar `session_id` + `valor_atipico`,
     **mantener la conexión fetch abierta** (el server está bloqueado esperando, hasta 300 s).
   - `result_etapa1` → set `result` (fuente única para la pantalla de resultados).
   - `complete` → `fase="done"`, set `analysisId`.
   - `error` (`SESSION_TIMEOUT` / `PARSE_ERROR`) → `fase="error"`.
3. **Pausa/reanudación por atípico:** cuando `fase==="waiting_outlier"`, la UI muestra el modal
   (§5). `resolveOutlier(decision)` hace un `POST /api/v1/analysis/outlier-decision`
   **por separado** (otra request), mandando `{ session_id, decision, dato_atipico: valor_atipico }`.
   Ese POST desbloquea el `asyncio.Event` del server, que **sigue emitiendo por la MISMA conexión
   fetch abierta** (frames con `iteracion:2` si la decisión fue `"rechazar"`). El reader del paso 2
   los sigue consumiendo sin reabrir nada.
4. **Timeout:** si pasan ~300 s sin decisión, el server manda `error{SESSION_TIMEOUT}` y cierra.
   La UI debe reflejarlo (no dejar el modal colgado). Considerar un contador visible en el modal.
5. `abort()` cancela el `AbortController` (usuario cancela el análisis / desmonta el componente).

**Puntos finos:** decodificar con `TextDecoder` acumulando en buffer (un frame puede partirse
entre chunks); respetar `prefers-reduced-motion` en las animaciones de "contador que sube".

---

## 3. Auth

### 3.1 AuthProvider

- Al montar, `GET /api/v1/auth/me` (react-query). 200 → sesión CU-01 activa; 401 → anónimo.
- Expone `{ user: UserMe | null, isAuthed: boolean, isLoading, login, logout, refetch }`.
- `login()` → `POST /login` (setea cookie) → invalida/`refetch` de `/me`.
- `logout()` → `POST /logout` (borra cookie) → limpia el cache y vuelve a estado anónimo.
- No se guarda nada del JWT en JS (la cookie es HttpOnly; no es accesible ni necesario).

### 3.2 Determinación CU-01 vs CU-02 (Decisiones C y D)

- **Puerta de entrada (pantalla 1, var. A):** login / registro / **"entrar como anónimo"**.
  "Anónimo" no llama a ningún endpoint — simplemente marca un flag de sesión anónima en el
  ThemeProvider/AuthProvider y navega a config.
- **CU-01 (docencia)** = `isAuthed === true`. Habilita: historial, persistencia, exportación
  (mock), y **elección de modo** (paso a paso / experto) en config.
- **CU-02 (anónimo)** = sin sesión. Por **Decisión D**, el anónimo usa **siempre la UI Experto**:
  sin selector de modo (se fija `modo="experto"` internamente), sin historial, sin exportar. Las
  pantallas con "desarrollo paso a paso" colapsan a "solo resultados".
- La distinción **no** se resuelve por ruta: la misma pantalla de config/stream/resultados se
  renderiza distinto según `isAuthed` + el modo elegido, igual que el backend usa la misma ruta
  `/analysis/stream` con o sin cookie.

### 3.3 Guards

- `RequireAuth` — envuelve `history/` y el detalle `analysis/{id}`. Si `!isAuthed` → redirige a la
  puerta de entrada (esas rutas del backend responden 401 sin cookie).
- `RedirectIfAuthed` — en la puerta de entrada, si ya hay sesión, saltear a config.
- `stream`, `config`, `results` son accesibles en ambos modos (anónimo y docencia).

### 3.4 Workaround de desarrollo — 500 de `register` sin SMTP

Sin `SMTP_*` configurado, `POST /register` devuelve **500 `AUTH_VERIFICATION_EMAIL_FAILED`**
(§2 de `frontend-integration.md`). Para no bloquear el desarrollo de la UI de auth cuando no hay
App Password:

- **Opción A (recomendada, sin tocar backend):** correr el backend con `auth/email.py` mockeado
  localmente (el propio backend ya tiene precedente de mock — ver `sprint.md`), o setear SMTP real.
  El frontend no necesita workaround propio.
- **Opción B (solo frontend, modo dev):** detectar el `codigo === "AUTH_VERIFICATION_EMAIL_FAILED"`
  y, **bajo `import.meta.env.DEV`**, mostrar un aviso "modo dev: SMTP no configurado — pedí el
  token de verificación por consola del backend" en vez de un error rojo bloqueante. El token de
  verificación se obtiene de los logs del backend (`grep` del token, ver `sprint.md`).
- **Importante:** el flujo de `verify` **sí** funciona sin SMTP si se consigue el token de los
  logs — el token vive en memoria del proceso, no se manda solo por mail. Documentar en el README
  del frontend cómo obtenerlo en dev.

> El link de verificación que arma el backend apunta a `${FRONTEND_URL}/auth/verify?token=...`
> (`auth/email.py`). El frontend **debe** exponer esa ruta `/auth/verify` que lea el `token` del
> query string y llame a `POST /api/v1/auth/verify`.

---

## 4. Theming — tokens "Instrumento"

Extraídos de `metis-prototipo-fase3.html` (objeto `THEMES.instrumento`). Se materializan como
CSS vars globales (mismos nombres que usa el prototipo, para trazabilidad) y como objeto TS.

### 4.1 `tokens.instrumento.css`

```css
:root[data-theme="instrumento"][data-mode="light"] {
  --bg:#F3F6F8; --surf:#FFFFFF; --surf2:#E9EEF2; --ink:#0B0E12; --mut:#5B6672; --fnt:#9AA5B1;
  --line:#DEE5EB; --line-strong:#C6D0D8; --acc:#0E7490; --acc-soft:#D4EEF3; --on-acc:#FFFFFF;
  --acc2:#4D7C0F; --ok:#128A4E; --warn:#B5791A; --crit:#C24444;
}
:root[data-theme="instrumento"][data-mode="dark"] {
  --bg:#090C10; --surf:#12171F; --surf2:#191F29; --ink:#E6EDF3; --mut:#8A97A6; --fnt:#566270;
  --line:#212A36; --line-strong:#33404E; --acc:#22D3EE; --acc-soft:#0C2A33; --on-acc:#04252B;
  --acc2:#C6F84E; --ok:#35D07A; --warn:#F4B740; --crit:#FF6A6A;
}
:root[data-theme="instrumento"] {
  --f-head:'JetBrains Mono',monospace; --f-body:'JetBrains Mono',monospace; --f-mono:'JetBrains Mono',monospace;
  --r-sm:3px; --r-md:4px;
}
```

### 4.2 Tratamientos "Instrumento" (de `global.css`)

Del prototipo (líneas 141-152): **retícula técnica** de fondo (grid 28px), **esquinas tipo
corchete (HUD)** en las tarjetas (`::before`/`::after` con borde de acento), **glow de señal** en
botones primarios, **badge que pulsa** ("REC" en vivo), y en **modo oscuro**: **scanlines CRT**
suaves + **text-shadow neón** en las cifras (KPI y estadísticos). Aplicar con moderación
(riesgo "demasiado de programador" señalado en Fase 2 — mitigar reservando el glow/scanlines al
stream en vivo y a las cifras, no a toda la app).

### 4.3 Aplicación global

- `ThemeProvider` setea `data-theme="instrumento"` fijo y togglea `data-mode` (light/dark) en
  `:root`, persistiendo en `localStorage` y respetando `prefers-color-scheme` como default.
- Números (estadísticos, valores críticos, EEA, cuantiles) **siempre** en `--f-mono` (JetBrains
  Mono) — decisión transversal de Fase 2 ("números como ciudadanos de primera clase"). En
  Instrumento todo es mono, pero mantener la clase semántica `.num` para que sobreviva si algún
  día se cambia de tema.
- **Accesibilidad (Fase 2):** el estado de una prueba nunca se comunica solo por color — siempre
  con etiqueta textual (`aprobada`/`warning`/`crítico`). Contraste texto ≥ 4.5:1.

---

## 5. Mapa pantalla → variante + flujo

Las 8 pantallas con su variante elegida (★) de `metis-wireframes-fase1-decisiones.md`:

| # | Pantalla | Ruta | Variante ★ | Backend | Notas de implementación |
|---|----------|------|-----------|---------|-------------------------|
| 1 | Puerta de entrada | `/` | **A** (login + botón anónimo) | Auth real | Decisión C. Botón "entrar como anónimo" → flag anónimo, sin endpoint. Ruta `/auth/verify` aparte para el link de mail. |
| 2 | Carga y configuración | `/config` | **H** (2 col + modo + params) | — | Decisión A: toggle **modo** (paso_a_paso/experto) elegido acá, **una vez**, inmutable. En anónimo el toggle se reemplaza por etiqueta "solo resultados" (Decisión D). Partición Cramer custom = **MOCK/deshabilitada** (§6). |
| 3 | Análisis en vivo | `/stream` | **A** (timeline vertical) | SSE real (Etapa 1) | Pasos completados **clickeables** → despliegan su `test_result`. Consume `useAnalysisStream` (§2.3). Modal de atípico (abajo). |
| 4 | Resultados Etapa 1 | `/results` | **E** (resumen + tablero) | `result_etapa1` real | Fuente única: el objeto `Etapa1Result`. Muestra `nivel_confianza`, niveles de independencia/homogeneidad, tabla de pruebas, warnings con `descripcion`. |
| 5 | Paso a paso vs Experto | (dentro de `/results`) | **D** (acordeón de pasos) | — | Decisión A: **no** es pantalla aparte conmutable; se renderiza según el `modo` ya elegido. Paso a paso = acordeón con fórmulas; Experto/anónimo = solo resultados. |
| 6 | Ranking de distribuciones | `/ranking` | **D** (tarjetas + toggle cal/hidro) | **MOCK** | Etapa 2 no expuesta. Datos falsos + `PendingBadge`. Toggle año calendario/hidrológico obligatorio. **Nunca** etiquetar una distribución como "óptima/ganadora" (constraints.md). |
| 7 | Eventos de diseño | `/design-events` | **B** (foco en período) | **MOCK** | `design-events` no implementado. Todo mock. |
| 8 | Historial | `/history` | **B** (tarjetas resumen) | `/history` real | Solo CU-01 (`RequireAuth`). Sin paginación en backend — paginar client-side (§6/§9). |

### 5.1 Decisión A — modo elegido una vez define la UI de las etapas

- El `modo` se guarda en un context (`AnalysisConfigProvider`) al confirmar la config, y es
  **inmutable** durante el análisis. Las pantallas 3/4/5 leen ese modo para decidir su presentación
  (con desarrollo de fórmulas vs. solo resultados). No hay toggle de modo por paso.
- Coherente con el backend: `modo` viaja en el form de `/stream` (aunque hoy solo afecta lo
  persistido, la UI ya respeta el modo localmente).

### 5.2 Decisión D — anónimo = UI Experto

- En anónimo se fuerza `modo="experto"`: sin acordeón de fórmulas, sin historial, sin exportar.
- Solo hay **dos presentaciones reales**: *con desarrollo* (docencia + paso a paso) y *solo
  resultados* (docencia experto ≡ anónimo).

### 5.3 Modal de decisión de atípico (Chow)

- Se dispara cuando `useAnalysisStream` entra en `fase="waiting_outlier"`.
- Muestra el `valor_atipico` recibido y dos acciones: **Rechazar** / **Aceptar**.
- Al elegir → `resolveOutlier(decision)` (§2.3, paso 3). Mientras se espera, el timeline queda en
  pausa visible. Incluir un contador (300 s) para que el usuario sepa que hay límite.
- Aplica a CU-01 y CU-02 por igual (ambos pausan). Tras `"rechazar"`, la UI debe **reemplazar** los
  resultados de `iteracion:1` con los de `iteracion:2` (no mostrar ambos).

---

## 6. Capa de mocks (lo NO implementado)

Todo lo de la lista "Gaps" de `frontend-integration.md` §6 se implementa con datos falsos y una
**marca visual `PendingBadge`** ("pendiente · datos de ejemplo") clara, para que en la defensa
quede explícito qué es real y qué es maqueta.

| Gap | Cómo se mockea | Marca |
|---|---|---|
| Ranking de distribuciones (Etapa 2) | `mocks/etapa2.mock.ts` con un ranking por EEA de ejemplo, shape según `api-contracts.md`. | `PendingBadge` en la pantalla + tooltip "Etapa 2 no expuesta por API todavía". |
| `design-events` | `mocks/designEvents.mock.ts` con eventos de diseño de ejemplo por período de retorno. | `PendingBadge`. |
| Exportación PDF (`/export/{id}`) | Botón visible pero deshabilitado o que abre un modal "próximamente". | Estado `disabled` + nota. |
| CU-03 (`/validate/`, X-API-Key) | Fuera de alcance de esta fase (sprint.md). No se construye UI. | — |
| `cramer_particion` custom | Opción "Personalizada" en config **deshabilitada** (roto en el wiring backend, §3 de integration). Solo "default" activo. | `PendingBadge` en la opción. |
| Campos descriptivos extendidos (curtosis, MPP, rango, etc.) | No llegan por SSE. No mostrarlos, o mostrarlos como "—" con nota. Es gap de backend. | Nota si se decide exponerlos. |

**Estrategia de mock — decisión tomada (22/07/2026): MSW (Mock Service Worker).** Los handlers
de MSW interceptan las rutas no implementadas (`/api/v1/analysis/design-events`, y el ranking de
Etapa 2 cuando corresponda) y sirven los datos de `mocks/*.mock.ts` como si fueran el backend. Los
componentes llaman al cliente real (§2.2) sin saber que la respuesta es falsa — el día que el
endpoint real exista, **solo se quita el handler de MSW**, sin tocar componentes ni cliente. MSW se
reutiliza además en los tests (§9.1), unificando el mock de dev y el de test en un solo lugar.

---

## 7. Diccionario de errores código → texto (español)

`i18n/errors.es.ts` — mapa único de todos los códigos del catálogo a texto legible, porque el
backend **no manda mensaje legible en los eventos SSE intermedios** (§4/§5 de integration). Cubre
tanto los eventos en vivo como los errores HTTP de auth.

```ts
export const ERROR_TEXT: Record<string, string> = {
  // Contrato — bloqueantes
  CONTRACT_SERIES_TOO_SHORT: "La serie tiene menos de 10 datos. No se puede analizar.",
  CONTRACT_NO_TEMPORAL_RESOLUTION: "No se pudo determinar la resolución temporal de la serie.",
  // Contrato — warnings
  CONTRACT_LENGTH_WARNING: "Serie con menos de 30 datos — los resultados no son certificables.",
  CONTRACT_NEGATIVE_VALUES: "Hay valores negativos en una serie de caudal/precipitación.",
  CONTRACT_MISSING_VALUES: "Hay valores faltantes o celdas vacías.",
  CONTRACT_DUPLICATE_TIMESTAMPS: "Se detectaron duplicados en el eje temporal.",
  CONTRACT_WRONG_ORDER: "La serie no está en orden cronológico.",
  CONTRACT_IRREGULAR_SPACING: "El espaciado temporal es irregular.",
  CONTRACT_NON_NUMERIC_VALUES: "Hay valores no numéricos mezclados en la serie.",
  // Etapa 1 — pruebas
  TEST_WARNING_TREND: "Se detectó una posible tendencia (Mann-Kendall o Kolmogorov-Smirnov).",
  TEST_WARNING_HOMOGENEITY: "Helmert o t de Student rechazaron homogeneidad.",
  TEST_WARNING_SMALL_SAMPLE: "Muestra chica (n ≤ 40) — Wald-Wolfowitz se ejecuta con advertencia.",
  TEST_WARNING_OUTLIER_DETECTED: "Chow detectó un dato atípico — se requiere tu decisión.",
  TEST_NOT_EXECUTED_ZEROS: "Chow no se ejecutó: hay ceros en la serie de caudal/precipitación.",
  TEST_NOT_EXECUTED_CONDITION: "La prueba no se ejecutó: no se cumple una condición previa.",
  // Auth (errores HTTP)
  AUTH_EMAIL_ALREADY_REGISTERED: "Ese email ya está registrado.",
  AUTH_VERIFICATION_EMAIL_FAILED: "No pudimos enviar el mail de verificación. Probá de nuevo en unos minutos.",
  AUTH_INVALID_TOKEN: "El link de verificación es inválido o expiró.",
  AUTH_USER_NOT_FOUND: "No encontramos el usuario.",
  AUTH_INVALID_CREDENTIALS: "Email o contraseña incorrectos.",
  AUTH_EMAIL_NOT_VERIFIED: "Verificá tu email antes de iniciar sesión.",
  // Stream
  PARSE_ERROR: "No se pudo leer el archivo. Revisá el formato y las columnas seleccionadas.",
  SESSION_TIMEOUT: "Se agotó el tiempo de espera para decidir sobre el dato atípico.",
};
```

Los niveles crítico/normal se derivan de `warning_nivel` (en `test_result`/`result_etapa1`) y de
`nivel_independencia`/`nivel_homogeneidad`, no de un código separado (§5 de integration — no existen
`TEST_CRITICAL_*` como códigos emitidos).

---

## 8. Fases de entrega incremental

Cada fase termina con un criterio de "hecho" verificable. Se marca qué se prueba **contra el
backend real** (Etapa 1) y qué queda **mockeado**.

### Fase 0 — Scaffold + theming
- Vite + React + TS (strict) en `frontend/`, ESLint del repo, React Router, providers base.
- `theme/` con tokens Instrumento (claro/oscuro), toggle funcionando, tratamientos globales.
- Layout base (barra superior con logo METIS, toggle claro/oscuro, badge de modo).
- **Hecho si:** `npm run dev` levanta en 5173; `npm run lint` limpio; toggle claro/oscuro cambia
  todos los tokens; `GET /ping` alcanzable desde el front (prueba de conectividad + CORS).

### Fase 1 — Auth end-to-end (BACKEND REAL)
- Puerta de entrada (var. A), `/auth/verify`, AuthProvider, guards, `login/logout/me`, workaround
  dev del 500 de register (§3.4).
- **Hecho si:** registro → verificación (token de logs en dev) → login → `/me` 200 con cookie →
  logout → `/me` 401. Rutas protegidas redirigen sin sesión. Probado contra el backend real.

### Fase 2 — Config + stream Etapa 1 (BACKEND REAL)
- Pantalla config (var. H) con toggle de modo (Decisión A) y anónimo=experto (Decisión D).
- `useAnalysisStream` (SSE-sobre-fetch), pantalla stream (var. A, pasos clickeables), modal de
  atípico + reanudación, diccionario de errores en vivo.
- **Hecho si:** subir un CSV real corre Etapa 1 completa; los 8 `test_result` aparecen; un caso con
  atípico pausa, el modal decide, y `"rechazar"` re-ejecuta mostrando `iteracion:2` (reemplazo, no
  duplicado); un caso bloqueante (<10 datos) muestra `contract_error` legible. Probado contra el
  backend real.

### Fase 3 — Resultados Etapa 1 (BACKEND REAL)
- Pantalla resultados (var. E) desde `result_etapa1`; acordeón paso a paso (var. D) según modo.
- **Hecho si:** los tres modos de presentación (docencia paso a paso / docencia experto / anónimo)
  renderizan correctamente el mismo `Etapa1Result`; warnings con `descripcion`; niveles de
  confianza/independencia/homogeneidad visibles con etiqueta (no solo color).

### Fase 4 — Historial (BACKEND REAL, solo CU-01)
- Pantalla historial (var. B) con `/history`; detalle con `/analysis/{id}`.
- **Hecho si:** un usuario logueado ve sus análisis persistidos; el detalle carga `etapa1` real;
  anónimo no accede (guard). Paginación client-side sobre el array plano.

### Fase 5 — Mocks de Etapa 2 (MOCKEADO)
- Ranking (var. D) + eventos de diseño (var. B) + botón export, todos con `PendingBadge`.
- **Hecho si:** las pantallas renderizan con datos de ejemplo y marca visual de "pendiente";
  ninguna distribución se etiqueta como "óptima"; toggle calendario/hidrológico presente.

### Fase 6 — Pulido, a11y y testing
- `prefers-reduced-motion`, contraste, foco/teclado en el modal, estados de carga/error.
- Suite de tests (§9). **Hecho si:** Vitest verde, lint limpio, revisión de accesibilidad básica
  pasada, flujo CU-01 y CU-02 recorridos manualmente contra el backend real.

---

## 9. Testing y riesgos de integración

### 9.1 Estrategia de testing

| Nivel | Qué | Herramienta |
|---|---|---|
| Unit | Reducer de `useAnalysisStream` (parseo de frames, dedupe por `iteracion`, transiciones de fase), diccionario de errores, guards. | Vitest |
| Componente | Pantallas con estados mockeados (resultados según modo, modal de atípico, PendingBadge en mocks). | React Testing Library |
| Red mockeada | Flujos de auth y análisis con **MSW** simulando respuestas del backend, incluida una **secuencia SSE canned** (frames de ejemplo con atípico + iteracion:2). | MSW |
| Integración real (manual) | Fases 1-4 recorridas contra el backend real (Docker local). No hay E2E automatizado — está **fuera de alcance V1.0** (`constraints.md`: sin Selenium/Playwright). | Manual |

Fixture recomendado: guardar una **grabación de una secuencia SSE real** (con y sin atípico) como
archivo de frames para alimentar los tests del hook sin depender del backend.

### 9.2 Riesgos de integración

1. **SSE sobre POST — no EventSource.** Riesgo central. Mitigación: `@microsoft/fetch-event-source`
   o reader manual con buffering de `TextDecoder` bien testeado. Un frame puede partirse entre
   chunks — el parser debe bufferear hasta `\n\n`.
2. **Cookie + CORS.** Sin `credentials:"include"` la cookie no viaja y todo da 401 silencioso.
   `FRONTEND_ORIGIN` debe matchear el origen exacto (puerto 5173). **Decisión tomada (22/07/2026):**
   en dev se usa **proxy de Vite** (`/api` → `localhost:8000`) para evitar CORS por completo (mismo
   origen) — se configura en Fase 0. **⚠️ Pendiente explícito:** el proxy es un atajo **solo de
   desarrollo**; NO ejercita el CORS real del backend. **CORS real debe implementarse y probarse
   antes de producción** (nginx sirve front + proxya `/api`, o el front pega directo con
   `FRONTEND_ORIGIN` productivo y cookie `Secure`). Ver §10, pendiente P1. La cookie es
   `SameSite=Lax` y sin `Secure` en dev (funciona en HTTP localhost); en prod requiere HTTPS
   (`ENV=production` activa `Secure`).
3. **`iteracion`.** Si la UI acumula en vez de reemplazar, tras rechazar un atípico se muestran
   resultados duplicados/contradictorios. El reducer debe versionar por `iteracion`.
4. **`total` de `progress` no confiable** (§4 de integration). No atar la barra de progreso a
   `total`; contar `test_result` (se esperan 8) o usar los pasos conocidos.
5. **Timeout de 300 s del atípico.** Si el usuario tarda, el server cierra con `SESSION_TIMEOUT`.
   La UI no debe quedar colgada — reflejar el cierre y ofrecer reintentar.
6. **`cramer_particion` custom roto.** No habilitar la opción hasta que el backend la arregle
   (§6). Si se habilita, rompe en runtime del backend (no da 400 controlado).
7. **Sin mensajes legibles en eventos SSE intermedios.** Depender del diccionario §7; el texto no
   viene del backend hasta `result_etapa1`.
8. **500 de register sin SMTP** en dev. Documentar el workaround (§3.4) para no confundirlo con un
   bug del frontend.
9. **Tokens de verificación en memoria del proceso.** Un restart del backend invalida los tokens
   pendientes — puede desconcertar en dev. Documentarlo.

---

## 10. Decisiones tomadas y pendientes

### Decisiones tomadas (22/07/2026)

- **D1 — Librería SSE:** `@microsoft/fetch-event-source` (§0, §2.3). El reader manual queda como
  fallback documentado.
- **D2 — CORS en dev:** proxy de Vite (`/api` → `localhost:8000`), mismo origen, sin CORS en
  desarrollo (§9.2.2). Ver pendiente **P1**.
- **D3 — Mocks:** MSW intercepta las rutas no implementadas y se reutiliza en tests (§6, §9.1).

### Decisiones tomadas (28/07/2026 — inicio de Fase 1, Auth)

- **D4 — Sin TanStack Query todavía.** `AuthProvider` usa `fetch` + `useState`/`useEffect` simple
  (sin la dependencia de §1.1) para `/me`, `login` y `logout`. Menos superficie para arrancar Auth;
  React Query se suma recién en Fase 4, cuando `/history` lo justifique más — no antes, para no
  sumar una dependencia sin necesidad real todavía.
- **D5 — Sin MSW todavía.** Los tests de Auth (Fase 1) siguen el patrón ya establecido en el repo
  antes de esta fase (`vi.stubGlobal("fetch", ...)`, ver `ping.test.ts`/`useBackendPing.test.tsx`),
  no MSW. La decisión D3 (MSW) sigue en pie para cuando Fase 5 la necesite de verdad con los mocks
  de Etapa 2 — introducirla antes sería una dependencia nueva sin consumidor real todavía.
- **D6 — Workaround de dev para el 500 de `register`, sin tocar el backend.** Al leer el código real
  de `auth/router.py`/`auth/email.py` se confirmó que la nota original de este documento (§3.4,
  Opción B — "token de logs") **ya no aplica**: el mock que lo hacía posible
  (`print("MOCK SMTP...")`) fue reemplazado por completo en Auth Parte 2 (19/07/2026, ver
  [DECISIÓN 032](../docs/decisiones/decision032.md) y
  [DECISIÓN 034](../docs/decisiones/decision034.md)). Hoy, sin SMTP real configurado,
  `send_verification_email()` lanza `RuntimeError` **antes** de que el token se guarde en
  `_pending_tokens` o se loguee en ningún lado, y como el mail se manda antes de comitear el usuario
  (para evitar huérfanos, DECISIÓN 032), no queda ningún usuario ni token creado — no hay ningún
  token real que rescatar de los logs con el código actual. Opción evaluada y descartada: agregar
  2 líneas de log dev-only en `register()` para exponer el token igual — fuera de alcance de
  "frontend Fase 1", no se tocó el backend. En su lugar, el banner de dev (bajo
  `import.meta.env.DEV`, ver `EntryPage.tsx`) es honesto sobre la limitación en vez de sugerir
  revisar logs que no van a tener nada. Ver pendiente **P4**.
- **D7 — Persistencia del flag anónimo.** `enterAnonymously()` persiste en `localStorage`
  (clave `metis-anon-session`), mismo patrón que `metis-theme-mode` de `ThemeProvider`, para
  sobrevivir a un refresh de página. Se limpia al loguear con una cuenta real.
- **D8 — Fidelidad visual de la Puerta de entrada.** El markup de `EntryPage` se adaptó
  directamente del HTML real de la variante A ★ en `frontend-design/metis-prototipo-fase3.html`
  (bloque `auth.variants[0]`), no de una estructura nueva — mismas clases genéricas (`.h`, `.sub`,
  `.fn`, `.logo`, `.row`, `.col`, `.field`, `.input`, `.b`/`.b-pri`/`.b-sec`, `.banner`), portadas a
  `theme/components.css` con alcance acotado a lo que Fase 1 necesita — el resto de las clases del
  prototipo se suma página por página cuando esa pantalla se implemente de verdad, no todas de una.

### Decisiones tomadas (28/07/2026 — Fase 2, Config + stream Etapa 1)

- **D9 — Router state en vez de `AnalysisConfigProvider`.** `ConfigPage` arma el `AnalysisStreamForm`
  completo (incluido el `File`) y lo pasa a `/stream` vía `navigate(path, {state})` de React Router,
  no vía un context dedicado. Es un hand-off de una sola vez que `StreamPage` consume una única vez
  al montar — un context solo se justifica si varios componentes desconectados necesitaran leer
  `modo` reactivamente entre renders, que no es el caso acá.
- **D10 — Sin preview de CSV/Excel en Config.** `columna_x`/`columna_y` son inputs de texto plano,
  fieles al contrato real (`Form(str)`, sin `Literal` — ver `frontend-integration.md` §3), en vez
  de la tabla de preview con columnas parseadas de la variante H. Parsear el archivo en el cliente
  para mostrar una preview real exigiría sumar una dependencia (`papaparse`/`xlsx`) sin necesidad
  probada todavía — el backend ya hace el parseo real y acepta cualquier nombre/índice de columna
  como string. Queda como posible pulido de Fase 6, no bloquea el flujo funcional.
- **D11 — Agrupación por bloque, no lista plana de 8 pruebas.** El timeline de `StreamPage` agrupa
  las 8 pruebas en 4 pasos conceptuales (Independencia, Homogeneidad, Tendencia, Atípicos), igual
  que la propia forma de `Etapa1Result` (`independencia[]`/`homogeneidad[]`/`tendencia[]`/
  `atipicos[]`) — cada paso se expande al hacer click una vez que tiene datos, mostrando el detalle
  prueba por prueba. Más fiel al concepto de "timeline" de la variante A que una lista de 8 filas
  sueltas.
- **D12 — La finalización del stream es un paso manual, no un auto-redirect.** Al llegar
  `fase="done"`, `StreamPage` muestra un banner de completado con un botón "Ver resultados ▸" en vez
  de navegar sola a `/results` — así se puede ver el timeline completo (todos los grupos con su
  veredicto) antes de pasar a la pantalla de resultados, útil para pruebas manuales/demo mientras
  `ResultsPage` siga siendo el stub de Fase 3.
- **D13 — Mockeo de `sse.test.ts` a nivel de librería.** Los tests de `useAnalysisStream` mockean el
  módulo `@microsoft/fetch-event-source` directamente (capturando `onopen`/`onmessage`/`onclose`/
  `onerror`) y disparan secuencias de eventos sintéticas armadas a mano según los shapes reales de
  `frontend-integration.md` §4, en vez de grabar una sesión SSE real contra el backend (no
  disponible en esta sesión — ver P5). Coherente con D5 (sin MSW todavía) y con el precedente ya
  establecido en el backend de series 100% sintéticas con expectativa recomputada inline
  (`backend/tests/README.md`), no dato real.

### Decisiones tomadas (28/07/2026 — Fase 3, Resultados Etapa 1)

- **D14 — Sin sustitución de fórmulas en la pantalla de resultados.** La variante D del wireframe
  ("Paso a paso vs Experto") muestra un acordeón con pasos tipo "Planteo y media", "Secuencias y
  cambios", "Fórmula y sustitución" — pero `TestResultDetail` (el shape real de cada prueba en
  `Etapa1Result`) solo trae `estadistico`/`valor_critico`/`veredicto`/`n1`/`n2`/`warning_*`, no las
  cantidades intermedias (S, C, τ, etc.) que un desarrollo paso a paso genuino necesitaría — esos
  datos no salen del backend por ningún evento SSE ni por `GET /analysis/{id}`. Inventar esos
  números para simular una sustitución de fórmula sería fabricar contenido estadístico no respaldado
  por el backend, algo que este proyecto trata como una falta grave (ver la cultura de
  `formulas-etapa1.md`/`formulas-etapa2.md`: "ninguna fórmula se implementa sin referencia
  explícita"). La sustitución de fórmulas con valores reales **sí** es un requisito real, pero
  específico del PDF de exportación (`constraints.md`, "PDF de exportación — CU-01"), no de esta
  pantalla — se implementará ahí cuando corresponda, no acá con datos inventados.
- **D15 — El modo Paso a paso se expresa como divulgación progresiva (`<details>`), no como
  contenido distinto.** Docencia+paso_a_paso envuelve cada grupo de pruebas
  (independencia/homogeneidad/tendencia/atípicos) en un `<details class="results-group">` nativo,
  colapsado por defecto; docencia+experto y anónimo (Decisión D) muestran las mismas tarjetas
  siempre abiertas, sin acordeón. Es la misma data en los tres modos — la única diferencia real es
  el widget de presentación, consistente con el criterio de "hecho" de Fase 3
  (`§8`: "los tres modos de presentación renderizan correctamente el mismo Etapa1Result").
- **D16 — Sin gráficos (serie temporal, correlograma, boxplot).** La variante E del wireframe
  incluye gráficos, pero requieren la serie cruda de datos y estadísticos que `Etapa1Result` no
  expone (el evento `descriptive_stats` solo trae los 8 campos agregados, no la serie ni el
  correlograma — ver `frontend-integration.md` §4, nota sobre `DescriptiveStats`). No hay datos
  reales que graficar todavía; agregarlos requeriría o bien un gap de backend nuevo, o mockear datos
  falsos en una pantalla que sí tiene datos reales — deliberadamente no se mezclan ambas cosas acá.
- **`modo` viaja de `ConfigPage` a `ResultsPage` a través de `StreamPage`** (router state en las tres
  paradas, coherente con D9) — `StreamPage` no lo necesitaba para sí misma pero sí reenviarlo.

### Decisiones tomadas (28/07/2026 — Fase 4, Historial)

- **D17 — `Etapa1ResultView` extraído de `ResultsPage` para reutilizar en el detalle de historial.**
  `GET /history/{id}` devuelve el mismo shape de `Etapa1Result` que `result_etapa1` del stream (ver
  `frontend-integration.md` §3, "mismo shape que GET /analysis/{analysis_id}"). En vez de duplicar el
  banner/KPIs/descriptivos/warnings/grupos entre `ResultsPage` y `HistoryDetailPage`, esa parte se
  extrajo a un componente presentacional puro (`routes/results/Etapa1ResultView.tsx`, `{result,
  modo}`) que no sabe de dónde vino el dato (stream en vivo vs. historial persistido) ni decide el
  `modo` efectivo — esa decisión (anónimo=experto, Decisión D) sigue siendo responsabilidad de quien
  lo usa, según su propio contexto de auth. `ResultsPage` quedó como un wrapper delgado (redirect si
  no hay `result` en el state + `modoEfectivo` derivado de `isAuthed`).
- **D18 — Paginación 100% client-side, tamaño de página 10.** `GET /history/` devuelve un array
  plano sin paginación (`frontend-integration.md` §3, discrepancia de forma con `api-contracts.md`).
  Sin volumen real de análisis por usuario todavía, paginar de a 10 en el cliente es suficiente y no
  exige tocar el backend; si el volumen real lo justifica más adelante, paginar server-side es un
  cambio de backend + un ajuste menor acá (reemplazar el `slice()` por parámetros de query), no una
  reescritura.
- **`HistoryDetailPage` no recibe `modo` por router state** (a diferencia de `ResultsPage`) — se lee
  directamente de `AnalysisDetail.modo` (persistido en la BD), porque esta ruta es un destino
  bookmarkeable/recargable por URL (`/history/:id`), no una parada intermedia de un flujo en memoria
  como stream→resultados.

### Pendientes

- **P1 — CORS real para producción (bloquea deploy, no el desarrollo).** El proxy de Vite (D2) es
  solo de dev y NO ejercita el CORS real del backend. Antes de producción hay que implementar y
  probar el camino real: nginx sirviendo el build del front y proxyando `/api` (arquitectura
  definida en `architecture.md`), con cookie `Secure` (`ENV=production`) y `FRONTEND_ORIGIN`
  productivo. Agendar como tarea explícita al cerrar el desarrollo local.
- **P2 — Puerto/herramienta del frontend.** Se asume **5173/Vite** (alineado con `FRONTEND_ORIGIN`
  del `.env.example`). Confirmar antes del scaffold para no desalinear el CORS del backend.
- **P3 — Azul institucional UCC** para las secciones con logo (blend UCC de Fase 2) — pendiente de
  confirmar contra el manual de marca. No bloquea el arranque; sí el pie de PDF/encabezados.
- **P4 — Verificación E2E de registro→verify bloqueada sin SMTP real (ver D6).** El tramo
  registro→mail→verify de Fase 1 solo tiene cobertura de tests unitarios/componente (fetch
  mockeado) — no se pudo correr manualmente contra el backend real en esta sesión por falta de
  credenciales SMTP locales. Login/logout/`me` sí quedan para verificarse manualmente contra el
  backend real (Docker) al cierre de esta fase, reutilizando el usuario ya verificado que
  documenta `sprint.md` ("Usuario de prueba para smoke tests", `2200631@ucc.edu.ar`) si sigue
  existiendo en la BD local, o insertándolo directo en Postgres si no.
- **P5 — Verificación E2E de Fase 2 contra el backend real, pendiente.** Config→stream se probó
  manualmente en el navegador solo contra un backend inexistente (proxy de Vite devolviendo 500) —
  confirma que el flujo no rompe ante un fallo de conexión (banner de error legible, sin excepciones
  sin manejar), pero no confirma el camino feliz real: subir un CSV real, ver los 8 `test_result`,
  un caso con atípico pausando y `resolveOutlier` desbloqueando la `iteracion:2`, ni un caso
  bloqueante mostrando `contract_error`. Cobertura de tests unitarios/componente completa (D13);
  falta la corrida manual contra Docker, agendada junto con P4 al cierre de esta etapa de trabajo.
- **P6 — Verificación E2E de Fase 3 contra el backend real, pendiente.** `ResultsPage` no se pudo
  ejercer contra un `Etapa1Result` real (no hay backend disponible esta sesión, y a diferencia de
  Fase 2 no existe un camino de "fallo gracioso" que la ejercite igual sin backend — esta pantalla
  solo se alcanza tras un análisis completo). Cobertura de tests de componente completa (6 tests:
  redirect sin resultado, banner de `nivel_confianza`, KPIs, warnings, acordeón en paso a paso,
  tarjetas planas en experto/anónimo) con un `Etapa1Result` sintético armado a mano. Falta la corrida
  manual real (los tres modos de presentación sobre un resultado real), agendada junto con P4/P5.
- **P7 — Verificación E2E de Fase 4 contra el backend real, pendiente.** `HistoryPage`/
  `HistoryDetailPage` están detrás de `RequireAuth` — sin backend real no hay forma de alcanzarlas
  siquiera (`/auth/me` nunca resuelve `isAuthed=true`, así que el guard redirige antes de que se
  monten). A diferencia de Fase 2, tampoco hay un camino de "fallo gracioso" que las ejercite sin
  login real. Cobertura de tests de componente completa (7 tests entre las dos pantallas: carga,
  error, lista vacía, paginación, links, y detalle con/sin `etapa1`) con datos sintéticos. Falta la
  corrida manual: loguearse, correr al menos un análisis real para tener algo que listar, ver el
  historial, y abrir el detalle.

**Backlog de verificación E2E contra el backend real — consolidado.** P4, P5, P6 y P7 son la misma
espera de fondo (no hay Docker disponible en esta sesión de trabajo): registro→verify, Config→stream
con un CSV real (incluido un caso con atípico), los tres modos de presentación de resultados sobre un
análisis real, y el historial de un usuario logueado con al menos un análisis persistido. Se corren
todos juntos la primera vez que haya acceso a Docker — no hace falta resolverlos uno por uno a medida
que cada fase se cierra.

---

## Resumen para arrancar

- Frontend Vite+React+TS en `frontend/`, tema Instrumento (tokens en §4), 8 pantallas ★.
- SSE **sobre fetch** (no EventSource) — es la decisión técnica que condiciona todo el streaming.
- Auth por cookie; CU-01/CU-02 se decide por presencia de sesión; anónimo = experto (Decisión D);
  modo elegido una vez en config (Decisión A).
- Etapa 1 se prueba contra el backend real; Etapa 2 / export / CU-03 son **mock con marca visual**.
- Entrega en 6 fases incrementales, cada una con criterio de "hecho" y separación explícita real vs.
  mock.
