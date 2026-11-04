# Plan de mejoras post-despliegue UCC y respuestas de Facundo

Oct 29, 2026 · @Kevin y/o Joaquin

## Resumen

METIS está bien desplegado en 172.16.168.14, pero hoy no se puede defender: el registro devuelve 500 y, desde la red del campus, Etapa 2 y la pausa por atípico nunca llegan al navegador. Las dos causas están identificadas y ninguna está en el motor estadístico.

- **Registro:** el `.env` del servidor usa `SMTP_HOST=wally.ucc.edu.ar`, cuyo certificado no lo cubre. Con `wally.uccor.edu.ar` la verificación estricta y la autenticación pasan desde el contenedor. Se arregla con una línea.
- **Etapa 2:** desde adentro del servidor el ranking sale en 50 ms. Desde UCC-Free no llega ni un evento en 90 s. Algo en la red retiene cada respuesta HTTP hasta que termina, y un stream en pausa nunca termina. Se arregla con HTTPS o con una excepción de IT.
- **Respuestas de Facundo:** tres se resuelven sin tocar código (U\_T, t de Student con n impar, Mann-Kendall). La Generalizada de Pareto sale del cálculo en la v1 (decisión de Kevin, 29/10).

La evaluación se hizo con `sonda_metis.py` desde una notebook en UCC-Free y con comandos por SSH en el servidor (`metis@ingpi`).

## Hallazgos de la evaluación

De 13 hallazgos, dos son críticos y bloquean la defensa (H1 y H2). Los marcados "a confirmar" salen de leer el repo y falta verlos en el servidor.

| ID | Hallazgo | Evidencia | Causa | Severidad | Bloque |
| --- | --- | --- | --- | --- | --- |
| H1 | El registro devuelve 500 | Log: `SSLCertVerificationError`, hostname mismatch para `wally.ucc.edu.ar` | Configuración: `SMTP_HOST` es el nombre de la comunicación de IT, no el corregido en la DECISIÓN 034 | Crítica | A1 |
| H2 | Etapa 2 y la pausa por atípico no llegan desde UCC-Free | Interno: ranking en 50 ms por nginx y directo al backend. Externo: 0 eventos en 90 s, `/ping` normal | Red del campus: retiene cada respuesta HTTP hasta que termina | Crítica | A3 |
| H3 | Un error de TLS en el envío sale como 500 genérico, sin código | Traceback crudo de `ssl.SSLCertVerificationError` en `auth/router.py:67` | Código: el `except` atrapa `SMTPException` y `RuntimeError`, no `ssl.SSLError` | Alta | A2 |
| H4 | Sin HTTPS: contraseña y cookie de sesión viajan en claro por un wifi abierto | Puerto 443 cerrado; solo escucha el 80 | Infraestructura: nginx sin certificado | Alta | A3 |
| H5 | Tras un reinicio del servidor, METIS no vuelve a levantar | Ningún servicio de `docker-compose.yml` tiene `restart:` (a confirmar) | Configuración del compose | Alta | B3 |
| H6 | La cookie de sesión sale sin `Secure` | `ENV=development` en el backend | Consecuencia de H4: con `Secure` sobre HTTP el login quedaría muerto | Media | A3 |
| H7 | Sin cabeceras de seguridad y nginx expone su versión | `Server: nginx/1.31.8`; faltan `X-Content-Type-Options`, `X-Frame-Options`, CSP, `Referrer-Policy` | nginx sin endurecer | Media | B1 |
| H8 | Un reinicio del backend deja cuentas sin verificar y sin forma de reenviar el mail | Tokens en `_pending_tokens` (memoria); re-registrarse da `AUTH_EMAIL_ALREADY_REGISTERED` | Diseño: limitación documentada en `auth/router.py` | Media | B5 |
| H9 | Sin respaldo de la base | Sin cron de `pg_dump` (a confirmar) | Operación | Media | B6 |
| H10 | Login y registro sin límite de intentos | Código de `auth/router.py` | Diseño | Media | v2 |
| H11 | El bundle de 447 KB sale sin compresión ni caché | Sin `Content-Encoding`, sin `Cache-Control` | `gzip` comentado en el nginx desplegado | Baja | B2 |
| H12 | El reloj del servidor atrasa una hora | El servidor marcó 16:41 a las 17:41 de Córdoba | Zona horaria o NTP del host | Baja | B4 |
| H13 | Un archivo de 11 MB corta la conexión en vez de mostrar el error | `IncompleteRead` en la sonda: nginx cierra durante la subida | Comportamiento de nginx con el 413 (a verificar desde la interfaz) | Baja | B2 |

Verificado sin problemas: PostgreSQL, el backend directo y Mailpit no se ven desde la red; las migraciones están aplicadas; recargar en `/config` y abrir `/auth/verify` sirven la SPA; `/ping` responde en 30 ms de mediana; Etapa 1 completa en 0,04 s.

## Bloque A: urgente, antes de la defensa

A1 y A2 se resuelven en el día; A3 depende de IT y es el único punto con riesgo de llegar tarde, por eso tiene un plan de respaldo.

### A1. Corregir el SMTP en el servidor (H1)

1. En el directorio del compose del servidor, cambiar en `.env` la línea `SMTP_HOST=wally.ucc.edu.ar` por `SMTP_HOST=wally.uccor.edu.ar`.
2. Recrear el backend con `docker compose up -d backend`. Un `restart` no relee el `env_file`.
3. Verificar de punta a punta con una casilla real `@ucc.edu.ar`: registro 201, llega el mail, el link verifica, el login entra.
4. Agregar un addendum a la DECISIÓN 034 con lo que se verificó hoy desde adentro: los dos nombres resuelven a 172.16.66.113 (DNS split-horizon), el certificado es solo para `wally.uccor.edu.ar` y vence el 30/12/2026. Cierra los pendientes 1 a 3 de `sprint.md`.

**Hecho:** una cuenta creada y verificada desde UCC-Free, y el addendum mergeado.

### A2. Atrapar los errores de TLS del envío (H3)

1. En `auth/router.py::register`, ampliar el `except` a `(aiosmtplib.SMTPException, ssl.SSLError, OSError, RuntimeError)`. `OSError` cubre también timeouts y conexiones rechazadas que no lleguen envueltas.
2. Test de regresión en `tests/unit/auth/test_router_register.py`: `aiosmtplib.send` con `side_effect=ssl.SSLCertVerificationError(...)` tiene que devolver 500 con `AUTH_VERIFICATION_EMAIL_FAILED` y no persistir el usuario.
3. Correr el test en el commit previo (rojo) y en el del arreglo (verde), y guardar las dos corridas.

**Hecho:** PR mergeado con el test en verde y la evidencia rojo/verde guardada.

### A3. Que Etapa 2 llegue desde la red del campus (H2, H4, H6)

HTTPS es la solución de fondo: un firewall no puede retener por contenido lo que no puede leer, y además cifra la contraseña y la cookie.

1. **Pedido a IT (hoy).** Dos cosas en el mismo mensaje, con la evidencia de H2: que excluyan 172.16.168.14 de la inspección HTTP, y un nombre DNS interno para METIS con su certificado (o el de la CA interna de la UCC).
2. **Compose del despliegue UCC versionado.** Un override `docker-compose.ucc.yml`, sin secretos, con `restart: unless-stopped`, el 443 publicado, el certificado montado de solo lectura, `ENV=production` y `FRONTEND_ORIGIN`/`FRONTEND_URL` con `https://` y el nombre nuevo. Se registra como DECISIÓN 083 (despliegue en la UCC).
3. **nginx con TLS.** Un `server` en 443 con el certificado, el 80 redirigiendo a 443 y las mismas `location` de hoy, `proxy_buffering off` incluido. HSTS recién cuando el certificado esté estable.
4. **Verificación.** `sonda_metis.py --base https://<nombre>` desde UCC-Free: Etapa 1+2 hasta el ranking, la pausa por atípico con `serie_con_atipico.csv`, cookie con `Secure`.

Si el firewall descifrara TLS (solo pasa si los equipos confían en su CA), el síntoma seguiría igual. La verificación del paso 4 lo descarta.

**Respaldo si IT no llega a tiempo:** defender con el despliegue local de `scripts/deploy-local.sh` en la notebook, que ya es el procedimiento de la demo del TP de Calidad. La corrección de fondo en el código (cerrar el stream en cada pausa y que la decisión devuelva la continuación) queda para la v2: es un cambio grande en el contrato SSE.

**Hecho:** desde UCC-Free, una corrida con Etapa 1 y 2 llega a "Elegí una distribución" y el modal de atípico aparece.

## Bloque B: endurecimiento del despliegue

Ninguno bloquea la defensa, pero B1 a B3 son baratos y el tribunal los puede preguntar. Todo cambio de nginx va en `nginx/nginx.conf` del repo, para que viaje con el despliegue y no quede solo en el servidor.

| ID | Qué | Dónde | Esfuerzo | Para |
| --- | --- | --- | --- | --- |
| B1 | `server_tokens off`; `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`; CSP primero en modo `Report-Only` para no romper el chunk de KaTeX | `nginx/nginx.conf` | 1 h | v1 |
| B2 | `gzip on` para HTML, JS, CSS y JSON, **sin** `text/event-stream` (comprimir el SSE lo bufferiza); `/assets/` con `Cache-Control: immutable` de un año e `index.html` con `no-cache`. Validar el tamaño del archivo en el frontend antes de subirlo y subir `client_max_body_size` a 11m, para que el usuario vea `PARSE_FILE_TOO_LARGE` y no un error de red (H13) | `nginx/nginx.conf`, `ConfigPage.tsx` | 2 h | v1 |
| B3 | Reinicio controlado del servidor, con IT avisado, para confirmar que `restart: unless-stopped` de A3 levanta todo solo y en orden (H5) | Servidor | 30 min | v1 |
| B4 | Zona horaria `America/Argentina/Cordoba` y NTP activo con `timedatectl`, o pedirlo a IT si el host lo administran ellos (H12) | Servidor | 15 min | v1 |
| B5 | Respaldo diario con `pg_dump` desde cron, retención de 7 días y una restauración de prueba documentada (H9) | Servidor | 1 h | v1 |
| B6 | Smoke del repo contra el servidor tras cada redespliegue: `pytest -m smoke` dentro del contenedor del backend con `SMOKE_BASE_URL` apuntando a nginx y una cuenta de smoke propia | Servidor, `tests/smoke/` | 1 h | v1 |
| B7 | Runbook del despliegue UCC: cómo se levanta, `.env` esperado sin secretos, comandos de verificación (sonda, smoke, SMTP) y contingencias. Alimenta `contingencia.md` del TP | `docs/calidad/despliegue-ucc.md` | 2 h | v1 |
| B8 | Tokens de verificación en la base (hash y vencimiento) y endpoint para reenviar el mail (H8) | `auth/`, migración 007 | 4 h | v1 si sobra tiempo; si no, v2 con el riesgo documentado |
| B9 | Límite de intentos en login y registro (H10) | nginx `limit_req` o backend | 2 h | v2 |

## Bloque C: respuestas de Facundo del 29/10

Tres de las cuatro respuestas confirman lo que METIS ya hace y solo piden documentación; la cuarta saca la Generalizada de Pareto de la v1.

| Consulta | Respuesta | ¿Cambia el código? | Qué hay que hacer |
| --- | --- | --- | --- |
| C1. U\_T con F > 0,5 | Se mantiene IV-105 (1 − F). Lo más probable es que la planilla tenga un error por arrastre de ecuaciones | No | Cerrar `hallazgo-ut-planilla-causa-c.md` con la respuesta. En el libro, atribuir a la planilla las diferencias de cuantiles y EEA en Normal, Log-Normal, Gamma y Log-Pearson III, y los cambios de orden del ranking en las estaciones 5 y 8 |
| C2. t de Student con n impar | Es indistinto: el subgrupo más grande puede ser el primero o el segundo | No | Registrar la convención de METIS (dato del medio al segundo subgrupo) como decisión, igual que la partición de Cramer, y fijarla con un test de n = 39 → 19 + 20. Documentar que en la estación 5 METIS acepta (t = 1,817) y la tesis rechaza (t = 2,082) |
| C3. Mann-Kendall, colas | Dos colas | No | Documentar la diferencia con la Tabla A.4 de Caamaño (1,64 al 5 % es una cola) y el caso de la estación 2 (Z = 1,662: con 1,96 no detecta tendencia) |
| C4. Generalizada de Pareto | No la recuerda; puede quedar fuera de la librería hasta conseguir mejor bibliografía | Sí | Sacarla del cálculo en la v1 (decisión de Kevin, 29/10). Detalle abajo |

### C4. Sacar la Generalizada de Pareto de la v1

El módulo `gen_pareto.py` y sus tests quedan en el repo para la v2; lo que cambia es que el pipeline deja de ajustarla.

1. **Addendum a la DECISIÓN 074.** La 074 había descartado ocultarla por trazabilidad; con la respuesta de Facundo se elige esa alternativa. La v2 la reincorpora con Hosking y Wallis (1987) verificado en `Bibliografia/`.
2. **`core/`.** Un `EXCLUIDAS_V1 = frozenset({"gen_pareto"})` en `core/etapa2/distributions/__init__.py`, y `ejecutar_etapa2` saltea esos nombres: el ranking pasa a 12 distribuciones.
3. **Borde de la API.** `distribution-decision`, `simulate-exclusion` y `design-events` rechazan `gen_pareto` con un código propio y registrado en el catálogo de errores, en lugar del rechazo por pendiente de validación.
4. **Historial.** Los análisis ya guardados traen a Pareto en su ranking. El frontend y el PDF tienen que seguir mostrándolos como "pendiente de validación", así que esa rama de `Etapa2RankingView.tsx` y de `reportes/pdf.py` se queda para datos viejos.
5. **Tests.** Actualizar los que cuentan 13 distribuciones o esperan a Pareto en el ranking, y agregar uno que afirme que no aparece.
6. **Documentación.** "13 distribuciones" figura en 53 archivos del repo (docs, reglas de `.claude/` y código). Barrido con `grep`, distinguiendo la tesis (13) de METIS v1 (12). Lo mismo en el libro.

**Hecho:** el stream y el PDF muestran 12 distribuciones, un análisis viejo del historial con Pareto se sigue viendo bien, y la 074 tiene su addendum.

## Orden de ejecución

A1 se hace hoy y destraba el registro; todo lo que depende de IT se prepara antes, para que la llegada del certificado sea solo un merge y un redespliegue.

&#91;embedded content: orden de ejecución · 4 frentes, 1 verificación final\]

Los PRs de esta semana no esperan a IT. El de nginx con TLS queda listo y se mergea cuando llega el certificado; los PRs A2 y C4 tienen que estar en `staging` antes del redespliegue.

Criterio de hecho del plan completo:

- [ ] Una cuenta nueva se registra, verifica e inicia sesión desde UCC-Free
- [ ] Una corrida con Etapa 1 y 2 llega a "Elegí una distribución" desde UCC-Free
- [ ] El modal de atípico aparece con `serie_con_atipico.csv` desde UCC-Free
- [ ] `sonda_metis.py` sin FALLA ni RIESGO en HTTPS, cabeceras y puertos
- [ ] El ranking muestra 12 distribuciones y el historial viejo con Pareto se sigue viendo
- [ ] El servidor vuelve solo después de un reinicio y hay un respaldo restaurado de prueba

## Trazabilidad: defectos, decisiones y evidencia

Los tres defectos de esta evaluación no los podía detectar ni el CI ni el despliegue efímero: aparecen solo con la red, el DNS y el relay reales de la UCC. Es el argumento para el libro de por qué el despliegue real es un nivel de prueba propio.

| Defecto | Hallazgo | Tipo | Detectado por | Test de regresión |
| --- | --- | --- | --- | --- |
| D-UCC-01 | H1, `SMTP_HOST` incorrecto | Configuración | Sonda + logs por SSH | No aplica; lo cubre el runbook (B7) y la verificación SMTP |
| D-UCC-02 | H3, error de TLS sin código de contrato | Código | Logs por SSH | Sí, A2, con evidencia rojo/verde |
| D-UCC-03 | H2, la red retiene el stream en pausa | Infraestructura | Sonda externa contra curl interno | Verificación de la sonda en HTTPS (A3, paso 4) |

Cada uno va como issue con la plantilla de defecto, enlazado a su PR.

Decisiones a registrar:

- **DECISIÓN 083:** despliegue en la UCC, con HTTPS, `docker-compose.ucc.yml` y el diagnóstico de D-UCC-03 como contexto.
- **DECISIÓN 084:** partición de t de Student con n impar (respuesta C2).
- **Addendum a la 034:** hostname interno verificado y DNS split-horizon.
- **Addendum a la 074:** Generalizada de Pareto fuera de la v1 (respuesta C4).

Evidencia a guardar en `docs/calidad/evidencia/despliegue-ucc-29-10-2026/`, antes de que se pierda: las tres salidas de la sonda, las capturas del curl interno y de los logs, y la prueba SMTP con verificación estricta.

## Estado al 02/11/2026

La versión 1 de METIS se da por cerrada. El despliegue en intranet es un agregado del trabajo de investigación y no
bloquea la presentación del proyecto integrador. Lo que sigue abierto depende de IT o es de la versión 2.

El estado de arriba (casillas del criterio de hecho, bloques A a C) refleja el plan tal como se escribió el 29/10. Esta
sección es el estado real. Los PRs figuran como "en rama" hasta que se pushean y se mergean.

| Punto | Estado | Dónde |
| --- | --- | --- |
| A1. SMTP del servidor | Hecho el 30/10. Registro, mail, verificación y login funcionan desde la red de IT | Configuración del servidor; addendum a la DECISIÓN 034 |
| A2. Errores de TLS del envío | Hecho, con timeout de 20 s. Evidencia rojo/verde guardada | Rama `fix/register-error-tls` |
| A3. HTTP: reinicio automático, subred propia, SMTP, mailpit apagado | Hecho y probado en el servidor. Se agregó un defecto que el plan no tenía: la red de Docker (172.18.0.0/16) pisaba el gateway de la ruta de IT (D-23) | `docker-compose.ucc.yml`, DECISIÓN 083 parte 1 |
| A3. HTTPS, nombre DNS y certificado | Cambió el esquema el 04/11: el sitio está detrás de Cloudflare y IT pidió HTTPS autofirmado en un puerto nuevo. Implementado en la rama `deploy/ucc` (archivo adicional `docker-compose.ucc-tls.yml`). IT respondió el 04/11 (URL `https://metis.ucc.edu.ar`, puerto 4443, `X-Real-IP`, tope de 100 s con latido, sin límite de mails). **Falta que IT repunte el proxy** y el rango del proxy para `real_ip` | DECISIÓN 083, addendum del 04/11/2026 |
| B1, B2. Cabeceras, gzip sin SSE, caché, tope de subida | Hecho | Rama `feature/nginx-endurecimiento` |
| B3. Reinicio controlado | **Depende de IT** | |
| B4. Zona horaria y NTP | **Depende de IT** | |
| B5. Respaldo diario | Script hecho (`scripts/respaldo-db.sh`). Falta instalarlo en cron en la VM y probar la restauración | Runbook, sección de respaldo |
| B6. Smoke en el servidor | Se corre a mano en la VM tras cada redespliegue. Falta la primera corrida | Runbook |
| B7. Runbook | Hecho | `docs/calidad/despliegue-ucc.md` |
| B8. Tokens de verificación en la base y reenvío del mail | Parcial. La migración 007 crea `auth_tokens` con un campo `purpose` pensado para esto, y la recuperación de contraseña destraba las cuentas sin verificar. Falta mover el token de verificación y el endpoint de reenvío: versión 2 | DECISIÓN 085 |
| B9. Límite de intentos | Versión 2: `limit_req` de nginx sobre `/api/v1/auth/` | |
| C1 a C3. Respuestas de Facundo | Hecho | DECISIÓN 084 y documentación |
| C4. Generalizada de Pareto fuera de la v1 | Hecho, incluido el barrido de "13 distribuciones" en los documentos vivos | Addendum a la DECISIÓN 074 |
| Recuperación de contraseña | **No estaba en el plan.** Se detectó probando en el servidor el 02/11/2026 | DECISIÓN 085 |

Criterio de hecho del plan completo:

- [x] Una cuenta nueva se registra, verifica e inicia sesión desde la red de IT (30/10)
- [x] Una corrida con Etapa 1 y 2 llega a "Elegí una distribución" (30/10, con la excepción de inspección que dio IT)
- [x] El ranking muestra 12 distribuciones y el historial viejo con Pareto se sigue viendo
- [ ] El modal de atípico aparece con `serie_con_atipico.csv` desde UCC-Free: sin verificar en esta tanda
- [ ] `sonda_metis.py` sin FALLA ni RIESGO en HTTPS: depende de desplegar el TLS y de que IT repunte el proxy
- [ ] El servidor vuelve solo después de un reinicio y hay un respaldo restaurado de prueba: depende de IT (reinicio) y de B5
