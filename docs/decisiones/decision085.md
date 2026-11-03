# DECISIÓN 085: recuperación de contraseña por mail, con token de un solo uso guardado como hash

**Fecha:** 2 de noviembre de 2026
**Estado:** Decidida y aplicada (backend + frontend + migración 007).
**Decide:** Kevin, a partir de la prueba en el servidor de la UCC del 2/11/2026.
**Depende de:** DECISIÓN 004 (mecanismo de envío de mail), DECISIÓN 034 (verificación de cuenta y su límite H8),
DECISIÓN 049 (Mailpit en CI).

### Problema

METIS no tenía ninguna forma de recuperar una contraseña olvidada. Se detectó probando la aplicación desplegada en
la UCC: quien la olvida o escribe mal el mail al registrarse queda sin acceso y solo puede volver a entrar creando
otra cuenta con otro mail, o pidiendo que alguien edite la base. Es un faltante de un sistema con cuentas, y es
probable que lo pidan tanto el informe del proyecto integrador como su presentación.

Además, el registro tenía un límite ya documentado (H8, DECISIÓN 034): el token de verificación vive en memoria del
proceso, así que un reinicio del backend antes de que el usuario abra su mail deja la cuenta sin verificar y sin
forma de verificarla.

### La decisión

1. **Dos endpoints públicos** (contrato en `.claude/rules/architecture/api-contracts.md`):
   - `POST /api/v1/auth/forgot-password` recibe `{email}`. Responde siempre `200` con el mismo mensaje, exista o no
     la cuenta, para que no sirva para averiguar qué mails están registrados. El envío del mail corre en segundo
     plano y un fallo solo se registra en el log: si saliera como error, la respuesta dejaría de ser idéntica.
   - `POST /api/v1/auth/reset-password` recibe `{token, password}`. Cambia la contraseña (mismo mínimo de 8
     caracteres que el registro) o responde `400 AUTH_RESET_TOKEN_INVALID` si el token no existe, venció o ya se usó.
2. **Tabla `auth_tokens`** (migración 007): `user_id` con `ON DELETE CASCADE`, `purpose`, `token_hash`, `expires_at`,
   `used_at`, `created_at`. La base guarda el **SHA-256** del token, nunca el valor que viaja en el mail: quien lea
   la base no puede armar un link válido. El campo `purpose` deja la tabla lista para mover después el token de
   verificación del registro, que hoy sigue en memoria.
3. **Un solo uso, resuelto por la base.** El consumo es un único `UPDATE ... WHERE used_at IS NULL AND expires_at >
   ahora ... RETURNING user_id`. Si el mismo link se usa dos veces a la vez, solo una de las dos transacciones
   encuentra la fila libre.
4. **Vigencia de 1 hora** (`RESET_TOKEN_TTL_MINUTES`) y **solo vale el último link**: pedir uno nuevo invalida los
   anteriores todavía vivos. Al restablecer la contraseña también se invalidan los restantes.
5. **Enfriamiento de 60 segundos por cuenta** (`RESET_COOLDOWN_SECONDS`). Dentro de ese lapso no se genera un token
   nuevo ni se manda otro mail, y la respuesta es la misma. Evita usar el endpoint, que no pide sesión, para llenar
   una casilla ajena o agotar el cupo del relay SMTP de la UCC.
6. **Restablecer la contraseña marca la cuenta como verificada.** Abrir el link prueba que la persona controla la
   casilla, que es lo mismo que prueba el link de registro. Con esto la recuperación también destraba las cuentas
   afectadas por H8, sin tocar el mecanismo de verificación.
7. **Frontend:** link "¿Olvidaste tu contraseña?" en el formulario de login y dos pantallas, `/auth/forgot-password`
   (pide el mail) y `/auth/reset-password?token=...` (contraseña nueva con confirmación). Validan largo y
   coincidencia antes de llamar al backend; `AUTH_RESET_TOKEN_INVALID` se traduce en `errors.es.ts`.

### Alternativas descartadas

- **Token firmado sin estado (JWT de reseteo).** No necesita tabla, pero no se puede invalidar ni limitar a un uso
  sin guardar algo en la base, que es justo lo que pide el requisito de un solo uso.
- **Mover también el token de verificación a `auth_tokens` en este cambio.** Resolvería H8 de raíz, pero cambia el
  camino de registro, que ya está probado de punta a punta (E2E-0), y agranda este PR. La tabla queda preparada;
  la mudanza puede hacerse aparte.
- **Responder `404` cuando la cuenta no existe.** Más cómodo para quien se equivoca de mail, pero convierte el
  endpoint en una consulta de qué personas usan METIS.
- **Pedir un código de verificación adicional o una pregunta secreta.** Sin un segundo canal confiable (la
  institución solo ofrece el mail), no agrega seguridad real y complica el uso.

### Verificación

- Unitarios de `metis.auth` (tokens, endpoints, armado del mail): 76 pasan en Python 3.11.
- Integración contra PostgreSQL real (`tests/integration/db/test_recuperacion_contrasena.py`, 9 tests): respuesta
  idéntica con y sin cuenta, un solo token en el enfriamiento, un pedido nuevo invalida el link anterior, token
  vencido, inexistente y reutilizado, contraseña corta sin gastar el token, cuenta sin verificar que queda
  verificada, borrado en cascada y el flujo completo con mail real. Este último y el de registro necesitan
  Mailpit: se saltean sin `MAILPIT_URL` y corren en CI (`METIS_REQUIRE_MAILPIT=1`). Corrida local de
  `tests/integration/db`: 30 pasan, 2 se saltean por Mailpit.
- Frontend: 599 tests de vitest, `tsc -b` y `eslint` sin errores; `scripts/check-error-catalog.sh` confirma que el
  catálogo, el backend y el diccionario del frontend coinciden.
- E2E-6 (`frontend/e2e/e2e6-recuperacion.spec.ts`): registro sin verificar, pedido desde el login, mail en Mailpit,
  contraseña nueva, link reutilizado rechazado y login con la nueva; la vieja deja de servir. Escrito y chequeado de
  tipos y de estilo, pero **no ejecutado localmente** (requiere Docker y Mailpit): su primera corrida es la del job
  `despliegue` de CI.

### Consecuencias y límites conocidos

- **Las sesiones ya iniciadas no se cierran.** El JWT emitido antes del cambio sigue siendo válido hasta que vence
  (`JWT_EXPIRE_MINUTES`, 60 por defecto). Quien sospeche que le robaron la cuenta cambia la contraseña, pero el
  atacante con una sesión abierta conserva el acceso hasta una hora. Cerrar sesiones exigiría guardar una versión
  de sesión por usuario; queda fuera de V1.0.
- **El enfriamiento es por cuenta, no por origen.** No frena a alguien que pida links para muchas cuentas distintas.
  El complemento natural es un `limit_req` de nginx sobre `/api/v1/auth/`, a agregar sobre la configuración del PR de
  endurecimiento de nginx.
- **Diferencia de tiempo mínima entre cuenta existente e inexistente.** Si la cuenta existe, el endpoint hace un
  `INSERT` y un `COMMIT` más antes de responder. La respuesta es idéntica en contenido; la diferencia de tiempo es de
  milisegundos y no se trata en V1.0.
- **El token viaja en la URL de la pantalla** (`/auth/reset-password?token=...`), así que queda en el log de acceso
  de nginx al cargar esa página, igual que ya ocurre con el link de verificación. Lo acotan el uso único y la hora
  de vigencia; la llamada a la API lleva el token en el cuerpo del `POST`, no en la URL.
- **Depende del relay SMTP.** Si el relay está caído, el usuario recibe el mismo mensaje de éxito y no le llega
  nada. El log del backend registra el fallo (`Fallo al enviar mail de recuperación`); la respuesta operativa es la
  de `integracion-smtp.md` §5.
- Variables nuevas, ambas opcionales: `RESET_TOKEN_TTL_MINUTES` y `RESET_COOLDOWN_SECONDS` (en `.env.example`).
  El despliegue exige correr `alembic upgrade head` (migración 007) antes de levantar la versión nueva del backend.
