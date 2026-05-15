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

```
metis/
├── api/        # Controllers: endpoints, contratos request/response. Sin lógica de negocio.
├── core/       # Motores estadísticos Etapa 1 y Etapa 2. SIN conocimiento de HTTP ni BD.
├── services/   # Orquestación del pipeline, lógica de negocio.
├── db/         # Modelos SQLAlchemy, acceso a datos.
├── schemas/    # Modelos Pydantic: validación de inputs y outputs.
└── auth/       # Lógica OAuth, JWT descartada. Pendiente de confirmacion de modelo de autenticacion.
```

**Regla crítica:** `core/` no importa nada de `api/`, `services/`, ni `db/`. El motor estadístico es una librería pura — recibe datos, devuelve resultados. Esto es lo que hace posible los tests de regresión matemática.

---

## Comandos esenciales

```bash
# Levantar entorno completo
docker-compose up --build

# Solo backend en desarrollo
uvicorn metis.main:app --reload --port 8000

# Tests
pytest tests/ -v

# Linting backend
ruff check metis/
ruff format metis/

# Frontend
cd frontend && npm install && npm run dev

# Linting frontend
cd frontend && npm run lint
```

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

```
POST   /api/v1/auth/register
POST   /api/v1/auth/verify
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me

POST   /api/v1/analysis/stream            # SSE — CU-01 y CU-02
POST   /api/v1/analysis/outlier-decision  # Decisión ante atípico Chow — CU-01 y CU-02
POST   /api/v1/analysis/design-events     # Eventos de diseño por distribución — CU-01 y CU-02
GET    /api/v1/analysis/{id}              # Consulta análisis persistido — CU-01

GET    /api/v1/history/
GET    /api/v1/history/{id}

GET    /api/v1/export/{id}                # PDF on-demand

POST   /api/v1/validate/                  # CU-03, sincrónico, solo Etapa 1
```

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

**El sistema no garantiza resultados fuera del contrato.** Toda decisión ante un warning es responsabilidad del usuario y queda registrada en el historial (CU-01).

---

## Referencias — Leer todas al comienzo. Consultar con @mención cada vez que se referencien

- `.claude/rules/architecture.md` — decisiones de arquitectura con justificaciones
- `.claude/rules/api-contracts.md` — contratos detallados de cada endpoint y catálogo de errores
- `.claude/rules/statistical-pipeline.md` — lógica completa Etapa 1 y Etapa 2
- `.claude/rules/testing.md` — estrategia de testing y fixtures de referencia
- `.claude/rules/constraints.md` — restricciones no negociables, pendientes y scope
- `.claude/rules/sprint.md` — estado actual del sprint, qué está en curso y qué está fuera de alcance
- `.claude/rules/core-implementation.md` — librerías permitidas, fuentes por prueba, restricciones del motor estadístico
- `.claude/rules/decisions-log.md` — historial de decisiones descartadas y reemplazadas. Leer cuando algo en el código no coincida con los archivos de decisiones vigentes.