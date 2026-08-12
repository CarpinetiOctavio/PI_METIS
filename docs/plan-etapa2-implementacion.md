# Plan de implementación — Etapa 2 de punta a punta

**Fecha:** 9 de Agosto de 2026
**Estado:** PLAN — no implementado
**Alcance:** cableado del motor de Etapa 2 al stream, frontend real (sin mocks),
gráficos interactivos, tests de regresión, exportación PDF y agregación
temporal por año hidrológico.
**Milestones afectados:** M2 (Etapa 2 operativa en staging) y M3 (API completa).

> Documento de trabajo, no de trazabilidad: **se elimina cuando la
> implementación cierra.** Todo lo que tenga que sobrevivir a este plan va a
> `docs/decisiones/` (decisiones), `docs/auditoria/pendientes/` (preguntas
> abiertas) o `.claude/rules/` (contratos y reglas operativas). Cada bloque
> dice explícitamente qué deja escrito y dónde.

---

## 0. Estado real verificado — 09/08/2026

Verificado contra el código, no contra la documentación. Hay dos cosas que la
documentación afirma y el código contradice; están marcadas.

### 0.1 Lo que existe y funciona

| Pieza | Estado |
|---|---|
| `core/etapa2/` | Completo: 13 distribuciones, `eea.py`, `empirical.py`, `utils.py`, `types.py` |
| `core/pipeline/pipeline_etapa2.py::ejecutar_etapa2()` | Completo — recorre las 13 × sus `METODOS_APLICABLES`, calcula EEA, ordena el ranking |
| `core/pipeline/full_pipeline.py` | Completo — encadena Etapa 1 → Etapa 2 |
| `analysis_results.etapa2` (JSONB) | Columna ya existente en la BD. **No hace falta migración.** |
| Guard `p ∈ (0,1)` en `cuantil()` | Presente en **las 13** distribuciones |
| Tests unitarios de distribuciones | 8 archivos en `tests/unit/core/etapa2/distributions/` |

### 0.2 El gap completo

`grep -rn "etapa2" backend/metis/api backend/metis/services` devuelve
exactamente dos líneas, y ninguna ejecuta nada:

```
services/analysis_service.py:413:        etapa2=None,           # al persistir
services/analysis_service.py:454:        "etapa2": result.etapa2,   # al leer del historial
```

**Nadie llama nunca a `ejecutar_etapa2()`.** El motor está completo y
desconectado. Concretamente falta:

1. `POST /analysis/stream` recibe `etapas: str = Form("1")` y **lo descarta** —
   nunca llega a `stream_etapa1()`. No hay forma de pedir `[1, 2]`
   (DECISIÓN 037).
2. `stream_etapa1()` termina en `result_etapa1` → `complete`. El evento
   `result_etapa2_ranking` que `statistical-pipeline.md` documenta no se emite
   nunca.
3. No existe el endpoint `/analysis/design-events`. El router tiene
   `preview-columns`, `stream`, `outlier-decision` y `{analysis_id}`.
4. `session_store` guarda un `asyncio.Event` y un `str` de decisión. No guarda
   la serie ni los ajustes — un `design-events` con `session_id` no tendría de
   dónde sacar los parámetros.
5. Nada calcula eventos de diseño. `EventoDiseno` existe en `types.py` y no lo
   construye ninguna función.
6. `_persistir()` escribe `etapa2=None` y `etapas=["1"]` hardcodeados.
7. El frontend: `RankingPage` importa `mocks/etapa2.mock.ts` directo y MSW
   intercepta `design-events` (DECISIÓN 042).

### 0.3 Dos afirmaciones de la documentación que el código contradice

- **`sprint.md` — "Guard p ∈ (0,1) — PENDIENTE PROPAGACIÓN"**, listando 11
  distribuciones pendientes. Falso: está en las 13. La Fase 4.5 se hizo y
  nunca se registró. Corregir `sprint.md` en el Bloque 0.
- **`CLAUDE.md` — `tests/` con markers `integration`, `e2e`, `regression`.**
  Los tres directorios existen y contienen únicamente `__init__.py`. No hay ni
  un test de integración, e2e ni de regresión en el repo. El job `test` de CI
  tolera exit code 5 precisamente por eso.

---

## 1. Descomposición en sub-proyectos

Lo pedido no entra en una sola especificación: son cinco subsistemas con
bloqueos externos distintos. Se ejecutan en orden; cada uno tiene su propia
verificación y su propio PR (o serie de PRs).

| # | Sub-proyecto | Depende de | Bloqueo externo | Milestone |
|---|---|---|---|---|
| **0** | Higiene de documentación | — | ninguno | — |
| **A** | Cableado del motor en el stream (backend) | 0 | ninguno | M2 |
| **B** | Frontend real de Etapa 2, sin mocks | A | ninguno | M2 |
| **C** | Gráficos interactivos | B | ninguno | M2 |
| **D** | Tests de regresión de Etapa 2 | A | **lo lleva Octavio — fuera de este plan**, ver §6 | M2 |
| **E** | Exportación PDF | A, B, C | FE-14 sin implementar | M3 |
| **F** | Agregación temporal y año hidrológico | 0 | parcial — ver §7 | M2 |

**F es independiente de A-E** y sale de un hallazgo de este mismo plan: METIS
acepta series mensuales y no las agrega, con consecuencias estadísticas
reales. Se puede ejecutar en paralelo con A. Está descrito en §7.

**El Bloque D no es de este plan** (Kevin, 09/08/2026): los tests de regresión
contra la tesis los está trabajando Octavio. La sección §6 se conserva como
insumo para él, no como tarea nuestra.

**E se especifica aparte.** Depende de una pieza que hoy no existe en ninguna
capa (fórmulas con valores sustituidos en modo paso a paso, FE-14) y de una
decisión de formato que no está tomada. Este plan define su alcance y sus
precondiciones (§7), no su implementación.

---

## 2. Bloque 0 — Higiene de documentación

Independiente de todo lo demás, barato, y saca ruido antes de agregar seis
documentos nuevos. **Correr después de que la pasada 5 del frontend esté
mergeada a `staging`** — hoy hay tres worktrees activos
(`.worktrees/feat/frontend-pasada5-bloque-*`) y tocar `sprint.md` ahora genera
conflictos innecesarios.

### 0.1 `docs/superpowers/` — evaluado, tiene valor, se conserva reubicado

Contenido real: un solo archivo, `plans/2026-07-22-frontend-fase0-scaffold.md`
(1493 líneas). Es el plan de implementación de la Fase 0 del frontend —
scaffold de Vite + React + TS, tokens del tema "Instrumento", 8 rutas stub,
conectividad verificada contra el backend. **Ya ejecutado y mergeado.**

Es el único registro de por qué el scaffold quedó como quedó (puerto 5173
atado a `FRONTEND_ORIGIN`, theming por CSS custom properties sin runtime CSS-in-JS,
proxy del dev server en vez de CORS real), y está citado desde dos lugares
vivos: `.claude/rules/sprint.md:481` y
`docs/frontend/frontend-implementation-plan.md:739`.

Encaja exactamente en el criterio de `docs/historico/README.md`: documento
superado por trabajo posterior, se conserva por trazabilidad.

- `git mv docs/superpowers/plans/2026-07-22-frontend-fase0-scaffold.md
  docs/historico/2026-07-22-frontend-fase0-scaffold.md`
- Borrar el directorio `docs/superpowers/` vacío.
- Entrada nueva en `docs/historico/README.md`, con el mismo formato que las
  dos existentes: qué era, cuándo se superó, qué lo reemplaza
  (`docs/frontend/frontend-implementation-plan.md` y el informe de Fases 1-6).
- Actualizar las dos referencias (`sprint.md:481`,
  `frontend-implementation-plan.md:739`) a la ruta nueva.
- Quitar del encabezado del archivo la línea *"For agentic workers: REQUIRED
  SUB-SKILL: Use superpowers:…"* — apunta a un flujo de trabajo que el
  proyecto ya no usa; reemplazarla por una nota de una línea diciendo que el
  plan está ejecutado y se conserva como registro.
- `docs/frontend/plan-arreglo-ui-rota.md:15` cita
  `superpowers:test-driven-development` para justificar la regla de "ningún
  arreglo sin su test rojo primero". La **regla** es correcta y sigue
  vigente; lo que ya no existe es la skill. Reescribir esa línea para que la
  regla se sostenga por sí sola, citando `.claude/rules/testing.md` en su
  lugar.

### 0.2 `.superpowers/` en la raíz — se borra, no se documenta

Estado interno de la herramienta (`sdd/progress.md` y once `.diff` de
revisiones). **Ya está en `.gitignore:57`**, nunca se commiteó, no hay nada
que preservar. `rm -rf .superpowers/`. Las entradas de `.gitignore` se
conservan: `.worktrees/` sigue en uso con git worktree plano.

### 0.3 Registrar el guard `p ∈ (0,1)` — Fase 4.5, cerrada sin registrarse

`sprint.md` lista la Fase 4.5 como "PENDIENTE PROPAGACIÓN" en 11
distribuciones. Está en las 13. El trabajo se hizo y nadie lo registró — que
es peor que no haberlo hecho, porque el próximo que lea `sprint.md` lo va a
implementar de nuevo.

Registrarlo en prosa no alcanza: una afirmación en un `.md` se vuelve a
desincronizar. Se cierra con las dos cosas:

- **Test que lo vuelve ejecutable.** `tests/unit/core/etapa2/test_cuantil_guard.py`,
  parametrizado sobre los 13 módulos de `distributions/`, verificando que
  `cuantil()` levanta `ValueError` para `p = 0`, `p = 1`, `p < 0` y `p > 1`.
  Descubre los módulos recorriendo `_DISTRIBUCIONES` de `pipeline_etapa2.py`,
  no una lista hardcodeada — así una distribución nueva entra al test sola.
  A partir de acá, la afirmación no puede desincronizarse en silencio.
- **`sprint.md`** — Fase 4.5 marcada COMPLETA con la fecha de verificación
  (09/08/2026), el comando que lo comprueba y el archivo de test que lo
  sostiene. La entrada de "PENDIENTE PROPAGACIÓN" no se borra: se tacha,
  igual que el resto de las correcciones históricas de ese archivo.

### 0.4 `docs/pendientes-tecnicos.md` — registro nuevo

Los tres directorios de test vacíos no tienen dónde vivir hoy.
`docs/auditoria/pendientes/` es para preguntas de dominio a Facundo;
`docs/decisiones/` es para decisiones tomadas; un plan como este se borra al
cerrarse. La deuda técnica conocida y sin dueño no tiene archivo — y por eso
se pierde.

Se crea `docs/pendientes-tecnicos.md`, indexado en `docs/README.md`: registro
vivo de lo que sabemos que falta y no es ni una decisión ni una pregunta de
dominio. Entradas de arranque:

| Pendiente | Estado |
|---|---|
| `tests/integration/` vacío (solo `__init__.py`) | Bloque A6 lo estrena |
| `tests/regression/` vacío | Lo lleva Octavio, fuera de este plan |
| `tests/e2e/` vacío | Sin plan — `constraints.md` excluye E2E de UI del scope V1.0, pero los E2E de API de `testing.md` §3 no están excluidos y tampoco existen |
| El job `test` de CI tolera exit code 5 | Deja de hacer falta cuando `integration/` tenga tests; quitar el flag en un PR propio |
| FE-16 — `Etapa1Result` no expone la serie cruda | Bloquea serie temporal, boxplot mensual y gráfico de Chow |
| `resolucion_temporal` se calcula y nunca se consume | Bloque F2.1 — hoy una serie mensual se analiza como si fuera anual |
| `_espaciado_regular()` da falso positivo en toda serie mensual | Bloque F2.2 |
| `_inferir_resolucion()` usa el promedio y no la moda de los deltas | Bloque F2.3 |
| MSW sin uso real si el Bloque B borra su último handler | Evaluar sacarlo del proyecto |
| `schemas/analysis.py::AnalysisRequest` código muerto | Se resuelve en A3 |

Cada entrada dice qué falta, qué bloquea y quién la cierra. Las que se cierran
se tachan con la fecha, no se borran — mismo criterio de trazabilidad que el
resto del proyecto.

### 0.5 Otras correcciones al estado documentado

- `.claude/rules/testing.md` — dejar explícito que `tests/integration/`,
  `tests/e2e/` y `tests/regression/` están vacíos y apuntar a
  `docs/pendientes-tecnicos.md`, para que la estrategia de cuatro niveles se
  lea como compromiso y no como estado.

### 0.6 Criterios de hecho

- `grep -rn "superpowers" --include=*.md . | grep -v ^./.worktrees` no devuelve
  ninguna referencia a una skill, solo la entrada de `docs/historico/README.md`.
- `ls docs/` no muestra `superpowers/`.
- `docs/historico/README.md` tiene tres entradas.
- `pytest tests/unit/core/etapa2/test_cuantil_guard.py -v` — 13 módulos × 4
  casos en verde.
- `docs/pendientes-tecnicos.md` creado y enlazado desde `docs/README.md`.
- Fase 4.5 marcada COMPLETA en `sprint.md`.

---

## 3. Bloque A — Cableado del motor en el stream (backend)

El bloque más grande y del que dependen todos los demás. Principio rector:
**Etapa 2 se cablea igual que Etapa 1, no de una forma nueva.** Cada pieza de
abajo tiene su equivalente exacto ya funcionando en el stream actual.

### A0 — Decisiones a escribir antes de tocar código

Cuatro decisiones nuevas. Los números asumen que **051 ya la tomó la pasada 5
del frontend** (salida de Three.js); verificar `docs/decisiones/README.md`
antes de escribir y correr los números si hace falta. Recordar que 046 (E2E
con Playwright) y 049 (escotilla SMTP) siguen reservadas y sin escribir.

| Decisión | Tema | Bloquea |
|---|---|---|
| **052** | Transporte de Etapa 2 por SSE con pausa; `distribution-decision` reemplaza `design-events` | A1, A4 |
| **053** | `session_store` con estado de sesión y TTL | A2 |
| **054** | `etapas` cableado de punta a punta — cierra DECISIÓN 037 | A3 |
| **055** | Etapa 2 no usa `full_pipeline.py` — por qué, y para qué queda | A5 |

Ninguna de las cuatro es opcional: las cuatro cambian un contrato ya escrito
en `.claude/rules/`, y la regla del proyecto es que un contrato no se cambia
en silencio.

### A1 — Contrato SSE, simétrico con Chow (DECISIÓN 052)

El stream ya sabe pausar y esperar al usuario. La secuencia actual es:

```
… → test_result(chow) → outlier_detected → [PAUSA] → test_result… → result_etapa1 → complete
                              ↑
              POST /analysis/outlier-decision  →  session_store.resolve_session()
```

Etapa 2 replica la misma forma, sin inventar un mecanismo nuevo:

```
result_etapa1 → progress(etapa 2) → result_etapa2_ranking → [PAUSA] → result_etapa2_eventos → complete
                                              ↑
                    POST /analysis/distribution-decision  →  session_store.resolve_session()
```

Condiciones para entrar a Etapa 2, en este orden:

1. `etapas == [1, 2]` (A3). Si es `[1]`, el stream termina como hoy.
2. `result_final.nivel_confianza != "rechazado"`. Es el único estado que
   bloquea — con warnings, incluso críticos, Etapa 2 corre igual. Está escrito
   en el docstring de `full_pipeline.py` y respaldado por el comportamiento de
   referencia de la tesis (estación Alpa Corral: rechazo unánime de Etapa 1,
   Etapa 2 se corrió igual).

**El endpoint.** `api-contracts.md` documenta `POST /analysis/design-events`
como un endpoint sincrónico que **devuelve** los eventos calculados. Con SSE
con pausa eso deja de tener sentido: los eventos viajan por el stream, y lo
que el cliente manda es una decisión. Se reemplaza por:

```
POST /api/v1/analysis/distribution-decision
Request:  {"session_id": "...", "distribucion": "gumbel", "metodo": "momentos",
           "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500]}
Auth:     JWT opcional (igual que el stream activo)
Response: {"ok": true, "pipeline_continua": true}
Errores:  404 SESSION_NOT_FOUND, 400 DIST_SELECTION_INVALID
```

Misma forma que `outlier-decision`, misma respuesta, mismo mecanismo de
desbloqueo. `design-events` queda documentado en `api-contracts.md` como
**reemplazado por este**, con el porqué — no se borra la entrada, se marca.

`periodos_retorno` se valida en el borde: lista no vacía, todos `> 1`
(`F = 1 - 1/T` necesita `T > 1` para caer en `(0,1)`), máximo 20 elementos.
Fuera de eso → `DIST_SELECTION_INVALID`.

**Dos códigos de error nuevos.** `SESSION_NOT_FOUND` y `DIST_SELECTION_INVALID`
van a `api-contracts.md` **y** a `frontend/src/i18n/errors.es.ts` en el mismo
commit que los introduce, o el job `error-catalog` de CI se pone rojo — el
script chequea las tres direcciones y `DIST`/`SESSION` ya son prefijos
reconocidos (`scripts/check-error-catalog.sh:22`). Es la regla que dejó
DECISIÓN 038.

### A2 — `session_store` con estado y TTL (DECISIÓN 053)

Hoy son dos diccionarios sueltos:

```python
_store: dict[str, asyncio.Event] = {}
_decisions: dict[str, str] = {}
```

Pasa a uno solo, con una dataclass — sin cambiar la interfaz pública que
`analysis_service.py` ya usa (`create_session`, `wait_for_decision`,
`resolve_session`, `get_decision`, `remove_session`), para que el camino de
Chow no se toque:

```python
@dataclass
class SessionState:
    event: asyncio.Event
    decision: dict | None = None        # era str — ahora payload completo
    serie: list[float] | None = None
    tiene_ceros: bool = False
    etapa2: Etapa2Result | None = None
    created_at: float = field(default_factory=time.monotonic)
```

Tres cambios de comportamiento:

- **`decision` pasa de `str` a `dict`.** Chow manda `{"decision": "rechazar"}`,
  la selección de distribución manda el payload de A1. Un solo mecanismo para
  las dos pausas; `get_decision()` devuelve el dict y cada consumidor lee lo
  suyo.
- **El stream guarda `serie`, `tiene_ceros` y el `Etapa2Result`** antes de
  pausar. Sin eso, la selección de distribución no tiene los parámetros
  ajustados y habría que reajustar todo de nuevo.
- **Barrido por TTL.** Hoy una sesión solo se limpia si el `finally` de
  `stream_etapa1()` corre. Si el cliente corta la conexión de una forma que
  no dispara el `finally`, la entrada queda para siempre — y ahora cada
  entrada carga la serie completa y el `Etapa2Result` de 13 distribuciones,
  no un `Event` vacío. Se agrega `sweep_expired()` con la misma constante de
  300s (`SESSION_TIMEOUT`), llamado al principio de `create_session()`: sin
  tarea de fondo, sin `asyncio.create_task`, sin nada que pueda quedar
  colgado. Barrido perezoso, suficiente para el volumen real de este sistema.

`SessionState` no persiste nada en BD, así que **CU-01 y CU-02 usan el mismo
camino** — que es la razón por la que se eligió esta opción y no leer de
`analysis_id`, que sería exclusiva de CU-01.

### A3 — `etapas` de punta a punta (DECISIÓN 054, cierra DECISIÓN 037)

Cuatro capas, en orden:

1. **`api/v1/analysis.py`** — `etapas: str = Form("1")` se parsea a
   `list[int]`. Solo se aceptan `"1"` y `"1,2"`; cualquier otra cosa →
   400 `CONTRACT_ETAPAS_INVALID` (tercer código nuevo, mismo tratamiento de
   catálogo que los dos de A1). El parseo vive en el borde, igual que
   `cramer_particion` desde DECISIÓN 036 — el core nunca ve un string.
2. **`stream_etapa1()`** — recibe `etapas: list[int]` y decide si entra a
   Etapa 2. El nombre de la función queda mal (ya no es solo Etapa 1):
   renombrar a `stream_analysis()`, con el `import` actualizado en
   `api/v1/analysis.py`. Es el único renombre del bloque.
3. **`schemas/analysis.py::AnalysisRequest`** — hoy es código muerto que
   ninguna ruta importa. Se decide una de dos y se documenta en la 054: o se
   cablea como el modelo real del request, o se borra. **Recomendado
   borrarlo**: el endpoint es `multipart/form-data` con un `UploadFile`, que
   no se modela bien con un `BaseModel` plano, y mantener un modelo paralelo
   que nadie valida es exactamente lo que produjo DECISIÓN 037.
4. **`frontend/src/api/analysis.ts`** — el `FormData` empieza a mandar
   `etapas`. Hoy no lo manda en absoluto.

### A4 — Eventos de diseño (módulo nuevo en `core/`)

`core/etapa2/design_events.py`, función pura, sin conocimiento de HTTP ni de
sesiones — la restricción de aislamiento de `core/` aplica igual:

```python
def calcular_eventos_diseno(
    modulo,                      # el módulo de la distribución
    parametros: dict,
    periodos_retorno: list[float],
) -> list[EventoDiseno]:
    # F = 1 - 1/T   (Weibull, coherente con empirical.py)
    # xT = modulo.cuantil(F, parametros)
```

`EventoDiseno` ya existe en `etapa2/types.py`. El guard `p ∈ (0,1)` ya está en
las 13 `cuantil()`, así que un `T` inválido levanta `ValueError` en el core y
no hay que duplicar la validación — pero A1 igual valida `T > 1` en el borde
para devolver un 400 legible en vez de un 500.

Un `T` que haga fallar `cuantil()` para una distribución particular no puede
tumbar el request entero: se registra ese evento con `valor: null` y se sigue.
Es el mismo principio que rige todo Etapa 2 — ningún caso especial detiene el
pipeline.

Tests unitarios propios en `tests/unit/core/etapa2/test_design_events.py`,
con al menos un caso verificado a mano contra la tesis.

### A5 — Serialización, orquestación y `full_pipeline.py` (DECISIÓN 055)

**`_serializar_etapa2()`** en `analysis_service.py`, hermana exacta de
`_serializar_etapa1()`. Serializa el `Etapa2Result` completo: las 13
distribuciones, todos sus métodos con `status` y `eea`, `mejor_metodo`,
`mejor_eea`, `n_parametros` y los `warnings` (`DIST_HIGH_EEA`). **No aplana el
resultado a un top-3.** La grilla completa —incluidos los `no_converge`,
`no_aplicable` y `disabled_zeros`— es el valor docente del sistema: la tesis
misma reporta que GVE/Momentos y Gen. Pareto/MV no convergen, y eso es
información, no un error a esconder.

**`full_pipeline.py` no se usa desde `services/`** y eso es deliberado, no un
descuido: `ejecutar_pipeline_completo()` corre las dos etapas de un tirón, y
el stream necesita emitir Etapa 1 prueba por prueba y pausar en Chow antes de
que Etapa 2 empiece. `analysis_service` llama `ejecutar_etapa1()` (con su
bucle de re-ejecución por Chow, como hoy) y después `ejecutar_etapa2()`
directo.

`full_pipeline.py` **no se borra**: pasa a ser la función que consumen los
tests de regresión del Bloque D, que sí quieren las dos etapas de un tirón sin
streaming. Se le agrega al docstring la nota de por qué `services/` no la usa
— si no, el próximo que la lea va a pensar que es un olvido y la va a cablear.

**Persistencia.** `_persistir()` pasa a recibir `etapas` real y el
`Etapa2Result`, y escribe `etapa1`, `etapa2` y `decisiones` (que ahora incluye
la distribución y el método elegidos por el usuario — es registro de auditoría
de CU-01, igual que la decisión ante el atípico). Sin migración: la columna
`etapa2` ya existe.

### A6 — Tests

- **Unitarios** (`tests/unit/`): `design_events.py`, `_serializar_etapa2()`,
  el parseo de `etapas`, y `session_store` con `SessionState` + TTL.
- **Integración** (`tests/integration/`): **este bloque estrena el
  directorio.** Un test que corre el stream completo con `etapas=[1,2]` sobre
  una serie de fixture, consume los eventos SSE en orden, manda la selección
  de distribución y verifica que llegan `result_etapa2_eventos` y `complete`.
  Es la única forma de verificar la pausa sin un navegador.
- El job `test` de CI ya corre `pytest -m "unit or integration"` y tolera exit
  code 5 — con este bloque deja de hacer falta esa tolerancia, pero **no se
  quita el flag** en este PR (un cambio de CI y un cambio de features no van
  juntos).

### A7 — Criterios de hecho del Bloque A

- `docker exec <backend> pytest -m "unit or integration" -v` en verde, con los
  tests nuevos de A6.
- `ruff check metis/` y `ruff format --check metis/` limpios.
- `./scripts/check-error-catalog.sh` en verde con los tres códigos nuevos.
- Smoke test manual con `curl` contra el backend real: `POST /analysis/stream`
  con `etapas=1,2` sobre un CSV de 40 años emite `result_etapa2_ranking`;
  `POST /analysis/distribution-decision` desbloquea el stream y llegan
  `result_etapa2_eventos` y `complete`.
- Con `etapas=1` el stream se comporta **exactamente** como hoy — el camino de
  Etapa 1 no cambió.
- Un análisis de CU-01 queda persistido con `etapas=["1","2"]` y
  `analysis_results.etapa2` no nulo (verificar con `psql`).
- Las cuatro decisiones (052-055) escritas y en `docs/decisiones/README.md`.

---

## 4. Bloque B — Frontend real de Etapa 2

### B0 — El mock cumplió su función; reemplazarlo no es desenchufarlo

El mock de Etapa 2 existió para que el flujo completo fuera navegable mientras
el frontend se construía, y para eso sirvió (DECISIÓN 042). Su vida útil
termina acá: se borra sin ceremonia. Lo que sí importa es que **reemplazarlo
es más que cambiar el origen de los datos.**

`RankingItem` es plano: `{distribucion, metodo, eea, rank}`. El resultado real
es una lista de `DistResult`, cada uno con N `MetodoResult` que llevan `status`
(`ok`, `no_converge`, `no_aplicable`, `disabled_zeros`) y `eea` posiblemente
`null`. La maqueta de tres tarjetas nunca mostró un método que falla, y esos
casos son la mitad de lo que un alumno tiene que ver.

Es un rediseño de pantalla, no un cambio de origen de datos.

### B1 — Tipos y cliente

- `api/types.ts` — `RankingItem` se reemplaza por `Etapa2Result`,
  `DistribucionResult`, `MetodoResult` y `EventoDiseno`, derivados del shape
  real de `_serializar_etapa2()`. El comentario actual que aclara que
  `RankingItem` "es un shape de ejemplo, no una interfaz derivada de
  `api-contracts.md`" se borra: ahora sí lo es.
- `api/sse.ts` — `useAnalysisStream` maneja tres eventos nuevos:
  `result_etapa2_ranking` (fase `waiting_distribution`),
  `result_etapa2_eventos` y el `progress` de etapa 2. **Cuidado con el bug ya
  conocido:** `result_etapa1` no llegaba a `state.result` porque `onmessage`
  no desenvolvía ese evento en particular (corregido en Fase 2, con test de
  regresión en `sse.test.ts`). Los tres eventos nuevos necesitan el mismo
  tratamiento y el mismo test.
- `api/analysis.ts` — `postDistributionDecision()`, hermana de
  `postOutlierDecision()`. `postDesignEvents()` se borra.
- `mocks/` — se borran `etapa2.mock.ts`, `designEvents.mock.ts` y el handler
  de `design-events` en `handlers.ts`. Si `handlers.ts` queda sin handlers,
  se evalúa sacar MSW del proyecto entero (era su único uso real, ver
  DECISIÓN 041/042) — decisión a tomar en el PR, con su nota.
- `PendingBadge` desaparece de `RankingPage` y `DesignEventsPage`.

### B2 — `RankingPage` rediseñada

Una fila por distribución, ordenada por `mejor_eea` ascendente (el orden ya
viene resuelto del backend — el frontend **no** reordena ni recalcula el
ranking). Cada fila:

- Nombre, `n_parametros`, mejor EEA y mejor método.
- Expandible: la grilla de sus métodos con `eea` y `status`. Los métodos que
  fallaron se muestran con su motivo (`no converge`, `no aplicable`,
  `deshabilitada por ceros`), nunca ocultos.
- Botón "Elegir" por método, no por distribución — el usuario elige el par
  distribución+método, que es lo que `distribution-decision` recibe.

Regla de producto que no se negocia (`constraints.md`): **METIS no sugiere
ganadora.** Se puede decir "menor EEA" como hecho objetivo en la primera fila
—como ya hace el mock— pero ninguna etiqueta puede decir "recomendada",
"óptima" ni "ganadora".

Los `warnings` de `DIST_HIGH_EEA` se muestran como banner, con el mismo
componente que Etapa 1 ya usa.

### B3 — `DesignEventsPage`

Deja de hacer una llamada REST propia: los eventos llegan por el stream. La
pantalla pasa a ser presentacional sobre el `result_etapa2_eventos` que
`useAnalysisStream` ya tiene en estado, más la selección de períodos de
retorno, que ahora se manda **antes** (en `distribution-decision`) en vez de
después.

Consecuencia de UX a resolver en el PR: los períodos de retorno se eligen en
`RankingPage`, junto con la distribución, no en `DesignEventsPage`. Se
propone un selector de períodos en el pie de `RankingPage` con el default de
`api-contracts.md` (`[2, 5, 10, 25, 50, 100, 200, 500]`) preseleccionado.

### B4 — Historial y modos

- `HistoryDetailPage` — muestra Etapa 2 cuando `AnalysisDetail.etapa2` no es
  nulo, con el mismo componente presentacional de `RankingPage` (mismo patrón
  que `Etapa1ResultView`, reutilizado entre `/results` y el detalle).
- **Modo paso a paso vs. experto también aplica a Etapa 2.** Hoy el modo solo
  se respeta en Etapa 1. En paso a paso, cada distribución explica qué es el
  EEA y por qué un método no converge; en experto, la grilla directa. Es la
  razón de ser del software — no puede quedar afuera.
- `ConfigPage` — el selector de alcance (`etapas`) no existe todavía. Se
  agrega: "Solo validación (Etapa 1)" / "Validación + análisis de frecuencia
  (Etapa 1 y 2)", que es lo que alimenta A3.

### B5 — Tests y criterios de hecho

- Mismo patrón de mock que toda la suite: `vi.stubGlobal("fetch", …)` y
  `vi.mock("@microsoft/fetch-event-source")`, **nunca MSW en un test**
  (DECISIÓN 041). Todo test de página bajo `<StrictMode>` vía `renderPage`.
- Test de integración de `StreamPage` que cubra el segundo punto de pausa,
  hermano del que ya existe para Chow.
- `npm run lint && npm test && npm run build` en verde.
- `grep -rn "mock" frontend/src/routes/ranking frontend/src/routes/design-events`
  vacío.
- Verificación manual en navegador contra el backend real, en los dos temas y
  en los dos modos, **después del último commit del PR** (Capa 4 de
  `testing.md`).

---

## 5. Bloque C — Gráficos interactivos

### C1 — Librería (DECISIÓN 056)

Requisitos: zoom, tooltip con el valor exacto de x e y en cada punto,
tematizable con los tokens del design system, testeable en jsdom, y sin
volver a inflar el bundle (la pasada 5 acaba de sacar Three.js).

| Opción | Peso | Problema |
|---|---|---|
| Recharts | ~100 kB gz | Pelea con el tema; tematizar es sobreescribir su sistema |
| uPlot | ~15 kB | Canvas — jsdom no lo implementa, mismo dolor que los fondos |
| **`d3-scale` + `d3-shape` + SVG propio** | **~10 kB** | Zoom y tooltip se escriben a mano (~150 líneas) |

**Recomendado: `d3-scale` + `d3-shape` con SVG propio.** Se tematiza con
`var(--acc)` como cualquier otro componente, se testea con
`getByRole`/`getByText` sobre SVG real, y el zoom/tooltip escrito a mano es
código que entendemos y podemos defender ante el tribunal — que es el
criterio que rige todo este proyecto.

### C2 — Los dos gráficos

- **Gráfico de ajuste** — puntos empíricos (Weibull, `probabilidades_weibull`
  ya los calcula) contra la curva de la distribución ajustada. Requiere que el
  backend exponga las probabilidades empíricas y la serie ordenada en
  `_serializar_etapa2()` — **verificar en el Bloque A que van en el payload**,
  o C queda bloqueado por un cambio de contrato.
- **Eventos de diseño** — `xT` contra `T`, eje x logarítmico.

Interacción, común a los dos: zoom por rueda y por selección de rectángulo,
reset a la vista completa, tooltip al hover con `(x, y)` exactos, teclado
(flechas para moverse entre puntos, respetando `prefers-reduced-motion` para
las transiciones).

### C3 — El toggle calendario/hidrológico se elimina de estos dos gráficos

`constraints.md:50` y `statistical-pipeline.md:259` definen los dos años:
calendario (1 ene → 31 dic) e hidrológico (**1 jul → 30 jun** del año
siguiente — el de la región centro de Argentina, que arranca después del
estiaje invernal). Los dos archivos coinciden; no hay ambigüedad en la fecha.

Donde sí hay un problema es en **qué significa el toggle**. La diferencia
entre los dos años es el mes en que empieza el año, y eso decide **qué valor
cae en qué año** — o sea, decide la serie de máximos anuales. Cambiar de
calendario a hidrológico no reetiqueta un eje: cambia la muestra, y con ella
los parámetros ajustados, el EEA, el ranking completo y los eventos de diseño.
Es una regla de agregación que vive **aguas arriba de Etapa 1**, no una opción
de presentación aguas abajo de Etapa 2.

La maqueta actual pone el toggle dentro de cada tarjeta del ranking, como si
fuera una opción de dibujo (y con un bug ya registrado: D5 de la pasada 2 —
el estado es único a nivel página pero el control se renderiza por tarjeta,
así que tocarlo en una las cambia todas). Implementado así, el toggle no
puede producir el resultado correcto: llega demasiado tarde en el pipeline.

**El problema real es que METIS hoy no puede hacer esa agregación.** El
contrato de entrada es una columna X (año) y una columna Y (valor): la serie
llega **ya agregada a paso anual**. La decisión calendario/hidrológico la tomó
quien preparó el archivo, antes de subirlo. Para que METIS la ofreciera de
verdad haría falta que el archivo trajera datos sub-anuales y que el sistema
construyera los máximos anuales él mismo — `parser.py` ya infiere
`resolucion_temporal` de los timestamps, así que la información para detectar
el caso existe, pero nada la usa para agregar.

**Decisión tomada (Kevin, 09/08/2026): el toggle se elimina** del gráfico de
ajuste y del de eventos de diseño. Un control que no puede cambiar el
resultado que promete es peor que no tenerlo, y el bug D5 confirma que hoy ni
siquiera hace lo poco que aparenta. La elección de año pasa a resolverse donde
corresponde —en la construcción de la serie, Bloque F (§7)— y en estos dos
gráficos se convierte, a lo sumo, en un **rótulo** que dice con qué criterio
se construyó la serie que se está viendo.

La forma de ese rótulo depende del Bloque F y se implementa ahí, no acá. Este
bloque solo saca el control.

Donde la regla de "dos versiones" sí aplica sin ninguna duda y hoy no está
implementada: serie temporal, boxplot mensual y gráfico de Chow. Los tres
tienen eje temporal real, y los tres necesitan la serie cruda, que
`Etapa1Result` no expone (FE-16) — fuera de alcance de este plan, anotado en
`docs/pendientes-tecnicos.md`.

### C4 — Criterios de hecho

- Zoom, reset, tooltip y navegación por teclado verificados a mano en los dos
  gráficos, en los dos temas.
- `npm run build` — el aumento de bundle registrado en el informe de cierre y
  por debajo de 15 kB gz.
- Tests de los componentes de gráfico sobre SVG real, sin snapshots.
- El toggle calendario/hidrológico ya no aparece en el gráfico de ajuste ni en
  el de eventos de diseño, y el bug D5 de la pasada 2 queda cerrado por
  eliminación del control (registrarlo así, no como "corregido").

---

## 6. Bloque D — Tests de regresión de Etapa 2 (LO LLEVA OCTAVIO)

> **Fuera del alcance de este plan (Kevin, 09/08/2026).** Confirmado con
> Octavio: los tests de regresión contra la tesis los está trabajando él. Lo
> que sigue es el análisis que produjo este plan, conservado por si le sirve
> como insumo — no es una tarea de este frente y ningún PR de §9 lo cubre.
>
> **Lo único que sí nos toca es el punto de contacto:** si el Bloque F cambia
> cómo se construye la serie anual, los fixtures de regresión tienen que
> conocer con qué `mes_inicio_anio` se armaron las 9 estaciones de la tesis —
> ver F6.3. Avisarle a Octavio cuando la 057 se escriba.

### D1 — El bloqueo es parcial, no total

M1 lista "tests de regresión matemática" como bloqueado esperando las series
de las 9 estaciones en formato digital. Eso sigue siendo cierto **para cerrar
el criterio tal como está redactado**. Pero
`docs/auditoria/regresion/regresion-e2e-coreEstadistico/est_01..09-e2e.md` ya
tiene las nueve estaciones transcriptas del PDF de la tesis, con sus
resultados esperados, del análisis E2E cerrado el 15/07/2026.

Se pueblan los fixtures desde ahí. Cada fixture lleva en su docstring, de
forma explícita, que los valores son **transcripción manual del PDF**, no un
archivo digital nativo de Facundo. Cuando llegue el archivo, se reemplaza la
fuente sin tocar los tests.

### D2 — Forma

`tests/regression/test_etapa2_estaciones.py`, `@pytest.mark.regression`,
parametrizado sobre las 9 estaciones, consumiendo
`ejecutar_pipeline_completo()` (que es para lo que queda viva, A5). Verifica
el ranking por EEA, los parámetros de las distribuciones que la tesis reporta,
y —tan importante como lo anterior— que **las combinaciones que la tesis marca
como no convergentes sigan sin converger**. Un test que empieza a converger
donde la tesis no lo hace es una regresión, no una mejora.

Tolerancia `pytest.approx(..., rel=1e-4)`, salvo donde la auditoría ya
documentó una discrepancia conocida — esos casos se marcan con `xfail` que
cita el pendiente correspondiente, nunca se ajusta la tolerancia para que
pase.

### D3 — Lo que sigue pendiente con Facundo, y no lo desbloquea este bloque

- Comportamiento ante ceros de 5 distribuciones (`gamma3p`,
  `exponencial_x0_beta`, `gen_pareto`, `lognormal3p`, `gen_exponencial`) —
  `PENDING_ZEROS_CONFIRMATION` sigue en `True` en el código.
- ME y MC en otras distribuciones.
- Gamma 3p + MPP: la Tabla IV-1 dice "Sí" y el capítulo IV no desarrolla las
  ecuaciones.
- Mann-Kendall Tabla A.4, n=7.

Los cuatro están en `pendientes-facundo.md`. Los tests de regresión se
escriben sobre lo que sí está confirmado; los casos pendientes se marcan
`skip` con la referencia al pendiente, para que aparezcan en la salida de
pytest y no se olviden.

### D4 — Criterios de hecho

- `pytest -m regression -v` corre las 9 estaciones y pasa.
- Ningún test ajusta tolerancia para pasar; las discrepancias conocidas son
  `xfail` con referencia.
- `.claude/rules/testing.md` actualizado: `tests/regression/` deja de estar
  vacío.
- `sprint.md` — M1/M2 actualizados con qué cubre esta suite y qué sigue
  esperando el archivo digital.

---

## 7. Bloque F — Agregación temporal y año hidrológico

Hallazgo de este plan, no de la lista original. Es independiente de A-E y
puede ejecutarse en paralelo con A.

### F1 — Lo que la documentación dice, y lo que no

Buscado en `.claude/rules/`, `docs/decisiones/`, `docs/auditoria/` y
`docs/frontend/`:

**Lo que sí está escrito.** El año hidrológico es **1 julio → 30 junio** del
año siguiente (`constraints.md:50`, `statistical-pipeline.md:259`, coinciden).
Todo gráfico con eje temporal lleva las dos versiones. Ojo: los dos archivos
lo escriben como una constante del sistema, no como el valor de la región
centro del país — ver F3, donde eso se corrige.

**Lo que no está escrito en ninguna parte:**

- Cómo se construye la serie anual a partir de datos sub-anuales. Ninguna
  regla de agregación, en ningún archivo.
- Qué se hace con los años incompletos — el registro que arranca en marzo, o
  cuya cantidad de meses no es múltiplo de 12.
- Cuál de los dos años es el criterio **del análisis** (no del gráfico). La
  documentación solo exige las dos versiones para graficar; nunca dice cuál
  manda para construir la muestra.
- Las 9 estaciones de `docs/auditoria/` son "caudales máximos anuales" sin
  explicitar con qué criterio de año se armaron — en la tesis la serie ya
  viene construida.

Es un hueco real del contrato de datos, no algo que se nos haya pasado leer.

### F2 — Dos bugs encontrados al buscarlo

**F2.1 — `resolucion_temporal` se calcula y no se usa nunca.**
`ParsedData.resolucion_temporal` es `"anual" | "mensual" | None`
(`core/types.py:75`) — el sistema **sí contempla entrada mensual**. Pero
`grep -rn "resolucion_temporal" backend/metis` muestra que el único consumidor
del valor es `contract.py:26`, y solo evalúa `if resolucion_temporal is None`.
Nadie mira nunca si dice `"mensual"`.

Consecuencia: una serie mensual entra al pipeline y se le corren Anderson,
Wald-Wolfowitz, Helmert, t de Student, Cramer, Mann-Kendall, KS, Chow y el
ajuste de las 13 distribuciones **sobre los valores mensuales crudos**, como
si fueran máximos anuales. No falla ni advierte: devuelve un resultado con la
forma correcta y sin sentido hidrológico. Peor: la estacionalidad rompe
independencia y homogeneidad por construcción, así que el usuario ve warnings
críticos que son un artefacto del bug y no una propiedad de sus datos.

**F2.2 — toda serie mensual dispara `CONTRACT_IRREGULAR_SPACING`.**
`contract.py::_espaciado_regular()` compara los deltas exactos entre
timestamps y exige `len(set(diffs)) == 1`. Los meses duran 28, 30 o 31 días.
Falso positivo garantizado para el 100% de las series mensuales.

**F2.3 — `_inferir_resolucion()` usa el promedio, no la moda.**
`(ts[-1] - ts[0]) / (len(ts) - 1)`: una serie mensual con un hueco largo puede
inferirse como `"anual"` y pasar sin que nada lo note. No es tan grave como
las dos anteriores, pero es la misma familia de problema.

Los tres se corrigen en este bloque. F2.1 y F2.2 son bugs de contrato de
datos, no features — se pueden arreglar sin esperar ninguna respuesta.

### F3 — Mes de inicio del año, configurable (decisión de Kevin, 09/08/2026)

El año hidrológico **no es una constante**: cambia según la zona del país.
`constraints.md:50` fija julio-junio, que es el de la región centro donde
están las 9 estaciones de la tesis, pero eso es un **valor por defecto
razonable, no una regla universal**. Un registro del NOA, de la cuenca del
Plata o de la Patagonia arranca en otro mes.

Por lo tanto: **el mes de inicio del año se configura antes de correr el
análisis, y puede ser cualquiera de los 12.**

Esto simplifica el modelo en vez de complicarlo. Deja de haber dos
"modalidades" (calendario vs. hidrológico) con un toggle entre ellas: hay **un
solo parámetro**, `mes_inicio_anio ∈ [1..12]`. El año calendario es
simplemente `mes_inicio_anio = 1` — un caso particular, no un modo aparte. La
dicotomía que `constraints.md` describía era una simplificación de esto.

Este es también el motivo profundo por el que el toggle de C3 no podía
funcionar: no era una opción binaria de presentación, era un parámetro de
construcción de la muestra con doce valores posibles.

**Parámetro nuevo, de punta a punta:**

| Capa | Cambio |
|---|---|
| `POST /analysis/stream` | Campo `mes_inicio_anio: int` (`Form`), default `7`, validado en `[1..12]` → 400 `CONTRACT_MES_INICIO_INVALID` |
| `core/validacion/` | Módulo nuevo `aggregation.py`, función pura |
| `analyses.configuracion` (JSONB) | Se guarda junto a `cramer_particion` — es registro de auditoría, el resultado no se puede reproducir sin él |
| `ConfigPage` | Selector de mes (§F5) |
| Gráficos y PDF | Rótulo: "año hidrológico: junio–mayo" |

`mes_inicio_anio` **no es opcional en el registro de auditoría**: dos análisis
sobre el mismo archivo con meses distintos dan series distintas y resultados
distintos. Sin guardarlo, el historial de CU-01 muestra un resultado que no se
puede volver a producir.

### F4 — La agregación y el recorte de los extremos

Módulo nuevo `core/validacion/aggregation.py`, función pura, sin conocimiento
de HTTP ni de BD — la restricción de aislamiento de `core/` aplica igual:

```python
def agregar_a_maximos_anuales(
    serie: list[float],
    timestamps: list,
    mes_inicio: int,
) -> AgregacionResult:
    ...
```

Devuelve la serie anual, los timestamps de cada año agregado, y la lista de
períodos descartados con su motivo, para que el pipeline pueda emitir los
warnings.

**Regla de recorte en los dos extremos (decisión de Kevin, 09/08/2026).**
El registro casi nunca arranca justo en el mes de inicio ni termina justo en
el mes de cierre. Los datos que sobran en cualquiera de los dos extremos **se
descartan**:

- *Inicio.* Si `mes_inicio = 6` y el registro arranca en marzo de 2001, los
  meses marzo–mayo de 2001 no forman un año completo: se descartan. El primer
  año del análisis es junio 2001 – mayo 2002.
- *Fin.* Si el mismo registro termina en agosto de 2010, los meses junio–agosto
  de 2010 no llegan a cerrar el año: se descartan. El último año del análisis
  es junio 2009 – mayo 2010.

En otras palabras, el registro se **recorta a años completos**. No se completa,
no se interpola, no se acepta un año parcial "casi lleno" en los extremos —
`constraints.md` es explícito en que METIS no corrige datos, y el máximo de un
año parcial está sesgado a la baja por construcción.

Se emite un warning **no bloqueante**, `CONTRACT_PARTIAL_YEARS_TRIMMED`, que
dice cuántos meses se descartaron en cada extremo y cuál es el período
efectivo del análisis. El usuario tiene que ver qué se recortó: es la
diferencia entre "descartar" y "borrar en silencio".

**Etiquetado del año agregado.** Un año junio 2001 – mayo 2002 se etiqueta con
el año calendario **en que empieza** (2001). Con `mes_inicio = 1` esto degenera
exactamente en el año calendario, lo que sirve de verificación de consistencia
del propio algoritmo. La convención se documenta explícitamente porque cambia
el eje X de todos los gráficos temporales y el rótulo de los resultados.

**El recorte ocurre antes del conteo de n.** Un registro de 12 años que pierde
los dos extremos entra a Etapa 1 con n=10, y si eso lo deja bajo el piso
bloquea con `CONTRACT_SERIES_TOO_SHORT` como cualquier serie corta. Es
coherente con la regla existente, no una excepción nueva.

**Dónde se llama.** Al principio de `ejecutar_etapa1()`, antes de
`validar_contrato()` — no en `services/`. Así el conteo de la regla de n opera
ya sobre la serie agregada, `services/` no gana lógica de dominio, y se
respeta "el pipeline siempre arranca por Etapa 1".

**El caso que Kevin no especificó, y que hay que resolver igual: el hueco
interior.** Los extremos están definidos; un año del medio al que le faltan
meses (una estación fuera de servicio seis meses en 2007) no. No es lo mismo
que un extremo: recortarlo partiría el registro en dos. Propuesta, a confirmar
en F6: se descarta ese año y se emite
`CONTRACT_INCOMPLETE_YEARS_DISCARDED` — código distinto del recorte de
extremos, porque significa otra cosa (hay un agujero en el registro, no un
borde). La serie resultante queda con un salto temporal, que `contract.py` ya
detecta como `CONTRACT_IRREGULAR_SPACING`. Con eso, los tres warnings juntos
cuentan la historia completa sin que ninguno mienta.

**Función de agregación.** Máximo por año, que es lo que corresponde al
análisis de frecuencia de eventos extremos y a lo que hace la tesis. Para
`tipo_variable == "otro"` el máximo puede no ser lo que el usuario quiere —
queda en F6.

### F5 — Frontend

**Selector de mes en `ConfigPage`.** Doce opciones, con el rango visible en la
etiqueta ("Junio — el año va de junio a mayo"), default julio, y una nota de
una línea explicando que define cómo se agrupan los datos en años.

**Cuándo mostrarlo.** Si la columna X son años de 4 dígitos, la serie ya viene
anual y el selector no cambia nada. `ConfigPage` ya tiene la heurística para
detectarlo: `pareceFechaOAnio()` distingue `/^\d{4}$/` de una fecha completa, y
el panel de muestra de columnas de la pasada 5 ya tiene los valores a mano.
Regla: **el selector se muestra habilitado solo cuando la columna X elegida
tiene fechas completas**; con años puros se muestra deshabilitado, con la nota
de que la serie ya está agregada. El campo se manda siempre — el backend lo
ignora cuando la resolución es anual, y así el frontend no necesita adivinar
nada que el backend no pueda re-verificar.

**Resultados.** El período efectivo del análisis y el criterio de año se
muestran junto a la estadística descriptiva, y el warning de recorte con el
mismo componente de banner que el resto de Etapa 1.

### F6 — Decisión, y lo que queda para Facundo

**DECISIÓN 057 — Agregación temporal por año hidrológico configurable.** Cubre
F3, F4 y F5, los tres bugs de F2 y los tres códigos de error nuevos. El mes
configurable y el recorte de extremos son decisión de producto ya tomada
(Kevin, 09/08/2026) y se documentan como tal.

Lo que sigue siendo dominio y va a
`docs/auditoria/pendientes/pendientes-facundo.md`:

1. **Hueco interior.** ¿Se descarta el año incompleto del medio, o hay un
   umbral de meses mínimos por debajo del cual recién se descarta? Nuestra
   posición: descartar el que no tenga los 12.
2. **Función de agregación para `tipo_variable == "otro"`.** Máximo anual es
   correcto para caudal y precipitación. ¿Y para una variable arbitraria?
3. **Las 9 estaciones de la tesis, ¿con qué mes de inicio se armaron?** No
   cambia la implementación, pero sí los fixtures del Bloque D: si se armaron
   por año calendario, un test de regresión que agregue por julio no las
   reproduce.

Ninguna de las tres bloquea F2, F3 ni el grueso de F4 — solo el hueco interior
y el caso `otro`.

### F7 — Criterios de hecho

- F2.1: una serie mensual ya no atraviesa el pipeline como si fuera anual —
  se agrega, siempre.
- F2.2: una serie mensual real de 10 años no dispara
  `CONTRACT_IRREGULAR_SPACING`. Test unitario con meses de 28/30/31 días.
- F2.3: `_inferir_resolucion()` usa la moda de los deltas; test con una serie
  mensual con un hueco de 14 meses que antes se inferían como `"anual"`.
- **Tests de `agregar_a_maximos_anuales()`**, uno por caso:
  - registro que arranca y termina justo en el mes de inicio (sin recorte);
  - arranca tarde (recorte de inicio, el ejemplo de marzo con `mes_inicio=6`);
  - termina temprano (recorte de fin, el ejemplo de agosto);
  - los dos extremos parciales a la vez;
  - `mes_inicio = 1` reproduce exactamente el año calendario;
  - `mes_inicio = 12` (caso borde: el año cruza el cambio de año calendario
    con un solo mes del lado viejo);
  - el recorte deja n < 10 → `CONTRACT_SERIES_TOO_SHORT` bloqueante;
  - año interior incompleto (según lo que se resuelva en F6.1).
- `mes_inicio_anio` fuera de `[1..12]` → 400 `CONTRACT_MES_INICIO_INVALID`.
- `analyses.configuracion` guarda `mes_inicio_anio`; verificado con `psql` en
  un análisis de CU-01.
- `./scripts/check-error-catalog.sh` verde con los tres códigos nuevos.
- Verificación manual: mismo archivo mensual analizado con `mes_inicio = 1` y
  con `mes_inicio = 7` produce series anuales distintas, y el warning de
  recorte dice qué meses se descartaron en cada caso.
- DECISIÓN 057 escrita.

---

## 8. Bloque E — Exportación PDF (spec aparte)

**No se implementa con este plan.** Se define acá su alcance y sus
precondiciones para que quede claro qué falta.

Precondiciones que hoy no se cumplen:

1. **FE-14 — fórmulas con valores sustituidos** en modo paso a paso. No existe
   en ninguna capa: ni el backend expone los términos intermedios de cada
   fórmula, ni el frontend los renderiza. `constraints.md` lo exige
   explícitamente para el PDF en modo paso a paso.
2. **Los gráficos tienen que existir en el PDF.** Con la decisión de graficar
   en el frontend (C1), el PDF necesita o un render server-side aparte, o que
   el cliente mande los SVG generados. Es exactamente la decisión que se
   difirió al elegir "datos crudos ahora, PNG después" — hay que tomarla acá.
3. `GET /export/{id}` no existe. `constraints.md` fija que se genera
   on-demand y no se almacena en disco.
4. El contenido varía según lo ejecutado (solo Etapa 1 vs. completo) y según
   el modo — cuatro combinaciones, cada una con su plantilla.

Su spec sale cuando A, B y C estén cerrados y FE-14 tenga una decisión.

---

## 9. Orden de ejecución y PRs

| PR | Bloque | Sale de | Depende de |
|---|---|---|---|
| 1 | 0 — higiene de documentación | `staging` | pasada 5 mergeada |
| 2 | A0 — las cuatro decisiones (052-055) | `staging` | PR 1 |
| 3 | A1-A3 — contrato SSE, `session_store`, `etapas` | `staging` | PR 2 |
| 4 | A4-A6 — eventos de diseño, serialización, persistencia, tests | `staging` | PR 3 |
| 5 | B — frontend real | `staging` | PR 4 |
| 6 | C — gráficos | `staging` | PR 5 |
| 7 | F2 — los tres bugs de contrato temporal | `staging` | PR 1 |
| 8 | F3-F4 — mes configurable, agregación y recorte (backend) | `staging` | PR 7 |
| 9 | F5 — selector de mes y período efectivo (frontend) | `staging` | PR 8 |

El Bloque D no tiene PR acá — lo lleva Octavio (§6).

PR 7 no depende de ninguno de A-C: son bugs aislados de `core/validacion/`.
PR 8 y 9 tampoco esperan a nadie — con el mes configurable y el recorte de
extremos ya decididos, lo único que sigue abierto con Facundo es el hueco
interior y el caso `tipo_variable == "otro"` (F6), que se pueden implementar
con la propuesta y ajustar después si responde distinto. **Conviene mandarle
las tres preguntas de F6 al abrir el PR 7**, no cuando el PR 8 esté escrito.

**Coordinación con Octavio:** el PR 8 cambia cómo se construye la serie anual.
Avisarle antes de mergearlo — sus fixtures de regresión asumen las series de
la tesis tal como están, y F6.3 es justamente la pregunta de con qué mes se
armaron.

---

## 10. Definition of done — todos los PRs

1. Backend: `pytest -m "unit or integration"`, `ruff check`, `ruff format
   --check` — dentro del contenedor, no contra el Python del host.
2. Frontend: `npm run lint && npm test && npm run build`.
3. Los cuatro jobs de `ci.yml` en verde, incluido `error-catalog`.
4. **Evidencia de navegador** para todo PR que toque `frontend/`, tomada
   después del último commit del PR, en los dos temas.
5. Ninguna decisión de arquitectura tomada en el código sin su archivo en
   `docs/decisiones/` — es la regla que pediste explícitamente y la que
   sostiene la defensa ante el tribunal.
6. Ninguna aserción de test existente modificada sin justificarlo en el PR.

---

## 11. Documentación a actualizar al cerrar

- `docs/decisiones/` — 052 a 057 escritas, indexadas en `README.md`.
- `docs/decisiones/decision037.md` — marcada como cerrada por la 054.
- `docs/decisiones/decision042.md` — marcada como superada (los mocks ya no
  existen).
- `.claude/rules/architecture/api-contracts.md` — `distribution-decision`
  documentado, `design-events` marcado como reemplazado, seis códigos de error
  nuevos en el catálogo (tres de A1/A3 más `CONTRACT_MES_INICIO_INVALID`,
  `CONTRACT_PARTIAL_YEARS_TRIMMED` y `CONTRACT_INCOMPLETE_YEARS_DISCARDED` del
  Bloque F), `etapas` y `mes_inicio_anio` con sus valores válidos.
- `.claude/rules/core/statistical-pipeline.md` — la secuencia real de eventos
  SSE de Etapa 2, con la pausa; y la regla de agregación temporal del Bloque F,
  que hoy no está escrita en ninguna parte.
- `.claude/rules/architecture/constraints.md` — **corregir** la sección "Año
  hidrológico": hoy fija julio-junio como constante del sistema, y pasa a ser
  el default de un parámetro configurable en los 12 meses. Sumar el recorte de
  extremos y el criterio de etiquetado del año agregado.
- `.claude/rules/testing.md` — `tests/integration/` deja de estar vacío.
  (`tests/regression/` lo cierra Octavio por su lado.)
- `.claude/rules/sprint.md` — M2 y su estado; Fase 4.5 marcada COMPLETA; nota
  de que los tests de regresión los lleva Octavio, para que el próximo que lea
  M1/M2 no los tome como pendiente sin dueño.
- `CLAUDE.md` — "Frontend — estado actual": Etapa 2 deja de estar mockeada.
- `docs/auditoria/pendientes/pendientes-facundo.md` — las tres preguntas de F6.
- `docs/pendientes-tecnicos.md` — creado en el Bloque 0, y actualizado a medida
  que cada bloque cierra sus entradas.
- `docs/README.md` — índice con `pendientes-tecnicos.md`.
- **Este archivo se elimina** cuando los siete PRs estén mergeados. Lo que
  quede sin cerrar en ese momento se migra a `docs/pendientes-tecnicos.md`
  antes de borrarlo — no se pierde nada por borrar un plan.
