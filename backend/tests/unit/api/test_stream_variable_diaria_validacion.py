"""
Tests unitarios de la validación de variable_diaria en POST /analysis/stream
(DECISIÓN 065, PR 2.5 / R0.2). Solo se aceptan "pico" y "media" en el borde;
cualquier otro valor responde 400 CONTRACT_VARIABLE_DIARIA_INVALID antes de
tocar db, current_user o el archivo.

Mismo patrón que test_stream_etapas_validacion.py.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from metis.api.v1.analysis import stream_analysis


def _archivo(
    content: bytes = b"anio,caudal\n1980,94.71\n", filename: str = "serie.csv"
) -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


async def _llamar(variable_diaria: str):
    return await stream_analysis(
        archivo=_archivo(),
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="caudal_precipitacion",
        etapas="1",
        modo="experto",
        cramer_particion="default",
        mes_inicio_anio=7,
        variable_diaria=variable_diaria,
        db=None,
        current_user=None,
    )


@pytest.mark.unit
@pytest.mark.parametrize("valor", ["pico", "media"])
async def test_valores_validos_no_lanzan(valor):
    respuesta = await _llamar(valor)
    assert isinstance(respuesta, StreamingResponse)


@pytest.mark.unit
@pytest.mark.parametrize("valor", ["instantaneo", "PICO", "", "maximo_diario"])
async def test_valor_invalido_da_400(valor):
    with pytest.raises(HTTPException) as exc_info:
        await _llamar(valor)

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_VARIABLE_DIARIA_INVALID"
    )
