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
│   ├── analysis.py       # /analysis/stream (SSE), /outlier-decision, /preview-columns, /design-events, /{id}
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

Ver `.claude/rules/architecture/architecture.md` — sección "Exposición de puertos en desarrollo" para por qué `backend` y `postgres` mapean puertos al host, y "DATABASE_URL — diferencia entre Docker y host" para el override de Alembic/psql desde la terminal local.

**CI (`.github/workflows/ci.yml`)** corre en cada push/PR a `staging`/`main`: job `lint` (ruff check + format --check), job `test` (`pytest -m "unit or integration"`, exit code 5 tolerado — no hay tests de integración todavía), job `error-catalog` (`scripts/check-error-catalog.sh` — verifica en las tres direcciones que todo código de error emitido por el backend, documentado en `api-contracts.md` y usado en `frontend/src/i18n/errors.es.ts` esté sincronizado; excepciones legítimas van en `scripts/error-catalog-allowlist.txt`, ver DECISIÓN 038), job `frontend` (lint + test + build). No mergear sin que los cuatro pasen.

**SonarCloud** analiza cada PR además de estos jobs — no vía un paso propio de `ci.yml`, sino por
Análisis Automático (App de GitHub de SonarCloud). Hoy el check no es *required* en el Ruleset, así
que es consultivo, no bloqueante. Ver [decision044.md](docs/decisiones/decision044.md).

---

## Frontend — estado actual

Vite + React + TypeScript + react-router-dom, 8 pantallas de CU-01/CU-02: `entry`, `config`, `stream`, `results`, `ranking`, `design-events`, `history`, `auth-verify` (`frontend/src/routes/`, tabla de rutas en `frontend/src/routes.tsx`). Tema visual fijo "Instrumento" (claro/oscuro, no seleccionable por el usuario) en `frontend/src/theme/` — `tokens.ts` y `tokens.instrumento.css` deben mantenerse en paridad (verificado por `tokenParity.test.ts`).

**Ya no es scaffold** — Fases 1 a 5 del plan de integración están completas con integración real contra el backend (verificado contra Docker): auth end-to-end (`src/auth/`), stream de Etapa 1 vía SSE-sobre-fetch (`src/api/sse.ts`, hook `useAnalysisStream` — ver `docs/decisiones/decision040.md`), los tres modos de presentación de resultados de Etapa 1, historial con lista paginada y detalle. Etapa 2 (ranking, eventos de diseño) está mockeada con MSW (`src/mocks/`) y marca visual `PendingBadge` ("Vista previa · datos de demostración", texto reformulado en F1 de la pasada 4 — ver `docs/frontend/plan-mejora-frontend-pasada4.md`) porque los endpoints reales de Etapa 2 todavía no existen en el backend — no confundir con "no implementado en el frontend"; ver `docs/decisiones/decision042.md` para el alcance exacto de qué es mock y qué no. Fase 6 (pulido y accesibilidad) quedó parcial. Verificación E2E contra backend real: login/logout/me, Config→stream con atípico real, los tres modos de Resultados e Historial cerrados; solo el tramo registro→verify de Auth sigue bloqueado por falta de SMTP real en desarrollo. Punto de entrada para retomar el estado exacto: [`docs/frontend/informe-implementacion-frontend-fase1-6.md`](docs/frontend/informe-implementacion-frontend-fase1-6.md) (resumen navegable) y [`docs/frontend/frontend-implementation-plan.md`](docs/frontend/frontend-implementation-plan.md) §10 (fuente de verdad decisión por decisión).

**Pasada 4 de mejora (31/07-01/08/2026):** tipografía real (JetBrains Mono cargada de verdad, no solo declarada en tokens), tokens de movimiento + regla universal de `prefers-reduced-motion`, estados de interacción (hover/active/focus-visible) en todo el design system, dos fondos animados en Canvas 2D (`DotFieldBackground`, `GridScanBackground` — DECISIÓN 045), `TopBar` reescrito dentro del design system, columnas de `ConfigPage` pobladas por dropdown real vía `POST /analysis/preview-columns` (DECISIÓN 047), archivado de historial por soft-delete (DECISIÓN 048) y texto de `PendingBadge` reformulado. Tres PRs apilados — ver [`docs/frontend/informe-resultados-pasada4.md`](docs/frontend/informe-resultados-pasada4.md) para el detalle completo y el estado exacto de verificación de cada bloque.

**Testing del frontend — un solo mecanismo de mock de red.** Toda la suite usa `vi.stubGlobal("fetch", ...)` (Vitest + Testing Library) — MSW (`src/mocks/`) corre únicamente en el navegador de dev para las pantallas mock de Etapa 2, nunca dentro de un test. No introducir MSW en un test nuevo; seguir el patrón de mock manual existente. Ver `docs/decisiones/decision041.md` y [frontend/README.md](frontend/README.md) — sección "Testing".

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
POST   /api/v1/analysis/design-events     # Eventos de diseño por distribución — CU-01 y CU-02
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

METIS detecta y advierte, pero **no bloquea** — excepto el único caso absoluto:

- **< 10 datos → error bloqueante.** Pipeline se detiene. Único caso.
- **10–29 datos → warning no bloqueante.** Pipeline continúa. Responsabilidad del usuario.
- **≥ 30 datos → condiciones recomendables.** Sin warning por longitud.

Pendiente: DECISIÓN 030 propone una segunda excepción — desorden cronológico bloqueante — sin implementar todavía. Ver docs/decisiones/decision030.md.

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