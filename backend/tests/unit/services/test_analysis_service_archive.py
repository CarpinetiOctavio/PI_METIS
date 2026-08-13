"""
Tests unitarios de archive_analysis/unarchive_analysis/get_history (DECISIÓN 048).

Mismo patrón de mocking que tests/unit/auth/test_router_register.py: la
AsyncSession se mockea (MagicMock + AsyncMock en execute/commit), no se abre
conexión real — no son tests de integración.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from metis.db.models.analysis import Analysis
from metis.services.analysis_service import (
    archive_analysis,
    get_history,
    unarchive_analysis,
)


def _mock_db_scalar_one_or_none(value):
    db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    return db


def _mock_db_scalars_all(values):
    db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    db.execute = AsyncMock(return_value=result)
    return db


def _analysis(**kwargs):
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "serie": {},
        "tipo_variable": "otro",
        "etapas": ["1"],
        "modo": "experto",
        "archivado_at": None,
    }
    defaults.update(kwargs)
    a = Analysis(**{k: v for k, v in defaults.items() if k != "created_at"})
    a.created_at = kwargs.get("created_at") or __import__("datetime").datetime(
        2026, 7, 31
    )
    return a


@pytest.mark.unit
async def test_archive_analysis_marca_archivado_at_y_commitea():
    user_id = uuid.uuid4()
    analysis = _analysis(user_id=user_id, archivado_at=None)
    db = _mock_db_scalar_one_or_none(analysis)

    ok = await archive_analysis(analysis_id=analysis.id, user_id=user_id, db=db)

    assert ok is True
    assert analysis.archivado_at is not None
    db.commit.assert_awaited_once()


@pytest.mark.unit
async def test_archive_analysis_retorna_false_si_no_existe_o_no_pertenece():
    db = _mock_db_scalar_one_or_none(None)

    ok = await archive_analysis(analysis_id=uuid.uuid4(), user_id=uuid.uuid4(), db=db)

    assert ok is False
    db.commit.assert_not_awaited()


@pytest.mark.unit
async def test_unarchive_analysis_limpia_archivado_at_y_commitea():
    user_id = uuid.uuid4()
    analysis = _analysis(user_id=user_id)
    analysis.archivado_at = __import__("datetime").datetime(2026, 7, 31)
    db = _mock_db_scalar_one_or_none(analysis)

    ok = await unarchive_analysis(analysis_id=analysis.id, user_id=user_id, db=db)

    assert ok is True
    assert analysis.archivado_at is None
    db.commit.assert_awaited_once()


@pytest.mark.unit
async def test_unarchive_analysis_retorna_false_si_no_existe_o_no_pertenece():
    db = _mock_db_scalar_one_or_none(None)

    ok = await unarchive_analysis(analysis_id=uuid.uuid4(), user_id=uuid.uuid4(), db=db)

    assert ok is False
    db.commit.assert_not_awaited()


@pytest.mark.unit
async def test_get_history_expone_archivado_at_en_cada_item():
    user_id = uuid.uuid4()
    activo = _analysis(user_id=user_id, archivado_at=None)
    db = _mock_db_scalars_all([activo])

    items = await get_history(user_id=user_id, db=db)

    assert items[0]["archivado_at"] is None
    assert items[0]["id"] == str(activo.id)


@pytest.mark.unit
async def test_get_history_default_no_filtra_en_memoria_delega_al_query():
    """get_history no filtra en Python — confía en el WHERE armado sobre
    Analysis.archivado_at.is_(None). Este test solo verifica que, cuando
    incluir_archivados=False (default), la llamada no pide incluir
    archivados — el filtrado real lo prueba un test de integración con BD
    real, fuera de alcance de esta suite unitaria (ver testing.md)."""
    user_id = uuid.uuid4()
    db = _mock_db_scalars_all([])

    await get_history(user_id=user_id, db=db)

    assert db.execute.await_count == 1


@pytest.mark.unit
async def test_get_history_incluir_archivados_true_pasa_por_el_mismo_camino():
    user_id = uuid.uuid4()
    archivado = _analysis(user_id=user_id)
    archivado.archivado_at = __import__("datetime").datetime(2026, 7, 31)
    db = _mock_db_scalars_all([archivado])

    items = await get_history(user_id=user_id, db=db, incluir_archivados=True)

    assert items[0]["archivado_at"] is not None


# ── F7a/F7b (plan de fixes pre-reunión) — nombre_archivo y serie_preview ────


@pytest.mark.unit
async def test_get_history_expone_nombre_archivo_y_serie_preview():
    user_id = uuid.uuid4()
    analysis = _analysis(
        user_id=user_id,
        configuracion={
            "cramer_particion": "default",
            "nombre_archivo": "estacion_04.csv",
        },
        serie=[94.71, 89.83, 105.13],
    )
    db = _mock_db_scalars_all([analysis])

    items = await get_history(user_id=user_id, db=db)

    assert items[0]["nombre_archivo"] == "estacion_04.csv"
    assert items[0]["serie_preview"] == [94.71, 89.83, 105.13]


@pytest.mark.unit
async def test_get_history_degrada_nombre_archivo_a_null_sin_backfill():
    """Análisis persistidos antes de F7a — configuracion no tiene la clave
    nombre_archivo (o configuracion es None directamente). Igual que
    timestamps (DECISIÓN 058 §4), sin backfill: el frontend degrada
    mostrando tipo_variable en vez de romper o esconder la fila."""
    user_id = uuid.uuid4()
    sin_clave = _analysis(
        user_id=user_id, configuracion={"cramer_particion": "default"}
    )
    sin_configuracion = _analysis(user_id=user_id, configuracion=None)
    db = _mock_db_scalars_all([sin_clave, sin_configuracion])

    items = await get_history(user_id=user_id, db=db)

    assert items[0]["nombre_archivo"] is None
    assert items[1]["nombre_archivo"] is None
