# DECISIÓN 051 — ThreadsBackground pasa de Three.js a Canvas 2D; Three.js sale del proyecto
**Fecha:** 06 de Agosto de 2026
**Estado:** Implementada

### Contexto

[DECISIÓN 045](decision045.md) fijó Canvas 2D + `requestAnimationFrame`, sin
dependencias nuevas, como la vía elegida para los fondos animados de la
identidad "Instrumento" — y su addendum del 05/08/2026 abrió una excepción
puntual: `ThreadsBackground` (el fondo de "hilos" de la puerta de entrada)
se implementó con Three.js, admitido explícitamente como "la excepción
documentada", justificada porque el chunk se cargaba únicamente en `/` vía
`React.lazy()` — ninguna pantalla autenticada pagaba el costo (medido en su
momento: +128.37 KB gzip en un chunk aparte, +0.52 KB en el bundle
principal).

`docs/frontend/plan-mejora-frontend-pasada5.md` (Bloque B) encontró P4: la
pantalla `/config` no tiene strands, solo el dot field — la segunda pantalla
del flujo debía mantener los hilos además del campo de puntos. Montar
`ThreadsBackground` tal como estaba en más de una ruta invierte la premisa
que sostenía la excepción de DECISIÓN 045: si todas las pantallas
(autenticadas incluidas) van a montar el componente, todas pasarían a cargar
Three.js para dibujar 18 polilíneas sinusoidales — exactamente el costo que
el Bloque B original de la pasada 4 había descartado.

### Qué hacía la versión Three.js

`ThreadsBackground.tsx` (versión anterior a esta decisión) usaba:
- `THREE.Scene` + `THREE.OrthographicCamera(-1, 1, 1, -1, 0, 10)` — cámara
  ortográfica sin perspectiva, coordenadas NDC (-1..1).
- `THREE.WebGLRenderer({ alpha: true, antialias: true })`, sin luces, sin
  materiales con sombreado, sin profundidad real.
- 18 `THREE.Line` (`THREAD_COUNT`), cada una con `THREE.BufferGeometry` de 64
  puntos (`POINTS_PER_THREAD`) y un `THREE.LineBasicMaterial` plano
  (`transparent: true`, opacidad fija por hilo).
- `THREE.Color.lerp` para interpolar una paleta de 5 tonos
  (`PALETTE_STEPS`) entre `--glow` y `--acc2`.

Es decir: geometría 2D pura (una polilínea por hilo, sin normales, sin
texturas, sin cámara en perspectiva) renderizada con un motor 3D completo.
El propio addendum de DECISIÓN 045 ya lo describía así ("cámara ortográfica,
sin luces, sin materiales, sin profundidad — es una polilínea 2D").

### Por qué se reemplaza

1. **Invalida la justificación de la excepción de DECISIÓN 045.** Esa
   excepción se sostenía en que el costo quedaba aislado a una sola ruta.
   Resolver P4 (strands en `/config`) montando el mismo componente en más
   pantallas rompe esa premisa — el resto de las pantallas autenticadas
   pasarían a cargar el chunk de Three.js, que es justo el escenario que la
   decisión original (Bloque B, pasada 4) había descartado por costo de
   bundle.
2. **El efecto no necesita un motor 3D.** Una polilínea 2D animada con una
   función de onda es geometría de canvas trivial — exactamente el mismo
   argumento que ya sostiene a `DotFieldBackground` y `GridScanBackground`
   en Canvas 2D puro.
3. **Reescribirlo en Canvas 2D permite reusar la infraestructura ya
   probada** de los otros dos fondos: `sizeCanvasToViewport`,
   `secureRandom`, `readCssVar`, las cuatro guardas de ciclo de vida
   (`prefers-reduced-motion`, `visibilitychange`, `IntersectionObserver`,
   cleanup completo) — sin reinventar nada, solo trasladando la
   implementación del wave function y la paleta de un `THREE.Line` a un
   `ctx.beginPath()`/`lineTo()`.

### Opciones evaluadas

1. **Dejar `ThreadsBackground` en Three.js y montarlo también en
   `/config`.** Descartada: reabre exactamente el costo de bundle que
   DECISIÓN 045 había descartado para el resto de las pantallas — la
   excepción deja de ser "una sola ruta paga el costo" para convertirse en
   "todas las pantallas autenticadas pagan el costo", sin ningún cambio en
   la justificación original que lo sostenga.
2. **Mantener dos componentes: uno Three.js para `/` y una reimplementación
   Canvas 2D nueva para el resto de las pantallas.** Descartada: dos
   implementaciones del mismo efecto visual (mismos parámetros, misma
   función de onda) es deuda de mantenimiento sin beneficio real — cualquier
   ajuste futuro (paleta, densidad, velocidad) habría que aplicarlo dos
   veces y mantenerlas visualmente idénticas a mano.
3. **Reescribir `ThreadsBackground` en Canvas 2D, con exactamente los mismos
   parámetros visuales, y sacar Three.js del proyecto.** Elegida — mismo
   componente para las tres pantallas, sin duplicar código, sin pagar el
   costo de un motor 3D en ninguna ruta.

### Decisión

`ThreadsBackground.tsx` se reescribe en Canvas 2D + `requestAnimationFrame`,
hermana de `DotFieldBackground.tsx`/`GridScanBackground.tsx` en
`frontend/src/theme/backgrounds/`. Conserva su nombre, su ubicación y su
contrato externo (componente sin props, `<canvas>` `position: fixed;
inset: 0; z-index: -1; pointer-events: none`).

**Parámetros visuales conservados sin cambios** respecto a la versión
Three.js: `THREAD_COUNT = 18`, `POINTS_PER_THREAD = 64`,
`PALETTE_STEPS = 5`, la misma función de onda
(`sin(x*3 + t*speed + seed)*0.15 + sin(x*7 - t*speed*1.7 + seed)*0.05`), los
mismos rangos de `speed` (`0.15 + secureRandom()*0.15`) y `yOffset`
(`(i/(THREAD_COUNT-1))*2-1`). Lo único que cambia es el mecanismo de
render:

- Coordenadas: la cámara ortográfica trabajaba en NDC (-1..1); la versión
  Canvas 2D conserva la función de onda en NDC y solo agrega un paso final
  de mapeo a píxeles del viewport (`ndcToPixel`), usando
  `sizeCanvasToViewport` — el mismo helper que ya usan los otros dos
  fondos.
- La interpolación de paleta que hacía `THREE.Color.lerp` se implementa como
  `lerpHex(a, b, t)` en `canvasUtils.ts` — interpolación lineal por canal
  RGB, función pura y exportada, con su propio test unitario
  (`canvasUtils.test.ts`).
- `secureRandom()` se conserva sin cambios para sembrar las semillas de cada
  hilo (ya existía en `canvasUtils.ts` — Sonar marca `Math.random()` sin
  distinguir jitter visual de valores sensibles).
- Las cuatro guardas de ciclo de vida son las mismas de siempre:
  `prefersReducedMotion()` → un solo `draw(0)` sin loop;
  `visibilitychange` → no dibuja en pestaña oculta; `IntersectionObserver`
  → no dibuja fuera del viewport; cleanup completo (`cancelAnimationFrame` +
  los tres listeners desregistrados + `intersectionObserver.disconnect()`).
  La única guarda que cambia de forma es la que protegía la creación del
  renderer: `try { new THREE.WebGLRenderer() } catch { return; }` pasa a ser
  `const ctx = canvas.getContext("2d"); if (!ctx) return;` — mismo rol
  (degradar sin romper el render de la app si el contexto no está
  disponible), mismo mecanismo que ya usan `DotFieldBackground` y
  `GridScanBackground`.

`ThreadsBackground` se monta siempre en `RootLayout.tsx`, sin
`React.lazy()` ni `<Suspense>` — el `lazy(...)` que lo acotaba a `pathname
=== "/"` se elimina junto con el comentario que lo explicaba, porque ya no
hay ningún costo de chunk que aislar.

`frontend/package.json` pierde `three` y `@types/three` — no queda ninguna
dependencia de Three.js en el proyecto.

### Qué gana el proyecto

- **Bundle más chico, no solo redistribuido.** Antes: `index.js` (bundle
  principal) 332.98 KB minificados / 112.23 KB gzip, más un chunk aparte
  `ThreadsBackground-*.js` de 507.63 KB minificados / 128.37 KB gzip que
  solo `/` descargaba. Después: un único `index.js` de 333.50 KB
  minificados / 112.25 KB gzip, sin chunk aparte. El total que puede llegar
  a descargar un usuario baja de ~840.6 KB a ~333.5 KB minificados (~240.6
  KB a ~112.25 KB gzip) — no es que el costo se movió de un chunk a otro,
  desapareció: la reescritura en Canvas 2D no agrega peso comparable al que
  sacó.
  Medido con `npm run build` sobre el mismo estado del árbol de trabajo,
  alternando `three`/`@types/three` en `package.json` + `npm install` para
  reproducir "antes" y "después" exactos (no una estimación).
- **Strands disponibles en todas las pantallas sin pagar el costo de Three.js
  en ninguna** — resuelve P4 sin reabrir el problema que motivó la
  excepción de DECISIÓN 045 en primer lugar.
- **Un solo mecanismo de render para los tres fondos** — mismas guardas,
  mismos helpers (`sizeCanvasToViewport`, `secureRandom`, `readCssVar`),
  mismo patrón de test (`*.lifecycle.test.tsx`). Menos superficie
  conceptual para quien lea `frontend/src/theme/backgrounds/` por primera
  vez: tres archivos con la misma forma, no dos con una excepción aparte.
- **Menos dependencias de producción** — `three` (y su `@types/three` de
  desarrollo) salen del árbol de dependencias por completo, con todo lo que
  eso implica para `npm audit`, tiempo de `npm install` y superficie de
  actualización futura.

### Verificación

- `npm test` — 33 archivos, 186 tests en verde, incluidos
  `ThreadsBackground.lifecycle.test.tsx` (las cuatro guardas, adaptado de
  `new THREE.WebGLRenderer()` en `try/catch` a `getContext("2d")` devolviendo
  `null`, sin modificar ninguna aserción existente) y el test nuevo de
  `lerpHex` en `canvasUtils.test.ts`.
- `npm run lint` limpio.
- `npm run build` verde, tamaños de bundle documentados en la sección
  anterior.
- `grep -rn "three" frontend/src frontend/package.json` sin coincidencias.
- Verificación visual manual (strands en `/` y `/config`, en los dos temas,
  conviviendo con el dot field) — diferida al controlador de esta tarea; el
  entorno de esta sesión no tiene un navegador real disponible.

### Criterio de hecho

- `frontend/package.json` no lista `three` ni `@types/three` en ninguna
  sección.
- `frontend/src/theme/backgrounds/ThreadsBackground.tsx` no importa `three`
  — usa `canvasUtils.ts` (`hexToRgba`, `lerpHex`, `prefersReducedMotion`,
  `readCssVar`, `secureRandom`, `sizeCanvasToViewport`), igual que sus dos
  hermanos.
- `frontend/src/components/RootLayout.tsx` monta `<ThreadsBackground />`
  incondicionalmente, sin `lazy()` ni `<Suspense>`.
- `grep -rn "three" frontend/src frontend/package.json` vacío.

**Ver también:** [DECISIÓN 045](decision045.md) — la decisión que esta
051 supera parcialmente (el addendum del 05/08/2026 sobre la excepción de
Three.js queda superado; la decisión original de Canvas 2D para
`DotFieldBackground`/`GridScanBackground` sigue vigente sin cambios, y ahora
se extiende a los tres fondos).
