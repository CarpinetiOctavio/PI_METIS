# Plan de contingencia ante la caída de una dependencia crítica

TP integrador de Calidad de Software, bloque B9. Qué pasa con METIS cuando falla algo de lo que depende, cómo se
detecta y qué se hace. El SMTP tiene su propio plan, más detallado, en `integracion-smtp.md` §5; acá se resume.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión. El comportamiento ante la base caída se verificó ese día (§2) |

## 1. Dependencias y qué arrastra cada una

| Dependencia | Si cae, qué deja de andar | Qué sigue andando |
|---|---|---|
| PostgreSQL | CU-01 entero: login, historial, persistencia, PDF | CU-02 completo (Etapa 1 y 2, simulación de exclusión) |
| Migraciones sin aplicar | Lo mismo que si cae PostgreSQL | Lo mismo |
| SMTP (relay de la UCC) | El registro de usuarios nuevos | Todo lo demás, incluido el login de usuarios ya verificados |
| Proceso del backend (reinicio) | Los streams en curso y sus pausas; los tokens de verificación pendientes | Lo persistido |
| GitHub Actions | El pipeline: no hay forma de verificar un PR | La aplicación desplegada |
| SonarCloud | El análisis consultivo del PR | El pipeline (el gate propio no depende de Sonar) |
| Registries (Docker Hub, PyPI, npm) | El build de imágenes y la instalación de dependencias en CI | Un despliegue ya hecho |

## 2. PostgreSQL caído o sin migrar

**Verificado el 09/10/2026** en el entorno de desarrollo, con el contenedor de PostgreSQL detenido:

| Pedido | Respuesta |
|---|---|
| `GET /ping` | 200 `{"status": "ok"}`: **no detecta la caída** |
| `POST /analysis/preview-columns` (anónimo) | 200, normal |
| `POST /analysis/stream` (anónimo, `etapas=1`) | 200, stream completo hasta `complete` |
| `POST /auth/login` | 500 `Internal Server Error` en texto plano, sin la estructura `{"error": {...}}` |

Al volver a levantar el contenedor, el login siguió en 500, pero por otra causa: la base de desarrollo no tenía
ninguna tabla (`relation "users" does not exist`; `alembic current` sin revisión). Es el mismo síntoma que el
05/08/2026 con `/history/` (`CLAUDE.md`, sección de migraciones).

| Síntoma | Detección | Respuesta |
|---|---|---|
| Login o historial responden 500 | Log del backend: un error de conexión de asyncpg (base caída) o `UndefinedTableError`/`UndefinedColumnError` (sin migrar) | Base caída: `docker-compose up -d postgres` y comprobar con `docker exec <postgres> pg_isready`. Sin migrar: `docker exec <backend> alembic upgrade head` |
| El usuario no puede entrar a su cuenta | El frontend muestra el texto genérico, porque el 500 no trae código del catálogo | Mientras dura: CU-02 sigue disponible para analizar sin guardar. Comunicarlo a los usuarios |
| Datos perdidos | El volumen `postgres_data` se borró | Sin backup automático en V1.0. Para producción en la UCC: volcado periódico con `pg_dump` (pendiente de definir con IT) |

**Prevención.** En CI y en el despliegue local la base nunca queda sin migrar: `deploy-local.sh` corre
`alembic upgrade head` siempre, y el smoke prueba el login y el historial contra la base. **Mejora pendiente:** que
`/ping` haga un `SELECT 1`, para que un monitor o el smoke detecten la caída antes que el primer usuario, y que el
manejador global devuelva un error con código (por ejemplo, `DB_UNAVAILABLE`) en lugar del 500 en texto plano.
Ninguna de las dos está implementada; quedan como riesgo R-04 en `riesgos.md`.

## 3. SMTP caído

Resumen de `integracion-smtp.md` §5. El registro responde 500 `AUTH_VERIFICATION_EMAIL_FAILED`, el usuario ve el
mensaje traducido y puede reintentar (no queda nada persistido). Si la caída se prolonga, `scripts/seed-dev-user.sh`
crea el usuario ya verificado directo en la base. Con credenciales vencidas, se pide a IT un App Password nuevo y se
actualiza el `.env`, sin redeploy de código. **No se desactiva la verificación** ni se agrega una rama "sin mail":
toca el camino crítico de autenticación (DECISIÓN 049).

## 4. Reinicio del backend

| Qué se pierde | Cómo lo ve el usuario | Respuesta |
|---|---|---|
| Streams en curso y sus pausas (`session_store` en memoria, DECISIÓN 053) | El stream se corta: el frontend muestra `STREAM_CLOSED_EARLY` o `STREAM_CONNECTION_ERROR`. Una elección de distribución enviada después responde 404 `SESSION_NOT_FOUND` (`outlier-decision` no valida la sesión: responde 200 sin efecto) | Volver a correr el análisis. En CU-01 no queda un análisis a medias: se persiste al terminar |
| Tokens de verificación pendientes (`_pending_tokens`) | `AUTH_INVALID_TOKEN` con un link que antes servía | Repetir el registro |

Para minimizarlo, reiniciar en un horario sin uso. Con `--reload` (solo desarrollo) cada cambio de código reinicia el
proceso: no usar el compose de desarrollo como producción (`architecture.md`).

## 5. Herramientas del pipeline

| Si cae | Qué se hace | Qué no se hace |
|---|---|---|
| GitHub Actions | Se espera. Para avanzar en local: `scripts/test.sh all` corre lo mismo que el pipeline (`backend`, `frontend`, `duplicacion`, `gate`, `smoke`, `e2e`) | **No se mergea sin el pipeline en verde**, aunque las corridas locales pasen: el ruleset lo bloquea y los números del informe salen del pipeline |
| SonarCloud | Se mergea igual si los siete jobs propios pasan: Sonar es consultivo hasta B13. Se revisa el análisis cuando vuelve | — |
| Docker Hub, PyPI o npm | Reintentar el job | No se fijan imágenes o paquetes "de cualquier origen" para salir del paso |
| Mailpit en CI | El job `test` falla (`METIS_REQUIRE_MAILPIT=1`), no saltea los tests: se reintenta | No se quita la variable para que pase |

## 6. Revisión

Se revisa este plan cuando aparece una dependencia nueva (por ejemplo, el despliegue en la UCC traerá su propia red,
su registry y su relay SMTP) o cuando una caída real muestra un comportamiento que no está acá.
