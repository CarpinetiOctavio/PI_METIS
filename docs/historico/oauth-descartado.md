# Flujo de autenticación OAuth — descartado

**Movido desde `architecture.md` el 17 de Julio de 2026.** Este documento
describe el flujo de Google OAuth tal como se había diseñado originalmente,
antes de ser descartado por `DECISIÓN 001` en
`docs/decisiones/decision001.md`. Se conserva por trazabilidad —
muestra qué se evaluó y por qué se lo reemplazó — no representa el
comportamiento vigente del sistema. El flujo real hoy es usuario/contraseña
+ JWT, documentado en `architecture.md`, sección "Autenticación — flujo
vigente".

## Flujo original evaluado

1. Frontend → GET /api/v1/auth/google
2. Backend redirige a accounts.google.com/oauth2/auth con scope=email
3. Google autentica al usuario
4. Google → GET /api/v1/auth/callback?code=XXX (llega al BACKEND, no al frontend)
5. Backend intercambia code por token con Google
6. Backend verifica que email termine en @ucc.edu.ar → 403 si no cumple
7. Backend genera JWT propio (NO usa el token de Google directamente)
8. Backend setea JWT en HttpOnly Cookie con SameSite=Lax, Secure=True
9. Backend redirige al frontend — el frontend NUNCA ve el JWT

**Motivo del descarte:** el servidor corre en la intranet de la UCC, sin
salida pública — el callback entrante de Google (paso 4) no puede
completarse contra un servidor sin acceso desde el exterior. Ver
`DECISIÓN 001` para el detalle completo.

**Variables de entorno que hubiera requerido (no usadas hoy):**
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://dominio-ucc/api/v1/auth/callback
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=60
DATABASE_URL=postgresql://user:pass@postgres:5432/metis