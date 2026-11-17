# DECISIÓN 059 — Selector de intensidad de animación (alta/media/sin animaciones)

**Fecha:** 14 de Agosto de 2026
**Estado:** Implementada

### Contexto

Bloque A del plan post-avance (`docs/plan-post-avance.md`, insumo de Kevin
tras la reunión de avance con los directores). Feedback de Octavio: la
interfaz se percibe "barroca" — sobrecargada de movimiento. Antes de este
PR, la única puerta de salida era `prefers-reduced-motion` del sistema
operativo — todo o nada, y el usuario no la controla desde adentro de la
app.

### Inventario de movimiento en la app (verificado archivo por archivo)

1. `ThreadsBackground` — 18 hilos animados, en todas las pantallas.
2. `DotFieldBackground` — grilla de puntos que reacciona al puntero, en
   todas menos `/`.
3. `GridScanBackground` — barrido de haz sobre grilla, solo en `/`.
4. `SpotlightCard` — brillo que sigue al mouse dentro de cada card.
5. `Magnet` — el botón se desplaza hacia el cursor.
6. `SpecularHighlight` — reflejo especular sobre botones primarios.
7. `CountUp` — los números se cuentan hacia arriba al aparecer.
8. `.route-enter`/`.step-entrance`/`.pill` — fade-up de entrada.
9. `badge-pulse`/`prog-sweep` — loops infinitos de estado ("en vivo",
   barra de progreso).
10. Cápsula deslizante del nav (`.topbar__pill-indicator`).
11. Transiciones de hover/active/focus (`--t-fast`/`--t-mid`/`--t-slow`).

### Qué significa cada nivel

**`alta`** — exactamente lo de hoy. Default, sin cambios.

**`media`** — decisión de producto de Kevin: los tres fondos **siguen
animándose**, pero con mucha menos densidad — no se apagan, porque la
identidad "Instrumento" se conserva; lo que molesta es la carga, no el
fondo en sí:
- `ThreadsBackground`: 18 → 6 hilos.
- `DotFieldBackground`: paso de grilla 28 → 56 (una cuarta parte de los
  puntos en 2D) y **sin seguimiento del puntero** — el listener de
  `pointermove`/`pointerleave` directamente no se registra.
- `GridScanBackground`: se conserva la grilla base, se **apaga el haz de
  barrido** — el elemento más llamativo del fondo.
- Todos los efectos de puntero (`SpotlightCard`, `Magnet`,
  `SpecularHighlight`) se apagan — cada uno sigue renderizando su
  estructura (el `<div>`/`<span>` real, con `className`/`style`), solo sin
  el listener ni el efecto reactivo.
- Se conservan sin cambios: entradas fade-up, transiciones de hover/foco,
  `CountUp`, los dos loops de estado (`badge-pulse`, `prog-sweep`) y la
  cápsula del nav — son informativos, no decorativos.

**`off`** — equivalente exacto a `prefers-reduced-motion: reduce`: los
tres fondos **no se montan** (no alcanza con no animarlos — no arrancar el
`requestAnimationFrame` es el punto), efectos de puntero apagados,
entradas apagadas, loops apagados, transiciones a `0.01ms`.

### El sistema operativo manda

Si `prefers-reduced-motion: reduce` está activo a nivel SO, el nivel
efectivo es `off` sin importar lo que el usuario haya elegido en la app —
regla de accesibilidad, no configurable. El selector lo dice
explícitamente ("tu sistema pide movimiento reducido") en vez de
comportarse como si no hiciera nada.

### Implementación

- **`frontend/src/theme/motion.ts`** — extendido con `MotionLevel` y
  `resolveMotionLevel(stored)`, que combina la preferencia guardada con
  `prefersReducedMotion()`. `prefersReducedMotion()` en sí no cambia.
- **`frontend/src/theme/MotionProvider.tsx`** (nuevo) — hermano de
  `ThemeProvider.tsx`, mismo patrón (`useState` con init perezoso desde
  `localStorage`, `useLayoutEffect` que escribe
  `document.documentElement.dataset.motion` y persiste bajo
  `metis-motion-level`). Expone `useMotion()`: `{level, effectiveLevel,
  setLevel, systemForcesReduced}`.
- **Desviación deliberada de `useTheme()`:** `useTheme()` lanza si no hay
  `<ThemeProvider>` ancestro; `useMotion()` **degrada a `{level: "alta",
  effectiveLevel: "alta", ...}`** en vez de lanzar. Motivo: `useTheme()`
  tiene un solo consumidor (`TopBar`); `useMotion()` lo leen ampliamente
  `SpotlightCard`/`Magnet`/`SpecularHighlight` (usados en decenas de
  pantallas) y los tres fondos animados. Exigir el provider en cada test
  que los toque habría sido una superficie de rotura enorme por una
  preferencia que, sin proveedor, debe comportarse exactamente igual que
  antes de este feature: "alta", sin restricciones. La app real siempre
  tiene el provider (`main.tsx`) — el default solo importa en aislamiento
  (tests). Verificado: los 258 tests existentes de la suite (incluidos
  `SpotlightCard.test.tsx`, `Magnet.test.tsx`, `SpecularHighlight.test.tsx`,
  y las tres `*.lifecycle.test.tsx` de los fondos) siguieron pasando **sin
  ninguna modificación** gracias a este default.
- **`useCanvasAnimationLoop.ts`** — gana un parámetro `motionLevel`
  (posicional, antes de `setupExtra`), que se suma a las dependencias del
  efecto (`[canvasRef, motionLevel]`). Es la única razón para que
  `motionLevel` viaje como parámetro del hook: `draw`/`setupExtra` ya se
  leen vía ref y no necesitan que el efecto reinicie para reflejar
  cambios — pero `setupExtra` (el registro de listeners de puntero de
  `DotFieldBackground`) solo se invoca **una vez** por montaje; sin
  reiniciar el efecto, pasar de "alta" a "media" nunca desregistraría el
  tracking de puntero hasta un remount real. `prefersReducedMotion()` se
  conserva dentro del hook como defensa en profundidad (mismo criterio que
  `Magnet.tsx` conserva su propio chequeo inline).
- **Los tres fondos** leen `useMotion().effectiveLevel` y ajustan su
  propia densidad; `ThreadsBackground` necesita regenerar
  `threadsRef.current` explícitamente cuando cambia el nivel (el patrón
  original `threadsRef.current ??= ...` solo asigna una vez — se agregó
  `threadsLevelRef` para detectar el cambio).
- **`RootLayout.tsx`** decide si monta o no cada fondo según
  `effectiveLevel === "off"` — la responsabilidad de "no montar" vive acá,
  no en cada fondo.
- **`TopBar.tsx`** — `<select>` nativo de tres opciones junto al toggle de
  tema, con una nota condicional cuando `systemForcesReduced` es `true`.

### Opciones evaluadas para el "apagado" de `GridScanBackground` en "media"

El plan post-avance dejaba dos alternativas: apagar el haz de barrido por
completo, o subir `CYCLE_MS` de 6000 a ~18000 (barrido más lento en vez de
ausente). Se eligió **apagar el haz** — es la opción que el propio plan
marca como preferida ("lo más llamativo del fondo"), y mantiene la grilla
base con exactamente el mismo tratamiento visual que `DotFieldBackground`
en "media" (fondo conservado, elemento más activo apagado), en vez de
introducir un tercer criterio (velocidad reducida) que ninguno de los
otros dos fondos usa.

### Verificación

- `npx tsc -b` y `npm run lint` limpios.
- `npm test` — 271 tests en verde (258 preexistentes sin modificar +
  `MotionProvider.test.tsx`, `RootLayout.test.tsx` nuevos, y casos nuevos
  agregados a las tres `*.lifecycle.test.tsx` de los fondos y a
  `TopBar.test.tsx`).
- `npm run build` verde.
- No verificado en navegador real dentro de esta sesión (ver
  `docs/pendientes-tecnicos.md` si corresponde anotarlo) — la verificación
  del resto del plan post-avance sí se hizo contra Docker real; este
  bloque quedó cubierto por la suite automatizada solamente.

### Criterio de hecho

- `document.documentElement.dataset.motion` refleja el nivel efectivo
  (`alta`/`media`/`off`) en todo momento, y `localStorage["metis-motion-level"]`
  persiste la elección del usuario (no la efectiva).
- Con `off`, ningún `<canvas>` de fondo está en el DOM
  (`RootLayout.test.tsx`).
- Con `media`, los tres fondos siguen montados pero
  `DotFieldBackground` no registra `pointermove`/`pointerleave`, y
  `GridScanBackground` sigue con un loop de rAF vivo (la grilla no se
  apaga, solo el haz).
- `prefers-reduced-motion: reduce` del sistema fuerza `effectiveLevel =
  "off"` sin importar `level` guardado.

**Ver también:** [DECISIÓN 045](decision045.md)/[051](decision051.md) —
la infraestructura de Canvas 2D que este PR extiende, sin reemplazarla.
