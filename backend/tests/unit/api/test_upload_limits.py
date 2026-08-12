"""
Tests unitarios del cap de tamaño de subida (DECISIÓN 050).

Mismo patrón que test_analysis_preview_columns.py: llamar a las funciones
del endpoint directamente, no vía TestClient — ninguna de las dos rutas
necesita BD real para llegar al punto donde se aplica el cap, porque
_leer_archivo_limitado() es lo primero que corre en las dos.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile

from metis.api.v1.analysis import (
    MAX_UPLOAD_BYTES,
    _leer_archivo_limitado,
    preview_columns,
    stream_analysis,
)


def _archivo(content: bytes, filename: str = "serie.csv") -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


@pytest.mark.unit
async def test_leer_archivo_limitado_bajo_el_limite_devuelve_contenido_completo():
    content = b"x" * (MAX_UPLOAD_BYTES - 1)

    resultado = await _leer_archivo_limitado(_archivo(content))

    assert resultado == content


@pytest.mark.unit
async def test_leer_archivo_limitado_exactamente_en_el_limite_pasa():
    content = b"x" * MAX_UPLOAD_BYTES

    resultado = await _leer_archivo_limitado(_archivo(content))

    assert len(resultado) == MAX_UPLOAD_BYTES


@pytest.mark.unit
async def test_leer_archivo_limitado_supera_el_limite_corta_sin_leer_todo():
    # Contenido bastante mayor al límite — si _leer_archivo_limitado no
    # cortara temprano, este test seguiría pasando pero tardaría y
    # bufferearía varias veces MAX_UPLOAD_BYTES en memoria. El corte
    # temprano es lo que hace que esto sea instantáneo y barato.
    content = b"x" * (MAX_UPLOAD_BYTES + 5 * 1024 * 1024)

    with pytest.raises(HTTPException) as exc_info:
        await _leer_archivo_limitado(_archivo(content))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "PARSE_FILE_TOO_LARGE"


@pytest.mark.unit
async def test_preview_columns_archivo_sobre_el_limite_da_400_no_500():
    content = b"x" * (MAX_UPLOAD_BYTES + 1)

    with pytest.raises(HTTPException) as exc_info:
        await preview_columns(archivo=_archivo(content))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "PARSE_FILE_TOO_LARGE"


@pytest.mark.unit
async def test_stream_analysis_archivo_sobre_el_limite_da_400_antes_de_tocar_bd():
    content = b"x" * (MAX_UPLOAD_BYTES + 1)

    with pytest.raises(HTTPException) as exc_info:
        await stream_analysis(
            archivo=_archivo(content),
            columna_x="anio",
            columna_y="caudal",
            tipo_variable="caudal_precipitacion",
            etapas="1",
            modo="experto",
            cramer_particion="default",
            mes_inicio_anio=7,
            db=None,
            current_user=None,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "PARSE_FILE_TOO_LARGE"
