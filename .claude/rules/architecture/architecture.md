# Decisiones de Arquitectura — METIS

**Última actualización: 29 de Julio de 2026.** Corregida la sección "Nginx como reverse proxy" — afirmaba que el frontend "entra en operación recién en la primera instancia de avance del proyecto (mediados de agosto de 2026)", falso desde el commit `2afcc5d` (Fase 1 del frontend, 28/07/2026). El frontend ya está integrado contra el backend real; lo que sigue sin existir es el build estático servido por nginx, que es otra cosa. Detectado en la pasada 2 de mejora del frontend (`docs/frontend/plan-mejora-frontend-pasada2.md`), corregido en la pasada 3 — `architecture.md` está en la lista de lectura obligatoria de `CLAUDE.md` al inicio de cada sesión, así que una afirmación falsa acá se propaga a cada sesión nueva.

Actualización anterior — 17 de Julio de 2026: se agregó la justificación de nginx, se corrigió la duplicación de `backend:` en el YAML de Docker Compose, se movió el flujo de OAuth descartado a `docs/historico/oauth-descartado.md` (reemplazado por "Autenticación — flujo vigente"), se sumó `auth/` a la restricción de aislamiento de `core/`, y se incorporó acá la sección "Separación de responsabilidades — flujo de datos" (antes en `core-implementation.md`).

## Por qué estas decisiones existen (no cambiar sin justificación explícita)

### FastAPI sobre Flask
FastAPI genera documentación OpenAPI automáticamente — Carlos (CU-03) necesita esa documentación para integrar su sistema externo. La validación automática con Pydantic cubre el contrato complejo de CU-03 (serie, client_id, tipo_variable, columnas X/Y) sin código adicional. Flask requeriría implementar todo eso manualmente.

### PostgreSQL sobre SQLite
CU-01 puede tener múltiples docentes ejecutando análisis simultáneamente. SQLite tiene limitaciones de concurrencia de escritura. PostgreSQL soporta concurrencia real. Además, JSONB de PostgreSQL es necesario para almacenar los resultados heterogéneos de Etapa 2.

### JSONB para resultados estadísticos
Los resultados de Etapa 2 tienen estructura heterogénea — los parámetros de Gumbel son distintos a GVE, Log-Normal 3p, etc. Los resultados siempre se acceden como bloque completo, nunca por campo individual. Normalizar en tablas relacionales agregaría complejidad sin beneficio de consulta.

### SSE sobre WebSockets para el stream del pipeline
El pipeline es unidireccional — el servidor emite progreso, el cliente escucha. SSE es nativo en el navegador y FastAPI lo soporta con StreamingResponse. WebSockets agregaría complejidad bidireccional que no está justificada. Los dos únicos puntos de interacción del usuario (decisión ante atípico de Chow, selección de distribución) se resuelven con requests sincrónicos separados, no con WebSockets.

### HttpOnly Cookie para JWT
Protege contra ataques XSS. Si el JWT estuviera en localStorage, un script malicioso inyectado podría leerlo. HttpOnly Cookie es inaccesible desde JavaScript — el navegador la envía automáticamente en cada request pero ningún código puede leerla.

### Mismo endpoint /analysis/stream para CU-01 y CU-02
CU-01 y CU-02 ejecutan exactamente el mismo pipeline estadístico. La diferencia es la presencia de JWT: con JWT el análisis se persiste y habilita exportación; sin JWT la sesión es efímera. Dos endpoints separados duplicarían código que ejecuta el mismo pipeline.

### core/ completamente aislado
El motor estadístico en core/ no importa nada de api/, services/, db/ ni auth/. Esto hace posible los tests de regresión matemática — se puede testear que Anderson calcula correctamente el estadístico sin levantar la aplicación completa. Es el argumento técnico más sólido ante el tribunal de ISI.

### Nginx como reverse proxy
Único servicio expuesto al exterior — FastAPI y React nunca se exponen directamente. Sirve el build estático del frontend, actúa como reverse proxy hacia `/api` del backend, y termina HTTPS con certificado institucional. Relevante en particular por el despliegue dentro de la intranet de la UCC. El frontend ya está integrado contra el backend real (Fases 1-5, ver `sprint.md` — "feature/frontend-fases1-5").

**Actualización 31/07/2026 (`fix/frontend-ui-integracion`, F9):** el build estático servido por nginx ya existe y corre — `frontend/Dockerfile` (multi-stage: node build + nginx sirviendo `dist/` con fallback `try_files` a `index.html`, necesario porque el router usa `createBrowserRouter`). Verificado end-to-end por primera vez en la historia del proyecto: `docker-compose up -d` levanta los cuatro servicios, y a través de nginx `GET /` responde 200 con HTML real, `/ping` proxea al backend, `/config` sirve la SPA, y un login real funciona same-origin (sin CORS de por medio, tal como predice esta misma sección). La nota anterior de esta sección ("lo que todavía no existe es el build estático servido por nginx") queda superada — ver mapeo de puertos del backend más abajo, que sigue siendo válido para desarrollo sin levantar nginx.

---

## Separación de responsabilidades — flujo de datos

El flujo de datos desde el request hasta el core sigue
este orden estricto. Cada capa tiene una única responsabilidad:

api/        → recibe el request HTTP, valida con Pydantic,
genera session_id, delega a services/
NO parsea archivos, NO ejecuta lógica de negocio
core/parser.py → extrae serie, timestamps y resolucion_temporal
del UploadFile. Devuelve tipos Python puros.
NO sabe que existe HTTP ni BD
services/   → orquesta el pipeline: llama a core/parser.py,
llama a core/pipeline.py, emite eventos SSE,
persiste en BD si hay user_id
NO recibe UploadFile, NO define endpoints
core/       → ejecuta pruebas estadísticas sobre tipos Python puros
NO sabe que existe HTTP, BD, archivos ni sesiones

Cualquier lógica que no encaje claramente en una de estas
capas es señal de que falta un módulo nuevo.

---

## Estructura de contenedores Docker

```yaml
services:
  backend:
    build: ./backend
    command: uvicorn metis.main:app --host 0.0.0.0 --port 8000 --reload   # --reload — DECISIÓN de PR fix/backend-hot-reload (12/08/2026)
    volumes:
      - ./backend:/app   # bind mount — el proceso ve los cambios del host sin docker cp + docker restart
    depends_on: [postgres]
    env_file: .env
    ports: ["8000:8000"]   # mapeo al host — necesario para smoke tests y desarrollo local sin nginx

  frontend:
    build: ./frontend
    depends_on: [backend]

  postgres:
    image: postgres:15
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports: ["5432:5432"]   # mapeo al host — necesario para Alembic y psql desde la terminal local

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    depends_on: [backend, frontend]
```

### `--reload` + bind mount en `backend` — solo para desarrollo local

Antes de este PR, `docker cp` actualizaba los archivos dentro del contenedor
pero el proceso `uvicorn` ya arrancado seguía sirviendo el código que tenía
cargado en memoria — solo un `docker restart` hacía que el servidor HTTP
viera un cambio de código (`pytest`/`ruff` vía `docker exec` no lo sufrían,
por correr como procesos nuevos). Ver `docs/pendientes-tecnicos.md` para el
diagnóstico original, encontrado en el Bloque C del plan de Etapa 2.

`command: uvicorn ... --reload` + `volumes: ["./backend:/app"]` resuelve
esto: el bind mount monta el código del host sobre `/app` (donde el
Dockerfile ya lo había copiado), y `--reload` (vía `watchfiles`, incluido en
`uvicorn[standard]==0.29.0`) reinicia el proceso solo cuando detecta un
cambio. Las dependencias instaladas viven en `site-packages`, fuera de
`/app`, así que el mount no las tapa.

**Caveat de producción.** Este `docker-compose.yml` es también la
aproximación al despliegue de la UCC. Con `--reload` + bind mount, el
contenedor sirve el código del host, no el de la imagen — correcto para
desarrollo, no para producción. Si en M4/M5 aparece un compose de producción
real, esta configuración se mueve a un `docker-compose.override.yml` y el
base vuelve al `CMD` del Dockerfile (que no cambia — sigue siendo el de
producción, este `command` solo lo pisa a nivel de compose).

### Exposición de puertos en desarrollo — backend y postgres

`expose` y `ports` no son equivalentes:

- **`expose: ["N"]`** — publica el puerto solo dentro de la red Docker interna.
  Los contenedores se conectan entre sí por nombre de servicio (ej. `backend:8000`,
  `postgres:5432`), pero el host no puede alcanzar `localhost:N`.

- **`ports: ["N:N"]`** — mapea el puerto del contenedor al host.
  Permite conectarse desde la terminal local con `localhost:N`.

**`ports: ["8000:8000"]` en backend** es necesario para:
- Smoke tests manuales desde el host sin levantar nginx ni el frontend
- Desarrollo local directo contra la API (`curl`, httpie, Postman)
- El frontend en desarrollo (`npm run dev` en el host) que hace requests a `localhost:8000`
- Mientras el frontend no esté implementado, nginx no puede levantarse — este
  mapeo permite verificar la API sin depender del stack completo

**`ports: ["5432:5432"]` en postgres** es necesario para:
- `alembic upgrade head` / `alembic check` desde la terminal del host
- `psql` u otros clientes de BD en desarrollo
- Tests de integración que corren fuera de Docker

En producción en la intranet de la UCC estos mapeos no representan riesgo
adicional: el firewall perimetral de la UCC controla el acceso externo.
Ambos puertos solo son alcanzables desde dentro de la red institucional.

Nginx es el único servicio expuesto al exterior para tráfico HTTP/HTTPS.
FastAPI y React nunca se exponen directamente.

### DATABASE_URL — diferencia entre Docker y host

Esta es la fuente de confusión más común al configurar el entorno por primera vez.

El `.env` contiene una sola `DATABASE_URL`, pero el host correcto de PostgreSQL
depende de **dónde corre el código que la usa**:

| Contexto | Host en la URL | Por qué |
|---|---|---|
| Backend dentro de Docker | `postgres` | nombre del servicio en la red Docker interna |
| Alembic / psql desde el host | `localhost` | puerto 5432 mapeado via `ports: ["5432:5432"]` |

**Regla:** el `.env` siempre debe tener `postgres` como host — es el valor correcto
para el runtime principal (backend Docker). Nunca cambiar el `.env` a `localhost`.

**Override para herramientas desde el host:**
Sobreescribir `DATABASE_URL` en la línea de comando, sin tocar el `.env`:

```bash
# Alembic desde el host
DATABASE_URL=postgresql+asyncpg://metis_user:metis_pass@localhost:5432/metis \
  alembic upgrade head

DATABASE_URL=postgresql+asyncpg://metis_user:metis_pass@localhost:5432/metis \
  alembic check

# psql desde el host (usa psycopg2, no asyncpg)
psql postgresql://metis_user:metis_pass@localhost:5432/metis
```

El override solo existe en la sesión de terminal. No se commitea. El `.env` no se toca.

---

## Esquema de base de datos

### Tabla: users
```sql
id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
email          VARCHAR(255) UNIQUE NOT NULL  -- siempre @ucc.edu.ar
nombre         VARCHAR(255)
password_hash  VARCHAR(255) NOT NULL         -- bcrypt hash
email_verified BOOLEAN NOT NULL DEFAULT false
created_at     TIMESTAMP DEFAULT NOW()
last_login     TIMESTAMP
```

### Tabla: analyses
```sql
id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id        UUID REFERENCES users(id) ON DELETE CASCADE
serie          JSONB NOT NULL        -- array numérico completo
timestamps     JSONB                 -- migración 005 (DECISIÓN 058) — timestamps de `serie`
                                      -- tal como se subió, ISO-8601; NULL sin backfill en filas
                                      -- previas a esta migración
tipo_variable  VARCHAR(50) NOT NULL  -- caudal_precipitacion | otro
etapas         VARCHAR[]             -- {1} | {1,2}
modo           VARCHAR(20)           -- paso_a_paso | experto
configuracion  JSONB                 -- partición Cramer, mes_inicio_anio, decisiones contrato
created_at     TIMESTAMP DEFAULT NOW()
archivado_at   TIMESTAMP             -- migración 004 (DECISIÓN 048) — soft-delete, NULL si no archivado
```

### Tabla: analysis_results
```sql
id           UUID PRIMARY KEY DEFAULT gen_random_uuid()
analysis_id  UUID REFERENCES analyses(id) ON DELETE CASCADE
etapa1       JSONB    -- estadísticos, valores críticos, veredictos, warnings
etapa2       JSONB    -- ranking EEA, distribución seleccionada, eventos de diseño. NULL si no ejecutó.
decisiones   JSONB    -- registro de auditoría: qué decidió el usuario ante cada warning
```

### Tabla: api_clients
```sql
id               UUID PRIMARY KEY DEFAULT gen_random_uuid()
client_id        VARCHAR(100) UNIQUE NOT NULL
api_key_hash     VARCHAR(255) NOT NULL  -- bcrypt hash, nunca texto plano
auto_clean       BOOLEAN DEFAULT FALSE
report_frequency INTEGER DEFAULT 1
cramer_particion VARCHAR(20) DEFAULT 'default'
created_at       TIMESTAMP DEFAULT NOW()
activo           BOOLEAN DEFAULT TRUE
```

**Índices obligatorios:**
```sql
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);
CREATE INDEX idx_analysis_results_analysis_id ON analysis_results(analysis_id);
CREATE INDEX idx_api_clients_client_id ON api_clients(client_id);
```

---

## Autenticación — flujo vigente

Usuario/contraseña + JWT (HttpOnly Cookie) + verificación por mail institucional, dentro de la intranet de la UCC. Google OAuth fue evaluado y descartado — el servidor no puede recibir el callback entrante de Google desde la intranet. Ver `docs/decisiones/decision001.md` — DECISIÓN 001. El flujo original evaluado con OAuth queda documentado en `docs/historico/oauth-descartado.md`.

**Variables de entorno del flujo vigente:**
```
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=60
DATABASE_URL=postgresql://user:pass@postgres:5432/metis
SMTP para verificación de mail: ver `docs/decisiones/decision004.md` — DECISIÓN 004.
```