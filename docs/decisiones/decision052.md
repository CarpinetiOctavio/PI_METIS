# DECISIÓN 052 — Transporte de Etapa 2 por SSE con pausa; `distribution-decision` reemplaza `design-events`
**Fecha:** 09 de Agosto de 2026
**Estado:** Decidida — implementación en curso (Bloque A del [plan de implementación de Etapa 2](../plan-etapa2-implementacion.md))

### Contexto

El motor de Etapa 2 (`core/etapa2/`, `core/pipeline/pipeline_etapa2.py::ejecutar_etapa2()`)
está completo — 13 distribuciones, cálculo de EEA, ranking — pero desconectado:
`grep -rn "etapa2" backend/metis/api backend/metis/services` no encuentra ninguna
llamada real a `ejecutar_etapa2()`. `.claude/rules/architecture/api-contracts.md`
documenta `POST /api/v1/analysis/design-events` como endpoint sincrónico que
recibe `session_id`, `distribucion`, `metodo` y `periodos_retorno`, y devuelve los
eventos de diseño calculados en la misma respuesta. Ese contrato nunca se
implementó — el router solo tiene `preview-columns`, `stream`,
`outlier-decision` y `{analysis_id}`.

Mientras tanto, el stream de Etapa 1 ya resuelve exactamente este problema para
Chow: pausa el generador SSE, espera una decisión del usuario vía un endpoint
sincrónico aparte, y reanuda. `session_store.py` + `POST
/analysis/outlier-decision` son ese mecanismo, funcionando en producción desde
`feature/services-sse`.

### Diagnóstico

El contrato documentado de `design-events` (sincrónico, devuelve los eventos)
deja de tener sentido en cuanto Etapa 2 se cablea al mismo stream que Etapa 1:
el cliente ya está escuchando un `EventSource`/`fetch`-SSE abierto para ver el
ranking (`result_etapa2_ranking`) antes de poder elegir distribución+método. Si
`design-events` fuera una llamada REST aparte, el flujo tendría dos mecanismos
de transporte distintos para dos pausas del mismo pipeline — una asimetría sin
justificación, y exactamente el tipo de "forma nueva" que
`.claude/rules/architecture/architecture.md` (sección "Mismo endpoint
/analysis/stream para CU-01 y CU-02") advierte no introducir sin necesidad.

### Opciones evaluadas

1. **Mantener `design-events` sincrónico tal como está documentado**, separado
   del stream. Descartada: el cliente necesitaría abrir una segunda conexión
   HTTP fuera del SSE ya abierto, duplicando el estado de sesión (¿qué pasa si
   el stream se cierra mientras esa llamada está en vuelo?) sin ganar nada a
   cambio — Etapa 2 no tiene ningún requisito que Etapa 1 no tenga ya resuelto
   con el mecanismo de pausa existente.
2. **Un mecanismo de pausa nuevo, específico de Etapa 2** (WebSocket, polling,
   long-polling). Descartada por la misma razón que
   `architecture.md` ya usó para rechazar WebSockets en Etapa 1: el pipeline es
   unidireccional salvo por los dos puntos de decisión del usuario, y esos dos
   puntos ya se resuelven con requests sincrónicos separados. Etapa 2 no agrega
   un tercer patrón de interacción, agrega un segundo punto de decisión del
   mismo tipo que Chow.
3. **Etapa 2 replica el mecanismo de pausa de Chow, sin inventar nada nuevo.**
   Elegida.

### Decisión

Etapa 2 se cablea con la misma forma que Etapa 1, no con una forma nueva:

```
… → test_result(chow) → outlier_detected → [PAUSA] → test_result… → result_etapa1 → complete   (Etapa 1, ya existe)

result_etapa1 → progress(etapa 2) → result_etapa2_ranking → [PAUSA] → result_etapa2_eventos → complete   (Etapa 2, esta decisión)
                                              ↑
                    POST /analysis/distribution-decision  →  session_store.resolve_session()
```

Condiciones para entrar a Etapa 2, evaluadas en este orden:

1. `etapas == [1, 2]` (ver [DECISIÓN 054](decision054.md)). Si es `[1]`, el
   stream termina exactamente como hoy — este cambio no altera en absoluto el
   camino de quien no pide Etapa 2.
2. `result_final.nivel_confianza != "rechazado"`. Es el único estado que
   bloquea — con warnings, incluso críticos, Etapa 2 corre igual. Coherente con
   el comportamiento de referencia de la tesis (estación Alpa Corral: rechazo
   unánime de Etapa 1, Etapa 2 se corrió de todos modos) y con el docstring de
   `full_pipeline.py`.

**`POST /api/v1/analysis/design-events` se reemplaza por
`POST /api/v1/analysis/distribution-decision`**, hermano exacto de
`outlier-decision` en forma y mecanismo de desbloqueo:

```
POST /api/v1/analysis/distribution-decision
Request:  {"session_id": "...", "distribucion": "gumbel", "metodo": "momentos",
           "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500]}
Auth:     JWT opcional (igual que el stream activo)
Response: {"ok": true, "pipeline_continua": true}
Errores:  404 SESSION_NOT_FOUND, 400 DIST_SELECTION_INVALID
```

`periodos_retorno` se valida en el borde del endpoint (lista no vacía, todos
`> 1` — `F = 1 - 1/T` necesita `T > 1` para caer en `(0,1)`, máximo 20
elementos), no en `core/`: el guard `p ∈ (0,1)` de `cuantil()` (ver
`tests/unit/core/etapa2/test_cuantil_guard.py`) ya rechazaría un `T` inválido,
pero dejarlo llegar ahí produciría un 500 en vez de un 400 legible.

`api-contracts.md` conserva la entrada de `design-events`, marcada como
**reemplazada por `distribution-decision`**, con el porqué — no se borra, seguí
el mismo criterio de trazabilidad que rige el resto del proyecto.

**Dos códigos de error nuevos:** `SESSION_NOT_FOUND` y `DIST_SELECTION_INVALID`.
Van a `api-contracts.md` **y** a `frontend/src/i18n/errors.es.ts` en el mismo
commit que los introduce — `DIST` y `SESSION` ya son prefijos reconocidos por
`scripts/check-error-catalog.sh:22` (`PREFIXES="AUTH|CONTRACT|TEST|DIST|PARSE|SESSION"`,
verificado contra el script real), así que el job `error-catalog` de CI se pone
rojo si algún lado queda desincronizado. Es la regla que dejó
[DECISIÓN 038](decision038.md).

### Criterio de hecho

- `api-contracts.md` documenta `POST /analysis/distribution-decision` con su
  contrato completo, y `design-events` marcado como reemplazado (no borrado).
- `SESSION_NOT_FOUND` y `DIST_SELECTION_INVALID` presentes en `api-contracts.md`
  y en `frontend/src/i18n/errors.es.ts`.
- `./scripts/check-error-catalog.sh` en verde con los dos códigos nuevos.
- Smoke test manual: `POST /analysis/stream` con `etapas=1,2` emite
  `result_etapa2_ranking`; `POST /analysis/distribution-decision` desbloquea el
  stream y llegan `result_etapa2_eventos` y `complete`.
- Con `etapas=1` el stream se comporta exactamente como antes de esta decisión.

**Ver también:** [DECISIÓN 040](decision040.md) — SSE sobre fetch para el
stream de Etapa 1, el mecanismo de transporte que esta decisión extiende sin
modificar. [DECISIÓN 053](decision053.md) — el `session_store` con estado que
esta decisión necesita para guardar la serie y el `Etapa2Result` antes de
pausar. [DECISIÓN 042](decision042.md) — el mock de `design-events` que esta
decisión deja sin contraparte real que sostener.
