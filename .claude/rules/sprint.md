# Estado del Sprint Actual

## Sprint 1 — Etapa 1 completa

### Estrategia de ramas
Una rama por funcionalidad. Flujo de tres niveles: feature/xxx → staging → main.
Nunca merge directo de feature a main.

### Orden de implementación
1. feature/db-models     — modelos SQLAlchemy + sesión  ✓ mergeado a staging
2. feature/schemas       — modelos Pydantic de request/response  ✓ mergeado a staging
3. feature/auth          — OAuth Google + JWT en HttpOnly Cookie  ✓ completado
4. feature/core-etapa1   — motor estadístico Etapa 1 completo  ✓ completado
5. feature/api-etapa1    — endpoints de Etapa 1 + auth  ✓ completado
6. feature/services-sse  — orquestación stream SSE hasta resultado Etapa 1  ✓ completado

### Fuera de alcance en este sprint
- Etapa 2 (distribuciones, ranking EEA, eventos de diseño)
- Frontend React + TypeScript
- Exportación PDF
- Endpoint /export/
- Endpoint /analysis/design-events
- Endpoint /api/v1/validate/ (CU-03) — sprint posterior

### Completado
- Scaffolding inicial (feature/project-scaffolding — en GitHub, inactiva)
- feature/db-models — mergeado a staging
- feature/schemas — mergeado a staging
- feature/auth — mergeado a staging
- feature/core-etapa1 — mergeado a staging
- feature/api-etapa1 — mergeado a staging
- feature/services-sse — mergeado a staging
- feature/github-actions — CI pipeline con ruff + pytest  ✓ completado

### Archivos creados en feature/github-actions
- `.github/workflows/ci.yml` — jobs lint (ruff check + format --check) y test (pytest unit+integration, exit code 5 tolerado)

### feature/tests-unitarios — EN CURSO

#### Bugs corregidos como parte de esta rama
- independence.py — eliminado WarningItem con código
  TEST_WARNING_INDEPENDENCE (no existía en el catálogo)
- trend.py — corregido `resultado.h is False` por
  `not bool(resultado.h)` — Mann-Kendall reportaba tendencia
  en el 100% de las series por comparación de identidad
  con numpy.bool_
- pytest.ini — agregado pythonpath = . para resolución
  de imports en desarrollo local

#### Archivos completados
- tests/unit/core/conftest.py — fixtures: serie_facundo
  (40 valores reales 1980-2019, Anderson rechaza, pendiente
  validación con Excel de Facundo) y serie_corta_15
- tests/unit/core/test_contract.py — 14/14 tests pasando.
  Cubre 2 bloqueantes y 7 warnings del catálogo.
- tests/unit/core/test_independence.py — 8/8 tests pasando.
  Cubre jerarquía Anderson manda, propagación de TEST_WARNING_SMALL_SAMPLE,
  y caso borde de Wald con todos los valores iguales.
  Fix documentado: test protege contra reintroducción de
  TEST_WARNING_INDEPENDENCE (código inexistente en el catálogo).
- tests/unit/core/test_homogeneity.py — 6/6 tests pasando.
  Cubre jerarquía Cramer manda, los tres niveles de homogeneidad,
  presencia de n1 y n2 en Cramer, y partición custom con cálculo
  inline de valores esperados.
- pytest.ini — agregado filterwarnings para suprimir
  PytestCollectionWarning de TestResult (dataclass de producción
  con nombre que pytest intenta colectar como clase de test).
  Decisión documentada: suprimir es correcto, no tocar el dataclass.

#### Decisión de implementación — serie_facundo no produce nivel_confianza="validado"
El smoke test confirmó que serie_facundo tiene Anderson rechazando
(dependiente). No sirve como fixture base para tests que requieren
nivel_confianza="validado". Para test_pipeline.py caso 4, se construye
una serie inline con nota explicativa. Esta decisión aplica al resto
de los archivos pendientes.

- tests/unit/core/test_trend.py — 8/8 tests pasando.
  Cubre Mann-Kendall (n=7 no ejecutada, aprueba, rechaza),
  KS (aprueba, rechaza), y lógica OR de determinar_warnings_tendencia.
  Series de rechazo verificadas con smoke test antes de escribir.
  Documenta pendiente: valor crítico n=7 Tabla A.4 sin confirmar con Facundo.

- tests/unit/core/test_outliers.py — 7/7 tests pasando.
  Cubre las tres rutas del código: TEST_NOT_EXECUTED_ZEROS (cero en caudal),
  TEST_NOT_EXECUTED_CONDITION (cero o negativo en cualquier tipo),
  sin atípico, y con atípico. Tests separados verifican que
  warning_nivel es siempre "normal" y que valor_atipico es el
  valor original de la serie, no su logaritmo.
  Serie con atípico verificada con smoke test antes de escribir.

- tests/unit/core/test_pipeline.py — 8/8 tests pasando.
  Cubre pipeline bloqueante (serie corta, sin resolución temporal,
  strings sin suficientes numéricos), nivel_confianza="validado"
  con serie numpy seed=1 n=50 (seed=42 descartada — Anderson rechaza),
  nivel_confianza="con_warnings" con serie_facundo, Chow no_ejecutada
  sin detener el pipeline, filtrado de strings antes de pruebas,
  y presencia de n1/n2 en Cramer.

#### Estado final — feature/tests-unitarios COMPLETA (comportamiento)
51/51 tests pasando. Ruff limpio. Sin warnings en pytest.
Sin importaciones prohibidas en core/.
Tests de regresión matemática bloqueados — esperando series
reales de Facundo en formato digital.

### Archivos creados en feature/services-sse
- `metis/services/session_store.py` — dict en memoria de sesiones activas con asyncio.Event y timeout 300s
- `metis/services/analysis_service.py` — orquestación SSE: parseo → pipeline → pausa Chow → re-ejecución → persistencia
- `metis/core/types.py` — agregado campo `valor_atipico: float | None` a TestResult
- `metis/core/outliers.py` — calcular_chow llena valor_atipico con el valor original de la serie

### feature/auth-refactor — EN CURSO

#### Decisión implementada
Autenticación usuario/contraseña + bcrypt + JWT HttpOnly Cookie con verificación de cuenta por mail @ucc.edu.ar.
Mecanismo SMTP: App Password via smtp.gmail.com:587 (Opción B — confirmada por IT).
Ver decisions-log.md — DECISIÓN 001, 002, 003, 004, 005.

#### División en dos partes
Parte 1 — COMPLETADA
Parte 2 — BLOQUEADA esperando IT (cuenta metis-noreply@ucc.edu.ar + App Password de 16 dígitos)

#### Paso 0 completado — Alembic configurado
- alembic/env.py — psycopg2 síncrono para migraciones,
  asyncpg sigue para la app. Base.metadata conectada.
- alembic/versions/001_baseline_schema.py — esquema inicial,
  generada manualmente, verificar con BD activa
- alembic/versions/002_add_password_hash_email_verified.py —
  agrega password_hash y email_verified a users,
  generada manualmente, verificar con BD activa
- Pendiente ejecutar: alembic stamp head (BD existente)
  o alembic upgrade head (BD vacía) cuando Docker esté activo

#### Parte 1 completada
- Paso 1: architecture.md actualizado (columnas password_hash y email_verified en tabla users)
- Paso 2: auth/google.py eliminado
- Paso 3: db/models/user.py — agregados password_hash (String 255) y email_verified (Boolean)
- Paso 4: schemas/auth.py — RegisterRequest, LoginRequest, VerifyRequest, UserMe extendido
- Paso 5: auth/email.py creado con mock SMTP (loggea token, pendiente aiosmtplib)
- Paso 6: auth/router.py reescrito — /register, /verify, /login, /logout, /me
- Paso 7: auth/__init__.py sin cambios (exports no cambian)
- Paso 8: .env.example actualizado — eliminadas vars Google OAuth, SMTP comentado
- requirements.txt — agregados bcrypt==4.1.3, psycopg2-binary==2.9.9, alembic==1.13.1

---

## Decisiones pendientes — no implementar hasta confirmar

---

## Milestones del proyecto

M1 — SSE operativo en staging
     CI verde, ruff limpio, pipeline emite eventos reales,
     tests unitarios core pasando

M2 — Etapa 2 operativa en staging
     M1 completo + distribuciones ajustando correctamente,
     tests de regresión matemática pasando contra tesis Facundo

M3 — API completa en staging
     M2 completo + todos los endpoints respondiendo,
     tests de integración pasando

M4 — CU-01 funcional en staging
     M3 completo + frontend React integrado,
     flujo completo de punta a punta verificado manualmente

M5 — CU-01 stable — primer merge a main
     M4 completo + tests e2e de CU-01 pasando,
     sin issues abiertos críticos

M6 — CU-02 stable en main
     M5 completo + flujo anónimo verificado

M7 — CU-03 stable en main
     M6 completo + integración con sistema de Carlos validada

M8 — V1.0
     M7 completo + tests de regresión todos verdes,
     desplegado en servidores UCC, documentación entregada

---

## Scope post-M5 — pruebas adicionales confirmadas por Carlos

Pruebas a incorporar en Etapa 1 después de M5:
- Independencia: Durbin-Watson, Ljung-Box
- Homogeneidad: Mann-Whitney, Mood
- Tendencia: Spearman
- Atípicos: Kn

Cada una entra en su módulo correspondiente en core/.
El output de Etapa1Result se extiende — afecta schemas/ y frontend.
Implementar como feature/pruebas-adicionales post-M5.