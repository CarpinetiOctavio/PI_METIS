# DECISIÓN 027 — Migración Alembic `46f270df2e87` renombrada a `003` (nomenclatura, no contenido)
**Fecha:** 17 de Julio de 2026
**Estado:** APLICADA — cadena de revisiones verificada íntegra con `alembic history`

### Contexto
`001_baseline_schema.py` y `002_add_password_hash_email_verified.py` usan
`revision`/`down_revision` con IDs literales secuenciales (`"001"`, `"002"`),
escritos a mano. La tercera migración (`fix_nullability_baseline`) se generó
con `--autogenerate` (Docker activo, BD real) y Alembic le asignó un hash
automático (`46f270df2e87`) en vez de seguir la convención secuencial del
resto del proyecto — el nombre de archivo y el `revision=` interno quedaron
con ese hash, rompiendo la consistencia de nomenclatura (no la cadena en sí:
`down_revision = "002"` ya apuntaba correctamente).

### Verificación previa a aplicar el cambio
Confirmado leyendo los tres archivos antes de tocar nada:
- `001_baseline_schema.py`: `revision = "001"`, `down_revision = None`.
- `002_add_password_hash_email_verified.py`: `revision = "002"`,
  `down_revision = "001"`.
- `46f270df2e87_fix_nullability_baseline.py`: `revision = "46f270df2e87"`,
  `down_revision = "002"`.

Grep de `46f270df2e87` en todo el repo antes del rename: sin resultados —
el hash no estaba referenciado en ningún otro archivo ni migración.

### Decisión
`git mv` de `46f270df2e87_fix_nullability_baseline.py` a
`003_fix_nullability_baseline.py`, y dentro del archivo:
`revision: str = "46f270df2e87"` → `revision: str = "003"` (también
actualizado el bloque `Revision ID:` del docstring). `down_revision = "002"`
no se tocó — ya apuntaba correctamente. **Cambio puramente de nomenclatura
— cero cambio de contenido/lógica de la migración.**

### Verificación posterior
`alembic history --verbose` (con `DATABASE_URL` de override, sin necesidad
de BD real levantada) confirma la cadena íntegra:
`001 → 002 → 003 (head)`, sin huecos ni referencias rotas.

### Archivos modificados
- `backend/alembic/versions/46f270df2e87_fix_nullability_baseline.py` →
  renombrado a `backend/alembic/versions/003_fix_nullability_baseline.py`
  (contenido: solo `revision=` y docstring de cabecera, ver arriba).

----
