"""Fixtures de integración contra PostgreSQL real (B3 del plan del TP de Calidad).

Estos tests necesitan una base con las migraciones aplicadas (`alembic upgrade head`) en la
`DATABASE_URL` del entorno. En CI la levanta el job `test` como servicio (DECISIÓN 077).

- Sin base alcanzable, los tests se **saltean**: así `pytest -m integration` sigue corriendo en
  una máquina sin Postgres.
- Con `METIS_REQUIRE_DB=1` (lo que setea CI), la misma situación **falla**: en el pipeline una
  base caída no puede pasar en silencio como "0 tests".

Aislamiento: `stream_analysis()` y los servicios del historial hacen `commit()` por su cuenta,
así que el rollback por test que sugiere `testing.md` no alcanza. Cada test crea sus propios
usuarios con un email único y los borra al terminar; `ON DELETE CASCADE` (users → analyses →
analysis_results) se lleva todo lo que el test persistió.
"""

import os
import uuid

import bcrypt
import pytest
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from metis.db.models import User

from tests.integration.db._datos import PASSWORD

# rounds=4: el mínimo de bcrypt; el costo de la función no es lo que se prueba acá.
_HASH = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(rounds=4)).decode()


@pytest.fixture
async def db():
    # NullPool: pytest-asyncio abre un event loop por test y una conexión asyncpg no puede
    # cambiar de loop. Sin pool, cada test abre y cierra las suyas.
    engine = create_async_engine(os.environ["DATABASE_URL"], poolclass=NullPool)
    try:
        async with engine.connect() as conexion:
            await conexion.execute(
                text("SELECT archivado_at, timestamps FROM analyses LIMIT 0")
            )
    except Exception as exc:  # noqa: BLE001 — cualquier falla de conexión o de esquema
        await engine.dispose()
        mensaje = f"Sin PostgreSQL de test con las migraciones aplicadas: {exc!r}"
        if os.environ.get("METIS_REQUIRE_DB") == "1":
            pytest.fail(mensaje)
        pytest.skip(mensaje)

    sesiones = async_sessionmaker(engine, expire_on_commit=False)
    async with sesiones() as sesion:
        yield sesion
    await engine.dispose()


@pytest.fixture
async def crear_usuario(db):
    """Fábrica de usuarios verificados con email único; los borra al final del test."""
    creados: list[uuid.UUID] = []

    async def _crear(prefijo: str = "docente") -> User:
        usuario = User(
            email=f"{prefijo}-{uuid.uuid4().hex[:10]}@ucc.edu.ar",
            nombre="Test integración",
            password_hash=_HASH,
            email_verified=True,
        )
        db.add(usuario)
        await db.commit()
        creados.append(usuario.id)
        return usuario

    yield _crear

    await db.rollback()
    if creados:
        await db.execute(delete(User).where(User.id.in_(creados)))
        await db.commit()
