"""
Tests unitarios de recalcular_eventos_diseno() (Bloque C2c, DECISIÓN 062) —
historial interactivo: recálculo stateless de eventos de diseño para una
distribución+método explorados desde el historial, sin reajustar nada y
sin tocar session_store ni `analysis_results.decisiones`.

Mismo patrón de mocking que test_analysis_service_archive.py: la
AsyncSession se mockea, no se abre conexión real.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from metis.db.models.analysis import Analysis
from metis.db.models.result import AnalysisResult
from metis.services.analysis_service import (
    MetodoNoAjustadoError,
    recalcular_eventos_diseno,
)


def _mock_db_first(value):
    db = MagicMock()
    result = MagicMock()
    result.first.return_value = value
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    db.add = MagicMock()
    return db


def _etapa2_con_gumbel_ok() -> dict:
    return {
        "ranking": [
            {
                "distribucion": "gumbel",
                "n_parametros": 2,
                "metodos": [
                    {
                        "metodo": "momentos",
                        "parametros": {"mu": 100.0, "alpha": 20.0},
                        "eea": 12.5,
                        "status": "ok",
                    },
                    {
                        "metodo": "mv",
                        "parametros": None,
                        "eea": None,
                        "status": "no_converge",
                    },
                ],
                "mejor_eea": 12.5,
                "mejor_metodo": "momentos",
            }
        ],
        "warnings": [],
        "puntos_empiricos": [
            {"valor": 142.5, "periodo_retorno": 41.0, "probabilidad": 0.9756}
        ],
        "seleccion": None,
    }


@pytest.mark.unit
async def test_recalcular_retorna_none_si_analisis_no_existe_o_no_es_del_usuario():
    db = _mock_db_first(None)

    result = await recalcular_eventos_diseno(
        analysis_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        distribucion="gumbel",
        metodo="momentos",
        periodos_retorno=[2, 10, 100],
        db=db,
    )

    assert result is None


@pytest.mark.unit
async def test_recalcular_retorna_none_si_el_analisis_no_tiene_etapa2():
    analysis = Analysis(id=uuid.uuid4(), user_id=uuid.uuid4())
    analysis_result = AnalysisResult(
        analysis_id=analysis.id, etapa1={}, etapa2=None, decisiones={}
    )
    db = _mock_db_first((analysis, analysis_result))

    result = await recalcular_eventos_diseno(
        analysis_id=analysis.id,
        user_id=analysis.user_id,
        distribucion="gumbel",
        metodo="momentos",
        periodos_retorno=[2, 10, 100],
        db=db,
    )

    assert result is None


@pytest.mark.unit
async def test_recalcular_levanta_error_si_la_distribucion_no_esta_en_el_ranking():
    analysis = Analysis(id=uuid.uuid4(), user_id=uuid.uuid4())
    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1={},
        etapa2=_etapa2_con_gumbel_ok(),
        decisiones={},
    )
    db = _mock_db_first((analysis, analysis_result))

    with pytest.raises(MetodoNoAjustadoError):
        await recalcular_eventos_diseno(
            analysis_id=analysis.id,
            user_id=analysis.user_id,
            distribucion="gve",
            metodo="ml",
            periodos_retorno=[2, 10, 100],
            db=db,
        )


@pytest.mark.unit
async def test_recalcular_levanta_error_si_el_metodo_no_convergio():
    analysis = Analysis(id=uuid.uuid4(), user_id=uuid.uuid4())
    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1={},
        etapa2=_etapa2_con_gumbel_ok(),
        decisiones={},
    )
    db = _mock_db_first((analysis, analysis_result))

    with pytest.raises(MetodoNoAjustadoError):
        await recalcular_eventos_diseno(
            analysis_id=analysis.id,
            user_id=analysis.user_id,
            distribucion="gumbel",
            metodo="mv",
            periodos_retorno=[2, 10, 100],
            db=db,
        )


@pytest.mark.unit
async def test_recalcular_devuelve_eventos_y_curva_para_una_combinacion_ok():
    analysis = Analysis(id=uuid.uuid4(), user_id=uuid.uuid4())
    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1={},
        etapa2=_etapa2_con_gumbel_ok(),
        decisiones={"chow": {"accion": "rechazar", "dato": 950.0}},
    )
    db = _mock_db_first((analysis, analysis_result))

    result = await recalcular_eventos_diseno(
        analysis_id=analysis.id,
        user_id=analysis.user_id,
        distribucion="gumbel",
        metodo="momentos",
        periodos_retorno=[2, 10, 100],
        db=db,
    )

    assert result is not None
    assert [e["periodo_retorno"] for e in result["eventos_diseno"]] == [2, 10, 100]
    assert all(e["valor"] is not None for e in result["eventos_diseno"])
    assert len(result["curva_ajuste"]) == 60
    # Curva log-espaciada arranca en 1.05 — cubre el mismo rango que el
    # gráfico de ajuste del stream (DECISIÓN 056).
    assert result["curva_ajuste"][0]["periodo_retorno"] == pytest.approx(1.05)


@pytest.mark.unit
async def test_recalcular_no_persiste_nada_ni_toca_decisiones():
    """DECISIÓN 062 — explorar no es decidir: el recálculo es de lectura
    pura, nunca llama a db.commit() ni db.add(), y no muta `decisiones`."""
    analysis = Analysis(id=uuid.uuid4(), user_id=uuid.uuid4())
    decisiones_originales = {"chow": {"accion": "rechazar", "dato": 950.0}}
    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1={},
        etapa2=_etapa2_con_gumbel_ok(),
        decisiones=decisiones_originales,
    )
    db = _mock_db_first((analysis, analysis_result))

    await recalcular_eventos_diseno(
        analysis_id=analysis.id,
        user_id=analysis.user_id,
        distribucion="gumbel",
        metodo="momentos",
        periodos_retorno=[2, 10, 100],
        db=db,
    )

    db.commit.assert_not_awaited()
    db.add.assert_not_called()
    assert analysis_result.decisiones == decisiones_originales
