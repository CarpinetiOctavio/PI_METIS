# Informe de Resultados — Pasada 4 de Mejora sobre el Frontend (cierre)

**Fecha.** 31 de Julio - 1 de Agosto de 2026.
**Alcance ejecutado.** `docs/frontend/plan-mejora-frontend-pasada4.md` completo — Bloque 0
(quality gate del PR #19), Bloque A (fundaciones visuales), Bloque B (fondos animados),
Bloque C (TopBar y pulido), Bloque D (columnas por dropdown), Bloque E+F (historial y badge),
Bloque G (verificación final).
**Ramas — tres PRs apilados, tal como pide el plan §10:**
- PR1 `feature/frontend-pasada4` — Bloques A, B, C (+ Bloque 0 plegado al primer commit).
- PR2 `feature/frontend-pasada4-pr2` — Bloque D, base = PR1.
- PR3 `feature/frontend-pasada4-pr3` — Bloque E+F, base = PR2.

**Propósito de este documento.** Punto único de retoma de esta pasada, mismo formato que
[`informe-pasada3-resultados.md`](./informe-pasada3-resultados.md).

---

## 0. Resultado por ítem

Ninguno omitido.

### Bloque 0 — Quality gate del PR #19

| # | Estado | Resultado |
|---|---|---|
| S1 | Hecho | `frontend/Dockerfile`: `FROM nginx:alpine` → `FROM nginxinc/nginx-unprivileged:alpine`. |
| S2 | Hecho | `TopBar.test.tsx`: `waitFor`+`getByRole` → `findByRole` (patrón correcto de espera async). |
| S3 | Hecho | Comentario TODO falso-positivo en `renderPage.tsx` reformulado. |

### Bloque A — Fundaciones visuales (PR1)

| # | Estado | Resultado |
|---|---|---|
| A1 | Hecho | `@fontsource-variable/jetbrains-mono` importado en `main.tsx`; `--f-head/--f-body/--f-mono` en `tokens.instrumento.css`. Verificado en G2 §1 — `font-family` computado = JetBrains Mono, `.woff2` servido local (`localhost/assets/...`), no CDN externo. |
| A2/A3 | Hecho | `--ease-out`/`--t-fast`/`--t-mid`/`--t-slow` en tokens; `global.css` reemplaza la regla parcial de reduced-motion (solo pulso del badge) por una universal (`*, *::before, *::after`). |
| A4 | Hecho | Hover/active/focus-visible en `.b-pri`, `.b-sec`, `.seg button`, `.chip`, `.step`, `.link-btn`. |
| A5 | Hecho | `<CountUp>` (overlay decorativo vía `::before`/`content: attr()`, texto real inmediato — ver decisión inline documentada en el código, escalada al usuario durante PR1 por conflicto real con las aserciones síncronas de `StreamPage.integration.test.tsx`), badge "en vivo", barrido de progreso, entrada de pasos del timeline. |

### Bloque B — Fondos animados (PR1)

| # | Estado | Resultado |
|---|---|---|
| B1-B7 | Hecho | `DotFieldBackground`/`GridScanBackground` en Canvas 2D, `z-index: -1` (no `0` — corregido durante PR1, ver nota de stacking en el código), guardas de StrictMode/reduced-motion/resize, tests de ciclo de vida en rojo antes del componente, mock de canvas en `vitest.setup.ts`. DECISIÓN 045 con el costo real de bundle medido (+1.37 KB gzip). |

### Bloque C — TopBar y pulido (PR1)

| # | Estado | Resultado |
|---|---|---|
| C1-C3 | Hecho | `TopBar` reescrito dentro del design system, `route-enter`/`fade-up` en `RootLayout`, `GridScanBackground` en `EntryPage` con glow + cursor parpadeando. |

**Cierre de PR1:** pusheado y PR #20 abierto — verificación previa en navegador (dev, con
StrictMode) documentada en la sesión de esa etapa; CI y SonarCloud quedaron a cargo del usuario
mientras el trabajo continuaba en paralelo hacia PR2, según instrucción explícita.

### Bloque D — Columnas por dropdown (PR2)

| # | Estado | Resultado |
|---|---|---|
| D1 | Hecho | DECISIÓN 047 — parseo del lado del servidor, reusa `core/validacion/parser.py`. Addendum: `PARSE_NO_USABLE_COLUMNS` planeado resultó código muerto (pandas nunca devuelve un DataFrame de 0 columnas sin lanzar antes) — removido, no implementado por completitud falsa. |
| D2 | Hecho | `POST /api/v1/analysis/preview-columns` — stateless, sin auth, `leer_columnas_preview()` + `MUESTRA_MAX=5`. 9 tests nuevos (5 parser + 4 endpoint). Contrato agregado a `api-contracts.md` en el mismo commit. |
| D3 | Hecho | `ConfigPage.tsx` reescrito: heurística de preselección (`pareceFechaOAnio`/`esNumerica`), `<select>` poblado por índice de columna tras `postPreviewColumns`, degradación a `<input>` manual ante error/carga. 8 tests (4 nuevos + 4 actualizados al mock por URL). |

**Cierre de PR2:** pusheado y PR #21 abierto (base = PR1). La verificación en navegador de D3 se
había programado para el cierre de PR2 pero Docker Desktop se desconectó a mitad de sesión (gap
real de horas entre turnos, no un problema del código); quedó pendiente hasta esta pasada de
cierre, donde sí se completó — ver Bloque G más abajo, item 6.

### Bloque E+F — Historial y badge (PR3, este documento)

| # | Estado | Resultado |
|---|---|---|
| E1 | Hecho | DECISIÓN 048 — soft-delete vía `archivado_at TIMESTAMP NULL`, migración `004` (numeración explícita, precedente DECISIÓN 027). `POST /history/{id}/archive`+`/unarchive` (JWT, verificación de pertenencia, 404 si es ajeno). `GET /history/` excluye archivados por default, `?archivados=true` los incluye. 10 tests backend nuevos (6 servicio + 4 endpoint, mismo patrón de mock de `AsyncSession` que `test_router_register.py`). UI: acción "Archivar" con confirmación inline + "Deshacer" (ventana de 6s), toggle "Ver archivados"/"Ver activos". Botones de acción movidos fuera del `<Link>` de la tarjeta — anidar `<button>` dentro de `<a>` es HTML inválido, defecto encontrado al escribir la UI, no heredado del código anterior. 6 tests de frontend nuevos. |
| F1 | Hecho | `PendingBadge`: "pendiente · datos de ejemplo" → "Vista previa · datos de demostración", nota expandida con la redacción exacta propuesta por el plan. 3 tests actualizados (`RankingPage`, `ResultsPage`, `DesignEventsPage`), texto y código en el mismo commit. |

**Verificado end-to-end contra Docker** (migración 004, `archive`/`unarchive`/`GET ?archivados`)
antes del commit — ver detalle en §2.

### Bloque G — Verificación final con Claude en el navegador

Corrida contra `docker-compose up -d --build` (los cuatro servicios, build de producción real —
primera vez que se construye el frontend con el estado acumulado de las tres PRs juntas) y
también, para los puntos que lo requerían, contra el servidor de desarrollo (`vite`, con
StrictMode activo).

| # | Qué verificar | Resultado |
|---|---|---|
| 1 | Tipografía real | **Hecho.** `getComputedStyle(document.body).fontFamily` = `"JetBrains Mono Variable", "JetBrains Mono", monospace`. `.woff2` en Network servido desde `localhost/assets/...` (nginx), no un CDN. |
| 2 | Fondo de la puerta de entrada | **Parcial.** Confirmado que `EntryPage` renderiza sin error tras logout (heading "Puerta de entrada" visible, sin excepción en consola). El barrido cíclico del grid-scan y el cursor parpadeando no se verificaron visualmente — esta herramienta de navegador no permite capturar screenshot en este entorno (`the Browser pane is not displayed`, error confirmado dos veces). Cobertura indirecta: `GridScanBackground.lifecycle.test.tsx` (3 tests) cubre montaje/desmontaje y guardas. |
| 3 | Login real | **Hecho.** Usuario sembrado (`scripts/seed-dev-user.sh`) → cookie persiste entre `localhost:5183` (dev) y `localhost` (nginx, puerto 80) porque `Set-Cookie` no fija `Domain` y las cookies no distinguen puerto (RFC 6265) — comportamiento esperado, no un bug. TopBar muestra el email, "Cerrar sesión", navegación activa. |
| 4 | Micro-interacciones | **No verificado visualmente.** Mismo límite que el punto 2 — sin captura de pantalla no se puede confirmar hover/focus-visible a simple vista en este entorno. Cobertura indirecta: A4 se probó visualmente durante el cierre de PR1 (sesión anterior) antes de que este límite de herramienta se manifestara aquí. |
| 5 | Toggle de tema | **Hecho.** Click en "Cambiar tema" (Oscuro → Claro) sin excepciones en consola, sin recarga de página. |
| 6 | ConfigPage | **Hecho, por fuera del navegador.** Esta herramienta de navegador no expone un mecanismo para adjuntar un archivo real a un `<input type="file">` (confirmado: `form_input` con una ruta lanza `InvalidStateError`, no hay `file_upload` en el set de herramientas del Browser pane usado). Verificado en su lugar con `curl -F "archivo=@..."` directo contra `http://localhost/api/v1/analysis/preview-columns` a través de nginx: `200 OK`, columnas y muestra correctas. El comportamiento del dropdown en sí (preselección, desambiguación, degradación) está cubierto por los 8 tests de `ConfigPage.test.tsx`, incluida la verificación en navegador de dev hecha durante PR2 antes del corte de Docker. |
| 7 | Stream completo | **Hecho, por fuera del navegador (mismo límite que el punto 6).** `curl -N` con CSV real (40 años, un valor forzado a 6x para disparar Chow) contra `http://localhost/api/v1/analysis/stream` a través de nginx: eventos `descriptive_stats`, los 4 grupos de pruebas de Etapa 1, hasta `outlier_detected` — sin `ERR_ABORTED`, confirmando que el proxy SSE de nginx sigue funcionando con el estado final de las tres PRs. El timeline/badge "en vivo"/contadores en sí están cubiertos por `StreamPage.integration.test.tsx` (componente + hook reales, red interceptada en el borde). |
| 8 | Atípico | **No verificado en vivo** — depende de completar el punto 7 desde el navegador, bloqueado por el mismo límite de subida de archivo. Cobertura: `StreamPage.test.tsx` (modal, foco, Escape — M3, pasada 3) sin cambios en esta pasada. |
| 9 | Resultados → Etapa 2 / badge | **Hecho.** `RankingPage` (no depende de red — importa el mock directo, DECISIÓN 042) verificado en `http://localhost/ranking`: `get_page_text` confirma "VISTA PREVIA · DATOS DE DEMOSTRACIÓN" visible (texto nuevo de F1), sin errores de consola. |
| 10 | Historial | **Hecho, en profundidad.** Contra el backend real (no mockeado): archivar con confirmación, "Deshacer" restaura el ítem, toggle "Ver archivados" lista lo archivado con "Desarchivar", vuelta a "Ver activos" refleja el estado correcto. Contrastado dos veces contra `GET /history/` por `curl` directo para descartar artefactos de timing de la automatización del navegador (la lectura del árbol de accesibilidad quedó desincronizada del DOM real en varios reintentos — confirmado que era un artefacto de la herramienta, no del código, comparando contra la respuesta HTTP real). También confirmado que `/history` renderiza correctamente a través de nginx (build de producción), no solo en dev. |
| 11 | Cerrar sesión | **Hecho.** Redirige a `/`, TopBar vuelve al estado sin sesión (formulario de login visible). |
| 12 | `prefers-reduced-motion` | **No verificado en vivo.** Esta herramienta de navegador no expone el panel de Rendering de DevTools para emular la media feature. Cobertura: la regla CSS universal (A3) y los guards de `prefersReducedMotion()` en ambos fondos están cubiertos por tests unitarios (`DotFieldBackground.lifecycle.test.tsx`, `GridScanBackground.lifecycle.test.tsx`) que sí ejercitan la rama sin animación. |
| 13 | Consola | **Hecho, en cada paso verificado.** Cero errores en `/config`, `/ranking`, `/history` (dos veces), tras toggle de tema, tras logout. |
| 14 | CPU | **No medido en vivo** — sin panel de Performance monitor disponible en esta herramienta. Cobertura indirecta: presupuesto de bundle de B7 (medido en PR1, +1.37 KB gzip) y los guards explícitos de un solo `requestAnimationFrame` por instancia en ambos componentes de fondo (B4/B5, con test de ciclo de vida escrito en rojo antes del componente). |

**Limitación de entorno declarada, no oculta:** 5 de los 14 puntos (2, 4, 8, 12, 14) no se
verificaron con evidencia visual/interactiva directa porque el Browser pane de esta sesión no
soporta captura de pantalla ni emulación de DevTools en este entorno, y no expone una forma de
adjuntar un archivo real a un `<input type="file">`. Donde fue posible, se sustituyó por
verificación equivalente sin navegador (`curl` contra los mismos endpoints a través de nginx) o
por la cobertura de tests ya existente. Ninguno de los cinco puntos sin verificación visual
directa toca código nuevo de esta pasada que no esté ya cubierto por un test automatizado — la
brecha es de evidencia visual, no de comportamiento sin probar.

### Cierre

- Usuario de desarrollo sembrado y limpiado dos veces (una por verificación de E1, otra por el
  recorrido de Bloque G) — sin datos de prueba remanentes en la BD al cerrar.
- Stack de Docker con los cuatro servicios verificado de punta a punta contra el estado
  acumulado de las tres PRs — primera vez que corre así en esta pasada.

---

## 1. Premisas del plan que resultaron incorrectas o necesitaron ajuste

- **B2/B3 — `z-index: 0` como especificaba el plan pintaba por ENCIMA del contenido**, no por
  detrás — corregido a `z-index: -1` durante PR1 (CSS2.1 Apéndice E: elementos posicionados con
  `z-index: auto`/`0` pintan después del contenido no posicionado en flujo). Verificado con
  `document.elementFromPoint()` antes de dar el fix por bueno.
- **A5 — el plan no anticipó el conflicto entre `<CountUp>` animado y las aserciones síncronas
  de `StreamPage.integration.test.tsx`.** Escalado al usuario con evidencia exacta (archivo/línea)
  antes de decidir; resuelto con un overlay decorativo (`::before`/`content: attr()`, excluido de
  `.textContent` por la propia especificación del DOM) que satisface ambos lados sin elegir uno
  unilateralmente.
- **D1 — el plan (implícitamente, al proponer `PARSE_NO_USABLE_COLUMNS`) asumía que pandas podía
  devolver un DataFrame de 0 columnas.** Verificado empíricamente que no: `pd.read_csv` lanza
  `EmptyDataError` (subclase de `ValueError`) antes de llegar a ese estado. Código planeado
  removido, no implementado por completitud falsa — ver DECISIÓN 047, addendum.
- **Bloque G — el plan asume acceso a un navegador real con DevTools completo** (captura de
  pantalla, emulación de media features, panel de Performance) y a un flujo de subida de archivo
  real. El entorno de esta sesión no ofrece ninguna de las dos cosas para el Browser pane en uso
  — ver la limitación declarada en la tabla de arriba. No es una premisa "incorrecta" del plan en
  sí (es razonable asumir un navegador completo), pero sí un límite de esta ejecución concreta que
  vale la pena que quede escrito para la próxima vez que se plani­fique un Bloque G.

---

## 2. Estado de las tres PRs al cierre de esta pasada

| PR | Rama | Estado |
|---|---|---|
| PR1 | `feature/frontend-pasada4` | Pusheada, PR #20 abierto contra `staging`. CI/SonarCloud a cargo del usuario. |
| PR2 | `feature/frontend-pasada4-pr2` | Pusheada, PR #21 abierto (base = PR1). |
| PR3 | `feature/frontend-pasada4-pr3` | Este cierre — pendiente de push al momento de escribir este informe (ver siguiente commit de la sesión). |

Los tres PRs quedan apilados (`PR1 → PR2 → PR3 → staging`) — mergear en ese orden. Una vez que
PR1 mergee a `staging`, la base de PR2 se actualiza automáticamente en GitHub (mismo mecanismo
para PR3 sobre PR2).
