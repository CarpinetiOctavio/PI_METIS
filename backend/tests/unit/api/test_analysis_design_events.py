"""
Tests unitarios de POST /analysis/{id}/design-events (Bloque C2c, DECISIÓN
062) — mismo patrón que test_history_archive.py: llamar a la función del
endpoint directamente, con el servicio mockeado en el borde. Estos tests
verifican la orquestación HTTP (400/404 según lo que retorna/levanta
recalcular_eventos_diseno()), no la lógica de recálculo en sí, ya cubierta
en tests/unit/services/test_recalcular_eventos_diseno.py.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from metis.api.v1.analysis import recalcular_design_events
from metis.db.models.user import User
from metis.schemas.analysis import DesignEventsRecalcRequest
from metis.services.analysis_service import MetodoNoAjustadoError


def _user() -> User:
    return User(
        id=uuid.uuid4(),
        email="legajo@ucc.edu.ar",
        nombre="Test",
        password_hash="x",
        email_verified=True,
    )


def _body(**kwargs) -> DesignEventsRecalcRequest:
    defaults = {
        "distribucion": "gumbel",
        "metodo": "momentos",
        "periodos_retorno": [2, 10, 100],
    }
    defaults.update(kwargs)
    return DesignEventsRecalcRequest(**defaults)


@pytest.mark.unit
async def test_recalcular_design_events_ok():
    user = _user()
    analysis_id = uuid.uuid4()
    payload = {
        "eventos_diseno": [{"periodo_retorno": 2, "valor": 138.4}],
        "curva_ajuste": [{"periodo_retorno": 1.05, "valor": 61.2}],
    }

    with patch(
        "metis.api.v1.analysis.recalcular_eventos_diseno",
        new_callable=AsyncMock,
        return_value=payload,
    ) as mock_recalcular:
        response = await recalcular_design_events(
            analysis_id=analysis_id, body=_body(), db=object(), current_user=user
        )

    assert response.eventos_diseno[0].periodo_retorno == 2
    assert response.curva_ajuste[0].valor == 61.2
    mock_recalcular.assert_awaited_once()
    assert mock_recalcular.call_args.kwargs["analysis_id"] == analysis_id
    assert mock_recalcular.call_args.kwargs["user_id"] == user.id


@pytest.mark.unit
async def test_recalcular_design_events_404_si_el_servicio_retorna_none():
    user = _user()

    with patch(
        "metis.api.v1.analysis.recalcular_eventos_diseno",
        new_callable=AsyncMock,
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await recalcular_design_events(
                analysis_id=uuid.uuid4(), body=_body(), db=object(), current_user=user
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"]["codigo"] == "ANALYSIS_NOT_FOUND"


@pytest.mark.unit
async def test_recalcular_design_events_400_si_el_metodo_no_esta_ajustado():
    user = _user()

    with patch(
        "metis.api.v1.analysis.recalcular_eventos_diseno",
        new_callable=AsyncMock,
        side_effect=MetodoNoAjustadoError(),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await recalcular_design_events(
                analysis_id=uuid.uuid4(), body=_body(), db=object(), current_user=user
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "DIST_METHOD_NOT_FITTED"


@pytest.mark.unit
async def test_recalcular_design_events_400_si_la_seleccion_es_invalida():
    user = _user()

    with patch(
        "metis.api.v1.analysis.recalcular_eventos_diseno",
        new_callable=AsyncMock,
    ) as mock_recalcular:
        with pytest.raises(HTTPException) as exc_info:
            await recalcular_design_events(
                analysis_id=uuid.uuid4(),
                body=_body(distribucion=""),
                db=object(),
                current_user=user,
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"
    mock_recalcular.assert_not_awaited()


@pytest.mark.unit
async def test_recalcular_design_events_400_si_periodos_retorno_fuera_de_rango():
    user = _user()

    with pytest.raises(HTTPException) as exc_info:
        await recalcular_design_events(
            analysis_id=uuid.uuid4(),
            body=_body(periodos_retorno=[1]),  # T debe ser > 1
            db=object(),
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "DIST_SELECTION_INVALID"
