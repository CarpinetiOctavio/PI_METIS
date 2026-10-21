# DECISIÓN 080: las exclusiones de puntos hechas después del análisis se pueden guardar en el historial, aparte del resultado

**Fecha:** 21 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend) — bloque C2 de `docs/plan-revision-manual-21-10-2026.md`.
**Decide:** Kevin, a partir de la revisión manual del 21/10/2026.
**Depende de:** DECISIÓN 062 ("explorar no es decidir") y DECISIÓN 071 (simulación de exclusión de puntos).

### Problema

Hay dos formas de quitar puntos de un análisis. En la pausa de Chow, el usuario rechaza atípicos: es una decisión, el
análisis se recalcula sin ellos y queda en `decisiones.chow`. Con "Excluir puntos de la serie", después del análisis,
el usuario quita cualquier punto y ve los resultados sin él (DECISIÓN 071): es una exploración, y hasta ahora no se
guardaba en ningún lado. Al volver al historial, esa exploración se perdía; para mostrársela a alguien había que
rehacerla a mano.

### La decisión

La exclusión se puede **guardar aparte** del resultado, como una exclusión registrada del análisis.

- **Qué se guarda** (`analysis_results.exclusiones`, migración `006`, lista JSONB con default `[]`): por cada
  exclusión, `{id, creado_at, indices, puntos: [{indice, periodo, valor}], alfa, cramer_particion}`. Los años y los
  valores salen del análisis persistido, no del cliente: del cliente llegan solo los índices.
- **Qué no se guarda: los resultados.** Al abrir una exclusión guardada, la comparación se recalcula con
  `POST /analysis/simulate-exclusion`, que es determinístico (misma serie, mismos índices, misma configuración, mismo
  resultado). Guardarlos duplicaría el resultado de cada exploración y haría crecer la base sin agregar información.
- **Cuándo se guarda: a pedido.** Solo cuando el usuario aprieta "Guardar esta exclusión en el historial" en la vista
  comparativa. Una exclusión probada y descartada no ensucia el historial. Guardarla siempre que se simula sería
  cambiar dónde se llama al endpoint, nada más.
- **Quién puede:** solo CU-01. CU-02 no tiene historial y el botón no aparece.
- **La misma selección no se duplica:** guardar dos veces los mismos índices (en cualquier orden) devuelve la
  exclusión existente.
- **Dónde se ve:** en el detalle del historial, el bloque "Exclusiones guardadas" con la fecha y los años de cada una,
  y dos acciones con el mismo peso: "Ver" (carga la selección en el panel y recalcula la comparación) y "Quitar". En la
  lista del historial, la etiqueta "N exclusiones guardadas" (`GET /history/` lleva solo la cantidad).

### Cómo convive con la DECISIÓN 062

"Explorar no es decidir" sigue en pie: guardar, ver o quitar una exclusión **no modifica** `etapa1`, `etapa2` ni
`decisiones`. El resultado registrado sigue siendo el del análisis, con las decisiones que se tomaron durante el
stream. Lo que cambia es que la exploración ya no se pierde: queda guardada al lado, rotulada como exploración. Un test
de integración lo verifica comparando el registro antes y después de guardar y de quitar.

### Contrato

- `POST /api/v1/history/{id}/exclusiones` — cuerpo `{"indices_excluidos": [3, 13]}`. JWT y pertenencia: 404
  `ANALYSIS_NOT_FOUND` si el análisis no existe o no es del usuario. Índices vacíos, fuera de rango, repetidos o que
  vacían la serie, o un análisis sin la serie analizada registrada: 400 `CONTRACT_EXCLUSION_INVALID`. Responde la
  entrada creada (o la existente).
- `DELETE /api/v1/history/{id}/exclusiones/{exclusion_id}` — misma autenticación y pertenencia; 404
  `ANALYSIS_EXCLUSION_NOT_FOUND` (código nuevo) si el análisis es del usuario pero no tiene esa exclusión.
- `GET /history/{id}` suma `exclusiones` (`[]` si no hay); `GET /history/` suma `exclusiones_guardadas`.

### Consecuencias

- La migración `006` hay que correrla en cada entorno (`alembic upgrade head`), incluido el servidor de la UCC: nada
  la corre al arrancar.
- Los análisis anteriores quedan con la lista vacía (sin backfill), igual que `timestamps` (DECISIÓN 058 §4).
- Tests: `tests/integration/db/test_exclusiones_guardadas.py` (guardar, listar, quitar, no duplicar, bordes VL-09 y
  VL-10, pertenencia también por HTTP, resultado y decisiones intactos), `test_analysis_service_archive.py`;
  `ResultsPage.simulacion.test.tsx`, `HistoryDetailPage.simulacion.test.tsx`, `HistoryPage.test.tsx`.

### Relación con otras decisiones

- **DECISIÓN 062** — "explorar no es decidir": sigue vigente; revisión del 21/10/2026 en ese archivo.
- **DECISIÓN 071** — la simulación de exclusión, ahora también desde el historial y con exclusiones guardadas;
  revisión del 21/10/2026 en ese archivo.
- **DECISIÓN 048** — mismo criterio de pertenencia (404 a un análisis ajeno, sin revelar si existe).
