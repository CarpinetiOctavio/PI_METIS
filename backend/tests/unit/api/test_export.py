"""
Tests unitarios de GET /export/{id} y POST /export/{id}/simulacion (DECISIÓN
075) — mismo patrón que test_analysis_design_events.py: la función del
endpoint se llama directo, con el servicio mockeado en el borde. Verifican la
orquestación HTTP (PDF como adjunto, errores con la estructura estándar), no el
contenido del PDF, cubierto en tests/unit/reportes/test_pdf.py.
"""

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from metis.api.v1.export import exportar_analisis, exportar_analisis_con_simulacion
from metis.core.pipeline.exclusiones import ExclusionInvalidaError
from metis.db.models.user import User
from metis.schemas.export import ExportSimulacionRequest
from metis.services.export_service import SimulacionNoDisponibleError


def _user(nombre: str | None = "Ana") -> User:
    return User(
        id=uuid.uuid4(),
        email="ana@ucc.edu.ar",
        nombre=nombre,
        password_hash="x",
        email_verified=True,
    )


@pytest.mark.unit
async def test_exportar_devuelve_el_pdf_como_adjunto():
    user = _user()
    analysis_id = uuid.uuid4()

    with patch(
        "metis.api.v1.export.exportar_pdf",
        new_callable=AsyncMock,
        return_value=(b"%PDF-1.4 ...", "metis_estacion_2026-10-06.pdf"),
    ) as mock_exportar:
        response = await exportar_analisis(
            analysis_id=analysis_id, db=object(), current_user=user
        )

    assert response.status_code == 200
    assert response.media_type == "application/pdf"
    assert response.body == b"%PDF-1.4 ..."
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="metis_estacion_2026-10-06.pdf"'
    )
    kwargs = mock_exportar.call_args.kwargs
    assert kwargs["analysis_id"] == analysis_id
    assert kwargs["user_id"] == user.id
    assert kwargs["autor"] == "Ana (ana@ucc.edu.ar)"


@pytest.mark.unit
async def test_exportar_sin_nombre_usa_solo_el_email():
    with patch(
        "metis.api.v1.export.exportar_pdf",
        new_callable=AsyncMock,
        return_value=(b"%PDF", "x.pdf"),
    ) as mock_exportar:
        await exportar_analisis(
            analysis_id=uuid.uuid4(), db=object(), current_user=_user(nombre=None)
        )

    assert mock_exportar.call_args.kwargs["autor"] == "ana@ucc.edu.ar"


@pytest.mark.unit
async def test_exportar_404_con_estructura_de_error_estandar():
    with patch(
        "metis.api.v1.export.exportar_pdf",
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = await exportar_analisis(
            analysis_id=uuid.uuid4(), db=object(), current_user=_user()
        )

    assert response.status_code == 404
    body = json.loads(response.body)
    assert body["error"]["codigo"] == "ANALYSIS_NOT_FOUND"


# --- POST /export/{id}/simulacion (DECISIÓN 075, addendum) ------------------


async def _exportar_simulacion(indices: list[int]):
    return await exportar_analisis_con_simulacion(
        analysis_id=uuid.uuid4(),
        body=ExportSimulacionRequest(indices_excluidos=indices),
        db=object(),
        current_user=_user(),
    )


@pytest.mark.unit
async def test_exportar_simulacion_devuelve_el_pdf():
    with patch(
        "metis.api.v1.export.exportar_pdf_simulacion",
        new_callable=AsyncMock,
        return_value=(b"%PDF", "metis_x_simulacion.pdf"),
    ) as mock_exportar:
        response = await _exportar_simulacion([3, 17])

    assert response.status_code == 200
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="metis_x_simulacion.pdf"'
    )
    assert mock_exportar.call_args.kwargs["indices_excluidos"] == [3, 17]


@pytest.mark.unit
async def test_exportar_simulacion_sin_indices_es_400_sin_calcular():
    with patch(
        "metis.api.v1.export.exportar_pdf_simulacion", new_callable=AsyncMock
    ) as mock_exportar:
        response = await _exportar_simulacion([])

    assert response.status_code == 400
    assert json.loads(response.body)["error"]["codigo"] == "CONTRACT_EXCLUSION_INVALID"
    mock_exportar.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize(
    "error",
    [
        SimulacionNoDisponibleError("sin datos"),
        ExclusionInvalidaError("fuera de rango"),
    ],
)
async def test_exportar_simulacion_400_si_no_se_puede_simular(error):
    with patch(
        "metis.api.v1.export.exportar_pdf_simulacion",
        new_callable=AsyncMock,
        side_effect=error,
    ):
        response = await _exportar_simulacion([1])

    assert response.status_code == 400
    body = json.loads(response.body)
    assert body["error"]["codigo"] == "CONTRACT_EXCLUSION_INVALID"
    assert body["error"]["mensaje"] == str(error)


@pytest.mark.unit
async def test_exportar_simulacion_404():
    with patch(
        "metis.api.v1.export.exportar_pdf_simulacion",
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = await _exportar_simulacion([1])

    assert response.status_code == 404
    assert json.loads(response.body)["error"]["codigo"] == "ANALYSIS_NOT_FOUND"
