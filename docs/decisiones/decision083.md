# DECISIÓN 083: despliegue en la UCC con un override versionado, subred propia y HTTPS pendiente del certificado

**Fecha:** 29 de octubre de 2026 (actualizada el 30/10/2026)
**Estado:** Parte HTTP aplicada en el servidor. Parte HTTPS lista en la rama `feature/despliegue-ucc-tls-cert`, sin
mergear: se aplica cuando IT entregue el nombre DNS interno y el certificado.
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

**Parte 2, pendiente (rama `feature/despliegue-ucc-tls-cert`):** `docker-compose.ucc.yml` con el 443, el certificado
montado desde `certs/` (ignorado por git), `ENV=production` y `METIS_URL` con `https://`; y `nginx/nginx.ucc.conf` con
el 80 redirigiendo al 443 y TLS 1.2 y 1.3, partiendo lo común con la versión HTTP en `nginx/metis-comun.conf`. HSTS queda comentado hasta que el certificado esté estable. Esa rama tiene
que rebasarse sobre la parte 1 y convertir el override en un archivo adicional (`docker-compose.ucc-tls.yml`), porque
el override de la parte 1 no puede traer el 443 sin certificado: nginx no arrancaría.

### Verificación

- **D-UCC-04 (30/10/2026):** `ip route` del servidor sin `172.18.0.0/16` y con `10.250.0.0/24`; en el log de nginx
  aparecen accesos desde `172.18.5.26`, que antes del cambio no podían responderse. Los cuatro servicios llevan más
  de 27 horas arriba sin reinicios.
- **D-UCC-03:** con la exclusión de IT, desde un cliente de la red de la UCC llegan el `stream` de Etapa 1 y 2 (17 y
  35 KB), `outlier-decision`, `distribution-decision` y `simulate-exclusion`, todos con 200. Falta la corrida
  formal de `sonda_metis.py` desde UCC-Free.
- **Parte 2:** verificada en local con un certificado autofirmado (80 redirige, cookie con `Secure`, stream completo
  por HTTPS). Falta la verificación desde UCC-Free con el nombre y el certificado reales, y el reinicio controlado
  del servidor (B3).

### Relación con otras decisiones

- **DECISIÓN 028:** deploy a la UCC; esta decisión define cómo se levanta, no cómo llega el código.
- **DECISIÓN 034:** SMTP de la UCC; su addendum del 29/10/2026 corrige el host.
- **DECISIÓN 050:** tope de subida; nginx deja pasar 11 MB y responde el 413 con el código del contrato.
- **DECISIONES 052 y 053:** pausas del stream; la alternativa (b) las cambiaría.
- **DECISIÓN 077:** `docker-compose.ci.yml` y `deploy-local.sh`, el patrón que sigue este override.
