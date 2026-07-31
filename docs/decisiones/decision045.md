# DECISIÓN 045 — Fondos animados en Canvas 2D sin dependencias, WebGL descartado
**Fecha:** 31 de Julio de 2026
**Estado:** Decidida — implementación en curso (Bloque B, pasada 4)

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
Comparación de `npm run build` antes (commit `9f6d5f5`, A1-A4 sin fondos) y
después de implementar B2/B3 (Canvas 2D, cero dependencias nuevas — la única
adición de `package.json` en toda la pasada hasta este punto fue
`@fontsource-variable/jetbrains-mono` en A1, ya contabilizada). Como no se
agrega ninguna librería para los fondos, el costo es exactamente el peso del
código propio de `DotFieldBackground.tsx`/`GridScanBackground.tsx` — sin
overhead de dependencia externa. Cifras exactas en el commit que cierra B7.

### Criterio de hecho
- `frontend/package.json` no gana ninguna dependencia nueva por los fondos
  animados (`git diff` entre el commit de A4 y el de cierre de Bloque B).
- `frontend/src/theme/backgrounds/DotFieldBackground.tsx` y
  `GridScanBackground.tsx` no importan `three` ni ninguna librería de
  partículas/WebGL.

**Ver también:** `docs/frontend/plan-mejora-frontend-pasada4.md` §4 (Bloque B
completo, guardas B4, presupuesto de rendimiento B7).
