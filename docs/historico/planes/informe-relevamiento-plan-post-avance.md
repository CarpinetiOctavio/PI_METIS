# Informe de relevamiento — Bloque I del plan post-avance

**Fecha:** 19 de Agosto de 2026
**Alcance:** auditoría final de los Bloques A-H3 del [plan post-avance](plan-post-avance.md),
corrida contra `staging` real en `337af68` (merge de PR #74, el último de la
pila), después de que los 12 PRs de código estuvieran mergeados.

**Método.** Para cada bloque: (1) grep/lectura directa del código en
`staging`, no de la memoria de qué PR se abrió; (2) verificación del
encabezado `Estado:` de cada `decisionNNN.md` citado contra el contenido real
del cuerpo del documento; (3) diff exacto entre los archivos `decisionNNN.md`
en disco y las filas de `docs/decisiones/README.md`; (4) re-ejecución de
`scripts/check-error-catalog.sh` y de la suite completa (`pytest -m "unit or
integration"`, `ruff check`/`format --check`, `npm run lint && npm test &&
npm run build`) sobre el estado consolidado.

---

## Tabla bloque por bloque

| Bloque | Qué debía existir | Estado real verificado | Hallazgo |
|---|---|---|---|
| A — Niveles de animación | `MotionProvider`, `useMotion()`, `theme/motion.ts`, tres niveles, DECISIÓN 059 | `frontend/src/theme/{motion.ts,MotionProvider.tsx,MotionProvider.test.tsx}` presentes; `decision059.md` con `Estado: Implementada` | Sin hallazgos |
| B1/B2 — Navegación automática + `StreamPage` sin presentación final | `navigate("/results", { replace: true })`; `Etapa2EventosView` fuera de `StreamPage` | `StreamPage.tsx:230-231` confirma `replace: true`; `Etapa2EventosView` no aparece en `StreamPage.tsx` (grep vacío) | Sin hallazgos |
| B3 — Fix timestamps desalineados | `timestamps_efectivos` filtrado con el mismo índice que la serie; `mes_inicio_anio` propagado a la segunda `ejecutar_etapa1()` | `analysis_service.py:556-589` — `serie_filtrada`, filtro por `enumerate`/`i != indice_real` sobre timestamps, `mes_inicio_anio=mes_inicio_anio` en la segunda llamada | Sin hallazgos |
| B4 — Persistencia si el usuario abandona la pausa | Documentado como pendiente explícito, no como implementado | No implementado — correcto, el plan lo marca como "si no entra en este ciclo, se anota en `pendientes-tecnicos.md`" | Ver nota abajo (Pendiente real, no un hallazgo de auditoría) |
| C2a — `seleccion` persistida | Bloque `seleccion` en `_serializar_etapa2()` | `analysis_service.py:236` — `"seleccion": seleccion` | Sin hallazgos |
| C2b — `decisiones` en `GET /history/{id}` | `get_analysis_by_id()` devuelve `decisiones` | `analysis_service.py:909` — `"decisiones": result.decisiones` | Sin hallazgos |
| C2c — Endpoint stateless de recálculo | `POST /analysis/{id}/design-events` | `api/v1/analysis.py:337` — `@router.post("/{analysis_id}/design-events", ...)` | Sin hallazgos |
| C3 — Historial interactivo | `HistoryDetailPage` con `Etapa2EventosView`, modo `"exploracion"` | `HistoryDetailPage.tsx:149,178-179,198` — `modo="exploracion"`, `onElegir={handleExplorar}` | Sin hallazgos |
| D — Fórmula sustituida | `TestResult.explicacion` en `core/types.py`; renderizado en `Etapa1ResultView` | `core/types.py:39` — `explicacion: Explicacion \| None = None`; consumido en `Etapa1ResultView.tsx` | Sin hallazgos |
| E — Panel acoplable | `data-dock`, `role="separator"`, persistencia `metis-column-panel` | `ConfigPage.tsx:308,637`; `ConfigPage.css:41,48`; tests dedicados en `ConfigPage.test.tsx:493-528` | Sin hallazgos |
| F — Nota de tipo de variable | Nota explicativa bajo el selector, Opción 1 | `ConfigPage.tsx:494-505` — nota exacta con el texto de la Opción 1 recomendada | Sin hallazgos |
| G — Inventario | No genera código, es solo diagnóstico | N/A — no aplica verificación de código | Sin hallazgos |
| H1 — Cramer partición personalizada | `_parsear_cramer_particion()`, `CramerParticionCustom`, guard `n_w1/n_w2 < 2`, UI habilitada | Verificado en la sesión que implementó el bloque (PR #73); re-confirmado por la suite completa en verde sobre `staging` | Sin hallazgos |
| H2 — Contraste WCAG AA | 5 tokens recalculados, `contrast.ts`, `contrast.test.ts` | Verificado en la sesión que implementó el bloque (PR #72); `contrast.test.ts` presente y en verde | Sin hallazgos |
| H3 — Orden cronológico bloqueante | `timestamps_desordenados()`, paso 0a en `ejecutar_etapa1()`, `CONTRACT_WRONG_ORDER` bloqueante | Verificado en la sesión que implementó el bloque (PR #74); re-confirmado por la suite completa en verde sobre `staging` | Sin hallazgos |
| H4 — SonarCloud gate | Configuración manual de GitHub/SonarCloud, no código | No aplica — explícitamente fuera del alcance de una sesión de agente (requiere login humano) | Pendiente real, documentado como tal desde el propio plan |
| H5 — Umbral 5% EEA | Pregunta de dominio para Facundo, no se cierra desde código | Sigue abierta — correcto, el plan la marca así explícitamente | Pendiente real, no un hallazgo de auditoría |

---

## Correcciones aplicadas durante este relevamiento

1. **`docs/decisiones/decision062.md`** — el encabezado `Estado:` decía
   *"Decidida — implementación en curso (Bloque C2c del plan post-avance)"*
   pese a que tanto el backend (Bloque C2c, PR #66) como el frontend (Bloque
   C3, PR #67) estaban completos y mergeados el mismo día. El cuerpo del
   documento ya describía el comportamiento terminado — solo el encabezado
   había quedado atrás. Corregido a *"Aplicada — backend ... y frontend ...,
   ambos mergeados a `staging`"*, con un addendum fechado explicando que es
   una corrección de documentación, no un cambio de comportamiento.
2. **`docs/decisiones/README.md`**, fila de la DECISIÓN 062 — reflejaba el
   mismo estado desactualizado (*"Decidida — implementación en curso"*).
   Corregida a *"Aplicada (backend + frontend)"* para que coincida con el
   archivo fuente.

Ninguna otra decisión citada por el plan (030, 036, 043, 059, 060, 061, 063,
064) tenía un encabezado desincronizado con su propio cuerpo — las ocho se
verificaron una por una y ya decían "Aplicada"/"Implementada"/"Decidida y
aplicada" según corresponda, consistente con el código real.

---

## Verificación de índice — sin huecos ni entradas huérfanas

Comparación exacta entre los 61 archivos `docs/decisiones/decisionNNN.md`
en disco y las 61 filas de `docs/decisiones/README.md`: **coinciden
uno a uno**, sin archivos sin fila y sin filas sin archivo. La colisión de
numeración documentada en el propio plan (060→062→063→064, ver contexto de
`decision062.md`) quedó correctamente resuelta — cada número usado apunta a
un solo archivo, sin duplicados ni saltos sin explicar.

---

## Verificación de documentos transversales

- **`scripts/check-error-catalog.sh`** — corrido sobre `staging` consolidado:
  *"Catálogo de códigos de error sincronizado en las tres direcciones"* —
  backend, `api-contracts.md` y `frontend/src/i18n/errors.es.ts` coinciden
  exactamente, incluidos los códigos nuevos de H1 (`CONTRACT_CRAMER_PARTICION_INVALID`)
  y H3 (`CONTRACT_WRONG_ORDER` movido a bloqueante) y los retirados
  documentados por trazabilidad (`CONTRACT_CRAMER_PARTICION_UNSUPPORTED`).
- **`.claude/rules/architecture/api-contracts.md`** — contiene las secciones
  "Cerrado" de H1 y las entradas de C2c (`POST /analysis/{id}/design-events`,
  DECISIÓN 062) y de `GET /history/{id}` (`decisiones`, `seleccion`).
- **`.claude/rules/core/statistical-pipeline.md`** — documenta el campo
  `explicacion` de Bloque D y no quedó ninguna mención residual de
  `CONTRACT_WRONG_ORDER` como no bloqueante.
- **`CLAUDE.md`** — actualizado en el mismo commit de H3: "dos excepciones
  reales" en vez de "único caso absoluto".

---

## Verificación de la suite completa sobre `staging` consolidado

Corrida en `337af68` (HEAD de `staging` al momento de este informe, incluye
los 12 PRs A-H3):

```
Backend:  pytest -m "unit or integration"  → 338 passed, 1 skipped
          ruff check metis/                → All checks passed!
          ruff format --check metis/       → 66 files already formatted

Frontend: npm run lint                     → sin errores
          npm test -- --run                → 47 test files, 324 tests, todos en verde
          npm run build                    → tsc -b + vite build, sin errores
```

Ninguno de los archivos de test "entregable de verdad" citados por los
bloques individuales (`contrast.test.ts`, `test_stream_cramer_particion.py`,
`test_pipeline_etapa1.py`, `test_contract.py`, `ConfigPage.test.tsx`,
`sse.test.ts`, `test_homogeneity.py`) fue borrado ni marcado `.skip` — los
siete existen y corren como parte de la suite verde de arriba.

---

## Conclusión

De los 17 puntos de la tabla (A, B1/B2, B3, B4, C2a, C2b, C2c, C3, D, E, F,
G, H1, H2, H3, H4, H5), **15 están cerrados y verificados sin hallazgos**, y
los **2 restantes (B4 y H4/H5) son pendientes reales que el propio plan ya
marcaba como fuera del alcance de este ciclo** — B4 requiere una decisión de
producto propia (cuándo persistir Etapa 1 si el usuario abandona una pausa),
y H4/H5 requieren acción humana fuera de una sesión de agente (login en
SonarCloud; una pregunta de dominio para Facundo).

Se encontró y corrigió **un solo hallazgo real de documentación**: el
encabezado desactualizado de la DECISIÓN 062 y su fila espejo en
`README.md` — ambos corregidos con addendum fechado, sin reescribir la
historia del documento original.

No se encontró ningún caso de código faltante, código que no hace lo que su
documentación describe, entrada huérfana en el índice de decisiones, ni
desincronización en el catálogo de errores. El plan post-avance queda
cerrado.
