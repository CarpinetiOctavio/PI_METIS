# Estado del Sprint Actual

## Sprint 1 — Etapa 1 completa

### Estrategia de ramas
Una rama por funcionalidad. Flujo de tres niveles: feature/xxx → staging → main.
Nunca merge directo de feature a main.

**Pendiente — documentar formalmente (20/07/2026):** protección de
ramas main/staging vía GitHub Ruleset ya configurada y activa
(bloquea push directo, exige PR). Falta: decisión completa con
alternativas evaluadas (Rulesets vs. Classic, reglas activadas/
descartadas con motivo) en `docs/decisiones/decision035.md` — no
escrita todavía. También pendiente: chequeo custom en `ci.yml` para
restringir que `main` sólo reciba PRs desde `staging` (ver discusión,
diferido por bajo riesgo con equipo de dos personas).

**Corrección 30/07/2026 (limpieza SonarCloud, D3):** esta sección decía "exige
PR + CI", dando a entender que ningún check puede estar en rojo al mergear.
Verificado contra el PR #17 real (`gh pr view 17 --json
mergeStateStatus,reviewDecision,statusCheckRollup`): con el check de
SonarCloud en `FAILURE`, `mergeStateStatus` es `UNSTABLE` (checks no
requeridos fallando) y no `BLOCKED` (que es lo que devuelve GitHub cuando un
check requerido falla) — el botón de merge sigue habilitado.
`reviewDecision` está vacío pese a haber una revisión pendiente solicitada:
tampoco la revisión es requerida. La parte verificable de la afirmación
original —que el Ruleset bloquea push directo y exige pasar por PR— se
sostiene; la parte de "exige CI" no se sostiene al menos para el check de
SonarCloud, y no se pudo confirmar el estado de los tres checks de `ci.yml`
como *required* porque este repo devuelve 404/lista vacía en los endpoints
de Ruleset/branch-protection de la API para un token sin permiso `admin`
(solo `push`/`maintain`) — pendiente de verificar con acceso admin real.
Ver [DECISIÓN 044](../../docs/decisiones/decision044.md), sección "La
pregunta de gobernanza abierta".

### Orden de implementación
1. feature/db-models     — modelos SQLAlchemy + sesión  ✓ mergeado a staging
2. feature/schemas       — modelos Pydantic de request/response  ✓ mergeado a staging
3. feature/auth          — OAuth Google + JWT en HttpOnly Cookie  ✓ completado
   (mecanismo original planeado — descartado y reemplazado por usuario/contraseña,
   ver DECISIÓN 001 y docs/historico/oauth-descartado.md)
4. feature/core-etapa1   — motor estadístico Etapa 1 completo  ✓ completado
5. feature/api-etapa1    — endpoints de Etapa 1 + auth  ✓ completado
6. feature/services-sse  — orquestación stream SSE hasta resultado Etapa 1  ✓ completado

### Fuera de alcance en este sprint
- Etapa 2 (distribuciones, ranking EEA, eventos de diseño)
- ~~Frontend React + TypeScript~~ — alcance original de Sprint 1 (backend-only,
  Etapa 1). Contradicho desde el 28/07/2026: ver
  "feature/frontend-fases1-5 — COMPLETA" más abajo. Se deja tachado, no
  eliminado, por trazabilidad del alcance histórico real de este sprint.
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
- feature/frontend-fases1-5 — Fases 1-5 del frontend (Auth, Config+Stream,
  Resultados, Historial, Mocks Etapa 2)  ✓ completado — ver sección propia
  más abajo

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

### feature/core-etapa2 — EN CURSO

Motor de análisis de frecuencia: 13 distribuciones con métodos por distribución según tesis.
Pendientes de confirmación con Facundo: ME/MC en otras distribuciones, ceros en 5 distribuciones.
Ver .claude/rules/core-etapa2-implementation.md y .claude/rules/formulas-etapa2.md.

#### Fase 1 — Scaffold y tipos base ✓ COMPLETA

Archivos creados:
- metis/core/etapa2/__init__.py — exports públicos del subpaquete
- metis/core/etapa2/types.py — MetodoResult, DistResult, Etapa2Result, EventoDiseno,
  CONVERGENCIA=1e-7, STATUS_OK/NO_CONVERGE/NO_APLICABLE/DISABLED_ZEROS
- metis/core/etapa2/empirical.py — probabilidades_weibull (T=(n+1)/m, P=1-1/T — Tesis Cap. IV sec. IV.1)
- metis/core/etapa2/eea.py — calcular_eea (Ec. IV-263), es_high_eea (umbral 5% — decisión METIS)
- metis/core/etapa2/distributions/__init__.py — DISABLED_WITH_ZEROS y PENDING_ZEROS_CONFIRMATION como frozenset
- metis/core/etapa2/distributions/uniforme.py        — N_PAR=2, momentos/mv, IV-58 a IV-62
- metis/core/etapa2/distributions/normal.py          — N_PAR=2, momentos/mv/ml, IV-92 a IV-105
- metis/core/etapa2/distributions/gumbel.py          — N_PAR=2, momentos/mv/ml/me, IV-177 a IV-199
- metis/core/etapa2/distributions/gve.py             — N_PAR=3, momentos/mv/ml, IV-203 a IV-245
- metis/core/etapa2/distributions/lognormal2p.py     — N_PAR=2, momentos/mv, DISABLED_WITH_ZEROS, IV-107 a IV-109
- metis/core/etapa2/distributions/lognormal3p.py     — N_PAR=3, momentos/mv, PENDING_ZEROS, IV-111 a IV-120
- metis/core/etapa2/distributions/logpearson3.py     — N_PAR=3, momentos_directo/momentos_indirecto/mv, DISABLED_WITH_ZEROS, IV-247 a IV-260
- metis/core/etapa2/distributions/gamma2p.py         — N_PAR=2, momentos/mv/ml, DISABLED_WITH_ZEROS, IV-123 a IV-135
- metis/core/etapa2/distributions/gamma3p.py         — N_PAR=3, momentos/mv, PENDING_ZEROS, IV-137 a IV-144
- metis/core/etapa2/distributions/exponencial_beta.py    — N_PAR=1, momentos/mv, DISABLED_WITH_ZEROS, IV-65 a IV-67
- metis/core/etapa2/distributions/exponencial_x0_beta.py — N_PAR=2, momentos/mv, PENDING_ZEROS, IV-70 a IV-74
- metis/core/etapa2/distributions/gen_pareto.py      — N_PAR=3, momentos/mv/mc, PENDING_ZEROS, IV-145 a IV-156
- metis/core/etapa2/distributions/gen_exponencial.py — N_PAR=2, momentos/mv/ml, PENDING_ZEROS, IV-77 a IV-89

Patrón de stubs: ajustar() retorna STATUS_NO_APLICABLE (pipeline2.py puede ejecutarse de punta
a punta antes de implementar ninguna distribución); cuantil() levanta NotImplementedError.
Cada archivo incluye referencias a ecuaciones de la tesis como documentación ejecutable.

#### pipeline2.py — línea base del smoke test (Fase 1)
Smoke test con serie_facundo (n=40, sin ceros): 13 distribuciones, 30 llamadas
a ajustar(), todas retornan no_aplicable, 0 crashes, 0 warnings.
Con tiene_ceros=True: 4 distribuciones correctamente disabled_zeros
(exponencial_beta, lognormal2p, gamma2p, logpearson3).
A medida que avance Fase 2, el número de status=ok crecerá desde 0.

#### Fase 2 — EN CURSO

##### Distribuciones implementadas
- Normal — momentos, mv, ml — smoke test OK
- Gumbel — momentos, mv, ml, me — smoke test OK
  Bugs encontrados y corregidos: IV-179/IV-180 mal
  transcriptas en formulas-etapa2.md (sumas, no medias)
- Log-Normal 2p — momentos, mv — smoke test OK
  Refactor: _ut extraída a utils.py (compartida por
  Normal, Log-Normal 2p, 3p, Log-Pearson III)
- Log-Pearson III — momentos_directo, momentos_indirecto, mv — smoke test OK
  momentos_directo no_aplicable para serie_facundo (B=2.63, fuera del rango
  (3,6]) — comportamiento correcto según tesis. momentos_indirecto y mv
  convergen correctamente.
- GVE — momentos, mv, ml — smoke test OK
  momentos: converge. mv: no_converge (esperado según tesis).
  ml: no_aplicable — pendiente respuesta de Facundo sobre
  inconsistencia IV-238 vs IV-243/244 (ver docs/decisiones/decision029.md)

##### Errores corregidos en formulas-etapa2.md
- Gumbel MV IV-179/IV-180: eran medias, son sumas con n
- Log-Normal 3p IV-113: exponente incorrecto en g
- Log-Normal 3p IV-114: signo invertido en ẑ
- Log-Normal 3p IV-116: era σ̂²y, es σ̂y directamente
- Log-Pearson III IV-260: cuantil con WH correcto
- GVE — IV-203/204 signos invertidos y coeficiente g⁴ incorrecto,
  rangos de g incorrectos, IV-208/209/210-215 ausentes,
  IV-216-218 P/Q/R ausentes, IV-234 faltaba -ln(2)/ln(3),
  IV-237 signo, IV-239 fórmula incorrecta

- Log-Normal 3p — momentos, mv — smoke test OK
  Fórmulas IV-111 a IV-116 corregidas en formulas-etapa2.md.
  momentos y mv convergen. x0 negativo es válido (umbral
  muy por debajo del mínimo observado).

##### Fase 2 COMPLETA

#### Fase 3 — COMPLETA

##### Distribuciones implementadas
- Exponencial β — momentos, mv — smoke test OK
  momentos y MV coinciden (β=1/x̄). DISABLED_WITH_ZEROS=True.
  EEA alta (~95) para serie_facundo — esperado, ajuste pobre.

- Gamma 2p — momentos, mv, ml — smoke test OK
  momentos: alpha=22.81, beta=3.90, Q100=137.8, EEA=36.3
  mv: alpha=23.00, beta=3.86, Q100=137.6, EEA=36.2
  ml: polinomio IV-130 produce EEA alta (~118) para esta serie —
  el ranking lo deprioritiza automáticamente. DISABLED_WITH_ZEROS=True.
  NOTA nomenclatura: la tesis usa β̂ como forma en MV/ML (IV-126) y
  α̂ como forma en Momentos (IV-123). El módulo unifica: alpha=forma, beta=escala.

- Gamma 3p — momentos, mv — smoke test OK
  momentos: con g=0.19, β̂=110, x0=-1963, Q100=-1940, EEA=2114 —
  matemáticamente correcto según IV-137/138/139, ranking lo deprioritiza.
  La tesis no define umbral mínimo de g — solo guard g≈0 implementado.
  mv: beta=24.4, alpha=3.75, x0=-2.67, Q100=137.4, EEA=36.7 — converge.
  PENDING_ZEROS_CONFIRMATION=True.

#### Fase 4 — COMPLETA

##### Distribuciones implementadas
- Uniforme — momentos, mv — smoke test OK
  momentos: alpha=56.66, beta=121.14, Q100=120.50, EEA=37.40
  mv: alpha=54.10, beta=130.40, Q100=129.64, EEA=40.95

- Exponencial (x₀, β) — momentos, mv — smoke test OK
  momentos: x0=70.28, beta=18.62, Q100=156.01, EEA=34.52
  mv: x0=54.08, beta=0.89, Q100=58.19, EEA=39.97
  PENDING_ZEROS_CONFIRMATION=True.

- Generalizada Exponencial — momentos, mv, ml — smoke test OK
  momentos: alpha=79.34, lambda=0.0512, Q100=175.23, EEA=47.47
  mv: no_converge — sistema IV-80/IV-81 no converge para serie_facundo (comportamiento esperado)
  ml: alpha=0.81, lambda=0.009, Q100=488.72, EEA=115.90 (EEA alta, ranking deprioritiza)
  PENDING_ZEROS_CONFIRMATION=True.
  NOTA IV-77: la ecuación como escrita tiene -1/α = x̄/S sin solución válida.
  Se implementa CV-matching con momentos teóricos de la GE. Pendiente confirmar con Facundo.
  NOTA IV-84: la tesis escribe "+ψ(1)" — se implementa "-ψ(1)" (forma correcta). Pendiente Facundo.

- Generalizada de Pareto — momentos, mv, mc, mpp — smoke test OK
  momentos: eps=0.553, mu=65.70, sigma=53.32, Q100=154.60, EEA=47.30
  mv: no_converge — esperado según tesis
  mc: eps=0.508, mu=66.97, sigma=49.99, Q100=155.94, EEA=46.88
  mpp: eps=5.362, mu=45.70, sigma=648.84, Q100=166.71, EEA=72.51
  PENDING_ZEROS_CONFIRMATION=True.

##### Bugs corregidos en Fase 4
1. gen_pareto MC — fsolve reportaba convergencia falsa (residual=0.007 en valor inicial
   ε=0.3). El root real estaba en ε≈0.51. Fix: scan + brentq sobre (-0.49, 50.0),
   iterando sobre todos los brackets para evitar raíz espuria cerca de ε=0
   (denom_b≈0 → B_hat→∞). Ver DECISIÓN 010 en docs/decisiones/decision010.md.
2. ValueError guard propagado a cuantil() en gen_exponencial y gen_pareto —
   p debe estar en (0,1). Propagación al resto de distribuciones pendiente (ver abajo).

##### Pendientes con Facundo — surgidos en Fase 4
- gen_pareto MPP: guard denominador IV-167 = 0 puede dispararse para ciertas series
  (I2*(n-1) - I1 = 0) → STATUS_NO_APLICABLE. Confirmar si hay restricción adicional en tesis.
- gen_pareto MC: confirmar rango válido de ε en la tesis (implementado -0.49 a 50.0
  con justificación teórica en límite inferior, conservador en superior).

#### Guard p ∈ (0,1) en cuantil() — PENDIENTE PROPAGACIÓN
Propagado en: gen_exponencial, gen_pareto.
Pendiente en: uniforme, normal, gumbel, gve, lognormal2p, lognormal3p, logpearson3,
gamma2p, gamma3p, exponencial_beta, exponencial_x0_beta.
Los asserts se deshabilitan con python -O — usar siempre if/raise.

#### Fases siguientes
- Fase 4.5: propagar guard p∈(0,1) a todas las cuantil() pendientes
- Fase 5: pipeline2.py — orquestación exhaustiva
- Fase 6: tests de comportamiento

#### ACTUALIZACIÓN 15 de Julio de 2026 — cierre del primer análisis E2E del core estadístico

Se completó el primer análisis end-to-end del core estadístico (Etapa 1 +
Etapa 2 juntas), corriendo el flujo real y completo del pipeline
(`ejecutar_etapa1()` seguido de `ejecutar_etapa2()`, sin atajos) contra las
9 estaciones disponibles de la tesis de Facundo Ganancias Martínez, a modo
de pruebas de regresión contra sus resultados publicados. Documentado en
`.claude/rules/auditoria/` — `fases/fase1-unitarias.md` (fidelidad de
fórmula), `fases/fase2-cableado.md` (integración entre módulos),
`fases/fase3-testing.md` (integridad de la suite de tests), `fases/fase4-e2e.md`
(el análisis E2E en sí, estación por estación en
`regresion/regresion-e2e-coreEstadistico/est_0X-e2e.md`), con el informe de
consolidación en `regresion/regresion-e2e-coreEstadistico/consolidacion-e2e.md`
y las preguntas abiertas a escalar a Facundo en `pendientes-facundo.md`.

**No queda cerrado por completo** — hay pendientes reales sin resolver
(preguntas a Facundo con respuesta cerrada, necesidad del Excel original de
la tesis para varios casos, y un par de correcciones cosméticas ya
identificadas, como el conteo real de combinaciones distribución×método).
Pero **no queda ninguna parte del core estadístico sin analizar** — de acá
en más todo lo que falta es accionar sobre pendientes ya identificados y
redactados, no seguir auditando a ciegas. Dos bugs de código reales se
encontraron y corrigieron en el proceso (DECISIÓN023 en
`docs/decisiones/decision023.md`, DECISIÓN025 en
`docs/decisiones/decision025.md`), ambos verificados sin regresión
contra las 9 estaciones.

**Próximo paso: comenzar el desarrollo de autenticación** (continuación de
`feature/auth-refactor` — ver Parte 2 más abajo, ya no bloqueada: las
credenciales de Soporte IT de la UCC llegaron el 15/07/2026).

### feature/auth-refactor — mergeado a staging ✓

#### Decisión implementada
Autenticación usuario/contraseña + bcrypt + JWT HttpOnly Cookie con verificación de cuenta por mail @ucc.edu.ar.
Mecanismo SMTP: App Password via smtp.gmail.com:587 (Opción B — confirmada por IT).
Ver docs/decisiones/ — DECISIÓN 001, 002, 003, 004, 005.

#### División en dos partes
Parte 1 — COMPLETADA
Parte 2 — BLOQUEADA esperando IT (cuenta metis-noreply@ucc.edu.ar + App Password de 16 dígitos)

**ACTUALIZACIÓN 15 de Julio de 2026:** credenciales recibidas de Soporte IT
de la UCC — Parte 2 deja de estar bloqueada. Queda como próximo trabajo a
implementar (ver actualización en la sección de `feature/core-etapa2` más
arriba).

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

#### Smoke test de auth — COMPLETADO ✓

7 pasos ejecutados contra Docker local. Resultado: todos pasaron.

Bugs encontrados y corregidos durante el smoke test:
- auth/email.py: `logger.info()` → `print(flush=True)` — el root logger suprime
  INFO de loggers de aplicación; print garantiza visibilidad en Docker logs
- auth/router.py: `datetime.now(timezone.utc)` → `datetime.utcnow()` en la
  actualización de `last_login` — TIMESTAMP WITHOUT TIME ZONE no acepta
  datetime timezone-aware; el error era un 500 silencioso en POST /login
- docs/decisiones/, sprint.md: corregido el usuario psql en comandos de
  limpieza (`metis_user` → `metis`, que es el POSTGRES_USER real del .env)
- .env.example: reescrito con reglas explícitas de consistencia (ver DECISIÓN 008)

Pasos verificados:
1. POST /register → 201 + mensaje de verificación
2. Logs Docker → token MOCK SMTP visible con print()
2.5. POST /login antes de verificar → 403 AUTH_EMAIL_NOT_VERIFIED
3. POST /verify con token → 200
4. POST /login después de verificar → 200 + HttpOnly cookie
5. GET /me con cookie → 200 + email_verified: true
6. POST /logout → 200 + cookie eliminada (Max-Age=0)
7. GET /me sin cookie → 401

7. GET /me sin cookie → 401


#### Parte 2 — COMPLETADA ✓ (19 de Julio de 2026)

Mock de `auth/email.py` reemplazado por implementación real con
`aiosmtplib.send()` (App Password, smtp.gmail.com:587, start_tls=True).
`register` reordenado para mandar el mail antes de comitear el usuario
en base — evita usuarios huérfanos si el envío falla. `IntegrityError`
en registros concurrentes capturado y mapeado a
`AUTH_EMAIL_ALREADY_REGISTERED`. Excepciones logeadas con
`logger.exception()` — primer uso de `logging` en el repo.
Detalle completo de las decisiones de diseño (orden de operaciones,
alternativas de lock evaluadas y descartadas, precedente de mocking
para tests) en `docs/decisiones/decision032.md`.

- `requirements.txt` — agregado `aiosmtplib==5.1.2`
- `.env.example` — vars SMTP descomentadas y marcadas requeridas
- `tests/unit/auth/` — primeros tests del repo (10/10), primer uso de
  mocking (`unittest.mock` + `AsyncMock`) — precedente documentado en
  decision032.md
- `pytest.ini` — agregado `ignore::PendingDeprecationWarning:starlette.formparsers`
  (primer import de FastAPI en tests/unit/ expone una deprecation de
  Starlette/python-multipart). Bump que lo resuelve de raíz, diferido
  con condiciones explícitas de habilitación — ver decision033.md.
- `api-contracts.md` — sumado `500 AUTH_VERIFICATION_EMAIL_FAILED` al
  contrato de `register`, agregada sección `### Auth` al catálogo
  maestro de errores (no existía, sólo estaban documentados inline
  por endpoint)

#### Smoke test de Auth Parte 2 — COMPLETADO ✓ (20 de Julio de 2026)

Camino A (envío exitoso) y Camino B (falla real de conexión) verificados
contra el relay SMTP real de la UCC — no mockeado. Detalle completo de
los bugs encontrados en `docs/decisiones/decision034.md`; verificación
con evidencia real registrada en la actualización de `decision032.md`.

Bugs encontrados y corregidos durante el smoke test:
- `.env`: línea `SMTP_HOST` con `#` sin espacio adelante — python-dotenv
  no lo trataba como comentario, el resto de la línea quedaba pegado al
  valor. Trampa nueva de la misma familia que DECISIÓN 008 — pendiente
  sumarla como regla nueva a esa decisión (ver Regla 6 más abajo).
- `SMTP_HOST=wally.ucc.edu.ar` (dato literal compartido por IT) no
  coincide con el CN real del certificado (`wally.uccor.edu.ar`) — mismo
  servidor (misma IP), nombre de host distinto. Corregido, y verificado
  como infraestructura legítima de la UCC (ver DECISIÓN 034).
- `email.py` usaba `SMTP_USER` (identidad de autenticación, `metis`, sin
  dominio) también como remitente del mensaje — el mail se aceptaba y
  encolaba sin error, pero se perdía silenciosamente río abajo (candidato:
  SPF/DMARC sin dominio para validar). Separado en `SMTP_FROM_ADDRESS`.
- `tests/unit/auth/`: tras la separación de `SMTP_FROM_ADDRESS`, 3/4
  tests de `test_email.py` quedaron rotos sin que se corriera la suite
  para detectarlo — corregido, 12/12 en verde.

Pasos verificados (Camino A, contra `2200631@ucc.edu.ar` — mismo usuario
de prueba que Parte 1):
1. `POST /register` → 201, mail real recibido
2. Token real extraído del mail
3. `POST /verify` con token real → 200
4. `POST /login` → 200 + cookie HttpOnly
5. `GET /me` → 200, `email_verified: true`
6. Limpieza — `DELETE` aplicado, verificado con `SELECT`

#### Pendiente — verificación dentro de la red UCC (bloqueado, sin acceso a infraestructura real)

Todo lo verificado en el smoke test de arriba corrió desde red doméstica,
nunca desde un host dentro de la intranet de la UCC. Pendientes reales,
no urgentes hasta que haya acceso al servidor real (`172.16.168.14`) —
ver DECISIÓN 034 para el detalle de qué se verificó desde afuera:

1. Alcanzabilidad de `wally.uccor.edu.ar:587` desde el servidor real de
   la UCC — no verificado. Reglas de firewall interno pueden comportarse
   distinto para tráfico interno vs. externo.
2. Resolución DNS interna — verificado solo contra DNS público (resolvió
   a `190.3.95.77` y `200.45.112.13`). Si la UCC usa DNS split-horizon,
   un host interno podría resolver distinto.
3. Coincidencia de certificado/hostname desde adentro — casi seguro el
   mismo servidor físico, pero no verificado directamente, sólo inferido.
4. Deploy real de METIS en la infraestructura de la UCC en sí — todo el
   stack corrió en Docker local hasta ahora. Pendiente para cuando
   arranque el despliegue real (no urgente todavía según milestones
   actuales — M4/M5 siguen lejos).

Ninguno de los cuatro bloquea el cierre de Auth Parte 2 tal como está
definida — son verificaciones de infraestructura, no de la
implementación de auth en sí.

### feature/frontend-fases1-5 — COMPLETA

Implementación de Fases 1 a 5 del frontend (28-29/07/2026), sobre el scaffold de
Fase 0 (`docs/superpowers/plans/2026-07-22-frontend-fase0-scaffold.md`, ya
mergeado). Plan completo y decisión por decisión en
`docs/frontend/frontend-implementation-plan.md` §10; resumen navegable en
`docs/frontend/informe-implementacion-frontend-fase1-6.md`.

**Nota de nomenclatura:** este proyecto ya usaba "Fase 1...Fase 6" para el
desarrollo de Core Etapa 2 (ver más arriba, `feature/core-etapa2`). El frontend
reutiliza los mismos números para una secuencia distinta. Toda mención nueva
dice explícitamente "Fase N del frontend" para no confundir ambas — las
entradas de esta sección son todas del frontend salvo que se aclare lo
contrario.

#### Fase 1 — Auth end-to-end
Archivos clave: `src/auth/AuthProvider.tsx`, `src/auth/guards.tsx`,
`src/api/auth.ts`, `src/api/client.ts` (agregó `ApiError`/`requestJson`),
`src/routes/entry/EntryPage.tsx`, `src/routes/auth-verify/AuthVerifyPage.tsx`.
Login/registro/anónimo en una sola pantalla, guards `RequireAuth`/
`RedirectIfAuthed`, flag de sesión anónima persistido en `localStorage`
(FE-7). Verificado contra Docker: login/logout/me reales; registro→verify
bloqueado por falta de SMTP real en desarrollo (FE-6, límite conocido, no un
bug de esta fase).

#### Fase 2 — Config + stream de Etapa 1
Archivos clave: `src/routes/config/ConfigPage.tsx`, `src/api/sse.ts` (hook
`useAnalysisStream`, SSE-sobre-fetch — DECISIÓN 040), `src/routes/stream/StreamPage.tsx`.
Timeline agrupado en 4 pasos (FE-11), modal de atípico de Chow real, router
state para pasar el form completo a `/stream` (FE-9). Verificado con CSV
sintético de 40 años contra el backend real, con un atípico forzado —
**dos bugs reales encontrados y corregidos** en `useAnalysisStream`
(`complete` pisando una `fase="error"` previa; `result_etapa1` sin desenvolver
el payload crudo del evento), ambos con test de regresión en `sse.test.ts`.
Detalle completo en `frontend-implementation-plan.md` §10, pendiente P5.

#### Fase 3 — Resultados de Etapa 1
Archivo clave: `src/routes/results/Etapa1ResultView.tsx` (componente
presentacional puro, reutilizado en Fase 4). Tres modos de presentación sobre
el mismo `Etapa1Result`: docencia+paso_a_paso (`<details>` colapsados, FE-15),
docencia+experto (tarjetas siempre abiertas), anónimo (fuerza experto, UX-D).
Sin sustitución de fórmulas (FE-14 — esa pieza es del PDF de exportación, no
de esta pantalla) ni gráficos (FE-16 — `Etapa1Result` no expone la serie
cruda). Verificado con datos reales en los tres modos.

#### Fase 4 — Historial
Archivos clave: `src/routes/history/HistoryPage.tsx`,
`src/routes/history/HistoryDetailPage.tsx`. Paginación 100% client-side,
tamaño de página 10 (FE-18 — sin volumen real que lo justifique todavía).
`HistoryDetailPage` lee `modo` de `AnalysisDetail.modo` persistido, no de
router state (ruta bookmarkeable). Verificado: lista y detalle reales
coinciden exactamente con lo visto en vivo en Fase 2/3.

#### Fase 5 — Mocks de Etapa 2
Archivos clave: `src/routes/ranking/RankingPage.tsx`,
`src/routes/design-events/DesignEventsPage.tsx`, `src/mocks/`. MSW intercepta
solo `POST /analysis/design-events` (tiene contrato REST documentado); el
ranking no tiene endpoint REST real (solo evento SSE nunca emitido) y
`RankingPage` importa el mock directo, sin red de por medio — DECISIÓN 042.
`PendingBadge` visible en ambas pantallas. Verificado manualmente en el
navegador de dev (única fase que no depende de backend real, por diseño).

#### Fase 6 — Pulido y accesibilidad — COMPLETA salvo D11
Bloque D (`docs/frontend/plan-mejora-frontend-pasada2.md`) y M3
(`docs/frontend/plan-mejora-frontend-pasada3.md`) cerraron las correcciones
puntuales de código y accesibilidad. Con `inert` ya aplicado al contenedor
de fondo (D10), el foco no podía escaparse del diálogo — el grueso del
focus trap ya estaba resuelto de hecho. M3 cerró lo que faltaba en
`StreamPage.tsx`, modal de atípico:
- **Auto-foco al abrir** — al contenedor del diálogo (`tabIndex={-1}`), no
  a ninguno de los dos botones. Foco en un botón sesgaría al usuario hacia
  esa decisión ante un Enter apurado; ninguna de las dos es un "cancelar"
  por defecto.
- **Escape no cierra el modal ni descarta la decisión** — decisión de
  producto, no de accesibilidad: el backend está bloqueado esperando
  (`session_store`, hasta 300s) y "rechazar"/"aceptar" son las únicas dos
  decisiones válidas, cada una con su propio código de auditoría
  (`TEST_OUTLIER_REJECTED_BY_USER`/`TEST_OUTLIER_ACCEPTED_BY_USER`) — un
  Escape accidental no puede convertirse silenciosamente en ninguna de las
  dos. Escape solo devuelve el foco al contenedor del diálogo.
- **Restaura el foco** al elemento que lo tenía cuando el modal se cierra.

Las tres con test de regresión (`StreamPage.test.tsx`). Único pendiente real
de Fase 6: `docs/decisiones/decision043.md` — DECISIÓN 043 (contraste WCAG
del tema Instrumento) — identidad visual fijada, pendiente de decisión de
Kevin/Octavio, no de implementación.

#### Verificación E2E fuera de las 6 fases nominales (backlog P4-P7)
~~Corrida contra `docker-compose up backend postgres` real, no mockeada. Login →
`200` + cookie, `GET /me` → `200`, logout → `200` + cookie borrada
verificada. Config→stream con CSV sintético de 40 años y atípico forzado,
resultados en los tres modos, historial con 6 análisis reales — todo
verificado punta a punta.~~ Único tramo genuinamente bloqueado: registro→verify,
por falta de SMTP real en desarrollo (no resoluble desde este backlog). Usuario
de prueba y sus análisis borrados de Postgres al cerrar la verificación — no
queda dato de prueba en la BD.

**Corrección 31/07/2026 (`fix/frontend-ui-integracion`, informe de diagnóstico
de UI rota):** el párrafo de arriba tachado quedó invalidado el mismo día que
se escribió — el commit `c27d6ac` (más abajo, "Bugs corregidos como parte de
esta rama") cambió el ciclo de vida de `StreamPage` horas después de esta
verificación, e introdujo F1 (`docs/frontend/informe-diagnostico-ui-rota.md`):
bajo `<StrictMode>` (el modo real de desarrollo), el stream se abortaba a sí
mismo al montar y nunca avanzaba. Dos PRs se mergearon a `staging` con CI
verde y 98 tests en verde sin que nadie volviera a abrir el navegador después
de ese commit. La verificación "Config→stream... verificado punta a punta"
citada arriba corresponde a un estado del código anterior a `c27d6ac`, no al
que terminó mergeado. F1 fue diagnosticado y corregido en
`fix/frontend-ui-integracion` — ver ese informe y
`docs/frontend/plan-arreglo-ui-rota.md` para el detalle completo y el resto de
los once defectos encontrados en la misma pasada (F2-F12).

#### Bugs corregidos como parte de esta rama
- `useAnalysisStream`: `complete` pisaba una `fase="error"` previa con
  `"done"` — corregido, `complete` ya no sobreescribe una fase de error.
- `useAnalysisStream`: `result_etapa1` nunca llegaba a `state.result` porque
  `onmessage` no desenvolvía ese evento en particular — corregido.

#### Decisiones asociadas
D1-D20 del plan original, migradas a `docs/decisiones/` según criterio
explícito — ver DECISIÓN 039 (criterio de promoción y tabla de equivalencia
completa), DECISIÓN 040 (SSE sobre fetch), DECISIÓN 041 (sin TanStack Query,
patrón único de test), DECISIÓN 042 (alcance de mocks de Etapa 2). El resto
(D2, D6-D18) quedan como notas `FE-NN` en `frontend-implementation-plan.md` §10.

#### Pendiente
- Fase 6 (pulido, accesibilidad) — ver Bloque D del plan de mejora.
- Tres hallazgos de backend encontrados durante esta implementación pero no
  escalados en su momento — registrados recién en la pasada de mejora
  posterior: DECISIÓN 036 (partición de Cramer personalizada inalcanzable),
  DECISIÓN 037 (`etapas` descartado, `AnalysisRequest` sin cablear),
  DECISIÓN 038 (códigos de error fuera del catálogo).

---

### fix/frontend-ui-integracion — Bloques 0-3 completos

Rama de arreglo abierta tras el hallazgo de que la app estaba rota en uso
real pese a dos PRs mergeados con CI verde (ver la corrección de 31/07/2026
más arriba). Punto de entrada completo:
`docs/frontend/informe-diagnostico-ui-rota.md` (diagnóstico, doce defectos
F1-F12) y `docs/frontend/plan-arreglo-ui-rota.md` (plan priorizado en 4
bloques). Sale de `staging` (no de `fix/frontend-pasada2`, que ya estaba
mergeado a `staging` vía PR #18 al momento de abrir esta rama).

**Bloque 0 — reproducir antes de arreglar:** `StreamPage.lifecycle.test.tsx`
escrito en rojo contra el código real, confirmando F1. Confirmación manual en
navegador (Network tab: `POST /analysis/stream` en `net::ERR_ABORTED`) y
contraprueba diferencial (sacar `<StrictMode>` temporalmente, ver que el
stream avanza, revertir de inmediato).

**Bloque 1 — bloqueantes (P0):**
- 1.3(a): `scripts/seed-dev-user.sh` + `clean-dev-user.sh` — automatiza el
  INSERT bcrypt que este archivo ya documentaba en prosa, vía `docker compose
  exec` (no nombres de contenedor hardcodeados).
- 1.1+1.2 (F1): `StreamPage.tsx` pasa a un solo efecto con limpieza
  colocada — la guarda `startedRef` de dos efectos separados es lo que
  rompía bajo el doble montaje de StrictMode. `sse.ts::onclose` ahora mueve
  la fase a `error` con código nuevo `STREAM_CLOSED_EARLY` si el servidor
  cierra sin `complete`.
- 1.4 (F3): `AuthProvider.refetch()` distingue 401 legítimo de un fallo real
  (red caída, CORS, 500); `login()` ahora puede lanzar y lo hace con
  `SESSION_NOT_ESTABLISHED` si `/me` no confirma la sesión tras un login
  200.

**Capa 2 de testing (4.1+4.2):** `src/test/renderPage.tsx` — toda página se
renderiza bajo `StrictMode` desde ahora (regla, no algo que recordar por
archivo). `StreamPage.integration.test.tsx` — componente y hook reales, solo
la red interceptada en el borde (mock de `fetchEventSource`, no MSW — ver
nota inline sobre por qué, coherente con DECISIÓN 041). `routes.navigation.test.tsx` —
grafo de navegación sobre el array `routes` real, no rutas de mentira.

**Bloque 2 — navegación (F4-F8):** `TopBar` con links reales según sesión
(`enterAnonymously`/`exitAnonymously` en `AuthProvider`), "Cerrar
sesión"/"Salir" navegan a `/` en vez de dejar al usuario en la misma
pantalla. Botón "Continuar a Etapa 2" en `ResultsPage` (con `PendingBadge`).
Guard nuevo `RequireSession` (auth o anónimo) en `/config`, `/stream`,
`/results`, `/ranking`, `/design-events`. Timeline de `StreamPage` reemplaza
`disabled` nativo por `aria-disabled` + pill "esperando resultados" — un
paso sin resultados todavía y uno roto se veían idénticos antes.

**Bloque 3 — infraestructura (F9-F12):** `frontend/Dockerfile` (multi-stage,
nginx sirviendo el build estático) — verificado end-to-end por primera vez
en la historia del proyecto: `docker-compose up -d` levanta los cuatro
servicios, `http://localhost/` responde 200, `/ping` proxea al backend real,
`/config` sirve la SPA vía `try_files` fallback, login real funciona same-origin
a través de nginx. Default de CORS en `main.py` corregido de `:3000` a
`:5173` (F10 — el resto de "unificar FRONTEND_ORIGIN/FRONTEND_URL" resultó
innecesario: `.env`/`.env.example` ya las documentaban como dos variables
intencionalmente separadas, con valores ya correctos). `nginx.conf` proxea
`/ping` (F11). `.catch()` agregado al `postDesignEvents(...)` de
`DesignEventsPage` (F12).

**Pendiente de esta rama:** Bloque 4.3 (E2E con Playwright) y 1.3(b)
(escotilla SMTP en desarrollo) — ambos requieren escribir una DECISIÓN nueva
primero (046 y 045 respectivamente [corrección 05/08/2026, H1 del roadmap
post-pasada4: 045 la tomó "Fondos animados en Canvas 2D" — la escotilla SMTP
queda reasignada a **049**, ver `docs/decisiones/README.md`]) antes de
implementarse; no se avanzó sobre ninguno de los dos. `testing.md` y
`architecture.md` actualizados en consecuencia (ver sus propias notas de
corrección).

---

## Decisiones pendientes — no implementar hasta confirmar

- **Partición de Cramer personalizada** — inalcanzable hoy por el endpoint
  `POST /api/v1/analysis/stream`: `cramer_particion` llega siempre como `str`
  vía `multipart/form-data`, y `calcular_cramer` indexa `particion["n1_pct"]`
  asumiendo `dict` en cualquier valor distinto de `"default"` → `TypeError`
  no manejado. El botón "Personalizada" de `ConfigPage.tsx` está `disabled`
  en consecuencia. Tres opciones evaluadas sin decisión cerrada — ver
  `docs/decisiones/decision036.md` — DECISIÓN 036. No implementar ninguna
  sin decidir entre las tres opciones primero.

- **`etapas` se recibe y se descarta en `POST /analysis/stream`** —
  `api/v1/analysis.py` declara `etapas: str = Form("1")` pero nunca lo pasa
  a `stream_etapa1()`; el frontend tampoco lo envía.
  `schemas/analysis.py::AnalysisRequest` (el modelo tipado que representaría
  el contrato completo) no lo importa ninguna ruta — código muerto. Inocuo
  mientras Etapa 2 esté mockeada en el frontend; **prioridad para M2/M3**,
  cuando Etapa 2 se exponga de verdad y el backend necesite saber si el
  usuario pidió `[1]` o `[1, 2]`. Ver `docs/decisiones/decision037.md` —
  DECISIÓN 037.

- **Contraste WCAG AA de `tokens.instrumento.css`** — pendiente heredado de
  Fase 6 del frontend, hallazgos y propuesta calculada movidos a
  `docs/decisiones/decision043.md` — DECISIÓN 043 (M1, pasada 3 de mejora).
  Estado: PENDIENTE DE DECISIÓN — Kevin/Octavio.

---

## Entorno de desarrollo — datos de prueba

### Usuario de prueba para smoke tests de auth

Creado durante el smoke test de feature/auth-refactor en staging local.
No usar este mail en producción ni en entornos compartidos.

```
email:    2200631@ucc.edu.ar
password: test1234
nombre:   Octavio
```

**Por qué documentarlo:** los tokens de verificación quedan en
`_pending_tokens` (memoria del proceso) y el usuario queda en la BD hasta
limpieza explícita. Sin esta documentación, un segundo smoke test fallaría
con `AUTH_EMAIL_ALREADY_REGISTERED` sin que quede claro por qué.

**Cómo obtener el token de verificación (mock SMTP) — DESACTUALIZADO, ver nota 28/07/2026 abajo:**
Con el backend corriendo, después de POST /register:
```bash
docker-compose logs backend | grep "MOCK SMTP" | tail -1
```
El token aparece en la URL: `.../auth/verify?token=<TOKEN>`

**ACTUALIZACIÓN 28/07/2026 (desde la Fase 1 del frontend, Auth):** este
procedimiento ya no funciona. `print("MOCK SMTP...")` pertenecía al mock de
`auth/email.py` de la Parte 1, reemplazado por completo en la Parte 2
(19/07/2026, envío real con `aiosmtplib`) — hoy no hay ningún log de token.
Peor aún: sin `SMTP_HOST/USER/PASSWORD` configurados, `send_verification_email()`
lanza `RuntimeError` **antes** de que el token se guarde en `_pending_tokens`, y
como el mail se manda antes de comitear el usuario (DECISIÓN 032, evita
huérfanos), `POST /register` **no crea ningún usuario ni token** — no hay nada
que rescatar de los logs. Sin credenciales SMTP reales, el flujo
registro→verify no se puede probar localmente en absoluto (ni con este
procedimiento ni con ningún otro atajo actual); solo queda cobertura de tests
con `fetch` mockeado. Ver `docs/frontend/frontend-implementation-plan.md` §10, Decisión
D6, para el detalle completo y por qué se decidió no tocar el backend para
reintroducir un log dev-only.

**Cómo limpiar el usuario después del smoke test:**
El usuario de psql que acepta el contenedor es el definido por
`POSTGRES_USER` en el `.env` (actualmente `metis`) — no `metis_user`
genérico. Verificar el valor con `docker inspect pi-postgres-1 | grep
POSTGRES_USER` antes de correr:
```bash
docker exec pi-postgres-1 bash -c \
  "psql -U metis -d metis -c \"DELETE FROM users WHERE email = '2200631@ucc.edu.ar';\""
```
Verificar que no quedó:
```bash
docker exec pi-postgres-1 bash -c \
  "psql -U metis -d metis -c \"SELECT email FROM users;\""
```

**Cookie de sesión durante el smoke test:**
Se guarda en `/tmp/metis_smoke_cookies.txt` — archivo temporal, no commitear.
Se destruye al hacer POST /logout o al borrar el archivo.

**ACTUALIZACIÓN 29/07/2026 — insertar un usuario verificado sin pasar por
/register (sigue sin haber SMTP real):** confirmado que sin SMTP,
`POST /register` falla por completo (ver nota de arriba) — no hay forma de
crear NINGÚN usuario verificado vía la API todavía. Para probar
login/logout/me/historial del lado del frontend (verificación E2E del backlog
P4-P7, fuera de las 6 fases nominales del frontend — ver
"feature/frontend-fases1-5 — COMPLETA" más abajo, contra
`docker-compose up backend postgres`), se insertó un usuario ya
verificado directo en Postgres, generando el hash bcrypt con el propio
Python del contenedor backend (evita instalar `bcrypt` en el host):
```bash
docker exec pi_metis-backend-1 python3 -c \
  "import bcrypt; print(bcrypt.hashpw(b'una-password', bcrypt.gensalt()).decode())"

docker exec pi_metis-postgres-1 psql -U metis_user -d metis -c "
INSERT INTO users (id, email, nombre, password_hash, email_verified, created_at)
VALUES (gen_random_uuid(), 'legajo@ucc.edu.ar', 'Nombre', '<hash de arriba>', true, now());
"
```
Notar `pi_metis-backend-1`/`pi_metis-postgres-1` (guión bajo, prefijo del
nombre de carpeta real `PI_METIS`) — no `pi-postgres-1` con guión medio como
en las notas anteriores de este archivo; el prefijo del contenedor lo decide
Docker Compose a partir del nombre del directorio, no es fijo entre sesiones.
Verificar con `docker ps` antes de asumir cualquiera de los dos.
Limpieza al cerrar, incluyendo los análisis que haya generado el usuario
(`analysis_results` se limpia solo por `ON DELETE CASCADE`):
```bash
docker exec pi_metis-postgres-1 psql -U metis_user -d metis -c \
  "DELETE FROM analyses WHERE user_id = (SELECT id FROM users WHERE email = 'legajo@ucc.edu.ar');"
docker exec pi_metis-postgres-1 psql -U metis_user -d metis -c \
  "DELETE FROM users WHERE email = 'legajo@ucc.edu.ar';"
```

### Otros emails de prueba usados — Auth Parte 2 (SMTP real, 19-20/07/2026)

`2200999@ucc.edu.ar` — legajo inventado para el primer intento de
POST /register del smoke test de Camino A, antes de aclarar que hacía
falta una casilla real para confirmar entrega. Quedó huérfano en `users`
(201 sin verificar) porque el smoke test recién detectó el error un paso
después. Limpiado el 20/07/2026 con el mismo procedimiento de arriba.
No reusar — no es una casilla real.

### Regla general para datos de prueba

- Nunca commitear datos de prueba (usuarios, tokens, cookies) al repositorio
- Siempre limpiar la BD de staging local después de smoke tests manuales
- Si se necesita un fixture de BD persistente, documentarlo aquí con el
  script SQL de creación y el procedimiento de limpieza
- Preferir emails con formato de legajo (7 dígitos + @ucc.edu.ar) para
  pruebas — son inválidos en producción real y fáciles de identificar

---

## Milestones del proyecto

M1 — SSE operativo en staging
     CI verde, ruff limpio, pipeline emite eventos reales,
     tests unitarios core pasando

### M1 — Estado actual: EN CURSO

Criterios completados al 15 de Mayo de 2026:
- CI verde ✓
- ruff limpio ✓
- Pipeline emite eventos reales ✓
- Tests unitarios comportamiento 51/51 ✓
- Auth refactorizada y verificada end-to-end ✓

Criterios pendientes — bloqueados por factores externos:
- Tests de regresión matemática: esperando series reales
  de Facundo en formato digital. NOTA 15/07/2026: distinto del análisis
  E2E manual/documentado ya cerrado en `.claude/rules/auditoria/` (que usó
  series transcriptas del PDF de la tesis, no un fixture digital nativo de
  Facundo) — ese análisis no satisface este criterio de M1 tal como está
  redactado, sigue pendiente el archivo digital real si se quiere una
  suite automatizada en `tests/regression/`.
- Auth Parte 2 (SMTP real): esperando credenciales IT
  (cuenta metis-noreply@ucc.edu.ar + App Password). **RESUELTO 15/07/2026
  — credenciales recibidas de Soporte IT de la UCC desde 10/06/2026.**
- Verificación end-to-end del pipeline con CSV real:
  pendiente hasta tener frontend o cliente HTTP configurado

**ACTUALIZACIÓN 19 de Julio de 2026:** Auth Parte 2 (SMTP real)
completada — implementación, tests (10/10 en tests/unit/auth/) y
documentación (decision032.md, decision033.md) cerrados. De los tres
criterios pendientes listados arriba, éste queda resuelto por
completo — no sólo credenciales recibidas, como marcaba la nota del
15/07. Quedan 2 criterios pendientes para cerrar M1: tests de
regresión matemática y verificación E2E con CSV real.

**ACTUALIZACIÓN 29 de Julio de 2026:** Verificación end-to-end del pipeline
con CSV real — **CERRADA.** El backlog P4-P7 de
`docs/frontend/frontend-implementation-plan.md` §10 (pendiente P5) corrió un CSV
sintético de 40 años contra el backend real (`docker-compose up backend
postgres`, no mockeado), con un valor forzado a 6-7x el resto para disparar
Chow: los 4 grupos de pruebas de Etapa 1 llegaron y se resolvieron
correctamente, el atípico pausó el stream con el modal real, y
`resolveOutlier("rechazar")` desbloqueó la `iteracion:2` con el reemplazo
correcto de resultados (sin duplicar). Dos bugs reales de `useAnalysisStream`
aparecieron recién en esta verificación — ver
"feature/frontend-fases1-5 — COMPLETA" más abajo para el detalle. De los tres
criterios pendientes originales de M1, quedan **2**: tests de regresión
matemática (bloqueado externamente, esperando series de Facundo) y el tramo
registro→verify de Auth (bloqueado por falta de SMTP real en desarrollo — no
es un criterio de M1 en sí, pero es el único hueco real que queda en la
superficie de auth verificada).

**ACTUALIZACIÓN 29 de Julio de 2026 (pasada 3):** `pytest -m unit` corrido por
primera vez de punta a punta contra un entorno real — vía Docker
(`docker-compose up -d backend postgres`, `docker exec pi_metis-backend-1
pytest -m unit -v`), no contra el Python del host (que no tiene las
dependencias instaladas, ni `venv` en el repo — ver `CLAUDE.md`, sección de
comandos, actualizada con el procedimiento). **131 passed, 1 skipped.**
`ruff check`/`ruff format --check` también verificados dentro del
contenedor, ambos limpios. Esto no cierra el criterio de "tests de regresión
matemática" (sigue bloqueado esperando las series digitales de Facundo — son
tests distintos, en `tests/regression/`), pero confirma que la suite
`unit` existente corre reproduciblemente, cosa que nunca se había verificado
de punta a punta en este repo antes de esta pasada.

M1 no se cierra hasta que los criterios pendientes estén resueltos.
El desarrollo continúa hacia M2 en paralelo.

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