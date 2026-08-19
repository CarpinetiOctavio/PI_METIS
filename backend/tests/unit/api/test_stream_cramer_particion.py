"""
Tests unitarios de la validación de cramer_particion en POST /analysis/stream
(DECISIÓN 036, Bloque H1 del plan post-avance).

Historia: antes de la pasada 5, cualquier valor distinto de "default" llegaba
como str a calcular_cramer() y producía un TypeError no manejado -> 500. La
pasada 5 cerró el 500 con una guarda que rechazaba TODO valor no-default
(CONTRACT_CRAMER_PARTICION_UNSUPPORTED) — la funcionalidad seguía sin existir.
Este bloque implementa la opción 1 real: "default" pasa tal cual, cualquier
otro valor se parsea como JSON y se valida — si es válido, se manda a
services/ como dict; si no, 400 CONTRACT_CRAMER_PARTICION_INVALID.

Mismo patrón que test_stream_etapas_validacion.py: llamar a stream_analysis()
directamente, con db=None/current_user=None — la validación ocurre antes de
que el código toque cualquiera de los dos, y el generador SSE es lazy (no
ejecuta su cuerpo hasta que algo lo itera).
"""

import io

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from metis.api.v1.analysis import _parsear_cramer_particion, stream_analysis


def _archivo(
    content: bytes = b"anio,caudal\n1980,94.71\n", filename: str = "serie.csv"
) -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


async def _llamar(cramer_particion: str):
    return await stream_analysis(
        archivo=_archivo(),
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="caudal_precipitacion",
        etapas="1",
        modo="experto",
        cramer_particion=cramer_particion,
        mes_inicio_anio=7,
        db=None,
        current_user=None,
    )


# ── _parsear_cramer_particion — unidad ───────────────────────────────────────


@pytest.mark.unit
def test_parsear_default_pasa_tal_cual():
    assert _parsear_cramer_particion("default") == "default"


@pytest.mark.unit
def test_parsear_json_valido_da_dict():
    resultado = _parsear_cramer_particion('{"n1_pct": 60, "n2_pct": 30}')
    assert resultado == {"n1_pct": 60.0, "n2_pct": 30.0}


@pytest.mark.unit
def test_parsear_json_malformado_da_400():
    with pytest.raises(HTTPException) as exc_info:
        _parsear_cramer_particion("no es json")
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )


@pytest.mark.unit
def test_parsear_vacio_da_400():
    with pytest.raises(HTTPException) as exc_info:
        _parsear_cramer_particion("")
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "payload",
    [
        '{"n1_pct": 0, "n2_pct": 30}',  # fuera de rango (< 1)
        '{"n1_pct": 101, "n2_pct": 30}',  # fuera de rango (> 100)
        '{"n1_pct": 60}',  # falta n2_pct
        '{"n1_pct": "sesenta", "n2_pct": 30}',  # no numérico
        "[60, 30]",  # forma equivocada (no es objeto)
    ],
)
def test_parsear_forma_o_rango_invalido_da_400(payload):
    with pytest.raises(HTTPException) as exc_info:
        _parsear_cramer_particion(payload)
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )


@pytest.mark.unit
def test_parsear_n1_igual_n2_da_400():
    # Ni siquiera empatados — el bloque 1 tiene que ser estrictamente el
    # período más largo.
    with pytest.raises(HTTPException) as exc_info:
        _parsear_cramer_particion('{"n1_pct": 30, "n2_pct": 30}')
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )


@pytest.mark.unit
def test_parsear_n1_menor_a_n2_da_400():
    # Invertidos — Cramer no mide lo que dice medir si el "período largo"
    # es en realidad el más corto.
    with pytest.raises(HTTPException) as exc_info:
        _parsear_cramer_particion('{"n1_pct": 20, "n2_pct": 60}')
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )


# ── stream_analysis() — integración con el endpoint ──────────────────────────


@pytest.mark.unit
async def test_default_no_lanza():
    respuesta = await _llamar("default")
    assert isinstance(respuesta, StreamingResponse)


@pytest.mark.unit
async def test_particion_custom_valida_no_lanza():
    # Antes de este bloque, esto daba 400 UNSUPPORTED sin importar que el
    # JSON fuera perfectamente válido — es el caso que este bloque existe
    # para arreglar.
    respuesta = await _llamar('{"n1_pct": 60, "n2_pct": 30}')
    assert isinstance(respuesta, StreamingResponse)


@pytest.mark.unit
async def test_particion_custom_invalida_da_400_no_500():
    with pytest.raises(HTTPException) as exc_info:
        await _llamar('{"n1_pct": 20, "n2_pct": 60}')
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )


@pytest.mark.unit
async def test_vacio_da_400_no_500():
    with pytest.raises(HTTPException) as exc_info:
        await _llamar("")
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"] == "CONTRACT_CRAMER_PARTICION_INVALID"
    )
