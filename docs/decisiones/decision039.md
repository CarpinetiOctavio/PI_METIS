# DECISIÓN 039 — Criterio de promoción de las decisiones de frontend y unificación de numeración
**Fecha:** 29 de Julio de 2026
**Estado:** ESTABLECIDA

### Contexto
La sesión de implementación de Fases 1-5 del frontend (28-29/07/2026) tomó 20
decisiones de diseño (`D1`-`D20`), registradas únicamente en
`docs/frontend-implementation-plan.md` §10 — sin número global, sin estado, sin
entrada en `docs/decisiones/README.md`. `docs/decisiones/` fija la convención del
proyecto: un archivo por decisión, número inmutable, entrada en el índice. Esa
sesión no la siguió para el trabajo de frontend.

### Diagnóstico confirmado
Verificado leyendo `frontend-implementation-plan.md` §10 completo: de las 20, no
todas son decisiones de arquitectura — varias son notas de implementación sobre
cómo quedó armada una pantalla puntual (ej. D8 fidelidad de markup del prototipo,
D11 agrupación del timeline en 4 bloques, D12 botón manual "Ver resultados", D15
`<details>` vs. tarjetas siempre abiertas). Migrar las 20 a `decisionNNN.md`
inflaría el índice con contenido que no restringe nada fuera de la pantalla donde
vive.

### Criterio de promoción
Se promueve a `decisionNNN.md` lo que **restringe decisiones futuras o
contradice un documento vigente del repo**. Lo que solo describe cómo quedó
implementada una pantalla se queda como nota de implementación en el plan, con
prefijo `FE-NN` (ver [DECISIÓN 039 — B2](#unificación-de-numeración) más abajo).

### Promoción aplicada

| Del plan | A | Motivo |
|---|---|---|
| D1 | [DECISIÓN 040](decision040.md) | Decisión técnica central de todo el streaming (`@microsoft/fetch-event-source` sobre `EventSource` nativo, que no soporta POST/body/headers) — condiciona la librería y el manejo de errores de toda la capa SSE. |
| D4 + D5 + D20 | [DECISIÓN 041](decision041.md) | D4 contradice su propia promesa en `§1.1` del plan ("TanStack Query recién en Fase 4") — Fase 4 pasó sin agregarla. Define el patrón de testing de toda la suite (`vi.stubGlobal("fetch")` como mecanismo único, D5+D20 explícitamente lo prefieren sobre MSW-en-tests para no correr dos interceptores de red en simultáneo). |
| D3 + D19 | [DECISIÓN 042](decision042.md) | Define qué es mock y qué es real en Etapa 2 — MSW intercepta `design-events` (tiene contrato REST documentado) pero no el ranking (nunca tuvo endpoint REST, solo evento SSE no emitido). Relevante para la defensa ante el tribunal: hay que poder decir con precisión qué del sistema es dato real y qué es maqueta. |
| D2, D6-D18 (el resto) | quedan en el plan | Notas de implementación — renombradas de `D-N` a `FE-N` (ver más abajo), sin archivo propio. |

### Unificación de numeración
Antes de esta pasada convivían, con aspecto idéntico y significados distintos:
- `DECISIÓN 001`-`035` — convención de `docs/decisiones/`.
- `D1`-`D20` — `frontend-implementation-plan.md` §10.
- `Decisión A` / `Decisión C` / `Decisión D` — `frontend-design/metis-wireframes-fase1-decisiones.md`.

El código las mezclaba sin distinguirlas (`sse.ts` citando "Decisión D1" y
`ConfigPage.tsx` citando "Decisión D" para cosas completamente distintas — una del
plan de implementación, otra de los wireframes de diseño).

**Prefijos adoptados, sin ambigüedad:**
- `DECISIÓN NNN` — decisiones del repo en `docs/decisiones/` (sin cambios).
- `FE-NN` — notas de implementación del plan de frontend que no se promovieron
  (`D2`, `D6` a `D18`, conservando su número original con el nuevo prefijo: `FE-2`,
  `FE-6`...`FE-18`).
- `UX-A`..`UX-D` — decisiones de `frontend-design/metis-wireframes-fase1-decisiones.md`.

### Tabla de equivalencia D1..D20 → destino final

| Original | Destino |
|---|---|
| D1 | DECISIÓN 040 |
| D2 | FE-2 (plan §10, nota de implementación) |
| D3 | DECISIÓN 042 |
| D4 | DECISIÓN 041 |
| D5 | DECISIÓN 041 |
| D6 | FE-6 |
| D7 | FE-7 |
| D8 | FE-8 |
| D9 | FE-9 |
| D10 | FE-10 |
| D11 | FE-11 |
| D12 | FE-12 |
| D13 | FE-13 |
| D14 | FE-14 |
| D15 | FE-15 |
| D16 | FE-16 |
| D17 | FE-17 |
| D18 | FE-18 |
| D19 | DECISIÓN 042 |
| D20 | DECISIÓN 041 |

Las cinco referencias de código que citaban el esquema viejo (`sse.ts`,
`ConfigPage.tsx`, `Etapa1ResultView.tsx`, `ResultsPage.tsx`, `EntryPage.tsx`) y las
referencias cruzadas dentro de `frontend-implementation-plan.md` se actualizan al
prefijo nuevo en el mismo commit que esta decisión (ver Bloque B2 del plan de esta
pasada).

### D4 — la promesa de TanStack Query, resuelta
D4 (22/07/2026) prometía explícitamente: *"React Query se suma recién en Fase 4,
cuando `/history` lo justifique más"*. Fase 4 (Historial) se implementó
(28/07/2026) y **no se agregó** — verificado: `frontend/package.json` no lista
`@tanstack/react-query` ni `react-query`, y `HistoryPage.tsx` usa
`useState`+`useEffect`+`fetch` plano, igual que `AuthProvider`. La promesa quedó
incumplida sin que nada lo señalara.

**Resuelto en [DECISIÓN 041](decision041.md):** no se descarta TanStack Query de
forma permanente por decreto, pero se diferee formalmente con criterios explícitos
de habilitación — mismo patrón que [DECISIÓN 033](decision033.md) usó para el bump
de FastAPI/Starlette. Ningún trigger informal ("cuando lo justifique más") sin
fecha ni condición verificable.

### Criterio de hecho
- `decisiones/README.md` indexa 036-042 con su título y estado real (no `EN CURSO`
  genérico).
- `grep -rn "Decisión D" frontend/src` devuelve cero coincidencias, o solo
  coincidencias con el prefijo nuevo (`UX-D`, `FE-NN`).
- `frontend-implementation-plan.md` §10 usa `FE-NN` para D2/D6-D18 y referencia
  `DECISIÓN 040/041/042` para D1/D3/D4/D5/D19/D20, sin duplicar el contenido ya
  promovido.

**Ver también:** [DECISIÓN 040](decision040.md), [DECISIÓN 041](decision041.md),
[DECISIÓN 042](decision042.md) — las tres decisiones promovidas por esta.
