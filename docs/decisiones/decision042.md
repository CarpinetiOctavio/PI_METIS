# DECISIÓN 042 — Alcance de los mocks de Etapa 2 y rol de MSW
**Fecha:** 22 y 28 de Julio de 2026 (tomadas) — promovida el 29 de Julio de 2026
**Estado:** ~~Implementado — verificado manualmente en navegador de dev~~ **SUPERADA 09/08/2026 — ver addendum**

### Addendum 09/08/2026 — Etapa 2 dejó de ser mock (Bloque B del plan de Etapa 2)
Con el backend cableado de punta a punta (Bloque A) y el frontend real
implementado en el mismo commit que agrega este addendum, los dos gaps que
motivaban esta decisión ya no existen: `result_etapa2_ranking` y
`result_etapa2_eventos` son eventos SSE reales que el backend emite de
verdad (DECISIÓN 052), no una fabricación de MSW. En consecuencia:

- `frontend/src/mocks/` se borró por completo (`handlers.ts`,
  `etapa2.mock.ts`, `designEvents.mock.ts`, `browser.ts`, `PendingBadge.tsx`)
  — MSW no tiene ningún handler real que sostener sin ellos, y `PendingBadge`
  no tiene ninguna pantalla mock que marcar.
- `RankingPage`/`DesignEventsPage` como rutas separadas se retiraron —
  la pausa de Etapa 2 ahora se resuelve **dentro** de `StreamPage`, mismo
  mecanismo que la pausa de Chow (ver la pregunta de arquitectura resuelta
  con Kevin antes de este bloque: todo dentro del stream, sin navegar).
  `Etapa2RankingView`/`Etapa2EventosView` (`routes/results/`) son los
  componentes de presentación reales, reusados en modo interactivo
  (`StreamPage`) y de solo lectura (`ResultsPage`, `HistoryDetailPage`).
- `msw` sale de `package.json` — sin ningún handler que ejecutar, no hay
  razón para mantener la dependencia.
- El botón "Exportar PDF" de `DesignEventsPage` (mencionado en la decisión
  original) se perdió junto con la pantalla — no se reimplementó en ningún
  lado en este bloque; sigue pendiente (FE-14 / exportación PDF, fuera del
  alcance del Bloque B, ver Bloque E del plan de Etapa 2).

Esta decisión se conserva completa abajo, sin reescribir, por trazabilidad
de por qué los mocks existieron y cómo estaban armados — igual criterio que
el resto de `docs/decisiones/`.

### Contexto
Etapa 2 (ranking de distribuciones por EEA, eventos de diseño) no está cableada
del lado del backend — `sprint.md` la documenta como fuera de alcance del sprint
actual. El frontend necesitaba mostrar esas dos pantallas igual (son parte de las
8 ★ de CU-01/CU-02) para que el flujo completo sea navegable en la defensa, sin
fabricar la impresión de que Etapa 2 está integrada de verdad.

D3 (22/07/2026) fijó la estrategia general: **MSW (Mock Service Worker)**
intercepta las rutas no implementadas y sirve datos de `mocks/*.mock.ts` como si
fueran el backend — los componentes llaman al cliente real sin saber que la
respuesta es falsa, y el día que el endpoint exista de verdad "solo se quita el
handler de MSW, sin tocar componentes ni cliente".

### Diagnóstico confirmado — por qué D3 no se aplicó igual a las dos pantallas
Al implementar Fase 5 (28/07/2026, D19) se encontró una asimetría real entre los
dos gaps de Etapa 2:

- **`design-events` tiene contrato REST documentado** — `POST
  /api/v1/analysis/design-events` existe en `api-contracts.md`, aunque no
  implementado en el backend. MSW interceptándolo es fiel a D3 tal como estaba
  escrita: hay una URL real que mockear.
- **El ranking nunca tuvo un endpoint REST documentado.** Solo aparece como
  evento SSE `result_etapa2_ranking` dentro del mismo stream de Etapa 1
  (`statistical-pipeline.md`) — evento que el backend nunca emite porque Etapa 2
  no está cableada del lado del servidor. Inventar una URL para que MSW la
  intercepte habría fabricado un contrato que no existe en ningún documento del
  proyecto.

### Decisión
- `frontend/src/mocks/handlers.ts` (MSW) intercepta únicamente `POST
  /api/v1/analysis/design-events`, sirviendo `mocks/designEvents.mock.ts`.
- `RankingPage` importa `mocks/etapa2.mock.ts` **directo**, sin capa de red de por
  medio — no hay handler de MSW para el ranking porque no hay contrato que
  mockear con fidelidad. Esta es la única desviación real de D3 tal como estaba
  escrita originalmente, y queda documentada acá en vez de silenciosa.
- Ambas pantallas llevan `PendingBadge` ("pendiente · datos de ejemplo") visible,
  para que en la defensa quede explícito qué es real y qué es maqueta —
  `frontend-implementation-plan.md` §6 documenta el mapeo completo de gaps
  mockeados (ranking, design-events, exportación PDF, `cramer_particion` custom,
  campos descriptivos extendidos).
- Botón "Exportar PDF" ubicado solo en `DesignEventsPage`, visible únicamente si
  `isAuthed` (CU-02 anónimo y CU-03 no exportan) — no repetido en `ResultsPage` ni
  `HistoryDetailPage`.

MSW se usa exclusivamente en el navegador de dev, no en los tests — ver
[DECISIÓN 041](decision041.md) para esa parte (D20).

### Verificación
Verificado manualmente en el navegador de dev (única fase de este backlog que no
depende de un backend real corriendo, porque Etapa 2 es 100% mock por diseño):
flujo Ranking→"Elegir"→Design Events, con `POST
/api/v1/analysis/design-events` interceptado por MSW (confirmado en Network:
`200 OK` sin ningún backend corriendo), chips de período de retorno cambiando el
valor mostrado, badge de "pendiente" visible en ambas pantallas.

### Criterio de hecho
- `frontend/src/mocks/handlers.ts` no define un handler para el ranking.
- `RankingPage.tsx` importa `etapa2.mock.ts` directamente, no via `fetch`.
- `PendingBadge` presente y visible en `RankingPage` y `DesignEventsPage`.

**Ver también:** [DECISIÓN 039](decision039.md) — criterio de promoción.
[DECISIÓN 037](decision037.md) — el gap de backend real (Etapa 2 no cableada) que
motiva estos mocks en primer lugar.
