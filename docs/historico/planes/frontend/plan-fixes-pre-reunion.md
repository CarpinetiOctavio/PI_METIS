# Plan de fixes de frontend — pre-reunión (14/08/2026)

**Contexto para quien ejecute esto:** son los últimos arreglos antes de una
reunión de avance. El objetivo NO es dejar el frontend perfecto: es que la
demo se vea sólida y que ningún defecto cosmético distraiga de lo que
realmente importa mostrar. Hay siete hallazgos y una mañana. El orden de
abajo está pensado para que, si el tiempo se corta, lo que quede sin hacer
sea lo que menos se nota en pantalla.

## Reglas del repo que aplican acá

- Working directory: `frontend/`. Verificación: `npm run lint && npm test && npm run build`.
- Todo test que renderice una pantalla completa va bajo `<StrictMode>` vía
  `src/test/renderPage.tsx`. No hay excepción por archivo.
- Un solo mecanismo de mock de red: `vi.stubGlobal("fetch", ...)`. MSW no
  vuelve al proyecto.
- Todo código de error nuevo se agrega a `api-contracts.md` y a
  `i18n/errors.es.ts` **en el mismo commit** — el job `error-catalog` de CI
  lo verifica en las tres direcciones.
- Si un cambio toca el contrato de la API, se actualiza `api-contracts.md`
  en el mismo commit.
- Definition of done: correr el flujo en el navegador **después del último
  commit**, no antes.

## Antes de tocar nada: dos verificaciones de 5 minutos

Dos de los siete hallazgos pueden no ser bugs. Verificarlos primero evita
gastar la mañana arreglando algo que funciona.

### V1 — ¿El historial realmente pierde la Etapa 2?

El código dice que no debería. `_persistir()` (`services/analysis_service.py`,
~línea 685) se llama **después** de resolver la pausa de distribución y
recibe `etapa2_result`. `HistoryDetailPage` renderiza `detail.etapa2` si
existe. Y en las capturas del hallazgo, el análisis se corrió con
**"Solo validación (Etapa 1)"** seleccionado en `ConfigPage`, así que
"Etapas: 1" sería el valor correcto.

Correr esto antes de asumir un bug:

1. `ConfigPage` → alcance **"Validación + análisis de frecuencia (Etapa 1 y 2)"**, con sesión iniciada (CU-01).
2. Llegar al ranking, **elegir una distribución** y dejar que el stream termine en `complete`.
3. Ir al historial: el item debe decir `Etapas: 1, 2`.
4. Abrir el detalle: debe aparecer el bloque de Etapa 2.

**Si eso funciona**, el hallazgo real es otro y más específico: qué pasa si
el usuario **abandona** la pausa sin elegir distribución. En ese caso el
stream nunca llega a `_persistir()` y **no se guarda nada** — ni siquiera la
Etapa 1 que sí se calculó. Eso sí es un defecto real y vale arreglarlo
(persistir Etapa 1 antes de la pausa, o al timeout de sesión). Anotarlo en
`docs/pendientes-tecnicos.md` si no hay tiempo.

### V2 — ¿Los warnings de Etapa 2 indican algo roto?

**No, y el motivo no es el que parece a primera vista.**

`core/etapa2/eea.py::es_high_eea()` emite `DIST_HIGH_EEA` cuando
`EEA > 0.05 * |media|`. Con una serie de media ≈ 110, el umbral queda en
**5,5** — y el mejor ajuste de toda la grilla (`gve/ml`) tiene EEA 7,66. O
sea: **ninguna** combinación baja del umbral, ni siquiera la ganadora. De ahí
los ~25 banners.

Esto no depende de que la serie tenga un atípico. El umbral del 5% de la
media es equivalente a exigir un error relativo menor al 5%, que para una
serie hidrológica real es exigente: el mejor ajuste de esta corrida tiene
**7 % de error relativo**, que es un ajuste perfectamente razonable, y aun
así dispara el mismo warning que `exponencial_beta` con **83 %**, que es
inservible.

Dato verificable de que los números son consistentes y no hay bug de datos:
`uniforme/momentos EEA=9.7648` aparece idéntico en la lista de warnings y en
la card del ranking (`9,76482`). Ranking y warnings salen del mismo cálculo.

**Dos conclusiones, y las dos importan:**

1. **Para esta mañana:** el fix es de presentación, no de cálculo (F4). Pero
   agrupar no alcanza — hay que hacer visible la magnitud, porque hoy un
   ajuste al 7 % y uno al 83 % se ven exactamente igual.
2. **Para la reunión:** el umbral del 5 % es una **decisión de diseño de
   METIS, no viene de la tesis** — está dicho así, textual, en el docstring
   de `es_high_eea()`. Si dispara para el 100 % de las combinaciones en una
   serie normal, el warning deja de discriminar y pierde su función. Vale
   llevarlo como pregunta concreta a Facundo: *¿el 5 % es el criterio
   correcto, o debería ser relativo al mejor ajuste de la grilla?* Es
   exactamente el tipo de pregunta que conviene hacer antes de que la haga
   el tribunal. **No cambiar el umbral por cuenta propia**: es regla de
   negocio y está documentada.

---

## Bloque A — cosméticos (30 min, riesgo cero)

Hacer estos primero: son los que más mejoran la percepción por minuto
invertido y no pueden romper nada.

### F1 — El brillo que sigue al mouse es demasiado fuerte

**Archivo:** `src/components/SpotlightCard.css`

Hoy: `opacity: 0.55` en hover, con `white 12%` en el centro del gradiente.
Se lee como una linterna; el pedido es "mínimo, casi transparente".

Cambios:

- `.spotlight-card:hover .spotlight-card__glow` → `opacity: 0.22`.
- En el `radial-gradient`, bajar la mezcla del centro de `white 12%` a
  `white 6%`, y el segundo stop de `var(--acc) 8%` a `var(--acc) 4%`.

**Verificar en los dos temas.** El tema claro es donde más se nota: en la
captura del historial en claro, la mancha azulada sobre la card blanca es
más visible que el propio contenido. Si en claro sigue molestando con 0.22,
bajar a 0.15 solo para claro con una regla bajo el selector de tema — pero
probar primero el valor único, que es más simple de defender.

### F2 — El número del eje Y se corta cuando es grande

**Archivos:** `src/charts/InteractiveChart.tsx`, `src/i18n/format.ts`

Dos causas, las dos hay que tocar:

1. **Margen insuficiente.** `MARGIN.left = 60` (línea ~49). Con una etiqueta
   como `1.000,00000` no alcanza y se corta el primer dígito. Subir a `88`.
   Verificar que `plotWidth` se recalcula solo (lo hace: `VIEW_W - MARGIN.left - MARGIN.right`).

2. **Los ticks del eje no deberían tener 5 decimales.** `formatNum()` fuerza
   5 decimales fijos, que es correcto para las tablas de resultados (la
   tesis imprime así y el docente compara a mano) pero absurdo en un eje:
   `800,00000` ocupa el triple de ancho del que necesita. Agregar a
   `format.ts` un formateador aparte:

   ```ts
   // Ejes de gráficos: los 5 decimales de formatNum() son para tablas de
   // resultados, donde el docente compara contra la tesis. En un eje solo
   // roban ancho y obligan a un margen enorme.
   const axisFormatter = new Intl.NumberFormat("es-AR", {
     maximumFractionDigits: 2,
   });
   export function formatAxis(value: number): string {
     return axisFormatter.format(value);
   }
   ```

   Y usarlo en las etiquetas de tick de `InteractiveChart` y `BoxPlot`.
   **No tocar `formatNum`** — lo usan las tablas de Etapa 1 y ahí los 5
   decimales son deliberados y están documentados.

Con las dos cosas juntas, `MARGIN.left = 72` probablemente alcance. Ajustar
mirando el resultado real con la serie del atípico, que es el peor caso.

---

## Bloque B — Etapa 2: lo que más se ve en la demo (2 h)

### F3 — Trece cards de distribución ocupan toda la pantalla

**Archivo:** `src/routes/results/Etapa2RankingView.tsx`

Hoy `Etapa2RankingView` mapea `etapa2.ranking` completo a una grilla de 13
cards visualmente idénticas. El backend ya las devuelve ordenadas
ascendente por `mejor_eea` (nulls al final) — **el frontend no reordena**,
esa regla se mantiene.

Cambio: mostrar las primeras **4** y esconder el resto detrás de un botón.

```tsx
const TOP_VISIBLE = 4;
const [verTodas, setVerTodas] = useState(false);
const visibles = verTodas ? etapa2.ranking : etapa2.ranking.slice(0, TOP_VISIBLE);
const ocultas = etapa2.ranking.length - TOP_VISIBLE;
```

Y bajo la grilla, si `!verTodas && ocultas > 0`:

> `Ver las {ocultas} distribuciones restantes`

Al expandir, el botón pasa a `Ver solo las {TOP_VISIBLE} mejores`.

**Detalle que importa para el tribunal:** el texto del botón no debe sugerir
que las ocultas son peores *como modelo* — solo tienen mayor EEA. Mantener
la frase ya existente arriba de la grilla ("METIS ordena por EEA; la
distribución la elegís vos") visible **siempre**, también con la grilla
colapsada.

### F4 — Los warnings de Etapa 2 inundan la pantalla

**Archivo:** `src/routes/results/Etapa2RankingView.tsx` (~línea 126)

Hoy: un banner por warning, ~25 banners apilados antes de llegar al ranking.

Cambio: agrupar por `codigo`. Si un código aparece más de 3 veces, colapsar
en un solo banner con el conteo y un `<details>` para el detalle:

> ▲ **25 combinaciones superan el 5% de la media (EEA alto).** El ajuste es
> válido pero de bajo valor práctico para esta serie. — *Ver detalle*

Dentro del `<details>`, la lista de las 25 descripciones tal como vienen hoy.

**Además, hacer visible la magnitud (ver V2).** Agrupar sin esto solo esconde
el problema: hoy el mejor ajuste (7 % de error relativo, perfectamente usable)
y el peor (83 %, inservible) producen banners idénticos. En la tabla de
métodos de cada card, junto al EEA, agregar el **EEA como porcentaje de la
media** — `EEA 7,65775 (7,0 %)`. La media de la serie ya está disponible en el
resultado de Etapa 1 (`datos` de `result_etapa1`, bloque de estadística
descriptiva); si llegar a ella desde el componente resulta engorroso, dejarlo
anotado y no forzarlo hoy.

Reglas al implementar:

- Agrupar **solo** los de `nivel === "normal"`. Un warning crítico nunca se
  colapsa: se muestra entero y arriba de todo. Esa jerarquía es regla de
  negocio (`RF-GEN-P-03`), no preferencia visual.
- El umbral de agrupación (3) va como constante nombrada, no como número
  suelto.
- No inventar texto que el backend no manda: el resumen es del frontend,
  pero la descripción de cada warning se sigue mostrando textual dentro del
  detalle.
- **No tocar el umbral del 5 %** en `es_high_eea()`. Es regla de negocio y su
  revisión es una consulta a Facundo, no un fix de frontend.

### F5 — El botón "Elegir" no se encuentra

**Archivo:** `src/routes/results/Etapa2RankingView.tsx`

El botón **existe** (línea ~82) pero vive dentro de la tabla de métodos, que
está colapsada detrás de "Ver los N métodos". El usuario que mira la grilla
no ve ninguna acción y concluye que no se puede elegir. Es un problema de
descubribilidad, no una funcionalidad faltante.

Cambio mínimo: agregar en la card, junto a "Mejor ajuste: {método} · EEA
{valor}", un botón primario **"Elegir este ajuste"** que llame a
`onElegir(item.distribucion, item.mejor_metodo)` directo. Los botones por
método dentro de la tabla se quedan como están, para quien quiera un método
distinto del mejor.

Condiciones: solo si `onElegir` está presente (modo interactivo) y
`item.mejor_metodo` no es null. En modo solo lectura (`ResultsPage`,
`HistoryDetailPage`) no aparece nada, igual que hoy.

---

## Bloque C — selector de períodos de retorno (1 h)

### F6 — No se pueden elegir los años

**Archivos:** `src/routes/stream/StreamPage.tsx` (~línea 231),
`src/routes/results/Etapa2RankingView.tsx`

Hoy `StreamPage` manda siempre `PERIODOS_RETORNO_DEFAULT` — fue una
simplificación deliberada del bloque que implementó Etapa 2, no un olvido.

Cambio: un campo en la vista de ranking, encima del botón de elegir, con los
períodos separados por coma y valor inicial igual al default actual.

Validar **en el cliente antes de mandar**, con los mismos límites que ya
aplica el backend (`DIST_SELECTION_INVALID`): entre 1 y 20 valores, todos
numéricos y **estrictamente mayores que 1** (`F = 1 - 1/T` necesita `T > 1`).
Mostrar el error inline; no dejar que el 400 llegue como banner genérico.

**No agregar un código de error nuevo.** Si la validación del cliente falla,
es un mensaje de formulario, no un código de catálogo — y así no hay que
tocar `api-contracts.md` ni el job `error-catalog`.

---

## Bloque D — historial (2 h, toca backend)

Este es el bloque más caro y el único que cruza al backend. Si el tiempo se
corta, **es el que se recorta** — el historial no es el centro de la demo.

### F7a — El título es el tipo de variable, no el archivo

**Archivos:** `services/analysis_service.py`, `api/v1/history.py`,
`src/routes/history/HistoryPage.tsx`, `api-contracts.md`

Hoy la lista muestra `item.tipo_variable`, así que todos los análisis se
llaman `caudal_precipitacion` y son indistinguibles.

`analyses` **no tiene** columna para el nombre del archivo. Dos caminos:

- **Recomendado (sin migración):** guardarlo dentro de `configuracion`
  (JSONB, ya existe) como `nombre_archivo`. `_persistir()` ya recibe todo lo
  necesario; `filename` está disponible en `stream_analysis()` (se usa en
  `parse_file`). Hay que pasarlo hasta `_persistir()` y exponerlo en el item
  de `GET /history/`.
- **Con migración:** columna `nombre_archivo` en `analyses` (migración 006).
  Más limpio a largo plazo, más caro hoy. **No hacerlo esta mañana.**

Frontend: título = nombre de archivo, y el tipo de variable baja a la línea
de metadatos junto a modo y etapas. Para análisis viejos sin
`nombre_archivo`, degradar explícitamente al comportamiento actual (mostrar
el tipo de variable) — mismo criterio que ya se usa con `timestamps === null`
en `HistoryDetailPage`. **Sin backfill.**

Actualizar `api-contracts.md` (sección `GET /api/v1/history/`) en el mismo
commit.

### F7b — Miniatura de la serie en cada item

Depende de F7a. La lista **no** devuelve la serie hoy.

Camino barato: agregar `serie_preview` al item de la lista — la serie
completa ya vive en `analyses.serie` y son ~40 valores por análisis, así que
el payload no cambia de orden de magnitud. Con eso, una sparkline SVG de
~120×32 px en cada fila, sin ejes ni interacción, reusando las escalas de
`d3-scale` que ya están en el proyecto.

**No usar `InteractiveChart` para esto.** Es un componente con zoom, tooltip
y navegación por teclado; una sparkline decorativa no necesita nada de eso y
montar 20 instancias en una lista es caro. Componente nuevo y chico.

Si F7a se complica, **saltear F7b entero**: es lo más prescindible de los
siete hallazgos.

---

## Orden de ejecución sugerido

| # | Fix | Costo | Riesgo | Se nota en demo |
|---|-----|-------|--------|-----------------|
| V1, V2 | Verificaciones previas | 5 min | — | — |
| F1 | Brillo del spotlight | 10 min | Nulo | Sí, en todas las pantallas |
| F2 | Eje Y cortado | 20 min | Bajo | Sí, en los 5 gráficos |
| F3 | Top 4 + Ver más | 45 min | Bajo | Mucho |
| F4 | Agrupar warnings | 45 min | Bajo | Mucho |
| F5 | Botón Elegir visible | 20 min | Bajo | Sí |
| F6 | Períodos de retorno | 1 h | Medio | Solo si lo preguntan |
| F7a | Nombre de archivo | 1,5 h | Medio (toca backend) | Poco |
| F7b | Sparkline | 1 h | Medio | Poco |

**Corte recomendado:** si a las 11 no está cerrado hasta F5, saltar F6 y F7 y
usar el tiempo restante en verificar la demo end-to-end. Un flujo que corre
limpio vale más en la reunión que dos features a medio terminar.

## Agrupación en PRs — máximo 4

Los siete fixes entran en **cuatro PRs y ni uno más**. El criterio no es
estético: tres de los fixes tocan el mismo archivo, y abrir un PR por fix
garantizaría conflictos entre ramas propias y triplicaría la revisión del
mismo diff. Todos salen de `staging` y vuelven a `staging`, como siempre.

### PR 1 — `fix/frontend-cosmeticos-pre-reunion`

**Contiene:** F1 (brillo del spotlight) + F2 (eje Y cortado).

Solo CSS y capa de gráficos. Ninguna lógica de negocio, ningún contrato.
Es el PR que se mergea primero y sin discusión: si algo del resto se cae,
esto ya está adentro y es lo que más se nota en pantalla por línea cambiada.

**Tests:** el de paridad de tokens y los de `InteractiveChart` ya existentes
tienen que seguir en verde. Sumar uno que fije el formateador de eje nuevo
(`formatAxis(1000)` → `"1.000"`, sin decimales de relleno).

### PR 2 — `fix/etapa2-densidad-visual`

**Contiene:** F3 (top 4 + ver más) + F4 (agrupar warnings + % de la media) +
F5 (botón "Elegir este ajuste").

Los tres tocan `Etapa2RankingView.tsx`. Separarlos sería pelearse con uno
mismo por el mismo archivo tres veces. Van juntos y el PR se titula por el
efecto, no por los tres fixes: la densidad visual de la pantalla de Etapa 2.

**Tests:** tres, uno por fix. Que con 13 distribuciones se rendericen 4 cards
y el botón de expandir; que 25 warnings del mismo código produzcan un solo
banner con el conteo; que el botón "Elegir este ajuste" llame a `onElegir`
con el `mejor_metodo` y no aparezca cuando `onElegir` es `undefined`.

### PR 3 — `feature/periodos-retorno-configurables`

**Contiene:** F6.

**Se apila sobre PR 2** — toca el mismo componente, así que sale de la rama
de PR 2 y se retargetea a `staging` cuando esa mergee. Es el patrón que ya
se usó en las pasadas 4 y 5.

**Tests:** validación del cliente (más de 20 valores, un valor ≤ 1, campo
vacío) y que el valor editado llegue efectivamente a `resolveDistribution`
en lugar del default.

### PR 4 — `feature/historial-nombre-archivo`

**Contiene:** F7a (nombre de archivo) + F7b (sparkline), si F7b llega.

Es el único que cruza a backend, y por eso va solo: si rompe algo, rompe en
los jobs `test` o `error-catalog`, y conviene que eso no arrastre a los otros
tres PRs. Independiente de PR 1-3, se puede abrir en paralelo.

**No lleva migración.** El nombre de archivo va dentro de `configuracion`
(JSONB, ya existe). Si alguien propone la columna nueva, es para después de
la reunión.

**Obligatorio en este PR:** actualizar `api-contracts.md`, sección
`GET /api/v1/history/`, en el mismo commit que cambia la respuesta. Es regla
del repo y el tribunal ya tiene el documento.

**Tests:** que un análisis persistido guarde y devuelva el nombre de archivo,
y que la lista degrade al tipo de variable cuando el campo no está (análisis
anteriores a este cambio).

### Si el corte de las 11 aplica

Con **PR 1 y PR 2 mergeados ya está el grueso del valor visual**: el brillo,
los ejes, y toda la pantalla de Etapa 2. PR 3 y PR 4 son mejoras que se
notan si alguien las busca. Cerrar dos PRs limpios y verificados es mejor
resultado que dejar cuatro ramas abiertas a mitad de camino.

## Verificación final (no saltear)

```bash
cd frontend
npm run lint && npm test && npm run build
```

Y después del último commit, con `docker-compose up -d` levantado, correr el
flujo completo en el navegador: carga → Etapa 1 → decisión de atípico →
ranking de Etapa 2 → elegir distribución → eventos de diseño → historial.
Los dos temas, claro y oscuro.

Si algo de esto se cae, es preferible revertir el fix que llegar a la
reunión con la aplicación rota — ya pasó una vez en este proyecto que dos
PRs entraron con CI en verde y la app no andaba (ver
`informe-diagnostico-ui-rota.md`), y la causa fue exactamente saltearse este
paso.
