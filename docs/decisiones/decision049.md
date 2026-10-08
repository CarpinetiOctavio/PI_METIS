# DECISIÓN 049: Mailpit como servidor SMTP de captura en desarrollo, E2E y CI; sin escotilla en `auth/email.py`

**Fecha:** 8 de octubre de 2026
**Estado:** Decidida — implementación en el Bloque B4 de `docs/plan-tp-calidad-software.md`.
**Decide:** Kevin.
**Origen:** número reservado para la "escotilla SMTP de desarrollo en `auth/email.py`"
(`docs/historico/planes/frontend/plan-arreglo-ui-rota.md` §1.3(b), reasignado de 045 a 049 el 05/08/2026). Se
escribe ahora porque el TP integrador de Calidad de Software exige probar la integración externa con un flujo E2E
automatizado en cada despliegue, y el registro de CU-01 depende de un mail.

### Contexto

`auth/router.py::register` manda el mail de verificación antes de confirmar el alta (DECISIÓN 032). `auth/email.py`
llama a `aiosmtplib.send(...)` con `start_tls=True` fijo y exige `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` y
`SMTP_FROM_ADDRESS`. En desarrollo no hay un SMTP real disponible, así que el registro responde 500
`AUTH_VERIFICATION_EMAIL_FAILED` y la única forma de tener un usuario es `scripts/seed-dev-user.sh`, que lo inserta ya
verificado directo en Postgres. Resultado: el camino registro → mail → verificación solo se prueba con dobles
(`AsyncMock` sobre `aiosmtplib.send` en `test_email.py` y `test_router_register.py`) y contra el relay de la UCC a
mano (smoke del 20/07/2026).

### Decisión

1. **Mailpit** (sucesor mantenido de MailHog, imagen con versión fija) se suma como servicio en los compose de
   desarrollo, E2E y CI. Es un servidor SMTP real: habla el protocolo, recibe y guarda el mail, y expone una API HTTP
   (`/api/v1/search`, `/api/v1/message/{ID}`) para que un test lea el mensaje y extraiga el link de verificación.
2. **Un solo cambio de código:** `SMTP_STARTTLS` configurable por variable de entorno en `auth/email.py`, con default
   `true`. Producción no cambia. En los compose con Mailpit va en `false` (Mailpit sin TLS rechaza STARTTLS). Con su
   test.
3. Configuración de los compose con Mailpit: `SMTP_HOST=mailpit`, `SMTP_PORT=1025`, `SMTP_STARTTLS=false`,
   credenciales de relleno (el código las exige aunque Mailpit no autentique; Mailpit con
   `MP_SMTP_AUTH_ACCEPT_ANY=1` y `MP_SMTP_AUTH_ALLOW_INSECURE=1`) y `FRONTEND_URL` apuntando a nginx
   (`http://localhost`), para que el link del mail no lleve al servidor de Vite.
4. **Gmail real / relay de la UCC** queda para el despliegue en los servidores de la UCC, que es parte de la defensa
   de la tesis y no del TP. Se declara como trabajo posterior.

### Alternativas evaluadas

- **Escotilla por `ENV` en `auth/email.py`** (si no es producción y faltan credenciales, loguear el token y devolver
  éxito). Descartada: mete una rama `if dev` en el camino crítico de autenticación que DECISIÓN 032 ordenó con
  cuidado, y no ejercita el envío real: un error en el armado del mensaje o en la llamada a `aiosmtplib` pasaría
  igual.
- **Quedarse solo con `seed-dev-user.sh`.** Descartada como única vía: sirve para tener un usuario, pero no prueba el
  registro ni el mail. Se mantiene como bypass operativo (plan de contingencia ante SMTP caído).
- **MailHog.** Descartada a favor de Mailpit: MailHog no tiene mantenimiento activo; Mailpit es su reemplazo directo,
  con la misma idea y API documentada.
- **Una cuenta de Gmail de prueba desde CI.** Descartada para el TP: credenciales reales en secrets del repo, límites
  de envío, y la red de la UCC (donde va a correr METIS) es justamente la que no se puede reproducir en GitHub
  Actions.

### Consecuencias

- El flujo registro → mail → verificación → login se prueba contra un SMTP real en cada despliegue (E2E-0 de
  DECISIÓN 046 y un test de integración).
- `.env.example` documenta `SMTP_STARTTLS` y los valores para Mailpit.
- El riesgo que queda abierto es el del relay real (TLS, autenticación, firewall de la UCC): se registra en la matriz
  de riesgos del TP y se verifica en el despliegue de la UCC.
