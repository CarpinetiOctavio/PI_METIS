# Plan de Mejora — Pasada 2 sobre el Frontend (Fases 1-6)

**Fecha:** 29 de Julio de 2026.
**Autor del diagnóstico:** revisión integral posterior a la sesión de implementación
documentada en [`informe-implementacion-frontend-fase1-6.md`](./informe-implementacion-frontend-fase1-6.md).
**Destinatario:** la próxima sesión de Claude Code que retome el frontend.
**Alcance:** reintegración documental del trabajo de Fases 1-5 con el resto del proyecto,
escalamiento formal de tres hallazgos de backend que la sesión anterior encontró pero no
registró, y una lista acotada de correcciones de código.

---

## 0. Cómo leer este plan

La sesión anterior hizo buen trabajo de ingeniería: el razonamiento de las decisiones es
sólido, los dos bugs de `useAnalysisStream` son reales y están bien diagnosticados, y la
verificación E2E contra Docker fue el paso correcto en el momento correcto. **Este plan no
corrige errores de criterio técnico.**

Lo que corrige es que ese trabajo quedó **encapsulado en sus propios archivos**: se escribió
mucho en `frontend-implementation-plan.md` §10 y en el informe consolidado, pero no se tocaron
los documentos que son fuente de verdad del proyecto (`CLAUDE.md`, `sprint.md`,
`docs/decisiones/`, `api-contracts.md`). El resultado es que hoy el repo se contradice a sí
mismo en varios lugares, y que hallazgos de backend con impacto en requerimientos funcionales
están documentados únicamente dentro de código de frontend.

El plan está ordenado por urgencia real, no por comodidad de ejecución. **Bloque A antes que
todo lo demás.**

### Reglas de alcance para esta pasada

**SÍ entra:**
- Documentación: `CLAUDE.md`, `.claude/rules/`, `docs/`.
- Correcciones puntuales en `frontend/src/` (lista cerrada, Bloque D).
- Registro formal de hallazgos de backend en `docs/decisiones/`.

**NO entra — no hacer sin consultar a Kevin u Octavio:**
- Modificar `backend/metis/core/` (motor estadístico). Los hallazgos de backend de esta
  pasada se **documentan**, no se implementan.
- Renumerar, reordenar o fusionar decisiones existentes (`decision001.md` a `decision034.md`).
  El número es inmutable — ver `docs/decisiones/README.md`, "El número es inmutable".
- Cambiar el stack (`constraints.md`). En particular: **no** agregar TanStack Query, Prettier
  ni una librería de UI en esta pasada.
- Tocar `.env`, credenciales, o cualquier cosa relacionada con SMTP.
- Cerrar el pendiente de accesibilidad de Fase 6 antes de terminar los Bloques A-C. Es lo
  único que el informe anterior reconocía como faltante, y es lo *menos* urgente de esta lista.

---

## Bloque A — Hallazgos de backend sin registrar (máxima prioridad)

Los tres son defectos reales, verificados contra el código, que la sesión anterior detectó
(total o parcialmente) y no escaló. El primero es un requerimiento funcional caído.

### A1 — Partición de Cramer personalizada es inalcanzable por el endpoint

**Evidencia.** `frontend/src/routes/config/ConfigPage.tsx`, bloque "Partición de Cramer": el
botón "Personalizada" está `disabled` con `title="No disponible — partición personalizada rota
en el backend actual"`. **Eso es todo lo que existe hoy como documentación del hallazgo.**

**Diagnóstico verificado.**
- `backend/metis/api/v1/analysis.py` declara `cramer_particion: str = Form("default")`. Un
  campo `multipart/form-data` siempre llega como string.
- `backend/metis/core/etapa1/homogeneity.py::calcular_cramer` espera `dict | str` y en la rama
  `else` hace `particion["n1_pct"]`.
- Consecuencia: cualquier valor distinto del literal `"default"` llega como `str` a
  `calcular_cramer`, entra al `else` e indexa un string con una clave → `TypeError`. No hay
  ningún camino por el que el endpoint pueda recibir la partición personalizada.

**Por qué importa.** Contradice tres documentos vigentes a la vez:
- `.claude/rules/architecture/api-contracts.md` — `cramer_particion: "default" | {n1_pct, n2_pct}`.
- `.claude/rules/core/statistical-pipeline.md` — *"Partición configurable: default = últimos 60%
  y últimos 30%. CU-01/CU-02: usuario configura partición desde la interfaz."*
- `.claude/rules/core/formulas-etapa1.md` §6, nota de arquitectura sobre personalización de bloques.

**Tarea.** Escribir `docs/decisiones/decision036.md` (ver Bloque B para la reserva de números)
con el formato estándar del repo: Contexto / Diagnóstico confirmado / Opciones evaluadas /
Decisión / Ver también. Como mínimo debe evaluar y dejar registro de:

1. Recibir `cramer_particion` como JSON string en el `Form` y parsearlo con
   `CramerParticionCustom.model_validate_json()` en la capa `api/`.
2. Recibir dos campos `Form` separados (`cramer_n1_pct`, `cramer_n2_pct`, opcionales) y armar
   el dict en `api/`.
3. Dejar la partición fija en `"default"` para V1.0 y bajar el requerimiento explícitamente.

**No implementar la opción elegida en esta pasada** — la decisión queda documentada y el
trabajo de backend se agenda. Sí actualizar:
- `.claude/rules/sprint.md` — entrada del pendiente con la referencia a la decisión.
- `frontend/src/routes/config/ConfigPage.tsx` — reemplazar el `title` improvisado por una
  referencia a `docs/decisiones/decision036.md`, y sacar la palabra "rota" del texto visible al
  usuario (es correcto en la decisión, no en la UI).

**Criterio de hecho:** existe `decision036.md`, está en el índice de `docs/decisiones/README.md`
con título/fecha/estado, está referenciada desde `sprint.md`, desde `api-contracts.md` (nota de
que el contrato documentado no está implementado) y desde el código de `ConfigPage.tsx`.

---

### A2 — `etapas` se acepta y se descarta; `AnalysisRequest` es código muerto

**Diagnóstico verificado.**
- `analysis.py` declara `etapas: str = Form("1")` y **nunca lo pasa** a `stream_etapa1()`.
- `frontend/src/api/sse.ts::buildFormData` directamente no lo envía.
- `backend/metis/schemas/analysis.py::AnalysisRequest` — el modelo Pydantic que representa el
  contrato documentado, con `etapas: list[Etapa]` y `cramer_particion: Literal["default"] |
  CramerParticionCustom` — **no lo importa ninguna ruta**. Solo se exporta desde
  `schemas/__init__.py`. `/stream` redeclara todo como `Form(...)` sueltos.

**Por qué importa.** `CLAUDE.md` describe `schemas/` como "Modelos Pydantic: analysis.py" y
`sprint.md` marca `feature/schemas` como mergeado y completo. La capa de validación tipada es
argumento de ingeniería ante el tribunal de ISI; que el endpoint principal no la use es
exactamente el tipo de inconsistencia que conviene tener resuelta y documentada antes de la
defensa, no descubierta en ella.

Hoy es inocuo porque Etapa 2 está mockeada. Deja de serlo en M2.

**Tarea.** `docs/decisiones/decision037.md`, evaluando al menos: (a) cablear `AnalysisRequest`
al endpoint multipart, (b) mantener los `Form(...)` sueltos y borrar el modelo muerto, (c)
mantener ambos con el modelo como fuente de verdad del contrato documentado y una nota
explícita de por qué no se usa en runtime. Registrar también qué pasa con `etapas` cuando
Etapa 2 se exponga de verdad.

**Criterio de hecho:** decisión escrita e indexada; `sprint.md` la referencia dentro del
alcance de M2 o M3 según corresponda; `CLAUDE.md` no queda afirmando algo que el código no hace.

---

### A3 — Códigos de error fuera del catálogo, en las dos direcciones

**Diagnóstico verificado.**

Emitidos por el backend y **ausentes** del catálogo de `.claude/rules/architecture/api-contracts.md`:

| Código | Emitido en |
|---|---|
| `TEST_NOT_EXECUTED_MIN_SAMPLES` | `core/etapa1/trend.py` (Mann-Kendall, n < 10) |
| `PARSE_ERROR` | `services/analysis_service.py` (evento SSE `error`) |
| `SESSION_TIMEOUT` | `services/analysis_service.py` (timeout de decisión de atípico) |

Presentes en el catálogo y **ausentes** de `frontend/src/i18n/errors.es.ts`:

| Código | Nota |
|---|---|
| `TEST_CRITICAL_INDEPENDENCE` | Uno de los dos únicos códigos CRÍTICOS del sistema |
| `TEST_CRITICAL_HOMOGENEITY` | Ídem |
| `TEST_OUTLIER_REJECTED_BY_USER` | Registro de auditoría de decisión del usuario |
| `TEST_OUTLIER_ACCEPTED_BY_USER` | Ídem |

Además, `STREAM_CONNECTION_ERROR` existe en `errors.es.ts` pero es **código muerto** — ver D1.

**Hallazgo adicional a verificar.** `core/etapa1/trend.py` setea
`warning_codigo = "TEST_WARNING_SMALL_SAMPLE"` en el `TestResult` de Mann-Kendall (10 ≤ n ≤ 30),
pero `determinar_warnings_tendencia()` **no lo levanta** a `result.warnings` — solo emite
`TEST_WARNING_TREND`. Resultado: el usuario nunca ve la advertencia de muestra chica por la vía
de tendencia, solo por la de Wald-Wolfowitz. Confirmar si es intencional
(`formulas-etapa1.md` §7 documenta el umbral como advertencia esperada) y, si no lo es,
registrarlo como pendiente — **sin tocar `core/` en esta pasada.**

**Tarea.**
1. Agregar los tres códigos faltantes al catálogo de `api-contracts.md`, en la sección que
   corresponda (crear una sección `### Stream / sesión` si no encaja en las existentes).
2. Agregar las cuatro entradas faltantes a `errors.es.ts`.
3. Revisar el texto de `TEST_WARNING_SMALL_SAMPLE` en `errors.es.ts` — hoy dice "Wald-Wolfowitz"
   explícitamente. Es correcto mientras el backend solo lo emita desde independencia; si el
   hallazgo adicional se resuelve emitiéndolo también desde tendencia, el texto debe generalizarse.
4. Documentar el conjunto en `docs/decisiones/decision038.md` — no por los códigos en sí, sino
   por la regla: **el catálogo de `api-contracts.md` es la fuente única, y todo código nuevo
   emitido por `core/` o `services/` se agrega ahí en el mismo commit que lo introduce.**

**Criterio de hecho:** `grep` de cada código emitido en `backend/metis/` devuelve al menos una
coincidencia en `api-contracts.md`; `grep` de cada código del catálogo devuelve al menos una
coincidencia en `errors.es.ts`. Dejar ese chequeo anotado en la decisión como verificación
reproducible.

---

## Bloque B — Reintegración de las decisiones de frontend

### B0 — Reservar los números ANTES de escribir nada

**Crítico y fácil de pasar por alto:** `decision035.md` **ya está reservado** para la
protección de ramas vía GitHub Ruleset — ver `.claude/rules/sprint.md`, sección "Estrategia de
ramas", pendiente del 20/07/2026. Todavía no existe el archivo, pero el número está
comprometido por escrito.

**Las decisiones de esta pasada arrancan en 036.** Asignación propuesta:

| # | Título | Origen |
|---|---|---|
| 035 | *(reservado — GitHub Ruleset, no tocar)* | sprint.md 20/07 |
| 036 | Partición de Cramer personalizada inalcanzable por el endpoint multipart | A1 |
| 037 | Contrato de `/analysis/stream`: `etapas` descartado y `AnalysisRequest` sin cablear | A2 |
| 038 | Catálogo de códigos de error como fuente única, en ambas direcciones | A3 |
| 039 | Criterio de promoción de las decisiones de frontend y unificación de numeración | B1 |
| 040 | SSE sobre fetch para el stream de Etapa 1 | D1 del plan |
| 041 | Estado de servidor sin TanStack Query; `vi.stubGlobal("fetch")` como patrón único de test | D4, D5, D20 |
| 042 | Alcance de los mocks de Etapa 2 y rol de MSW | D3, D19 |

Primera tarea de la pasada: agregar las ocho filas al índice de `docs/decisiones/README.md`
con estado `EN CURSO`, antes de escribir el contenido. Así ningún trabajo paralelo pisa un número.

### B1 — Migrar las decisiones que lo ameriten, no las veinte

`docs/decisiones/README.md` fija la convención: un archivo por decisión, número inmutable,
entrada en el índice. Las 20 decisiones de frontend viven en `frontend-implementation-plan.md`
§10, sin número global, sin estado, sin índice.

**No corresponde crear 20 archivos.** Varias de las D no son decisiones de arquitectura sino
notas de implementación (D8 fidelidad de markup, D11 agrupación del timeline, D12 botón manual
de "Ver resultados", D15 `<details>` vs tarjetas). El criterio a aplicar, y a dejar escrito en
`decision039.md`, es:

> Se promueve a `decisionNNN.md` lo que **restringe decisiones futuras o contradice un documento
> vigente del repo**. Lo que solo describe cómo quedó implementada una pantalla se queda como
> nota de implementación en el plan.

**Promoción propuesta:**

| Del plan | A | Motivo |
|---|---|---|
| D1 | `decision040.md` | Decisión técnica central de todo el streaming; condiciona la librería y el manejo de errores. |
| D4 + D5 + D20 | `decision041.md` | Contradice `§1.1` del propio plan y define el patrón de testing de toda la suite. |
| D3 + D19 | `decision042.md` | Define qué es mock y qué es real — relevante para el tribunal. |
| D2, D6-D18 | quedan en el plan | Notas de implementación; se renombran (ver B2). |

**Además:** D4 prometía *"React Query se suma recién en Fase 4, cuando `/history` lo justifique
más"*. Fase 4 pasó y no se sumó. `decision041.md` debe cerrar eso explícitamente — o se
descarta React Query para V1.0, o se agenda con condición de habilitación (mismo patrón que
`decision033.md` usó para el bump de FastAPI).

### B2 — Resolver la colisión de tres esquemas de numeración

Hoy conviven, con aspecto idéntico y significados distintos:

- `DECISIÓN 001`-`034` — convención del repo.
- `D1`-`D20` — plan de frontend §10.
- `Decisión A` / `Decisión C` / `Decisión D` — `frontend-design/metis-wireframes-fase1-decisiones.md`.

El código las mezcla sin distinguirlas:

| Archivo | Referencia | Apunta a |
|---|---|---|
| `frontend/src/api/sse.ts` | "Decisión D1" | plan §10 |
| `frontend/src/routes/config/ConfigPage.tsx` | "Decisión D" | wireframes |
| `frontend/src/routes/results/Etapa1ResultView.tsx` | "Decisión D" | wireframes |
| `frontend/src/routes/results/ResultsPage.tsx` | "Decisión D" | wireframes |
| `frontend/src/routes/entry/EntryPage.tsx` | "Decisión D6" | plan §10 |

**Tarea.** Adoptar prefijos inequívocos y aplicarlos en documentos y código:
- `DECISIÓN NNN` — decisiones del repo (sin cambios).
- `FE-NNN` — notas de implementación del plan de frontend (renombrar D2, D6-D18).
- `UX-A` .. `UX-D` — decisiones de los wireframes.

Actualizar las cinco referencias de código de la tabla, y todas las referencias cruzadas dentro
de `frontend-implementation-plan.md`. Dejar en `decision039.md` una tabla de equivalencia
`D1..D20 → destino final`, para que las referencias históricas sigan siendo resolubles.

### B3 — `frontend-design/` está sin trackear y el código de producción lo cita

`frontend/frontend-design/` (wireframes Fase 1, identidad Fase 2, prototipo Fase 3, más
`versiones/` con 9 archivos históricos) **no está en git**. Al mismo tiempo:
- `ConfigPage.tsx` cita `metis-wireframes-fase1-decisiones.md`.
- La decisión D8 del plan cita `metis-prototipo-fase3.html` como fuente del markup de `EntryPage`.

Desde un clone limpio, ninguna de esas dos referencias es resoluble.

**Esto requiere decisión de Kevin, no del agente.** Opciones a presentarle:
1. Commitear `frontend-design/` completo (incluido `versiones/`) — coherente con la cultura de
   trazabilidad del proyecto (`docs/historico/` nunca borra nada).
2. Commitear solo los tres archivos vigentes y dejar `versiones/` fuera vía `.gitignore`.
3. Dejarlo fuera del repo y **eliminar las citas del código**, reemplazándolas por el contenido
   relevante transcripto en el plan.

Recomendación: opción 1. Es el criterio que el repo ya aplica en todos lados.

---

## Bloque C — Documentos de verdad desactualizados

### C1 — `CLAUDE.md`, sección "Frontend — estado actual"

Hoy dice: *"por ahora es scaffold, no integración real con los endpoints de análisis"*. Es
falso desde el commit `2afcc5d`. `CLAUDE.md` es el documento que se lee primero en toda sesión;
mientras diga eso, cada sesión nueva arranca con el modelo mental equivocado.

Ninguno de los siete commits de la sesión anterior tocó `CLAUDE.md`.

**Reescribir** la sección con: auth end-to-end operativa, stream SSE de Etapa 1 integrado
contra el backend real, resultados en tres modos, historial, Etapa 2 mockeada con marca visual,
y el estado real de la verificación E2E. Mencionar `frontend/src/api/sse.ts` como pieza central.

### C2 — `.claude/rules/sprint.md` no tiene sección de frontend

~5.700 líneas y cinco fases aparecen solo como notas incidentales sobre SMTP bajo "Entorno de
desarrollo — datos de prueba". Problemas concretos:

- La línea *"Fuera de alcance en este sprint: Frontend React + TypeScript"* quedó contradicha
  y sin corregir.
- **Colisión de nombres de fase dentro del mismo archivo:** `sprint.md` ya usaba "Fase 1…Fase 6"
  para el desarrollo de Core Etapa 2. Ahora el frontend usa "Fase 1…Fase 6" para otra cosa
  distinta, en el mismo documento, sin calificar. Toda mención nueva debe decir
  "Fase N del frontend" explícitamente.
- La nota del 29/07 sobre insertar un usuario verificado en Postgres dice "(Fase 6, verificación
  E2E...)", pero según el informe la verificación E2E fue **fuera de las 6 fases nominales**
  (backlog P4-P7), y Fase 6 es pulido y accesibilidad. Corregir la etiqueta.

**Tarea.** Agregar una sección `### feature/frontend-fases1-5 — COMPLETA` con el mismo nivel de
detalle que tienen las secciones de `feature/core-etapa2` y `feature/auth-refactor`: archivos
creados por fase, bugs encontrados y corregidos, decisiones asociadas (por número, ya migradas
en el Bloque B), y qué quedó pendiente.

### C3 — Un criterio de M1 se cerró y no se registró

`sprint.md`, sección M1, lista como pendiente: *"Verificación end-to-end del pipeline con CSV
real: pendiente hasta tener frontend o cliente HTTP configurado"*.

**Eso se cerró.** El pendiente P5 del plan documenta un CSV sintético de 40 años corrido contra
el backend real en Docker, con un atípico forzado, el modal de Chow real, `resolveOutlier`
real y la re-ejecución de `iteracion:2` verificada.

De los tres criterios pendientes de M1 quedan **dos** (tests de regresión matemática con las
series digitales de Facundo, y el tramo registro→verify de auth, bloqueado por SMTP).

Actualizar M1 con el mismo formato de "**ACTUALIZACIÓN <fecha>**" que ya usan las entradas de
Auth Parte 2 — no reescribir el texto original, agregar la actualización debajo.

### C4 — `docs/README.md` incumple su propia regla

El README declara: *"Cada vez que se agregue o modifique un directorio o archivo directamente
bajo `docs/`, se actualiza este README"*. Estado real:

- La sección "Estructura" **no lista** `frontend-implementation-plan.md` ni
  `frontend-integration.md`, que existen desde hace días.
- La sección `### decisiones/` sigue diciendo *"decision001.md a decision031.md"* cuando el
  índice va por 034 (y con esta pasada llegará a 042).
- El informe del 29/07 **sí** se registró en el historial. Cumplimiento parcial.

**Tarea.** Poner al día "Estructura" e historial. **Evaluar además** agrupar los cuatro
documentos de frontend (`frontend-implementation-plan.md`, `frontend-integration.md`,
`informe-implementacion-frontend-fase1-6.md`, y este plan) bajo `docs/frontend/`. Hoy están
sueltos en la raíz de `docs/` sin categoría, que es justamente lo que el README pide discutir
antes de hacer: *"Contenido nuevo que no encaje claramente en `auditoria/`, `decisiones/` o
`historico/` se discute antes de crear una carpeta nueva o forzarlo en la que más se le
parezca."* Proponer, no ejecutar unilateralmente.

Este mismo documento (`plan-mejora-frontend-pasada2.md`) también debe quedar registrado.

### C5 — El plan de frontend se contradice a sí mismo

`frontend-implementation-plan.md` §1.1 (tabla de stack) y §3.1 siguen afirmando cosas que las
decisiones posteriores derogaron:

| §1.1 dice | Realidad |
|---|---|
| TanStack Query para REST | Nunca se agregó (D4). §3.1 todavía dice "`GET /me` (react-query)". |
| Prettier | No está en `package.json`. |
| CSS Modules (o vanilla-extract) | Se usa CSS plano co-locado por ruta. |
| MSW para mocks en tests | Derogado por D5/D20 — MSW solo en navegador de dev. |

**Tarea.** Actualizar §1.1 y §3.1 marcando lo derogado con referencia a la decisión que lo
deroga (no borrar el texto original — mismo criterio de trazabilidad que usa
`docs/decisiones/`). Cerrar además el pendiente **P2** (puerto 5173 / Vite), que está resuelto
de hecho desde Fase 0 y sigue listado como abierto.

### C6 — `frontend/README.md`

Describe únicamente el scaffold. Actualizar con la estructura real de `src/` (`api/`, `auth/`,
`i18n/`, `mocks/`, `routes/`, `theme/`), el patrón de testing vigente, y una nota de que
Etapa 2 es mock con marca visual (`PendingBadge`).

### C7 — `.claude/launch.json`

Entró en el commit de Fase 1 (`2afcc5d`) sin mención en el mensaje de commit ni en ningún
documento. `launch.json` es convención de VS Code, no de Claude Code — con toda probabilidad es
un archivo inerte que nadie lee. **O se documenta qué es y quién lo consume, o se elimina.**
No dejarlo sin explicación en un repo que se va a exponer ante un tribunal.

---

## Bloque D — Correcciones de código (lista cerrada)

Ninguna es urgente en el sentido de A1, pero D3 es el defecto más visible de toda la interfaz.

| # | Archivo | Problema | Corrección |
|---|---|---|---|
| **D1** | `src/api/sse.ts`, `onerror` | `mensaje: String(err)` muestra el texto crudo de un `Error` de JavaScript al usuario. La entrada `STREAM_CONNECTION_ERROR` de `errors.es.ts` existe y nunca se usa. | Usar `errorText("STREAM_CONNECTION_ERROR")`. Revisar por consistencia el caso `error`, que usa `event.mensaje` del backend mientras `contract_error` usa el diccionario — unificar el criterio y dejarlo comentado. |
| **D2** | `src/routes/stream/StreamPage.tsx` | No se llama `abort()` al desmontar. Si el usuario navega a mitad de stream: el `fetch` sigue vivo, hay `setState` sobre componente desmontado, y queda una sesión colgada hasta 300s en `session_store` del backend. | `useEffect` de cleanup que llame `abort()`. Test de regresión. |
| **D3** | `Etapa1ResultView.tsx`, `StreamPage.tsx`, `HistoryDetailPage.tsx` | **Ningún número tiene formato.** `media` se renderiza como `142.53333333333333`. En una herramienta estadística que se compara contra el Excel de Facundo y se defiende ante un tribunal, esto es el defecto más visible de la UI. | Helper único (`src/i18n/format.ts` o similar): decimales significativos configurables y separador decimal es-AR. Aplicarlo a todo `className="num"`. Definir la cantidad de decimales de forma consistente con cómo reporta la tesis (4-5), y **documentar el criterio** — no elegirlo al azar. |
| **D4** | `src/api/sse.ts`, `resolveOutlier` | Depende de `internal` completo → el `useCallback` se recrea en cada evento SSE. Además hay riesgo de closure obsoleta. | Leer `outlier` vía `setInternal` funcional o un `ref`. |
| **D5** | `src/routes/ranking/RankingPage.tsx` | El estado `axis` es único a nivel página pero el toggle calendario/hidrológico se renderiza **por tarjeta**: tocarlo en una cambia todas. | Estado por tarjeta, o un único control a nivel página. Se arrastra a la implementación real de Etapa 2 si no se corrige ahora. |
| **D6** | `Etapa1ResultView.tsx`, `GroupTable` | `(t.n1 !== null \|\| t.n2 !== null)` renderiza literalmente `n2=null` cuando solo uno de los dos está presente. Relevante porque Cramer siempre debe reportar `n1` y `n2` (`statistical-pipeline.md`). | Renderizar cada uno solo si no es `null`. |
| **D7** | `src/auth/guards.tsx` | Devuelve `null` mientras `isLoading` → pantalla completamente en blanco en cada carga de la app. | Skeleton o spinner mínimo, consistente con el tema Instrumento. |
| **D8** | `src/auth/AuthProvider.tsx` | `logout()` no limpia `localStorage["metis-anon-session"]`. | Limpiarlo. |
| **D9** | `src/routes/stream/StreamPage.tsx`, `summarizeGroup` | Deriva la criticidad del grupo del `warning_nivel` de cada prueba, no de `nivel_independencia` / `nivel_homogeneidad`. Con Anderson aprobando y Wald-Wolfowitz rechazando, el timeline muestra "warning" aunque la jerarquía documentada diga INDEPENDIENTE (`constraints.md`, "Anderson manda"). | **Es una decisión de dominio, no de UI.** Resolver explícitamente: o el timeline en vivo refleja la jerarquía, o se documenta por qué muestra el estado por prueba. Dejar constancia donde corresponda. |

### D10 — Accesibilidad del modal de atípico (pendiente heredado de Fase 6)

Además del focus trap, auto-foco y cierre con Escape que el informe anterior ya identifica:

- `role="dialog"` y `aria-modal="true"` están sobre el **backdrop**, no sobre la tarjeta del
  diálogo. Moverlos al contenedor correcto.
- El resto de la página no queda `inert` ni `aria-hidden` mientras el modal está abierto.
- `PendingBadge` comunica su nota únicamente por `title`, que no es un afordance confiable ni
  para lector de pantalla ni para teclado.

### D11 — Pasada de contraste WCAG sobre `tokens.instrumento.css`

Segundo pendiente heredado de Fase 6. Verificar claro y oscuro. Si algún token no cumple AA,
**no cambiarlo unilateralmente** — el tema Instrumento es identidad visual fijada; proponer el
ajuste y dejarlo registrado.

---

## Bloque E — Requiere confirmación de Kevin antes de ejecutar

### E1 — Line endings y ausencia de `.gitattributes`

Leyendo el repo desde Linux aparecen **212 archivos modificados**, idénticos salvo CRLF vs LF
(37.973 líneas de cada lado). La explicación más probable es que sea un artefacto de leer un
checkout de Windows con `core.autocrlf=true` desde otro sistema — no un cambio real.

Pero el repo **no tiene `.gitattributes`**, y con dos personas trabajando en sistemas
potencialmente distintos eso es un `git status` fantasma esperando a ocurrir.

**Antes de tocar nada:** correr `git status` en el Windows de Kevin.
- Si sale limpio → confirmado que es artefacto. Agregar `.gitattributes` con `* text=auto` y
  las excepciones binarias que correspondan, en un commit aislado y bien identificado.
- Si sale sucio → hay un problema real que resolver **antes** que todo lo demás de este plan.

### E2 — Destino de `frontend-design/`

Ver B3. Tres opciones, recomendación: commitear completo.

### E3 — `docs/frontend/` como subcarpeta

Ver C4. El README de `docs/` pide discutirlo antes de crear una carpeta nueva.

---

## Orden de ejecución sugerido

```
0. E1 (confirmar line endings)          ← bloquea todo lo demás si sale sucio
1. B0 (reservar 036-042 en el índice)   ← antes de escribir cualquier decisión
2. A1 → A2 → A3                         ← hallazgos de backend, máxima prioridad
3. B1 → B2 → B3                         ← migración y unificación de numeración
4. C1 → C2 → C3                         ← CLAUDE.md, sprint.md, M1
5. C4 → C5 → C6 → C7                    ← resto de documentación
6. D1 → D2 → D3 → D4..D9                ← código
7. D10 → D11                            ← accesibilidad (pendiente de Fase 6)
8. Verificación final
```

## Verificación final de la pasada

Antes de dar la pasada por cerrada, ejecutar y **pegar la salida real** en el informe de
resultados — no afirmar sin evidencia:

1. `cd frontend && npm run lint && npm test && npm run build` — los tres en verde, con el
   conteo real de tests (la pasada anterior cerró con 119; debería subir con los tests de
   regresión de D2 y D3).
2. `cd backend && ruff check metis/ && ruff format --check metis/ && pytest -m unit -v`.
3. `git status` limpio (o con solo lo que se decidió dejar sin trackear, explicitado).
4. Chequeo de códigos de error en ambas direcciones (A3) — el `grep` reproducible que la
   decisión 038 debe dejar documentado.
5. Ninguna referencia rota: todo `docs/decisiones/decisionNNN.md`, `§N` o nombre de archivo
   citado desde código o documentación debe existir. Verificarlo, no asumirlo.
6. `grep -rn "Decisión D" frontend/src` debe devolver cero — o solo referencias con el prefijo
   nuevo (`UX-D`, `FE-NN`).

## Formato del informe de resultados

Mismo formato que `informe-implementacion-frontend-fase1-6.md`, que estuvo bien planteado.
Agregar, además:

- **Una fila por ítem de este plan** (A1..A3, B0..B3, C1..C7, D1..D11, E1..E3) con estado:
  hecho / parcial / no hecho / descartado con motivo. Sin omitir ninguno: un ítem descartado
  con justificación es un resultado válido; un ítem que desaparece del informe, no.
- Los números de decisión finalmente asignados, si difieren de la propuesta de B0.
- Todo hallazgo **nuevo** que aparezca durante la pasada — con el mismo criterio que este plan
  aplica a A1: si contradice un documento vigente o restringe decisiones futuras, va a
  `docs/decisiones/`, no a un comentario de código.
