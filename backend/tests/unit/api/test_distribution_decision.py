"""
Tests unitarios de POST /analysis/distribution-decision (DECISIÓN 052).
Reemplaza al design-events documentado y nunca implementado — misma forma
que outlier-decision, con dos errores propios: 404 SESSION_NOT_FOUND (la
sesión no existe, chequeo explícito que outlier-decision no tiene) y 400
DIST_SELECTION_INVALID (validado en el borde, no con Pydantic, para no
devolver un 422 genérico).

Mismo patrón que test_stream_cramer_particion.py: llamar a la función del
endpoint directamente, no vía TestClient.
"""

import uuid

import pytest
from fastapi import HTTPException

from metis.api.v1.analysis import distribution_decision
from metis.schemas.analysis import DistributionDecisionRequest
from metis.services import session_store


@pytest.fixture(autouse=True)
def _limpiar_sessions():
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()


def _body(**overrides) -> DistributionDecisionRequest:
    defaults = {
        "session_id": uuid.uuid4(),
        "distribucion": "gumbel",
        "metodo": "momentos",
        "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500],
    }
    defaults.update(overrides)
    return DistributionDecisionRequest(**defaults)


@pytest.mark.unit
async def test_sesion_inexistente_da_404_session_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(body=_body(), current_user=None)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"]["codigo"] == "SESSION_NOT_FOUND"


@pytest.mark.unit
async def test_sesion_existente_resuelve_y_desbloquea():
    session_id = uuid.uuid4()
    session_store.create_session(str(session_id))

    respuesta = await distribution_decision(
        body=_body(session_id=session_id), current_user=None
    )

    assert respuesta.ok is True
    assert respuesta.pipeline_continua is True
    decision = session_store.get_decision(str(session_id))
    assert decision == {
        "distribucion": "gumbel",
        "metodo": "momentos",
        "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500],
    }


@pytest.mark.unit
async def test_distribucion_vacia_da_400_dist_selection_invalid():
    session_id = uuid.uuid4()
    session_store.create_session(str(session_id))

    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(
            body=_body(session_id=session_id, distribucion=""), current_user=None
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"


@pytest.mark.unit
async def test_metodo_vacio_da_400():
    session_id = uuid.uuid4()
    session_store.create_session(str(session_id))

    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(
            body=_body(session_id=session_id, metodo=""), current_user=None
        )

    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"


@pytest.mark.unit
async def test_periodos_retorno_vacio_da_400():
    session_id = uuid.uuid4()
    session_store.create_session(str(session_id))

    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(
            body=_body(session_id=session_id, periodos_retorno=[]), current_user=None
        )

    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"


@pytest.mark.unit
async def test_periodo_retorno_menor_o_igual_a_uno_da_400():
    # F = 1 - 1/T necesita T > 1 para caer en (0,1) — mismo guard que
    # cuantil() en core/, ver tests/unit/core/etapa2/test_cuantil_guard.py.
    session_id = uuid.uuid4()
    session_store.create_session(str(session_id))

    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(
            body=_body(session_id=session_id, periodos_retorno=[2, 1]),
            current_user=None,
        )

    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"


@pytest.mark.unit
async def test_mas_de_veinte_periodos_retorno_da_400():
    session_id = uuid.uuid4()
    session_store.create_session(str(session_id))

    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(
            body=_body(session_id=session_id, periodos_retorno=list(range(2, 23))),
            current_user=None,
        )

    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"


@pytest.mark.unit
async def test_validacion_corre_antes_que_el_chequeo_de_sesion():
    """Una sesión inexistente Y un payload inválido deben responder
    DIST_SELECTION_INVALID (400), no SESSION_NOT_FOUND (404) — la validación
    de forma en el borde corre antes de tocar session_store."""
    with pytest.raises(HTTPException) as exc_info:
        await distribution_decision(
            body=_body(distribucion=""), current_user=None
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"
