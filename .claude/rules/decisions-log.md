# Registro de Decisiones Cambiadas — METIS

Este archivo documenta decisiones de arquitectura que fueron tomadas, luego
descartadas, y reemplazadas. Su propósito es preservar la trazabilidad de por
qué se llegó al estado actual sin contaminar los archivos de decisiones vigentes.

Cuando Claude Code lea este archivo, debe entender que las decisiones marcadas
como DESCARTADA no representan el estado actual del sistema — representan el
camino recorrido para llegar a él.

---

## DECISIÓN 001 — Autenticación CU-01
**Fecha:** 10 de Mayo de 2026
**Estado:** PARCIALMENTE IMPLEMENTADO — Parte 1 completa, Parte 2 pendiente de credenciales SMTP de IT

### Decisión original
Autenticación mediante Google OAuth 2.0 con verificación de dominio @ucc.edu.ar.
El mail institucional UCC es una cuenta Google Workspace, por lo que OAuth era el
mecanismo natural. El flujo consistía en: el usuario redirige a Google, Google
autentica, Google envía el callback al backend de METIS en el endpoint
GET /api/v1/auth/callback, el backend verifica @ucc.edu.ar, genera un JWT propio
y lo setea en HttpOnly Cookie. El frontend nunca ve el JWT.

Esta decisión fue implementada en:
- auth/google.py — lógica de intercambio de código y verificación de dominio
- auth/router.py — endpoints /auth/google, /auth/callback, /auth/logout, /auth/me
- .env.example — variables GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

### Por qué fue descartada
METIS corre en la intranet de la UCC. El servidor no tiene puertos expuestos al
exterior — puede hacer requests salientes a internet, pero no puede recibir
conexiones entrantes desde internet. Google OAuth requiere que Google contacte
directamente al servidor para enviar el callback en el paso 4 del flujo. Ese
tráfico es entrante desde internet hacia el servidor, y está bloqueado por la
configuración de red de la UCC. Google OAuth es técnicamente inviable en este
entorno, independientemente de que el servidor pueda hacer requests salientes.

Active Directory institucional también fue evaluado y descartado: existe en la UCC
pero requiere aprobación manual de IT por cada usuario nuevo, lo que es inviable
para un sistema docente con alumnos que rotan cada semestre.

### Decisión de reemplazo — PENDIENTE DE CONFIRMACIÓN CON IT
Autenticación propia con usuario/contraseña + bcrypt + JWT en HttpOnly Cookie.
El mecanismo de JWT en HttpOnly Cookie no cambia — solo cambia cómo se obtiene el JWT.

Hay dos variantes según disponibilidad de SMTP en el servidor:

OPCIÓN A CON SMTP (preferida):
  El servidor puede enviar mails porque tiene acceso saliente a internet.
  El mail de verificación llega al Gmail institucional del usuario.
  El usuario hace click desde su navegador — tráfico interno, funciona.
  - POST /api/v1/auth/register {email, password, nombre}
  - Backend valida formato @ucc.edu.ar, hashea password con bcrypt
  - Backend crea usuario con email_verified=False
  - Backend envía mail con token de verificación via SMTP
  - GET /api/v1/auth/verify?token=XXX activa la cuenta
  - POST /api/v1/auth/login {email, password} genera JWT en HttpOnly Cookie

OPCIÓN A SIN SMTP (fallback):
  Igual pero sin verificación por mail.
  La cuenta queda activa inmediatamente al registrarse.
  Solo se valida el formato del mail, no su existencia real.
  Suficiente para intranet universitaria donde la red ya garantiza pertenencia
  institucional.

Validación de formato para alumnos: exactamente 7 dígitos numéricos + @ucc.edu.ar
Validación de formato para docentes: cualquier formato válido + @ucc.edu.ar

### Qué hay que hacer cuando IT confirme
1. Eliminar auth/google.py
2. Reescribir auth/router.py con los nuevos endpoints
3. Actualizar auth/dependencies.py — get_current_user y get_optional_user
   no cambian en su contrato, solo en cómo verifican el JWT
4. Actualizar .env.example: eliminar variables de Google, agregar SMTP si aplica
5. Agregar columna password_hash y email_verified a la tabla users en BD
6. Actualizar tests de integración — mock de OAuth reemplazado por mock de login

### Estado actual del código
auth/google.py y auth/router.py tienen implementado Google OAuth.
Ese código está pendiente de reemplazo. No agregar funcionalidad sobre él.
No usar auth/google.py como referencia para nada nuevo.
NO tocar auth/ hasta que Octavio confirme la decisión de IT.

---

---

## DECISIÓN 002 — Esquema tabla users y refactor de auth/
**Fecha:** 10 de Mayo de 2026
**Estado:** IMPLEMENTADO — password_hash y email_verified agregados a users via migración 002 de Alembic

### Contexto
Consecuencia directa de DECISIÓN 001. El reemplazo de Google OAuth por
autenticación propia requiere cambios en la tabla users y en auth/.

### Archivos que SE ELIMINAN cuando se implemente
- metis/auth/google.py — completo. Toda la lógica de OAuth con Google
  (get_google_auth_url, exchange_code_for_email, is_ucc_email) deja de existir.

### Archivos que SE REESCRIBEN cuando se implemente
- metis/auth/router.py — los endpoints /google y /callback se eliminan.
  Se reemplazan por /register, /login, y opcionalmente /verify (si hay SMTP).
  /logout y /me se mantienen con la misma lógica actual.

### Archivos que NO CAMBIAN
- metis/auth/jwt.py — create_access_token, decode_access_token, is_valid_token
  permanecen exactamente igual. El JWT se genera y valida de la misma forma.
- metis/auth/dependencies.py — get_current_user y get_optional_user permanecen
  exactamente igual. Leen el JWT de la HttpOnly Cookie de la misma forma.
- metis/auth/__init__.py — sin cambios.

### Cambio en db/models/user.py
El modelo User actual tiene: id, email, nombre, created_at, last_login.
Agregar dos columnas:
  password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
  email_verified: Mapped[bool] = mapped_column(default=False)

Con SMTP: email_verified arranca en False, se setea True al verificar el mail.
Sin SMTP: email_verified se setea True inmediatamente al registrarse.

### Variables de entorno
Eliminar de .env.example:
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_REDIRECT_URI

Agregar a .env.example (solo si SMTP disponible):
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=
  SMTP_PASSWORD=

JWT_SECRET_KEY, JWT_EXPIRE_MINUTES, FRONTEND_URL, ENV se mantienen igual.

### Estado actual del código
Ninguno de estos cambios está implementado todavía.
NO tocar auth/ hasta confirmar con IT disponibilidad de SMTP.

---

## DECISIÓN 003 — Gestión de migraciones de esquema: Alembic
**Fecha:** 14 de Mayo de 2026
**Estado:** PARCIALMENTE IMPLEMENTADO — Alembic configurado y migraciones generadas. Pendiente: ejecutar contra BD activa cuando Docker esté disponible

### Contexto
Al implementar feature/auth-refactor, la tabla users requiere dos columnas
nuevas (password_hash, email_verified — ver DECISIÓN 002). La tabla ya existe
en PostgreSQL con el esquema original. SQLAlchemy no modifica tablas existentes
automáticamente — hay que decirle explícitamente a PostgreSQL qué cambió.

### Opciones evaluadas

OPCIÓN DESCARTADA — Dropear y recrear la tabla:
Funciona cuando no hay datos reales. Pero es una solución manual sin memoria:
cada cambio de esquema futuro requiere recordar qué se hizo antes, aplicarlo
a mano en cada entorno, y coordinar con Kevin. En producción con datos reales
de docentes y alumnos, esta opción no existe. Introducirla ahora crearía una
deuda técnica que se pagaría cara más adelante.

OPCIÓN ELEGIDA — Alembic:
Sistema de migraciones estándar para SQLAlchemy. Cada cambio de esquema genera
un script versionado que describe exactamente qué cambió. Alembic mantiene
registro de qué migraciones están aplicadas en cada entorno y aplica solo las
que faltan. Es el equivalente a Git pero para la base de datos — trazabilidad
completa del historial de esquema.

### Por qué Alembic aunque no haya datos todavía
No es por los datos — es por el proceso. Este es el proceso correcto que se
va a usar en producción, y establecerlo ahora tiene costo bajo. Si se dropea
ahora, cuando llegue producción con datos reales hay que introducir Alembic
de todas formas, pero sobre una base que nunca lo usó y con migraciones que
reconstruir desde cero. Hacerlo ahora, sin presión, con un esquema simple,
es el momento correcto.

### Justificación ante tribunal de ISI
"Usamos Alembic para gestionar cambios de esquema" es una respuesta técnica
sólida con justificación clara. Cada migración es un archivo versionado con
ID único y descripción — historial completo de cómo evolucionó el esquema.

### Lo que se implementa
Paso 0 de feature/auth-refactor:
- alembic init en backend/
- Configurar alembic.ini y env.py para usar los modelos de METIS
- Migración 001: esquema inicial (tablas existentes)
- Migración 002: agregar password_hash y email_verified a users

Todas las migraciones futuras siguen el mismo patrón:
cambiar el modelo → alembic revision --autogenerate → alembic upgrade head

---

## DECISIÓN 004 — Mecanismo de envío de mail para verificación de cuenta
**Fecha:** 14 de Mayo de 2026
**Estado:** PARCIALMENTE IMPLEMENTADO — mock SMTP en desarrollo (auth/email.py), aiosmtplib pendiente de credenciales IT (cuenta metis-noreply@ucc.edu.ar + App Password)

### Contexto
Con la autenticación propia usuario/contraseña confirmada (DECISIÓN 001),
el sistema necesita verificar que el mail @ucc.edu.ar ingresado al registrarse
existe realmente. Esto requiere enviar un mail de verificación desde el servidor.
El servidor tiene acceso saliente a internet confirmado por IT (puerto 587 disponible).
Google deprecó la autenticación SMTP con usuario/contraseña simple — se requiere
uno de los dos métodos actuales.

### Opciones evaluadas

OPCIÓN A — OAuth2 con Google Cloud Console:
IT crea un proyecto en Google Cloud Console bajo el tenant de la UCC.
Se generan Client ID y Client Secret para la aplicación.
El servidor obtiene un Refresh Token y lo usa para cada envío.
Ventaja: estándar de seguridad más alto de Google actualmente.
Desventaja: requiere configuración de proyecto en Google Cloud — más complejo
para IT y para la implementación.

OPCIÓN B — App Password (contraseña de aplicación):
IT crea una cuenta emisora institucional (ej. metis-noreply@ucc.edu.ar)
con verificación en dos pasos activada.
Se genera un App Password de 16 dígitos exclusivo para el servidor.
El servidor se conecta a smtp.gmail.com:587 con esa cuenta y ese password.
Ventaja: implementación directa con aiosmtplib, sin proyectos en la nube.
Desventaja: ninguna relevante para el volumen de mails de METIS.

### Decisión tomada
Opción B — App Password. Confirmado por IT de la UCC en Mayo 2026.
IT indicó que es la opción más conveniente para este caso.

### Estado de implementación
- Parte 1 (sin credenciales): auth/email.py implementado con mock en desarrollo.
  En lugar de enviar, loggea el token de verificación en consola con comentario
  explícito de pendiente.
- Parte 2 (con credenciales): pendiente de que IT provea la cuenta emisora
  metis-noreply@ucc.edu.ar y el App Password de 16 dígitos.

### Variables de entorno cuando IT provea las credenciales
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=metis-noreply@ucc.edu.ar
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

### Librería de implementación
aiosmtplib — cliente SMTP async compatible con FastAPI.
Agregar a requirements.txt cuando se implemente Parte 2.

---

## DECISIÓN 005 — Almacenamiento de tokens de verificación en memoria
**Fecha:** 14 de Mayo de 2026
**Estado:** ACEPTADO para V1.0 — revisión post-M5

### Contexto
Los tokens de verificación de mail se almacenan en un dict en memoria
del proceso (_pending_tokens en auth/router.py). Es simple y suficiente
para V1.0 con un solo worker en intranet.

### Limitación conocida
En producción con múltiples workers (uvicorn workers o Docker replicas),
cada worker tiene su propio dict. El token generado en worker A no lo
encuentra worker B — el usuario no puede verificar su cuenta.

### Decisión
Aceptado para V1.0 — METIS corre con un solo worker en intranet.
Solución futura (post-M5): mover tokens a tabla BD o Redis.

---

## DECISIÓN 006 — Regla de nullability en migraciones Alembic + SQLAlchemy
**Fecha:** 15 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar en todas las migraciones futuras

### Contexto
La migración 001 fue escrita manualmente porque Docker no estaba activo al
momento de implementar feature/auth-refactor. Al escribirla manualmente se
usó `nullable=True` para columnas con `server_default` o FK opcionales, sin
considerar cómo SQLAlchemy infiere la nullability a partir del tipo de la
columna en `Mapped[T]`.

Al levantar Docker y correr `alembic check`, se detectaron 9 columnas donde
el esquema de la BD (nullable=True) divergía de lo que los modelos declaraban
(NOT NULL). Se generó la migración 003 con `--autogenerate` para corregirlo.

### La regla

SQLAlchemy con `Mapped[T]` infiere la nullability directamente del tipo Python:

```python
# NOT NULL en la BD — T no es Optional
nombre: Mapped[str] = mapped_column(String(255))
created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
activo: Mapped[bool] = mapped_column(Boolean, default=True)

# NULLABLE en la BD — T es Optional (con | None o Optional[T])
nombre: Mapped[str | None] = mapped_column(String(255))
last_login: Mapped[datetime | None] = mapped_column(DateTime)
```

Tener un `server_default` o `default` NO implica nullable. El default garantiza
que la BD siempre tendrá un valor, pero la columna sigue siendo NOT NULL.
El nullable lo determina únicamente si T es Optional o no.

### Por qué importa para migraciones manuales
Cuando se escribe una migración a mano, `nullable` debe coincidir con lo que
el modelo SQLAlchemy declara. Si se escribe `nullable=True` para una columna
cuyo modelo usa `Mapped[T]` (sin Optional), `alembic check` fallará y la BD
tendrá constraints incorrectas.

### Proceso correcto para migraciones futuras

**Con Docker activo (caso normal):**
```bash
# 1. Cambiar el modelo SQLAlchemy
# 2. Generar la migración con autogenerate — Alembic lee los modelos y la BD
alembic revision --autogenerate -m "descripcion_del_cambio"
# 3. Revisar el archivo generado antes de aplicar
# 4. Aplicar
alembic upgrade head
# 5. Verificar que no queden diferencias
alembic check
```

**Sin Docker activo (caso excepcional):**
Escribir la migración manualmente prestando atención a la regla de nullability.
Marcar el archivo con el comentario "generada manualmente — verificar con
`alembic check` cuando Docker esté disponible". Al levantar Docker, correr
`alembic check` inmediatamente y generar una migración correctiva si hay
divergencias (como sucedió con la migración 003).

### Columnas corregidas en migración 003
Las siguientes columnas estaban definidas como nullable=True en la BD (por
error en migración 001) y se corrigieron a NOT NULL mediante la migración 003:

- `analyses.user_id` — FK obligatoria (analyses solo se persisten en CU-01)
- `analyses.created_at` — timestamp con server_default=now()
- `analysis_results.analysis_id` — FK obligatoria al análisis padre
- `api_clients.auto_clean` — boolean con default=False
- `api_clients.report_frequency` — integer con default=1
- `api_clients.cramer_particion` — varchar con default='default'
- `api_clients.created_at` — timestamp con server_default=now()
- `api_clients.activo` — boolean con default=True
- `users.created_at` — timestamp con server_default=now()

---

## DECISIÓN 007 — DATABASE_URL dual-ambiente y convenciones de entorno de desarrollo
**Fecha:** 15 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar siempre

### Problema
El mismo `.env` es leído por el backend (dentro de Docker) y por herramientas
del host (Alembic, psql). Pero el host de PostgreSQL es distinto en cada caso:

- Dentro de Docker: `postgres` (nombre del servicio en la red Docker interna)
- Desde el host: `localhost` (puerto 5432 mapeado via `ports: ["5432:5432"]`)

Usar `localhost` en el `.env` rompe el backend. Usar `postgres` en el `.env`
rompe Alembic desde el host. Descubierto durante el smoke test de auth-refactor.

### Decisión

**El `.env` siempre tiene `postgres` como host** — es el valor correcto para el
runtime principal. Nunca cambiar el `.env` a `localhost`.

**Las herramientas desde el host sobreescriben `DATABASE_URL` en la línea de
comando** sin tocar el `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/metis alembic upgrade head
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/metis alembic check
```

El override solo existe en la sesión de terminal. No se commitea.

### Por qué no usar dos archivos .env distintos
Agregar `.env.docker` y `.env.host` introduce fricción: hay que recordar cuál
usar en cada contexto y mantenerlos sincronizados. El override en línea de
comando es más explícito y no requiere mantenimiento adicional.

### Cómo afecta a nuevos colaboradores
Al clonar el repo y seguir `.env.example`, el valor por defecto es `postgres`.
El smoke test del backend dentro de Docker funciona inmediatamente.
Para Alembic desde el host, el override está documentado en `.env.example`,
`architecture.md` y aquí.

---

## DECISIÓN 008 — Estructura del .env y trampas silenciosas de python-dotenv
**Fecha:** 15 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar en todo entorno nuevo

### Contexto
Durante el smoke test de feature/auth-refactor se detectaron tres problemas
en el `.env` de desarrollo que no generaron error explícito pero causaban
comportamiento incorrecto o inesperado:

1. **`JWT_SECRET_KEY` duplicado con primera ocurrencia vacía.**
   Python-dotenv toma la *primera* ocurrencia de cada variable. Si existe una
   línea `JWT_SECRET_KEY=` vacía antes de la línea con valor, el JWT queda
   firmado con string vacío — funciona (vacío == vacío en verificación) pero
   sin ninguna seguridad. El error es completamente silencioso.

2. **`FRONTEND_ORIGIN` ausente.**
   La política CORS del backend depende de esta variable. Sin ella, el backend
   rechaza todas las requests del frontend con error CORS. No hay warning al
   iniciar — solo falla en runtime cuando el frontend hace el primer request.

3. **Credenciales de `DATABASE_URL` sin coincidir con `POSTGRES_USER`/`POSTGRES_PASSWORD`.**
   El `.env.example` original mostraba `metis_user:metis_pass` en `DATABASE_URL`
   pero `POSTGRES_USER=metis` y `POSTGRES_PASSWORD=metis`. El contenedor postgres
   se crea con las variables `POSTGRES_*` — si `DATABASE_URL` usa credenciales
   distintas, el backend arranca sin error pero falla en el primer query con
   `authentication failed for user "metis_user"`.

### Reglas establecidas para el .env

**Regla 1 — Sin variables vacías con valor posterior:**
Toda variable con valor debe tener exactamente una ocurrencia en el `.env`.
Si una variable aparece vacía arriba y con valor abajo, python-dotenv usa el
valor vacío. El `.env.example` no debe tener entradas vacías — o tiene el
placeholder o tiene comentario.

**Regla 2 — `JWT_SECRET_KEY` nunca vacío:**
En desarrollo usar un string largo cualquiera (no importa cuál, importa que
no esté vacío). En producción usar un valor generado con:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Regla 3 — Credenciales de DATABASE_URL == POSTGRES_USER:POSTGRES_PASSWORD:**
Las credenciales en la URL deben coincidir exactamente con las variables
`POSTGRES_USER` y `POSTGRES_PASSWORD`. Son las credenciales que Docker usa
para crear el usuario en PostgreSQL al iniciar el contenedor por primera vez.

**Regla 4 — FRONTEND_ORIGIN siempre presente:**
Requerida para CORS. Su ausencia no genera error al iniciar el servidor —
solo falla en runtime con errores CORS que pueden confundirse con bugs del
frontend. Siempre incluir en el `.env` y en el `.env.example`.

**Regla 5 — Sin duplicados:**
Cada variable una sola vez. Los duplicados que resultan de copiar bloques del
`.env.example` son silenciosos (python-dotenv no advierte) y generan confusión
sobre cuál valor está activo.

### Cómo verificar el .env antes de levantar Docker
```bash
# Detectar duplicados
sort /ruta/.env | grep -v "^#" | grep -v "^$" | cut -d= -f1 | sort | uniq -d

# Verificar que JWT_SECRET_KEY no esté vacío
grep "^JWT_SECRET_KEY=" /ruta/.env

# Verificar que DATABASE_URL use las mismas credenciales que POSTGRES_USER/PASSWORD
grep -E "^(DATABASE_URL|POSTGRES_USER|POSTGRES_PASSWORD)=" /ruta/.env
```

---

## CONVENCIÓN — Usuario de prueba para smoke tests

### Usuario establecido en feature/auth-refactor

```
email:    2200631@ucc.edu.ar
password: test1234
nombre:   Octavio
```

Formato de legajo (7 dígitos + @ucc.edu.ar) — identificable como test, nunca
aparecería como usuario real en producción.

### Por qué documentarlo
Los tokens de verificación quedan en `_pending_tokens` (memoria del proceso)
y el usuario queda en la BD hasta limpieza explícita. Sin documentación, un
segundo smoke test fallaría con `AUTH_EMAIL_ALREADY_REGISTERED` sin saber
por qué.

### Procedimiento de limpieza obligatorio post smoke test

El usuario de psql que acepta el contenedor es el definido por `POSTGRES_USER`
en el `.env` — no `metis_user` genérico. Verificar el valor con
`docker inspect pi-postgres-1 | grep POSTGRES_USER` antes de correr.

```bash
# Con POSTGRES_USER=metis (valor actual del .env de desarrollo):
docker exec pi-postgres-1 bash -c \
  "psql -U metis -d metis -c \"DELETE FROM users WHERE email = '2200631@ucc.edu.ar';\""
```

Verificar:
```bash
docker exec pi-postgres-1 bash -c \
  "psql -U metis -d metis -c \"SELECT email FROM users;\""
```

### Regla general
- Todo usuario creado en BD de desarrollo debe documentarse aquí con su
  procedimiento de limpieza
- Nunca usar emails reales (@ucc.edu.ar con nombre real) en entornos de prueba
- El archivo de cookies `/tmp/metis_smoke_cookies.txt` se destruye al hacer
  POST /logout o al terminar la sesión de terminal

---

## DECISIÓN 011 — Fórmula de Cramer: partición y grados de libertad
**Fecha:** 16 de Junio de 2026
**Estado:** IMPLEMENTADO — verificado numéricamente contra tesis Facundo est_02

### Contexto
Durante los tests de regresión de est_02 (Vado de Río Seco, n=24) se detectaron
dos divergencias en la prueba de Cramer respecto de los resultados del sheet de Facundo.

### Divergencia 1 — Tamaño del subgrupo n_w2

**Comportamiento anterior:** `n_w2 = ceil(n × 0.30)` → para n=24: n_w2=8
→ subgrupo = serie[-8:] → tau_w2=0.67071 (tesis: 0.35206) ✗

**Corrección:** `n_w2 = floor(n × 0.30)` → para n=24: n_w2=7
→ subgrupo = serie[-7:] → tau_w2=0.35206 ✓

n_w1 usa `ceil` (correcto, confirmado con tau_w1=0.18289 ✓).
La asimetría ceil/floor entre n_w1 y n_w2 está confirmada numéricamente.

### Divergencia 2 — Grados de libertad del valor crítico

**Comportamiento anterior:** `ν_w = n + n_w - 2`
→ ν_w1=36 (crit≈2.026), ν_w2=29 (crit≈2.042) — no coincide con sheet

**Corrección:** `ν = n - 2` para ambos subgrupos
→ ν=22 (crit=2.0739) — coincide exactamente con sheet ✓

La tesis escribe "ν = n₁ + n₂ - 2" en p.51, pero los resultados numéricos
del sheet de Facundo (est_02 y est_03) son consistentes con ν = n - 2.
Ante discrepancia texto/práctica, se prioriza la práctica numérica de la
fuente bibliográfica primaria.

PENDIENTE: confirmación formal de Facundo sobre la fórmula de ν.

### Archivos modificados
- `metis/core/homogeneity.py` — calcular_cramer: ceil→floor para n_w2, nu=n-2
- `.claude/rules/formulas-etapa1.md` — sección Cramer actualizada con esta decisión

---

## DECISIÓN 012 — Criterio de aprobación Anderson: comparación entera vs ratio flotante
**Fecha:** 16 de Junio de 2026
**Estado:** IMPLEMENTADO — verificado contra tesis Facundo est_02

### Contexto
Durante los tests de regresión de est_02 (n=24, k_max=8) se detectó que el criterio
`lags_fuera / k_max <= 0.10` rechazaba la prueba de Anderson cuando la tesis la aprueba.

### Comportamiento anterior
```python
aprobada = (lags_fuera / k_max) <= 0.10
```
Con 1 lag fuera de 8: `1/8 = 0.125 > 0.10` → rechazada.
La tesis reporta "Aceptada (1 punto fuera no supera el límite admisible de 1)".

### Corrección
```python
aprobada = lags_fuera <= math.ceil(k_max * 0.10)
```
Con k_max=8: `ceil(8 × 0.10) = ceil(0.8) = 1`. `1 ≤ 1` → aprobada ✓

### Justificación
La tesis compara el conteo absoluto de lags fuera contra un umbral entero,
no contra un ratio flotante. `ceil` garantiza que con k_max=8 el umbral sea 1
(no 0), reproduciendo exactamente el criterio de Facundo.
El ratio flotante era incorrecto para k_max que no son múltiplos de 10.

### Archivos modificados
- `metis/core/independence.py` — `calcular_anderson`: import math agregado, condición corregida

---

## DECISIÓN 013 — Fórmula de asimetría no sesgada: ddof=0 (IV-4/IV-5) en todas las distribuciones
**Fecha:** 17 de Junio de 2026
**Estado:** IMPLEMENTADO — propagado a las 5 distribuciones con _skewness interno

### Contexto
Durante los tests de regresión de est_02 se detectó que `descriptive.py` calcula
g=1.6686 (siguiendo IV-4/IV-5) mientras que gamma3p, gve, logpearson3, lognormal3p
y gen_pareto calculaban g≈1.565 internamente con `_skewness` usando `ddof=1`.

### Raíz del problema
Las funciones `_skewness` locales usaban `np.std(x, ddof=1)` en el denominador.
IV-4 requiere `var_sesgada` con ddof=0:

  g_sesg = mean((xi-xbar)³) / (var_sesgada)^(3/2)   [IV-4, ddof=0]
  g_insesg = n²/((n-1)(n-2)) * g_sesg               [IV-5]

El código anterior usaba `S = std(ddof=1)`, que coincide con SKEW() de Excel y
scipy.stats.skew(bias=False), pero difiere de IV-4/IV-5 por un factor √(n/(n-1))
en el denominador.

### Decisión
METIS sigue IV-4/IV-5 como fuente de verdad bibliográfica.
`descriptive.py` ya implementa correctamente — no se modifica.
Las 5 distribuciones con `_skewness` interno se corrigen a ddof=0.

### Consecuencia en tests de regresión (est_02)
- g METIS = 1.6686 (IV-4/IV-5)
- g tesis Facundo = 1.565 (Excel SKEW(), ddof=1)
- diff = 6.62%
Parámetros afectados por g: Gamma 3p momentos (beta=4/g²), Log-Normal 3p momentos
(w=f(g)), GVE momentos (polinomio en g). Diffs en estos parámetros clasifican como
INFO (no bug) — origen trazable a diferencia de fórmula documentada.
LP3 Indirecto usa gy = asimetría de yi=ln(xi), no de la serie original — también afectada.

### Archivos modificados
- `metis/core/etapa2/distributions/gamma3p.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/gve.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/logpearson3.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/lognormal3p.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/gen_pareto.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)

---

## DECISIÓN 009 — Convención de nombres de distribuciones en el pipeline
**Fecha:** 17 de Mayo de 2026
**Estado:** IMPLEMENTADO

Las claves que identifican distribuciones en `DISABLED_WITH_ZEROS` y
`PENDING_ZEROS_CONFIRMATION` deben coincidir exactamente con los nombres
de módulo en `distributions/` (sin guiones entre palabras, todo minúsculas):
`lognormal2p`, `logpearson3`, `gamma2p`, `exponencial_beta`, etc.

### Bug encontrado durante smoke test de Fase 1
`DISABLED_WITH_ZEROS` usaba `log_normal_2p` con guiones bajos entre palabras,
pero el pipeline usa `lognormal2p`. El lookup `nombre in DISABLED_WITH_ZEROS`
fallaba silenciosamente — las distribuciones afectadas no quedaban deshabilitadas
ante series con ceros. Detectado al verificar el output del smoke test con
`tiene_ceros=True`. Corregido antes de commitear.

### Regla
Cualquier cambio en nombres de módulo de distribuciones requiere verificar
consistencia con estas constantes en `distributions/__init__.py`.

---

## DECISIÓN 010 — Estrategia de root-finding para métodos iterativos
**Fecha:** 19 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar en todas las distribuciones

### Contexto
Durante el smoke test de Gen. Pareto MC (Fase 4 de feature/core-etapa2) se detectó
que `fsolve` reportaba `ier=1` ("solución convergida") con residual=0.007 — sin moverse
del valor inicial ε=0.3. El verdadero root de IV-153 estaba en ε≈0.51.

`fsolve` declara convergencia cuando el **paso de Newton es pequeño**, no cuando el
**residual es pequeño**. Para funciones casi planas cerca del punto inicial puede
reportar convergencia falsa con residual alto. No es un bug de scipy — es el criterio
de convergencia por defecto de MINPACK.

### Estrategia adoptada en METIS

**Para ecuaciones unidimensionales: scan + brentq**

Evaluar la función en N puntos del dominio para detectar cambios de signo,
luego aplicar `brentq` en el intervalo con cambio de signo.
Garantiza residual ≤ CONVERGENCIA = 1e-7.

```python
_scan = np.linspace(lo, hi, N)
_vals = np.array([f(e) for e in _scan])
_idx = np.where(np.diff(np.sign(_vals)) != 0)[0]
eps = float(brentq(f, float(_scan[_idx[0]]), float(_scan[_idx[0]+1]), xtol=CONVERGENCIA))
```

Puede haber múltiples raíces (incluso espurias). En ese caso, iterar sobre todos
los brackets hasta encontrar parámetros que pasen todos los guards de validez.
Ejemplo en `gen_pareto.py` método MC: la ecuación IV-153 tiene una raíz espuria
cerca de ε=0 (produce denom_b≈0) y la raíz válida en ε≈0.51. Se itera hasta
encontrar la primera que da sigma > 0.

**Para sistemas multidimensionales (MV): fsolve con verificación explícita de residual**

`fsolve` es necesario para sistemas (N ecuaciones, N incógnitas). Después de
obtener la solución, verificar el residual explícitamente antes de aceptarla.
Si residual > umbral → STATUS_NO_CONVERGE.

```python
sol, info, ier, _ = fsolve(system, x0, full_output=True)
if ier != 1 or np.max(np.abs(info["fvec"])) > RESIDUAL_UMBRAL:
    return MetodoResult(..., status=STATUS_NO_CONVERGE)
```

### Alcance
Revisar todos los usos de `fsolve` en el codebase y agregar verificación de residual
donde corresponda. Distribuciones afectadas: gen_pareto MV, gen_exponencial MV,
logpearson3 MV, lognormal3p MV, gamma3p MV, gve MV.

---

## RESUELTO — GVE ML: error de orden de serie en IV-243/244
**Fecha:** 19 de Mayo de 2026
**Estado:** IMPLEMENTADO — bug de implementación corregido

No era inconsistencia en la tesis sino error de implementación.
La tesis p.81 especifica explícitamente que la serie debe ordenarse
DE MAYOR A MENOR para IV-243 y IV-244. El código ordenaba de menor
a mayor. Con orden descendente, (2·M̂(1) - M̂(0)) resulta positivo,
C > 0, α̂ > 0.
Fix: `xs = np.sort(serie)[::-1]` en `_momentos_L()`.

Smoke test post-fix (serie_facundo, n=40):
- ml: nu=89.50, alpha=20.61, beta=0.071, Q100=170.44, EEA=46.71 ✓

---

## PENDIENTE — Tabla IV-1: Momentos vs MV en Normal y Log-Normal 2p
**Fecha:** Mayo 2026
**Estado:** PENDIENTE — confirmar con Facundo

Tabla IV-1 de la tesis lista Normal y Log-Normal 2p solo bajo MV, no bajo Momentos.
Pendiente confirmar con Facundo si es porque Momentos y MV coinciden (y por eso
se listan como uno solo) o si Momentos no debe implementarse como método separado.

Actualmente ambas distribuciones tienen `METODOS_APLICABLES = ("momentos", "mv")`
con estimadores idénticos. Si Facundo confirma que deben listarse como un solo
método, eliminar "momentos" del tuple y dejar solo "mv".