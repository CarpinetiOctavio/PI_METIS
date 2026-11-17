import os

# Los tests de este directorio arman el payload persistido con los
# serializadores reales de metis.services.analysis_service, que en
# import-time arrastra metis.db.models y exige DATABASE_URL (ver
# tests/unit/services/conftest.py). Nunca abren conexión real.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_unit_dummy"
)
