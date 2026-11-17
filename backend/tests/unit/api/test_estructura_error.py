"""
Estructura de error estándar (api-contracts.md) de punta a punta, por HTTP:
`{"error": {codigo, mensaje}}` sin envolver en `detail`. Antes de
metis/api/errors.py, FastAPI respondía `{"detail": {"error": {...}}}` y el
frontend (api/client.ts::toApiError) mostraba el texto genérico en lugar del
código — por ejemplo, en el login con contraseña incorrecta.

Los demás tests de api/ llaman a la función del endpoint directo y ven la
HTTPException, nunca el body serializado: este archivo pasa por la app real.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from metis.api.deps import get_optional_user
from metis.main import app


@pytest.fixture
def client():
    app.dependency_overrides[get_optional_user] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.unit
def test_error_con_codigo_responde_la_estructura_estandar(client):
    response = client.post(
        "/api/v1/analysis/distribution-decision",
        json={
            "session_id": str(uuid.uuid4()),
            "distribucion": "gumbel",
            "metodo": "momentos",
            "periodos_retorno": [1],
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert "detail" not in body
    assert body["error"]["codigo"] == "DIST_SELECTION_INVALID"
    assert body["error"]["mensaje"]


@pytest.mark.unit
def test_detail_de_texto_sigue_igual(client):
    # Sin cookie: get_current_user levanta HTTPException(401, "No autenticado").
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "No autenticado"}


@pytest.mark.unit
def test_ruta_inexistente_sigue_igual(client):
    response = client.get("/api/v1/no-existe")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.unit
def test_validacion_pydantic_sigue_siendo_422_con_detail(client):
    response = client.post(
        "/api/v1/analysis/distribution-decision", json={"session_id": "x"}
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
