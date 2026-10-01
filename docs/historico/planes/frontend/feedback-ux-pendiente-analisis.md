# Feedback de UX/Diseño — Pendiente de Análisis (no implementar todavía)

**Fecha.** 31 de Julio de 2026.
**Origen.** Observaciones de Kevin probando `fix/frontend-ui-integracion` en vivo (stack completo
vía Docker/nginx, ver [`informe-resultados-arreglo-ui-rota.md`](./informe-resultados-arreglo-ui-rota.md)),
después de que el flujo funcional quedara arreglado.
**Estado — importante.** Este documento **no es un plan ni una decisión**. Es un relevamiento de
puntos a analizar antes de decidir qué hacer con cada uno — ninguno de los ítems de abajo se
implementa a partir de este archivo solo. Cuando se decida avanzar con alguno, corresponde:
(a) una entrada en `docs/decisiones/` si cambia comportamiento o contrato, o (b) promoverlo a un
plan tipo `plan-mejora-frontend-pasadaN.md` si es una pasada de trabajo concreta — siguiendo el
mismo criterio de esta carpeta.

---

## 1. Identidad visual y diseño general

**Observación.** El frontend implementado se parece a los wireframes y al tema "Instrumento"
(`frontend/frontend-design/`, `frontend/src/theme/`), pero diverge de ellos en varios puntos — no
es una reproducción fiel. Además el resultado se percibe muy simple: sin animaciones, sin
transiciones ni micro-interacciones ante acciones del usuario (clicks, cambios de estado, cargas).
La barra superior (`TopBar.tsx`) en particular — que ahora concentra la navegación real entre
pantallas desde el Bloque 2.1 de la pasada de arreglo — se ve poco cuidada visualmente.

**Estado actual del código.** `TopBar.tsx` es intencionalmente minimal: un `<header>` con estilos
inline (`style={{...}}`), sin animación de ningún tipo. `theme/components.css`/`tokens.instrumento.css`
definen la paleta y tipografía del tema "Instrumento" pero no incluyen transiciones ni estados de
hover/focus más allá de lo que da el navegador por defecto (ver `.step`, `.pill`, `.b` en
`components.css`). Ninguna pantalla usa animación de entrada/salida ni transición de estado.

**Para analizar antes de decidir:**
- ¿Divergencia del wireframe es deriva no intencional (implementación que se apartó sin que nadie
  lo notara) o son ajustes deliberados de fases anteriores que nunca se reconciliaron con el
  diseño original? Comparar pantalla por pantalla contra
  `frontend/frontend-design/metis-prototipo-fase3.html` (o el archivo de prototipo vigente) antes
  de decidir si se corrige hacia el original o se actualiza el original.
- ¿Cuánto esfuerzo de animación/interacción se justifica para V1.0, dado que no es un requisito
  funcional (`RF-XXX`) sino una mejora de percepción? Definir alcance antes de tocar código —
  "agregar animaciones" sin acotar es la clase de tarea que se expande indefinidamente.
- `TopBar` específicamente: ¿rediseño visual acotado a esa barra, o se resuelve como parte de una
  pasada más amplia de pulido que también toque el resto de las pantallas?

---

## 2. ConfigPage — selección de columnas por dropdown, no texto libre

**Observación.** Los campos "Columna X" y "Columna Y" son inputs de texto libre donde el usuario
tiene que escribir a mano el nombre exacto de la columna del Excel/CSV. Debería: (a) autocompletarse
después de analizar el archivo cargado (detectar las columnas reales), y (b) ser un dropdown que
permita elegir cuál columna del archivo corresponde a cuál campo que METIS necesita, en vez de
depender de que el usuario tipee el nombre correcto sin errores.

**Estado actual del código.** `ConfigPage.tsx` — `columnaX`/`columnaY` son `useState<string>`
atados a `<input type="text">`, sin ninguna lectura previa del archivo. El archivo (`archivo: File`)
se manda tal cual al backend en el `FormData` del stream (`sse.ts::buildFormData`) — el frontend
nunca parsea el CSV/Excel del lado del cliente; quien lo parsea hoy es
`core/validacion/parser.py` (`pandas.read_csv`/`read_excel`), del lado del servidor, dentro del
pipeline de Etapa 1 ya en curso.

**Para analizar antes de decidir:**
- Esto requiere parsear el archivo (al menos las cabeceras) **del lado del cliente**, antes de
  enviarlo — hoy no hay ninguna lógica de parseo en `frontend/`. Evaluar una librería liviana
  (ej. leer solo la primera fila con `FileReader` para CSV; Excel es más complejo, requeriría algo
  tipo `xlsx`/`sheetjs` en el bundle del frontend) vs. un endpoint nuevo de "previsualizar
  columnas" que delegue el parseo al backend (que ya sabe hacerlo) antes de correr el pipeline
  completo.
- `columna_x`/`columna_y` hoy viajan como string (nombre o índice, ver
  `core/validacion/parser.py::_resolver_columna`) — un dropdown pobla ese mismo campo con el valor
  elegido, no cambia el contrato en sí. Pero si se agrega un paso de "previsualizar antes de
  ejecutar", eso sí es un cambio de flujo (¿un paso nuevo en el wizard? ¿carga asincrónica dentro de
  la misma pantalla?) que conviene decidir explícitamente, no improvisar.
- Comportamiento ante archivo con columnas ambiguas, sin cabecera, o con nombres duplicados — a
  definir antes de implementar el dropdown, no durante.

---

## 3. Tipo de variable — extensible y usado como etiqueta del conjunto de datos

**Observación.** "Tipo de variable" hoy es una elección fija entre dos botones ("Caudal/Precip." /
"Otro"). Debería permitir escribir un valor libre y ofrecer otras opciones además de esas dos —  y a
partir de ahí, el resto de la aplicación (resultados, historial, etc.) debería referirse al conjunto
de datos usando el tipo de variable elegido, no un genérico.

**Estado actual del código.** `types.ts::TipoVariable = "caudal_precipitacion" | "otro"` — unión
literal cerrada, no un string libre. `ConfigPage.tsx` la implementa como dos botones tipo toggle
(`aria-pressed`), no como campo editable. El backend recibe `tipo_variable` como `Form(str)` en
`api/v1/analysis.py`, pero **la lógica de negocio real depende de que el valor sea exactamente
`"caudal_precipitacion"`** en varios puntos del core — no es solo una etiqueta decorativa:
- `core/etapa1/outliers.py` (Chow): decide `TEST_NOT_EXECUTED_ZEROS` solo si
  `tipo_variable == "caudal_precipitacion"` y hay ceros.
  `DISABLED_WITH_ZEROS` (`core/etapa2/distributions/`) aplica la misma condición a 4 distribuciones
  de Etapa 2.
- Warnings de contrato (`CONTRACT_NEGATIVE_VALUES`) también condicionan por ese valor exacto.

**Para analizar antes de decidir:**
- Esto **no es solo un cambio de UI** — `tipo_variable` es hoy un discriminante que activa reglas
  de negocio específicas de hidrología (ceros, negativos) en `core/`, `constraints.md` y
  `formulas-etapa1.md`/`formulas-etapa2.md`. Un campo libre necesita definir: ¿"caudal_precipitacion"
  sigue siendo un valor mágico especial (con las reglas de ceros/negativos activas) y todo lo demás
  cae en el comportamiento de "otro"? ¿O se necesita una tercera categoría intermedia?
- "Que de ese punto en adelante se refieran al conjunto de datos en base al tipo de variable
  elegida" — hoy `HistoryItem`/`AnalysisDetail` ya exponen `tipo_variable` tal cual se envió, así
  que mostrarlo en Resultados/Historial es principalmente trabajo de UI. Pero si el pedido es que
  aparezca como **etiqueta prominente** en más lugares (títulos de sección, gráficos, PDF de
  exportación), conviene relevar todas las pantallas que hoy asumen "caudal" implícitamente en su
  texto (ej. columnas de tablas, textos de ayuda) antes de tocar una sola.
- Confirmar con Facundo/Octavio si ampliar `tipo_variable` más allá de las dos opciones actuales
  tiene sentido hidrológico, o si "Otro" ya cubre el caso general a propósito.

---

## 4. Qué es el badge "pendiente · datos de ejemplo"

**Pregunta de Kevin, respondida acá para que quede documentado.** Es el componente
`PendingBadge` (`frontend/src/mocks/PendingBadge.tsx`), visible en `RankingPage` y
`DesignEventsPage`. Significa exactamente lo que dice: Etapa 2 (ranking de distribuciones, eventos
de diseño) **no tiene backend real todavía** — los endpoints existen documentados en
`api-contracts.md` pero no están implementados del lado del servidor (`design-events`) o ni
siquiera tienen contrato REST (`ranking`, solo mencionado como evento SSE que el backend nunca
emite). Lo que se ve en esas dos pantallas son datos de ejemplo hardcodeados en el frontend
(`frontend/src/mocks/etapa2.mock.ts`, `designEvents.mock.ts`), no un análisis real de los datos
cargados. Es una decisión de producto explícita (DECISIÓN 042) mostrar el flujo completo de todas
formas — para que se vea la experiencia de punta a punta — en vez de ocultar esas dos pantallas
hasta que Etapa 2 se exponga de verdad.

**Para analizar (no una pregunta técnica, sino de producto):**
- ¿El texto/tono actual ("pendiente · datos de ejemplo", con nota expandida "Etapa 2 no expuesta
  por API todavía") es apropiado para el usuario final (docente, alumno, uso anónimo), o suena
  demasiado a lenguaje interno de desarrollo? Si el tribunal o un usuario real va a ver esta
  pantalla, vale la pena decidir una redacción pensada para ese público, no solo para quien conoce
  el proyecto por dentro.

---

## 5. Historial — borrar/archivar análisis, y búsqueda por nombre de archivo

**Observación.** "Tu historial" debería permitir borrar o archivar análisis existentes. Además,
debería incorporar una barra de búsqueda que permita encontrar todos los análisis hechos sobre un
mismo archivo por nombre (ejemplo: buscar "dique san roque" y que traiga todos los análisis
corridos sobre excels que se llamaban así).

**Estado actual del código — dos gaps distintos, de tamaño muy distinto:**

- **Borrar/archivar: no existe ningún endpoint para esto.** `api-contracts.md` no documenta ningún
  `DELETE /api/v1/history/{id}` ni campo de estado tipo `archivado`. `HistoryPage.tsx`/
  `HistoryDetailPage.tsx` solo leen (`listHistory`/`getHistoryItem`, ambos `GET`). Requiere
  endpoint nuevo en el backend (`api/v1/history.py`), decisión sobre soft-delete (columna
  `archivado`/`deleted_at` en la tabla `analyses`) vs. borrado real, y la confirmación de UX
  correspondiente (¿confirmación antes de borrar? ¿deshacer?).

- **Búsqueda por nombre de archivo: el dato ni siquiera se guarda hoy.** Ni `HistoryItem`/
  `AnalysisDetail` (`frontend/src/api/types.ts`) ni la tabla `analyses` (ver `architecture.md`,
  columnas `id, user_id, serie, tipo_variable, etapas, modo, configuracion, created_at`) tienen un
  campo para el nombre del archivo original subido. El nombre del `File` que el usuario carga en
  `ConfigPage` **nunca se persiste** — se usa para el `FormData` del stream y se descarta. Esto es
  un cambio de esquema (agregar columna, ej. `nombre_archivo`), no solo de UI: hay que decidir dónde
  se captura (¿en el momento del upload? ¿se guarda tal cual o normalizado?) y cómo migra
  (`alembic`) antes de que la búsqueda tenga algo sobre qué buscar.

**Para analizar antes de decidir:**
- Los dos ítems de este punto no tienen el mismo tamaño — borrar/archivar es principalmente un
  endpoint + UI; búsqueda por archivo requiere primero decidir y migrar un cambio de esquema.
  Conviene tratarlos como dos decisiones separadas, no una sola tarea.
- Si se guarda el nombre del archivo, ¿debe poder editarse después (por si el usuario quiere
  renombrar "para buscar mejor" más adelante) o queda fijo al momento de la carga?
- Alcance de la búsqueda: ¿coincidencia exacta, parcial (`LIKE %texto%`), o algo más flexible
  (normalizar mayúsculas/tildes, como "Dique San Roque" vs. "dique_san_roque.csv")? Afecta si la
  búsqueda se resuelve client-side (ya se pagina client-side, ver `HistoryPage.tsx`) o necesita un
  parámetro nuevo en `GET /api/v1/history/`.
