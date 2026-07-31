# Informe de diagnóstico — UI del frontend rota en uso real

**Fecha:** 31 de Julio de 2026
**Rama analizada:** `fix/frontend-pasada2` (HEAD `faf134c`)
**Motivo:** dos PRs de frontend mergeados sin errores detectados (CI verde, SonarCloud limpio, 98 tests de Vitest en verde) y, al probar la aplicación a mano en el navegador, el flujo está roto: botones que no responden, registro y login que no funcionan, y el análisis estadístico que llega hasta la fase de pruebas y no continúa.

**Qué es este documento:** el resultado de la fase 1 y 2 de depuración sistemática — investigación de causa raíz y análisis de patrón. **No propone arreglos.** El plan de arreglo, priorizado y con su cobertura de tests, vive en [`plan-arreglo-ui-rota.md`](plan-arreglo-ui-rota.md).

**Estado de la evidencia:** cada hallazgo está marcado como VERIFICADO (contrastado contra archivo y línea, o contra el historial de git) o HIPÓTESIS (consistente con el síntoma reportado, pendiente de confirmación en el navegador). No se mezclan.

---

## 0. Resumen ejecutivo

Son **doce defectos** repartidos en cuatro grupos. Tres explican los tres síntomas que reportaste; los otros nueve son gaps reales que todavía no se manifestaron porque nadie llegó tan lejos en el flujo.

| # | Defecto | Síntoma que produce | Severidad | Evidencia |
|---|---|---|---|---|
| F1 | El stream se aborta a sí mismo al montar, bajo StrictMode | "El análisis llega a la fase de análisis y no continúa" | **Bloqueante** | VERIFICADO |
| F2 | Sin SMTP, `register` no crea usuario — y sin usuario no hay login | "El registro y el login no funcionan" | **Bloqueante** | VERIFICADO |
| F3 | `AuthProvider` silencia todo fallo de `/me` | "El botón no hace nada" | Alta | VERIFICADO |
| F4 | Ninguna pantalla navega a `/history` | Historial invisible | Alta | VERIFICADO |
| F5 | Ninguna pantalla navega a `/ranking` | Etapa 2 inalcanzable | Alta | VERIFICADO |
| F6 | "Cerrar sesión" no redirige | "El botón no hace nada" | Media | VERIFICADO |
| F7 | 5 de 8 rutas sin guard de sesión | Difumina CU-01 vs CU-02 | Media | VERIFICADO |
| F8 | Botones `disabled` por diseño, indistinguibles de rotos | "Botones que no funcionan" | Media (UX) | VERIFICADO |
| F9 | `frontend/Dockerfile` no existe | `docker-compose up --build` falla | Alta | VERIFICADO |
| F10 | CORS del backend apunta a un origen que nadie usa | Latente — explota sin el proxy de Vite | Alta | VERIFICADO |
| F11 | nginx no proxea `/ping` | "Backend no disponible" en producción | Baja | VERIFICADO |
| F12 | `DesignEventsPage` sin `.catch()` | Pantalla colgada en "Calculando…" | Media | VERIFICADO |

La sección 5 —**por qué 98 tests en verde no atraparon ninguno de estos**— es la parte de este informe que importa para el tribunal. Los bugs son bugs; el hueco de la estrategia de testing es una decisión de ingeniería que hay que poder defender.

---

## 1. Los tres bloqueantes

### F1 — El stream se aborta a sí mismo al montar (StrictMode)

**Síntoma reportado:** el análisis carga, la pantalla de stream aparece, y ahí se queda. Barra de progreso en 0 %, los cuatro grupos del timeline sin responder al click, ningún mensaje de error.

**Archivos:** `frontend/src/routes/stream/StreamPage.tsx` líneas 107-124; `frontend/src/main.tsx` línea 11; `frontend/src/api/sse.ts` líneas 166-239.

**El código, tal como está hoy** — dos efectos separados:

```tsx
// StreamPage.tsx, L107-124
useEffect(() => {
  if (!form) { navigate("/config", { replace: true }); return; }
  if (startedRef.current) return;
  startedRef.current = true;
  start(form);
}, [form, start, navigate]);

useEffect(() => {
  // "Si el usuario navega a mitad de stream, sin esto el fetch queda vivo…"
  return () => abort();
}, [abort]);
```

`main.tsx` monta la aplicación dentro de `<StrictMode>`. En React 18, **en desarrollo**, StrictMode monta cada componente, corre sus efectos, corre las funciones de limpieza de esos efectos, y vuelve a correr los efectos. Es deliberado: sirve para detectar efectos que no son idempotentes. Lo importante acá es que **los `useRef` no se reinicializan** en ese ciclo — React preserva el estado del componente entre las dos pasadas.

La secuencia real al entrar a `/stream` es entonces:

1. Efecto A (primera pasada): `startedRef.current = true`, `start(form)` → se abre el `fetch` del SSE.
2. Efecto B (primera pasada): se registra.
3. Limpieza de B: `abort()` → **se dispara el `AbortController` del stream recién abierto.**
4. Efecto A (segunda pasada): `startedRef.current` ya vale `true` → `return` temprano → **el stream nunca se reinicia.**

Resultado: `state.fase` queda congelada en `"streaming"`, `progress` en `{0, 0}` (por eso la barra queda en 0 %), y `tests` vacío — lo que hace que `summarizeGroup` devuelva `"pending"` para los cuatro grupos, y esos botones se rendericen `disabled` (`StreamPage.tsx`, L~253). **Los "botones que no funcionan" del timeline no son un bug propio: son la consecuencia visible de que nunca llegó ningún resultado.**

**Por qué ni siquiera aparece un error:** `@microsoft/fetch-event-source` no invoca `onerror` cuando el aborto lo provocó el propio cliente (chequea `signal.aborted` antes de llamarlo). El `.catch()` que `sse.ts` cuelga al final (L233) traga la promesa rechazada a propósito. La falla es completamente silenciosa.

**Cuándo se introdujo — VERIFICADO contra git:**

```
3374f73  fix(frontend): two useAnalysisStream bugs found by testing against the real backend
...
c27d6ac  fix(frontend): D1/D2/D4/D9/D10 code fixes from pasada 2     ← 29/07/2026 12:12
```

`git log` es cronológico inverso: `3374f73` es **anterior** a `c27d6ac`. Es decir, la verificación end-to-end contra Docker real que `sprint.md` registra como exitosa ("Config→stream con atípico real … cerrados") ocurrió **antes** del commit que introdujo `return () => abort()`. El cuerpo de `c27d6ac` lo dice con todas las letras:

> D2 - StreamPage.tsx: abort() now runs on unmount, so navigating away mid-stream doesn't leave the fetch alive or the backend session hanging for 300s. Added a regression test.

Se verificó, después se arregló otra cosa, y no se volvió a verificar. El "regression test" que ese commit agregó testea el escenario que le importaba (navegar afuera aborta) contra un hook mockeado — no el escenario que rompió.

**Defecto secundario en el mismo bloque (menor, no es la causa):** el efecto A declara `[form, start, navigate]` como dependencias, y `form` sale de `location.state`. La guarda de `startedRef` lo tapa hoy, pero es fragilidad: cualquier cambio de referencia de `form` reintentaría arrancar el stream.

---

### F2 — Registrarse es imposible en desarrollo, y por lo tanto loguearse también

**Síntoma reportado:** "el registro y login de usuario tampoco [funcionan]".

**Archivo:** `backend/metis/auth/router.py` líneas 64-79.

`register` manda el mail de verificación **antes** de comitear el usuario — decisión deliberada y documentada (DECISIÓN 032: evita usuarios huérfanos si el envío falla). Sin `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` en el entorno, `send_verification_email` levanta `RuntimeError`, se captura en L72 y se responde `500 AUTH_VERIFICATION_EMAIL_FAILED`. Consecuencia encadenada:

- No se crea el usuario (`db.add` está después del `try`).
- No queda token en `_pending_tokens` (se registra recién tras el commit, L94).
- Por lo tanto `/verify` no tiene nada que verificar.
- Y `/login` responde `403 AUTH_EMAIL_NOT_VERIFIED` para cualquier cuenta que igual existiera, porque `email_verified` arranca en `false`.

Esto **está** documentado: `sprint.md`, actualización del 28/07/2026, y FE-6 del plan de implementación. Lo que no está documentado es la conclusión operativa: **no hay ninguna manera de obtener una cuenta usable sin insertar el hash bcrypt a mano en Postgres.** El propio `sprint.md` (actualización 29/07) describe ese INSERT manual como el procedimiento, pero no está automatizado ni es evidente para quien abre la app a probar.

Para alguien que testea la UI, "el registro no funciona" y "el login no funciona" son el mismo defecto observado desde dos pantallas. El frontend, en este punto, se comporta correctamente: `EntryPage.tsx` L134-147 muestra un banner explícito de modo dev ante `AUTH_VERIFICATION_EMAIL_FAILED`.

**Aclaración importante:** F2 no es un bug del frontend. Es una dependencia dura de infraestructura que hace intesteable a mano la mitad de la aplicación (todo CU-01: modo paso a paso, persistencia, historial, exportación). Sigue en pie aunque F1 se arregle.

---

### F3 — Fallos de sesión invisibles

**Archivo:** `frontend/src/auth/AuthProvider.tsx` líneas 35-45.

```tsx
const refetch = useCallback(async () => {
  try {
    const currentUser = await authApi.me();
    setUser(currentUser);
  } catch {
    // 401 (sin cookie) o error de red — ambos significan "no autenticado"
    setUser(null);
  }
}, []);
```

El `catch` sin discriminar colapsa tres situaciones distintas en una sola: un 401 legítimo (no hay sesión), el backend caído, y un rechazo de CORS. Y `login()` (L59-68) llama a `refetch()` sin verificar el resultado: si el `POST /login` devuelve 200 pero el `GET /me` posterior falla, **`login()` resuelve sin lanzar**, `LoginForm` no muestra ningún error, `isSubmitting` vuelve a `false`, y la pantalla queda idéntica a antes del click.

Ese es, literalmente, el síntoma "aprieto el botón y no pasa nada". El comentario del código lo justifica citando §3.1 del plan de implementación como decisión de fase — pero el efecto secundario es que **cualquier problema de sesión se manifiesta como un botón muerto, sin diagnóstico posible desde la UI.**

HIPÓTESIS (no verificable sin el navegador): si además de F2 hubiera un problema de cookie o de origen, F3 es lo que lo estaría ocultando. Vale la pena mirar la pestaña Network antes de dar por cerrado el tema de login.

---

## 2. Navegación: pantallas que existen pero a las que no se llega

Estos cuatro explican la otra mitad de "hay botones que no funcionan": no es que los botones estén rotos, es que **los botones que faltan nunca se escribieron.**

### F4 — El historial es inalcanzable desde la UI

`grep -rn "navigate(\|to=\"" --include=*.tsx frontend/src` sobre todo el código de producción devuelve exactamente nueve destinos de navegación. **Ninguno es `/history`.** `TopBar.tsx` no tiene un solo link: sólo el estado del backend, el email, "Cerrar sesión" y "Cambiar tema". La pantalla `HistoryPage` está implementada, testeada y protegida por `RequireAuth` — y sólo se llega tipeando la URL.

### F5 — Etapa 2 es inalcanzable

Mismo grep: nada navega a `/ranking`. `ResultsPage.tsx` termina renderizando `Etapa1ResultView` y no ofrece ninguna continuación. El tramo `RankingPage → /design-events` sí existe (`RankingPage.tsx` L97), pero su puerta de entrada no. Las dos pantallas mockeadas de Etapa 2 son, en la práctica, código muerto desde el punto de vista del usuario.

### F6 — "Cerrar sesión" no redirige

`TopBar.tsx` L37-39: `onClick={() => void logout()}`. `logout()` borra la cookie y limpia el estado, pero nadie navega. Como `/config`, `/stream` y `/results` no tienen guard (F7), el usuario se queda exactamente en la pantalla donde estaba; lo único que cambia es que desaparece el email del header. Desde afuera: el botón no hizo nada.

### F7 — Cinco de ocho rutas no tienen guard

`routes.tsx`: sólo `/history` y `/history/:id` están envueltas en `RequireAuth`, y `/` en `RedirectIfAuthed`. `/config`, `/stream`, `/results`, `/ranking` y `/design-events` son accesibles sin sesión de ningún tipo — ni autenticada ni anónima. No provoca un crash, pero difumina la distinción CU-01 / CU-02 que `constraints.md` declara no negociable ("la distinción no se resuelve por ruta — se resuelve por presencia de JWT"). Hoy se puede entrar a `/config` sin haber pasado nunca por la puerta de entrada.

### F8 — Botones deshabilitados por diseño, que se leen como rotos

Dos casos, ambos correctos según la documentación vigente, ambos indistinguibles de un bug para quien prueba:

- `ConfigPage.tsx`: el botón "Personalizada" de la partición de Cramer está `disabled` por DECISIÓN 036. La explicación está en `title=`, invisible salvo hover.
- `StreamPage.tsx`: los cuatro pasos del timeline se renderizan `disabled` mientras `summarizeGroup` devuelve `"pending"`. Con F1 activo eso es **siempre**.

---

## 3. Infraestructura: el camino de producción nunca se ejecutó

### F9 — `frontend/Dockerfile` no existe

`docker-compose.yml` declara `frontend: build: ./frontend`, y `nginx/nginx.conf` hace `proxy_pass http://frontend:3000`. `ls frontend/` confirma que no hay Dockerfile. **`docker-compose up --build` falla.** Todo el camino de producción —build estático, nginx como único servicio expuesto, terminación de HTTPS— es hoy una decisión de arquitectura documentada que nunca se ejecutó ni una vez. `architecture.md` ya reconoce parte de esto ("lo que todavía no existe es el build estático servido por nginx"), pero no que el `docker-compose.yml` en el repo está roto tal como está.

### F10 — El CORS del backend apunta a un origen que nadie usa

`backend/metis/main.py` L14:

```python
allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")]
```

El frontend de desarrollo corre en `5173`; bajo nginx sería el puerto `80`. **Ningún escenario real usa `3000`.** Hoy es invisible porque el proxy de Vite (`vite.config.ts`) hace que todo salga same-origin y el navegador nunca necesite CORS. El día que el frontend se sirva sin ese proxy —o sea, la primera vez que se pruebe el stack completo— toda la autenticación se cae de golpe, y con F3 activo se caería en silencio.

Además, `auth/router.py` lee `FRONTEND_URL` (para armar el link del mail) y `main.py` lee `FRONTEND_ORIGIN`: **dos variables de entorno distintas para el mismo concepto**, con defaults incoherentes entre sí (`5173` y `3000`).

### F11 — nginx no proxea `/ping`

`nginx.conf` tiene `location /api/` y `location /`. `useBackendPing` pega a `/ping`, que cae en `location /` → se proxea al frontend → devuelve HTML o 404. El header diría "Backend no disponible" en producción con el backend perfectamente sano.

### F12 — `DesignEventsPage` sin manejo de rechazo

`DesignEventsPage.tsx` L30-43: `postDesignEvents(...).then(...)` sin `.catch()`. Si MSW no arrancó —build de producción, o `worker.start()` que falla— la promesa se rechaza, `data` queda en `null`, y la pantalla se queda para siempre en `"Calculando eventos de diseño…"` con un unhandled rejection en consola. Es el mismo patrón de falla silenciosa de F1 y F3.

---

## 4. Lo que se descartó durante la investigación

Registrado para que no se vuelva a investigar:

- **`indice_atipico` faltante en `TestResult`.** `analysis_service.py` L253 lee `prueba.indice_atipico`; si no existiera, el generador SSE reventaría al rechazar un atípico y el stream moriría — un candidato perfecto para el síntoma. **Descartado:** existe en `core/types.py` L22 y lo llena `core/etapa1/outliers.py` L83.
- **Nombres de pruebas desalineados entre backend y frontend.** Los `GROUPS` de `StreamPage.tsx` esperan `anderson`, `wald_wolfowitz`, `helmert`, `t_student`, `cramer`, `mann_kendall`, `kolmogorov_smirnov`, `chow`. **Descartado:** el backend emite `test_result` con el campo `prueba` tomado de `TestResult.prueba` del core; no hay traducción de por medio.
- **`fetchEventSource` mal cableado al formato SSE del backend.** **Descartado:** `_sse()` emite `event: <tipo>\ndata: <json>\n\n`, que es exactamente lo que la librería parsea en `ev.event` / `ev.data`; el caso especial de `result_etapa1` ya está contemplado en `sse.ts` L203-206.
- **El proxy de Vite rompiendo SSE por buffering.** No descartado formalmente, pero **improbable y no necesario para explicar el síntoma**: F1 ya lo explica por completo. Si tras arreglar F1 el stream sigue sin avanzar, éste es el siguiente sospechoso.

---

## 5. Por qué 98 tests en verde no atraparon nada de esto

Esta es la parte defendible ante un tribunal de ISI. Los doce defectos de arriba son consecuencias; lo de acá abajo es la causa.

### 5.1 El hueco tiene exactamente la forma del bug

Hay tres `vi.mock` en todo el repo. Dos de ellos, juntos, dibujan el hueco:

- `routes/stream/StreamPage.test.tsx` L8 mockea **`useAnalysisStream` entero**. Sus 12 tests verifican cómo se renderiza un `StreamState` inyectado a mano. El ciclo de vida real —montar, arrancar, abortar— no se ejecuta nunca.
- `api/sse.test.ts` L8 mockea **`fetchEventSource`**. Sus 25 tests sí ejercitan el hook real, pero fuera de cualquier componente, sin montaje ni desmontaje.

Entre esos dos mocks queda una franja que ningún test cruza: **el hook real, dentro de un componente real, con su ciclo de vida real.** F1 vive exactamente ahí. No es mala suerte — es el resultado previsible de mockear a ambos lados de una frontera.

### 5.2 Ningún test corre bajo StrictMode, pero la aplicación sí

`grep -rn "StrictMode" frontend/src` devuelve **una sola coincidencia: `main.tsx`.** Ningún test lo usa. Es decir: el modo en que la aplicación efectivamente corre en desarrollo —el único modo en que vos la probaste— no está cubierto por ninguna prueba. Todo bug que StrictMode expone (efectos no idempotentes, limpiezas que rompen, refs que no se reinician) es invisible para esta suite por construcción.

### 5.3 No existe un test del login exitoso

Los 5 tests de `EntryPage.test.tsx` cubren: alternar login/registro, login fallido con credenciales inválidas, registro exitoso, registro fallido en modo dev, y entrada anónima. **El camino feliz —login correcto → llegar a `/config`— no está testeado en ningún lado.** Y no puede estarlo con el patrón actual: ese redirect lo produce `RedirectIfAuthed`, que vive en `routes.tsx`, mientras `EntryPage.test.tsx` renderiza `<EntryPage />` pelada dentro de un `MemoryRouter` con rutas de mentira.

### 5.4 El grafo de navegación real no se testea

`App.test.tsx` tiene **un** test: que la raíz renderiza la puerta de entrada. Las ocho pantallas se testean aisladas, cada una con su `MemoryRouter` y destinos falsos del estilo `<Route path="/config" element={<div>config screen</div>} />`. Con ese patrón, "¿existe algún camino de clicks que lleve a `/history`?" es una pregunta **imposible de formular**, mucho menos de responder. De ahí F4, F5 y F6: no se escaparon de la red, es que no hay red en ese lado.

### 5.5 Los tests que existen validan renderizado, no comportamiento del sistema

De los 98 tests, la enorme mayoría responden "dado este estado, ¿aparece este texto?". Muy pocos responden "dada esta acción del usuario, ¿el sistema termina en el estado correcto?". Ese sesgo hace que la suite sea excelente detectando regresiones de presentación —de hecho detectó varias durante la limpieza de SonarCloud— y ciega ante regresiones de integración.

### 5.6 La causa raíz estructural: E2E está fuera de alcance por decisión

`.claude/rules/architecture/constraints.md`, sección "Scope V1.0 — lo que NO entra":

> - Tests end-to-end de UI automatizados (Selenium/Playwright)

Esa exclusión es **la** causa raíz. F1, F4, F5, F6 y F9 tienen algo en común: son exactamente el tipo de defecto que sólo aparece cuando el sistema completo corre junto y alguien lo recorre de punta a punta. La decisión de dejar esa capa afuera es defendible en costo, pero tiene una consecuencia que hay que aceptar explícitamente: **con esta pirámide de tests, que dos PRs pasen limpios y la aplicación esté rota no es un accidente — es el comportamiento esperado del proceso.** Revisar esa decisión es la recomendación principal de este informe.

### 5.7 El fallo de proceso, sin vueltas

`c27d6ac` cambió el ciclo de vida del stream y no se volvió a abrir el navegador después. La verificación E2E manual que `sprint.md` documenta con detalle quedó desactualizada el mismo día en que se escribió, por un commit posterior de la misma jornada. Ninguna herramienta automática iba a avisar. Es un problema de *definition of done*, no de código.

---

## 6. Cómo confirmar F1 en dos minutos, sin escribir nada

Antes de tocar código, dejá la evidencia registrada:

1. `docker-compose up -d backend postgres`
2. `cd frontend && npm run dev`
3. Abrir `http://localhost:5173`, entrar como anónimo, cargar un CSV y ejecutar.
4. **Pestaña Network, filtro Fetch/XHR.** Vas a ver `POST /api/v1/analysis/stream` con status `(cancelled)` o `(canceled)` a los pocos milisegundos. Ese "cancelled" es F1, en vivo.
5. Contraprueba: comentar `<StrictMode>` en `main.tsx`, recargar, repetir. El stream avanza. **Volver a descomentarlo inmediatamente** — sacar StrictMode no es el arreglo, es sólo la confirmación del diagnóstico.

El paso 5 es la prueba diferencial: una sola variable cambiada, un solo comportamiento distinto.

---

## 7. Siguiente paso

[`plan-arreglo-ui-rota.md`](plan-arreglo-ui-rota.md) — plan de arreglo en cuatro bloques priorizados, con el test que cubre cada arreglo y la estrategia de testing en cuatro capas que evita que esta clase de defecto se repita.
