# Integración externa: envío de mail de verificación (SMTP)

TP integrador de Calidad de Software, bloque B4 (`docs/plan-tp-calidad-software.md`). Decisiones: DECISIÓN 004
(mecanismo de envío), DECISIÓN 032 (mail antes del commit), DECISIÓN 034 (identidad vs. remitente), DECISIÓN 049
(Mailpit y `SMTP_STARTTLS`).

## 1. Qué es la integración

El registro de CU-01 (`POST /api/v1/auth/register`) manda un mail con un link de verificación antes de confirmar
el alta en la base. Sin ese mail, la cuenta nunca se puede verificar y el docente no puede iniciar sesión. Es la
única dependencia externa de METIS en tiempo de ejecución, además de PostgreSQL.

## 2. Contrato

| Elemento | Valor |
|---|---|
| Cliente | `aiosmtplib.send()` en `backend/metis/auth/email.py::send_verification_email` |
| Servidor | `SMTP_HOST`:`SMTP_PORT` (producción: relay institucional; hoy `smtp.gmail.com:587`) |
| Autenticación | `SMTP_USER` / `SMTP_PASSWORD` (identidad del relay, no el remitente — DECISIÓN 034) |
| Remitente | `SMTP_FROM_ADDRESS` |
| Cifrado | STARTTLS si `SMTP_STARTTLS` no es `false`/`0`/`no` (default: activo) |
| Mensaje | Asunto "METIS — Verificá tu cuenta"; cuerpo de texto con `{FRONTEND_URL}/auth/verify?token=<token>` |
| Token | `secrets.token_urlsafe(32)`, un solo uso, guardado en memoria del proceso (`auth/router.py::_pending_tokens`) |

**Errores.** Si faltan las variables obligatorias, `send_verification_email` levanta `RuntimeError`; si el servidor
rechaza o no responde, `aiosmtplib.SMTPException`. En los dos casos el registro responde **500
`AUTH_VERIFICATION_EMAIL_FAILED`** y **no persiste el usuario** (DECISIÓN 032): el docente puede reintentar sin quedar
con una cuenta huérfana sin verificar.

## 3. Cómo se prueba, por nivel

| Nivel | Qué | Dónde | Doble o real |
|---|---|---|---|
| Unidad | Parámetros de `aiosmtplib.send`, armado del mensaje, validación de variables, `SMTP_STARTTLS` | `tests/unit/auth/test_email.py` | Doble (`AsyncMock` sobre `aiosmtplib.send`) |
| Unidad | Orquestación del registro: mail antes del commit, falla de SMTP → 500 sin persistir, email repetido | `tests/unit/auth/test_router_register.py` | Doble (`send_verification_email` y sesión de BD) |
| Integración | Registro → mail → verificación → login, de punta a punta | `tests/integration/db/test_registro_mailpit.py` | **Real**: Mailpit + PostgreSQL |
| E2E | El mismo flujo desde el navegador (E2E-0) | `frontend/e2e/` (bloque B6) | **Real**: Mailpit + despliegue completo |

**Por qué dobles en unidad.** Lo que se prueba ahí es la lógica propia (qué se manda, en qué orden, qué pasa ante
una falla); un servidor real haría el test lento y no aportaría nada a esa pregunta. **Por qué Mailpit en
integración.** Es un servidor SMTP real: habla el protocolo, exige el handshake y la autenticación, y guarda el
mensaje. Un error en el armado del mensaje o en la llamada a `aiosmtplib` que los dobles no ven, acá falla. Corre en
cada ejecución del pipeline (job `test`, servicio `mailpit`) con `METIS_REQUIRE_MAILPIT=1`: si Mailpit no está, el
test falla en vez de saltearse.

## 4. Qué queda para el despliegue en la UCC

Gmail o el relay institucional no se prueban en este TP: la red de la UCC (firewall, TLS, autenticación del relay)
no se puede reproducir en GitHub Actions, y poner credenciales reales en los secrets del repo es un riesgo sin
beneficio para la materia. Se verifica cuando METIS se despliegue en los servidores de la UCC, como parte de la
defensa de la tesis. Antecedente: el envío real ya se probó a mano contra el relay de la UCC el 20/07/2026
(`docs/sprint.md`).

## 5. Plan de contingencia: SMTP caído

| Síntoma | Detección | Respuesta |
|---|---|---|
| El relay no responde o rechaza | El registro devuelve 500 `AUTH_VERIFICATION_EMAIL_FAILED`; el log del backend registra la excepción con el destinatario (`logger.exception`) | El usuario ve el mensaje traducido ("No pudimos enviar el mail de verificación…") y puede reintentar: no queda nada persistido |
| Caída prolongada | Varios 500 seguidos del mismo código en el log | Bypass operativo: `scripts/seed-dev-user.sh <email>` crea el usuario ya verificado directo en la base; el docente entra sin esperar el mail |
| Credenciales vencidas (App Password revocado) | `SMTPAuthenticationError` en el log | Pedir a IT un App Password nuevo y actualizar `SMTP_PASSWORD` en el `.env`; no requiere redeploy de código |
| Tokens perdidos por reinicio del backend | El usuario recibe `AUTH_INVALID_TOKEN` con un link que antes servía | Limitación conocida (`_pending_tokens` en memoria, `auth/router.py`): reintentar el registro; mover los tokens a la base queda como mejora post-V1.0 |

Lo que **no** se hace ante una caída: no se desactiva la verificación ni se agrega una rama "sin mail" al registro.
Esa alternativa se descartó en DECISIÓN 049 porque toca el camino crítico de autenticación.
