# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# METIS — Contexto del Proyecto

## Qué es METIS

Software estadístico con enfoque docente para análisis de frecuencia de eventos extremos hidrológicos. Automatiza un pipeline de validación estadística (Etapa 1) y análisis de frecuencia (Etapa 2) actualmente ejecutado manualmente en Excel por el co-director Facundo Ganancias.

**Proyecto Integrador de grado** — Ingeniería en Sistemas de Información, UCC 2026.
**Autores:** Octavio Carpineti, Kevin Massholder.
**Directores:** Dr. Ing. Carlos Catalini, Mgter. Ing. Facundo Ganancias.
**Repositorio:** https://github.com/CarpinetiOctavio/PI_METIS

Se defenderá ante un tribunal de ISI — todas las decisiones técnicas deben poder justificarse desde ingeniería de software, no desde el dominio hidráulico.

---

## Stack definitivo — no cambiar sin consultar

| Capa | Tecnología |
|------|-----------|
| Backend | Python + FastAPI |
| ORM | SQLAlchemy |
| Base de datos | PostgreSQL |
| Frontend | React + TypeScript |
| Contenedores | Docker + Docker Compose |
| Reverse proxy | Nginx |
| Linting backend | ruff |
| Linting frontend | ESLint |

---

## Estructura de módulos del backend — respetar estrictamente

Todo el código Python vive bajo `backend/`; los comandos de este repo (pytest, ruff, uvicorn) se corren con `backend/` como working directory.

```
backend/metis/
├── api/v1/               # Controllers: endpoints, contratos request/response. Sin lógica de negocio.
│   ├── analysis.py       # /analysis/stream (SSE), /outlier-decision, /preview-columns, /distribution-decision, /{id}
│   ├── history.py        # /history/, /history/{id}, /history/{id}/archive|unarchive
│   └── export.py         # GET /export/{id}, POST /export/{id}/simulacion — PDF de CU-01 (DECISIÓN 075)
├── core/                 # Motor estadístico. SIN conocimiento de HTTP, BD, ni sesiones.
│   ├── estadistica_descriptiva/   # descriptive.py
│   ├── etapa1/            # independence.py, homogeneity.py, trend.py, outliers.py (Chow)
│   ├── etapa2/            # eea.py, empirical.py, design_events.py, utils.py, types.py, distributions/ (13 archivos)
│   ├── pipeline/          # pipeline_etapa1.py, pipeline_etapa2.py, full_pipeline.py, types.py,
│   │                      # exclusiones.py (what-if de atípicos — DECISIÓN 071)
│   ├── validacion/        # contract.py (validación de contrato de datos), parser.py,
│   │                      # aggregation.py (mensual/diaria → máximos anuales — DECISIÓN 057/065)
│   ├── types.py, utils.py
├── services/              # Orquestación: analysis_service.py (pipeline + SSE + persistencia), session_store.py,
│                          # export_service.py
├── reportes/              # pdf.py — informe PDF (ReportLab + matplotlib). Presentación pura: recibe el dict de
│                          # get_analysis_by_id(), no importa api/services/db/core (DECISIÓN 075)
├── db/                    # models/ (user, analysis, result, api_client) + base.py, session.py
├── schemas/               # Modelos Pydantic: analysis.py, auth.py, common.py
└── auth/                  # router.py, jwt.py, email.py (aiosmtplib), dependencies.py
```

**Regla crítica:** `core/` no importa nada de `api/`, `services/`, `db/` ni `auth/`. El motor estadístico es una librería pura — recibe datos, devuelve resultados. Esto es lo que hace posible los tests de regresión matemática.

### Flujo del stream SSE — lo que hay que leer en varios archivos para entender

`POST /analysis/stream` (`api/v1/analysis.py`) valida parámetros en el borde (`etapas`, `mes_inicio_anio`, `variable_diaria`, `cramer_particion`, tope de 10 MB) y delega a `services/analysis_service.py::stream_analysis()`, un generador async que orquesta todo: parsea con `core/validacion/parser.py`, corre `ejecutar_etapa1()` (paso 0a orden cronológico → paso 0 agregación → contrato → pruebas → Chow) y, si `etapas=[1,2]` y el resultado no es `rechazado`, `ejecutar_etapa2()`.

El stream **se pausa dos veces** (atípico de Chow; elección de distribución+método) esperando un `POST` aparte (`/outlier-decision`, `/distribution-decision`) que llega por otro request y desbloquea vía `services/session_store.py` (`SessionState` con `asyncio.Event` y TTL, en memoria del proceso). El mismo `Event` sirve para las dos pausas — se hace `.clear()` antes de la segunda espera.

Tras rechazar un atípico o para alimentar Etapa 2, usar `Etapa1Result.serie_efectiva`/`timestamps_efectivos` (la serie realmente analizada, ya agregada), **nunca** `serie_original` (la cruda subida) — mapear el índice de Chow contra la serie cruda borra un dato equivocado. Ambas listas se filtran de a pares (`core/utils.py::filtrar_numericos_alineados`) y quedan siempre del mismo largo, aun con celdas vacías en una carga anual — antes de eso el parser conservaba los `None` solo en los timestamps y las etiquetas de año se corrían (`docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md`). `core/pipeline/full_pipeline.py` no lo usa `services/` (DECISIÓN 055); existe para los tests de regresión. Detalle de eventos y payloads: `.claude/rules/core/statistical-pipeline.md`.

---

## Comandos esenciales

Backend — correr siempre con `backend/` como working directory. Los comandos de abajo asumen
`pip install -r requirements.txt` corrido en el Python que los ejecuta — **no asumir que el
Python del host lo tiene**: si no hay un `venv` del proyecto activado, corren contra el sistema
sin `sqlalchemy`/`aiosmtplib`/etc. instalados y fallan en el import. Verificado el 29/07/2026
(pasada 3): en esa máquina, sin `venv`, la ruta que sí corre reproduciblemente es dentro del
contenedor Docker (`docker exec <backend> pytest ...`, ver abajo). El conteo de tests cambia
con cada PR — no fiarse de un número escrito acá; el último registrado está en `docs/sprint.md`.

```bash
cd backend

# Servidor de desarrollo
uvicorn metis.main:app --reload --port 8000

# Todos los tests
pytest -v

# Solo una capa (markers definidos en pytest.ini): unit | integration | e2e | regression
pytest -m unit -v

# Un solo archivo o test puntual
pytest tests/unit/core/etapa1/test_independence.py -v
pytest tests/unit/core/etapa1/test_independence.py::test_anderson_manda_sobre_wald -v

# Linting — corre en CI (.github/workflows/ci.yml), correr antes de cada commit
ruff check metis/
ruff format metis/
```

**Sin `venv` local — correr todo lo de arriba dentro del contenedor:**

```bash
docker-compose up -d backend postgres
docker ps  # confirmar el nombre real del contenedor — el prefijo lo decide Docker Compose
           # a partir del nombre del directorio y ya cambió una vez en este repo
           # (pi-postgres-1 vs. pi_metis-postgres-1, ver docs/sprint.md)
docker exec <backend> ruff check metis/
docker exec <backend> ruff format --check metis/
docker exec <backend> pytest -m unit -v
```

Frontend — correr siempre con `frontend/` como working directory (ver [frontend/README.md](frontend/README.md)):

```bash
cd frontend
npm install
npm run dev       # Vite dev server, http://localhost:5173 — proxy /api y /ping hacia localhost:8000
npm run build     # tsc -b + build de producción a dist/
npm run lint      # ESLint
npm test          # Vitest + Testing Library, todos los tests (modo run, no watch)
npm run test:watch                            # Vitest en modo watch
npx vitest run src/routes/results/ResultsPage.test.tsx   # un solo archivo de test
```

Entorno completo (Docker):

```bash
docker-compose up --build
```

**Migraciones (`backend/alembic/versions/`, escritas a mano, no autogeneradas) — correrlas después de levantar `postgres`, no es automático.** Nada en
`backend/Dockerfile`, `docker-compose.yml` ni `metis/main.py` corre `alembic upgrade head`
ni crea tablas al arrancar (confirmado: `db/session.py` solo abre el engine, no llama
`Base.metadata.create_all()`). Una base de datos nueva queda sin ninguna tabla hasta que se
corre manualmente. Encontrado el 05/08/2026 en una BD local desactualizada (parada en la
migración `003`, sin `analyses.archivado_at` de `DECISIÓN 048`): `GET /history/` respondía
500 `UndefinedColumnError` en vez de un error controlado.

```bash
docker exec <backend> alembic upgrade head
```

Ver `.claude/rules/architecture/architecture.md` — sección "Exposición de puertos en desarrollo" para por qué `backend` y `postgres` mapean puertos al host, y "DATABASE_URL — diferencia entre Docker y host" para el override de Alembic/psql desde la terminal local.

**CI (`.github/workflows/ci.yml`)** corre en cada push/PR a `staging`/`main`: job `lint` (ruff check + format --check), job `test` (`pytest -m "unit or integration"`, exit code 5 tolerado — `tests/integration/` ya tiene tests reales, así que la tolerancia sobra y queda por sacar en un PR propio; `tests/e2e/` y `tests/regression/` siguen vacíos), job `error-catalog` (`scripts/check-error-catalog.sh` — verifica en las tres direcciones que todo código de error emitido por el backend, documentado en `api-contracts.md` y usado en `frontend/src/i18n/errors.es.ts` esté sincronizado; excepciones legítimas van en `scripts/error-catalog-allowlist.txt`, ver DECISIÓN 038), job `frontend` (lint + test + build). No mergear sin que los cuatro pasen.

**SonarCloud** analiza cada PR además de estos jobs — no vía un paso propio de `ci.yml`, sino por
Análisis Automático (App de GitHub de SonarCloud). Hoy el check no es *required* en el Ruleset, así
que es consultivo, no bloqueante. **Exclusiones de Sonar van en `.sonarcloud.properties`** (raíz): el
Análisis Automático ignora `sonar-project.properties` — sus exclusiones nunca se aplicaron hasta el
addendum del 02/10/2026. Ver [decision044.md](docs/decisiones/decision044.md).

### Reglas de flujo de trabajo que no se deducen del código

- **Código de error nuevo** (emitido por `core/`/`services/`/`api/`, o inventado por el frontend): se agrega a `api-contracts.md` y a `frontend/src/i18n/errors.es.ts` **en el mismo commit** — si no, falla el job `error-catalog`.
- **`docs/decisiones/decisionNNN.md` nuevo:** hacer `git fetch` y comparar el número más alto contra `origin/staging` antes de elegir NNN (hay ramas en paralelo). Hay números reservados sin archivo (035, 046, 049, 072) — no reutilizarlos.
- **PR que toca `frontend/`:** además de lint + test + build, correr el flujo en el navegador después del último commit y dejar evidencia (captura o pestaña Network). Los tests bajo `StrictMode` no reemplazan esto — ver `.claude/rules/testing.md`, "Capa 4".
- **Ramas:** `feature/xxx` / `fix/xxx` salen de `staging` y vuelven a `staging` por PR; `main` solo recibe PRs desde `staging`. Push directo bloqueado por Ruleset.

### Scripts de desarrollo — `scripts/`

- `seed-dev-user.sh [email]` / `clean-dev-user.sh [email]` — crean/borran un usuario ya verificado directo en Postgres (bcrypt vía el Python del contenedor backend), evitando el flujo `register`→`verify` que requiere SMTP real (no disponible en desarrollo local, ver DECISIÓN 032/034 y `docs/sprint.md`).
- `check-error-catalog.sh` — corre en el job `error-catalog` de CI (ver arriba); verifica en tres direcciones que todo código de error emitido por el backend, documentado en `api-contracts.md` y traducido en `frontend/src/i18n/errors.es.ts`, esté sincronizado. Excepciones legítimas van en `error-catalog-allowlist.txt` (DECISIÓN 038).

---

## Frontend — estado actual

Vite + React + TypeScript + react-router-dom, 7 pantallas de CU-01/CU-02: `entry`, `config`, `stream`, `results`, `history` (lista y detalle), `auth-verify` (`frontend/src/routes/`, tabla de rutas en `frontend/src/routes.tsx`).

```
frontend/src/
├── api/           # Cliente HTTP: client.ts (ApiError/requestJson), auth.ts, analysis.ts,
│                  # history.ts, sse.ts (SSE-sobre-fetch, hook useAnalysisStream — DECISIÓN 040), types.ts
├── auth/          # AuthProvider.tsx (sesión), guards.tsx (RequireAuth/RequireSession/RedirectIfAuthed)
├── charts/        # InteractiveChart.tsx (SVG propio, d3-scale+d3-shape — DECISIÓN 056), BoxPlot.tsx, Sparkline.tsx
├── components/    # RootLayout, TopBar, fondos animados Canvas 2D, BlockMath (KaTeX)
├── i18n/          # errors.es.ts (traducción del catálogo de códigos), mesInicioAnio.ts
├── routes/        # entry/, config/, stream/, results/, history/, auth-verify/ — una carpeta por pantalla
├── theme/         # tokens.ts + tokens.instrumento.css (paridad verificada por tokenParity.test.ts)
└── test/          # renderPage.tsx — helper que envuelve toda página en <StrictMode> (regla, no opcional)
```

Tema visual fijo "Instrumento" (claro/oscuro, no seleccionable por el usuario) en `frontend/src/theme/` — `tokens.ts` y `tokens.instrumento.css` deben mantenerse en paridad (verificado por `tokenParity.test.ts`).

Lo que no se deduce leyendo un solo archivo:

- **Las pausas del stream se resuelven dentro de `StreamPage`.** El atípico de Chow es un modal; la elección de distribución, un ranking inline (`Etapa2RankingView`). No hay rutas `/ranking` ni `/design-events`. Los componentes de `src/routes/results/` se reusan en modo interactivo (`StreamPage`) y de solo lectura (`ResultsPage`, `HistoryDetailPage`).
- **"Explorar no es decidir" (DECISIÓN 062).** `Etapa2Explorador` recalcula con `POST /analysis/{id}/design-events` y la simulación de exclusión pega a `POST /analysis/simulate-exclusion` (DECISIÓN 071). Ninguna de las dos toca la elección registrada, y el recálculo vive en `core/`, nunca en TypeScript.
- **El frontend no decide por el usuario.** Las dos opciones de una decisión (rechazar/aceptar atípico) se presentan con el mismo peso visual — sin botón primario ni efectos en uno solo. El ranking de Etapa 2 ordena por EEA pero no marca ganadora.
- **Gráficos:** SVG propio sobre `d3-scale`+`d3-shape` (`src/charts/InteractiveChart.tsx`, DECISIÓN 056), sin librería de charting. No sumar Recharts/three/etc. sin una decisión (DECISIÓN 051).
- **Lo que solo existe en la sesión interactiva:** `curva_ajuste` no se persiste, así que el gráfico de ajuste no aparece en `HistoryDetailPage`.

Historia de cómo se llegó a esto (fases 1-6, pasadas de mejora 2-5, planes de Etapa 2 y de feedback de directores): [`docs/planes-implementados.md`](docs/planes-implementados.md), con los planes originales archivados en `docs/historico/planes/`; decisión por decisión del frontend, [`docs/frontend/frontend-implementation-plan.md`](docs/frontend/frontend-implementation-plan.md) §10. Lo que sigue abierto del feedback de directores está en `docs/checklist-pendientes-feedback-directores.md`; **ese backend lo hacen Kevin y Claude desde el 01/10/2026** (Octavio sin tiempo): se puede tocar `backend/` con el estilo del resto, sumando a Octavio como reviewer sin bloquear en su aprobación.

**Testing del frontend — un solo mecanismo de mock de red.** Toda la suite usa `vi.stubGlobal("fetch", ...)` (Vitest + Testing Library). MSW salió del proyecto por completo el 09/08/2026 (Bloque B5 del plan de Etapa 2) — no queda ninguna dependencia `msw` en `package.json`; no reintroducirla. Ver `docs/decisiones/decision041.md` y [frontend/README.md](frontend/README.md) — sección "Testing".

---

## Tres casos de uso — diferencias críticas

| Atributo | CU-01 Docencia | CU-02 Anónimo | CU-03 API |
|----------|---------------|--------------|----------|
| Autenticación | JWT (@ucc.edu.ar) | Sin auth | API Key |
| Persistencia | Sí | No | No |
| Etapa 2 | Sí, selección manual | Sí, selección manual | No |
| Modos | Paso a paso / Experto | Solo resultados | — |
| Exportación | PDF | No | JSON estructurado |
| Decisiones guardadas | Sí | No | Automáticas (auto_clean) |

**La distinción CU-01 vs CU-02 no se resuelve por ruta — se resuelve por presencia de JWT.** Misma ruta `/api/v1/analysis/stream`, comportamiento distinto según autenticación.

---

## Endpoints — estructura definitiva

**Hay cuatro routers montados en `main.py` — auth, analysis, history, export.** `POST /validate/` (CU-03, con `X-API-Key`) está en el contrato pero **no existe todavía**; tampoco la gestión de API Keys — `db/models/api_client.py` está modelado y nada lo importa. No asumir que responden.

```
POST   /api/v1/auth/register
POST   /api/v1/auth/verify
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
POST   /api/v1/analysis/stream            # SSE — CU-01 y CU-02
POST   /api/v1/analysis/outlier-decision  # Decisión ante atípico Chow — CU-01 y CU-02
POST   /api/v1/analysis/preview-columns   # Columnas + muestra para los dropdowns de ConfigPage (DECISIÓN 047)
POST   /api/v1/analysis/distribution-decision  # Reemplaza design-events (DECISIÓN 052) — selección de distribución+método, desbloquea el stream — CU-01 y CU-02
POST   /api/v1/analysis/{id}/design-events     # Recálculo stateless desde el historial (DECISIÓN 062) — JWT requerido, no toca session_store ni decisiones
POST   /api/v1/analysis/simulate-exclusion     # What-if de atípicos (DECISIÓN 071) — sin auth ni estado: recalcula Etapa 1 (y 2) sin los puntos excluidos
GET    /api/v1/analysis/{id}              # Consulta análisis persistido — CU-01
GET    /api/v1/history/                   # ?archivados=true incluye archivados (DECISIÓN 048)
GET    /api/v1/history/{id}
POST   /api/v1/history/{id}/archive       # soft-delete — DECISIÓN 048
POST   /api/v1/history/{id}/unarchive
GET    /api/v1/export/{id}                # PDF on-demand, siempre formato Experto — CU-01 (DECISIÓN 075)
POST   /api/v1/export/{id}/simulacion     # El mismo PDF + resultados sin los puntos excluidos (DECISIÓN 071/075)
POST   /api/v1/validate/                  # CU-03, sincrónico, solo Etapa 1 — SIN IMPLEMENTAR
```

---

## Seguridad

Reglas no negociables (JWT en HttpOnly Cookie, API Key en `X-API-Key` y guardada como hash, credenciales solo en `.env`, CORS estricto, HTTPS en producción): `.claude/rules/architecture/constraints.md`, sección "Seguridad".

---

## Principio de negocio central — no violar

METIS detecta y advierte, pero **no bloquea** — excepto dos excepciones reales:

- **< 10 datos → error bloqueante.** Pipeline se detiene.
- **Timestamps fuera de orden cronológico → error bloqueante.** Pipeline se detiene, evaluado antes que cualquier otra cosa (incluida la agregación temporal mensual o diaria) — DECISIÓN 030, cerrada 18/08/2026 (Bloque H3 del plan post-avance). Datos faltantes NO son desorden y no bloquean — la distinción es exclusivamente sobre el orden temporal, nunca sobre la completitud. Ver docs/decisiones/decision030.md y `.claude/rules/core/statistical-pipeline.md`, "Paso 0a".
- **10–29 datos → warning no bloqueante.** Pipeline continúa. Responsabilidad del usuario.
- **≥ 30 datos → condiciones recomendables.** Sin warning por longitud.

**El sistema no garantiza resultados fuera del contrato.** Toda decisión ante un warning es responsabilidad del usuario y queda registrada en el historial (CU-01).

---

## Referencias

**Todo lo que está bajo `.claude/rules/` se carga solo en cada sesión** — no hace falta leerlo a mano, y todo lo que se agregue ahí pesa en el contexto de cada sesión. Por eso el estado del sprint vive fuera:

- `.claude/rules/architecture/` — `architecture.md` (decisiones con justificación), `constraints.md` (restricciones, pendientes, scope), `api-contracts.md` (contratos y catálogo de errores).
- `.claude/rules/core/` — `statistical-pipeline.md` (lógica de Etapa 1 y 2, eventos SSE), `core-etapa{1,2}-implementation.md` (librerías y restricciones del motor), `formulas-etapa{1,2}.md` (fórmula ↔ ecuación de la tesis — **ninguna fórmula se implementa sin referencia explícita ahí**).
- `.claude/rules/testing.md` — estrategia de testing del backend y del frontend.

Para consultar cuando el trabajo lo amerite (no se cargan solos):

- `docs/sprint.md` — registro cronológico del sprint (~100 KB, ~1600 líneas). Ubicar la sección con `Grep '^## '` y leer solo esa; las entradas de estado puntuales pueden estar atrasadas respecto de `git log`/`gh pr list`, que mandan.
- `docs/planes-implementados.md` — índice de todos los planes ejecutados, con PRs, decisiones y qué quedó abierto.
- `docs/decisiones/README.md` — índice de decisiones tomadas, descartadas o reemplazadas (una por archivo, `decisionNNN.md`), transversal a todo el proyecto. Consultar cuando algo en el código no coincida con una decisión vigente.
- `docs/auditoria/` — fases de auditoría, regresión numérica contra la tesis de Facundo y pendientes sin resolver (`pendientes/pendientes-facundo.md`). `hallazgos/` reúne verificaciones dirigidas a un tema puntual. Ver `docs/README.md`.
- `docs/pendientes-tecnicos.md` — deuda técnica abierta y cerrada, con fecha y qué la cerró. Consultar antes de asumir que algo "no está hecho".
- `docs/historico/` — documentos superados, conservados por trazabilidad.

## Documentación en Obsidian
Cada vez que se ejecute /init en este repositorio, revisar también la documentación del proyecto en el vault de Obsidian ubicado en C:\Users\kevin\OneDrive\Documents\Kevin\Proyectos\PI_METIS\ y actualizarla si hay cambios relevantes en el código que no estén reflejados ahí.
