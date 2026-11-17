# DECISIÓN 040 — SSE sobre fetch para el stream de Etapa 1
**Fecha:** 22 de Julio de 2026 (tomada) — promovida a `docs/decisiones/` el 29 de Julio de 2026
**Estado:** Implementado — verificado contra backend real (ver P5 en `frontend-implementation-plan.md` §10)

### Contexto
`POST /api/v1/analysis/stream` es `multipart/form-data` — sube un archivo junto con
el resto de los campos de configuración. El `EventSource` nativo del navegador
**solo soporta GET y no permite headers ni body**, por lo que no puede usarse para
este stream tal como está diseñado el endpoint (`architecture.md` — "SSE sobre
WebSockets para el stream del pipeline" ya fijó SSE como el mecanismo, pero no
resolvía cómo consumirlo desde un POST con archivo).

### Opciones evaluadas
1. **`fetch()` + `ReadableStream`** (`response.body.getReader()`), decodificando
   UTF-8 y parseando a mano los frames `event:`/`data:` separados por `\n\n`.
   Cero dependencias nuevas, pero reimplementa buffering de frames y reconexión a
   mano — superficie de bugs no trivial (frames partidos entre chunks, reconexión
   tras corte de red).
2. **`@microsoft/fetch-event-source`** — librería que encapsula exactamente ese
   patrón (fetch con body + parseo SSE + reconexión configurable).

### Decisión
Se usa `@microsoft/fetch-event-source` para no reimplementar el buffering de
frames SSE a mano. El reader manual (opción 1) queda como fallback documentado en
`frontend-implementation-plan.md` §2.3 por si se decide eliminar la dependencia
más adelante — no descartado, solo no elegido hoy.

Implementado en `frontend/src/api/sse.ts`, hook `useAnalysisStream`. Esta decisión
atraviesa toda la capa de streaming: el manejo de eventos (`onopen`/`onmessage`/
`onclose`/`onerror`), la pausa ante atípico de Chow, y la re-ejecución tras
`resolveOutlier`.

### Verificación
Corrido de punta a punta contra el backend real (Docker) con un CSV sintético de
40 años, incluido un atípico forzado — el modal de Chow real pausó el stream, y
`resolveOutlier("rechazar")` desbloqueó correctamente la `iteracion:2`. Dos bugs
reales de `useAnalysisStream` aparecieron en esa verificación (no relacionados con
la elección de librería en sí, sino con el manejo de eventos de la capa propia):
`complete` pisando una `fase="error"` previa, y `result_etapa1` sin desenvolver
correctamente el payload crudo del evento. Ambos corregidos con test de regresión
en `sse.test.ts` — detalle completo en
`docs/frontend/frontend-implementation-plan.md` §10, pendiente P5.

**Ver también:** [DECISIÓN 039](decision039.md) — criterio de promoción que trajo
esta decisión (originalmente "D1") a `docs/decisiones/`.
