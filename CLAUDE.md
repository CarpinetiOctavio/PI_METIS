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
│   └── history.py        # /history/, /history/{id}, /history/{id}/archive|unarchive
├── core/                 # Motor estadístico. SIN conocimiento de HTTP, BD, ni sesiones.
│   ├── estadistica_descriptiva/   # descriptive.py
│   ├── etapa1/            # independence.py, homogeneity.py, trend.py, outliers.py (Chow)
│   ├── etapa2/            # eea.py, empirical.py, utils.py, types.py, distributions/ (13 archivos)
│   ├── pipeline/          # pipeline_etapa1.py, pipeline_etapa2.py, full_pipeline.py, types.py
│   ├── validacion/        # contract.py (validación de contrato de datos), parser.py
│   ├── types.py, utils.py
├── services/              # Orquestación: analysis_service.py (pipeline + SSE + persistencia), session_store.py
├── db/                    # models/ (user, analysis, result, api_client) + base.py, session.py
├── schemas/               # Modelos Pydantic: analysis.py, auth.py, common.py
└── auth/                  # router.py, jwt.py, email.py (aiosmtplib), dependencies.py
```

**Regla crítica:** `core/` no importa nada de `api/`, `services/`, `db/` ni `auth/`. El motor estadístico es una librería pura — recibe datos, devuelve resultados. Esto es lo que hace posible los tests de regresión matemática.

---

## Comandos esenciales

Backend — correr siempre con `backend/` como working directory. Los comandos de abajo asumen
`pip install -r requirements.txt` corrido en el Python que los ejecuta — **no asumir que el
Python del host lo tiene**: si no hay un `venv` del proyecto activado, corren contra el sistema
sin `sqlalchemy`/`aiosmtplib`/etc. instalados y fallan en el import. Verificado el 29/07/2026
(pasada 3): en esa máquina, sin `venv`, la ruta que sí corre reproduciblemente es dentro del
contenedor Docker — 131 passed, 1 skipped.

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
           # (pi-postgres-1 vs. pi_metis-postgres-1, ver sprint.md)
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

**Correr las migraciones después de levantar `postgres` — no es automático.** Nada en
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

**CI (`.github/workflows/ci.yml`)** corre en cada push/PR a `staging`/`main`: job `lint` (ruff check + format --check), job `test` (`pytest -m "unit or integration"`, exit code 5 tolerado — no hay tests de integración todavía), job `error-catalog` (`scripts/check-error-catalog.sh` — verifica en las tres direcciones que todo código de error emitido por el backend, documentado en `api-contracts.md` y usado en `frontend/src/i18n/errors.es.ts` esté sincronizado; excepciones legítimas van en `scripts/error-catalog-allowlist.txt`, ver DECISIÓN 038), job `frontend` (lint + test + build). No mergear sin que los cuatro pasen.

**SonarCloud** analiza cada PR además de estos jobs — no vía un paso propio de `ci.yml`, sino por
Análisis Automático (App de GitHub de SonarCloud). Hoy el check no es *required* en el Ruleset, así
que es consultivo, no bloqueante. Ver [decision044.md](docs/decisiones/decision044.md).

---

## Frontend — estado actual

Vite + React + TypeScript + react-router-dom, 7 pantallas de CU-01/CU-02: `entry`, `config`, `stream`, `results`, `history` (lista y detalle), `auth-verify` (`frontend/src/routes/`, tabla de rutas en `frontend/src/routes.tsx`). Las rutas `/ranking` y `/design-events` que existían en el scaffold original ya no están — desde el Bloque B del plan de Etapa 2 (09/08/2026) el ranking y los eventos de diseño se muestran inline dentro de `StreamPage` mientras el stream está pausado. Tema visual fijo "Instrumento" (claro/oscuro, no seleccionable por el usuario) en `frontend/src/theme/` — `tokens.ts` y `tokens.instrumento.css` deben mantenerse en paridad (verificado por `tokenParity.test.ts`).

**Ya no es scaffold** — Fases 1 a 5 del plan de integración están completas con integración real contra el backend (verificado contra Docker): auth end-to-end (`src/auth/`), stream de Etapa 1 vía SSE-sobre-fetch (`src/api/sse.ts`, hook `useAnalysisStream` — ver `docs/decisiones/decision040.md`), los tres modos de presentación de resultados de Etapa 1, historial con lista paginada y detalle. **Etapa 2 dejó de ser mock el 09/08/2026** (Bloque B del plan de implementación de Etapa 2, ver `sprint.md`): `PendingBadge` y `src/mocks/` (MSW) se borraron por completo, igual que las rutas `/ranking` y `/design-events` — el ranking real y los eventos de diseño se muestran inline dentro de `StreamPage` mientras el stream está pausado (`Etapa2RankingView`/`Etapa2EventosView` en `src/routes/results/`, reusados de solo lectura en `ResultsPage` e `HistoryDetailPage`). `docs/decisiones/decision042.md` documenta el mock original y su addendum de cierre. **Gráficos interactivos agregados el 11/08/2026** (Bloque C del plan de implementación de Etapa 2, DECISIÓN 056): `Etapa2AjusteChart` (puntos empíricos vs. curva ajustada) y `Etapa2EventosChart` (xT vs. T), ambos sobre un componente SVG propio (`src/charts/InteractiveChart.tsx`, `d3-scale`+`d3-shape`, sin librería de charting completa) con zoom, tooltip y navegación por teclado — montados dentro de `Etapa2EventosView`, sin el toggle calendario/hidrológico que la maqueta original ponía por tarjeta (retirado, no trasladado — el criterio de año es una regla de agregación de Etapa 1 que todavía no existe, ver `sprint.md`, Bloque F). Fase 6 (pulido y accesibilidad) quedó parcial. Verificación E2E contra backend real: login/logout/me, Config→stream con atípico real, los tres modos de Resultados e Historial cerrados; solo el tramo registro→verify de Auth sigue bloqueado por falta de SMTP real en desarrollo. Punto de entrada para retomar el estado exacto: [`docs/frontend/informe-implementacion-frontend-fase1-6.md`](docs/frontend/informe-implementacion-frontend-fase1-6.md) (resumen navegable) y [`docs/frontend/frontend-implementation-plan.md`](docs/frontend/frontend-implementation-plan.md) §10 (fuente de verdad decisión por decisión).

**Pasada 4 de mejora (31/07-01/08/2026):** tipografía real (JetBrains Mono cargada de verdad, no solo declarada en tokens), tokens de movimiento + regla universal de `prefers-reduced-motion`, estados de interacción (hover/active/focus-visible) en todo el design system, dos fondos animados en Canvas 2D (`DotFieldBackground`, `GridScanBackground` — DECISIÓN 045), `TopBar` reescrito dentro del design system, columnas de `ConfigPage` pobladas por dropdown real vía `POST /analysis/preview-columns` (DECISIÓN 047), archivado de historial por soft-delete (DECISIÓN 048) y texto de `PendingBadge` reformulado. Tres PRs apilados — ver [`docs/frontend/informe-resultados-pasada4.md`](docs/frontend/informe-resultados-pasada4.md) para el detalle completo y el estado exacto de verificación de cada bloque.

**Pasada 5 de mejora (06-09/08/2026):** paridad del tema claro para los fondos animados (token `--glow`, separado de `--acc` — DECISIÓN 043 de contraste sigue pendiente y sin resolver acá), tercer fondo animado (`ThreadsBackground`) reescrito de Three.js a Canvas 2D y montado en todas las pantallas — `three`/`@types/three` fuera del proyecto por completo (DECISIÓN 051, supera el addendum de DECISIÓN 045), elevación de cards con sombra (`--elev-1`/`--elev-2`) y spotlight más leve, `TopBar` como cluster de vidrio, dropzone real reemplazando el `<input type="file">` nativo en `ConfigPage` + panel de muestra de columnas (`ColumnPreviewPanel`, layout responsive `.config-shell`), y blur del scrim en el modal de atípico de Chow. Cuatro PRs apilados — ver [`docs/frontend/informe-resultados-pasada5.md`](docs/frontend/informe-resultados-pasada5.md) para el detalle completo y el estado exacto de verificación de cada bloque.

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
POST   /api/v1/auth/register
POST   /api/v1/auth/verify
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
POST   /api/v1/analysis/stream            # SSE — CU-01 y CU-02
POST   /api/v1/analysis/outlier-decision  # Decisión ante atípico Chow — CU-01 y CU-02
POST   /api/v1/analysis/preview-columns   # Columnas + muestra para los dropdowns de ConfigPage (DECISIÓN 047)
POST   /api/v1/analysis/distribution-decision  # Reemplaza design-events (DECISIÓN 052) — selección de distribución+método, desbloquea el stream — CU-01 y CU-02
GET    /api/v1/analysis/{id}              # Consulta análisis persistido — CU-01
GET    /api/v1/history/                   # ?archivados=true incluye archivados (DECISIÓN 048)
GET    /api/v1/history/{id}
POST   /api/v1/history/{id}/archive       # soft-delete — DECISIÓN 048
POST   /api/v1/history/{id}/unarchive
GET    /api/v1/export/{id}                # PDF on-demand
POST   /api/v1/validate/                  # CU-03, sincrónico, solo Etapa 1

---

## Seguridad — reglas no negociables

- JWT en **HttpOnly Cookie** — nunca en localStorage ni sessionStorage
- API Key siempre en header `X-API-Key` — nunca en URL
- API Keys almacenadas como hash en BD — nunca en texto plano
- Credenciales en variables de entorno — nunca en código ni en el repositorio
- CORS configurado estrictamente — solo el dominio del frontend autorizado
- HTTPS obligatorio en producción

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

Separadas en dos niveles: lo que se lee siempre al arrancar una sesión de trabajo, y lo que se consulta puntualmente cuando el trabajo lo amerita — para no inflar el contexto de sesiones que no lo necesitan.

### Leer siempre al comienzo de cualquier sesión

- `.claude/rules/architecture/architecture.md` — decisiones de arquitectura con justificaciones
- `.claude/rules/architecture/constraints.md` — restricciones no negociables, pendientes y scope
- `.claude/rules/architecture/api-contracts.md` — contratos detallados de cada endpoint y catálogo de errores
- `.claude/rules/core/statistical-pipeline.md` — lógica completa Etapa 1 y Etapa 2
- `.claude/rules/testing.md` — estrategia de testing y fixtures de referencia
- `.claude/rules/sprint.md` — estado actual del sprint, qué está en curso y qué está fuera de alcance

`testing.md` y `sprint.md` no tienen subcarpeta propia dentro de `.claude/rules/` — a diferencia de `core/` y `architecture/`, que agrupan múltiples archivos de un mismo dominio, cada uno de estos dos es documento único de su tema, no partición de un tema mayor.

### Consultar solo cuando el trabajo lo amerite

- `.claude/rules/core/core-etapa1-implementation.md` — librerías permitidas, fuentes por prueba, restricciones del motor estadístico
- `.claude/rules/core/core-etapa2-implementation.md` — librerías, fuentes y restricciones del motor de Etapa 2
- `.claude/rules/core/formulas-etapa1.md` — referencias bibliográficas de todas las fórmulas de Etapa 1 mapeadas a ecuaciones de la tesis de Facundo, y demás referencias bibliográficas. Ninguna fórmula se implementa sin referencia explícita en este archivo.
- `.claude/rules/core/formulas-etapa2.md` — referencias bibliográficas de todas las fórmulas de Etapa 2 mapeadas a ecuaciones de la tesis de Facundo. Ninguna fórmula se implementa sin referencia explícita en este archivo.
- `docs/decisiones/README.md` — índice de decisiones tomadas, descartadas o reemplazadas (una por archivo, `decisionNNN.md`), transversal a todo el proyecto (no solo fidelidad estadística). Consultar cuando algo en el código no coincida con los archivos de decisiones vigentes.
- `docs/auditoria/` — fases de auditoría, regresión numérica contra el Excel de Facundo, y pendientes sin resolver. Consultar cuando el trabajo sea sobre fidelidad del core estadístico o el código no coincida con una decisión ya tomada. Ver `docs/README.md` para el detalle de qué contiene cada subcarpeta.
- `docs/historico/` — documentos superados por trabajo posterior, conservados por trazabilidad. Consultar solo si hace falta contexto de una decisión de implementación ya reemplazada.