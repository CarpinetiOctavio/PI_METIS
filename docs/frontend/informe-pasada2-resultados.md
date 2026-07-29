# Informe de Resultados — Pasada 2 de Mejora sobre el Frontend

**Fecha.** 29 de Julio de 2026.
**Alcance ejecutado.** `docs/frontend/plan-mejora-frontend-pasada2.md`, Bloques A a E completos, en el
orden que el propio plan sugiere.
**Rama.** `fix/frontend-pasada2` (creada desde `staging` — `staging` no admite commits directos,
`constraints.md`). 18 commits, uno por punto lógico, siguiendo la granularidad que el plan pedía en
varios puntos (ej. `.gitattributes` aislado, un commit por decisión).
**Propósito de este documento.** Punto único de retoma de esta pasada — igual que
[`informe-implementacion-frontend-fase1-6.md`](./informe-implementacion-frontend-fase1-6.md) lo es
de la sesión anterior.

---

## 0. Resultado por ítem

Ninguno omitido — un ítem descartado con motivo es un resultado válido, uno que desaparece del
informe no.

### Bloque A — Hallazgos de backend sin registrar

| # | Estado | Resultado |
|---|---|---|
| A1 | Hecho | [DECISIÓN 036](../decisiones/decision036.md) — partición de Cramer personalizada inalcanzable (`Form(str)` vs. indexado `dict`). Documentado, no implementado (fuera de alcance de esta pasada). `ConfigPage.tsx`, `sprint.md`, `api-contracts.md` actualizados. |
| A2 | Hecho | [DECISIÓN 037](../decisiones/decision037.md) — `etapas` se recibe y se descarta, `AnalysisRequest` es código muerto. Documentado, prioridad marcada para M2/M3. |
| A3 | Hecho | [DECISIÓN 038](../decisiones/decision038.md) — catálogo de errores como fuente única. 3 códigos backend→catálogo agregados (`TEST_NOT_EXECUTED_MIN_SAMPLES`, `PARSE_ERROR`, `SESSION_TIMEOUT`, sección nueva "Stream / sesión"), 4 catálogo→`errors.es.ts` agregados. Gap real encontrado *durante* la verificación reproducible (no solo asumido): `TEST_NOT_EXECUTED_MIN_SAMPLES` se había agregado al catálogo pero no a `errors.es.ts` en el primer paso — corregido antes de cerrar la decisión. Asimetría real documentada (no corregida — `core/` fuera de alcance): `trend.py` no promueve `TEST_WARNING_SMALL_SAMPLE` de Mann-Kendall a `result.warnings` como sí hace `independence.py` con Wald. |

### Bloque B — Reintegración de las decisiones de frontend

| # | Estado | Resultado |
|---|---|---|
| B0 | Hecho | 035-042 reservados en el índice antes de escribir contenido. 035 permanece reservado (GitHub Ruleset, sprint.md 20/07), sin tocar. |
| B1 | Hecho | [DECISIÓN 039](../decisiones/decision039.md) — criterio de promoción + tabla de equivalencia D1..D20 completa. D1→040, D4+D5+D20→041, D3+D19→042. La promesa incumplida de D4 (TanStack Query "en Fase 4") cerrada formalmente en 041, diferida con criterio explícito de habilitación (mismo patrón que 033), no descartada por decreto. |
| B2 | Hecho | Prefijos `DECISIÓN NNN` / `FE-NN` / `UX-A..D` aplicados. 5 referencias de código actualizadas (`sse.ts`, `ConfigPage.tsx`, `EntryPage.tsx`, `Etapa1ResultView.tsx`, `ResultsPage.tsx`) + todas las referencias cruzadas de `frontend-implementation-plan.md` §10. `metis-wireframes-fase1-decisiones.md` (la fuente de "Decisión de arquitectura A-D") **no se tocó** — es el documento autoral, `UX-A..D` es la forma abreviada que usan los demás documentos al citarlo, no un renombre del original. |
| B3 | Hecho | `frontend/frontend-design/` commiteado completo, incluido `versiones/` (9 archivos históricos) — decisión de Kevin, opción 1 del plan. |

### Bloque C — Documentos de verdad desactualizados

| # | Estado | Resultado |
|---|---|---|
| C1 | Hecho | `CLAUDE.md` — sección Frontend completada: auth end-to-end, SSE real, 3 modos de resultados, historial, Etapa 2 mock con `PendingBadge`, estado real de la verificación E2E (registro→verify es el único tramo bloqueado). |
| C2 | Hecho | `sprint.md` — sección `feature/frontend-fases1-5 — COMPLETA` con detalle por fase (mismo nivel que `feature/core-etapa2`). Contradicción "Frontend fuera de alcance" tachada, no borrada. Colisión "Fase N" (Core Etapa 2 vs. frontend) resuelta exigiendo "Fase N del frontend" en menciones nuevas. Nota del 29/07 sobre inserción de usuario en Postgres, mal etiquetada como "(Fase 6...)", corregida a "backlog P4-P7, fuera de las 6 fases nominales". |
| C3 | Hecho | `sprint.md`, M1 — "Verificación end-to-end del pipeline con CSV real" cerrada con `ACTUALIZACIÓN 29 de Julio de 2026` (mismo formato que las entradas de Auth Parte 2). De los 3 criterios originales de M1 quedan 2 pendientes (regresión matemática, registro→verify). |
| C4 | Hecho | `docs/README.md` — estructura actualizada (`decisiones/` 001-042), historial al día. `docs/frontend/` creado agrupando los 4 documentos — pregunta explícita a Kevin antes de ejecutar (no unilateral), respondida "sí, agrupar". |
| C5 | Hecho | `frontend-implementation-plan.md` §1.1/§3.1/§9.1 — TanStack Query, Prettier, CSS Modules y MSW-en-tests marcados `DEROGADO` con tachado + referencia a la decisión que deroga cada uno (texto original conservado). Pendiente P2 (puerto Vite) cerrado — resuelto desde Fase 0, listado como abierto por error. |
| C6 | Hecho | `frontend/README.md` reescrito: estructura real de `src/`, patrón de testing único (`vi.stubGlobal`), nota de Etapa 2 mock con `PendingBadge`. |
| C7 | Hecho — **la premisa del plan era incorrecta.** `.claude/launch.json` no es "probablemente inerte" ni convención de VS Code: es la config real que lee la herramienta de preview de navegador de Claude Code (`preview_start`) para levantar el dev server. Documentado en `frontend/README.md` en vez de eliminado. |

### Bloque D — Correcciones de código

| # | Estado | Resultado |
|---|---|---|
| D1 | Hecho | `sse.ts` — `onerror` y el evento `error` genérico usan `errorText(codigo)` siempre, nunca `mensaje` crudo del backend (inconsistente: técnico en `PARSE_ERROR`, curado en `SESSION_TIMEOUT`). Test existente actualizado para reflejar el comportamiento nuevo (era la aserción del comportamiento viejo, no una regresión). |
| D2 | Hecho | `StreamPage.tsx` — `abort()` en cleanup de `useEffect`. Test de regresión nuevo. |
| D3 | Hecho | `src/i18n/format.ts` nuevo (`formatNum`/`formatInt`) aplicado a todo `className="num"` en `Etapa1ResultView.tsx` y `StreamPage.tsx`. Criterio documentado: 4 decimales, misma precisión (`abs=1e-4`) que usan los tests de regresión matemática del backend — no elegido al azar. |
| D4 | Hecho | `sse.ts` `resolveOutlier` — lee `outlier` vía un ref sincronizado (`internalRef`) en vez de depender de `internal` completo. `useCallback` con deps `[]`, ya no se recrea en cada evento SSE. |
| D5 | Hecho | `RankingPage.tsx` — extraído `RankingCard` con estado `axis` propio; antes una tarjeta cambiaba las ocho. Test de regresión nuevo confirmó el bug antes del fix. |
| D6 | Hecho | `Etapa1ResultView.tsx` `GroupTable` — ya no renderiza el literal `"n2=null"` cuando solo uno de los dos está presente. |
| D7 | Hecho | `guards.tsx` — spinner mínimo (`role="status"`, tokens de Instrumento) en vez de `null` durante `isLoading`. Test de regresión nuevo. |
| D8 | Hecho | `AuthProvider.tsx` `logout()` — limpia `localStorage["metis-anon-session"]` residual. Test de regresión nuevo. |
| D9 | Hecho — **documentado, sin cambio de comportamiento.** Verificado que el límite crit/warn de `summarizeGroup` ya coincidía con "Anderson manda"/"Cramer manda" (`warning_nivel="critico"` solo lo produce la prueba dominante en `core/etapa1/{independence,homogeneity}.py`). "warn" es intencional cuando una prueba no dominante trae una nota de nivel "normal" documentado — no un bug. Razonamiento completo dejado como comentario en el código. |
| D10 | Hecho | Modal de atípico: `role="dialog"`/`aria-modal` movidos de backdrop al diálogo real. Resto de la página `inert`+`aria-hidden` mientras el modal está abierto. `PendingBadge` — la nota ya no depende solo de `title`, también es texto real (`.visually-hidden`). Focus trap/auto-foco/Escape quedan fuera de esta pasada (pendientes heredados de Fase 6, no en el alcance de D10). |
| D11 | Hecho — **documentado, no aplicado.** Auditoría real de contraste WCAG (fórmula de luminancia, no estimado) sobre los 21 pares texto/fondo de `tokens.instrumento.css`, incluidos los fondos `color-mix()` reales de los banners. Dos hallazgos reales: `--fnt` falla en ambos modos, `--ok`/`--warn`/`--crit` como texto de banner fallan solo en modo claro. Propuesta concreta calculada (mismo tono, oscurecido/aclarado al mínimo) registrada en `sprint.md` — no aplicada a los tokens, es identidad visual fijada. |

### Bloque E — Requería confirmación de Kevin

| # | Estado | Resultado |
|---|---|---|
| E1 | Hecho | `git status` en esta máquina (Windows) vino limpio — confirmado que el reporte de 212 archivos modificados era artefacto de leer el checkout desde Linux. `.gitattributes` (`* text=auto` + excepciones binarias) agregado en commit aislado, con decisión de Kevin. |
| E2 | Hecho | Mismo resultado que B3 — frontend-design/ completo, decisión de Kevin. |
| E3 | Hecho | Mismo resultado que C4 — `docs/frontend/`, decisión de Kevin. |

**Números de decisión:** coinciden exactamente con la propuesta de B0 — 036 (A1), 037 (A2), 038 (A3),
039 (B1), 040 (D1 del plan viejo), 041 (D4+D5+D20 del plan viejo), 042 (D3+D19 del plan viejo). Sin
desvíos.

**Hallazgos nuevos durante la pasada** (ninguno contradice un documento vigente lo bastante como para
ameritar una decisión nueva más allá de las ya creadas):
- El gap de `TEST_NOT_EXECUTED_MIN_SAMPLES` faltante en `errors.es.ts` (encontrado y corregido dentro
  de A3, ver arriba — no una decisión aparte, es el contenido mismo de 038).
- La premisa incorrecta del plan sobre `.claude/launch.json` (C7, arriba).
- Un bug real de rules-of-hooks introducido y corregido en el propio proceso de implementar D10
  (`useRef`/`useEffect` después de un `return null` condicional) — atrapado por ESLint antes de
  commitear, nunca llegó a la rama en estado roto. Mencionado acá por transparencia, no por ser un
  hallazgo sobre el código preexistente.

---

## 1. Verificación final — salida real

### Frontend
```
$ npm run lint
> eslint .
(sin salida — limpio)

$ npm test
Test Files  22 passed (22)
     Tests  123 passed (123)
(119 antes de esta pasada + 4 tests de regresión nuevos: D2, D5, D7, D8)

$ npm run build
✓ 77 modules transformed.
dist/index.html                  0.43 kB
dist/assets/index-*.css          9.67 kB
dist/assets/index-*.js         244.91 kB
✓ built in 793ms
```

### Backend
```
$ ruff check metis/
All checks passed!

$ ruff format --check metis/
64 files already formatted

$ pytest -m unit -v
```
**No se pudo ejecutar.** El Python de esta máquina (`C:/msys64/ucrt64/bin/python3.exe`) no tiene
instaladas las dependencias del proyecto (`sqlalchemy`, `aiosmtplib` ausentes — `pip show` lo
confirma, no hay `venv` en el repo). Es una brecha de entorno preexistente, no introducida por esta
pasada: **ningún archivo `backend/metis/*.py` se tocó** en todo este trabajo (alcance 100%
documentación + frontend), así que no hay riesgo real de regresión de backend sin verificar — pero
la ejecución real de `pytest` queda pendiente de un entorno con las dependencias instaladas (o
`docker-compose`, que es como el resto de este repo verifica el backend según `sprint.md`).

### Chequeo bidireccional de códigos de error (A3 / DECISIÓN 038)
```
$ grep -rhoE '"[A-Z_]+_[A-Z_]+"' backend/metis/core backend/metis/services | tr -d '"' | sort -u \
  | comm -23 - <(grep -oE '^[A-Z_]+' .claude/rules/architecture/api-contracts.md | sort -u)
STATUS_DISABLED_ZEROS
STATUS_NO_APLICABLE
STATUS_NO_CONVERGE
STATUS_OK
```
Las 4 salidas son constantes internas de estado de Etapa 2 (`core/etapa2/types.py`), no códigos de
error de cara al usuario — no es un gap real, es ruido esperado del regex (documentado también en
`decision038.md`).

```
$ grep -oE '^[A-Z_]+' .claude/rules/architecture/api-contracts.md | sort -u \
  | comm -23 - <(grep -oE '^  [A-Z_]+:' frontend/src/i18n/errors.es.ts | tr -d ' :' | sort -u)
A
DIST_DISABLED_ZEROS
DIST_HIGH_EEA
DIST_NOT_APPLICABLE
DIST_NOT_CONVERGED
E
P
```
`DIST_*` son códigos de Etapa 2, todavía no expuestos en el frontend real (ver DECISIÓN 042) —
esperado. `A`/`E`/`P` son ruido del regex sobre párrafos de prosa que empiezan con mayúscula, no
códigos reales.

### Referencias e integridad
```
$ [sweep completo sobre todo *.md del repo, resolviendo cada enlace relativo]
(sin salida — cero enlaces rotos)

$ grep -rn "Decisión D[0-9]\?" frontend/src
(sin salida — cero coincidencias del esquema viejo)

$ git status
On branch fix/frontend-pasada2
nothing to commit, working tree clean
```

---

## 2. Qué queda pendiente

- **Backend:** `pytest -m unit` real, en un entorno con las dependencias instaladas — no se ejecutó
  en esta pasada (ver arriba). Ninguna de las 3 opciones evaluadas en DECISIÓN 036/037 se implementó
  — quedan agendadas.
- **D11:** aplicar (o no) la propuesta de contraste de `tokens.instrumento.css` — decisión de
  Kevin/Octavio, no ejecutada acá.
- **Fase 6 del frontend** (pulido y accesibilidad) sigue parcial — focus trap, auto-foco y cierre con
  Escape del modal de atípico quedan fuera del alcance de D10, tal como los heredó esta pasada.
- Los dos criterios de M1 que ya estaban pendientes antes de esta pasada (regresión matemática,
  registro→verify) siguen exactamente igual — esta pasada no los tocó ni los pretendía tocar.
