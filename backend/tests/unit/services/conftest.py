import os

# metis.services.analysis_service importa metis.db.models, que en el
# import-time construye el engine async y exige DATABASE_URL en el entorno
# (metis/db/session.py). Los tests de este directorio son unitarios —
# solo ejercitan funciones puras del módulo, nunca abren conexión real.
# setdefault: no pisa un valor real si ya está seteado (ej. en CI).
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_unit_dummy"
)
