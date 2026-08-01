# DECISIÓN 048 — Archivado de análisis por soft-delete, no borrado físico
**Fecha:** 31 de Julio de 2026
**Estado:** Decidida — implementación en curso (Bloque E, pasada 4)

### Contexto
`docs/frontend/plan-mejora-frontend-pasada4.md` (punto 5a del feedback de UX)
pide poder sacar un análisis de la vista principal del historial. La pregunta
de arquitectura es si eso significa un `DELETE` físico o algo reversible.

### Opciones evaluadas
1. **`DELETE` físico de la fila en `analyses`** (cascada a
   `analysis_results` por `ON DELETE CASCADE`, ver `architecture.md`).
   Descartada: `constraints.md` establece que "toda decisión ante un
   warning es responsabilidad del usuario y queda registrada en el
   historial" — el historial de CU-01 es, en los hechos, el registro de
   auditoría del sistema. Un `DELETE` real destruye esa trazabilidad sin
   posibilidad de recuperación, y no hay ningún requisito que pida borrado
   real (el punto 5a del feedback pide sacar algo "de la vista", no
   destruirlo).
2. **Soft-delete vía columna `archivado_at`.** Elegida. El análisis sigue
   existiendo en la base — la vista principal del historial simplemente lo
   excluye por default. Reversible (`unarchive`), y no compromete la
   auditoría.

### Decisión
- **Migración Alembic `004_add_archivado_at_analyses.py`** — agrega
  `archivado_at TIMESTAMP NULL` a `analyses`. Nullable sin default: aditiva
  y reversible, no rompe filas existentes. Numeración `004` explícita (no
  el hash autogenerado) — mismo precedente que
  [DECISIÓN 027](decision027.md) fijó para `003`.
- **`POST /api/v1/history/{id}/archive`** y su inverso
  **`POST /api/v1/history/{id}/unarchive`** — requieren JWT, verifican
  pertenencia (`user_id`) igual que `get_analysis_by_id` ya hace.
- **`GET /api/v1/history/`** excluye archivados por default;
  `?archivados=true` los incluye.
- **No incluye búsqueda por nombre de archivo** (punto 5b del feedback) —
  fuera de alcance, requiere una migración de esquema previa
  (`nombre_archivo` no existe hoy en `analyses`) que esta pasada no cubre.

### Criterio de hecho
- `alembic upgrade head` y `alembic downgrade -1` corren limpio contra la
  BD de Docker, sin pérdida de datos existentes.
- `GET /api/v1/history/` sin `?archivados=true` no devuelve análisis
  archivados; con `?archivados=true` sí.
- `POST /api/v1/history/{id}/archive` de un análisis ajeno responde 404,
  igual que `GET /api/v1/history/{id}` ya hace hoy.
- Ningún endpoint hace `DELETE` sobre `analyses` — la fila persiste
  siempre.

**Ver también:** `architecture.md` — esquema de `analyses` y
`ON DELETE CASCADE` de `analysis_results`. [DECISIÓN 027](decision027.md)
— precedente de numeración explícita de migraciones.
