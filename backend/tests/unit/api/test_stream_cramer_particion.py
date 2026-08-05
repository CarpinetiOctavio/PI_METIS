"""
Tests unitarios de la validación de cramer_particion en POST /analysis/stream
(DECISIÓN 036, addendum Bloque D). Antes de este fix, cualquier valor
distinto de "default" llegaba como str a calcular_cramer() y producía un
TypeError no manejado -> 500. Ahora se rechaza en el borde del endpoint,
antes de tocar el archivo o la BD.

Mismo patrón que test_upload_limits.py: llamar a stream_analysis()
directamente, con db=None/current_user=None ya que la validación ocurre
antes de que el código toque cualquiera de los dos.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile

from metis.api.v1.analysis import stream_analysis


def _archivo(content: bytes = b"anio,caudal\n1980,94.71\n", filename: str = "serie.csv") -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


@pytest.mark.unit
async def test_cramer_particion_no_default_da_400_no_500():
    with pytest.raises(HTTPException) as exc_info:
        await stream_analysis(
            archivo=_archivo(),
            columna_x="anio",
            columna_y="caudal",
            tipo_variable="caudal_precipitacion",
            etapas="1",
            modo="experto",
            cramer_particion='{"n1_pct": 60, "n2_pct": 30}',
            db=None,
            current_user=None,
        )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"]
        == "CONTRACT_CRAMER_PARTICION_UNSUPPORTED"
    )


@pytest.mark.unit
async def test_cramer_particion_vacio_da_400():
    with pytest.raises(HTTPException) as exc_info:
        await stream_analysis(
            archivo=_archivo(),
            columna_x="anio",
            columna_y="caudal",
            tipo_variable="caudal_precipitacion",
            etapas="1",
            modo="experto",
            cramer_particion="",
            db=None,
            current_user=None,
        )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"]
        == "CONTRACT_CRAMER_PARTICION_UNSUPPORTED"
    )
