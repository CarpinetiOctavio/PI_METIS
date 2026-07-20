# DECISIÓN 007 — DATABASE_URL dual-ambiente y convenciones de entorno de desarrollo
**Fecha:** 15 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar siempre

### Problema
El mismo `.env` es leído por el backend (dentro de Docker) y por herramientas
del host (Alembic, psql). Pero el host de PostgreSQL es distinto en cada caso:

- Dentro de Docker: `postgres` (nombre del servicio en la red Docker interna)
- Desde el host: `localhost` (puerto 5432 mapeado via `ports: ["5432:5432"]`)

Usar `localhost` en el `.env` rompe el backend. Usar `postgres` en el `.env`
rompe Alembic desde el host. Descubierto durante el smoke test de auth-refactor.

### Decisión

**El `.env` siempre tiene `postgres` como host** — es el valor correcto para el
runtime principal. Nunca cambiar el `.env` a `localhost`.

**Las herramientas desde el host sobreescriben `DATABASE_URL` en la línea de
comando** sin tocar el `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/metis alembic upgrade head
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/metis alembic check
```

El override solo existe en la sesión de terminal. No se commitea.

### Por qué no usar dos archivos .env distintos
Agregar `.env.docker` y `.env.host` introduce fricción: hay que recordar cuál
usar en cada contexto y mantenerlos sincronizados. El override en línea de
comando es más explícito y no requiere mantenimiento adicional.

### Cómo afecta a nuevos colaboradores
Al clonar el repo y seguir `.env.example`, el valor por defecto es `postgres`.
El smoke test del backend dentro de Docker funciona inmediatamente.
Para Alembic desde el host, el override está documentado en `.env.example`,
`architecture.md` y aquí.
