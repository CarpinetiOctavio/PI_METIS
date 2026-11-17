"""
Tests unitarios de POST /history/{id}/archive y /unarchive (DECISIÓN 048).

Mismo patrón que tests/unit/api/test_analysis_preview_columns.py: llamar a
la función del endpoint directamente. El servicio (archive_analysis/
unarchive_analysis) se mockea en el borde — estos tests verifican la
orquestación HTTP (404 cuando el servicio retorna False), no la lógica de
persistencia, ya cubierta en tests/unit/services/test_analysis_service_archive.py.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from metis.api.v1.history import (
    archive_history_item,
    list_history,
    unarchive_history_item,
)
from metis.db.models.user import User


def _user() -> User:
    return User(
        id=uuid.uuid4(),
        email="legajo@ucc.edu.ar",
        nombre="Test",
        password_hash="x",
        email_verified=True,
    )


@pytest.mark.unit
async def test_archive_history_item_ok():
    user = _user()
    analysis_id = uuid.uuid4()
    db_sentinel = object()

    with patch(
        "metis.api.v1.history.archive_analysis",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_archive:
        response = await archive_history_item(
            analysis_id=analysis_id, db=db_sentinel, current_user=user
        )

    assert response == {"ok": True}
    mock_archive.assert_awaited_once_with(
        analysis_id=analysis_id, user_id=user.id, db=db_sentinel
    )


@pytest.mark.unit
async def test_archive_history_item_404_si_no_pertenece_o_no_existe():
    user = _user()

    with patch(
        "metis.api.v1.history.archive_analysis",
        new_callable=AsyncMock,
        return_value=False,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await archive_history_item(
                analysis_id=uuid.uuid4(), db=object(), current_user=user
            )

    assert exc_info.value.status_code == 404


@pytest.mark.unit
async def test_unarchive_history_item_ok():
    user = _user()
    analysis_id = uuid.uuid4()

    with patch(
        "metis.api.v1.history.unarchive_analysis",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = await unarchive_history_item(
            analysis_id=analysis_id, db=object(), current_user=user
        )

    assert response == {"ok": True}


@pytest.mark.unit
async def test_unarchive_history_item_404_si_no_pertenece_o_no_existe():
    user = _user()

    with patch(
        "metis.api.v1.history.unarchive_analysis",
        new_callable=AsyncMock,
        return_value=False,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await unarchive_history_item(
                analysis_id=uuid.uuid4(), db=object(), current_user=user
            )

    assert exc_info.value.status_code == 404


@pytest.mark.unit
async def test_list_history_default_no_incluye_archivados():
    user = _user()

    with patch(
        "metis.api.v1.history.get_history",
        new_callable=AsyncMock,
        return_value=[],
    ) as mock_get_history:
        await list_history(db=object(), current_user=user)

    assert mock_get_history.call_args.kwargs["incluir_archivados"] is False


@pytest.mark.unit
async def test_list_history_archivados_true_se_propaga():
    user = _user()

    with patch(
        "metis.api.v1.history.get_history",
        new_callable=AsyncMock,
        return_value=[],
    ) as mock_get_history:
        await list_history(archivados=True, db=object(), current_user=user)

    assert mock_get_history.call_args.kwargs["incluir_archivados"] is True
