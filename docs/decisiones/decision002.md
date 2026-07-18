# DECISIÓN 002 — Esquema tabla users y refactor de auth/
**Fecha:** 10 de Mayo de 2026
**Estado:** IMPLEMENTADO — password_hash y email_verified agregados a users via migración 002 de Alembic

### Contexto
Consecuencia directa de [DECISIÓN 001](decision001.md). El reemplazo de Google OAuth por
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
