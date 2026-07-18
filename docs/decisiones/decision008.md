# DECISIÓN 008 — Estructura del .env y trampas silenciosas de python-dotenv
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
