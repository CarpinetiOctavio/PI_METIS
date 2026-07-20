import os

# metis.auth.router importa metis.db (DATABASE_URL) y metis.auth.jwt
# (JWT_SECRET_KEY) en import-time. Los tests de este directorio son
# unitarios — nunca abren conexión real ni firman tokens reales.
# setdefault: no pisa un valor real si ya está seteado (ej. en CI).
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_unit_dummy"
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-unit-tests")
