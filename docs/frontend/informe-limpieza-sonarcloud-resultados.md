# Informe de Resultados — Limpieza de SonarCloud dentro del PR B

**Fecha.** 30 de Julio de 2026.
**Alcance ejecutado.** `docs/frontend/plan-limpieza-sonarcloud.md` — Bloque S (S1-S4), Bloque N
(N1-N3), Bloque R (R1-R4), Bloque T (32 conversiones `findBy*`), Bloque C (C1-C2), Bloque D
(D1-D3), Verificación final. **X3 pasos 4-6 (aviso a Octavio, merge del PR #17, apertura del PR B)
deliberadamente NO ejecutados** — ver §2.
**Rama.** `fix/frontend-pasada2` (misma rama de las pasadas 2 y 3). 20 commits nuevos sobre los 34
de cierre de pasada 3 (54 commits totales por delante de `staging`).
**Propósito de este documento.** Punto único de retoma, mismo formato que
[`informe-pasada2-resultados.md`](./informe-pasada2-resultados.md) e
[`informe-pasada3-resultados.md`](./informe-pasada3-resultados.md).

---

## 0. Resultado por ítem

Ninguno omitido.

### Bloque S — Las 2 condiciones del gate

| # | Estado | Resultado |
|---|---|---|
| S1 | Hecho | `.github/workflows/ci.yml`, job `frontend`: `npm ci` → `npm ci --ignore-scripts`. Verificado local antes de commitear (`rm -rf node_modules && npm ci --ignore-scripts && npm run lint && npm test && npm run build`) — no rompió nada, Vite 5/Rollup 4 resuelven binarios por `optionalDependencies`. |
| S2 | Hecho | `Etapa1ResultView.tsx`, tabla de descriptivos: 8 filas `<td>rótulo</td>` → `<th scope="row">rótulo</th>`. Único issue tipo `Bug` de los 61. CSS override agregado en `Etapa1ResultView.css` para que el `<th>` no herede el estilo de encabezado de columna — verificado en vivo con el navegador (computed style), no solo por lectura de código. |
| S3 | Hecho | `ConfigPage.tsx`: dos `<label id> + <div role="group" aria-labelledby>` → `<fieldset><legend>`; un `<label>Modo</label>` suelto en la rama anónima → `<p className="ct">`. CSS de reset para `fieldset`/`legend` agregado. Verificado en vivo con el navegador — estilos idénticos al original (border, padding, tamaño/color de fuente). |
| S4 | Hecho | `StreamPage.tsx`: `{" "}` explícito antes del botón "Ver resultados ▸". |
| Checkpoint | Hecho | `npm run lint && npm test && npm run build` verde, 126/126 tests, después de S1-S4. |

### Bloque N — Roles ARIA a elementos nativos

| # | Estado | Resultado |
|---|---|---|
| N1 | Hecho | `StreamPage.tsx`, pasos del timeline: `<div role="button" tabIndex={0} onClick onKeyDown>` → `<button type="button" disabled={!expandable}>` real, eliminando el manejo manual de teclado. CSS `.step` reajustado a reset de botón nativo. |
| N2 | Hecho | `role="status"` explícito → `<output>` (rol implícito) en `AuthVerifyPage.tsx` y `guards.tsx`. Verificado que ambos contenedores ya tenían `display:flex` explícito — sin cambio visual. `getByRole("status")` en los tests sigue resolviendo. |
| N3 | **Rechazado — Won't Fix, documentado** | Sonar pide `<dialog>` nativo para el modal de atípico. Rechazado: `dialog.showModal()` cierra con Escape por defecto, sin forma limpia de desactivarlo, y eso revertiría en silencio la decisión de producto de M3 (pasada 3) de que Escape no puede cerrar el modal ni resolver una decisión — el backend queda bloqueado hasta 300s esperando una de dos decisiones auditadas. Razonamiento completo en [DECISIÓN 044](../decisiones/decision044.md). |

### Bloque R — Smells mecánicos

| # | Estado | Resultado |
|---|---|---|
| R1 | Hecho | `Readonly<{...}>` en 12 firmas de props desestructuradas: `AuthProvider.tsx`, `guards.tsx` (×2), `PendingBadge.tsx`, `EntryPage.tsx` (×2), `HistoryPage.tsx`, `Etapa1ResultView.tsx` (×2), `StreamPage.tsx`, `ThemeProvider.tsx`, `RankingPage.tsx`. `AuthLoading` (sin props) no aplica pese a estar mencionado en el plan. |
| R2 | Hecho | `useMemo` sobre el `value` de Context en `AuthProvider.tsx` y `ThemeProvider.tsx` — evita renders innecesarios de todo el árbol de consumidores. |
| R3 | Hecho | `vitest.setup.ts`: `removeAttribute("data-theme"/"data-mode")` → `delete document.documentElement.dataset.theme/mode`, mismo patrón que usa `ThemeProvider` — archivo de mayor radio de impacto de todo el bloque, suite completa re-corrida después. |
| R4 | Hecho | `AuthVerifyPage.tsx`: dos ternarias anidadas → `Record<Status, string>` (`BANNER_KIND`, `STATUS_ICON`), mismo patrón que `STEP_CLASS`/`PILL_LABEL`/`NIVEL_CONFIANZA_KIND` ya usados en el resto del código. |

### Bloque T — `findBy*` en vez de `waitFor` + `getBy` (32 spots en 9 archivos)

| Archivo | Spots plan | Spots reales | Estado |
|---|---|---|---|
| `App.test.tsx` | 1 | 2 | Hecho |
| `guards.test.tsx` | 4 | 5 | Hecho |
| `AuthVerifyPage.test.tsx` | 2 | 2 | Hecho |
| `ConfigPage.test.tsx` | 3 | 3 | Hecho |
| `DesignEventsPage.test.tsx` | 5 | 5 | Hecho |
| `EntryPage.test.tsx` | 6 | 9 | Hecho |
| `HistoryDetailPage.test.tsx` | 3 | 3 | Hecho |
| `HistoryPage.test.tsx` | 2 | 4 | Hecho |
| `ResultsPage.test.tsx` | 6 | 6 | Hecho |

**El conteo real del plan quedó corto en 5 de los 9 archivos** — mismo patrón que el resto de esta
serie de pasadas: los números de línea (y en este caso también los conteos) son del PR A, movido
por las pasadas 2 y 3. Se convirtió **toda** ocurrencia del patrón `waitFor(() => expect(getBy...))`
encontrada en cada archivo, no solo las citadas por el plan, verificando cada archivo con
lint+tsc+vitest antes de commitear (uno o dos archivos por commit, nunca uno solo de los 32).
`waitFor` sigue existiendo en otros 5 archivos del repo (`sse.test.ts`, `useBackendPing.test.tsx`,
`AuthProvider.test.tsx`, `TopBar.test.tsx`, `StreamPage.test.tsx`) — están fuera del alcance de
Bloque T (Sonar no los señaló) y no se tocaron.

### Bloque C — Configuración de SonarCloud

| # | Estado | Resultado |
|---|---|---|
| C1 | Hecho | `sonar-project.properties` creado en la raíz. `organization=carpinetioctavio` **verificado contra la API pública de SonarCloud** (`api/components/show`), no inventado. Exclusiones (`mockServiceWorker.js`, `frontend/dist/**`, `frontend/frontend-design/**`) confirmadas como no-código-de-producción antes de aplicarlas. |
| C2 | Hecho (verificación, no implementación) | Confirmado que SonarCloud corre vía Análisis Automático: `ci.yml` no tiene ningún paso de Sonar, y sin embargo `api/ce/component` muestra una tarea `type: "REPORT"` con `hasScannerContext: true` ligada al PR #17. Cablear cobertura queda fuera de esta pasada — requiere `SONAR_TOKEN` como secret de organización, decisión de Kevin/Octavio. |

### Bloque D — Documentación

| # | Estado | Resultado |
|---|---|---|
| D1 | Hecho | [`decision044.md`](../decisiones/decision044.md) — 044 reservado en el índice antes de escribir contenido. Documenta qué es SonarCloud, las 2 condiciones que bloquearon el gate (de los 61 issues, solo 6 lo bloqueaban), el rechazo de `<dialog>` (N3), la decisión de mergear el PR #17 en rojo (X2, con los 10 archivos solapados), y la pregunta de gobernanza abierta (D3) como PENDIENTE DE DECISIÓN. |
| D2 | Hecho | SonarCloud agregado a `.claude/rules/testing.md` (sección "Análisis estático"), `.claude/rules/architecture/constraints.md` (sección "GitHub Flow — branching") y `CLAUDE.md` (junto a la descripción de CI). Los tres enlaces a `decision044.md` verificados programáticamente antes de commitear. |
| D3 | Hecho | Verificado contra el PR #17 real (`gh pr view 17 --json mergeStateStatus,reviewDecision,statusCheckRollup`): `mergeStateStatus: UNSTABLE` (no `BLOCKED`) con SonarCloud en `FAILURE` — confirma que el check no es required; `reviewDecision` vacío pese a revisión pendiente — tampoco la revisión es required. `sprint.md` corregido: ya no afirma sin matiz que el Ruleset "exige... CI". No se pudo confirmar el estado de los tres checks de `ci.yml` como *required* vía API (404/lista vacía sin permiso admin) — dejado como hueco explícito, no asumido en ninguna dirección. |

**Números de decisión:** 044 (única decisión nueva de esta pasada).

---

## 1. Premisas del plan que resultaron incorrectas o necesitaron ajuste

- **La premisa de fondo del plan original era falsa y ya fue corregida antes de ejecutar nada:**
  la primera versión de `plan-limpieza-sonarcloud.md` afirmaba que el PR #17 "se mergeó igual" con
  el gate en rojo. Verificado (`gh pr view 17`, `gh pr checks 17`) que seguía **abierto y sin
  mergear**, con SonarCloud en `fail` en vivo. Corregido por el usuario antes de que esta sesión
  ejecutara una sola línea — el Bloque X completo del plan corregido existe por este motivo. Mismo
  patrón que `.claude/launch.json` en la pasada 2 y el regex de F1 en la pasada 3: verificar antes
  de actuar, no asumir que un documento de planificación describe el estado real.
- **El conteo de spots de Bloque T quedó corto en 5 de los 9 archivos** (ver tabla arriba) — los
  números del plan son del PR A, movido por las pasadas 2 y 3. Resuelto igual que en pasadas
  anteriores: localizar por contenido, convertir toda ocurrencia real encontrada.
- **Ninguna otra premisa técnica del plan corregido resultó falsa** — las 2 condiciones del gate,
  los 6 issues bloqueantes, el listado de 10 archivos solapados de X1, y la firma de Análisis
  Automático (ausencia de paso Sonar en `ci.yml`) se confirmaron todas tal como estaban descritas.

## 2. Estado real para retomar — importante

**Todo el trabajo de este documento está en local, sobre `fix/frontend-pasada2`, ya pusheado a
`origin` como respaldo (X3.1, hecho en la pasada 3).** Lo que falta, y que esta sesión
**deliberadamente no ejecutó** para confirmar con Kevin antes de una acción difícil de revertir:

1. Avisar a Octavio / cerrar su revisión pendiente del PR #17.
2. Mergear el PR #17 con **"Create a merge commit"** — sin alternativas: "Squash and merge" o
   "Rebase and merge" romperían la ascendencia y el PR B mostraría 63 commits en vez de 33-54, con
   las líneas del frontend reapareciendo como cambios propios de esta rama.
3. Pushear `fix/frontend-pasada2` (ya está pusheada, pero puede necesitar un nuevo push si hay
   commits después del respaldo de X3.1 — que los hay: 20 commits nuevos) y abrir el PR B.

Las cuatro condiciones que hacen válido mergear el PR #17 en rojo (ver
[DECISIÓN 044](../decisiones/decision044.md), X2) están cumplidas hasta donde depende de esta
sesión: el PR B está verde localmente (ver §3) y listo para abrirse inmediatamente después.
**Esperar una segunda ronda de Sonar sobre el PR B** — trae ~6.000 líneas que Sonar nunca analizó
(pasadas 2 y 3 completas, más esta limpieza), es esperable que aparezcan hallazgos nuevos sobre
código nuevo.

## 3. Verificación final — salida real

### Frontend
```
$ npm run lint && npm test && npm run build
(lint sin salida — limpio)
Test Files  22 passed (22)
     Tests  126 passed (126)
✓ built in <1s
```
Mismo número de tests que al cierre de la pasada 3 — Bloque T convirtió `waitFor` a `findBy*` sin
agregar ni quitar ningún test.

### `npm ci --ignore-scripts` desde limpio (S1)
```
$ rm -rf node_modules && npm ci --ignore-scripts
added 381 packages, and audited 382 packages in 5s
$ npm run lint && npm test && npm run build
(lint limpio, 126/126 tests, build limpio — igual que arriba)
```

### Catálogo de códigos de error — las tres direcciones
```
$ bash scripts/check-error-catalog.sh
OK — backend emite, ausente del catálogo
OK — catálogo, ausente del diccionario del frontend
OK — diccionario del frontend, ausente del catálogo

Catálogo de códigos de error sincronizado en las tres direcciones.
```

### Backend (vía Docker — `pi_metis-backend-1` / `pi_metis-postgres-1`)
```
$ docker-compose up -d backend postgres
Container pi_metis-postgres-1  Started
Container pi_metis-backend-1  Started

$ docker exec pi_metis-backend-1 ruff check metis/
All checks passed!

$ docker exec pi_metis-backend-1 ruff format --check metis/
64 files already formatted

$ docker exec pi_metis-backend-1 pytest -m unit -v
131 passed, 1 skipped in 20.09s
```

### Referencias e integridad
```
$ [sweep completo sobre todo *.md del repo, resolviendo cada enlace relativo]
Checked 152 relative links across markdown files.
Zero broken relative links.

$ grep -rn 'role="group"\|role="button"\|role="status"' frontend/src
(solo comentarios de código documentando las conversiones N1-N2 — ningún
atributo real remanente)

$ git status
On branch fix/frontend-pasada2
nothing to commit, working tree clean (salvo INSTRUCCIONES-PR-frontend.md, sin trackear a propósito)
```

**CI en el PR — no verificable todavía.** No hay push posterior al respaldo de X3.1, así que estos
20 commits no corrieron en GitHub Actions ni en SonarCloud todavía.

---

## 4. Qué queda pendiente

- **X3 pasos 4-6** (aviso a Octavio, merge del PR #17, push + apertura del PR B) — todo lo demás
  está verde localmente, listo para ejecutarse en cuanto Kevin confirme.
- **Segunda ronda de Sonar sobre el PR B**, esperada y no un fracaso si aparece — ver §2.
- **DECISIÓN 044, pregunta de gobernanza (D3)** — pendiente de que Kevin/Octavio decidan si el
  check de SonarCloud pasa a ser *required* en el Ruleset, con o sin revisión obligatoria, o queda
  consultivo como está hoy.
- **DECISIÓN 043** (contraste WCAG) y las decisiones 036/037 (partición de Cramer,
  `etapas`/`AnalysisRequest`) siguen exactamente igual — fuera de alcance de esta pasada también.
- **Marcar N3 como *Won't fix* en la interfaz de SonarCloud** — esta sesión no tiene acceso a la
  organización de SonarCloud; queda para quien lo tenga, con el motivo ya escrito en
  [DECISIÓN 044](../decisiones/decision044.md).
