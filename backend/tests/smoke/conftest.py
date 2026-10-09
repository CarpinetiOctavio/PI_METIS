"""Smoke del despliegue (B5 del plan del TP de Calidad).

No importan nada de `metis`: le pegan por HTTP a un stack ya levantado, siempre a través de
nginx, como lo haría un navegador. Los levanta `scripts/deploy-local.sh` (en local y en el job
`despliegue` de CI) con `docker-compose.ci.yml`.

- `SMOKE_BASE_URL`: dónde está nginx (default `http://localhost`).
- `SMOKE_EMAIL`/`SMOKE_PASSWORD`: usuario verificado que siembra `scripts/deploy-local.sh`.
- Sin stack alcanzable los tests se **saltean** (un `pytest` suelto en una máquina sin el stack no
  falla por eso). Con `METIS_REQUIRE_SMOKE=1`, que setea el script, la misma situación **falla**.
"""

import os

import httpx
import pytest

BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://localhost").rstrip("/")
EMAIL = os.environ.get("SMOKE_EMAIL", "smoke@ucc.edu.ar")
PASSWORD = os.environ.get("SMOKE_PASSWORD", "smoke-metis-1234")


@pytest.fixture(scope="session")
def cliente():
    """Un solo cliente para toda la corrida: la cookie del login viaja a los tests siguientes."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        try:
            c.get("/ping")
        except httpx.TransportError as e:
            if os.environ.get("METIS_REQUIRE_SMOKE") == "1":
                pytest.fail(f"El stack no responde en {BASE_URL}: {e}")
            pytest.skip(
                f"Sin stack desplegado en {BASE_URL} (ver scripts/deploy-local.sh)"
            )
        yield c
