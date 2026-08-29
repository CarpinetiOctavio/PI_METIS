"""
Tests unitarios de la validación de etapas en POST /analysis/stream
(DECISIÓN 054, cierra DECISIÓN 037). Antes de esto el campo se recibía
y se descartaba sin validar; ahora se parsea a list[int] en el borde y
cualquier valor fuera de {"1", "1,2"} responde 400 CONTRACT_ETAPAS_INVALID.

Mismo patrón que test_stream_cramer_particion.py: llamar a stream_analysis()
directamente, con db=None/current_user=None ya que la validación ocurre
antes de que el código toque cualquiera de los dos.
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


@pytest.mark.unit
async def test_etapas_uno_dos_no_lanza():
    # "1,2" es válida — el generador SSE es lazy (no ejecuta su cuerpo hasta
    # que algo lo itera), así que construir el StreamingResponse no toca db
    # ni current_user todavía y no debe lanzar nada.
    respuesta = await stream_analysis(
        archivo=_archivo(),
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="caudal_precipitacion",
        etapas="1,2",
        modo="experto",
        cramer_particion="default",
        mes_inicio_anio=7,
        variable_diaria="pico",
        db=None,
        current_user=None,
    )

    assert isinstance(respuesta, StreamingResponse)
    assert respuesta.media_type == "text/event-stream"


@pytest.mark.unit
async def test_etapas_invalida_da_400_no_500():
    with pytest.raises(HTTPException) as exc_info:
        await stream_analysis(
            archivo=_archivo(),
            columna_x="anio",
            columna_y="caudal",
            tipo_variable="caudal_precipitacion",
            etapas="2",
            modo="experto",
            cramer_particion="default",
            mes_inicio_anio=7,
            variable_diaria="pico",
            db=None,
            current_user=None,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "CONTRACT_ETAPAS_INVALID"


@pytest.mark.unit
async def test_etapas_vacia_da_400():
    with pytest.raises(HTTPException) as exc_info:
        await stream_analysis(
            archivo=_archivo(),
            columna_x="anio",
            columna_y="caudal",
            tipo_variable="caudal_precipitacion",
            etapas="",
            modo="experto",
            cramer_particion="default",
            mes_inicio_anio=7,
            variable_diaria="pico",
            db=None,
            current_user=None,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "CONTRACT_ETAPAS_INVALID"


@pytest.mark.unit
async def test_etapas_invalida_se_valida_antes_de_leer_el_archivo():
    """La validación de etapas corre después de cramer_particion pero antes
    de _leer_archivo_limitado() — un archivo enorme con etapas inválida
    debe fallar rápido por CONTRACT_ETAPAS_INVALID, no gastar tiempo leyendo
    el archivo primero."""
    archivo_grande = _archivo(content=b"x" * (11 * 1024 * 1024))

    with pytest.raises(HTTPException) as exc_info:
        await stream_analysis(
            archivo=archivo_grande,
            columna_x="anio",
            columna_y="caudal",
            tipo_variable="caudal_precipitacion",
            etapas="3",
            modo="experto",
            cramer_particion="default",
            mes_inicio_anio=7,
            variable_diaria="pico",
            db=None,
            current_user=None,
        )

    assert exc_info.value.detail["error"]["codigo"] == "CONTRACT_ETAPAS_INVALID"
