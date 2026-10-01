# Plan de fixes de frontend — feedback de Facundo (02/09/2026)

**Origen.** `mejoras metis.docx` — cinco observaciones sobre la UI en
funcionamiento, cada una con captura. Este documento las traduce a tareas
ejecutables con el archivo y la línea exactos, ya verificados contra el
código en `staging`.

**Advertencia de alcance — leer antes de estimar.** El pedido original era
"fixes rápidos". Tres de los cinco hallazgos lo son (F1, F2, F4: CSS y una
prop). **Los otros dos no**: F3 y F5 revierten decisiones ya documentadas y
defendidas (DECISIÓN 064 y DECISIÓN 063 respectivamente). Kevin decidió el
02/09/2026 avanzar igual con la variante pesada de ambos. Eso implica
addendum en cada decisión, no solo código — si el tribunal lee `decision063.md`
y ve una ventana flotante en la demo, la contradicción sin explicar es peor
que el defecto original.

---

## Reglas del repo que aplican acá

- Working directory: `frontend/`. Verificación: `npm run lint && npm test && npm run build`.
- Todo test que renderice una pantalla completa va bajo `<StrictMode>` vía
  `src/test/renderPage.tsx`. Sin excepción.
- Un solo mecanismo de mock de red: `vi.stubGlobal("fetch", ...)` / mock de
  `@microsoft/fetch-event-source`. MSW no vuelve (DECISIÓN 041).
- `tokens.ts` y `tokens.instrumento.css` se mantienen en paridad — `tokenParity.test.ts`
  lo verifica. Todo token nuevo va a los dos.
- Ningún cambio de acá toca el contrato de la API: los cinco hallazgos son
  de render. Si algo termina necesitando un campo nuevo del backend, parar y
  replantear — no está en este plan.
- **Antes de crear `decisionNNN.md`:** `git fetch` + `git ls-tree -r --name-only
  origin/staging -- docs/decisiones/` para ver el máximo real del remoto. El
  local está en 067; el remoto puede estar más adelante. Ya pasó una vez
  (17/08/2026, colisión en 059).
- Definition of done: correr el flujo en el navegador **después** del último
  commit, no antes.

---

## Resumen de los cinco hallazgos

| # | Observación de Facundo | Archivo principal | Esfuerzo | Toca una decisión |
|---|---|---|---|---|
| F1 | "Se corta el texto" — tabla de métodos en la tarjeta de distribución | `Etapa2RankingView.tsx` + `SpotlightCard.css` | ~45 min | No |
| F2 | "Se corta el texto en los recuadros" — mismo defecto en la grilla completa de 13 | `Etapa2RankingView.css` | incluido en F1 | No |
| F4 | Los años seleccionados arriba deberían resaltarse en el gráfico | `Etapa2EventosView.tsx` + `InteractiveChart.tsx` | ~1 h | No |
| F3 | "Las fórmulas deberían mostrarse bien y no inline" | `i18n/explicaciones.ts` + `Etapa1ResultView.tsx` | ~4 h | **Sí — addendum a DECISIÓN 064** |
| F5 | El panel de columnas debería ser movible por toda la pantalla | `useColumnPanelDock.ts` + `ConfigPage.tsx` | ~6 h | **Sí — addendum a DECISIÓN 063** |

**Orden de ejecución: F1+F2 → F4 → F3 → F5.** Los tres primeros son
independientes entre sí y no tocan decisiones; si el tiempo se corta, lo que
queda pendiente es lo que tiene que discutirse igual antes de commitear.

---

## F1 + F2 — texto cortado en las tarjetas de distribución

**Qué se ve.** Con los métodos expandidos, la última columna de la tabla
(el botón "Elegir") queda cortada al medio contra el borde derecho de la
tarjeta. En la grilla completa ("Ver las 9 distribuciones restantes") pasa
en todas las tarjetas a la vez, que es la captura de la segunda observación
— es el mismo defecto, no dos.

**Causa verificada.**

1. `frontend/src/components/SpotlightCard.css:5` — `.spotlight-card { overflow: hidden }`.
   Está ahí para recortar el glow radial del hover; de paso recorta cualquier
   hijo que se pase de ancho, **sin scroll** y sin ninguna señal visual de que
   hay contenido más allá.
2. `frontend/src/routes/results/Etapa2RankingView.css:6-10` — la grilla es
   `repeat(auto-fit, minmax(220px, 1fr))`. Con 13 distribuciones en una
   pantalla ancha, cada tarjeta cae cerca del mínimo de 220px.
3. `frontend/src/routes/results/Etapa2RankingView.tsx:156-200` — dentro de esos
   220px entra una `<table class="t">` de **cuatro** columnas (método, EEA,
   estado, botón), con `table.t td { padding: 8px 10px }`
   (`theme/components.css:551`). El ancho mínimo del contenido supera al
   contenedor y `overflow:hidden` hace el resto.

**Qué hacer.** Los tres puntos se atacan juntos; ninguno alcanza solo.

- Subir el mínimo de la grilla a `minmax(320px, 1fr)` en
  `Etapa2RankingView.css`. Con 13 tarjetas eso da 3–4 columnas en un monitor
  típico en vez de 5–6 — más legible, y es la grilla que Facundo va a mirar
  proyectada.
- **No** sacar `overflow: hidden` de `.spotlight-card`: sostiene el recorte
  del glow (F1 de la pasada pre-reunión). En su lugar, envolver la `<table>`
  en un `<div class="etapa2-metodos-scroll">` con `overflow-x: auto` y
  `max-width: 100%`, para que el desborde se resuelva dentro de la tarjeta
  con scroll propio en vez de recortarse.
- Reducir la presión de ancho de la tabla misma, que es lo que evita
  depender del scroll en el caso normal:
  - `padding: 6px 8px` en las celdas de esta tabla (override local, no tocar
    `table.t` global — lo usan Etapa 1, el historial y los descriptivos).
  - La columna "Estado" muestra hoy un `.pill` con el texto completo
    (`STATUS_LABEL`). Para `status === "ok"` el texto "ajustado" no aporta
    nada que la fila no diga ya (tiene EEA y botón); dejar el pill visible
    solo para los estados que **no** son `ok` y, para `ok`, un punto de color
    con `aria-label="ajustado"`. Esto solo saca ancho de la columna que menos
    información lleva.
  - El botón de la última columna: `.b b-sec` con `white-space: nowrap` y
    padding reducido, para que `textoAccion.porMetodo` no se parta en dos
    líneas dentro de una celda angosta.

**Criterio de aceptación.** Con 13 distribuciones expandidas al mismo tiempo
en un viewport de 1366px y en uno de 1920px, ninguna tarjeta muestra texto
cortado contra su borde. En un viewport de 360px la tabla scrollea
horizontalmente dentro de la tarjeta en vez de recortarse.

**Tests.** `Etapa2RankingView.test.tsx` existe y no asume anchos —
verificar que sigue verde. Si el cambio de la columna "Estado" saca el texto
"ajustado" del DOM, cualquier assert que lo busque por texto pasa a buscar
por `aria-label`. Revisar también `ResultsPage.test.tsx` y
`HistoryDetailPage.test.tsx`, que reusan la vista de solo lectura.

---

## F4 — resaltar en el gráfico los períodos de retorno seleccionados

**Qué pide Facundo.** "Al seleccionar los años en la parte superior de estos
gráficos debería remarcar los puntos respectivos con otro color y hacerlos
más grandes."

**Estado actual.** En `frontend/src/routes/results/Etapa2EventosView.tsx:24`
el chip seleccionado vive en un `useState` local (`seleccionado`) que **solo**
alimenta el número grande del valor de diseño (líneas 46-58). Nunca baja al
gráfico: `Etapa2EventosChart` (línea 80) recibe `eventosDiseno` y
`curvaAjuste` y nada más. En `Etapa2EventosChart.tsx` los ocho eventos se
dibujan como una única serie `kind: "points"` con `colorVar: "--acc2"`, y
`InteractiveChart.tsx:355-361` les da `r={3.5}` a todos salvo al que tiene
foco de teclado (`r={5}`). Por eso los ocho puntos se ven idénticos.

**Qué hacer.**

1. `Etapa2EventosView.tsx` — pasar `seleccionado` como prop nueva a
   `Etapa2EventosChart` (`periodoResaltado?: number | null`). Mismo estado, sin
   estado nuevo: el chip ya es la fuente de verdad.
2. `Etapa2EventosChart.tsx` — partir la serie `eventos` en dos:
   `eventos` (los no seleccionados, `--acc2`, tamaño normal) y
   `evento-resaltado` (el seleccionado, un solo punto). Es la solución
   barata y no toca la API del gráfico… **pero** deja el tamaño igual, que es
   la mitad del pedido. Preferir el punto 3.
3. `InteractiveChart.tsx` — agregar a `ChartSeries` (línea 29) dos campos
   opcionales, ambos con default que preserva el render actual:
   `pointRadius?: number` (default 3.5) y `highlight?: (p: ChartPoint) => boolean`.
   En el `<circle>` de la línea 355, el radio pasa a ser
   `highlight?.(p) ? radio * 1.9 : radio`, y el `fill` a `var(--acc3)` (o el
   token de acento que corresponda, ver abajo) cuando `highlight` da true.
   La serie de eventos declara `highlight: (p) => p.x === periodoResaltado`.
   Así el resalte queda como capacidad del gráfico y sirve igual para el
   gráfico de ajuste y para los de Etapa 1, en vez de ser un truco de una
   sola pantalla.
4. **Color.** No inventar un hex. Usar un token existente de
   `theme/tokens.ts` + `tokens.instrumento.css`; si ninguno contrasta contra
   `--acc2` en los dos temas, agregar uno **a los dos archivos** (paridad
   verificada por `tokenParity.test.ts`) y correr `contrast.test.ts`.
5. Accesibilidad: el resalte por color no puede ser el único canal — el
   tamaño mayor ya es el segundo canal, y el chip activo (`aria-pressed`) ya
   dice cuál es. Agregar además el período resaltado al `ariaLabel` del
   gráfico.

**Criterio de aceptación.** Clickear cada uno de los ocho chips mueve el
resalte al punto correcto de la curva, en tema claro y oscuro, y el resalte
sobrevive a un zoom (el punto sigue siendo el mismo dato, no una posición).

**Tests.** `Etapa2EventosChart.test.tsx` e `InteractiveChart.test.tsx` — caso
nuevo: con `periodoResaltado` puesto, exactamente un `<circle>` tiene el
radio grande. Verificar que los tests existentes de `InteractiveChart` siguen
verdes sin tocar (los campos nuevos son opcionales — si algún test rompe, el
default no está bien puesto).

---

## F3 — fórmulas de Etapa 1: KaTeX (revierte DECISIÓN 064)

**Qué se ve.** En modo paso a paso, la fórmula sustituida sale como una sola
línea de texto monoespaciado:
`r₄ = -36.662,73878 / 159.773,26103 = -0,22947`. La división es una barra,
no una fracción; los símbolos van en ASCII (`µ_R`, `σ_R`, `√`); y la
expresión simbólica, la sustitución y el resultado viven en la misma línea.

**Estado actual y la decisión que esto revierte.**
`frontend/src/i18n/explicaciones.ts:33-89` arma ocho plantillas que devuelven
`string[]`, y `Etapa1ResultView.tsx:142-150` las pinta como `<code>` apilados
(`.results-test__formula`, `Etapa1ResultView.css`). Eso es literal lo que
**DECISIÓN 064 eligió** el 18/08/2026: evaluó `katex` + `react-katex`, lo
descartó por ~70 KB gzip, y dejó escrito que alcanzaba para las ocho
fórmulas de Etapa 1 "porque son todas expresiones de una línea", con KaTeX
a reevaluar "recién si Etapa 2 lo pide".

**Decisión del 02/09/2026: traer KaTeX ahora.** Motivo: el pedido no es
estético sino docente — es un software con enfoque de enseñanza y la fórmula
es el producto, no la decoración; y Etapa 2 (Log-Pearson III, GVE) iba a
pedirlo igual, así que la deuda se paga una vez.

**Qué hacer, en este orden.**

1. **Primero el addendum, antes del código.** Addendum fechado 02/09/2026
   dentro de `docs/decisiones/decision064.md` (un addendum va en el mismo
   archivo, no en uno nuevo — ver `docs/decisiones/README.md`). Tiene que
   decir: qué evidencia nueva apareció (el feedback de Facundo del 02/09), por
   qué el criterio "código propio y chico antes que una dependencia grande"
   cede acá y no cedió en DECISIÓN 045/051/056/063, y cuál es el costo real
   medido en el bundle — **medido, no estimado**: correr `npm run build`
   antes y después y anotar los dos números.
2. `npm i katex react-katex` + `@types/react-katex` si hace falta. Pinear
   versión exacta. Verificar que la licencia (MIT) queda anotada donde el
   repo anote dependencias.
3. Importar el CSS de KaTeX una sola vez, y revisar que su tipografía no pise
   los tokens del tema "Instrumento" — KaTeX trae sus propias fuentes.
   Acotar con un selector propio si hace falta.
4. Reescribir las ocho plantillas de `explicaciones.ts` para devolver LaTeX
   en vez de texto plano. **La regla de DECISIÓN 064 no cambia y es la parte
   no negociable:** el frontend sustituye términos que `core/` ya calculó
   (`TestResult.explicacion.terminos`), nunca deriva un estadístico nuevo. La
   única aritmética cosmética permitida sigue siendo la que ya existe (el
   denominador de t de Student, línea 54-58).
5. Renderizar en bloque (`BlockMath`), no inline, y en tres partes visualmente
   separadas: expresión simbólica → sustitución numérica → resultado. Eso es
   lo que "no inline" quiere decir en el pedido.
6. Mantener el `Ec. III-1` debajo, que es la trazabilidad a la tesis de
   Facundo y no se toca.
7. **Fallback.** Si KaTeX no puede renderizar una expresión, la pantalla no
   puede quedar en blanco: `renderError` de `react-katex` devuelve el
   `<code>` de texto plano actual. Vale la pena conservar las plantillas de
   texto para eso, no borrarlas.

**Criterio de aceptación.** Las ocho pruebas de Etapa 1 (anderson,
wald_wolfowitz, helmert, t_student, cramer, mann_kendall,
kolmogorov_smirnov, chow) renderizan en modo paso a paso con fracciones,
raíces y subíndices reales, en tema claro y oscuro, y con la rama
`no_ejecutada` (sin `explicacion`) intacta.

**Tests.** `i18n/explicaciones.test.ts` asserta con `toContain` sobre las
cadenas — al pasar a LaTeX varios asserts van a romper (`"Z = (R − µ_R) / σ_R"`
pasa a ser `\frac{...}`). Actualizar los asserts a la cadena LaTeX real, no
relajarlos a `toBeTruthy()`: el test está verificando que el número
sustituido sea el correcto, y eso se tiene que seguir verificando.
`Etapa1ResultView.test.tsx` puede necesitar un mock de `react-katex` si
jsdom se queja; si el mock termina siendo tan grande que el test ya no
prueba nada, es mejor testear `formatearFormula` (que devuelve strings) y
dejar el render de KaTeX fuera del assert.

---

## F5 — panel de columnas flotante (revierte DECISIÓN 063)

**Qué pide Facundo.** Dos cosas distintas, y conviene no mezclarlas:
(a) que el recuadro sea movible por toda la pantalla "similar a una pestaña
en el escritorio de una computadora", y (b) que **no aparezca tan lejos** del
recuadro inicial.

**(b) es el fix de 30 minutos y va primero, sin importar qué pase con (a).**
En `ConfigPage.css:41-45`, con `data-dock="right"` el grid es
`1fr 10px var(--column-panel-width, 420px)`, y `.config-card` tiene
`margin: 0 auto` (línea 26) dentro de la columna `main` con
`max-width: 560px` (línea 127). En un monitor ancho el formulario se centra
en su columna y el panel queda pegado al borde derecho: el hueco de la
captura. Alinear la tarjeta contra el divisor (`justify-self: end` con
`data-dock="right"`, `justify-self: start` con `"left"`) y el hueco
desaparece sin tocar ninguna decisión. **Hacer esto y verlo en pantalla antes
de escribir una línea de (a)** — es posible que resuelva la molestia real.

**(a) es lo que DECISIÓN 063 descartó explícitamente**, el 18/08/2026, y no
por desprolijidad: el archivo enumera lo que una ventana flotante de verdad
obliga a construir — z-index, límites de arrastre contra el viewport, qué
pasa si se arrastra fuera de la pantalla, foco al traer al frente, y el costo
real, **accesibilidad por teclado de todo eso desde cero**. El dock actual
reduce ese problema a una dimensión con `role="separator"` ya estandarizado
(`ConfigPage.tsx:693-698`). También hay un argumento que sigue siendo cierto
y que Facundo quizás no tuvo en cuenta: el pedido original de Bloque E
incluía que **el recuadro principal se reacomode**, y una ventana flotante
superpone, no reacomoda.

**Decisión del 02/09/2026: implementar el flotante igual.** Entonces, en este
orden:

1. **Addendum a `docs/decisiones/decision063.md`, fechado 02/09/2026, escrito
   antes del código.** Tiene que responder las tres preguntas que el tribunal
   va a hacer: (i) qué cambió respecto del 18/08 para revertir el criterio;
   (ii) cómo se cubre la accesibilidad por teclado que la decisión original
   dio como motivo principal; (iii) qué pasa con el reacomodo del recuadro
   principal, que era parte del pedido que originó el dock. Si (iii) no tiene
   respuesta, el flotante **no** reemplaza al dock: convive con él.
2. **Recomendación fuerte: flotante como cuarto modo, no como reemplazo.**
   `PanelDock` en `useColumnPanelDock.ts:6` pasa a
   `"right" | "left" | "bottom" | "floating"`, y el selector del header del
   panel gana un cuarto botón. Con eso el addendum de (iii) se escribe solo
   ("quien quiera reflow tiene los tres docks; quien quiera superponer tiene
   el flotante"), los tests de dock existentes siguen valiendo, y la
   migración de `localStorage` es aditiva.
3. Estado nuevo en `useColumnPanelDock.ts`: `floatingPos: { x, y }` persistido
   junto al resto en `metis-column-panel`. `readInitialState` tiene que
   tolerar el JSON viejo sin ese campo (ya tiene el patrón de validación por
   campo, seguirlo). Posición inicial **cerca del recuadro de configuración**,
   no en una esquina — es literal la segunda mitad del pedido de Facundo.
4. Arrastre por la barra de título del panel, con el mismo patrón de
   rendimiento que ya usa el redimensionado (DECISIÓN 063, "detalle de
   implementación no obvio"): `pointermove` escribe a custom properties CSS
   vía `ref`, y `setState` + `localStorage` recién en `pointerup`. Con
   `setState` por píxel se re-renderiza `ConfigPage` entera en cada
   movimiento.
5. **Clamp contra el viewport, y contra el viewport actual.** No alcanza con
   limitar al soltar: hay que reclampear en `resize`, o el panel queda fuera
   de pantalla e irrecuperable cuando alguien achica la ventana o cambia de
   monitor. Dejar siempre visible al menos la barra de título.
6. **Teclado — esto es lo que hace o rompe el addendum.** La barra de título
   arrastrable tiene que ser un elemento enfocable con rol y `aria-label`
   explícitos, mover con flechas en pasos de `RESIZE_KEYBOARD_STEP`, y
   anunciar la posición. Si esto no entra en el tiempo disponible, **no
   mergear el flotante**: dejarlo en la rama y quedarse con (b), porque un
   panel que solo se mueve con mouse es exactamente el costo que DECISIÓN 063
   se negó a pagar, y no tener respuesta para eso ante el tribunal es peor
   que el hueco de la captura.
7. Z-index desde los tokens, no un `9999` suelto.

**Criterio de aceptación.** El panel se arrastra desde su barra de título,
queda donde se lo suelta, sobrevive a un F5 y a un cambio de tamaño de
ventana, se mueve con teclado, y los tres docks existentes siguen
funcionando igual que hoy.

**Tests.** `ConfigPage.test.tsx:466-570` cubre dock, cierre/reapertura,
persistencia en `localStorage` y el divisor por teclado — todos tienen que
seguir verdes sin editarlos (si hay que editarlos, el flotante está
reemplazando al dock en vez de sumarse). Tests nuevos: persistencia de
`floatingPos`, clamp contra viewport, y movimiento por teclado.

**Cerrado 15/09/2026 — se descarta (a), se queda (b).** Se implementó el
flotante completo (cuarto modo, arrastre con mouse y teclado, clamp contra
el viewport, y una segunda vuelta que agregó colisión contra la card para
que no quedara obligado a vivir siempre debajo de ella) y se probó en uso
real. La hitbox de colisión contra la card resultó demasiado grande —se
extendía más allá de su forma visual hacia abajo— y el resultado no sumaba
lo suficiente como para justificar seguir puliéndolo. Exactamente el riesgo
que anticipaba el punto 6 de arriba, aunque el motivo real terminó siendo
otro: no la accesibilidad por teclado (esa sí quedó resuelta), sino la UX
de la colisión en sí. Revertido por completo —
`useColumnPanelDock.ts`, `ConfigPage.tsx`, `ColumnPreviewPanel.tsx/css` y
`tokens.instrumento.css` vuelven a su estado previo a este plan, sin
ningún rastro de `"floating"` en el código ni en los tests.

**`decision063.md` no lleva addendum.** El flotante nunca llegó a
commitearse, así que la decisión original ("Panel de columnas acoplado, no
ventana flotante") sigue siendo exactamente lo que el código hace — no hay
ninguna contradicción que explicarle al tribunal, el riesgo que la
"Advertencia de alcance" del encabezado de este documento marcaba de
entrada. Se mergea solo (b): la card se alinea contra el divisor
(`justify-self`) en los docks derecha/izquierda.

---

## Verificación final

1. `cd frontend && npm run lint && npm test && npm run build` — los cuatro
   jobs de CI (`lint`, `test`, `error-catalog`, `frontend`) tienen que pasar;
   sin los cuatro no se mergea.
2. `npx tsc -b` limpio.
3. Anotar el tamaño del bundle antes y después de KaTeX y volcarlo al
   addendum de DECISIÓN 064.
4. **Correr el flujo completo en el navegador después del último commit**:
   subir una serie, llegar al ranking de Etapa 2 con las 13 distribuciones
   expandidas (F1/F2), elegir un ajuste, clickear los ocho chips de período
   de retorno (F4), volver a Etapa 1 en modo paso a paso y leer las ocho
   fórmulas (F3), y mover el panel de columnas en `ConfigPage` (F5) — en tema
   claro y oscuro.
5. Los dos addendums (`decision063.md`, `decision064.md`) commiteados **en el
   mismo PR** que el código que los aplica, no después.
