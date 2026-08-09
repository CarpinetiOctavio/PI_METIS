import os

# Mismo motivo que tests/unit/services/conftest.py: importar
# metis.services.analysis_service arrastra metis.db.models, que en
# import-time construye el engine async y exige DATABASE_URL en el
# entorno. El test de este directorio no toca BD real (user_id=None,
# camino CU-02 anónimo) — setdefault: no pisa un valor real si ya está
# seteado (ej. en CI).
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_unit_dummy"
)
