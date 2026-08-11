# DECISIÓN 056 — Gráficos interactivos de Etapa 2: `d3-scale` + `d3-shape` con SVG propio
**Fecha:** 11 de Agosto de 2026
**Estado:** Decidida — implementación en curso

### Contexto

`docs/plan-etapa2-implementacion.md`, Bloque C, pide dos gráficos interactivos
sobre los resultados de Etapa 2 — gráfico de ajuste (puntos empíricos contra
la curva de la distribución elegida) y eventos de diseño (xT contra T, eje x
logarítmico) — con zoom, tooltip con el valor exacto de cada punto, tematizado
con los tokens del design system "Instrumento", testeable en jsdom, y sin
volver a inflar el bundle apenas [DECISIÓN 051](decision051.md) sacó Three.js
del proyecto.

### Opciones evaluadas

| Opción | Peso aprox. | Problema |
|---|---|---|
| Recharts | ~100 kB gz | Sistema de theming propio — tematizar con los tokens de Instrumento es pelear contra su API, no usarla |
| uPlot | ~15 kB gz | Renderiza en `<canvas>` — jsdom no implementa canvas 2D, mismo obstáculo de testing que ya obligó a los fondos animados a su propio patrón de test (`*.lifecycle.test.tsx` con mocks de `getContext`), esta vez sin esa opción disponible: los tests de gráficos necesitan verificar valores exactos de datos, no solo ciclo de vida |
| **`d3-scale` + `d3-shape` + SVG propio** | **~10 kB gz** | Zoom, tooltip y navegación por teclado se escriben a mano (~150 líneas) |

### Decisión

`d3-scale` (`scaleLog`, `scaleLinear`) para los ejes y `d3-shape`
(`line`, `curveMonotoneX`) para el generador de la curva de ajuste. Sin
ningún framework de charting completo — el resto (ejes, ticks, zoom,
tooltip, foco de teclado) se escribe en un componente propio,
`frontend/src/charts/InteractiveChart.tsx`.

**Motivos:**

1. **Renderiza SVG real, no canvas.** Los tests pueden usar
   `getByRole`/`getByText`/`container.querySelector("path")` sobre el DOM
   real que ve el usuario — mismo principio que ya rige el resto de la
   suite (`testing.md`, Capa 1/2: nada de snapshots, nada de mockear lo que
   se puede renderizar de verdad). Con canvas (uPlot) los tests solo podrían
   verificar que se llamó a `getContext` y no qué se dibujó, que es
   exactamente el techo que ya tienen `DotFieldBackground`/
   `GridScanBackground`/`ThreadsBackground` — aceptable para un fondo
   decorativo, no para un gráfico cuyo valor es que el número que muestra
   sea el correcto.
2. **Se tematiza igual que cualquier otro componente del design system** —
   `var(--acc)`, `var(--fg)`, etc. directamente en los atributos SVG, sin
   traducir a la API de theming de una librería de terceros.
3. **~150 líneas de zoom/tooltip escritas a mano son código que el equipo
   entiende y puede defender ante el tribunal** — el criterio explícito que
   ya usó [DECISIÓN 045](decision045.md)/[051](decision051.md) para elegir
   Canvas 2D sobre WebGL/Three.js en los fondos animados. Aplica igual acá:
   la complejidad de un framework de charting completo (Recharts) para dos
   gráficos de dispersión+curva es desproporcionada, y la traducción de
   fórmulas hidrológicas a props de una librería ajena es exactamente el
   tipo de capa opaca que este proyecto evita en `core/`.
4. **No reabre el problema que [DECISIÓN 051](decision051.md) acaba de
   cerrar** — Recharts (~100 kB gz) revertiría buena parte de la reducción
   de bundle que sacar Three.js acaba de lograr, para resolver un problema
   mucho más chico (dos gráficos XY, no un motor 3D completo).

### Alcance

Un solo componente de bajo nivel (`InteractiveChart`), parametrizado por
puntos/curva/marcadores y reusado por los dos gráficos del Bloque C
(`Etapa2AjusteChart`, `Etapa2EventosChart` en `routes/results/`) — no dos
implementaciones separadas de zoom/tooltip/teclado. Mismo patrón de reuso ya
usado por `Etapa2RankingView`/`Etapa2EventosView` entre `StreamPage`,
`ResultsPage` e `HistoryDetailPage` (Bloque B).

### Qué no incluye

El toggle calendario/hidrológico que la maqueta original ponía dentro de cada
tarjeta del ranking **no se traslada a estos gráficos** — ver
`docs/plan-etapa2-implementacion.md` §5 (C3): el criterio de año decide qué
valor cae en qué año, es una regla de agregación aguas arriba de Etapa 1
(Bloque F, todavía sin implementar), no una opción de dibujo aguas abajo de
Etapa 2. Ninguna opción de este documento lo reintroduce.

### Verificación

- `frontend/package.json` — `d3-scale` y `d3-shape` (+ `@types/d3-scale`,
  `@types/d3-shape` en devDependencies) como únicas dependencias nuevas.
- `npm run build` — aumento de bundle medido y documentado en el informe de
  cierre del Bloque C, por debajo de 15 kB gz.
- Tests de `InteractiveChart` y de los dos gráficos sobre SVG real
  (`container.querySelector`, `getByText` del tooltip), sin snapshots.

**Ver también:** [DECISIÓN 045](decision045.md) y
[DECISIÓN 051](decision051.md) — mismo criterio ("código propio y chico que
se puede defender" antes que una dependencia grande) aplicado ahora a
gráficos en vez de fondos animados.
