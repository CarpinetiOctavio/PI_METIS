# DECISIÓN 001 — Autenticación CU-01
**Fecha:** 10 de Mayo de 2026
**Estado:** RESUELTA — se conserva por trazabilidad y transparencia, no describe el mecanismo vigente. La "Decisión original" de este archivo (Google OAuth) fue evaluada y descartada — ver `docs/historico/oauth-descartado.md` para el flujo tal como se había diseñado. Reemplazada por usuario/contraseña + JWT (HttpOnly Cookie), con verificación de mail real contra el relay SMTP provisto por IT — Parte 1 (login) y Parte 2 (verificación por mail) ambas completas. Mecanismo vigente documentado en `architecture.md`, sección "Autenticación — flujo vigente"; detalle de Parte 2 en [DECISIÓN 004](decision004.md) y [DECISIÓN 034](decision034.md).

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

### Decisión de reemplazo — CONFIRMADA E IMPLEMENTADA
IT confirmó y proveyó las credenciales reales (ver DECISIÓN 004 y DECISIÓN 034
para el detalle de Parte 2). La variante implementada fue OPCIÓN A CON SMTP,
descrita abajo — no el fallback sin SMTP. El texto de esta sección quedó tal
como se escribió en el momento de la propuesta, antes de la confirmación;
se conserva por trazabilidad.

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

### Qué había que hacer cuando IT confirmara — COMPLETADO
Los seis puntos de abajo están hechos (ver DECISIÓN 002 para el detalle
de esquema/refactor de auth/, y DECISIÓN 004/034 para SMTP). Lista
conservada tal cual por trazabilidad, no como pendiente:
1. Eliminar auth/google.py
2. Reescribir auth/router.py con los nuevos endpoints
3. Actualizar auth/dependencies.py — get_current_user y get_optional_user
   no cambian en su contrato, solo en cómo verifican el JWT
4. Actualizar .env.example: eliminar variables de Google, agregar SMTP si aplica
5. Agregar columna password_hash y email_verified a la tabla users en BD
6. Actualizar tests de integración — mock de OAuth reemplazado por mock de login

### Estado actual del código — DESACTUALIZADO, ver nota
Todo lo que sigue en esta sección describe un estado transitorio que ya
no existe. `auth/google.py` fue eliminado (ver [DECISIÓN 002](decision002.md))
y el reemplazo por usuario/contraseña + JWT está completo, incluida la
Parte 2 de verificación por mail real (ver [DECISIÓN 004](decision004.md)
y [DECISIÓN 034](decision034.md)). El flujo de OAuth que describe todo
este archivo está descartado — ver `docs/historico/oauth-descartado.md`
para el diseño original tal como se había planeado, y
`architecture.md`, sección "Autenticación — flujo vigente", para el
mecanismo real hoy.

Texto original de esta sección, conservado por trazabilidad, ya no
refleja la realidad:
> auth/google.py y auth/router.py tienen implementado Google OAuth.
> Ese código está pendiente de reemplazo. No agregar funcionalidad sobre él.
> No usar auth/google.py como referencia para nada nuevo.
> NO tocar auth/ hasta que Octavio confirme la decisión de IT.
