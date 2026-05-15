# Decisiones de Arquitectura — METIS

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
El motor estadístico en core/ no importa nada de api/, services/, ni db/. Esto hace posible los tests de regresión matemática — se puede testear que Anderson calcula correctamente el estadístico sin levantar la aplicación completa. Es el argumento técnico más sólido ante el tribunal de ISI.

---

## Estructura de contenedores Docker

```yaml
services:
  backend:
    build: ./backend
    depends_on: [postgres]
    env_file: .env

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

### Exposición de puertos — postgres

`expose` y `ports` no son equivalentes:

- **`expose: ["5432"]`** — publica el puerto solo dentro de la red Docker interna.
  Los contenedores (backend) pueden conectarse entre sí por nombre de servicio
  (`postgres:5432`), pero el host no puede alcanzar `localhost:5432`.

- **`ports: ["5432:5432"]`** — mapea el puerto del contenedor al host.
  Permite conectarse desde la terminal local con `localhost:5432`.

El mapeo `ports: ["5432:5432"]` es necesario para:
- `alembic upgrade head` / `alembic check` desde la terminal del host
- `psql` u otros clientes de BD en desarrollo
- Tests de integración que corren fuera de Docker

En producción en la intranet de la UCC esto no representa riesgo adicional:
el firewall perimetral de la UCC controla el acceso externo. El puerto 5432
solo es alcanzable desde dentro de la red institucional.

Nginx es el único servicio expuesto al exterior para tráfico HTTP/HTTPS.
FastAPI y React nunca se exponen directamente.

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
tipo_variable  VARCHAR(50) NOT NULL  -- caudal_precipitacion | otro
etapas         VARCHAR[]             -- {1} | {1,2}
modo           VARCHAR(20)           -- paso_a_paso | experto
configuracion  JSONB                 -- partición Cramer, decisiones contrato
created_at     TIMESTAMP DEFAULT NOW()
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

## Flujo de autenticación OAuth — implementación correcta

```
1. Frontend → GET /api/v1/auth/google
2. Backend redirige a accounts.google.com/oauth2/auth con scope=email
3. Google autentica al usuario
4. Google → GET /api/v1/auth/callback?code=XXX (llega al BACKEND, no al frontend)
5. Backend intercambia code por token con Google
6. Backend verifica que email termine en @ucc.edu.ar → 403 si no cumple
7. Backend genera JWT propio (NO usa el token de Google directamente)
8. Backend setea JWT en HttpOnly Cookie con SameSite=Lax, Secure=True
9. Backend redirige al frontend — el frontend NUNCA ve el JWT

> ⚠️ IMPORTANTE: Este flujo fue descartado. Ver decisions-log.md — DECISIÓN 001.
```

**Variables de entorno necesarias:**
```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://dominio-ucc/api/v1/auth/callback
JWT_SECRET_KEY=
JWT_EXPIRE_MINUTES=60
DATABASE_URL=postgresql://user:pass@postgres:5432/metis
```
