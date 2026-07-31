# Informe de Resultados — Arreglo de UI Rota en Uso Real (cierre)

**Fecha.** 31 de Julio de 2026.
**Alcance ejecutado.** [`informe-diagnostico-ui-rota.md`](./informe-diagnostico-ui-rota.md) (doce
defectos F1-F12, diagnosticados el mismo día) + [`plan-arreglo-ui-rota.md`](./plan-arreglo-ui-rota.md)
— Bloques 0, 1, 2, 3 completos. Bloque 4.3 (E2E Playwright) y el ítem 1.3(b) del plan (escotilla
SMTP de desarrollo) **diferidos, ver §4** — ambos requieren una DECISIÓN nueva antes de
implementarse, no se avanzó sobre ninguno de los dos.
**Rama.** `fix/frontend-ui-integracion`, abierta desde `origin/staging` (no desde
`fix/frontend-pasada2`, que ya estaba mergeada a `staging` vía PR #18 al momento de abrir esta
rama — ver §2). 18 commits nuevos.
**Propósito de este documento.** Punto único de retoma de esta pasada, mismo formato que
[`informe-pasada2-resultados.md`](./informe-pasada2-resultados.md) e
[`informe-pasada3-resultados.md`](./informe-pasada3-resultados.md).

---

## 0. Resultado por ítem

Ninguno omitido. Los doce defectos del informe de diagnóstico (F1-F12) quedan cerrados salvo el
componente de F2 que requiere decisión (ver Bloque 1.3(b) en la tabla).

### Bloque 0 — Reproducir antes de arreglar

| # | Estado | Resultado |
|---|---|---|
| 0.1 | Hecho | `StreamPage.lifecycle.test.tsx` — componente y hook reales bajo `StrictMode`, con `fetchEventSource` mockeado. Confirmado en rojo contra el código real: `expected +0 to be 1` y `expected "spy" to not be called at all, but actually been called 1 times` — este segundo fallo es más revelador de lo que anticipaba el informe (el `AbortController` queda "gastado" por la limpieza fantasma de StrictMode; ni siquiera un desmontaje real vuelve a disparar `abort`). |
| 0.2 | Hecho | Confirmación manual en navegador: `POST /analysis/stream` → `net::ERR_ABORTED` en la pestaña Network, pantalla congelada en "Análisis en vivo" con los 4 grupos en `pending` y 0% de progreso. Contraprueba diferencial: comentar `<StrictMode>` en `main.tsx` (temporalmente) dejó que el mismo flujo llegara al backend y devolviera una respuesta real; revertido de inmediato. |

### Bloque 1 — Bloqueantes (P0)

| # | Estado | Resultado |
|---|---|---|
| 1.3(a) | Hecho | `scripts/seed-dev-user.sh` + `scripts/clean-dev-user.sh` — automatizan el INSERT bcrypt que `sprint.md` ya documentaba en prosa, vía `docker compose exec <servicio>` (no nombres de contenedor hardcodeados, evita la trampa de prefijo que `sprint.md` ya había documentado una vez). Verificado end-to-end: login real contra el backend con el usuario sembrado. |
| 1.3(b) | **Diferido — requiere DECISIÓN.** | Escotilla de desarrollo en `auth/email.py` para no depender solo del script (a). Toca DECISIÓN 032 (mandar el mail antes del commit) — no se implementa sin escribir `docs/decisiones/decision045.md` primero, con las alternativas evaluadas (escotilla por `ENV`, MailHog en `docker-compose`, o dejarlo como está). No escrita todavía. |
| 1.1+1.2 (F1) | Hecho | `StreamPage.tsx`: un solo efecto, limpieza colocada en el mismo efecto — la guarda `startedRef` de dos efectos separados es lo que rompía bajo el doble montaje de StrictMode. `sse.ts::onclose`: pasa a `fase="error"` con código nuevo `STREAM_CLOSED_EARLY` si el servidor cierra sin `complete` antes. Catálogo (`api-contracts.md` + `i18n/errors.es.ts`) actualizado en el mismo commit (DECISIÓN 038), verificado por `scripts/check-error-catalog.sh`. Verificado en vivo: patrón `ERR_ABORTED`→`200` esperado bajo StrictMode, stream llega a "Análisis completo". |
| 1.4 (F3) | Hecho | `AuthProvider.refetch()` distingue 401 legítimo (no hay sesión) de un fallo real (red caída, CORS, 500) — solo el segundo caso relanza. `login()` ahora puede lanzar y lo hace con `SESSION_NOT_ESTABLISHED` (código nuevo, mismo catálogo) si `/me` no confirma la sesión tras un `POST /login` 200. El efecto de montaje envuelto en su propio `try/catch` para no dejar la app colgada en el spinner si el backend está caído al arrancar. |

### Capa 2 de testing (4.1 + 4.2)

| # | Estado | Resultado |
|---|---|---|
| 4.1 | Hecho | `frontend/src/test/renderPage.tsx` — helper mínimo, `render(<StrictMode>{tree}</StrictMode>)`. Los 9 archivos de test de página migrados a usarlo. Único ajuste de comportamiento real: `StreamPage.test.tsx` (mockea el hook entero) asumía conteos de `start()`/`abort()` sin StrictMode — reescrito como el mismo invariante neto que usa el test de Bloque 0 (`start − abort` en vez de un conteo crudo). Ningún otro archivo reveló un bug propio de StrictMode en esta pasada. |
| 4.2(a) | Hecho | `StreamPage.integration.test.tsx` — componente y hook reales, red interceptada solo en el borde (`@microsoft/fetch-event-source` mockeado). **Desviación del plan, documentada inline:** el plan proponía MSW devolviendo un `ReadableStream` SSE en Node para esta capa, marcándolo como lo más delicado. Se optó por el mismo mecanismo que ya usan `StreamPage.lifecycle.test.tsx` y `sse.test.ts` — logra el mismo objetivo (componente + hook reales) sin apartarse del patrón único de mock de red que DECISIÓN 041 ya había fijado para toda la suite. Cuatro escenarios: camino feliz, atípico con re-ejecución (iteracion:2 reemplaza sin duplicar), contrato bloqueante (`complete` no pisa `fase="error"`), cierre sin `complete` (`STREAM_CLOSED_EARLY`). |
| 4.2(b) | Hecho | `routes.navigation.test.tsx` — `createMemoryRouter(routes)` sobre el array real de `routes.tsx`, no rutas de mentira por archivo. Tres escenarios: anónimo de punta a punta (entrada→config→stream→resultados→ranking→eventos de diseño), autenticado (login real→config; Historial→detalle; Cerrar sesión→entrada), y sin sesión (navegación directa a `/config` redirige — confirma F7 desde la raíz del árbol). Cierra F4/F5/F6/F7 y el camino feliz de login que el informe señalaba como no testeado (§5.3) de una sola pasada. |

### Bloque 2 — Navegación (P1)

| # | Estado | Resultado |
|---|---|---|
| 2.1 (F4/F5/F6) | Hecho | `TopBar` con links reales según sesión: sin sesión → nada; anónimo → "Nuevo análisis" + "Salir"; autenticado → "Nuevo análisis" + "Historial" + "Cerrar sesión". Ambos "Cerrar sesión"/"Salir" navegan a `/` tras su efecto (`await logout()` / `exitAnonymously()`), en vez de dejar al usuario en la misma pantalla. `exitAnonymously()` nuevo en `AuthProvider` (antes solo `logout()` limpiaba el flag `metis-anon-session`, incidentalmente). Verificado en vivo: Historial lista análisis reales, Cerrar sesión redirige. |
| 2.2 (F5) | Hecho | Botón "Continuar a Etapa 2 ▸" en `ResultsPage`, navega a `/ranking`, con `PendingBadge` al lado (Etapa 2 sigue mockeada server-side, DECISIÓN 042 — se decidió mostrar el flujo completo en vez de ocultarlo). Verificado en vivo desde resultados reales de Etapa 1. |
| 2.3 (F7) | Hecho | Guard nuevo `RequireSession` (autenticado o anónimo) en `/config`, `/stream`, `/results`, `/ranking`, `/design-events`. No reintroduce una distinción CU-01/CU-02 por ruta — ambas sesiones pasan, solo "sin sesión" se bloquea. Verificado en vivo: navegar directo a `/config` sin sesión redirige a la puerta de entrada. |
| 2.4 (F8) | Hecho | Timeline de `StreamPage`: `disabled` nativo reemplazado por `aria-disabled` + pill "esperando resultados" en vez de nada — antes un paso sin resultados todavía y uno roto se veían idénticos. La mitad de F8 sobre Cramer "Personalizada" resultó ya resuelta: el `<p class="fn">` visible ya existía en el commit exacto que el informe analizó (verificado con `git show`), la afirmación del informe sobre `title=` como única explicación no se sostenía del todo. |

### Bloque 3 — Infraestructura (P2)

| # | Estado | Resultado |
|---|---|---|
| 3.1 (F9) | Hecho | `frontend/Dockerfile` (multi-stage: `node:22-alpine` build + `nginx:alpine` sirviendo `dist/` con `try_files $uri /index.html`, obligatorio por `createBrowserRouter`) + `frontend/nginx.conf` + `frontend/.dockerignore`. **Verificado end-to-end por primera vez en la historia del proyecto:** `docker-compose up -d` levanta los cuatro servicios; a través de nginx, `GET /` → 200 con HTML real, `/config` → 200 (fallback SPA), login real funcionando same-origin desde `http://localhost` (no `:5173`). |
| 3.2 (F10) | Hecho | Default de CORS en `main.py` corregido de `:3000` (puerto que ningún escenario real usa) a `:5173`. El resto del ítem del plan ("unificar FRONTEND_ORIGIN/FRONTEND_URL en una sola variable") resultó innecesario: `.env`/`.env.example` ya documentaban ambas como conceptos intencionalmente separados (CORS vs. link de mail), con valores ya correctos y sincronizados — verificado antes de tocar nada. Verificado: 131 tests backend en verde, preflight CORS real contra el contenedor reconstruido. |
| 3.3 (F11) | Hecho | `nginx.conf`: `location /ping` agregada antes de `location /`, mismos headers de proxy que `/api/`. Sintaxis validada con `nginx -t` en un contenedor descartable antes de que existiera 3.1 (sin upstream real todavía); re-verificado end-to-end una vez que 3.1 permitió levantar el stack completo — `/ping` devuelve `{"status":"ok"}` real a través de nginx. |
| 3.4 (F12) | Hecho | `.catch()` agregado a `postDesignEvents(...)` en `DesignEventsPage.tsx` — un rechazo dejaba la pantalla colgada para siempre en "Calculando eventos de diseño…" con un unhandled rejection. Barrido del resto de `src/` confirmó que era el único `.then()` sin `.catch()` pareado. |

### Documentación de cierre

| # | Estado | Resultado |
|---|---|---|
| Docs | Hecho | `sprint.md` — tachada (no borrada) la verificación E2E de "feature/frontend-fases1-5" invalidada por `c27d6ac`, nueva sección resumiendo esta rama. `testing.md` — sección nueva "Testing del frontend" (separada de los cuatro niveles del anteproyecto, que son del backend). `architecture.md` — nota de "Nginx como reverse proxy" actualizada: el build estático ya existe y corre. `api-contracts.md` — `STREAM_CLOSED_EARLY` y `SESSION_NOT_ESTABLISHED` catalogados (ya reflejado en los ítems 1.1/1.2 y 1.4 de arriba). |

**Números de decisión:** ninguno nuevo escrito en esta pasada (045 y 046 quedan reservados
conceptualmente por el plan, sin archivo — ver §4).

---

## 1. Premisas del plan que resultaron incorrectas o necesitaron ajuste

- **Cramer "Personalizada" (F8) ya estaba resuelto en la mitad que importaba.** El informe de
  diagnóstico decía que la única explicación del botón deshabilitado vivía en `title=` ("invisible
  salvo hover"). `git show` contra el commit exacto que el informe analizó (`faf134c`) mostró que el
  `<p class="fn">La partición personalizada no está disponible todavía.</p>` **ya existía**, visible
  por defecto (sin CSS que lo oculte hasta hover). El plan mismo ya lo reconocía de pasada ("ya
  existe el `<p class="fn">`"), pero el informe de diagnóstico no. Verificado antes de tocar nada —
  no se hizo ningún cambio ahí.
- **MSW-en-Node para la Capa 2 de testing, evitado a propósito.** El plan marcaba esa vía como "lo
  técnicamente más delicado" y dejaba explícitamente habilitado un plan B (mockear el módulo
  directamente). Se fue directo al plan B: logra el mismo objetivo sin el riesgo, y sin apartarse
  del patrón único de mock de red que DECISIÓN 041 ya había fijado para toda la suite.
- **F10 no era "dos variables para el mismo concepto".** El informe de diagnóstico leía
  `FRONTEND_ORIGIN`/`FRONTEND_URL` como una duplicación a unificar. `.env`/`.env.example` ya las
  documentaban como dos variables intencionalmente separadas (CORS vs. link de verificación por
  mail), ambas requeridas, con valores ya sincronizados en `http://localhost:5173`. El único defecto
  real era un default hardcodeado inconsistente en el código Python (`main.py` decía `:3000`) —  se
  corrigió eso puntualmente, no se tocó el diseño de dos variables.

## 2. Estado real para retomar — importante

**`fix/frontend-ui-integracion` no está pusheada a `origin` ni hay PR abierto.** 18 commits nuevos
sobre `origin/staging`, todos locales a este checkout:

```
6faffdb docs: note frontend's single fetch-mock testing convention
e9c1068 docs(frontend): diagnóstico de UI rota en uso real + plan de arreglo
3ce3aae test(frontend): Bloque 0 - regression test for F1, red before fixing
a3e4ade feat(dev): Bloque 1.3(a) - scripts/seed-dev-user.sh + clean-dev-user.sh
5968713 fix(frontend): Bloque 1.1+1.2 - fix F1, single-effect stream lifecycle
3a6c8ab fix(frontend): Bloque 1.4 - fix F3, session failures were invisible
cfbd4dd test(frontend): Bloque 4.1 - render every page test under StrictMode
9d0725b test(frontend): Bloque 4.2(a) - end-to-end stream integration test
38ed523 fix(frontend): Bloque 2.1 - real navigation in TopBar (F4, F5, F6)
b9079ea fix(frontend): Bloque 2.2 - reach Etapa 2 from Results (F5)
ba31bbc fix(frontend): Bloque 2.3 - RequireSession guard on the pipeline routes (F7)
c33e86f fix(frontend): Bloque 2.4 - pending timeline steps look waiting, not broken (F8)
0d06369 test(frontend): Bloque 4.2(b) - navigation graph test over real routes.tsx
76fc6fc fix(frontend): Bloque 3.4 - .catch() on DesignEventsPage's request (F12)
b824564 fix(backend): Bloque 3.2 - correct CORS default origin to match reality (F10)
3029080 fix(infra): Bloque 3.3 - nginx proxies /ping to the backend (F11)
a51d395 feat(infra): Bloque 3.1 - add frontend/Dockerfile (F9)
ad522be docs: close the fix/frontend-ui-integracion pass
```

(El primer commit, `6faffdb`, es una nota de documentación de una tarea `/init` previa en la misma
sesión — sin relación con el arreglo de UI, pero vive en la misma rama por orden cronológico.)

Antes de que este trabajo sea visible fuera de este checkout:

1. Pushear la rama y abrir un PR hacia `staging` (el plan original recomendaba dividir en 3 PRs por
   bloque — no se hizo así en esta pasada; los 18 commits quedaron en una sola rama, decisión a
   confirmar con Kevin/Octavio antes de abrir el/los PR).
2. Confirmar que los tres jobs de CI (`lint`, `test`, `frontend`) y el job `error-catalog` pasan.
3. El stack de Docker completo (`backend`, `postgres`, `frontend`, `nginx`) quedó arriba en esta
   máquina para la verificación de F9/F11 — el usuario de desarrollo sembrado para las pruebas
   manuales fue borrado (`scripts/clean-dev-user.sh`) antes de cerrar.

## 3. Verificación final — salida real

### Frontend
```
$ npx vitest run
Test Files  25 passed (25)
     Tests  147 passed (147)

$ npm run lint
(sin salida — limpio)

$ npm run build
✓ built in <1s
```

### Backend (vía Docker — `pi_metis-backend-1`, reconstruido tras el fix de F10)
```
$ docker exec pi_metis-backend-1 ruff check metis/
All checks passed!

$ docker exec pi_metis-backend-1 ruff format --check metis/
64 files already formatted

$ docker exec pi_metis-backend-1 pytest -m unit -q
131 passed, 1 skipped
```

### Catálogo de códigos de error — las tres direcciones
```
$ ./scripts/check-error-catalog.sh
OK — backend emite, ausente del catálogo
OK — catálogo, ausente del diccionario del frontend
OK — diccionario del frontend, ausente del catálogo

Catálogo de códigos de error sincronizado en las tres direcciones.
```

### Stack completo vía nginx (F9/F11, `docker-compose up -d`)
```
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost/
200
$ curl -s http://localhost/ping
{"status":"ok"}
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost/config
200
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost/api/v1/auth/me
401
```
Login real verificado en el navegador contra `http://localhost` (no `:5173`) con el usuario
sembrado — llega a `/config` autenticado, same-origin, sin CORS de por medio.

### Verificación manual en navegador (evidencia de F1, F3-F8, F9)

Documentada inline en cada commit correspondiente (Network tab, page text, y en el caso de F1 la
contraprueba diferencial de `<StrictMode>`) — no repetida acá en detalle para no duplicar; ver los
mensajes de commit de la lista de §2.

---

## 4. Qué queda pendiente

- **Pushear la rama y abrir PR(s) hacia `staging`** — no hecho en esta pasada, ver §2.
- **DECISIÓN 045** (escotilla SMTP de desarrollo, ítem 1.3(b) del plan) — no escrita. Sin ella,
  `auth/email.py` sigue sin una vía de desarrollo alternativa al script de seed; el script ya
  desbloquea CU-01 completo, así que esto no es bloqueante para nada más.
- **DECISIÓN 046** (E2E con Playwright, Bloque 4.3 del plan) — no escrita. Contradice
  `constraints.md` tal como está hoy ("Scope V1.0 — lo que NO entra" excluye E2E automatizado);
  cinco de los doce defectos de esta pasada (F1, F4, F5, F6, F9) solo eran detectables desde esa
  capa, así que el argumento a favor de revisar la exclusión sigue en pie, pero no se escribió.
- **DECISIÓN 043** (contraste WCAG del tema Instrumento) — pendiente de antes de esta pasada, sin
  tocar acá, sigue esperando decisión de Kevin/Octavio.
- **Feedback de UX/diseño recibido al probar esta rama en vivo** — capturado por separado en
  [`feedback-ux-pendiente-analisis.md`](./feedback-ux-pendiente-analisis.md). Explícitamente no
  implementado todavía — es una lista para analizar, no un plan decidido.
