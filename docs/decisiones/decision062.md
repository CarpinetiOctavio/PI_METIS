# DECISIÓN 062 — Historial interactivo: explorar otra distribución no es decidir

**Fecha:** 18 de Agosto de 2026
**Estado:** Aplicada — backend (Bloque C2c, `POST /analysis/{id}/design-events`)
y frontend (Bloque C3, `HistoryDetailPage` interactiva) del [plan post-avance](../plan-post-avance.md),
ambos mergeados a `staging`.

**Corrección 18/08/2026 (Bloque I, relevamiento final del plan):** esta
sección decía "implementación en curso (Bloque C2c)" — desactualizado desde
que el Bloque C3 (frontend) se cerró y mergeó (PR #67) el mismo día. El
párrafo sobre "el frontend (Bloque C3) muestra siempre..." más abajo ya
describía el comportamiento real, solo el encabezado había quedado atrás —
encontrado auditando el relevamiento final (Bloque I), no un cambio de
comportamiento.

### Contexto

[DECISIÓN 060 y 061 ya están tomadas por otro frente de trabajo](decision060.md)
(guards de dominio y política ante ceros en Etapa 2, auditoría de Octavio del
17/08/2026) — el `plan-post-avance.md` había reservado esos dos números para
temas de este bloque (historial interactivo y paso a paso vs. experto), pero
ambos ya no están libres al momento de implementar. Esta decisión toma el
próximo número real disponible, **062** (`plan-post-avance.md` lo tenía
reservado para el panel acoplable del Bloque E — ese tema pasa a 063 cuando
se implemente).

El Bloque C del plan post-avance agrega historial interactivo de Etapa 2: el
detalle de un análisis persistido no solo muestra qué distribución se eligió
durante el stream, sino que permite elegir **otra** desde ahí y ver sus
eventos de diseño recalculados, sin volver a correr el pipeline completo.
Esto es posible sin reajustar nada porque `_serializar_etapa2()` ya persiste
`parametros` de las 28 combinaciones distribución+método en
`analysis_results.etapa2.ranking` — recalcular eventos de diseño para
cualquiera de ellas es solo `calcular_eventos_diseno()` con parámetros que
ya están en la base.

### La pregunta que resuelve esta decisión

Si el usuario, desde el historial, elige explorar una distribución distinta
de la que usó durante el análisis original — **¿eso queda registrado como
una nueva decisión?**

### Decisión

**No.** `analysis_results.decisiones` es el registro de auditoría de lo que
se decidió *durante el análisis* (CU-01) — la elección real ante el atípico
de Chow y ante la selección de distribución, en el momento en que el
pipeline estaba corriendo y esperando esa decisión para continuar. Dejar que
una exploración posterior, sin pipeline en curso y sin ningún efecto sobre
ningún resultado persistido, escriba en esa misma columna rompe la
trazabilidad: ya no se podría distinguir "esto fue lo que el usuario decidió
cuando corrió el análisis" de "esto fue lo último que miró en el historial".

En consecuencia, el endpoint nuevo `POST /analysis/{id}/design-events`:

- **No toca `session_store`** — no hay ningún stream en curso ni pausa que
  resolver, es una consulta stateless sobre datos ya persistidos.
- **No persiste nada** — ni una fila nueva, ni un campo actualizado en
  `analyses` o `analysis_results`.
- **No altera `analysis_results.decisiones`** — la elección original queda
  exactamente como quedó al terminar el stream.

El frontend (Bloque C3) muestra siempre, de forma destacada, cuál fue la
elección registrada (`etapa2.seleccion`) — y marca cualquier resultado que
venga de este endpoint como "exploración", visualmente distinto de la
elección real. Es información docente que las dos etiquetas puedan no
coincidir (la de menor EEA vs. la elegida vs. la explorada), no algo a
esconder.

### Errores

`GET /history/{id}` y `POST /analysis/{id}/design-events` comparten el mismo
guard de pertenencia (`Analysis.user_id == current_user.id`) — un análisis
ajeno o inexistente responde igual en los dos casos, sin distinguir "no
existe" de "no es tuyo" (mismo criterio que el resto del catálogo, ver
`api-contracts.md`).

Dos códigos nuevos:

- **`ANALYSIS_NOT_FOUND`** (404) — el análisis no existe, no pertenece al
  usuario, o no tiene Etapa 2 ejecutada (`analysis_results.etapa2` es
  `null`) — este último caso no es distinguible del anterior sin revelar si
  el id existe, así que se trata igual.
- **`DIST_METHOD_NOT_FITTED`** (400) — la combinación distribución+método
  pedida no aparece en el ranking persistido, o aparece con
  `status != "ok"` (no convergió, no aplicable, deshabilitada por ceros —
  no hay `parametros` de los que partir). Distinto de `DIST_SELECTION_INVALID`
  (400, reusado del endpoint `distribution-decision` sin cambios): ese código
  es sobre la **forma** del request (campos vacíos, `periodos_retorno` fuera
  de rango); este es sobre si la combinación pedida, bien formada, tiene algo
  que recalcular.

### Criterio de hecho

- `recalcular_eventos_diseno()` en `services/analysis_service.py` no importa
  nada de `session_store` ni escribe en `db` — solo lee.
- Test que confirma que, tras llamar al endpoint con una distribución
  distinta de la elegida, `GET /history/{id}` sigue devolviendo la misma
  `etapa2.seleccion` y las mismas `decisiones` que antes de la llamada.
- `pytest -m "unit or integration"` en verde.

**Ver también:** [DECISIÓN 055](decision055.md) — por qué `_serializar_etapa2()`
persiste la grilla completa sin aplanar, lo que hace viable este recálculo sin
reajustar nada. [DECISIÓN 052](decision052.md) — el endpoint que este bloque
complementa (`distribution-decision`, la decisión real durante el stream).
