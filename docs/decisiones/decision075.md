# DECISIÓN 075 — Exportación PDF de CU-01: ReportLab + matplotlib en el backend, siempre formato Experto, módulo `metis/reportes/`

**Fecha:** 6 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend).
**Decide:** Kevin.
**Origen:** pendiente `GET /export/{id}` de `docs/checklist-pendientes-feedback-directores.md` (M3), contrato ya
escrito en `api-contracts.md`/`constraints.md` ("PDF de exportación — CU-01") desde el anteproyecto.

### Contexto

El contrato fijaba tres cosas y dejaba el resto abierto: `GET /api/v1/export/{id}`, solo CU-01 (JWT y análisis
persistido), y PDF generado en el momento, sin guardarse en disco. No había librería de PDF en `requirements.txt`
ni decisión sobre gráficos, contenido de Etapa 2 o modo de presentación. `constraints.md` preveía un PDF distinto
para paso a paso (con fórmulas sustituidas) y para Experto.

### Alternativas evaluadas

**Dónde se genera.**
- *En el navegador* (jsPDF, `window.print()`): descartada. CU-01 ya tiene todo persistido en el backend, que es
  quien hace las cuentas; generarlo en el cliente obligaría a reconstruir en TypeScript tablas y gráficos que hoy
  dependen del estado de la pantalla, y el contrato ya era un endpoint del backend.
- *En el backend* — elegida.

**Librería.**
- *WeasyPrint* (HTML + CSS → PDF): maquetado más cómodo, pero necesita pango/cairo en la imagen Docker y es
  engorroso de instalar en Windows, donde se desarrolla.
- *ReportLab* — elegida: Python puro con wheels para Linux y Windows, sin dependencias de sistema; el
  `Dockerfile` no cambia.

**Gráficos.** Solo tablas era lo más liviano, pero un informe de frecuencia sin la curva de ajuste pierde lo
principal. Se dibujan con **matplotlib** (backend `Agg`, `Figure` sin `pyplot`, seguro en hilos) a PNG de 200 dpi:
serie analizada (con el atípico de Chow marcado), correlograma de Anderson (si el payload trae `desglose`) y ajuste
de la distribución elegida (puntos de Weibull, curva y eventos de diseño, eje T logarítmico). matplotlib 3.10.7:
3.9.x emite ~300 `PyparsingDeprecationWarning` con pyparsing 3.3; 3.10.7 no, y mantiene numpy 1.26.4.

**Modo.** El PDF es **siempre Experto** (resultados directos, sin fórmulas ni explicaciones), aunque el análisis se
haya corrido en paso a paso. Esto reemplaza la variante "paso a paso con fórmulas" de `constraints.md` para V1.0:
el modo docente vive en la pantalla, con KaTeX (DECISIÓN 064); duplicarlo en el PDF sería mantener una segunda
plantilla de cada fórmula.

**Ranking de Etapa 2.** Las 13 distribuciones con su mejor método, EEA y EEA/media, en el orden persistido (por
EEA). No se marca ninguna como ganadora (`constraints.md`, "METIS no sugiere distribución ganadora"); la única fila
resaltada es la que eligió el usuario, rotulada "Elegida por el usuario". Gen. Pareto lleva "Pendiente de
validación, no elegible" (DECISIÓN 074). Se descartó la grilla de los 28 métodos (varias páginas) y mostrar solo la
elegida (se pierde el contexto de la elección).

**Alcance.** Solo CU-01, como dice el contrato. Exportar CU-02 exigiría un endpoint que reciba el payload del
cliente — fuera de esta decisión.

### La decisión

- **`metis/reportes/pdf.py`** — módulo nuevo de presentación pura: `generar_pdf_analisis(detalle, autor)` recibe el
  dict de `get_analysis_by_id()` (el mismo de `GET /history/{id}`) y devuelve bytes. No importa `api/`,
  `services/`, `db/` ni `core/` y no recalcula nada. No va en `core/` (no es cálculo estadístico) ni en `services/`
  (no orquesta): es la capa que faltaba, según `architecture.md` ("lógica que no encaja → módulo nuevo").
  `curva_ajuste` no se recalcula: ya se persiste dentro de `etapa2.seleccion` (Bloque C2a).
- **Fuente DejaVu Sans**, tomada de los datos de matplotlib: cubre α, β, ≤ y subíndices, que Helvetica (WinAnsi) no
  tiene, sin sumar archivos de fuente al repo.
- **`services/export_service.py::exportar_pdf()`** — reusa `get_analysis_by_id()` (mismo guard de pertenencia) y
  corre el maquetado en `asyncio.to_thread` (CPU-bound, ~0,5 s con gráficos).
- **`api/v1/export.py`** — `GET /api/v1/export/{id}`, `get_current_user` obligatorio, `Content-Disposition:
  attachment; filename="metis_<archivo>_<fecha>.pdf"` (ASCII). 404 `ANALYSIS_NOT_FOUND` armado con `JSONResponse`
  para que el body sea `{"error": {...}}`, la estructura estándar — ver "Hallazgo" abajo. No hay código de error
  nuevo.
- **Frontend** — `ExportarPdfButton` (`routes/results/`) en `ResultsPage` (solo con sesión y `analysisId`) y en
  `HistoryDetailPage`. `api/export.ts` separa pedir el PDF (`obtenerPdfAnalisis`) de guardarlo (`guardarPdf`), por
  la misma razón que `descargarCsv`: jsdom no implementa `URL.createObjectURL`.

### Puntos excluidos

Dos caminos sacan puntos de la serie, y el PDF los trata distinto:

- **Atípico rechazado en la pausa de Chow.** Es una decisión registrada: el análisis persistido ya es el de la serie
  sin ese dato (Etapa 1 y Etapa 2), así que el PDF lo refleja sin hacer nada. Agrega la decisión, con el año del dato
  cuando la carga es anual (con carga mensual o diaria el valor es un máximo agregado y no se ubica en un único
  registro de la serie subida).
- **Exclusión interactiva (what-if, DECISIÓN 071).** No se guarda ni cambia lo registrado ("explorar no es decidir",
  DECISIÓN 062). Exportar solo el análisis registrado con una simulación a la vista era engañoso; exportar solo la
  simulación, perder la referencia. El PDF muestra **las dos**, como la pantalla: el análisis registrado completo y,
  en una página aparte, "Resultados sin los puntos excluidos": puntos quitados (año y valor) y `n` antes → después,
  la serie con los excluidos marcados, la comparación prueba por prueba (con lo que cambió resaltado), los niveles,
  el atípico que Chow marque sin esos puntos, las advertencias nuevas, el ranking sin esos puntos y, si hay una
  distribución elegida, sus eventos de diseño original contra reajustados (con la diferencia en %) y las dos curvas
  de ajuste superpuestas. La sección aclara que es una simulación y que no cambia el análisis ni la elección.

**`POST /api/v1/export/{id}/simulacion`** con `{"indices_excluidos": [...]}`. Del cliente llegan **solo los
índices** (posiciones en `datos.serie_efectiva`, como en `simulate-exclusion`): la serie, los años, la configuración
y la elección salen del análisis persistido (`services/export_service.py::_simular_desde_detalle`), y se recalcula
con la misma `simular_exclusion()` de DECISIÓN 071. Así el PDF no puede mostrar una serie distinta de la del
análisis. Se descartó mandar al backend la respuesta de `simulate-exclusion` que el frontend ya tiene: ahorraba ~40
ms de cálculo a cambio de imprimir, con el nombre del usuario, resultados que el servidor no calculó. Sin índices,
con índices fuera de rango o repetidos, o con un análisis sin `datos` (anterior a DECISIÓN 058) → 400
`CONTRACT_EXCLUSION_INVALID`. Sin código nuevo.

**Frontend:** con una simulación vigente, `ResultsPage` suma "Exportar PDF con la simulación" junto a "Exportar PDF".
Usa los índices de la simulación vigente (la respuesta del backend), no la selección en curso, que puede haber
cambiado sin recalcular. `HistoryDetailPage` no lo tiene porque el historial todavía no ofrece la simulación
(pendiente en `checklist-pendientes-feedback-directores.md`).

### Hallazgo (resuelto en `fix/estructura-error-estandar`)

Los endpoints que levantan `HTTPException(detail={"error": {...}})` responden `{"detail": {"error": {...}}}`, y
`api/client.ts::toApiError()` solo reconoce `{"error": {...}}`: esos códigos llegan al frontend como
`UNKNOWN_ERROR` y se muestra el texto genérico. Afecta a `CONTRACT_*`, `DIST_*`, `SESSION_NOT_FOUND` y
`ANALYSIS_NOT_FOUND` de `design-events`, y también a los `AUTH_*` (el login con contraseña incorrecta mostraba el
texto genérico). Este endpoint lo evita por su cuenta; el arreglo general va en un PR propio, con un manejador
global (`metis/api/errors.py`). Con ese PR mergeado, el `JSONResponse` de acá se puede volver un `HTTPException`
como el resto, sin cambio de comportamiento.

### Verificación

- `tests/unit/reportes/test_pdf.py` (12): payload armado con el pipeline y los serializadores reales; Etapa 1 sola,
  Etapa 1+2 con y sin elección, contrato bloqueante, Etapa 2 pedida con Etapa 1 rechazada, análisis anterior sin
  `datos`/`desglose`/`timestamps`, ranking de 13 sin ganadora, sin fórmulas aunque el payload traiga `explicacion`.
- Simulación, en el mismo archivo (5): la comparación con y sin los puntos, que la entrada sale del análisis
  persistido, la simulación que deja la serie bajo el mínimo, el análisis sin `datos` y el nombre del archivo.
- `tests/unit/api/test_export.py` (8) y `tests/unit/services/test_export_service.py` (4).
- Frontend: `api/export.test.ts`, `ExportarPdfButton.test.tsx` y `ResultsPage.simulacion.test.tsx` (el botón
  aparece con una simulación vigente y manda sus índices).
- Los 18 análisis de la BD local de desarrollo se exportaron sin error; revisión visual del PDF, con y sin
  simulación.
- HTTP real: 200 `application/pdf` con sesión (también a través del proxy de Vite), 404 con estructura estándar
  para un id ajeno o inexistente, 401 sin sesión; con simulación, 400 `CONTRACT_EXCLUSION_INVALID` para índices
  vacíos o fuera de rango.
