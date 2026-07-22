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

---

## Resumen para arrancar

- Frontend Vite+React+TS en `frontend/`, tema Instrumento (tokens en §4), 8 pantallas ★.
- SSE **sobre fetch** (no EventSource) — es la decisión técnica que condiciona todo el streaming.
- Auth por cookie; CU-01/CU-02 se decide por presencia de sesión; anónimo = experto (Decisión D);
  modo elegido una vez en config (Decisión A).
- Etapa 1 se prueba contra el backend real; Etapa 2 / export / CU-03 son **mock con marca visual**.
- Entrega en 6 fases incrementales, cada una con criterio de "hecho" y separación explícita real vs.
  mock.
