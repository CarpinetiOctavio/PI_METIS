# Informe de Resultados — Pasada 5 de Mejora sobre el Frontend (cierre)

**Fecha.** 9 de Agosto de 2026.
**Alcance ejecutado.** `docs/frontend/plan-mejora-frontend-pasada5.md` completo — Bloque A
(paridad del tema claro), Bloque B (strands en Canvas 2D), Bloque C (elevación de cards),
Bloque D (TopBar como cluster de vidrio), Bloque E (dropzone + panel de muestra de columnas),
Bloque F (blur del scrim del modal de atípico).
**Ramas — cuatro PRs apilados, tal como pide el plan §7:**
- PR1 `feat/frontend-pasada5-bloque-ab` — Bloques A + B (#37).
- PR2 `feat/frontend-pasada5-bloque-cd` — Bloques C + D, base = PR1 (#38).
- PR3 `feat/frontend-pasada5-bloque-e` — Bloque E, base = PR2 (#39).
- PR4 `feat/frontend-pasada5-bloque-f` — Bloque F, base = staging actualizado tras el merge de
  PR3 (#40).

**Propósito de este documento.** Punto único de retoma de esta pasada, mismo formato que
[`informe-resultados-pasada4.md`](./informe-resultados-pasada4.md).

---

## 0. Resultado por ítem

Ninguno omitido.

### Bloque A — Paridad del tema claro (PR1, #37)

| # | Estado | Resultado |
|---|---|---|
| A1 | Hecho | Token `--glow` agregado a `tokens.ts`/`tokens.instrumento.css` (light `#7dd3e8`, dark `#22d3ee` — idéntico a `--acc` oscuro por diseño). `tokenParity.test.ts` lo valida sin cambios propios (misma regla camelCase→kebab). |
| A2 | Hecho | `--bg` (`#f3f6f8`→`#edf1f5`) y `--line` (`#dee5eb`→`#d7dfe7`) en tema claro — separan el fondo de página del blanco de las cards. `--surf`/`--surf2`/`--line-strong` sin cambios; DECISIÓN 043 (contraste WCAG) sigue fuera de alcance. |
| A3 | Hecho | `GridScanBackground`, `DotFieldBackground` y `ThreadsBackground` migrados de `--acc` a `--glow` en trail/puntos/paleta. `grep -rn '"--acc"' frontend/src/theme/backgrounds/` sin coincidencias (verificado en el cierre de PR1). |

### Bloque B — Strands en Canvas 2D (PR1, #37)

| # | Estado | Resultado |
|---|---|---|
| B1-B6 | Hecho | `ThreadsBackground` reescrito de Three.js a Canvas 2D (mismos parámetros: `THREAD_COUNT=18`, `POINTS_PER_THREAD=64`, misma función de onda), montado sin lazy/Suspense en `RootLayout` junto a sus dos hermanos. Cuatro guardas de ciclo de vida conservadas (`prefersReducedMotion`, `visibilitychange`, `IntersectionObserver`, cleanup completo). `three`/`@types/three` fuera del `package.json`. DECISIÓN 051 escrita y enlazada desde `decision045.md` y el índice. |

**Bundle antes/después (medido en el cierre de PR1):** bundle único 333.48 kB min / 112.26 kB
gzip — antes ~840.6 kB min / ~240.6 kB gzip repartidos en dos chunks (el chunk separado de
Three.js desaparece por completo).

### Bloque C — Elevación de cards (PR2, #38)

| # | Estado | Resultado |
|---|---|---|
| C1 | Hecho | Tokens `--elev-1`/`--elev-2` en `tokens.instrumento.css` — no van a `tokens.ts` (no son hex), `tokenParity.test.ts` los ignora sin cambios. |
| C2 | Hecho | `.card` eleva con `--elev-1`, borde `--line-strong` solo en tema claro. `.card.soft` sin sombra (card anidada, ej. `.config-cramer`). `.entry`/`.config-card` con `--elev-2`. `.modal-backdrop .card` no se tocó — ya tenía `box-shadow` propia con mayor especificidad, nunca heredó la de `.card`. |
| C3 | Hecho | Spotlight de `SpotlightCard` más leve: radio 200px→260px, núcleo blanco 30%→12%, mezcla `--acc` 22%→8%, opacidad al hover 1→0.55. `SpotlightCard.test.tsx` sin cambios (verifica comportamiento, no intensidad). |

### Bloque D — TopBar como cluster de vidrio (PR2, #38)

| # | Estado | Resultado |
|---|---|---|
| D1-D3 | Hecho | `.topbar__indicators` pasa de flex suelto a panel de vidrio (mismo patrón que `.modal-backdrop .card` de la pasada 4): borde, `color-mix` sobre `--surf`, `backdrop-filter` blur+saturate. `.topbar__sep` 14px→16px. Email con `title={user.email}` + clase propia `.topbar__email` (tabular-nums, max-width 200px, ellipsis) en vez de tocar `.fn` (compartida por el resto del design system). `TopBar.test.tsx` sin modificar — ningún `data-testid`, `aria-label` ni el texto de `BACKEND_LABEL` cambió. |

### Bloque E — Dropzone + panel de muestra de columnas (PR3, #39)

| # | Estado | Resultado |
|---|---|---|
| E1 | Hecho | `<input type="file">` sigue siendo el único destino real de la carga (mismo `handleFileChange` para click y drop), oculto con `.visually-hidden`; su `<label>` pasa a ser la zona de arrastre con tres estados. Nombre accesible movido a `aria-label` sobre el input (necesario: el `<label>` ahora envuelve contenido visual que cambia con el estado — ver premisa ajustada en §1). Filtro de `accept` no replicado en JS. |
| E2 | Hecho | `etiquetaColumna()` deja de concatenar la muestra en el `<option>` (síntoma P8). Desambiguación de nombres duplicados conservada. |
| E3 | Hecho | `ColumnPreviewPanel` nuevo, presentacional puro: tabla con hasta 3 filas de muestra y el campo `filas` de `preview-columns` que el frontend descartaba. `columnaResaltada` por `onFocus`/`onBlur` de los `<select>`. |
| E4 | Hecho | `.config-shell`: grid `560px 1fr` con panel `sticky` desde 1100px; por debajo, una columna con `overflow-x` en la tabla. Sin panel montado, el shell queda en `block` y la card se centra sola. |
| E5 | Hecho | 3 tests nuevos en `ConfigPage.test.tsx` (drop dispara `preview-columns` y puebla los selects; panel poblado sin duplicar la muestra en el `<option>`; foco/blur resalta/desresalta la columna). Los 8 tests preexistentes de degradación siguen sin cambios. |

### Bloque F — Blur del scrim del modal de atípico (PR4, #40)

| # | Estado | Resultado |
|---|---|---|
| F1 | Hecho | `.modal-backdrop` suma `backdrop-filter: blur(6px)`. `.modal-backdrop .card` baja su blur de 20px a 10px (compone sobre un fondo ya desenfocado). Confirmado en el CSS del bundle de producción (`grep` sobre `dist/assets/index-*.css`). |
| F2 | Hecho | `StreamPage.tsx` sin tocar — auto-foco, manejo de Escape (M3, pasada 3) y restauración de foco intactos. `StreamPage.test.tsx`/`StreamPage.integration.test.tsx` sin modificar. |

### Verificación transversal — los cuatro PRs

- `npm test`: verde en cada PR al momento de su cierre (188/188 tras PR2, 191/191 tras PR3 y PR4
  — 33 archivos en los cuatro casos). Ningún test existente modificado sin justificarlo.
- `npm run lint`: limpio en los cuatro PRs.
- `npm run build`: verde en los cuatro PRs.
- Revisión manual del diff contra las categorías del quality gate de SonarCloud (bugs,
  vulnerabilidades, code smells, duplicación) antes de cada push — sin scanner local disponible
  (no hay `SONAR_TOKEN` ni `sonar-scanner` en este entorno; el Análisis Automático corre solo
  sobre el PR ya abierto en GitHub, y es consultivo, no bloqueante — DECISIÓN 044).

---

## 1. Premisas del plan que resultaron incorrectas o necesitaron ajuste

- **E1 — el plan asumía que el `<label>` podía seguir aportando el nombre accesible
  ("Archivo (CSV o Excel)") con solo agregarle un `<span>` visualmente oculto adentro.** En la
  práctica, `getByLabelText` de Testing Library resuelve por el `textContent` completo del
  `<label>` (no excluye contenido `aria-hidden`), así que con el ícono/mensaje visual dentro del
  mismo `<label>` el texto ya no coincidía con la cadena esperada por los 6+ tests existentes que
  dependen de `getByLabelText("Archivo (CSV o Excel)")`. Corregido moviendo el nombre accesible a
  un `aria-label` directo sobre el `<input>` (que tiene precedencia sobre cualquier `<label>`
  asociado en el cómputo de nombre accesible) — el contenido visual del `<label>` queda
  `aria-hidden` por claridad, aunque ya no participa del cómputo de todos modos. Los tests
  existentes no necesitaron ningún cambio.
- **Bloque E — verificación con el preview server incorrecto.** Al levantar el primer dev server
  de la pasada (para PR2), la herramienta de preview arrancó `npm run dev` desde el checkout
  principal del repo (rama `feat/spotlight-cards`, anterior al merge de PR1) en vez del worktree
  correcto — se detectó por un canvas con `data-engine="three.js r185"` que no debería existir
  post-PR1. Corregido levantando el dev server manualmente (`Bash` con `run_in_background`) desde
  el worktree correcto en cada bloque siguiente, en vez de confiar en la resolución por defecto
  de la herramienta de preview.
- **Bloque E — resaltado por foco no reproducible con `.focus()` programático vía JavaScript en
  esta pestaña.** El script cambiaba `document.activeElement` pero no disparaba el evento
  `focus`/`focusin` que React usa para `onFocus` — comportamiento consistente con una pestaña sin
  foco real a nivel de SO en un navegador automatizado en segundo plano, no un bug del código.
  Confirmado con una interacción de click real vía CDP (`computer.left_click`) sobre el mismo
  `<select>`: el resaltado sí se aplicó correctamente. El comportamiento de foco/blur en sí está
  cubierto determinísticamente por el test con `fireEvent.focus`/`fireEvent.blur` (que sí dispara
  los eventos sintéticos de React independientemente del foco real del SO).
- **Bloque E — sin backend real disponible para probar el camino exitoso de `preview-columns`.**
  Sin Docker levantado en la sesión, se interceptó `window.fetch` en el navegador en vivo para
  devolver una respuesta canned de `preview-columns` y así verificar `ColumnPreviewPanel` y el
  grid de `.config-shell` renderizando contra datos reales del DOM — no es una prueba end-to-end
  contra el backend real, es una verificación de integración de UI con la red interceptada en el
  borde, mismo patrón que ya usan `StreamPage.integration.test.tsx` y el resto de la Capa 2 de
  `testing.md`.
- **Bloque F — no se disparó el modal de atípico contra un backend real en esta sesión** (mismo
  motivo: sin Docker levantado). La verificación quedó en tres niveles: tests existentes del
  modal sin modificar y en verde, valores de `backdrop-filter` confirmados en el CSS del bundle
  de producción, y la verificación visual en vivo con el CSV de atípico forzado quedó para el
  usuario antes de mergear — mismo patrón que los PRs anteriores de esta pasada.
- **Limpieza de worktrees entre bloques.** Los procesos de `vite` de worktrees anteriores
  quedaron corriendo en segundo plano entre bloques (puertos 5173/5175 ocupados), lo que bloqueó
  la eliminación de sus directorios (`git worktree remove` falló con `Invalid argument` en
  Windows hasta matar los procesos vía `taskkill`). Resuelto identificando los PID por puerto
  (`netstat -ano`) antes de cada limpieza de worktree.

---

## 2. Estado de los cuatro PRs al cierre de esta pasada

| PR | Rama | Estado |
|---|---|---|
| PR1 | `feat/frontend-pasada5-bloque-ab` | Mergeado a `staging` (#37). |
| PR2 | `feat/frontend-pasada5-bloque-cd` | Mergeado a `staging` (#38, mergeado por el usuario mientras se implementaba PR3). |
| PR3 | `feat/frontend-pasada5-bloque-e` | Mergeado a `staging` (#39, mergeado por el usuario). |
| PR4 | `feat/frontend-pasada5-bloque-f` | Mergeado a `staging` (#40, mergeado por el usuario). |

Los cuatro PRs mergearon en orden sin conflictos. Ramas remotas de PR2, PR3 y PR4 ya borradas
(auto-delete o borrado manual del usuario); la de PR1 seguía presente en el remoto al momento de
escribir este informe — ver aviso aparte sobre limpieza de ramas.
