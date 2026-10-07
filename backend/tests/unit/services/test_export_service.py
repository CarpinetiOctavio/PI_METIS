"""
Tests unitarios de services/export_service.py::exportar_pdf() (DECISIÓN 075):
reusa get_analysis_by_id() (mismo guard de pertenencia que GET /history/{id})
y le pasa ese dict, tal cual, al generador del PDF.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from metis.services.export_service import exportar_pdf, exportar_pdf_simulacion

_DETALLE = {
    "created_at": "2026-10-06T12:00:00",
    "configuracion": {"nombre_archivo": "estacion.csv"},
}


@pytest.mark.unit
async def test_exportar_pdf_none_si_el_analisis_no_es_del_usuario():
    with (
        patch(
            "metis.services.export_service.get_analysis_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch("metis.services.export_service.generar_pdf_analisis") as mock_generar,
    ):
        resultado = await exportar_pdf(uuid.uuid4(), uuid.uuid4(), db=object())

    assert resultado is None
    mock_generar.assert_not_called()


@pytest.mark.unit
async def test_exportar_pdf_genera_desde_el_detalle_persistido():
    analysis_id, user_id = uuid.uuid4(), uuid.uuid4()
    with (
        patch(
            "metis.services.export_service.get_analysis_by_id",
            new_callable=AsyncMock,
            return_value=_DETALLE,
        ) as mock_get,
        patch(
            "metis.services.export_service.generar_pdf_analisis",
            return_value=b"%PDF-1.4",
        ) as mock_generar,
    ):
        pdf, nombre = await exportar_pdf(analysis_id, user_id, db=object(), autor="Ana")

    assert pdf == b"%PDF-1.4"
    assert nombre == "metis_estacion_2026-10-06.pdf"
    assert mock_get.call_args.kwargs == {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "db": mock_get.call_args.kwargs["db"],
    }
    mock_generar.assert_called_once_with(_DETALLE, "Ana")


@pytest.mark.unit
async def test_exportar_pdf_simulacion_pasa_la_simulacion_al_generador():
    simulacion = {"excluidos": [{"indice": 1, "periodo": 1981, "valor_original": 9.0}]}
    with (
        patch(
            "metis.services.export_service.get_analysis_by_id",
            new_callable=AsyncMock,
            return_value=_DETALLE,
        ),
        patch(
            "metis.services.export_service._simular_desde_detalle",
            return_value=simulacion,
        ) as mock_simular,
        patch(
            "metis.services.export_service.generar_pdf_analisis",
            return_value=b"%PDF-1.4",
        ) as mock_generar,
    ):
        pdf, nombre = await exportar_pdf_simulacion(
            uuid.uuid4(), uuid.uuid4(), db=object(), indices_excluidos=[1], autor="Ana"
        )

    assert pdf == b"%PDF-1.4"
    assert nombre == "metis_estacion_2026-10-06_simulacion.pdf"
    mock_simular.assert_called_once_with(_DETALLE, [1])
    mock_generar.assert_called_once_with(_DETALLE, "Ana", None, simulacion)


@pytest.mark.unit
async def test_exportar_pdf_simulacion_none_si_el_analisis_no_es_del_usuario():
    with (
        patch(
            "metis.services.export_service.get_analysis_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch("metis.services.export_service._simular_desde_detalle") as mock_simular,
    ):
        resultado = await exportar_pdf_simulacion(
            uuid.uuid4(), uuid.uuid4(), db=object(), indices_excluidos=[1]
        )

    assert resultado is None
    mock_simular.assert_not_called()
