# DECISIÓN 041 — Estado de servidor sin TanStack Query; `vi.stubGlobal("fetch")` como patrón único de test
**Fecha:** 22-28 de Julio de 2026 (tomadas) — promovidas y cerradas el 29 de Julio de 2026
**Estado:** DIFERIDO (TanStack Query) — condicionado a un criterio explícito, no abierto sin fecha; ESTABLECIDO (patrón de test único)

### Contexto
`frontend-implementation-plan.md` §1.1 (tabla de stack, 22/07/2026) fijaba
**TanStack Query** para el estado de servidor de REST (`/me`, `/history`,
`/analysis/{id}`), dejando el stream SSE fuera por ser un hook propio. Al arrancar
Fase 1 (Auth, 28/07/2026) se tomó la decisión D4: no sumarla todavía —
`AuthProvider` usa `fetch` + `useState`/`useEffect` simple, con la promesa
explícita de que *"React Query se suma recién en Fase 4, cuando `/history` lo
justifique más"*.

### Diagnóstico confirmado
Fase 4 (Historial) se implementó el 28/07/2026 y **la promesa no se cumplió**.
Verificado en esta pasada:
- `frontend/package.json` no lista `@tanstack/react-query` ni `react-query` entre
  dependencias ni devDependencies.
- `frontend/src/routes/history/HistoryPage.tsx` usa
  `useState`+`useEffect`+`fetch` plano — mismo patrón que `AuthProvider`, sin
  caching, sin invalidación, sin deduplicación de requests.
- Nadie señaló el incumplimiento hasta esta auditoría — la promesa quedó
  encapsulada en una nota de decisión que nadie volvió a leer al cerrar Fase 4.

En paralelo, D5 (28/07/2026, Fase 1) fijó que los tests de Auth siguen el patrón
ya establecido antes de esa fase (`vi.stubGlobal("fetch", ...)`, visto en
`ping.test.ts`/`useBackendPing.test.tsx`), no MSW — con la intención explícita de
que D3 (MSW) siguiera en pie para cuando Fase 5 lo necesitara de verdad. Al llegar
Fase 5 (Mocks de Etapa 2, 28/07/2026), D20 confirmó la misma elección para
`DesignEventsPage.test.tsx`: se evaluó `setupServer` de `msw/node`, pero comparte
el mismo slot global (`fetch`) que `vi.stubGlobal` — mezclar ambos interceptores
en el mismo archivo de test arriesga un conflicto real sin aportar más confianza.

### Decisión — TanStack Query
No se agrega en esta pasada ni se descarta de forma permanente por decreto. Se
diferee formalmente, mismo patrón que [DECISIÓN 033](decision033.md) usó para el
bump de FastAPI/Starlette — un trigger concreto y verificable, no "cuando lo
justifique más":

**Se reevalúa cuando se cumpla, al menos, una de estas dos condiciones:**
1. Más de una pantalla necesita el mismo dato de servidor simultáneamente con
   invalidación cruzada real (ej. una acción en `ConfigPage` que debería invalidar
   el `/history` ya cacheado en otra pestaña/pantalla) — hoy cada pantalla pide su
   propio dato una vez, sin necesidad de sincronización entre ellas.
2. Etapa 2 se cablea contra un backend real (ver [DECISIÓN 042](decision042.md)) y
   `RankingPage`/`DesignEventsPage`/`ResultsPage` empiezan a compartir estado de
   servidor que hoy es 100% mock local sin red de por medio.

Mientras ninguna se cumpla, `fetch`+`useState`/`useEffect` sigue siendo la elección
correcta — agregar una dependencia nueva sin un consumidor real que la necesite
contradice el criterio de mínima superficie que el propio proyecto aplica en otros
lados (`constraints.md`, "no cambiar el stack sin consultar").

`frontend-implementation-plan.md` §1.1 se marca como derogado en ese punto
específico, con referencia a esta decisión (ver [DECISIÓN 039](decision039.md) y
la actualización de §1.1/§3.1 del plan en esta misma pasada).

### Decisión — patrón único de test (`vi.stubGlobal("fetch")`)
**Establecida, no diferida.** Toda la suite de tests de red usa
`vi.stubGlobal("fetch", ...)` — MSW se reserva exclusivamente para lo que
`vi.stubGlobal` no puede dar: un humano navegando la pantalla mock en el navegador
de dev real, sin tooling especial. Ningún archivo de test mezcla ambos
interceptores. Esto deroga la intención original de `frontend-implementation-plan.md`
§9.1 ("MSW se reutiliza en los tests") — derogación registrada ahí mismo con
referencia a esta decisión.

### Criterio de hecho
- `frontend/package.json` no lista TanStack Query — confirmado arriba.
- Ningún archivo de test bajo `frontend/src/` importa `msw/node` junto con
  `vi.stubGlobal("fetch", ...)` en el mismo archivo.
- `frontend-implementation-plan.md` §1.1 y §9.1 marcan ambos puntos como
  derogados, con el texto original conservado y la referencia a esta decisión.

**Ver también:** [DECISIÓN 039](decision039.md) — criterio de promoción (D4, D5 y
D20 se unifican acá porque las tres versan sobre la misma pregunta: qué mecanismo
de estado/mock usa la suite, y por qué no el "default" del stack original).
[DECISIÓN 033](decision033.md) — precedente directo del formato "diferido con
criterios explícitos".
