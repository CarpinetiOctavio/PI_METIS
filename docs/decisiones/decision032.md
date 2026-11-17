# DECISIÓN 032 — Auth: orden mail-antes-que-commit en `register`, ventana residual aceptada
**Fecha:** 19 de Julio de 2026
**Estado:** IMPLEMENTADO — pendiente de verificación exhaustiva por test (10/10 tests de auth en verde; la rama de `IntegrityError` y el guard de configuración de `email.py` corren en la suite pero no fueron forzados contra una falla de red real, sólo mockeada)

### Contexto
[DECISIÓN 004](decision004.md) resolvió qué mecanismo usar para enviar el mail de verificación (App Password + `aiosmtplib`). Al implementar el manejo de errores del envío real — que el mock nunca necesitó, porque nunca fallaba — apareció un problema de fondo, distinto al de 004: con el orden original del código (`commit()` del usuario antes de intentar el envío del mail), un fallo de SMTP dejaba un usuario comiteado en base, con `email_verified=False`, sin ninguna vía de reenvío del token. No podía re-registrarse (el email ya existía), no podía loguearse (no verificado), y no había endpoint de reenvío — "usuario huérfano".

### Precisión conceptual — no es atomicidad ACID
El envío de mail via SMTP es un sistema externo, sin transacción compartida con Postgres. No existe forma de que el envío y el `commit()` sean una sola operación atómica — eso lo resolvería un patrón outbox/saga completo, que no se implementa acá porque el volumen y contexto (intranet, cuenta institucional de bajo tráfico) no lo justifican. Lo que se hizo es acotar la ventana de falla, no eliminarla.

### Opciones evaluadas
**Endpoint de reenvío** (`/resend-verification`), manteniendo el orden original: descartado. Requiere endpoint nuevo, schema nuevo, y reestructurar `_pending_tokens` (hoy indexado solo por token, no por email) para cubrir un modo de falla de baja probabilidad dado el contexto.

**Reordenar** — mandar el mail antes de tocar la sesión de BD, comitear solo si el envío tiene éxito: elegida. No requiere endpoint nuevo. Acota la ventana de falla a un caso más raro: que el mail salga bien pero el `commit()` falle después, dejando un token sin usuario asociado. Ese caso es auto-resuelto: el link da `AUTH_INVALID_TOKEN`, no rompe nada, el usuario puede re-registrarse limpio.

### Efecto secundario identificado, aceptado conscientemente
Con el orden nuevo, dos registros concurrentes con el mismo email disparan ambos el envío de mail antes de que ninguno comitee (antes, el que perdía la carrera crasheaba en el `commit()` sin llegar a mandar mail). Evaluadas dos mitigaciones:
- Lock de aplicación (`asyncio.Lock` por email, en memoria) — descartado. Mismo espíritu que la limitación ya aceptada en DECISIÓN 005 (`_pending_tokens` en memoria de proceso); no aporta nada nuevo para el volumen actual.
- Advisory lock de Postgres (`pg_advisory_xact_lock`) — descartado. Resuelve un problema (multi-worker) que no existe todavía en V1.0, a costa de sostener el lock durante una llamada de red externa, con riesgo real si el manejo de excepción para liberarlo no queda prolijo.

Riesgo residual aceptado: en esa race (baja probabilidad), el usuario puede recibir un mail de verificación duplicado. No compromete integridad de datos ni seguridad — el `unique constraint` de `User.email` sigue cerrando la consistencia de fondo vía `IntegrityError` capturado (ver abajo).

### Implementación
- `User(...)` construido en memoria, sin `db.add()` hasta confirmar envío exitoso de `send_verification_email`.
- `_pending_tokens[token]` registrado solo después de `commit()` exitoso — evita un token vivo apuntando a un usuario no persistido si el commit falla después de un envío exitoso.
- `IntegrityError` en `commit()` capturado, con `rollback()`, mapeado al mismo `AUTH_EMAIL_ALREADY_REGISTERED` que ya usa el chequeo previo por `SELECT`.
- Excepción real logeada con `logger.exception()` antes de levantar el `HTTPException` genérico — primer uso de `logging` en el repo. Confirmado sin configuración previa que lo suprima (el precedente de supresión en `sprint.md` era específico de `logger.info()` bajo el nivel default `WARNING`; `logging.exception()` loguea a `ERROR`, por encima de ese umbral).
- Mensaje de error corregido: ya no dice "la cuenta se creó pero..." (falso con el nuevo orden) — pasa a "no pudimos enviar el mail de verificación, intentá registrarte de nuevo en unos minutos."

### Precedente de testing establecido
Primeros tests de todo el repo que mockean I/O externa (`unittest.mock` + `AsyncMock`, sin dependencias nuevas). Principio aplicado: mockear en el borde de la unidad bajo test — los tests de `email.py` mockean `aiosmtplib.send`; los tests de `register` en `router.py` mockean `send_verification_email` directamente, sin bajar un nivel más. Queda como precedente general del proyecto para cualquier parte futura que necesite mockear I/O externa, no acotado a auth.

**Ver también:** [DECISIÓN 004](decision004.md) — mecanismo de envío de mail. [DECISIÓN 005](decision005.md) — `_pending_tokens` en memoria, limitación aceptada para V1.0.


#### -------------- Actualización ---------------

### Actualización 20 de Julio de 2026 — verificación exhaustiva completada con relay real
Smoke test manual completo contra el relay real (no mockeado), confirmando ambas ramas:

**Camino A — envío exitoso:** `POST /register` real → mail real recibido en casilla `@ucc.edu.ar` confirmada → token real extraído del mail → `POST /verify` (200) → `POST /login` (200, cookie) → `GET /me` (200, `email_verified: true`) → limpieza. Ciclo completo verificado de punta a punta.

**Camino B — falla real de conexión:** un bug de formato en `.env` (línea con `#` sin espacio, ver DECISIÓN 008) causó que `SMTP_HOST` resolviera a un string inválido, generando un `aiosmtplib.errors.SMTPConnectError` real — no simulado. El `except (aiosmtplib.SMTPException, RuntimeError)` lo capturó correctamente, `logger.exception()` logueó la excepción real, y el endpoint devolvió `500 AUTH_VERIFICATION_EMAIL_FAILED` sin dejar ningún usuario huérfano en la base.

Dos bugs adicionales de configuración SMTP encontrados y corregidos durante esta ronda — documentados en [DECISIÓN 034](decision034.md): hostname (`wally.ucc.edu.ar` vs. el CN real del certificado, `wally.uccor.edu.ar`) y separación de `SMTP_FROM_ADDRESS`/`SMTP_USER`.

Cobertura de test también actualizada tras esta ronda: 12/12 (ver DECISIÓN 034, sección "Resuelto").

Estado pasa de "pendiente de verificación exhaustiva por test" a "IMPLEMENTADO Y VERIFICADO — ambas ramas confirmadas contra relay real."