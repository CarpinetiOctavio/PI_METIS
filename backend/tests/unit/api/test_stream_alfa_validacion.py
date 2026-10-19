"""
Validación de `alfa` en el borde (DECISIÓN 078): POST /analysis/stream y
POST /analysis/simulate-exclusion solo aceptan 0.01, 0.05 y 0.10; cualquier
otro valor, también uno no numérico, responde 400 CONTRACT_ALFA_INVALID antes
de tocar el archivo o el pipeline.

Mismo patrón que test_stream_variable_diaria_validacion.py.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from metis.api.v1.analysis import simulate_exclusion, stream_analysis
from metis.schemas.analysis import SimulateExclusionRequest


async def _llamar(alfa: str):
    return await stream_analysis(
        archivo=UploadFile(
            file=io.BytesIO(b"anio,caudal\n1980,94.71\n"), filename="s.csv"
        ),
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="caudal_precipitacion",
        etapas="1",
        modo="experto",
        cramer_particion="default",
        mes_inicio_anio=7,
        variable_diaria="pico",
        alfa=alfa,
        db=None,
        current_user=None,
    )


@pytest.mark.unit
@pytest.mark.parametrize("valor", ["0.01", "0.05", "0.10", "0.1", "0.050"])
async def test_valores_validos_no_lanzan(valor):
    assert isinstance(await _llamar(valor), StreamingResponse)


@pytest.mark.unit
@pytest.mark.parametrize("valor", ["0.2", "0.025", "5", "abc", "", "nan", "inf"])
async def test_valor_invalido_da_400(valor):
    with pytest.raises(HTTPException) as exc_info:
        await _llamar(valor)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "CONTRACT_ALFA_INVALID"


def _simulacion(alfa: float) -> SimulateExclusionRequest:
    return SimulateExclusionRequest(
        serie=[60.0 + (i * 7) % 40 for i in range(15)],
        anios=list(range(2000, 2015)),
        tipo_variable="caudal_precipitacion",
        indices_excluidos=[3],
        etapas=[1],
        alfa=alfa,
    )


@pytest.mark.unit
async def test_simulate_exclusion_aplica_el_alfa_pedido():
    r = await simulate_exclusion(_simulacion(0.10))
    assert r["etapa1"]["alfa"] == 0.10
    wald = next(
        t for t in r["etapa1"]["independencia"] if t["prueba"] == "wald_wolfowitz"
    )
    assert wald["valor_critico"] == pytest.approx(1.645, abs=5e-4)


@pytest.mark.unit
async def test_simulate_exclusion_sin_alfa_usa_5_por_ciento():
    body = _simulacion(0.05).model_dump(exclude={"alfa"})
    r = await simulate_exclusion(SimulateExclusionRequest(**body))
    assert r["etapa1"]["alfa"] == 0.05


@pytest.mark.unit
async def test_simulate_exclusion_alfa_invalido_da_400():
    with pytest.raises(HTTPException) as exc_info:
        await simulate_exclusion(_simulacion(0.2))
    assert exc_info.value.detail["error"]["codigo"] == "CONTRACT_ALFA_INVALID"
