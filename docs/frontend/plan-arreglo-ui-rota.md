# Plan de arreglo — UI del frontend rota en uso real

**Fecha:** 31 de Julio de 2026
**Diagnóstico de entrada:** [`informe-diagnostico-ui-rota.md`](informe-diagnostico-ui-rota.md)
**Rama sugerida:** `fix/frontend-ui-integracion` (sale de `staging`, PR hacia `staging`)

Cuatro bloques. **El orden importa:** el Bloque 0 escribe los tests que fallan antes de tocar código de producción, y el Bloque 4 es lo único que impide que esto vuelva a pasar. Saltear el Bloque 0 convierte esto en otra pasada de arreglos sin evidencia — que es exactamente cómo llegamos acá.

Cada ítem trae: archivo, cambio concreto, test que lo cubre, y criterio de verificación.

---

## Bloque 0 — Reproducir antes de arreglar

Regla: **ningún arreglo del Bloque 1 se implementa antes de tener su test rojo.** Es la aplicación literal de `superpowers:test-driven-development` y de la fase 4 de depuración sistemática.

### 0.1 — Test de regresión de F1 (StrictMode aborta el stream)

Archivo nuevo: `frontend/src/routes/stream/StreamPage.lifecycle.test.tsx`

Este test **debe fallar** contra el código actual. Ese fallo es la confirmación empírica del diagnóstico.

```tsx
// Cubre F1 — el ciclo de vida REAL de StreamPage con el hook REAL, bajo
// StrictMode. Es la franja que StreamPage.test.tsx (que mockea el hook) y
// sse.test.ts (que testea el hook sin componente) dejan sin cubrir entre
// los dos. Ver informe-diagnostico-ui-rota.md §5.1.
import { describe, expect, it, vi, beforeEach } from "vitest";
import { StrictMode } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { StreamPage } from "./StreamPage";
import type { AnalysisStreamForm } from "../../api/types";

const abortSpy = vi.fn();

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn((_url: string, opts: { signal: AbortSignal }) => {
    opts.signal.addEventListener("abort", abortSpy);
    return new Promise(() => {}); // nunca resuelve: simula un stream abierto
  }),
}));

function makeForm(): AnalysisStreamForm {
  return {
    archivo: new File(["anio,caudal\n1980,100"], "serie.csv", { type: "text/csv" }),
    columna_x: "anio",
    columna_y: "caudal",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    cramer_particion: "default",
  };
}

function renderUnderStrictMode() {
  return render(
    <StrictMode>
      <MemoryRouter initialEntries={[{ pathname: "/stream", state: { form: makeForm() } }]}>
        <Routes>
          <Route path="/stream" element={<StreamPage />} />
          <Route path="/config" element={<div>config</div>} />
        </Routes>
      </MemoryRouter>
    </StrictMode>,
  );
}

describe("StreamPage — ciclo de vida bajo StrictMode", () => {
  beforeEach(() => abortSpy.mockClear());

  it("deja exactamente un stream vivo tras el doble montaje de StrictMode", async () => {
    const { fetchEventSource } = await import("@microsoft/fetch-event-source");
    const mocked = vi.mocked(fetchEventSource);
    mocked.mockClear();

    renderUnderStrictMode();

    // StrictMode puede arrancarlo dos veces (aceptable, el primero se aborta),
    // pero NO puede quedar cero streams vivos.
    const abiertos = mocked.mock.calls.length;
    const abortados = abortSpy.mock.calls.length;
    expect(abiertos - abortados).toBe(1);
  });

  it("aborta el stream al desmontar de verdad", () => {
    const { unmount } = renderUnderStrictMode();
    abortSpy.mockClear();
    unmount();
    expect(abortSpy).toHaveBeenCalled();
  });
});
```

La aserción `abiertos - abortados === 1` es la clave: no exige que StrictMode arranque el stream una sola vez (eso sería pelearse con React), exige que **al final quede uno vivo**. Contra el código actual da `1 - 1 = 0` y falla. El segundo test protege lo que `c27d6ac` quería lograr — el arreglo no puede reintroducir el fetch huérfano.

### 0.2 — Confirmación manual en el navegador

Procedimiento de §6 del informe. Guardar la captura de la pestaña Network con el `POST /analysis/stream` en `(cancelled)` y adjuntarla al PR. **Evidencia antes que afirmaciones**, en los dos sentidos: sirve para probar el bug y después para probar el arreglo.

---

## Bloque 1 — Bloqueantes (P0)

### 1.1 — F1: un solo efecto, limpieza correcta

`frontend/src/routes/stream/StreamPage.tsx`

Reemplazar los dos efectos por uno solo, y eliminar `startedRef`:

```tsx
// El form se congela en el primer render: location.state es estable dentro
// de una misma entrada del historial, pero no queremos que un cambio de
// referencia reintente el análisis. StreamPage lo consume una sola vez.
const formRef = useRef(form);

useEffect(() => {
  const f = formRef.current;
  if (!f) {
    navigate("/config", { replace: true });
    return;
  }
  start(f);
  // Limpieza en el MISMO efecto que arranca: en el doble montaje de
  // StrictMode se aborta el primer stream y la segunda pasada arranca uno
  // nuevo — que es lo correcto. Con la guarda de `startedRef` anterior, la
  // segunda pasada salía por el `return` temprano y no quedaba stream vivo.
  // Ver informe-diagnostico-ui-rota.md — F1.
  return () => abort();
}, [start, abort, navigate]);
```

`start` y `abort` son `useCallback` con dependencias estables (`[handleEvent]` y `[]` respectivamente, `sse.ts` L166 y L255); `navigate` es estable en react-router 6. El efecto corre una vez por montaje real.

**Costo aceptado y explícito:** en desarrollo, StrictMode va a disparar dos veces `POST /analysis/stream`; el primero se aborta a los pocos milisegundos. El backend crea una sesión en `session_store` y la limpia en el `finally` de `stream_etapa1`, así que no queda basura. En producción StrictMode no corre. Esto se documenta en el código, no se esconde.

**Alternativa descartada:** sacar `<StrictMode>` de `main.tsx`. Haría desaparecer el síntoma sin arreglar la causa, y renunciaría a la única herramienta que detecta efectos no idempotentes. No se hace.

**Cubierto por:** 0.1, y el test de integración 4.2-a.

### 1.2 — F1 (secundario): que un stream muerto se note

`frontend/src/api/sse.ts`

Hoy `onclose` no hace nada. Si el servidor cierra la conexión sin haber emitido `complete`, la fase queda en `"streaming"` para siempre. Pasar a `"error"` con un código nuevo:

```tsx
onclose() {
  setInternal((prev) =>
    prev.fase === "streaming" || prev.fase === "waiting_outlier"
      ? { ...prev, fase: "error",
          error: { codigo: "STREAM_CLOSED_EARLY", mensaje: errorText("STREAM_CLOSED_EARLY") } }
      : prev,
  );
},
```

**Deuda que esto genera y hay que pagar en el mismo commit:** `STREAM_CLOSED_EARLY` es un código nuevo originado en el frontend. DECISIÓN 038 dejó la regla explícita — todo código nuevo se agrega al catálogo de `api-contracts.md`, sección "Códigos originados en el frontend", **en el mismo commit que lo introduce**. Además hay un job de CI (`error-catalog`, `scripts/check-error-catalog.sh`) que lo verifica. Agregar también la entrada en `i18n/errors.es.ts`.

**Cubierto por:** test nuevo en `sse.test.ts` — "un `onclose` sin `complete` previo deja `fase='error'`".

### 1.3 — F2: poder crear un usuario en desarrollo

Dos entregables, uno inmediato y otro que requiere decisión.

**(a) Inmediato, sin tocar el backend — `scripts/seed-dev-user.sh`**

Automatiza el INSERT que `sprint.md` ya documenta en prosa (actualización 29/07/2026): genera el hash bcrypt con el Python del contenedor de backend, inserta el usuario con `email_verified=true`, e imprime las credenciales. Con su contraparte `scripts/clean-dev-user.sh`. Desbloquea CU-01 completo (login, modo paso a paso, persistencia, historial) sin ninguna decisión de arquitectura pendiente. **Hacer esto primero.**

**(b) Requiere DECISIÓN nueva — escotilla de desarrollo en `auth/email.py`**

Si `ENV != "production"` y faltan las credenciales SMTP, en vez de levantar `RuntimeError`, loggear el token con `print(flush=True)` y devolver éxito — restaurando el comportamiento del mock de la Parte 1 pero acotado a desarrollo. Esto toca DECISIÓN 032 (mandar el mail antes del commit), así que **no se implementa sin escribirlo como decisión primero** (`docs/decisiones/decision045.md` [corrección 05/08/2026: 045 la tomó "Fondos animados en Canvas 2D" antes de que esta se escribiera — la escotilla SMTP queda reasignada a **049**, ver `docs/decisiones/README.md`]), con las alternativas evaluadas: escotilla por `ENV`, servidor SMTP de captura local tipo MailHog en `docker-compose`, o dejarlo como está y depender sólo del script (a). Mi recomendación es MailHog: no toca el código de producción, no introduce una rama `if dev` en el camino crítico de autenticación, y ejercita `aiosmtplib` de verdad.

**Cubierto por:** E2E-1 y E2E-4 del Bloque 4 dependen de que exista una cuenta. Con (a) alcanza para desbloquearlos.

### 1.4 — F3: que un fallo de sesión se vea

`frontend/src/auth/AuthProvider.tsx`

Distinguir "401 legítimo" de "algo salió mal", y que `login()` falle si no puede confirmar la sesión:

```tsx
const refetch = useCallback(async () => {
  try {
    setUser(await authApi.me());
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      setUser(null);       // no hay sesión: estado normal, no es un error
      return;
    }
    setUser(null);
    throw err;             // red caída, CORS, 500: el llamador tiene que enterarse
  }
}, []);

const login = useCallback(async (body: LoginRequest) => {
  await authApi.login(body);
  await refetch();                       // ahora sí puede lanzar
  if (!userRef.current) {
    throw new ApiError(0, "SESSION_NOT_ESTABLISHED",
      "El login fue aceptado pero no se pudo abrir la sesión. Revisá la conexión con el backend.");
  }
  localStorage.removeItem(ANON_STORAGE_KEY);
  setIsAnonymous(false);
}, [refetch]);
```

Ojo con el arranque: el `useEffect` de montaje llama `refetch()` y ahora puede lanzar — hay que envolverlo en su propio `try/catch` para que la app no quede en pantalla de carga si el backend está caído. Mostrar en su lugar un estado "backend no disponible" (el `TopBar` ya tiene ese concepto con `useBackendPing`).

`SESSION_NOT_ESTABLISHED` es otro código nuevo: misma obligación de catálogo que 1.2.

**Cubierto por:** tests nuevos en `AuthProvider.test.tsx` (401 → `user=null` sin lanzar; error de red → lanza) y `EntryPage.test.tsx` (login 200 + `/me` 500 → banner visible, no botón muerto).

---

## Bloque 2 — Navegación (P1)

### 2.1 — F4/F6: barra de navegación real en `TopBar`

Links según el estado de sesión:

| Estado | Links |
|---|---|
| Sin sesión | (ninguno — sólo se está en la puerta de entrada) |
| Anónimo | Nuevo análisis · Salir |
| Autenticado | Nuevo análisis · Historial · Cerrar sesión |

`logout()` pasa a `await logout(); navigate("/", { replace: true })`. Ídem para "Salir" del anónimo, que además tiene que limpiar el flag `metis-anon-session` (hoy `enterAnonymously` lo setea y sólo `logout` lo limpia — un anónimo no tiene forma de volver a la puerta de entrada).

### 2.2 — F5: continuación de Etapa 1 a Etapa 2

`ResultsPage.tsx`: botón "Continuar a Etapa 2 ▸" que navega a `/ranking`, con el `PendingBadge` al lado para no dar a entender que Etapa 2 ya está implementada de verdad (coherente con DECISIÓN 042). Alternativa a discutir: ocultarlo hasta que el backend exponga Etapa 2. **Prefiero mostrarlo con el badge** — el tribunal va a querer ver el flujo completo de CU-01, y el badge deja explícito qué es mock.

### 2.3 — F7: guard de sesión para las cinco rutas sueltas

Guard nuevo `RequireSession` (autenticado **o** anónimo) en `auth/guards.tsx`, aplicado a `/config`, `/stream`, `/results`, `/ranking` y `/design-events`. Sin sesión de ningún tipo → redirect a `/`. Esto es lo que hace cumplir en la UI la regla de `constraints.md`: la distinción CU-01/CU-02 se resuelve por presencia de JWT, no por ruta — pero *ninguna* de las dos es "entrar sin pasar por la puerta".

### 2.4 — F8: que un botón deshabilitado explique por qué

- Cramer "Personalizada": nota visible debajo del control (ya existe el `<p class="fn">`, sólo hay que asegurar que se lea antes del hover) en vez de depender de `title=`.
- Pasos del timeline: reemplazar `disabled` por un estado visual "esperando resultados" no clickeable. Un botón deshabilitado y uno que todavía no tiene nada que mostrar se ven igual y no lo son.

**Cubiertos por:** el test de grafo de navegación, capa 3 del Bloque 4 (§4.2-b). Es el test que hace imposible volver a dejar una pantalla huérfana.

---

## Bloque 3 — Infraestructura (P2)

### 3.1 — F9: `frontend/Dockerfile`

Multi-stage: `node:22-alpine` para `npm ci --ignore-scripts && npm run build`, y `nginx:alpine` sirviendo `dist/` con `try_files $uri /index.html` (obligatorio: el router usa `createBrowserRouter`, sin ese fallback cualquier recarga en `/config` da 404). El `docker-compose.yml` ya lo espera en el puerto 3000 — configurar nginx interno para escuchar ahí, o cambiar el compose. Criterio de aceptación: **`docker-compose up --build` levanta los cuatro servicios y `http://localhost/` responde 200.**

### 3.2 — F10: unificar el origen del frontend

Una sola variable de entorno. `FRONTEND_URL` (que `auth/router.py` ya usa para el link del mail) y `FRONTEND_ORIGIN` (que `main.py` usa para CORS) son el mismo concepto con defaults incoherentes. Unificar en `FRONTEND_ORIGIN`, default `http://localhost:5173`, documentarla en `.env.example` con las tres formas que toma según el escenario (dev con proxy de Vite / dev sin proxy / producción tras nginx).

### 3.3 — F11: `/ping` en nginx

Agregar `location /ping { proxy_pass http://backend:8000; }` antes del `location /`.

### 3.4 — F12: `.catch()` en `DesignEventsPage`

Estado de error visible en vez de "Calculando…" eterno. Barrido rápido en busca del mismo patrón: `grep -rn "\.then(" frontend/src --include=*.tsx | grep -v catch`.

---

## Bloque 4 — Estrategia de testing anti-regresión

Esto es lo que pediste y es lo más importante del plan. La suite actual es buena en lo que cubre; el problema es qué no cubre. Cuatro capas, de la más barata a la más cara.

### 4.1 — Capa 1: unitarios (existe — corregir el sesgo)

**Cambio de regla, no de herramienta:** todo test que renderice una **página** lo hace bajo `<StrictMode>`. Helper único en `src/test/renderPage.tsx`:

```tsx
export function renderPage(ui: ReactNode, { route = "/", state }: Options = {}) {
  return render(
    <StrictMode>
      <MemoryRouter initialEntries={[{ pathname: route, state }]}>
        <AuthProvider>{ui}</AuthProvider>
      </MemoryRouter>
    </StrictMode>,
  );
}
```

Migrar los tests de página existentes a este helper. Los tests de funciones puras (`tokens.test.ts`, `format`, `errors.es`) no lo necesitan.

**Por qué esto y no otra cosa:** cierra §5.2 del informe — el modo en que la app corre en desarrollo pasa a estar cubierto por defecto, no por acordarse.

### 4.2 — Capa 2: integración (nueva — es la capa que faltaba)

Componente real + hook real + MSW. **Nada de `vi.mock` sobre módulos propios en esta capa** — sólo se intercepta la red, en el borde.

**(a) Stream de Etapa 1 de punta a punta, con MSW devolviendo SSE real**

`msw/node` puede responder un `ReadableStream` con `Content-Type: text/event-stream`. Fixture con la secuencia real que emite `_emitir_resultado` (`analysis_service.py`): `contract_warning` → `descriptive_stats` → 8 × (`progress` + `test_result`) → `result_etapa1` → `complete`. Escenarios:

1. Camino feliz: montar `StreamPage` bajo StrictMode → los 4 grupos llegan a estado final → aparece "Ver resultados". **Este test es el que hace imposible que F1 vuelva.**
2. Con atípico: `outlier_detected` → modal → `resolveOutlier("rechazar")` → llega `iteracion: 2` → los resultados se reemplazan, no se duplican.
3. Contrato bloqueante: `contract_error` + `complete` → banner de error, y `complete` **no** pisa la fase de error (regresión ya conocida, hoy sólo cubierta con el hook aislado).
4. El servidor cierra sin `complete` → `STREAM_CLOSED_EARLY` visible (1.2).

**(b) Grafo de navegación sobre `routes.tsx` real**

`createMemoryRouter(routes)` — el array real, no rutas de mentira. Recorrer con clicks:

- Anónimo: `/` → "Entrar como anónimo" → `/config` → ejecutar → `/stream` → "Ver resultados" → `/results` → "Continuar a Etapa 2" → `/ranking` → "Elegir" → `/design-events`.
- Autenticado: `/` → login OK → `/config`; header → "Historial" → `/history` → click en un ítem → `/history/:id`; "Cerrar sesión" → vuelve a `/`.
- Sin sesión, navegación directa a `/config` → redirect a `/` (cubre F7).

Este archivo cubre F4, F5, F6, F7 y el login exitoso de §5.3 de una sola vez, y es barato: un archivo, unos 150 renglones. **Es el de mejor relación costo/beneficio de todo el plan.**

**(c) Invariante de alcanzabilidad**

Test que enumera las rutas de `routes.tsx` y falla si alguna no aparece como destino en ningún `navigate()`/`<Link>` del código de producción. Convierte "nos olvidamos del botón" en un fallo de CI en vez de un hallazgo manual. Implementable con `grep` sobre `src/` o con un `import.meta.glob`; queda a criterio si vale la pena o alcanza con (b).

### 4.3 — Capa 3: E2E con Playwright contra Docker (nueva — requiere DECISIÓN)

**Esto contradice `constraints.md`.** No se implementa sin escribir primero `docs/decisiones/decision046.md`, que revise la exclusión de "Tests end-to-end de UI automatizados (Selenium/Playwright)" del scope V1.0.

El argumento a favor, para esa decisión: **cinco de los doce defectos del informe (F1, F4, F5, F6, F9) sólo eran detectables desde esta capa.** El costo de no tenerla ya se pagó una vez —dos PRs mergeados sobre una aplicación rota— y se va a volver a pagar en M4/M5, que son justamente los milestones definidos como "flujo completo de punta a punta verificado". El argumento en contra sigue siendo válido: es la capa más cara de mantener y la más frágil. Por eso el alcance propuesto es deliberadamente chico.

**Cinco escenarios, no más:**

| ID | Escenario | Defectos que hubiera atrapado |
|---|---|---|
| E2E-1 | Login con usuario sembrado → `/config` | F2, F3, §5.3 |
| E2E-2 | Anónimo → CSV de 40 años → stream completo → resultados | **F1** |
| E2E-3 | Stream con atípico → modal → rechazar → iteración 2 → resultados | F1 |
| E2E-4 | CU-01 → análisis → historial → detalle | F4 |
| E2E-5 | Serie de 8 datos → `CONTRACT_SERIES_TOO_SHORT` visible, sin cuelgue | — (protege el único caso bloqueante del pipeline) |

Más un **smoke de infraestructura**, que no necesita Playwright: `docker-compose up --build` levanta los cuatro servicios y `curl -f http://localhost/` devuelve 200. Tres renglones de bash que hubieran atrapado F9 el día que se escribió el `docker-compose.yml`.

Dependencias: el script de 1.3(a) para el usuario sembrado, y un CSV fixture versionado en `frontend/e2e/fixtures/`.

### 4.4 — Capa 4: cambio de proceso (gratis, y es el que más importa)

**Definition of done para todo PR que toque `frontend/`:** evidencia de haber corrido el flujo en el navegador después del último commit del PR — captura o log de la pestaña Network. F1 se coló porque `c27d6ac` cambió el ciclo de vida del stream y la verificación manual que lo cubría era anterior. Ninguna herramienta automática iba a avisar; una casilla en la plantilla de PR, sí.

Complemento barato: plantilla de PR (`.github/pull_request_template.md`) con esa casilla y con "¿este cambio introduce un código de error nuevo? → agregado a `api-contracts.md`" (que ya es regla de DECISIÓN 038 y hoy depende de acordarse).

### 4.5 — CI

```yaml
  frontend:
    # sin cambios: lint + test + build (ahora incluye capas 1 y 2)

  e2e:
    name: E2E (Playwright contra Docker)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose up -d --build          # smoke de F9: si esto falla, falla el job
      - run: ./scripts/seed-dev-user.sh
      - run: npx playwright test
        working-directory: frontend
      - uses: actions/upload-artifact@v4           # trazas y videos de los que fallen
        if: failure()
```

**Arrancar como no bloqueante** (`continue-on-error: true`) durante dos o tres PRs, para medir cuán flaky es antes de comprometerse. Si se estabiliza, hacerlo requerido en el Ruleset — y ahí sí, junto con los tres jobs de `ci.yml`, resolver de paso la pregunta de gobernanza abierta de DECISIÓN 044 (hoy ningún check es *required* de verdad).

---

## Orden de ejecución sugerido

| Paso | Contenido | Por qué en esta posición |
|---|---|---|
| 1 | 0.1 + 0.2 | Rojo antes que verde. La captura del `(cancelled)` es la evidencia. |
| 2 | 1.3(a) — script de seed | Desbloquea probar CU-01 a mano. Sin esto el resto se verifica a ciegas. |
| 3 | 1.1 + 1.2 | El bloqueante. Verde el test de 0.1. |
| 4 | 1.4 | Deja de esconder los fallos que vengan después. |
| 5 | 4.1 + 4.2(a) | Cementa 1.1/1.2 antes de seguir tocando. |
| 6 | Bloque 2 completo | Navegación. |
| 7 | 4.2(b) | Cementa el Bloque 2. |
| 8 | Bloque 3 | Infra. El Dockerfile habilita el E2E. |
| 9 | DECISIÓN 046 + 4.3 + 4.5 | E2E, sólo con la decisión escrita primero. |
| 10 | 4.4 | Proceso. Puede ir en cualquier momento; cuanto antes, mejor. |

Los pasos 1-4 son un PR. Los 5-7, otro. Los 8-10, un tercero. **No meter los tres en uno** — parte de cómo llegamos acá fue mergear cambios grandes de frontend sin verificación intermedia.

---

## Documentos a actualizar al cerrar

- `sprint.md` — corregir la sección "feature/frontend-fases1-5 — COMPLETA": la verificación E2E que registra como cerrada quedó invalidada por `c27d6ac` el mismo día. **Tacharla, no borrarla** (mismo criterio de trazabilidad que ya usa ese archivo).
- `constraints.md` — si se aprueba la DECISIÓN 046, mover "Tests end-to-end de UI automatizados" fuera de "Scope V1.0 — lo que NO entra".
- `api-contracts.md` — `STREAM_CLOSED_EARLY` y `SESSION_NOT_ESTABLISHED` en "Códigos originados en el frontend" (regla de DECISIÓN 038, verificada por el job `error-catalog`).
- `testing.md` — sumar las capas 2 y 3 a los cuatro niveles obligatorios; hoy sólo contempla backend.
- `architecture.md` — al cerrar 3.1, actualizar la nota de "Nginx como reverse proxy" que dice que el build estático todavía no existe.
- `docs/decisiones/` — 045 (SMTP en desarrollo) y 046 (E2E en scope), si se aprueban
  [corrección 05/08/2026: 045 terminó tomada por "Fondos animados en Canvas 2D" — la
  escotilla SMTP queda reasignada a **049**, ver `docs/decisiones/README.md`].

---

## Riesgos conocidos de este plan

- **1.1 asume que F1 es la causa única del stream colgado.** El informe descartó los otros candidatos (§4), pero si tras el arreglo el stream sigue sin avanzar, el siguiente sospechoso es el buffering del proxy de Vite sobre `text/event-stream`. Se diagnostica igual: pestaña Network, ver si los frames llegan.
- **MSW devolviendo SSE en Node** es lo técnicamente más delicado de 4.2(a). Si da problemas, el plan B es un servidor HTTP mínimo con `node:http` en el setup del test — menos elegante, igual de válido, y sigue siendo mucho más barato que Playwright.
- **1.3(b) toca autenticación**, que es código sensible y ya tiene decisiones escritas encima (032, 034). De ahí que la recomendación sea MailHog: cero cambios en el camino crítico.
