# Plan de mejora del frontend — Pasada 5 (paridad del tema claro y densidad de la interfaz)

**Fecha:** 6 de Agosto de 2026
**Estado:** IMPLEMENTADO (09/08/2026) — ver [`informe-resultados-pasada5.md`](informe-resultados-pasada5.md) para el cierre completo.
**Punto de entrada anterior:** [`plan-mejora-frontend-pasada4.md`](plan-mejora-frontend-pasada4.md) e
[`informe-resultados-pasada4.md`](informe-resultados-pasada4.md)

---

## 0. Por qué existe esta pasada

La pasada 4 cerró la identidad visual "Instrumento" (tipografía real, tokens de
movimiento, estados de interacción, dos fondos animados, `TopBar` dentro del
design system). La verificación manual de esa pasada se hizo, en la práctica,
mirando el **tema oscuro**. Lo que esta pasada arregla es la consecuencia
directa de eso: el tema claro comparte la estructura pero no la legibilidad, y
tres detalles de densidad de la interfaz (`TopBar`, carga de archivo, modal de
atípico) hacen que el programa se lea como un prototipo en fases básicas
aunque el backend detrás esté completo.

Diagnóstico observado en uso real (Kevin, 06/08/2026), pantalla por pantalla:

| # | Síntoma observado | Pantalla | Bloque |
|---|---|---|---|
| P1 | El scan line tiene "un color raro" en tema claro | `/` | A |
| P2 | Los strands casi no se ven en tema claro | `/` | A |
| P3 | La card de login no contrasta contra el fondo | `/` | C |
| P4 | La segunda pantalla no tiene strands, solo el dot field | `/config` | B |
| P5 | La card de `ConfigPage` tampoco contrasta en tema claro | `/config` | C |
| P6 | La info del header es texto suelto, sin recuadro ni efecto | todas | D |
| P7 | El campo de archivo es el `<input type="file">` nativo, chico | `/config` | E |
| P8 | Las muestras de datos se apelotonan dentro del `<option>` | `/config` | E |
| P9 | El modal de atípico no separa visualmente del fondo | `/stream` | F |
| P10 | El spotlight de las cards es demasiado fuerte | `/history`, `/ranking` | C |

### 0.1 La causa raíz de P1 y P2 — una sola, no dos

`GridScanBackground.tsx` y `ThreadsBackground.tsx` pintan **luz** (un barrido
con glow, hilos luminosos) usando `--acc` leído del tema activo. En tema
oscuro `--acc` es `#22D3EE` — cian brillante, se lee como luz. En tema claro
`--acc` es `#0E7490` — verde azulado oscuro, elegido para tener contraste
como **texto sobre fondo blanco**, que es exactamente lo contrario de lo que
necesita un glow. Pintado sobre `--bg: #F3F6F8`, `--acc` claro no se lee como
brillo sino como suciedad: una mancha oscura (P1) o unos hilos grises casi
invisibles (P2).

`GridScanBackground` ya intentó parchear esto introduciendo
`CORE_COLOR = "#ffffff"` para el núcleo del barrido — el comentario en ese
archivo describe el problema con precisión. Pero el parche es local (solo el
núcleo del beam) y hardcodeado: los bordes del gradiente, el trail de la
grilla y los 18 hilos de `ThreadsBackground` siguen usando `--acc` crudo.
**El parche correcto es un token, no una constante por archivo.**

### 0.2 Precondición antes de arrancar

Levantar el stack real y ver las dos pantallas en los dos temas antes de tocar
una línea:

```bash
cd frontend && npm install && npm run dev   # http://localhost:5173
# backend real para /config y /stream:
docker-compose up -d backend postgres
docker exec <backend> alembic upgrade head   # ver CLAUDE.md — no es automático
bash scripts/seed-dev-user.sh
```

Sin esto, cada bloque de abajo se implementa a ciegas contra una descripción
en prosa. La pasada 4 ya dejó constancia de lo que pasa cuando eso ocurre
(`informe-diagnostico-ui-rota.md`: dos PRs verdes con la app rota).

---

## 1. Bloque A — Paridad del tema claro

Toca `frontend/src/theme/tokens.ts`, `tokens.instrumento.css` y los tres
fondos de `theme/backgrounds/`. **Es el único bloque que modifica tokens** —
`tokenParity.test.ts` es el guardián y no se toca.

### A1 — Token de luz `--glow`, separado de `--acc`

`--acc` sigue siendo el acento *de contenido* (texto, bordes, relleno de la
cápsula de nav) y no cambia en ninguno de los dos temas. Se agrega un token
nuevo cuyo único propósito es ser **fuente de luz sobre el fondo del tema**:

| Token | light | dark | Rol |
|---|---|---|---|
| `--glow` | `#7DD3E8` | `#22D3EE` | Color de los fondos animados (beam, trail, hilos) |

En oscuro es el mismo valor que `--acc` (nada cambia visualmente). En claro es
un cian claro que, sobre `#F3F6F8`, se lee como brillo y no como mancha.

**Implementación — los dos archivos en el mismo commit:**

- `tokens.ts` — agregar `glow: string` a `ThemeTokenSet` y el valor a los dos
  objetos de `instrumentoTokens`.
- `tokens.instrumento.css` — agregar `--glow` a los dos bloques
  `[data-mode="…"]`.

`tokenParity.test.ts` convierte `glow` → `--glow` con la misma regla
camelCase→kebab que ya usa para `lineStrong`/`accSoft`, así que el test valida
la paridad del token nuevo sin necesitar ningún cambio en el test mismo. Si el
test falla, es porque uno de los dos archivos quedó sin actualizar — que es
exactamente para lo que existe.

### A2 — Ajuste leve de los tokens claros de superficie

Cambio mínimo, solo para que `--surf` (blanco puro) tenga contra qué
recortarse. No se toca ningún token de texto ni de estado (`--ink`, `--mut`,
`--ok`, `--warn`, `--crit` quedan igual — cualquier cambio ahí reabre
[DECISIÓN 043](../decisiones/decision043.md), que sigue pendiente de decisión
de Kevin/Octavio y **está fuera del alcance de esta pasada**).

| Token | Antes (light) | Después (light) | Motivo |
|---|---|---|---|
| `--bg` | `#F3F6F8` | `#EDF1F5` | Separa el fondo de página del blanco de las cards |
| `--line` | `#DEE5EB` | `#D7DFE7` | Los bordes de card quedaban a un paso del fondo nuevo |

`--surf`, `--surf2` y `--line-strong` no cambian. Verificar con
`tokenParity.test.ts` + `tokens.test.ts` en verde.

### A3 — Los tres fondos consumen `--glow`, no `--acc`

- `GridScanBackground.tsx` — `readCssVar("--acc", …)` → `readCssVar("--glow", …)`
  en el trail de la grilla y en los cuatro `addColorStop` del beam. `CORE_COLOR`
  se conserva (el núcleo blanco sigue siendo correcto en los dos temas) pero
  el comentario que lo justifica se actualiza para apuntar a `--glow` como la
  solución general de la que él era el parche local.
- `DotFieldBackground.tsx` — mismo cambio en el color de los puntos.
- `ThreadsBackground.tsx` — la paleta interpolada pasa a construirse entre
  `--glow` y `--acc2`, no entre `--acc` y `--acc2`.

Los fallbacks de `readCssVar` (segundo argumento) se actualizan al valor de
`--glow` del tema oscuro, coherente con lo que ya hacían.

### A4 — Criterios de hecho del Bloque A

- `npm test` verde, incluidos `tokenParity.test.ts` y `tokens.test.ts`.
- `grep -rn '"--acc"' frontend/src/theme/backgrounds/` no devuelve ninguna
  coincidencia (los tres fondos migraron; `--acc2` sí sigue apareciendo).
- Verificación manual en tema **claro**: el barrido de `/` se lee como una
  banda luminosa, no como una sombra vertical; los hilos son visibles sin
  forzar la vista.
- Verificación manual en tema **oscuro**: captura antes/después
  indistinguible — `--glow` oscuro es idéntico a `--acc` oscuro por diseño.

---

## 2. Bloque B — Strands en Canvas 2D, en todas las pantallas

Resuelve P4 (la segunda pantalla debe mantener strands además del dot field).

### B1 — Por qué se reescribe en vez de solo montarlo en más rutas

`ThreadsBackground` hoy usa Three.js, y ese import es la razón de que esté
acotado a `/` vía `React.lazy` — el addendum de
[DECISIÓN 045](../decisiones/decision045.md) lo admite explícitamente como
"la excepción documentada", justificada porque **ninguna pantalla autenticada
paga el costo del chunk**. Montarlo en `/config` invalida esa justificación:
todas las pantallas pasarían a cargar Three.js para dibujar 18 polilíneas
sinusoidales, que es exactamente el caso que DECISIÓN 045 había descartado en
el Bloque B de la pasada 4.

Lo que el componente hace de verdad —`THREE.Line` con `LineBasicMaterial`,
cámara ortográfica, sin luces, sin materiales, sin profundidad— es una
polilínea 2D. Se reimplementa en Canvas 2D con `requestAnimationFrame`,
hermana de los otros dos fondos, y Three.js sale del proyecto.

**Esto revierte el addendum de DECISIÓN 045 y requiere una decisión nueva:
`docs/decisiones/decision051.md`** (051 es el primer número libre — 046 y 049
ya están reservados, ver `docs/decisiones/README.md`). Escribirla antes de
mergear, no después.

### B2 — La reescritura

`ThreadsBackground.tsx` conserva su nombre, su ubicación y su contrato
externo (componente sin props, `<canvas>` `position: fixed; inset: 0;
z-index: -1; pointer-events: none`). Adentro:

- Mismos parámetros de la versión Three.js: `THREAD_COUNT = 18`,
  `POINTS_PER_THREAD = 64`, `PALETTE_STEPS = 5`, misma función de onda
  (`sin(x*3 + t*speed + seed)*0.15 + sin(x*7 - t*speed*1.7 + seed)*0.05`),
  mismos rangos de `speed` y `yOffset`.
- La interpolación de paleta que hacía `THREE.Color.lerp` se implementa en
  `canvasUtils.ts` como `lerpHex(a, b, t)` — función pura, exportada, con su
  propio test unitario.
- Coordenadas: la versión Three.js trabaja en NDC (`-1..1`); la versión Canvas
  mapea directo a píxeles del viewport vía `sizeCanvasToViewport`, el mismo
  helper que ya usan los otros dos fondos.
- `secureRandom()` de `canvasUtils.ts` se conserva para las semillas (Sonar
  marca `Math.random()`).

### B3 — Las cuatro guardas, no negociables

Idénticas a B4 de la pasada 4, porque son las mismas que ya tenía la versión
Three.js y las que `ThreadsBackground.lifecycle.test.tsx` verifica hoy:

1. `prefersReducedMotion()` → un solo `draw(0)`, sin loop.
2. `visibilitychange` → no dibujar en pestaña oculta.
3. `IntersectionObserver` → no dibujar fuera del viewport.
4. `cleanup` completo: `cancelAnimationFrame` + los tres listeners
   desregistrados + `intersectionObserver.disconnect()`.

`ThreadsBackground.lifecycle.test.tsx` se conserva y debe pasar **sin
modificarle las aserciones** — solo lo que sea específico de WebGL (el
`try/catch` de `new THREE.WebGLRenderer()`) se adapta al `getContext("2d")`
que usan los otros dos fondos.

### B4 — Montaje en `RootLayout`

```tsx
<ThreadsBackground />                    {/* siempre, sin Suspense ni lazy */}
{showDotField && <DotFieldBackground />}
{showGridScan && <GridScanBackground />}
```

`ThreadsBackground` queda primero en el DOM y por lo tanto debajo de sus
hermanos (los tres comparten `z-index: -1`). El comentario largo de
`RootLayout.tsx` sobre por qué los fondos viven acá y no dentro de las páginas
(el bug de `.route-enter` como containing block) sigue vigente y **no se
toca** — se le agrega una línea para el tercer fondo.

### B5 — Salida de Three.js

- `frontend/package.json` — quitar `three` y `@types/three`, correr
  `npm install` para regenerar el lockfile.
- `RootLayout.tsx` — quitar el `lazy(...)`, el `Suspense` y el import
  dinámico; quitar el comentario que explica el import diferido.
- `grep -rn "three" frontend/src` debe quedar vacío.

### B6 — Criterios de hecho del Bloque B

- `npm test` verde, con `ThreadsBackground.lifecycle.test.tsx` cubriendo las
  cuatro guardas y un test nuevo de `lerpHex`.
- `npm run build` verde y **más chico** que antes: registrar el tamaño del
  bundle antes y después en el informe de resultados (el chunk de Three.js
  ronda los 600 kB minificados — la diferencia debe ser visible).
- `grep -rn "three" frontend/src frontend/package.json` sin coincidencias.
- Verificación manual: strands visibles en `/` **y** en `/config`, en los dos
  temas, conviviendo con el dot field sin taparlo.
- `docs/decisiones/decision051.md` escrita y enlazada desde
  `docs/decisiones/README.md` y desde el addendum de `decision045.md`.

---

## 3. Bloque C — Elevación de cards y spotlight más leve

Resuelve P3, P5 y P10.

### C1 — Tokens de elevación

Dos variables nuevas en cada bloque de modo de `tokens.instrumento.css`.
**No van a `tokens.ts`**: `tokenParity.test.ts` extrae únicamente
declaraciones cuyo valor es un hex (`/--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]+)\s*;/`),
y una `box-shadow` compuesta no lo es — el test las ignora sin falsos
positivos y sin necesitar cambios.

| Token | light | dark |
|---|---|---|
| `--elev-1` | `0 1px 2px rgba(11,14,18,.06), 0 4px 12px rgba(11,14,18,.05)` | `0 1px 2px rgba(0,0,0,.4), 0 4px 14px rgba(0,0,0,.3)` |
| `--elev-2` | `0 2px 4px rgba(11,14,18,.07), 0 12px 32px rgba(11,14,18,.09)` | `0 2px 6px rgba(0,0,0,.45), 0 16px 40px rgba(0,0,0,.38)` |

En oscuro la sombra aporta poco (fondo casi negro) pero se define igual para
que ningún consumidor tenga que preguntar por el modo.

### C2 — `.card` eleva; las dos cards de entrada elevan más

En `theme/global.css`:

- `.card` — agregar `box-shadow: var(--elev-1)`. El borde pasa a
  `var(--line-strong)` **solo en tema claro**, vía
  `:root[data-mode="light"] .card { border-color: var(--line-strong); }`. En
  oscuro `--line` ya funciona.
- `.card.soft` — sin sombra (`box-shadow: none`): es una card *dentro* de otra
  card (`.config-cramer`), elevarla rompe la jerarquía.
- `.modal-backdrop .card` (en `StreamPage.css`) — conserva su `box-shadow`
  propia de vidrio, que es más fuerte; se le agrega `box-shadow` explícita
  para que no herede la de `.card` por cascada.

En `EntryPage.css` y `ConfigPage.css`: `box-shadow: var(--elev-2)` sobre
`.entry` (el contenedor de las dos mitades) y `.config-card`.

Las esquinas HUD (`.card::before` / `::after`, borde `--acc` al 65%) se
conservan tal cual — son identidad, no decoración.

### C3 — Spotlight "apenas notarse"

`components/SpotlightCard.css`, único archivo. Cuatro cambios, todos en el
mismo gradiente:

| Parámetro | Antes | Después |
|---|---|---|
| Radio | `200px` | `260px` |
| Núcleo | `white 30%` mezclado con `--acc` | `white 12%` |
| Mezcla intermedia | `--acc 22%` | `--acc 8%` |
| Opacidad al hover | `1` | `0.55` |

El radio sube y la intensidad baja: el efecto se vuelve un cambio de luz
ambiente y deja de leerse como una linterna. `SpotlightCard.test.tsx` verifica
comportamiento (la variable `--spot-x`/`--spot-y` sigue el puntero), no
intensidad — no requiere cambios.

### C4 — Criterios de hecho del Bloque C

- `npm test` verde sin tocar `SpotlightCard.test.tsx` ni `tokenParity.test.ts`.
- Verificación manual en tema claro: la card de login y la de `ConfigPage` se
  recortan del fondo sin ayuda de las esquinas HUD (taparlas mentalmente y
  seguir viendo el borde de la card).
- Verificación manual del spotlight en `/history` y `/ranking`: el efecto se
  nota al mover el puntero pero no llama la atención por sí solo.
- Ninguna card anidada (`.config-cramer`) tiene sombra.

---

## 4. Bloque D — `TopBar` como cluster de vidrio

Resuelve P6.

### D1 — Qué está mal hoy

`TopBar.tsx` renderiza a la derecha, sueltos sobre el fondo de la barra:
estado del backend, `<span>` con el email, botón "Cerrar sesión", separadores
de 1px y el toggle de tema. Tres bloques de información distintos que se leen
como una línea de texto continua. La cápsula de navegación de la izquierda
(`.topbar__nav`, con su pill indicator) ya demuestra el patrón correcto:
**un contenedor con borde, fondo propio y radio**.

### D2 — Un solo panel de vidrio con separadores internos

`.topbar__indicators` pasa de un `display: flex` sin superficie a un panel,
reusando el patrón de vidrio que `.modal-backdrop .card` ya introdujo en la
pasada 4 (y que por eso está probado en los dos temas):

```css
.topbar__indicators {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 5px 12px;
  border: 1px solid color-mix(in srgb, var(--ink) 10%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--surf) 65%, transparent);
  backdrop-filter: blur(12px) saturate(160%);
  -webkit-backdrop-filter: blur(12px) saturate(160%);
  box-shadow: inset 0 1px 0 color-mix(in srgb, white 14%, transparent);
  font-size: 12px;
  color: var(--mut);
}
```

Los `.topbar__sep` existentes se conservan como separadores internos del
panel (ya están en el DOM, con `aria-hidden`), subiendo su altura de 14px a
16px para que se lean como divisiones del cluster y no como comas.

El email (`.fn`) pasa a `font-variant-numeric: tabular-nums` y se le agrega
`title={user.email}` con `max-width: 200px; overflow: hidden; text-overflow:
ellipsis` — un legajo largo no puede empujar el toggle de tema fuera de la
barra.

### D3 — Lo que no se toca

**Ni un `data-testid`, ni un `aria-label`, ni el texto de `BACKEND_LABEL`.**
`TopBar.test.tsx` busca `backend-status`, `user-email`, `mode-badge` y el
nombre accesible `/cambiar tema/i`; el Pill Nav y su `useLayoutEffect` de
medición viven en el otro extremo del componente y no participan. Este bloque
es CSS más dos atributos de presentación — si hay que modificar una aserción
del test, algo se fue de alcance.

### D4 — Criterios de hecho del Bloque D

- `npm test` verde con `TopBar.test.tsx` **sin modificar**.
- Verificación manual en los dos temas: los tres indicadores se leen como un
  módulo, no como texto suelto; el `backdrop-filter` deja ver el fondo animado
  moviéndose detrás del panel.
- Un email de 30 caracteres no rompe el layout de la barra.

---

## 5. Bloque E — Carga de archivo y panel de muestra de columnas

Resuelve P7 y P8. Es el bloque más grande y el único que toca comportamiento;
va en su propio commit, idealmente en su propio PR.

### E1 — Dropzone en lugar del `<input type="file">` nativo

`ConfigPage.tsx` + `ConfigPage.css`. El `<input>` no desaparece: se mantiene
en el DOM con `id="config-archivo"` (el `<label htmlFor>` existente lo sigue
rotulando) y se oculta visualmente con la clase `.visually-hidden` que ya
existe en `global.css`. Encima se dibuja una zona ancha, del ancho de la card:

- Estado vacío — icono, `Buscá un archivo o arrastralo acá`, y debajo, en
  `.fn`: `CSV, XLSX o XLS · hasta 10 MB` (el cap real de
  `PARSE_FILE_TOO_LARGE`, DECISIÓN 050 — el frontend nunca lo mencionó).
- Estado con archivo — nombre, tamaño formateado, y un botón `Cambiar`.
- Estado `dragover` — borde `--acc` y fondo `--acc-soft`.

Eventos: `onDragOver`/`onDragLeave`/`onDrop` con `preventDefault()`, y el drop
llama a **la misma** `handleFileChange(file)` que el `onChange` del input. Un
solo camino de código para los dos gestos. Click sobre la zona: la zona es un
`<label htmlFor="config-archivo">`, así que el click nativo del label abre el
selector sin un solo `ref.click()`.

El filtro por extensión del `accept` **no se replica en JS**: si el usuario
suelta un `.txt`, se manda igual y el backend responde `PARSE_ERROR`, que
`ConfigPage` ya sabe mostrar (`preview.status === "error"` degrada a inputs de
texto con el banner de warning). Duplicar la validación en el cliente crearía
una segunda fuente de verdad sobre qué archivos acepta METIS.

### E2 — Las etiquetas del `<select>` vuelven a ser solo el nombre

`etiquetaColumna()` deja de concatenar `col.muestra.slice(0, 3).join(", ")`.
Conserva **sí o sí** la desambiguación de nombres duplicados
(`${col.nombre} (col. ${col.indice + 1})`), que no es cosmética: sin ella dos
columnas homónimas son indistinguibles en el desplegable. El `value` sigue
siendo el índice, por el mismo motivo que documenta el comentario actual del
archivo.

### E3 — Panel lateral de muestra

Componente nuevo: `routes/config/ColumnPreviewPanel.tsx` +
`ColumnPreviewPanel.css`. Presentacional puro, sin estado propio ni llamadas
de red — misma disciplina que `Etapa1ResultView.tsx` de la Fase 3.

```tsx
interface ColumnPreviewPanelProps {
  columnas: ColumnaPreview[];
  filas: number;
  columnaResaltada: string | null;  // índice como string, o null
}
```

Renderiza una tabla: una columna por cada `ColumnaPreview`, hasta 3 filas de
`muestra`, y un pie con `{filas} filas en el archivo` (el campo `filas` que
`POST /analysis/preview-columns` ya devuelve y que hoy el frontend descarta).
La columna cuyo índice coincide con `columnaResaltada` lleva la clase
`--activa`: fondo `--acc-soft` y borde superior `--acc`.

En `ConfigPage.tsx`, `columnaResaltada` es estado local movido por
`onFocus`/`onBlur` de los dos `<select>` — no por el valor seleccionado. El
panel se monta solo cuando `preview.status === "ready"`.

### E4 — Layout

`.config-shell` nuevo, envolviendo card + panel:

- `≥ 1100px` — `display: grid; grid-template-columns: 560px 1fr; gap: 20px;
  align-items: start`. La card mantiene su `max-width: 560px` actual; el panel
  ocupa la columna derecha y es `position: sticky; top: 20px`.
- `< 1100px` — una sola columna: el panel cae debajo de la card, ancho
  completo, con `overflow-x: auto` en la tabla.

La card sigue centrada cuando no hay archivo cargado (sin panel, la grilla
colapsa a una columna centrada por el `margin: 0 auto` que `.config-card` ya
tiene).

### E5 — Tests

Tres nuevos en `ConfigPage.test.tsx`, patrón de mock existente
(`vi.stubGlobal("fetch", …)`, nunca MSW — DECISIÓN 041), bajo `<StrictMode>`
vía `renderPage`:

1. Soltar un archivo en la dropzone dispara `POST /analysis/preview-columns`
   y puebla los dos `<select>` — el mismo resultado que elegirlo por el input.
2. Con `preview.status === "ready"`, el panel muestra las muestras y el
   `<option>` **no** las contiene (aserción negativa explícita — es el
   síntoma P8).
3. `focus` en el select de Columna X resalta la columna correspondiente en el
   panel; `blur` la desresalta.

Los tests existentes de degradación (`preview.status === "error"` → inputs de
texto) deben seguir pasando sin cambios.

### E6 — Criterios de hecho del Bloque E

- `npm test` verde, incluidos los tres tests nuevos y los de degradación.
- `npm run lint` verde.
- Verificación manual contra backend real con un CSV de 40 años: cargar por
  click y por drag&drop, ver el panel poblarse, cambiar de archivo y ver que
  el panel y los selects se limpian (`handleFileChange` ya lo hace), ejecutar
  el análisis y llegar a `/stream`.
- La ruta de degradación sigue viva: con un archivo no parseable, banner de
  warning + inputs de texto, análisis no bloqueado.

---

## 6. Bloque F — Blur del fondo en el modal de atípico

Resuelve P9. El bloque más chico: un archivo, dos declaraciones.

### F1 — El blur va en el scrim, no (solo) en la tarjeta

La ronda 3 de la pasada 4 movió el blur del scrim a la tarjeta, con el
razonamiento de que un panel de vidrio desenfoca lo que hay **detrás suyo**.
Eso es correcto para el borde de la tarjeta, pero dejó el resto de la página
—el timeline de pruebas, la `TopBar`, el fondo animado— perfectamente nítido
alrededor del diálogo. En `StreamPage.css`:

```css
.modal-backdrop {
  background: rgba(9, 12, 16, 0.4);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.modal-backdrop .card {
  backdrop-filter: blur(10px) saturate(180%);   /* era 20px */
  -webkit-backdrop-filter: blur(10px) saturate(180%);
}
```

El blur de la tarjeta baja de 20px a 10px porque ahora se compone sobre un
fondo ya desenfocado: mantenerlo en 20px vuelve el contenido de la tarjeta
lechoso sin ganar separación.

### F2 — Lo que no se toca, por ninguna razón

`StreamPage.tsx` no cambia. El auto-foco al contenedor del diálogo, el
`inert` sobre el contenido de fondo, el manejo de Escape que **no** cierra el
modal y la restauración del foco al cerrar son la decisión M3 de la pasada 3,
y están ahí por una razón de producto documentada: el backend está bloqueado
esperando en `session_store` (hasta 300s) y las dos únicas salidas válidas
son `TEST_OUTLIER_REJECTED_BY_USER` y `TEST_OUTLIER_ACCEPTED_BY_USER`. Este
bloque es presentación pura.

### F3 — Criterios de hecho del Bloque F

- `npm test` verde con `StreamPage.test.tsx` y
  `StreamPage.integration.test.tsx` **sin modificar**.
- Verificación manual con el CSV de atípico forzado (el de la verificación
  E2E de la pasada anterior): al abrir el modal, el timeline de atrás se ve
  desenfocado; al decidir, vuelve nítido y el stream continúa con
  `iteracion: 2`.

---

## 7. Orden de ejecución y agrupación en PRs

Los bloques tienen dependencias reales: A define `--glow`, que B consume; A2
ajusta `--bg`, contra el que C se calibra.

| PR | Bloques | Por qué juntos |
|---|---|---|
| 1 | A + B | Tokens de luz y los fondos que los consumen — verificables solo juntos |
| 2 | C + D | Superficies y elevación: cards y el cluster de la barra |
| 3 | E | Único bloque con comportamiento y componente nuevo |
| 4 | F | Aislado, dos declaraciones CSS |

Los cuatro salen de `staging` y vuelven a `staging` por PR, según el
GitHub Flow de tres niveles de `constraints.md`. PR 2 depende de PR 1
mergeado (C se calibra contra el `--bg` nuevo).

---

## 8. Definition of done — para los cuatro PRs

Además de los criterios de hecho de cada bloque:

1. `cd frontend && npm run lint && npm test && npm run build` — los tres en
   verde, corridos después del último commit del PR.
2. Los cuatro jobs de `ci.yml` en verde (`lint`, `test`, `error-catalog`,
   `frontend`).
3. **Evidencia de navegador en los dos temas**, después del último commit del
   PR — captura de cada pantalla afectada en claro y en oscuro. Esta es la
   Capa 4 de `testing.md`, y es la que existe precisamente porque esta pasada
   entera es la factura de haberla salteado en la anterior.
4. Ninguna aserción de test existente modificada sin justificarlo en el PR.
   Si un test hay que tocarlo, o el bloque se fue de alcance o el test estaba
   verificando presentación en vez de comportamiento — las dos cosas se
   discuten antes de mergear, no después.

---

## 9. Documentación a actualizar al cerrar

- `docs/decisiones/decision051.md` — salida de Three.js y strands en Canvas
  2D (revierte el addendum de DECISIÓN 045). **Bloqueante del PR 1.**
- `docs/decisiones/decision045.md` — nota de superación apuntando a la 051.
- `docs/decisiones/README.md` — entrada de la 051.
- `docs/frontend/informe-resultados-pasada5.md` — informe de cierre, con el
  estado de verificación bloque por bloque y el tamaño del bundle antes y
  después (Bloque B).
- `.claude/rules/sprint.md` — sección de la pasada 5 en la línea de
  `feature/frontend-*`.
- `CLAUDE.md` — sección "Frontend — estado actual": el párrafo de la pasada 4
  menciona "dos fondos animados en Canvas 2D (DECISIÓN 045)"; pasan a ser
  tres, y ya no hay ninguno en Three.js.

---

## 10. Fuera de alcance de esta pasada — explícito

- **Contraste WCAG AA de `tokens.instrumento.css`** — DECISIÓN 043, pendiente
  de decisión de Kevin/Octavio. A2 toca `--bg` y `--line` (superficies), no
  tokens de texto; no la resuelve ni la contradice.
- **Etapa 2 real.** Las pantallas de ranking y eventos de diseño siguen
  mockeadas con su `PendingBadge`, porque el gap es de backend, no de
  frontend: `POST /analysis/design-events` está documentado y no implementado,
  el ranking no tiene endpoint REST (solo un evento SSE que el backend nunca
  emite), y `POST /analysis/stream` recibe `etapas` y lo descarta
  (DECISIÓN 037). Ver [DECISIÓN 042](../decisiones/decision042.md).
- **Partición de Cramer personalizada** — DECISIÓN 036, sin decidir entre las
  tres opciones evaluadas. El botón sigue `disabled`.
- **E2E con Playwright** — DECISIÓN 046, sin escribir; `constraints.md` los
  excluye del scope V1.0.
- **Gráficos de Etapa 1** — `Etapa1Result` no expone la serie cruda (FE-16).
  Es un cambio de contrato de backend, no de presentación.
