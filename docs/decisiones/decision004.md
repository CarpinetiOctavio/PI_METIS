# DECISIÓN 004 — Mecanismo de envío de mail para verificación de cuenta
**Fecha:** 14 de Mayo de 2026
**Estado:** PARCIALMENTE IMPLEMENTADO — mock SMTP en desarrollo (auth/email.py), aiosmtplib pendiente de credenciales IT (cuenta metis-noreply@ucc.edu.ar + App Password)

### Contexto
Con la autenticación propia usuario/contraseña confirmada ([DECISIÓN 001](decision001.md)),
el sistema necesita verificar que el mail @ucc.edu.ar ingresado al registrarse
existe realmente. Esto requiere enviar un mail de verificación desde el servidor.
El servidor tiene acceso saliente a internet confirmado por IT (puerto 587 disponible).
Google deprecó la autenticación SMTP con usuario/contraseña simple — se requiere
uno de los dos métodos actuales.

### Opciones evaluadas

OPCIÓN A — OAuth2 con Google Cloud Console:
IT crea un proyecto en Google Cloud Console bajo el tenant de la UCC.
Se generan Client ID y Client Secret para la aplicación.
El servidor obtiene un Refresh Token y lo usa para cada envío.
Ventaja: estándar de seguridad más alto de Google actualmente.
Desventaja: requiere configuración de proyecto en Google Cloud — más complejo
para IT y para la implementación.

OPCIÓN B — App Password (contraseña de aplicación):
IT crea una cuenta emisora institucional (ej. metis-noreply@ucc.edu.ar)
con verificación en dos pasos activada.
Se genera un App Password de 16 dígitos exclusivo para el servidor.
El servidor se conecta a smtp.gmail.com:587 con esa cuenta y ese password.
Ventaja: implementación directa con aiosmtplib, sin proyectos en la nube.
Desventaja: ninguna relevante para el volumen de mails de METIS.

### Decisión tomada
Opción B — App Password. Confirmado por IT de la UCC en Mayo 2026.
IT indicó que es la opción más conveniente para este caso.

### Estado de implementación
- Parte 1 (sin credenciales): auth/email.py implementado con mock en desarrollo.
  En lugar de enviar, loggea el token de verificación en consola con comentario
  explícito de pendiente.
- Parte 2 (con credenciales): pendiente de que IT provea la cuenta emisora
  metis-noreply@ucc.edu.ar y el App Password de 16 dígitos.

### Variables de entorno cuando IT provea las credenciales
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=metis-noreply@ucc.edu.ar
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

### Librería de implementación
aiosmtplib — cliente SMTP async compatible con FastAPI.
Agregar a requirements.txt cuando se implemente Parte 2.

#### -------------- Actualizacion ---------------

### Actualización 17 de Julio de 2026
Credenciales de IT recibidas el 10 de Junio de 2026 (cuenta
`metis-noreply@ucc.edu.ar`, App Password de 16 dígitos, acceso SSH y
SMTP confirmados). La implementación de Parte 2 no se inició en ese
momento — el trabajo del core estadístico (Etapa 2, auditorías de
fidelidad y regresión) ocupó el tiempo de desarrollo hasta el cierre de
la sesión de reorganización de repo del 17/07/2026. A partir de acá,
Parte 2 (reemplazo del mock de `auth/email.py` por `aiosmtplib` con las
credenciales reales) es la rama de trabajo siguiente.

Estado pasa de "mock en desarrollo, pendiente de credenciales" a "mock
en desarrollo, credenciales en mano desde 10/06, implementación real
pendiente de iniciar."

**Ver también:** `[DECISIÓN 001](decision001.md)` — mecanismo de login (usuario/contraseña
+ JWT). Ambas decisiones son sobre autenticación pero resuelven
problemas distintos y no se reemplazan entre sí: 001 define cómo se
loguea el usuario, 004 cómo se verifica su mail al registrarse.
