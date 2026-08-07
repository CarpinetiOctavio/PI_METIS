# DECISIÓN 045 — Fondos animados en Canvas 2D sin dependencias, WebGL descartado
**Fecha:** 31 de Julio de 2026
**Estado:** Implementada, bundle medido — falta verificación visual final (Bloque G, cierre de PR1).
Addendum 05/08/2026 (segundo): excepción puntual a "WebGL descartado" para
`ThreadsBackground` en la puerta de entrada, acotada por code-splitting —
ver abajo. La decisión original (Canvas 2D sin dependencias para
`DotFieldBackground`/`GridScanBackground`) sigue vigente sin cambios.

### Addendum (05/08/2026, segundo) — excepción acotada: Threads (three.js) en la puerta de entrada

Verificación manual de Bloque C (`docs/plan-post-pasada4-roadmap.md` §3)
pidió explorar fondos más elaborados con three.js (referencias reactbits.dev
"Threads"/"Beams"), comparando fidelidad real, no una aproximación — ver
`frontend/src/experimental/README.md` (exploración descartable, no
comiteada) para el detalle de las dos rondas de feedback. Veredicto final:
**Threads queda confirmado para la puerta de entrada, `three`/`gsap` pasan a
dependencias reales.**

**Por qué esto no contradice la decisión original.** El argumento de más
arriba ("Opciones evaluadas", opción 1) fue "~600 KB adicionales al bundle
de producción... el costo no es proporcional al efecto buscado" — ese
argumento asumía que el costo se paga en **el bundle principal**, cargado
por **todas** las pantallas. `RootLayout.tsx` ahora importa
`ThreadsBackground` con `React.lazy()` + `import()` dinámico, montado
únicamente cuando `pathname === "/"` — el chunk de three.js nunca se
descarga para ninguna pantalla autenticada (config, stream, resultados,
ranking, historial, etc.), que es donde vive el 90% del uso real de la app.

**Costo en bundle — medido** (`npm run build`, antes vs. después de este
addendum):

| | Antes | Después | Delta |
|---|---|---|---|
| `index.js` (bundle principal, gzip) | 82.53 KB | 83.05 KB | **+0.52 KB** |
| `ThreadsBackground-*.js` (chunk aparte, gzip) | — | 128.37 KB | solo carga en `/` |

El bundle principal —el que paga cada pantalla autenticada— prácticamente
no se movió. Los 128 KB de three.js quedan aislados en un chunk que un
usuario que solo usa CU-01/CU-02 después de loguearse jamás descarga.

**Guardas obligatorias** (mismas que B4 exige para los otros dos fondos,
aplicadas acá también — ver `ThreadsBackground.tsx`): respeta
`prefers-reduced-motion` sin arrancar el loop, cancela `requestAnimationFrame`
en la limpieza (StrictMode monta dos veces), pausa fuera de viewport o
pestaña oculta, escala por `devicePixelRatio`. Guarda adicional propia de
este componente: `new THREE.WebGLRenderer()` está en un `try/catch` — WebGL
no está garantizado (GPU deshabilitada, navegador viejo, o directamente
jsdom en la suite de tests) y sin la guarda tira una excepción que rompe el
render de la puerta de entrada entera en vez de degradar a "sin Threads,
GridScanBackground sigue andando encima" (`ThreadsBackground.lifecycle.test.tsx`
cubre este caso explícitamente).

**Alcance de la excepción — no es un cambio general de postura.**
`DotFieldBackground` y `GridScanBackground` (las pantallas autenticadas y el
resto de la puerta de entrada) siguen en Canvas 2D puro, sin dependencias,
sin cambios. Esto no reabre la puerta a WebGL en cualquier lugar — es una
excepción puntual, justificada con números reales, para un solo componente
en una sola ruta, con el costo medido y aislado por diseño.

### Addendum (05/08/2026, primero) — presupuesto de CPU (B7) sin medir

`docs/plan-post-pasada4-roadmap.md` (§1.2, "debilidades reales del proceso")
registra que la verificación final del Bloque G quedó a mitad: **5 de 14
puntos sin evidencia directa**, por límites de la herramienta de navegador de
esa sesión — entre ellos, el **ítem 14 de la tabla G2**
(`plan-mejora-frontend-pasada4.md` línea 430): "CPU — Performance monitor en
reposo en `/config`: fondo por debajo del presupuesto de B7".

De los tres criterios medibles de B7 (línea 303-309 de ese plan), solo el del
bundle quedó verificado con números reales en la sección "Costo en bundle —
medido" de más abajo (+1.37 KB gzip, muy por debajo de los 8 KB de
presupuesto). **El criterio de CPU en reposo (~2% en un equipo de escritorio
normal, medido con el Performance monitor de DevTools) no se midió** — se
declaró pendiente en su momento, no se ocultó, pero sigue siendo deuda real
hasta que el Bloque C de la Pasada 5 (`docs/plan-post-pasada4-roadmap.md`
§3) lo cierre con evidencia (vía C1a manual o C1b Playwright).

### Contexto
`docs/frontend/plan-mejora-frontend-pasada4.md` (G3) encontró que la identidad
visual "Instrumento" (`docs/frontend-design/metis-identidad-fase2.md`,
Dirección 4) especifica una "línea de escaneo con glow" y una retícula técnica
reactiva que nunca se implementaron — la retícula de fondo existe
(`.app-shell`, `global.css`) pero es estática. El punto 2 del feedback de UX
pedía justo esto: que la app deje de sentirse "muy simple", y el fondo animado
es la pieza más visible de esa causa que faltaba resolver.

Las referencias visuales que motivaron el pedido (componentes tipo
`pixel-blast`/`grid-distortion` de librerías de efectos como reactbits) están
implementadas con Three.js + postprocessing.

### Opciones evaluadas
1. **Three.js + postprocessing** (la vía de las referencias). Descartada:
   ~600 KB adicionales al bundle de producción por un efecto de fondo, en una
   app que se despliega en la intranet de la UCC (sin CDN garantizado, ver
   `architecture.md`) y cuyo `npm run build` corre en CI en cada PR
   (`.github/workflows/ci.yml`, job `frontend`). El costo no es proporcional
   al efecto buscado — un campo de puntos y un barrido son geometría simple,
   no necesitan un motor 3D completo.
2. **Librería CSS-only de partículas** (ej. tsparticles). Descartada sin
   prototipar: igual necesita JS para reaccionar al cursor con la calidad que
   pide la identidad (onda de influencia, decaimiento), y sumar una
   dependencia externa para algo que Canvas 2D nativo resuelve en un archivo
   por componente no se justifica.
3. **Canvas 2D + `requestAnimationFrame`, sin dependencias nuevas.** Elegida.
   API nativa del navegador, ya usada indirectamente por el resto del stack
   (React no necesita ningún wrapper para Canvas). La calidad del efecto
   buscado depende del ajuste fino (densidad de puntos, easing, opacidad,
   respuesta al cursor), no de la tecnología de renderizado — Canvas 2D es
   perfectamente suficiente para dos fondos: un campo de puntos reactivo
   (`DotFieldBackground`, la app) y un barrido cíclico
   (`GridScanBackground`, la puerta de entrada).

### Decisión
Los dos fondos animados de la pasada 4 (Bloque B) se implementan en Canvas 2D
puro, sin ninguna dependencia nueva de npm. Guardas obligatorias (detalladas
en el plan, §4 B4, no repetidas acá): respetar `prefers-reduced-motion` sin
arrancar el loop, cancelar `requestAnimationFrame` en la limpieza del efecto
(clase de bug F1 — StrictMode monta dos veces), pausar fuera de viewport o
pestaña oculta, escalar por `devicePixelRatio`.

### Costo en bundle — medido
`npm run build` antes (commit `2cc3ef9`, A1-A4 + esta decisión, sin fondos
todavía cableados) vs. después de B2/B3 (DotFieldBackground +
GridScanBackground + canvasUtils, montados en RootLayout/EntryPage):

| | Antes | Después | Delta |
|---|---|---|---|
| JS (gzip) | 79.07 KB | 80.44 KB | **+1.37 KB** |
| CSS (gzip) | 6.09 KB | 6.09 KB | sin cambio |

Muy por debajo del presupuesto de 8 KB gzip (B7). `frontend/package.json` no
ganó ninguna dependencia nueva — el delta es exactamente el peso del código
propio de los dos componentes y `canvasUtils.ts`, sin overhead de librería
externa, confirmando la premisa de esta decisión.

### Criterio de hecho
- `frontend/package.json` no gana ninguna dependencia nueva por los fondos
  animados (`git diff` entre el commit de A4 y el de cierre de Bloque B).
- `frontend/src/theme/backgrounds/DotFieldBackground.tsx` y
  `GridScanBackground.tsx` no importan `three` ni ninguna librería de
  partículas/WebGL.

**Ver también:** `docs/frontend/plan-mejora-frontend-pasada4.md` §4 (Bloque B
completo, guardas B4, presupuesto de rendimiento B7).

### Nota de superación (06/08/2026)

El addendum de arriba ("excepción acotada: Threads (three.js) en la puerta
de entrada") queda **superado por [DECISIÓN 051](decision051.md)**.
`docs/frontend/plan-mejora-frontend-pasada5.md` (Bloque B) necesitó strands
también en `/config` — montar la versión Three.js en más de una pantalla
invalidaba la premisa que sostenía esta excepción ("ninguna pantalla
autenticada paga el costo del chunk"), así que `ThreadsBackground` se
reescribió en Canvas 2D (mismos parámetros visuales, misma función de onda)
y `three`/`@types/three` salieron por completo del proyecto. La decisión
original de este archivo (Canvas 2D sin dependencias para
`DotFieldBackground`/`GridScanBackground`) no cambia — al contrario, ahora
es el criterio que rige los tres fondos, no solo dos. Ningún contenido de
este archivo se borra; esta nota queda como registro de que el addendum de
arriba ya no describe el estado real del código.
