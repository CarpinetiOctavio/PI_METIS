# DECISIÓN 003 — Gestión de migraciones de esquema: Alembic
**Fecha:** 14 de Mayo de 2026
**Estado:** PARCIALMENTE IMPLEMENTADO — Alembic configurado y migraciones generadas. Pendiente: ejecutar contra BD activa cuando Docker esté disponible

### Contexto
Al implementar feature/auth-refactor, la tabla users requiere dos columnas
nuevas (password_hash, email_verified — ver [DECISIÓN 002](decision002.md)). La tabla ya existe
en PostgreSQL con el esquema original. SQLAlchemy no modifica tablas existentes
automáticamente — hay que decirle explícitamente a PostgreSQL qué cambió.

### Opciones evaluadas

OPCIÓN DESCARTADA — Dropear y recrear la tabla:
Funciona cuando no hay datos reales. Pero es una solución manual sin memoria:
cada cambio de esquema futuro requiere recordar qué se hizo antes, aplicarlo
a mano en cada entorno, y coordinar con Kevin. En producción con datos reales
de docentes y alumnos, esta opción no existe. Introducirla ahora crearía una
deuda técnica que se pagaría cara más adelante.

OPCIÓN ELEGIDA — Alembic:
Sistema de migraciones estándar para SQLAlchemy. Cada cambio de esquema genera
un script versionado que describe exactamente qué cambió. Alembic mantiene
registro de qué migraciones están aplicadas en cada entorno y aplica solo las
que faltan. Es el equivalente a Git pero para la base de datos — trazabilidad
completa del historial de esquema.

### Por qué Alembic aunque no haya datos todavía
No es por los datos — es por el proceso. Este es el proceso correcto que se
va a usar en producción, y establecerlo ahora tiene costo bajo. Si se dropea
ahora, cuando llegue producción con datos reales hay que introducir Alembic
de todas formas, pero sobre una base que nunca lo usó y con migraciones que
reconstruir desde cero. Hacerlo ahora, sin presión, con un esquema simple,
es el momento correcto.

### Justificación ante tribunal de ISI
"Usamos Alembic para gestionar cambios de esquema" es una respuesta técnica
sólida con justificación clara. Cada migración es un archivo versionado con
ID único y descripción — historial completo de cómo evolucionó el esquema.

### Lo que se implementa
Paso 0 de feature/auth-refactor:
- alembic init en backend/
- Configurar alembic.ini y env.py para usar los modelos de METIS
- Migración 001: esquema inicial (tablas existentes)
- Migración 002: agregar password_hash y email_verified a users

Todas las migraciones futuras siguen el mismo patrón:
cambiar el modelo → alembic revision --autogenerate → alembic upgrade head
