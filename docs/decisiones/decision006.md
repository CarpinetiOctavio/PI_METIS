# DECISIÓN 006 — Regla de nullability en migraciones Alembic + SQLAlchemy
**Fecha:** 15 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar en todas las migraciones futuras

### Contexto
La migración 001 fue escrita manualmente porque Docker no estaba activo al
momento de implementar feature/auth-refactor. Al escribirla manualmente se
usó `nullable=True` para columnas con `server_default` o FK opcionales, sin
considerar cómo SQLAlchemy infiere la nullability a partir del tipo de la
columna en `Mapped[T]`.

Al levantar Docker y correr `alembic check`, se detectaron 9 columnas donde
el esquema de la BD (nullable=True) divergía de lo que los modelos declaraban
(NOT NULL). Se generó la migración 003 con `--autogenerate` para corregirlo.

### La regla

SQLAlchemy con `Mapped[T]` infiere la nullability directamente del tipo Python:

```python
# NOT NULL en la BD — T no es Optional
nombre: Mapped[str] = mapped_column(String(255))
created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
activo: Mapped[bool] = mapped_column(Boolean, default=True)

# NULLABLE en la BD — T es Optional (con | None o Optional[T])
nombre: Mapped[str | None] = mapped_column(String(255))
last_login: Mapped[datetime | None] = mapped_column(DateTime)
```

Tener un `server_default` o `default` NO implica nullable. El default garantiza
que la BD siempre tendrá un valor, pero la columna sigue siendo NOT NULL.
El nullable lo determina únicamente si T es Optional o no.

### Por qué importa para migraciones manuales
Cuando se escribe una migración a mano, `nullable` debe coincidir con lo que
el modelo SQLAlchemy declara. Si se escribe `nullable=True` para una columna
cuyo modelo usa `Mapped[T]` (sin Optional), `alembic check` fallará y la BD
tendrá constraints incorrectas.

### Proceso correcto para migraciones futuras

**Con Docker activo (caso normal):**
```bash
# 1. Cambiar el modelo SQLAlchemy
# 2. Generar la migración con autogenerate — Alembic lee los modelos y la BD
alembic revision --autogenerate -m "descripcion_del_cambio"
# 3. Revisar el archivo generado antes de aplicar
# 4. Aplicar
alembic upgrade head
# 5. Verificar que no queden diferencias
alembic check
```

**Sin Docker activo (caso excepcional):**
Escribir la migración manualmente prestando atención a la regla de nullability.
Marcar el archivo con el comentario "generada manualmente — verificar con
`alembic check` cuando Docker esté disponible". Al levantar Docker, correr
`alembic check` inmediatamente y generar una migración correctiva si hay
divergencias (como sucedió con la migración 003).

### Columnas corregidas en migración 003
Las siguientes columnas estaban definidas como nullable=True en la BD (por
error en migración 001) y se corrigieron a NOT NULL mediante la migración 003:

- `analyses.user_id` — FK obligatoria (analyses solo se persisten en CU-01)
- `analyses.created_at` — timestamp con server_default=now()
- `analysis_results.analysis_id` — FK obligatoria al análisis padre
- `api_clients.auto_clean` — boolean con default=False
- `api_clients.report_frequency` — integer con default=1
- `api_clients.cramer_particion` — varchar con default='default'
- `api_clients.created_at` — timestamp con server_default=now()
- `api_clients.activo` — boolean con default=True
- `users.created_at` — timestamp con server_default=now()
