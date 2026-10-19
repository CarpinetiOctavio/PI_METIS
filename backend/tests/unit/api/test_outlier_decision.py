"""POST /analysis/outlier-decision — DECISIÓN 079: una decisión por atípico.

Mismo patrón que test_distribution_decision.py: la función del endpoint se llama
directo, sin TestClient.
"""

import uuid

import pytest
from fastapi import HTTPException

from metis.api.v1.analysis import outlier_decision
from metis.schemas.analysis import OutlierDecisionRequest
from metis.services import session_store


@pytest.fixture(autouse=True)
def _limpiar_sessions():
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()


def _pausa(indices: list[int]) -> str:
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)
    session_store.get_session(session_id).atipicos_pendientes = [
        {"indice": i} for i in indices
    ]
    return session_id


def _body(session_id: str, decisiones: list[tuple[int, str]]) -> OutlierDecisionRequest:
    return OutlierDecisionRequest(
        session_id=session_id,
        decisiones=[{"indice": i, "decision": d} for i, d in decisiones],
    )


@pytest.mark.unit
async def test_decidir_todos_los_atipicos_desbloquea_el_stream():
    session_id = _pausa([3, 17])

    r = await outlier_decision(
        _body(session_id, [(17, "rechazar"), (3, "aceptar")]),
        db=None,
        current_user=None,
    )

    assert r.ok and r.pipeline_continua
    estado = session_store.get_session(session_id)
    assert estado.event.is_set()
    assert estado.decision == {
        "decisiones": [
            {"indice": 17, "decision": "rechazar"},
            {"indice": 3, "decision": "aceptar"},
        ]
    }


@pytest.mark.unit
async def test_decisiones_que_no_coinciden_con_la_pausa_dan_400():
    session_id = _pausa([3, 17])
    with pytest.raises(HTTPException) as exc_info:
        await outlier_decision(
            _body(session_id, [(3, "aceptar")]), db=None, current_user=None
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "OUTLIER_DECISION_INVALID"
    assert not session_store.get_session(session_id).event.is_set()


@pytest.mark.unit
async def test_sesion_inexistente_da_404():
    with pytest.raises(HTTPException) as exc_info:
        await outlier_decision(
            _body(str(uuid.uuid4()), [(0, "aceptar")]), db=None, current_user=None
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"]["codigo"] == "SESSION_NOT_FOUND"


@pytest.mark.unit
async def test_sesion_sin_pausa_de_chow_da_400():
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)
    with pytest.raises(HTTPException) as exc_info:
        await outlier_decision(
            _body(session_id, [(0, "aceptar")]), db=None, current_user=None
        )
    assert exc_info.value.detail["error"]["codigo"] == "OUTLIER_DECISION_INVALID"
