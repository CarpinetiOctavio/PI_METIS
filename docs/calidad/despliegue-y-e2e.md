# Despliegue efímero, smoke y E2E

TP integrador de Calidad de Software, bloques B5 y B6 (`docs/plan-tp-calidad-software.md`). Decisiones: DECISIÓN 046
(E2E con Playwright), DECISIÓN 049 (Mailpit).

## 1. El despliegue

Un solo procedimiento, `scripts/deploy-local.sh`, para la demo local y para el job `despliegue` de CI:

| Paso | Qué hace |
|---|---|
| 1 | `docker compose down -v`: baja el despliegue anterior y borra su base |
| 2 | `docker compose up -d --build --wait` con `docker-compose.yml` + `docker-compose.ci.yml` |
| 3 | `alembic upgrade head` dentro del contenedor `backend` (nada lo hace al arrancar: incidente del 05/08/2026) |
| 4 | espera que nginx responda `/ping` |
| 5 | siembra un usuario verificado (`scripts/seed-dev-user.sh`) para el smoke y los E2E |
| 6 | corre el smoke (`scripts/test.sh smoke`); si falla, el script sale con error y el job falla |

`docker-compose.ci.yml` es el override con la configuración de producción. Respecto del compose de desarrollo:

- `backend` corre el `CMD` del Dockerfile, sin `--reload` ni bind mount: sirve el código de la imagen, no el del host
  (el "caveat de producción" de `architecture.md`).
- La configuración está en el override, no en `.env`: el despliegue no depende de la máquina. Las credenciales son de
  relleno porque el stack nunca sale de la máquina o del runner.
- SMTP contra Mailpit; `FRONTEND_URL=http://localhost` para que el link del mail abra la SPA servida por nginx.
- Solo nginx (80) y Mailpit (8025) se publican al host. Al backend y a la base no se les puede pegar salteándose nginx.
- Proyecto de Compose aparte (`-p metis-ci`): su base no es la de desarrollo, y `down -v` no la toca.
- `ENV=development` a propósito: sin certificado el stack se sirve por HTTP, y con `ENV=production` la cookie JWT
  sale con `Secure` y ni el navegador ni httpx la devuelven. HTTPS queda para el despliegue en la UCC.

Uso local (ocupa el puerto 80; bajar antes el stack de desarrollo con `docker compose down`, que no borra datos):

```bash
scripts/deploy-local.sh              # despliega y corre el smoke
scripts/test.sh e2e                  # E2E contra el despliegue (Mailpit en http://localhost:8025)
scripts/deploy-local.sh --bajar      # baja el despliegue y borra su base
```

## 2. Smoke (`backend/tests/smoke/`, marker `smoke`)

Lo mínimo para decir que el stack levantó y atiende de punta a punta. No importa nada de `metis`: le pega por HTTP a
nginx con httpx, como un cliente cualquiera.

| Test | Qué recorre |
|---|---|
| `test_spa_servida_por_nginx` | nginx → contenedor `frontend` (build estático) |
| `test_spa_resuelve_rutas_del_cliente` | `try_files` de `frontend/nginx.conf` (recargar en `/config` no da 404) |
| `test_ping_llega_al_backend` | `location /ping` de nginx → FastAPI |
| `test_preview_columns` | subida multipart y parser |
| `test_login_y_me` | base migrada, usuario sembrado, cookie HttpOnly |
| `test_stream_etapa1_hasta_complete` | SSE a través de nginx (`proxy_buffering off`) y el motor de Etapa 1 hasta `complete` |
| `test_historial_registra_el_analisis` | persistencia de CU-01 en la base del despliegue |

Sin stack alcanzable los tests se saltean; con `METIS_REQUIRE_SMOKE=1` (lo setea `scripts/test.sh smoke`) fallan.

## 3. E2E (`frontend/e2e/`, Playwright)

Contra el build de producción detrás de nginx, nunca contra `npm run dev` (DECISIÓN 046). Chromium, un worker, en
orden: E2E-4 lee el historial que deja E2E-3.

| ID | Archivo | Flujo | Defecto o riesgo que cubre |
|---|---|---|---|
| E2E-0 | `e2e0-registro.spec.ts` | Registro → mail en Mailpit → link de verificación → login | Integración SMTP de punta a punta (DECISIÓN 049) |
| E2E-1 | `e2e1-login.spec.ts` | Login a `/config`, sesión que sobrevive a recargar; contraseña incorrecta con el error del catálogo | F2, F3; estructura de error estándar (#106) |
| E2E-2 | `e2e2-anonimo.spec.ts` | CU-02: Etapa 1 con la pausa de Chow, sin "Exportar PDF" ni "Historial" | F1; CU-02 sin persistencia ni exportación |
| E2E-3 | `e2e3-cu01-analisis-historial.spec.ts` | CU-01: Etapa 1 y 2, rechazo del atípico, elección de distribución, Resultados y PDF (`%PDF`) | F1, F5; pausas del stream; DECISIÓN 075 |
| E2E-4 | ídem | Historial → detalle del análisis de E2E-3 | F4; persistencia de CU-01 |
| E2E-5 | `e2e5-serie-corta.spec.ts` | Serie de 8 datos: bloqueante con su mensaje y el stream cerrado | Único bloqueante por longitud, sin cuelgue |

Las series están copiadas en `frontend/e2e/fixtures/` (no referenciadas desde `docs/series prueba/`): si cambia la
serie de docs, el E2E no se rompe en silencio. `serie_8_datos.csv` son los primeros 8 años de `serie_con_atipico.csv`.

**En CI** (job `despliegue`): el smoke corre en cada push y PR; los E2E, en cada PR a `staging`/`main`. El reporte
HTML (`reporte-e2e`) se sube siempre, también en verde, con trazas y video de lo que falle.

**Reglas para escribir un escenario nuevo:** llegar a `/stream` y `/results` con clicks (el formulario viaja como
estado del router; sin él redirigen a `/config`); elegir por nombre accesible (`getByRole`/`getByLabel`), no por
clases del tema; emails únicos por corrida; el PDF se captura con el evento `download`, no por la red.
