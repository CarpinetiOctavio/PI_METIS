"""
Tests unitarios de POST /analysis/preview-columns (DECISIÓN 047).

Mismo patrón que tests/unit/auth/test_router_register.py: llamar a la
función del endpoint directamente, no vía TestClient. Acá es incluso más
simple que ese precedente — preview_columns() no declara ninguna
dependencia de BD ni de usuario (stateless a propósito), así que no hace
falta mockear nada más que el UploadFile.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile

from metis.api.v1.analysis import preview_columns


def _archivo(content: bytes, filename: str = "serie.csv") -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


@pytest.mark.unit
async def test_preview_columns_devuelve_columnas_y_filas():
    csv = b"anio,caudal\n1980,94.71\n1981,89.83\n1982,105.13\n"

    response = await preview_columns(archivo=_archivo(csv))

    assert response.filas == 3
    assert [c.nombre for c in response.columnas] == ["anio", "caudal"]
    assert response.columnas[0].indice == 0
    assert response.columnas[0].muestra == ["1980", "1981", "1982"]


@pytest.mark.unit
async def test_preview_columns_archivo_no_parseable_da_400_parse_error():
    contenido_binario = bytes(range(256))

    with pytest.raises(HTTPException) as exc_info:
        await preview_columns(archivo=_archivo(contenido_binario, "corrupto.csv"))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "PARSE_ERROR"


@pytest.mark.unit
async def test_preview_columns_archivo_vacio_da_400_parse_error():
    with pytest.raises(HTTPException) as exc_info:
        await preview_columns(archivo=_archivo(b"", "vacio.csv"))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "PARSE_ERROR"


@pytest.mark.unit
async def test_preview_columns_no_recibe_ni_usa_ningun_upload_filename_default():
    # archivo.filename puede ser None en teoría (UploadFile lo permite) —
    # preview_columns debe seguir funcionando con el fallback "upload" que
    # ya usa /analysis/stream, no reventar con un TypeError.
    csv = b"x,y\n1,2\n"
    archivo = UploadFile(file=io.BytesIO(csv), filename=None)

    response = await preview_columns(archivo=archivo)

    assert response.filas == 1
