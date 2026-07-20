# DECISIÓN 034 — Correcciones de configuración SMTP encontradas en smoke test real: hostname y separación de identidad de remitente
**Fecha:** 20 de Julio de 2026
**Estado:** IMPLEMENTADO — verificado con envío real a casilla confirmada

### Contexto
Al ejecutar el smoke test manual de [DECISIÓN 032](decision032.md) contra el relay real de la UCC (no mockeado, ver DECISIÓN 004, todavía pendiente de actualización formal sobre el mecanismo — esperando confirmación escrita de IT), aparecieron dos bugs de configuración que ningún test mockeado podía haber detectado, porque ambos dependen del comportamiento real del relay y de la entrega efectiva a un destinatario real.

---

### Bug 1 — Hostname SMTP no coincide con el certificado real

**Síntoma:** `ssl.SSLCertVerificationError: Hostname mismatch, certificate is not valid for 'wally.ucc.edu.ar'`. La conexión TCP y el handshake TLS avanzaban, pero `aiosmtplib` — a diferencia de una verificación manual con `openssl s_client` sin la opción de validación de hostname, que no detectó el problema en una prueba de alcanzabilidad previa — sí valida estrictamente que el hostname de conexión coincida con el CN del certificado, como corresponde a cualquier cliente TLS serio.

**Diagnóstico:** el hostname literal que compartió IT por Bitwarden (`wally.ucc.edu.ar`) no es el mismo que el CN real del certificado del servidor (`wally.uccor.edu.ar`). Confirmado que es el mismo servidor físico, no dos servidores distintos: `nslookup wally.uccor.edu.ar` resuelve a `200.45.112.13`, la misma IP contra la que ya se había validado el handshake TLS completo (certificado Let's Encrypt vigente, cadena de confianza válida) usando el hostname incorrecto.

**Alternativas evaluadas:**
- Deshabilitar la verificación de certificado en `aiosmtplib` para que `wally.ucc.edu.ar` conecte igual: descartado de plano. Elimina la protección contra ataques de intermediario sin que el cliente pueda detectarlo — inaceptable en un sistema que maneja una credencial institucional real, más aún de cara a la defensa ante el tribunal.
- Escalar a IT para que corrijan el hostname público o reemitan el certificado con el nombre correcto: descartado por ahora — el problema es resoluble sin intervención de terceros (usar el hostname que ya coincide con el certificado real), consistente con el criterio de agotar lo verificable antes de escalar.
- Usar el hostname que coincide con el certificado real (`wally.uccor.edu.ar`): elegida. Verificado contra la misma IP ya validada, sin ambigüedad.

**Implementación:** `SMTP_HOST=wally.uccor.edu.ar` en `.env`.

#### Verificación adicional de seguridad — antes de considerar el bug cerrado

**Duda planteada:** IT compartió el hostname `wally.ucc.edu.ar` de forma explícita y textual, tanto en la comunicación de Bitwarden como en el mail de confirmación de Ezequiel. Que el certificado real presentado por el servidor correspondiera a un nombre distinto (`wally.uccor.edu.ar`) generó una duda legítima antes de dar el fix por cerrado: ¿el nombre corregido correspondía al mismo destino autorizado por IT, o existía el riesgo de estar conectando (con las mismas credenciales reales) a una infraestructura distinta, privada o más sensible, no comprendida en lo que IT había habilitado?

**Verificación 1 — ambas IPs de `wally.ucc.edu.ar` presentan el mismo certificado único.** `wally.ucc.edu.ar` resuelve por DNS a dos IPs (`190.3.95.77` y `200.45.112.13`). Se verificó el certificado TLS ofrecido por cada una por separado, mediante `openssl s_client` con SNI explícito al hostname literal (`-servername wally.ucc.edu.ar`) — no sólo la primera IP alcanzada por casualidad. Las dos presentan el certificado idéntico: mismo número de serie, mismo CN (`wally.uccor.edu.ar`), mismas fechas de validez. No existe, en ningún punto de la infraestructura a la que DNS dirige ese hostname, un certificado emitido para el nombre literal `ucc`. Descarta la hipótesis de que una de las dos IPs fuera un servidor con identidad propia para el nombre dado por IT — es el mismo servicio (probablemente redundado/balanceado) respondiendo con una única identidad real en los dos casos.

**Verificación 2 — `uccor.edu.ar` confirmado como dominio institucional real de la UCC, por fuentes públicas independientes.** Sin depender de nada dicho por IT ni de nada documentado en este proyecto: la página institucional de Facebook de la Universidad Católica de Córdoba lista `info@uccor.edu.ar` como contacto oficial junto con `ucc.edu.ar`; el directorio de la Asociación Internacional de Universidades Jesuitas (IAJU) registra `www.uccor.edu.ar` como sitio web de la institución; y el contenido de `https://www.uccor.edu.ar/home/`, verificado en vivo, es el sitio real de la universidad — no una página ajena ni un placeholder. El uso conjunto de ambos dominios está documentado públicamente desde al menos 2016 (directorio de organismos, referencia indexada).

**Conclusión:** el alcance de acceso y las credenciales que dio IT no cambian — `wally.uccor.edu.ar` es el mismo destino físico, mismo puerto, mismas credenciales, sólo con el nombre técnico correcto en vez del nombre público que circuló de palabra. No hay evidencia de estar accediendo a infraestructura distinta, más sensible, o no autorizada.

**Pendiente de cortesía, no bloqueante:** informar a IT que el hostname que figura en su comunicación de Bitwarden (`wally.ucc.edu.ar`) no coincide con la identidad de certificado de ningún servidor al que ese nombre resuelve — inconsistencia de su propia documentación interna, útil que la conozcan aunque no bloquee nada de este lado.

**Nota para cuando se actualice DECISIÓN 004:** el mecanismo confirmado por IT usa `wally.uccor.edu.ar`, no el literal `wally.ucc.edu.ar` que aparece en la comunicación de Bitwarden — vale la pena que la actualización de esa decisión lo aclare explícitamente, para que nadie repita el mismo error de conexión leyendo sólo el mail de IT.

---

### Bug 2 — Identidad de autenticación usada como identidad de remitente, mail perdido silenciosamente

**Síntoma:** `POST /register` devolvía `201` sin ninguna excepción, `aiosmtplib.send()` retornaba éxito, pero el mail nunca llegaba a la casilla real de destino — ni bandeja de entrada, ni spam, sin ningún rebote (`mailer-daemon`).

**Diagnóstico:** obtenido instrumentando manualmente `SMTP.execute_command()` de `aiosmtplib` para capturar el transcript crudo de la conversación SMTP (`EHLO`, `AUTH`, `MAIL FROM`, `RCPT TO`, `DATA`). El relay aceptaba el mensaje de punta a punta con códigos de éxito en cada paso, incluida la cola final (`2.0.0 Ok: queued as ...`) — el problema no estaba en la conexión, la autenticación, ni en ningún rechazo explícito del relay. La causa real: `email.py` armaba `message["From"] = _SMTP_USER`, y `_SMTP_USER` es `metis` — la identidad de autenticación contra el relay, un nombre de usuario sin dominio, no una dirección de mail válida. El envelope sender quedaba como `MAIL FROM:<metis>`, sin dominio.

**Hipótesis de causa raíz, no confirmada de forma exhaustiva pero consistente con toda la evidencia disponible:** un remitente sin dominio no tiene registro SPF que validar — el sistema de correo de destino (Google Workspace, per DECISIÓN 001) probablemente descarta el mensaje antes de la bandeja, sin generar rebote. Consistente con la ausencia total de rastro del mail en cualquier carpeta.

**Alternativas evaluadas:**
- Exigir que `SMTP_USER` sea siempre una dirección de mail válida en cualquier entorno: descartado. Acopla dos conceptos distintos — la identidad de login contra el relay y la identidad de remitente del mensaje — que en este mecanismo real (usuario de servicio `metis` sobre relay institucional) no son la misma cosa, a diferencia del mecanismo originalmente anticipado en DECISIÓN 004 (donde `SMTP_USER` iba a ser directamente `metis-noreply@ucc.edu.ar`, una cuenta de Gmail).
- Separar la identidad de autenticación de la identidad del remitente con una variable nueva: elegida. `SMTP_FROM_ADDRESS`, con el mismo patrón de guard ya existente para `SMTP_HOST`/`USER`/`PASSWORD` — `RuntimeError` explícito si falta, sin default silencioso.

**Implementación:** `email.py` usa `message["From"] = _SMTP_FROM_ADDRESS`, variable nueva leída de entorno. `SMTP_FROM_ADDRESS=metis-noreply@ucc.edu.ar` en `.env`/`.env.example`.

**Verificación:** confirmado en tres rondas del script de diagnóstico — remitente sin dominio (`metis`): aceptado por el relay, nunca entregado, confirmado por revisión directa de la casilla real. Con `SMTP_FROM_ADDRESS` separado: aceptado por el relay y, en la ronda final contra una casilla real confirmada (`2200631@ucc.edu.ar`), efectivamente entregado — mail recibido, token real extraído, ciclo `register` → `verify` → `login` → `me` completado de punta a punta.

**Riesgo residual, no bloqueante:** no se descarta que el relay tenga alguna política de autorización de remitente (que el usuario autenticado `metis` sólo pueda mandar como ciertas direcciones habilitadas) — no se topó con ningún rechazo en las pruebas realizadas, pero tampoco se probó deliberadamente con remitentes no autorizados para confirmar ese límite. El remitente elegido (`metis-noreply@ucc.edu.ar`) es el que ya estaba anticipado desde el diseño original y funcionó sin objeciones — no hay indicio de que sea un problema, sólo no está descartado con certeza absoluta.

**RESUELTO — 20/07/2026:** `tests/unit/auth/test_email.py` sí dependía de `message["From"] == SMTP_USER` en `_set_config()` — la suite estuvo rota desde la separación de `SMTP_FROM_ADDRESS` hasta este momento, sin que nadie la hubiera vuelto a correr en el medio (3 de 4 tests fallaban con `RuntimeError` antes de comparar nada). Corregido: `_set_config` ahora setea `SMTP_FROM_ADDRESS` con default distinto de `SMTP_USER` (`"metis-noreply@ucc.edu.ar"` vs `"metis"`), y se sumó `test_send_verification_email_from_es_independiente_de_smtp_user` (valores centinela deliberadamente distintos) más `test_send_verification_email_sin_from_address_lanza_runtimeerror_sin_llamar_aiosmtplib` (guard de `SMTP_FROM_ADDRESS` faltante, no cubierto antes). Suite de auth: 12/12 en verde. Suite completa del repo: 132 tests, 1 failure preexistente sin relación (gen_pareto MC, ver Fase 3 de auditoría), sin regresiones fuera de este alcance.

**Ver también:** [DECISIÓN 004](decision004.md) — mecanismo de envío, pendiente de actualización con el hostname correcto. [DECISIÓN 032](decision032.md) — orden de operaciones, ahora verificado con evidencia real, no sólo mockeada.