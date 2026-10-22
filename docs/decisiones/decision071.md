# DECISIÓN 071 — Exclusión de puntos: eliminar en cualquier posición y `POST /analysis/simulate-exclusion` sin estado

**Fecha:** 1 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend)
**Decide:** Kevin (política elegida el 20/09/2026; implementada en el PR 5 del plan de fixes post-verificación,
[`plan-fixes-post-verificacion-01-10-2026.md`](../historico/planes/plan-fixes-post-verificacion-01-10-2026.md) §3.A).
**Origen:** pedido de Catalini en el feedback de directores (ítem A,
[`plan-backend-feedback-directores-20-09-2026.md`](../plan-backend-feedback-directores-20-09-2026.md) §4):
desactivar puntos desde la pantalla de resultados, ver los resultados como si no hubieran estado y, si sirve,
descargar la serie sin ellos.

### Contexto

El PR #93 (A1) ya resolvía la parte de frontend: selección con clic en el gráfico, lista con checkbox y descarga
del CSV. El PR #95 sumó la comparación original vs. simulado, pero contra un mock: el endpoint no existía y la
interfaz quedaba apagada detrás de `VITE_SIMULATE_EXCLUSION=1`. Faltaba decidir qué significa "excluir" un punto
y quién recalcula.

### Alternativas evaluadas

- **(1) Reemplazar el punto por la media.** **Postergada, no descartada.** Tres contras: sería el único lugar del
  producto que completa datos (todo el resto elimina y compacta); reduce la varianza y acerca las
  autocorrelaciones a cero, lo que favorece aprobar independencia; y en Etapa 2 un valor medio entraría como si
  fuera un máximo anual observado. Se decide con el feedback de los directores sobre la versión implementada.
- **(2) Recalcular en el frontend.** Descartada: duplicaría en TypeScript la batería de Etapa 1, y `core/` es la
  única fuente de verdad matemática (mismo criterio que DECISIÓN 058 para la versión calendario).
- **(3) Endpoint con `id` de análisis** (como `POST /analysis/{id}/design-events`). Descartada: dejaría afuera a
  CU-02, que no persiste nada. El frontend ya tiene la serie efectiva en el payload de Etapa 1.
- **(4) Elegida: eliminar en cualquier posición, en un endpoint sin estado** que recibe la serie efectiva.

### La decisión

- **Política:** un punto excluido se **elimina** junto con su año, en cualquier posición y para las dos etapas.
  Es la misma operación que ya hace el rechazo de un atípico de Chow (quitar valor y timestamp por índice) y el
  mismo criterio que aplican los faltantes y la agregación temporal: eliminar y compactar, nunca imputar.
- **`core/pipeline/exclusiones.py::aplicar_exclusiones(serie, anios, indices_excluidos, tratamiento="eliminar")`**
  — función pura. Devuelve la serie, los años y la lista `excluidos` (`{indice, periodo, valor_original}`).
  Cualquier `tratamiento` distinto de `"eliminar"` levanta `ExclusionInvalidaError`, nunca se ignora en silencio:
  es el punto de extensión si se aprueba el reemplazo por la media.
- **`POST /api/v1/analysis/simulate-exclusion`** — validación en el borde (`api/v1/analysis.py`), lógica en
  `services/analysis_service.py::simular_exclusion()`, mismo patrón que `recalcular_eventos_diseno()`:
  - Sin dependencia de usuario, sin `session_store`, sin BD. No persiste nada ni toca `decisiones`
    (DECISIÓN 062, "explorar no es decidir").
  - Recibe `serie`/`anios` = `datos.serie_efectiva` y los años de `datos.timestamps_efectivos` (la serie ya
    agregada; los índices son posiciones en ella, no en la serie cruda), más `tipo_variable`,
    `cramer_particion` (texto, igual que `/stream`), `etapas` y `tratamiento` opcional.
  - Corre `ejecutar_etapa1(..., resolucion_temporal="anual")`, igual que la segunda pasada del rechazo de Chow
    (no se vuelve a agregar). **Chow sin pausa:** un atípico nuevo se informa en `etapa1.atipicos`.
  - Con `etapas == [1, 2]` y `nivel_confianza != "rechazado"`, corre `ejecutar_etapa2` en la misma respuesta
    (~40 ms, sincrónico alcanza), con `tiene_ceros`/`tiene_negativos` sobre la serie resultante (DECISIÓN 073).
  - Serializa con `_serializar_etapa1`/`_serializar_etapa2`: la respuesta trae el mismo payload que el stream,
    incluido el `desglose` del addendum a la DECISIÓN 064, y la serie resultante para que el CSV salga de lo que
    devolvió `core/`.
- **Límites:** hasta 500 valores (un análisis anual real no pasa de ~150); `anios` como enteros.
- **Errores:** `CONTRACT_SERIES_INVALID` (serie vacía, > 500 o no finita) y `CONTRACT_EXCLUSION_INVALID`
  (índices fuera de rango o repetidos, `anios` de otro largo, `tratamiento` inexistente), ambos 400 y al
  catálogo en el mismo commit (DECISIÓN 038). Que queden menos de 10 datos **no** es un error nuevo: responde el
  bloqueante de siempre (`CONTRACT_SERIES_TOO_SHORT`) dentro de `etapa1.contract`, con 200.
- **El flujo de Chow no se toca** (decisión de Kevin del 20/09). Que los dos criterios den lo mismo se prueba con
  un test, no con un refactor compartido.
- **Frontend:** fuera `VITE_SIMULATE_EXCLUSION` y `simulacionExclusionDisponible()`; la interfaz queda siempre
  encendida en `ResultsPage`. El CSV se arma con `serie`/`anios` de la respuesta cuando la simulación corresponde
  a la selección actual.

### Consecuencias

- **Efecto conocido y aceptado sobre las pruebas de orden:** al quitar un punto interior, los vecinos quedan
  contiguos, y Anderson, Wald-Wolfowitz, Cramer y Mann-Kendall tratan como consecutivos a dos años que no lo son.
  Es el mismo efecto que ya tiene rechazar un atípico de Chow.
- Ningún estadístico, valor crítico ni veredicto del análisis original cambia: la simulación es una consulta
  aparte.
- **Tests:** unitarios de `aplicar_exclusiones` (posiciones, entrada sin modificar, pedidos inválidos);
  del endpoint (200, cada 400, sin cookie, `< 10` datos); **regresión 1** (`indices_excluidos=[]` da la misma
  Etapa 1 que el análisis original — verificado sobre una serie sintética, no sobre las 9 de la tesis, que
  siguen como verificación fuera del repo); **regresión 2**
  (`tests/integration/test_simulate_exclusion_equivale_a_chow.py`: excluir el atípico da los mismos estadísticos,
  veredictos y niveles que "rechazar" en el stream, también con una celda vacía en la carga anual). No se
  comparan `warnings`: el flujo de Chow arrastra los de agregación de la primera pasada
  (`CODIGOS_WARNING_AGREGACION`) y un endpoint sin estado no los tiene.

### Fuera de alcance

- `HistoryDetailPage` no ofrece la simulación todavía (solo `ResultsPage` pasa `simular`). Necesitaría
  `tipo_variable` y `cramer_particion` de `detail.configuracion`; queda anotado.
- Elegir una distribución sobre el ranking simulado requiere el endpoint de exploración sin id (bloque B,
  DECISIÓN 072 reservada), que no entra en este plan.

### Relación con otras decisiones

- **DECISIÓN 062** — "explorar no es decidir": la simulación no persiste ni altera `decisiones`.
- **DECISIÓN 064** (addendum 01/10/2026) — `desglose` de Anderson y Chow, presente en la respuesta.
- **DECISIÓN 073** — `tiene_negativos` para Etapa 2 de la simulación.
- **DECISIÓN 057/065** — la serie que se recibe ya está agregada; por eso `resolucion_temporal="anual"`.

### Addendum 02/10/2026 — eventos de diseño de la elección, sin los puntos excluidos

En uso real, recalcular sin el atípico actualizaba Etapa 1 y el ranking simulado, pero los gráficos de
"Evento de diseño" del fondo de `ResultsPage` seguían mostrando la elección del análisis original. El
backend no podía hacer otra cosa: el request no decía qué distribución+método se había elegido.

- **Request:** campo opcional `seleccion: {distribucion, metodo, periodos_retorno}` — la elección del stream.
  Se valida en el borde con la misma función que `distribution-decision` (400 `DIST_SELECTION_INVALID` y
  `DIST_PENDING_VALIDATION`); sin códigos nuevos.
- **Respuesta:** con `seleccion` y Etapa 2 recalculada, `etapa2.seleccion` trae `eventos_diseno` y
  `curva_ajuste` de esa misma combinación con los parámetros reajustados sin los puntos excluidos
  (`_seleccion_recalculada()`, mismas funciones que el stream: `calcular_eventos_diseno`,
  `_calcular_curva_ajuste`). Si la combinación ya no ajusta, los eventos van con `valor: null` y la curva
  vacía, igual que en el stream. Sin `seleccion`, o sin Etapa 2, `etapa2.seleccion` sigue en `null`.
- **Frontend:** la sección "Evento de diseño" gana un selector Original / Sin los puntos excluidos mientras
  haya una simulación vigente para la selección actual, con un rótulo de simulación. Al llegar una
  simulación nueva pasa a esa vista; si la selección cambia y la simulación queda desactualizada, vuelve
  sola al original.
- **Explorar no es decidir (DECISIÓN 062):** la elección registrada no cambia y nada se persiste. Se mantiene
  la misma distribución+método: elegir otra sobre el ranking simulado sigue requiriendo el bloque B.

### Revisión 18/10/2026 — la exploración de otra distribución respeta la simulación

En uso real, después de excluir el atípico de 950 y recalcular, la columna de exploración de
`Etapa2Explorador` seguía llamando a `POST /analysis/{id}/design-events`, que parte del ranking persistido de
la serie original: la curva explorada se veía con el 950 adentro aunque la simulación vigente lo hubiera
quitado, y no había forma de verla sin él. Bloque A de `docs/historico/planes/plan-significancia-y-fixes-18-10-2026.md`.

- **Sin endpoint nuevo.** Explorar bajo una simulación es llamar a `simulate-exclusion` con los mismos puntos
  excluidos y la combinación explorada en `seleccion` (el campo del addendum anterior). Sigue sin estado y sin
  tocar `decisiones` (DECISIÓN 062).
- **`etapa2.seleccion.estado`** (respuesta): el status de la combinación sobre la serie sin los puntos (`ok`,
  `no_converge`, `no_aplicable`, `disabled_zeros`, `disabled_negatives`; una combinación que no está en el
  ranking es `no_aplicable`). Antes, una combinación que dejaba de ajustar volvía con los eventos en `null` sin
  decir por qué. Solo lo trae esta respuesta: la `seleccion` persistida del historial no lo tiene.
- **Un único selector "Ver resultados: Original | Sin los puntos excluidos"** sobre la comparación, que cambia
  a la vez la elección registrada y la exploración. Comparar la elección sin los puntos contra una exploración
  con los puntos no tiene sentido, y dos selectores independientes invitan a ese error. Aparece solo con una
  simulación vigente que tenga Etapa 2. En CU-02 (sin exploración) queda donde estaba, en "Evento de diseño".
- **La exploración se pide dos veces en paralelo** cuando hay simulación (contra el análisis original y sin los
  puntos), y la vista simulada usa los `puntos_empiricos` de la simulación. Si la simulación cambia o se limpia,
  la exploración simulada que había deja de mostrarse y se vuelve a pedir: ninguna vista queda mostrando una
  simulación vieja. Si la combinación no ajusta sin los puntos, la vista lo explica con el status.
- Tests: `test_simulate_exclusion.py` (combinación que ajusta con el atípico y no sin él), `Etapa2Explorador.test.tsx`
  y `ResultsPage.simulacion.test.tsx`.

### Revisión 21/10/2026 — la simulación también desde el historial

Bloque B de `docs/plan-revision-manual-21-10-2026.md`. El detalle del historial dejaba marcar puntos y descargar el
CSV, pero no recalculaba: `HistoryDetailPage` montaba `Etapa1ResultView` sin la función `simular`. Ahora la arma con
los datos **persistidos**, sin cambios en el servidor: `etapa1.datos.serie_efectiva` y los años de
`timestamps_efectivos`, `tipo_variable`, `etapas`, `configuracion.cramer_particion`, `configuracion.alfa` y la
elección registrada (`etapa2.seleccion`). Las dos páginas construyen el pedido con la misma función,
`frontend/src/routes/results/simulacion.ts` (`crearPedirSimulacion`, `crearSimular`).

- Con una simulación vigente, el historial también ofrece el PDF con ella (`POST /export/{id}/simulacion`).
- Un análisis anterior a la DECISIÓN 058 (`timestamps === null`) no tiene los años de la serie analizada: no se ofrece
  la simulación y el aviso de ese caso lo dice.
- Sigue valiendo "explorar no es decidir" (DECISIÓN 062): la simulación no se guarda ni toca el registro.
- Fuera de este bloque: en el historial, la vista simulada de los eventos de diseño y de la exploración de Etapa 2 (el
  selector "Original | Sin los puntos excluidos" de Resultados). La comparación de Etapa 1 y el PDF sí están.
- Tests: `HistoryDetailPage.simulacion.test.tsx`.

### Revisión 21/10/2026 — la simulación se puede guardar (DECISIÓN 080)

Desde la vista comparativa (Resultados con `analysisId`, o el historial), "Guardar esta exclusión en el historial"
registra los índices, con su año y su valor, en `analysis_results.exclusiones`. No guarda el resultado de la
simulación: "Ver" vuelve a pedirlo a este mismo endpoint, que es determinístico. Ver la [DECISIÓN 080](decision080.md).
