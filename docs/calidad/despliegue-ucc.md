# Despliegue en el servidor de la UCC: runbook

B7 del [plan de mejoras post-despliegue](../Plan%20de%20mejoras%20post-despliegue%20UCC%20y%20respuestas%20de%20Facundo.md)
(29/10/2026). Cómo se levanta METIS en el servidor, qué tiene que tener el `.env`, cómo se verifica y qué hacer
cuando algo falla. Decisión de fondo: [DECISIÓN 083](../decisiones/decision083.md). El despliegue efímero de CI y de
la demo es otro: [despliegue-y-e2e.md](despliegue-y-e2e.md).

**Por qué este documento existe.** Los defectos de la evaluación del 29/10/2026 (D-UCC-01 a 04,
[registro-defectos.md](registro-defectos.md)) no los podía detectar ni el CI ni el despliegue efímero: aparecen solo
con la red, el DNS y el relay reales de la UCC. El despliegue real es un nivel de prueba propio.

## 1. Servidor y archivos

- **Host:** 172.16.168.14 (`ingpi`, Debian 12), usuario `metis`. IT administra el host. Se entra por el portal de la UCC
  (Guacamole, terminal por RDP), no por SSH directo. Docker y Compose están instalados; el usuario `metis` está en el
  grupo `docker` y no tiene `sudo`.
- **Directorio del compose:** `~/metis-app`, el clon del repo. Además de lo versionado tiene dos cosas que no están en
  git: el `.env` (los secretos, §2) y `respaldos/` (los volcados de la base, §5).
- **Qué archivos de compose se usan.** Tres, encadenados con `COMPOSE_FILE` en el `.env`, así cualquier `docker compose`
  hecho en ese directorio los toma sin acordarse de nada:

  ```
  COMPOSE_FILE=docker-compose.yml:docker-compose.ci.yml:docker-compose.ucc.yml
  ```

  `docker-compose.ci.yml` es la configuración "de producción" (sin `--reload`, sin bind mount, sin puertos de base y
  backend) y `docker-compose.ucc.yml` agrega lo propio del servidor (DECISIÓN 083).
- **Disco:** la VM tiene 9,3 GB y unos 3,9 GB libres. Antes de reconstruir imágenes, `df -h /`; si hace falta,
  `docker image prune -f`.

## 2. `.env` esperado (sin valores)

`docker-compose.ci.yml` lleva la configuración de la app y `docker-compose.ucc.yml` la del servidor, así que en el
`.env` quedan los secretos y las pocas variables de entorno del despliegue:

| Variable | Valor esperado | Nota |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | `metis` | El nombre del volumen de la base es `metis_postgres_data`: si cambia, la base "desaparece" |
| `COMPOSE_FILE` | los tres archivos (§1) | |
| `METIS_CI_DB_PASSWORD` | la clave con la que se creó la base | Postgres **ignora** `POSTGRES_PASSWORD` si el volumen ya existe: no cambiarla acá sin cambiarla en la base |
| `METIS_CI_JWT_SECRET` | cadena aleatoria larga | Cambiarla cierra todas las sesiones |
| `SMTP_PASSWORD` | credencial de IT | Obligatoria: sin ella el compose no arranca. Cargarla con `read -s`, entre comillas simples |
| `SMTP_HOST` | opcional, por defecto **`wally.uccor.edu.ar`** | No `wally.ucc.edu.ar`: el certificado del relay no lo cubre (D-UCC-01, DECISIÓN 034) |
| `SMTP_PORT`, `SMTP_USER`, `SMTP_FROM_ADDRESS` | opcionales: `587`, `metis`, `metis-noreply@ucc.edu.ar` | `SMTP_FROM_ADDRESS` distinta de `SMTP_USER` (DECISIÓN 034, bug 2) |
| `METIS_URL` | opcional, por defecto `http://172.16.168.14` | Con el nombre DNS de IT cuando lo asignen. Sin barra final |

Un valor de relleno sin reemplazar (`SMTP_PORT=PUERTO_REAL`, por ejemplo) hace caer el backend en bucle con
`ValueError` al arrancar. `docker compose config` muestra lo que se va a aplicar, con los secretos incluidos: no
pegar su salida en ningún lado.

## 3. Levantar y redesplegar

```bash
cd ~/metis-app
git pull                                             # main
docker compose up -d --build
docker compose exec backend alembic upgrade head     # nada lo corre solo
docker compose ps
```

- Un cambio en `.env` se aplica con `docker compose up -d backend`, **no** con `restart`: `restart` no relee el
  `env_file` ni las variables.
- **Cambiar la red de Docker** (la primera vez que se aplica la subred fija de D-UCC-04): `docker compose down`, **sin
  `-v`** (con `-v` se borra la base), y `docker compose up -d`. Después, `ip route` tiene que mostrar `10.250.0.0/24`
  y no `172.18.0.0/16`. Si el sitio da 502 al volver, `docker compose restart nginx`.
- Todos los servicios tienen `restart: unless-stopped`: después de un reinicio del servidor vuelven solos, siempre que
  Docker arranque con el host (`systemctl is-enabled docker`). Un `docker compose stop` los deja parados hasta el
  próximo `up`.
- **Antes de redesplegar:** un respaldo (§5) y las cuentas de la demo a mano. Los tokens de verificación viven en
  memoria del backend (H8): cada recreación del backend deja sin verificar a quien se registró y no terminó. No
  redesplegar la víspera de la defensa.
- **Antes de `up`, si `docker compose config` falla,** el mensaje dice qué variable falta o qué línea del YAML está
  mal. No avanzar hasta que valide.

## 4. Verificación después de cada redespliegue

1. **Sonda desde UCC-Free** (una notebook en el wifi del campus, no desde el servidor):
   `python sonda_metis.py --base http://172.16.168.14`. Tiene que llegar a Etapa 1 y 2 hasta el ranking y a la pausa
   por atípico con `serie_con_atipico.csv`. Con HTTPS (parte 2 de la DECISIÓN 083) pasa a `https://<nombre-interno>`
   y suma la cookie con `Secure` y los chequeos de cabeceras y puertos.
2. **Smoke del repo** (B6), desde el contenedor del backend, contra nginx y con una cuenta de smoke propia:

   ```bash
   scripts/seed-dev-user.sh smoke@ucc.edu.ar '<clave>'      # una sola vez
   scripts/seed-dev-user.sh smoke2@ucc.edu.ar '<clave>'     # test_aislamiento.py usa dos usuarios
   docker compose run --rm --no-deps \
     -e SMOKE_BASE_URL=http://nginx -e METIS_REQUIRE_SMOKE=1 \
     -e SMOKE_EMAIL=smoke@ucc.edu.ar -e SMOKE_EMAIL_2=smoke2@ucc.edu.ar -e SMOKE_PASSWORD='<clave>' \
     backend pytest -m smoke tests/smoke -v
   ```

3. **SMTP:** registrar una casilla real `@ucc.edu.ar` → 201, llega el mail (mirar también spam), el link verifica, el
   login entra. Si el registro devuelve 500 con `AUTH_VERIFICATION_EMAIL_FAILED`, el motivo está en
   `docker compose logs --tail 80 backend` (el error de TLS, de red o de timeout sale con código, D-UCC-02). Para
   aislar la causa sin pasar por la app, desde el contenedor:

   ```bash
   docker compose exec -T backend python -c "import socket,time; t=time.time(); s=socket.create_connection(('wally.uccor.edu.ar',587),timeout=10); print('conecta en', round(time.time()-t,2), 's'); print(s.recv(200))"
   ```

   Tiene que mostrar un banner `220 ... ESMTP Postfix`. Un `TimeoutError` es el firewall (pedir a IT la regla
   172.16.168.14 → 172.16.66.113:587); un `535` es la contraseña del `.env`.

## 5. Respaldo de la base (B5)

`scripts/respaldo-db.sh` hace `pg_dump` dentro del contenedor, lo comprime en `respaldos/` y borra los de más de 7 días
(`RETENCION_DIAS`). Como `COMPOSE_FILE` está en el `.env`, alcanza con ejecutarlo en el directorio del compose. Cron
del usuario `metis`, todos los días a las 3:

```cron
0 3 * * * cd /home/metis/metis-app && scripts/respaldo-db.sh >> respaldos/cron.log 2>&1
```

**Restauración de prueba** (en una base aparte, sin tocar la de producción):

```bash
docker compose exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" metis_restauracion'
gunzip -c respaldos/metis_<fecha>.sql.gz | docker compose exec -T postgres sh -c 'psql -q -U "$POSTGRES_USER" -d metis_restauracion'
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d metis_restauracion -c "select count(*) from analyses"'
docker compose exec -T postgres sh -c 'dropdb -U "$POSTGRES_USER" metis_restauracion'
```

Probado el 29/10/2026 contra el despliegue de `scripts/deploy-local.sh`: `users`, `analyses`, `analysis_results` y
`alembic_version` con los mismos conteos en la base original y en la restaurada. **Falta repetirlo en el servidor.**

## 6. Contingencias

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Registro 500 con `AUTH_VERIFICATION_EMAIL_FAILED`, log con `SSLCertVerificationError` | `SMTP_HOST` con un nombre que el certificado no cubre | `SMTP_HOST=wally.uccor.edu.ar` (o quitarlo del `.env`, el default ya es ese) y `docker compose up -d backend` (§2, D-UCC-01) |
| Registro 500 con `TimeoutError` en el log, o el navegador espera y corta | El 587 hacia `172.16.66.113` bloqueado, o el relay lento (el backend corta a los 20 s) | Prueba de conexión del §4.3; si no conecta, pedir a IT la regla del firewall |
| Registro 500 con `SMTPAuthenticationError 535` | La contraseña del `.env` no es la vigente | Recargarla con `read -s -p "Password SMTP: " P` y escribirla entre comillas simples; `docker compose up -d backend`. No pegarla en capturas ni chats |
| Backend en bucle de reinicios, `ValueError` en el log | Una variable del `.env` con un valor de relleno (`SMTP_PORT=PUERTO_REAL`) | Corregir el valor y `docker compose up -d backend` |
| IT no llega a la VM (ni ping ni el puerto 80) aunque las reglas y la ruta están bien | La red de Docker se solapa con el rango de la ruta de IT (172.18.0.0/16, D-UCC-04) | `ip route`: no debe haber `172.18.0.0/16`. Si está, la subred fija no se aplicó: `docker compose down` (sin `-v`) y `up -d` (§3) |
| Desde el campus no llega Etapa 2 ni el modal de atípico; `/ping` anda | La red retiene la respuesta HTTP hasta que termina (D-UCC-03): la excepción de IT dejó de aplicarse | Pedir a IT que verifique la exclusión de 172.16.168.14; la solución de fondo es HTTPS (DECISIÓN 083, parte 2) |
| El login responde 200 pero no queda sesión | Solo con HTTPS: cookie con `Secure` servida por HTTP | Entrar por `https://`. Con el servidor en HTTP, `ENV` tiene que seguir en `development` |
| METIS no vuelve después de un reinicio del servidor | Docker no arranca con el host, o se levantó sin los tres archivos | `systemctl is-enabled docker`; `docker compose up -d` en `~/metis-app` (§1) |
| Las cuentas sin verificar no reciben el link después de reiniciar el backend | Los tokens de verificación viven en memoria del proceso (H8) | Limitación conocida (B8, v2). Mientras tanto: borrar la cuenta con `scripts/clean-dev-user.sh` y que se registre de nuevo, o sembrarla con `scripts/seed-dev-user.sh` |
| `GET /history/` responde 500 `UndefinedColumnError` | Migraciones sin aplicar | `docker compose exec backend alembic upgrade head` |
| `no space left on device` al construir | Disco de 9,3 GB casi lleno | `df -h /`, `docker image prune -f` y reintentar. Un `unmount ... device or resource busy` de containerd es transitorio: reintentar |
| El certificado del relay vence | No aplica | El de `wally.uccor.edu.ar` vence el 30/12/2026: lo renueva IT; pedirle que confirme que es automático |

**Respaldo para la defensa** si el servidor no está disponible: el despliegue local de `scripts/deploy-local.sh` en la
notebook ([despliegue-y-e2e.md](despliegue-y-e2e.md)).

## 7. Pendiente en el servidor (no se hace desde el repo)

- [x] A1: `SMTP_HOST=wally.uccor.edu.ar`; registro, mail, verificación y login probados el 30/10/2026.
- [x] D-UCC-04: la subred fija se aplicó en el servidor (`ip route` sin 172.18.0.0/16).
- [ ] Aplicar este override versionado: `git pull` del PR, `docker compose config`, `docker compose up -d`.
- [ ] A3, parte 2: nombre DNS interno y certificado (área de Seguridad de IT); `certs/`, `METIS_URL` y redespliegue con
      el override de TLS; sonda del §4.1 por HTTPS.
- [ ] B3: reinicio controlado del servidor, con IT avisado (lo gestiona Seguridad), para confirmar que todo vuelve
      solo y en orden.
- [ ] B4: `timedatectl` y NTP: el servidor marcaba una hora menos (H12). Lo gestiona IT.
- [ ] B5: cron del §5 y una restauración de prueba en el servidor.
- [ ] B6: cuentas de smoke y una corrida del §4.2.
- [ ] Seguridad: cambiar la contraseña del usuario `metis` (`passwd`), pedir a IT la rotación de la contraseña SMTP
      (se mostró en capturas durante el diagnóstico) y limpiar el historial de la terminal (`history -c; history -w`).
- [ ] Corrida formal de `sonda_metis.py` desde UCC-Free (§4.1) y guardado de la salida en
      `evidencia/despliegue-ucc-29-10-2026/`.
