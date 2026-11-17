import os

# metis.api (vía metis.api.v1.analysis/history) importa metis.api.deps, que
# a su vez importa metis.auth.dependencies -> metis.auth.jwt (JWT_SECRET_KEY)
# y metis.db.session (DATABASE_URL), ambos leídos en import-time. Los tests
# de este directorio son unitarios — llaman a las funciones del endpoint
# directamente, nunca abren conexión real ni firman tokens reales.
#
# Sin este archivo, pytest solo carga tests/unit/auth/conftest.py (que ya
# setea estas mismas dos variables) cuando colecciona ESE directorio — y
# "api" se colecciona alfabéticamente antes que "auth", así que en CI (sin
# .env real) la importación de este paquete revienta con KeyError antes de
# que el conftest de auth llegue a correr. Localmente contra Docker no se
# nota porque el .env del compose ya trae ambas variables reales.
#
# setdefault: no pisa un valor real si ya está seteado (ej. en CI real).
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_unit_dummy"
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-unit-tests")
