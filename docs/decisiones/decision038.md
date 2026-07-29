# DECISIÓN 038 — Catálogo de códigos de error como fuente única, en ambas direcciones
**Fecha:** 29 de Julio de 2026
**Estado:** APLICADA — catálogo y `errors.es.ts` sincronizados; un gap de propagación en `core/` queda documentado, no corregido

### Contexto
`api-contracts.md` declara una sección "Catálogo completo de códigos
estandarizados" como referencia única de todos los códigos del sistema. En la
práctica, el catálogo y el código real (`backend/metis/`) y el diccionario de
textos del frontend (`frontend/src/i18n/errors.es.ts`) habían divergido en ambas
direcciones sin que nada lo detectara.

### Diagnóstico confirmado

**Emitidos por el backend y ausentes del catálogo** (verificado con grep antes de
esta pasada):

| Código | Emitido en |
|---|---|
| `TEST_NOT_EXECUTED_MIN_SAMPLES` | `core/etapa1/trend.py::calcular_mann_kendall` (n < 10) |
| `PARSE_ERROR` | `services/analysis_service.py`, evento SSE `error` |
| `SESSION_TIMEOUT` | `services/analysis_service.py`, evento SSE `error` (timeout de decisión de atípico) |

**Presentes en el catálogo y ausentes de `errors.es.ts`** (verificado leyendo el
archivo completo antes de esta pasada):

| Código | Nota |
|---|---|
| `TEST_CRITICAL_INDEPENDENCE` | Uno de los dos únicos códigos CRÍTICOS del sistema |
| `TEST_CRITICAL_HOMOGENEITY` | Ídem |
| `TEST_OUTLIER_REJECTED_BY_USER` | Registro de auditoría de decisión del usuario |
| `TEST_OUTLIER_ACCEPTED_BY_USER` | Ídem |

`STREAM_CONNECTION_ERROR` sí está en `errors.es.ts`, pero es código muerto — nunca
se llama `errorText("STREAM_CONNECTION_ERROR")` en ningún componente; `sse.ts`
usa `String(err)` crudo en su lugar. No se toca acá — es la corrección D1 del
plan de esta pasada, sobre código de `frontend/src/`, no sobre el catálogo.

**Hallazgo adicional — asimetría real en la propagación de `TEST_WARNING_SMALL_SAMPLE`.**
`core/etapa1/independence.py::determinar_warnings_independencia` (línea ~139)
comprueba `wald.warning_codigo == "TEST_WARNING_SMALL_SAMPLE"` y lo promueve
correctamente a la lista agregada de `result.warnings`. `core/etapa1/trend.py`
fija el mismo `warning_codigo` en el `TestResult` de Mann-Kendall cuando
`10 ≤ n ≤ 30` (`formulas-etapa1.md` §7 documenta este umbral como advertencia
esperada), pero `determinar_warnings_tendencia` (línea ~100) solo comprueba
`veredicto == "rechazada"` para emitir `TEST_WARNING_TREND` — nunca lee
`mann_kendall.warning_codigo`. Consecuencia: el usuario nunca ve la advertencia de
muestra chica por la vía de tendencia en `result.warnings`, aunque el `TestResult`
individual de Mann-Kendall (evento SSE `test_result`) sí la lleva. **No se corrige
en esta pasada** — alcance explícito del plan: no tocar `core/`. Queda como
pendiente de backend, con el diagnóstico ya cerrado, para que la próxima sesión
solo tenga que decidir si es intencional (no parece serlo, dado que el patrón
gemelo de independencia sí lo hace) y aplicar el fix simétrico en `trend.py`.

### Decisión
1. **Catálogo → código real.** Se agregan `TEST_NOT_EXECUTED_MIN_SAMPLES` a la
   sección "Etapa 1 — pruebas" de `api-contracts.md`, y se crea una sección nueva
   "### Stream / sesión" con `PARSE_ERROR` y `SESSION_TIMEOUT` (no encajaban en
   ninguna sección existente — son eventos SSE `error` de nivel de sesión, no de
   una prueba estadística puntual).
2. **Catálogo → `errors.es.ts`.** Se agregan las cuatro entradas faltantes
   (`TEST_CRITICAL_INDEPENDENCE`, `TEST_CRITICAL_HOMOGENEITY`,
   `TEST_OUTLIER_REJECTED_BY_USER`, `TEST_OUTLIER_ACCEPTED_BY_USER`) con texto en
   español consistente con el resto del diccionario.
3. **Regla para el futuro** (el motivo real de esta decisión, no los códigos en sí
   mismos): **el catálogo de `api-contracts.md` es la fuente única de códigos de
   error del sistema, y todo código nuevo emitido por `core/` o `services/` se
   agrega ahí en el mismo commit que lo introduce.** Un código de error que existe
   en producción pero no en el catálogo no es un detalle menor — es exactamente el
   tipo de divergencia silenciosa que esta decisión encontró dos veces en la misma
   pasada de revisión.
4. **`TEST_WARNING_SMALL_SAMPLE` se documenta como emitido por dos pruebas**, no
   solo por Wald-Wolfowitz, con nota explícita del gap de propagación en
   Mann-Kendall — sin corregir `core/`.

### Criterio de hecho — verificación reproducible
```bash
# Cada código emitido por el backend debe aparecer al menos una vez en el catálogo
grep -rhoE '"[A-Z_]+_[A-Z_]+"' backend/metis/core backend/metis/services \
  | tr -d '"' | sort -u > /tmp/codigos_backend.txt
grep -oE '^[A-Z_]+' .claude/rules/architecture/api-contracts.md \
  | sort -u > /tmp/codigos_catalogo.txt
comm -23 /tmp/codigos_backend.txt /tmp/codigos_catalogo.txt
# (salida esperada: vacía, o solo strings que no son códigos de error reales)

# Cada código del catálogo debe aparecer en errors.es.ts
grep -oE '^[A-Z_]+' .claude/rules/architecture/api-contracts.md | sort -u > /tmp/codigos_catalogo.txt
grep -oE '^  [A-Z_]+:' frontend/src/i18n/errors.es.ts | tr -d ' :' | sort -u > /tmp/codigos_frontend.txt
comm -23 /tmp/codigos_catalogo.txt /tmp/codigos_frontend.txt
# (salida esperada: vacía, salvo códigos de Etapa 2 — todavía no expuestos en
# frontend real, ver DECISIÓN 042)
```
Ambos comandos son heurísticos (dependen del formato de texto de cada archivo, no
de un parser real) — sirven para detectar divergencia nueva, no como CI
automatizado. **Ejecutados de verdad en esta pasada, no asumidos:**

- backend → catálogo: la única salida es `STATUS_DISABLED_ZEROS`,
  `STATUS_NO_APLICABLE`, `STATUS_NO_CONVERGE`, `STATUS_OK` — constantes internas
  de estado de Etapa 2 (`core/etapa2/types.py`), no códigos de error de cara al
  usuario. No es un gap real.
- catálogo → `errors.es.ts`: la única salida real son los cuatro `DIST_*`
  (Etapa 2, todavía no expuestos en el frontend real — ver DECISIÓN 042) más
  ruido de una letra (`A`, `E`, `P`) generado por el regex sobre párrafos de
  prosa que empiezan con mayúscula ("Ambos son...", "Emitidos por...",
  "Presentes en...") — no un código real. Esta corrida encontró y corrigió un
  gap real antes de cerrar la decisión: `TEST_NOT_EXECUTED_MIN_SAMPLES` se había
  agregado al catálogo pero no a `errors.es.ts` en el primer paso de esta misma
  pasada — ya corregido arriba.

Si el formato de alguno de los dos archivos cambia significativamente, el comando
necesita ajustarse.

**Ver también:** [DECISIÓN 036](decision036.md), [DECISIÓN 037](decision037.md) —
mismos hallazgos de esta pasada, mismo patrón de "documentar sin tocar `core/`".
