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
  inconsistencia IV-238 vs IV-243/244 (ver decisions-log.md)

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
   (denom_b≈0 → B_hat→∞). Ver DECISIÓN 010 en decisions-log.md.
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

### feature/auth-refactor — mergeado a staging ✓

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

#### Smoke test de auth — COMPLETADO ✓

7 pasos ejecutados contra Docker local. Resultado: todos pasaron.

Bugs encontrados y corregidos durante el smoke test:
- auth/email.py: `logger.info()` → `print(flush=True)` — el root logger suprime
  INFO de loggers de aplicación; print garantiza visibilidad en Docker logs
- auth/router.py: `datetime.now(timezone.utc)` → `datetime.utcnow()` en la
  actualización de `last_login` — TIMESTAMP WITHOUT TIME ZONE no acepta
  datetime timezone-aware; el error era un 500 silencioso en POST /login
- decisions-log.md, sprint.md: corregido el usuario psql en comandos de
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

---

## Decisiones pendientes — no implementar hasta confirmar

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

**Cómo obtener el token de verificación (mock SMTP):**
Con el backend corriendo, después de POST /register:
```bash
docker-compose logs backend | grep "MOCK SMTP" | tail -1
```
El token aparece en la URL: `.../auth/verify?token=<TOKEN>`

**Cómo limpiar el usuario después del smoke test:**
El usuario de psql es el valor de `POSTGRES_USER` en el `.env` (actualmente `metis`):
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
  de Facundo en formato digital
- Auth Parte 2 (SMTP real): esperando credenciales IT
  (cuenta metis-noreply@ucc.edu.ar + App Password)
- Verificación end-to-end del pipeline con CSV real:
  pendiente hasta tener frontend o cliente HTTP configurado

M1 no se cierra hasta que los tres criterios pendientes estén resueltos.
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