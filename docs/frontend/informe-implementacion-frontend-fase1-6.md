# Informe de Implementación — Frontend METIS, Fases 1 a 6

**Fecha.** 28-29 de Julio de 2026.
**Alcance.** Auth end-to-end, Config + stream de Etapa 1, Resultados, Historial, Mocks de
Etapa 2, y una primera verificación E2E completa contra el backend real (Docker).
**Estado.** Fases 1-5 completas e implementadas; Fase 6 parcial (ver §6, Pendientes).
**Propósito de este documento.** Punto único de consulta para retomar el trabajo — pensado
para que lo lea tanto una persona como otra sesión de Claude Code sin contexto previo. La
fuente de verdad más detallada, decisión por decisión, sigue siendo
[`docs/frontend/frontend-implementation-plan.md`](./frontend-implementation-plan.md) §10 — este informe
resume y da un mapa de navegación, no lo reemplaza.

---

## 0. Cómo se llegó hasta acá

El plan (`frontend-implementation-plan.md`) define 6 fases incrementales. Al empezar esta
sesión, Fase 0 (scaffold Vite+React+TS, tema Instrumento, routing, CI) ya estaba mergeada a
`staging` de una sesión anterior. Esta sesión implementó Fases 1 a 5 de punta a punta y cerró
la mayor parte de Fase 6.

Commits, en orden (`git log staging`):

```
2afcc5d feat(frontend): implement Auth end-to-end (Fase 1)
17936d4 feat(frontend): implement Config + stream Etapa 1 (Fase 2)
4cab21c feat(frontend): implement Resultados Etapa 1 (Fase 3)
7894499 feat(frontend): implement Historial (Fase 4)
63dc605 feat(frontend): implement Etapa 2 mocks (Fase 5)
3374f73 fix(frontend): two useAnalysisStream bugs found by testing against the real backend
```

Magnitud total: **63 archivos tocados, ~5.700 líneas agregadas, 17 archivos de test nuevos,
119/119 tests pasando, lint y build limpios** en el estado final.

---

## 1. Resumen por fase

| Fase | Qué agrega | Estado | Verificado contra backend real |
|---|---|---|---|
| 1 — Auth | Login, registro, verificación, guards, logout | ✅ Completa | ✅ Login/logout/me sí; registro→verify bloqueado (sin SMTP, ver §6) |
| 2 — Config + Stream | SSE-sobre-fetch, timeline, modal de atípico | ✅ Completa | ✅ Incluido caso real con atípico |
| 3 — Resultados | 3 modos de presentación sobre `Etapa1Result` | ✅ Completa | ✅ Los tres modos, con datos reales |
| 4 — Historial | Lista paginada + detalle | ✅ Completa | ✅ Lista y detalle reales |
| 5 — Mocks Etapa 2 | Ranking, eventos de diseño, MSW | ✅ Completa | ✅ (es 100% mock por diseño — no aplica "backend real") |
| 6 — Pulido y a11y | Motion, contraste, foco/teclado, testing | ⚠️ Parcial | Ver §6 |

### 1.1 — Auth (Fase 1)

**Archivos clave:** `src/auth/AuthProvider.tsx`, `src/auth/guards.tsx`, `src/api/auth.ts`,
`src/api/client.ts` (agregó `ApiError`/`requestJson`), `src/routes/entry/EntryPage.tsx`,
`src/routes/auth-verify/AuthVerifyPage.tsx`.

Login/registro/anónimo en una sola pantalla (markup adaptado del prototipo real, no
inventado), `AuthProvider` con `fetch`+`useState` (sin React Query — decisión D4), guards
`RequireAuth`/`RedirectIfAuthed`. El flag de sesión anónima persiste en `localStorage`
(D7, mismo patrón que el tema).

### 1.2 — Config + Stream Etapa 1 (Fase 2)

**Archivos clave:** `src/api/sse.ts` (`useAnalysisStream`), `src/routes/config/ConfigPage.tsx`,
`src/routes/stream/StreamPage.tsx`.

SSE-sobre-fetch vía `@microsoft/fetch-event-source` (no `EventSource` nativo — el stream es un
POST multipart). Reducer de estado por `fase` (`idle/streaming/waiting_outlier/done/error`),
con manejo de `iteracion` para que una re-ejecución tras rechazar un atípico reemplace
resultados en vez de acumularlos. Config pasa el formulario armado a Stream vía router state
(D9 — sin context dedicado). Sin preview de CSV (D10 — columnas son inputs de texto planos).

### 1.3 — Resultados Etapa 1 (Fase 3)

**Archivos clave:** `src/routes/results/Etapa1ResultView.tsx` (extraído en Fase 4, ver 1.4),
`src/routes/results/ResultsPage.tsx`.

Banner de `nivel_confianza`, KPIs de independencia/homogeneidad, descriptivos, warnings, y los
4 grupos de pruebas. Paso a paso = `<details>` colapsado; experto/anónimo = tarjetas siempre
abiertas — misma data, distinto widget (D15). **Sin sustitución de fórmulas ni gráficos**
(D14/D16): el backend no expone las cantidades intermedias ni la serie cruda, y fabricarlas
sería inventar contenido estadístico no respaldado — the fórmulas con valores sustituidos son
un requisito real, pero de la exportación PDF, no de esta pantalla.

### 1.4 — Historial (Fase 4)

**Archivos clave:** `src/api/history.ts`, `src/routes/history/HistoryPage.tsx`,
`src/routes/history/HistoryDetailPage.tsx`.

Lista con paginación 100% client-side (el backend devuelve un array plano, D18). El detalle
reutiliza `Etapa1ResultView` (extraído de `ResultsPage` en esta fase, D17) porque
`GET /history/{id}` devuelve el mismo shape de `Etapa1Result`. A diferencia de `ResultsPage`,
el `modo` viene de `AnalysisDetail.modo` persistido, no de router state — esta ruta es
bookmarkeable/recargable por URL.

### 1.5 — Mocks de Etapa 2 (Fase 5)

**Archivos clave:** `src/mocks/` (handlers, browser, etapa2.mock, designEvents.mock,
PendingBadge), `src/api/etapa2.ts`, `src/routes/ranking/RankingPage.tsx`,
`src/routes/design-events/DesignEventsPage.tsx`.

`RankingPage` usa datos mock **directos, sin red** — el ranking nunca tuvo un endpoint REST
documentado (solo existe como evento SSE que el backend nunca emite), así que no había ningún
contrato real que interceptar (D19). `DesignEventsPage` sí llama al endpoint real documentado
(`POST /analysis/design-events`, no implementado en el backend) y ahí MSW sí aporta valor real,
interceptándolo en el navegador de dev. Ninguna distribución se etiqueta "óptima/recomendada/
ganadora" (constraints.md) — solo el hecho objetivo "menor EEA" en la primera. MSW **no** se usó
en los tests (D20) — mismo mecanismo `vi.stubGlobal("fetch")` que el resto de la suite, para no
correr dos interceptores de red distintos en el mismo proceso de test.

### 1.6 — Verificación E2E contra el backend real (fuera de las 6 fases nominales)

Con Docker Desktop encendido pero el stack sin levantar, se completó por primera vez el
backlog de verificación diferido durante Fases 1-5 (ver `frontend-implementation-plan.md` §10,
"P4" a "P7"):

1. `.env` creado desde `.env.example` (sin SMTP real).
2. `docker-compose up --build backend postgres` + `alembic upgrade head` (vía `docker exec`,
   evita instalar Alembic en el host).
3. Usuario verificado insertado directo en Postgres (bcrypt generado con el Python del propio
   contenedor backend) — sin SMTP no hay forma de pasar por `/register`.
4. Verificado en el navegador real, contra la API real: login/logout/me, Config→Stream con un
   CSV sintético de 40 años (uno de ellos deliberadamente extremo para forzar a Chow),
   modal de atípico real, `resolveOutlier` real, los tres modos de Resultados, e Historial
   lista+detalle.
5. Usuario de prueba y sus 6 análisis borrados de Postgres al cerrar.

Esta verificación encontró y corrigió **2 bugs reales** — ver §2.

---

## 2. Bugs encontrados y corregidos

Ninguno de los dos fue detectado por los tests unitarios de Fase 2 porque ninguno ejercitó la
secuencia exacta de eventos que el backend real manda — es exactamente el valor de haber hecho
esta verificación en vez de seguir postergándola.

### Bug 1 — `complete` pisaba `fase="error"` con `"done"`

**Archivo:** `src/api/sse.ts`, reducer `handleEvent`, caso `"complete"`.
**Síntoma real:** un CSV con años como enteros crudos (`1980` en vez de `1980-01-01`) disparó
`CONTRACT_NO_TEMPORAL_RESOLUTION` real del backend — pero la UI mostró "Análisis completo" en
vez del banner de error.
**Causa:** el backend manda `complete` inmediatamente después de `contract_error` también
(ya documentado en `frontend-integration.md` §4), pero el `case "complete"` seteaba
`fase:"done"` sin condición, pisando el `fase:"error"` que el evento anterior ya había puesto.
**Corrección:** `complete` ahora no hace nada si `fase` ya es `"error"`.
**Test de regresión:** `sse.test.ts`, `"does not let the complete event that always follows
contract_error overwrite fase=error with done"`.

### Bug 2 — `result_etapa1` nunca llegaba a `state.result`

**Archivo:** `src/api/sse.ts`, función `onmessage`.
**Síntoma real:** toda la pantalla de Resultados redirigía sola de vuelta a `/config` — el
guard de "sin resultado, no hay nada que mostrar" se disparaba siempre, incluso con un análisis
recién completado.
**Causa:** el payload real de `result_etapa1` es el `Etapa1Result` crudo (campos `contract`,
`descriptive`, `independencia`, etc. sueltos), **no** envuelto en `{result: {...}}` — confirmado
inspeccionando un frame SSE real vía `fetch` manual en la consola del navegador. El propio
comentario del plan (`frontend-implementation-plan.md` §2.1) ya decía "envuelto al parsear,
data = Etapa1Result crudo" pero la implementación construía todos los eventos genéricamente
(`{type: ev.event, ...payload}`), así que `event.result` quedaba siempre `undefined`.
**Corrección:** `onmessage` ahora arma `result_etapa1` como caso especial:
`{ type: "result_etapa1", result: payload }`.
**Test de regresión:** `sse.test.ts`, `"unwraps result_etapa1 correctly"`.

---

## 3. Problemas encontrados a mitad de camino (no son bugs de código)

- **SMTP no disponible.** Sin credenciales reales, `POST /register` falla completo (no crea
  usuario ni token) — confirmado que el mecanismo de "leer el token de los logs" que documentaba
  `sprint.md` ya no existe desde que Auth Parte 2 reemplazó el mock por envío real (19/07/2026).
  Corregido en `sprint.md`. Workaround para probar el resto del flujo: usuario insertado directo
  en Postgres vía `psql` (documentado como técnica reutilizable en `sprint.md`).
- **Confusión de directorio de trabajo en la herramienta de shell.** `npm install -D msw` y
  `npx msw init` se corrieron por error desde la raíz del repo en vez de `frontend/`, creando un
  `package.json`/`node_modules`/`public/` espurios en la raíz. Detectado de inmediato con
  `git status` (todo quedó sin trackear, nada del usuario en riesgo), limpiado, y repetido
  correctamente dentro de `frontend/`.
- **`curl` vía Git Bash no pudo reproducir el stream.** Un intento de diagnosticar el stream con
  `curl -F "archivo=@/tmp/serie.csv"` falló con exit code 26 (error de lectura), aparentemente
  por cómo Git Bash traduce paths POSIX. Se abandonó ese camino y se usó `fetch()` manual desde
  la consola del navegador real en su lugar — más representativo del código de producción de
  todas formas.
- **Falsos positivos por batching de React durante pruebas manuales.** Dos `.click()` sucesivos
  en el mismo script (elegir "Experto" y después "Ejecutar análisis") no le daban a React lugar
  para re-renderizar entre uno y otro, así que el segundo click veía el estado viejo. No es un
  bug de producción — un usuario real con dos clicks de mouse separados no lo dispara. Se
  corrigió separando ambas acciones en llamadas de herramienta distintas.
- **Lectura de output de proceso en background poco fiable.** Un `docker-compose up` corrido en
  background con el archivo de salida redirigido quedó vacío incluso con los contenedores ya
  arriba — se verificó el estado real con `docker ps`/`docker logs` directamente en vez de
  confiar en el archivo de salida.

---

## 4. Decisiones tomadas — índice

Detalle completo de cada una (contexto, alternativas evaluadas, justificación) en
[`frontend-implementation-plan.md`](./frontend-implementation-plan.md) §10. Resumen:

| # | Resumen | Fase |
|---|---|---|
| D1-D3 | SSE-sobre-fetch (`@microsoft/fetch-event-source`), proxy de Vite para CORS en dev, MSW para mocks | 0 (previas a esta sesión) |
| D4 | `AuthProvider` con `fetch`+`useState`, sin React Query todavía | 1 |
| D5 | Sin MSW en los tests — mismo patrón `vi.stubGlobal("fetch")` en toda la suite | 1 |
| D6 | Workaround de dev para el 500 de `register` sin tocar el backend (banner honesto, no "revisá los logs") | 1 |
| D7 | Flag anónimo persistido en `localStorage` | 1 |
| D8 | Markup de `EntryPage` adaptado del prototipo real, no inventado | 1 |
| D9 | Router state en vez de un context de config dedicado | 2 |
| D10 | Sin preview de CSV en Config (columnas como texto plano) | 2 |
| D11 | Timeline agrupado en 4 bloques (no 8 pruebas sueltas) | 2 |
| D12 | Finalización del stream es un paso manual ("Ver resultados"), no auto-redirect | 2 |
| D13 | `sse.test.ts` mockea `@microsoft/fetch-event-source` a nivel de librería | 2 |
| D14 | Sin sustitución de fórmulas en Resultados (dato no disponible; sí aplica a export PDF) | 3 |
| D15 | Paso a paso = `<details>`; experto/anónimo = tarjetas planas — misma data | 3 |
| D16 | Sin gráficos en Resultados (la serie cruda no viaja por ningún canal) | 3 |
| D17 | `Etapa1ResultView` extraído para reutilizar entre Resultados e Historial | 4 |
| D18 | Paginación 100% client-side (backend no pagina) | 4 |
| D19 | MSW solo intercepta `design-events` (contrato real) — ranking no tiene contrato REST que interceptar | 5 |
| D20 | MSW no se usa en tests, solo en el navegador de dev | 5 |

---

## 5. Cobertura de tests

119 tests en 22 archivos, todos verdes; lint y build limpios en cada fase (verificado
incrementalmente, no solo al final). Patrón único de mock en toda la suite:
`vi.stubGlobal("fetch", ...)` — nunca MSW en tests (D5/D20), nunca dos mecanismos de
interceptación de red conviviendo en el mismo archivo.

---

## 6. Pendientes

### Fase 6 — Pulido y a11y (parcial)

- **Foco/teclado en el modal de atípico** (`StreamPage.tsx`, el `<div role="dialog">` del
  atípico): falta trap de foco, auto-foco al abrir, y cierre con Escape.
- **Revisión de contraste WCAG** sobre los tokens de `tokens.instrumento.css` — no se hizo
  todavía una pasada formal.
- Lo que **sí** quedó cerrado de Fase 6: Vitest en verde, lint limpio, y el flujo CU-01/CU-02
  recorrido manualmente contra el backend real (§1.6).

### Backlog de verificación E2E — casi cerrado

- **P4 (registro→verify) sigue bloqueado** — depende exclusivamente de credenciales SMTP reales
  que no están disponibles. No es algo que se pueda resolver sin esas credenciales.
- P5, P6, P7 — **cerrados** en esta sesión (§1.6).

### Otros pendientes ya documentados en `frontend-implementation-plan.md` §10

- **P1** — CORS real para producción (nginx + cookie `Secure`), bloquea deploy, no desarrollo.
- **P3** — Azul institucional UCC pendiente de confirmar contra el manual de marca.

---

## 7. Cómo continuar — para quien retome esto (persona o agente)

1. Leer `CLAUDE.md` (comandos, estructura) y `frontend-implementation-plan.md` completo
   (plan original + §10 con las 20 decisiones en detalle).
2. Si se van a hacer más pruebas contra el backend real: `.env` ya existe en la raíz (no
   commiteado, en `.gitignore`) con SMTP en placeholder. `docker-compose up backend postgres`
   más `docker exec <backend> alembic upgrade head` lo levantan. Ver `sprint.md`,
   "Entorno de desarrollo — datos de prueba" para la técnica de insertar un usuario verificado
   sin pasar por `/register`.
3. Para cerrar Fase 6: agregar trap de foco + Escape al modal de `StreamPage.tsx` (revisar
   patrones estándar de diálogo accesible — por ejemplo `inert` en el resto del DOM o una
   librería mínima de foco), y una pasada de contraste sobre `tokens.instrumento.css` claro y
   oscuro.
4. P4 (registro→verify) solo se cierra con credenciales SMTP reales — no hay atajo de
   ingeniería que lo resuelva.
5. Todo el resto del plan de 6 fases está implementado y verificado. Fase 6 restante es
   pulido, no funcionalidad faltante.
