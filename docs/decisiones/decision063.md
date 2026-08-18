# DECISIÓN 063 — Panel de columnas acoplado, no ventana flotante

**Fecha:** 18 de Agosto de 2026
**Estado:** Decidida y aplicada (Bloque E del [plan post-avance](../plan-post-avance.md))

### Contexto

`plan-post-avance.md` había anticipado este número como 062 para este mismo
tema; [DECISIÓN 062](decision062.md) explica por qué ese número ya estaba
tomado por otro frente (auditoría de dominio de Octavio, DECISIÓN 060/061) y
por qué el historial interactivo pasó a 062 en su lugar — este documento usa
el siguiente número real disponible, 063.

`ColumnPreviewPanel` (pasada 5) aparece cuando la previsualización de
columnas está lista y desaparece con el archivo. No se puede mover, ni
redimensionar, ni cerrar — el pedido explícito era agregar las tres cosas,
más "que se acomode también el recuadro principal".

### La pregunta que resuelve esta decisión

¿El panel se implementa como ventana flotante (superpuesta) o como panel
acoplado (dock, que reacomoda el layout)?

### Decisión

**Panel acoplado.** Una ventana flotante superpone el contenido — nunca
reacomoda nada de lo que hay debajo. El pedido incluía explícitamente que el
recuadro principal también se reacomode, y eso es exactamente lo que un
dock hace y una ventana flotante no.

El acople es configurable — derecha (default), izquierda o abajo — vía un
selector compacto en la barra de título del panel. `ConfigPage.tsx` resuelve
las tres posiciones con `grid-template-areas` distintas en `.config-shell`,
seleccionadas por el atributo `data-dock` (ver `ConfigPage.css`), sobre un
grid de tres áreas: `main`, `divider` (el borde arrastrable) y `panel`.

### Por qué no un gestor de ventanas propio

Una ventana flotante movible/redimensionable de verdad implica reconstruir,
aunque sea en miniatura, la superficie de un gestor de ventanas: z-index,
límites de arrastre contra el viewport, qué pasa si se arrastra fuera de la
pantalla, foco al traer al frente, y — el costo real — accesibilidad por
teclado de todo eso desde cero (mover con teclado, no solo con mouse; anunciar
posición a un lector de pantalla). Un panel acoplado con un divisor
`role="separator"` reduce ese problema a una sola dimensión (ancho o alto),
con la semántica ARIA de separador ya estandarizada y bien soportada — mismo
criterio de "código propio y chico, defendible ante el tribunal, antes que
una superficie grande" que ya aplicaron DECISIÓN 045/051/056 para los fondos
animados y los gráficos interactivos.

### Detalle de implementación no obvio

El redimensionado por arrastre (`pointerdown`+`pointermove`) escribe el
ancho/alto directo a una custom property CSS (`--column-panel-width` /
`--column-panel-height`) vía una `ref` al contenedor, no a través de
`useState` en cada `pointermove` — con `setState` por píxel arrastrado,
cada movimiento de mouse re-renderiza `ConfigPage` entera (sus dos
`<select>` de columnas, el dropzone, los tres `<fieldset>`). El estado de
React (y la escritura a `localStorage`) recién se actualiza una vez, al
soltar (`pointerup`/`pointercancel`) — `useColumnPanelDock.ts`.

El divisor es utilizable sin mouse: `role="separator"`, `aria-orientation`
(`"vertical"` para derecha/izquierda, `"horizontal"` para abajo — describe
la orientación de la línea divisoria, no del movimiento que habilita),
`aria-valuenow`/`aria-valuemin`/`aria-valuemax`, y responde a las flechas
del teclado (`ArrowLeft`/`ArrowRight` para derecha/izquierda,
`ArrowUp`/`ArrowDown` para abajo) en pasos de 16px. Sin esto el panel
quedaría inutilizable sin mouse.

Posición de acople, ancho/alto (uno por posición, no un valor único
compartido) y abierto/cerrado se persisten en `localStorage`
(`metis-column-panel`), mismo patrón de lectura-una-vez-al-montar que
`MotionProvider.tsx` (DECISIÓN 059) — sin Context, porque `ConfigPage` es el
único consumidor.

### Verificación

`npx tsc -b`, `npm run lint`, `npm test` (284 tests, +5 sobre la línea base
de PR6 recién mergeado a `staging`: cerrar/reabrir sin perder la
previsualización, cada posición de acople marca el botón activo y actualiza
`data-dock`, persistencia en `localStorage` tras cerrar/mover, el divisor
responde a las flechas y actualiza `aria-valuenow`, ausencia de
divisor/panel sin previsualización lista), `npm run build` — todos en
verde. Verificado en el navegador de dev
contra el backend real (Docker): las tres posiciones de acople cambian el
grid en vivo (confirmado por `grid-template-areas`/`grid-template-columns`
computados), el divisor por teclado modifica `aria-valuenow` y la custom
property CSS en los pasos esperados (260→276→244 con
`ArrowUp`×1/`ArrowDown`×2), cerrar+recargar la página mantiene el panel
cerrado con la posición y el tamaño guardados, "Ver columnas" lo reabre
exactamente donde quedó.

**Ver también:** [DECISIÓN 059](decision059.md) — mismo patrón de
persistencia en `localStorage` sin Context, para el nivel de animación.
