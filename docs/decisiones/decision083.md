# DECISIÓN 083: despliegue en la UCC con un override versionado, subred propia y HTTPS pendiente del certificado

**Fecha:** 29 de octubre de 2026 (actualizada el 30/10/2026)
**Estado:** Parte HTTP aplicada en el servidor. Parte HTTPS reescrita el 04/11/2026 para el esquema de Cloudflare con
certificado autofirmado (ver el addendum de esa fecha) y **desplegada en el servidor el 07/11/2026** desde la rama
`deploy/ucc` (ver el addendum de esa fecha): el 80 y el 4443 responden. Pendiente de que IT repunte el proxy al 4443,
de la prueba de la pausa del stream a través de Cloudflare y de `real_ip`.
**Decide:** Kevin, a partir de la evaluación del despliegue en 172.16.168.14 del 29/10/2026.
**Origen:** [plan de mejoras post-despliegue](../Plan%20de%20mejoras%20post-despliegue%20UCC%20y%20respuestas%20de%20Facundo.md),
bloque A3 (hallazgos H2, H4, H5 y H6). Defectos D-UCC-03 y D-UCC-04.

### Problema

1. Desde la red del campus, Etapa 2 y la pausa por atípico nunca llegaban al navegador: `/ping` respondía normal, pero
   el stream no entregaba ni un evento en 90 s. Desde adentro del servidor el ranking salía en 50 ms. Algo en la red
   retenía cada respuesta HTTP hasta que terminaba, y un stream en pausa (Chow, elección de distribución) no termina
   nunca: espera un `POST` que el usuario no puede mandar porque no vio la pregunta (D-UCC-03).
2. El servidor escucha solo en el 80: la contraseña y la cookie de sesión viajan en claro por un wifi abierto (H4), y la
   cookie sale sin `Secure` porque el backend corre con `ENV=development` (H6). Con `Secure` sobre HTTP el login
   quedaría muerto.
3. Ningún servicio del compose tenía `restart` (H5): tras un reinicio del servidor METIS no vuelve.
4. IT no llegaba a la VM por ping ni por el puerto 80 desde su firewall, aunque las reglas y la ruta estaban bien. La
   red de Docker del servidor usaba `172.18.0.0/16`, el rango del gateway `172.18.0.1` que usa la ruta de IT: las
   respuestas a ese origen se iban al puente de Docker y no salían por la placa de red (D-UCC-04).

### Alternativas evaluadas

- **(a) Pedirle a IT que excluya el servidor de la inspección HTTP.** Hecha por IT el 30/10/2026 (comentario 1 de su
  respuesta). Resuelve el síntoma, pero deja todo en claro y depende de una regla de red que puede cambiar sin aviso.
- **(b) Cambiar el contrato SSE:** cerrar el stream en cada pausa y que el `POST` de la decisión devuelva la
  continuación. Resuelve el síntoma con cualquier red, pero es un cambio grande en el contrato de las DECISIONES 052 y
  053 a días de la defensa. Queda para la v2.
- **(c) HTTPS en nginx.** Un intermediario no puede retener por contenido lo que no puede leer, y además cifra la
  contraseña y la cookie, lo que habilita `ENV=production`. Es la solución de fondo, pero IT respondió que el
  certificado no lo entregan ellos y derivó el nombre DNS al área de Seguridad, que lo ve la semana siguiente.

### La decisión

Se parte en dos para no atar lo que ya se puede desplegar a lo que depende de un tercero.

**Parte 1, aplicada (rama `feature/despliegue-ucc-http`):**

- **`docker-compose.ucc.yml`**, override sobre `docker-compose.yml` y `docker-compose.ci.yml` (el patrón de la
  DECISIÓN 077, el mismo que ya corre en el servidor), sin secretos: SMTP del relay real con el host
  `wally.uccor.edu.ar` (DECISIÓN 034), `FRONTEND_ORIGIN` y `FRONTEND_URL` desde `METIS_URL` (por defecto la IP),
  `restart: unless-stopped` en todos los servicios, Mailpit fuera (perfil `mailpit`) y la subred
  `10.250.0.0/24` para la red de Docker (D-UCC-04). `ENV` sigue en `development`: se sirve por HTTP.
- **nginx.** El endurecimiento (cabeceras de seguridad, gzip sin `text/event-stream`, caché de assets y tope de subida
  de 11 MB, B1 y B2) viaja en su propio PR, `feature/nginx-endurecimiento`. Esta decisión no cambia nginx.
- **Respaldo y runbook.** `scripts/respaldo-db.sh` (B5) y `docs/calidad/despliegue-ucc.md` (B7).
- **El servidor.** El compose ya fijaba lo mismo a mano: esta decisión lo versiona. Para que la subred tome efecto hay
  que bajar el stack sin `-v` y volver a levantarlo.

**Parte 2, reescrita el 04/11/2026 (rama `deploy/ucc`):** ver "Addendum 04/11/2026" más abajo. El texto original
suponía un certificado de la UCC y un nombre DNS interno; ninguno de los dos llegó.

### Verificación

- **D-UCC-04 (30/10/2026):** `ip route` del servidor sin `172.18.0.0/16` y con `10.250.0.0/24`; en el log de nginx
  aparecen accesos desde `172.18.5.26`, que antes del cambio no podían responderse. Los cuatro servicios llevan más
  de 27 horas arriba sin reinicios.
- **D-UCC-03:** con la exclusión de IT, desde un cliente de la red de la UCC llegan el `stream` de Etapa 1 y 2 (17 y
  35 KB), `outlier-decision`, `distribution-decision` y `simulate-exclusion`, todos con 200. Falta la corrida
  formal de `sonda_metis.py` desde UCC-Free.
- **Parte 2 (04/11/2026):** el certificado que genera `scripts/generar-cert-ucc.sh` se validó con `openssl` (SAN con la
  IP, `CA:FALSE`, `serverAuth`, clave y certificado correspondientes, clave con permisos 600, el script no pisa un
  certificado existente) y los tres YAML de compose parsean. **No se pudo levantar nginx en el entorno de trabajo** (sin
  Docker); la sintaxis y el contexto de cada directiva de `nginx.conf` y `nginx.ucc.conf` (con `metis-comun.conf` incluido) se
  validaron con el parser `crossplane`, que no reemplaza a `nginx -t`: la configuración con el HTTPS se verifica en el servidor con `docker compose config` y `nginx -t` antes de
  avisar a IT. Falta además la verificación desde UCC-Free, el reinicio controlado del servidor (B3) y la prueba de la
  pausa del stream a través de Cloudflare.
- **Parte 2, en el servidor (07/11/2026):** `docker compose config` valida, `nginx -t` da `test is successful` (con nginx
  real, lo que no se había podido en el entorno de trabajo), `/ping` responde 200 por el 80 y por el 4443, el certificado
  trae la IP y `metis.ucc.edu.ar`, `alembic current` da `007 (head)`, el log del backend sin errores y `ip route` con
  `10.250.0.0/24`. Evidencia en `docs/calidad/evidencia/despliegue-ucc-07-11-2026/verificacion-https.txt`. Sigue sin
  verificarse la entrada a través de Cloudflare, la sonda desde UCC-Free y el reinicio controlado (B3).

### Relación con otras decisiones

- **DECISIÓN 028:** deploy a la UCC; esta decisión define cómo se levanta, no cómo llega el código.
- **DECISIÓN 034:** SMTP de la UCC; su addendum del 29/10/2026 corrige el host.
- **DECISIÓN 050:** tope de subida; nginx deja pasar 11 MB y responde el 413 con el código del contrato.
- **DECISIONES 052 y 053:** pausas del stream; la alternativa (b) las cambiaría.
- **DECISIÓN 077:** `docker-compose.ci.yml` y `deploy-local.sh`, el patrón que sigue este override.

### Addendum 04/11/2026: HTTPS detrás de Cloudflare, con certificado autofirmado

**Qué cambió.** IT (Mariano Aliaga) respondió que el sitio ya está publicado detrás de Cloudflare, con acceso restringido
a la red interna de la UCC, y que hoy Cloudflare llega al contenedor por HTTP. Pidió exponer HTTPS con un certificado
autofirmado en un puerto nuevo y avisarle para que repunte el proxy. Eso reemplaza el plan de la parte 2 (certificado de
la UCC, nombre DNS interno, el 80 redirigiendo al 443).

**Decisión.**

- **Certificado autofirmado, generado en el servidor** con `scripts/generar-cert-ucc.sh` (RSA 2048, 10 años, SAN con la
  IP 172.16.168.14 y los nombres que se le pasen). Vive en `certs/`, ignorado por git. No hay nada que renovar: con
  Cloudflare en modo "Full" el certificado de origen se cifra pero no se valida, así que no tiene que ser de confianza
  (en modo "Full (strict)" haría falta un certificado de origen de Cloudflare: es una pregunta abierta a IT).
- **`docker-compose.ucc-tls.yml` como cuarto archivo de `COMPOSE_FILE`**, no como edición de `docker-compose.ucc.yml`:
  sin certificado, nginx no arranca, y el override de la parte 1 tiene que seguir sirviendo sin él. Publica el 4443 del
  host (el 443 del contenedor: IT pidió el 4443),
  monta `nginx/nginx.ucc.conf` y `certs/` de solo lectura, y deja el `ENV` del backend en `METIS_ENV`.
- **El 80 no redirige al 443.** Mientras IT no repunte el proxy, Cloudflare sigue entrando por el 80; una redirección
  ahí produce un bucle. Los dos puertos sirven lo mismo. Cuando el proxy ya entre por el 4443, el 80 puede pasar a
  redirigir, o cerrarse.
- **`nginx/metis-comun.conf`** parte lo común (tope de subida, cabeceras, `location`) entre `nginx.conf` (80, desarrollo,
  CI) y `nginx.ucc.conf` (80 y 443). `docker-compose.yml` lo monta, así que el cambio también pasa por el CI.
- **`ENV=production` se decide aparte** (`METIS_ENV`, por defecto `development`). Con `production` la cookie sale
  `Secure`; detrás de Cloudflare el navegador ve `https://` y funciona, pero quien entre por `http://172.16.168.14`
  directo se queda sin login. Se activa cuando nadie más entre por HTTP.
- **`METIS_URL`** pasa a ser la URL pública de Cloudflare: de ahí salen el origen que acepta CORS y los links de los
  mails de verificación y de recuperación. Con la IP, esos links apuntan a una dirección que fuera de la UCC no existe.
- **HSTS no se activa** con un certificado autofirmado.

**Respuesta de IT del 04/11/2026** (Mariano Aliaga, por mail):

- URL pública: `https://metis.ucc.edu.ar`. Es el `METIS_URL` del `.env`.
- Modo SSL de Cloudflare: lo configura IT; piden solo un autofirmado (modo "Full").
- Puerto: **4443** en lugar del 443. El 80 queda como está hasta que se avise.
- IP real: `X-Real-IP` y, si no está, `CF-Connecting-IP`. No dijeron los rangos desde los que se conecta el proxy.
- Sin desafíos, Rocket Loader ni Auto Minify, y sin caché de `/api/`: aceptado.
- Timeout de inactividad de Cloudflare: **100 s**, y la recomendación es un latido.
- Límite de envío del relay para el usuario `metis`: no hay.

**Latido del stream (mismo día).** Con el tope de 100 s confirmado, las dos pausas del stream (atípico de Chow y
elección de distribución, de hasta `SESSION_TIMEOUT` = 300 s) mandan un comentario SSE (`: latido`) cada 20 s mientras
esperan la decisión (`services/analysis_service.py::_esperar_decision_con_latido`). Es un comentario, no un evento: el
contrato del stream no cambia, y `@microsoft/fetch-event-source` lo entrega con `data` vacío, que `api/sse.ts` ya
descarta (`if (!ev.data) return`). Tests en `tests/unit/services/test_latido_sse.py`. Falta confirmarlo a través de
Cloudflare dejando una pausa abierta 3 minutos. nginx no hace falta tocarlo: `proxy_buffering off` y
`proxy_read_timeout 3600s` ya estaban.

**Qué sigue abierto:**

- **Rangos del proxy para `real_ip`.** `nginx.ucc.conf` trae el bloque comentado con `X-Real-IP`; se completa con la IP
  del proxy que se lea en el log de nginx después de que repunte. Es requisito previo para cualquier `limit_req` (B9).
- **Rotación de la contraseña SMTP** (se mostró en capturas durante el diagnóstico): no se había pedido a IT antes de
  terminar el despliegue. Se pide junto con el aviso del 4443.

**Por qué se sigue considerando solución para D-22.** El tramo que retenía las respuestas es el de la red de la UCC; si
Cloudflare entra por el 4443, ese tramo ya no es legible para la inspección. Se confirma con la corrida de
`sonda_metis.py` desde UCC-Free, no se da por cerrado antes.

### Addendum 07/11/2026: primer despliegue de la parte 2 en el servidor

- **Qué se hizo.** En `~/metis-app`: checkout de `deploy/ucc`, certificado con `scripts/generar-cert-ucc.sh`,
  `COMPOSE_FILE` con `docker-compose.ucc-tls.yml`, `up -d --build`, `alembic upgrade head` (la `007`, `auth_tokens`) y
  `nginx -t`. Resultado y evidencia en la sección Verificación.
- **Tropiezos, todos de procedimiento y ninguno de diseño** (ahora en el runbook, `despliegue-ucc.md` §6): un
  `docker-compose.ucc.yml` armado a mano que impedía el checkout; un bloque de comandos pegado dentro de `nano` que
  ensució el `.env` (se reparó con `sed`, sin mostrar valores); `docker compose exec` consumiendo la entrada pegada, y
  `/ping` que responde 405 a HEAD (el runbook usaba `curl -I`). Además, la primera migración se corrió antes de
  reconstruir la imagen, contra el código viejo, y no hizo nada: va después de `--build`, porque las migraciones viajan
  en la imagen.
- **Qué entra hoy.** Cloudflare sigue entrando por el 80, porque IT todavía no repunta. La entrada oficial es
  `https://metis.ucc.edu.ar`; la IP y el 4443 son direcciones del origen. `FRONTEND_ORIGIN` y `FRONTEND_URL` salen de
  `METIS_URL`, con la IP solo como valor por defecto del compose: con `METIS_URL` en el `.env` el origen CORS y los links de
  los mails usan el dominio. La prueba que vale es por el dominio.
- **La prueba del latido no espera a IT.** El tope de 100 s es del tramo entre el navegador y Cloudflare, sea cual sea
  el puerto del origen: se prueba por el dominio con una pausa de Etapa 2 abierta 3 minutos.
- **Qué sigue abierto:** confirmar `METIS_URL` en el `.env`, la prueba por el dominio, el aviso a IT (repunte al 4443,
  firewall proxy a VM por el 4443, IP del proxy para `set_real_ip_from`), la sonda desde UCC-Free, el reinicio
  controlado y NTP (B3 y B4, de IT), el cron del respaldo con una restauración de prueba (B5), el smoke del servidor
  (B6) y `METIS_ENV=production` cuando nadie entre por HTTP directo.
