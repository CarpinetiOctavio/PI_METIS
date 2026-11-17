# DECISIÓN 005 — Almacenamiento de tokens de verificación en memoria
**Fecha:** 14 de Mayo de 2026
**Estado:** ACEPTADO para V1.0 — revisión post-M5

### Contexto
Los tokens de verificación de mail se almacenan en un dict en memoria
del proceso (_pending_tokens en auth/router.py). Es simple y suficiente
para V1.0 con un solo worker en intranet.

### Limitación conocida
En producción con múltiples workers (uvicorn workers o Docker replicas),
cada worker tiene su propio dict. El token generado en worker A no lo
encuentra worker B — el usuario no puede verificar su cuenta.

### Decisión
Aceptado para V1.0 — METIS corre con un solo worker en intranet.
Solución futura (post-M5): mover tokens a tabla BD o Redis.
