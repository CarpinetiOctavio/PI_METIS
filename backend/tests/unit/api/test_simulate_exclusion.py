"""POST /analysis/simulate-exclusion (DECISIÓN 071).

Mismo patrón que test_distribution_decision.py: llamar a la función del endpoint
directamente, no vía TestClient. No tiene dependencia de usuario: responde igual
con o sin cookie (no hay `current_user` que pasarle).
"""

import pytest
from fastapi import HTTPException

from metis.api.v1.analysis import simulate_exclusion
from metis.core.pipeline import ejecutar_etapa1
from metis.schemas.analysis import SimulateExclusionRequest
from metis.services.analysis_service import _serializar_etapa1

# 15 años con un atípico evidente en la posición 10.
SERIE = [60.0 + (i * 7) % 40 for i in range(15)]
SERIE[10] = 5000.0
ANIOS = list(range(2000, 2015))


def _body(**overrides) -> SimulateExclusionRequest:
    datos = {
        "serie": SERIE,
        "anios": ANIOS,
        "tipo_variable": "caudal_precipitacion",
        "cramer_particion": "default",
        "indices_excluidos": [10],
        "etapas": [1],
    }
    datos.update(overrides)
    return SimulateExclusionRequest(**datos)


@pytest.mark.unit
async def test_200_sin_el_punto_y_con_lo_excluido():
    r = await simulate_exclusion(_body())

    assert r["serie"] == SERIE[:10] + SERIE[11:]
    assert r["anios"] == ANIOS[:10] + ANIOS[11:]
    assert r["excluidos"] == [{"indice": 10, "periodo": 2010, "valor_original": 5000.0}]
    assert r["etapa2"] is None
    assert len(r["etapa1"]["datos"]["serie_efectiva"]) == 14


@pytest.mark.unit
async def test_con_etapa_2_devuelve_el_ranking_completo_sin_seleccion():
    r = await simulate_exclusion(_body(etapas=[1, 2]))

    assert len(r["etapa2"]["ranking"]) == 13
    assert r["etapa2"]["seleccion"] is None


@pytest.mark.unit
async def test_sin_exclusiones_etapa1_identica_al_analisis_original():
    # Regresión 1 del plan de backend: con [] no puede haber dos criterios.
    original = _serializar_etapa1(
        ejecutar_etapa1(SERIE, "caudal_precipitacion", "anual", timestamps=ANIOS),
        mes_inicio_anio=7,
    )
    r = await simulate_exclusion(_body(indices_excluidos=[]))
    assert r["etapa1"] == original


@pytest.mark.unit
async def test_menos_de_10_datos_responde_el_bloqueante_de_siempre_dentro_de_etapa1():
    r = await simulate_exclusion(_body(indices_excluidos=list(range(6)), etapas=[1, 2]))

    assert r["etapa1"]["nivel_confianza"] == "rechazado"
    assert r["etapa1"]["contract"]["bloqueante"] is True
    assert r["etapa1"]["contract"]["codigo_error"] == "CONTRACT_SERIES_TOO_SHORT"
    assert r["etapa2"] is None


@pytest.mark.unit
@pytest.mark.parametrize(
    ("overrides", "codigo"),
    [
        ({"indices_excluidos": [10, 10]}, "CONTRACT_EXCLUSION_INVALID"),
        ({"indices_excluidos": [15]}, "CONTRACT_EXCLUSION_INVALID"),
        ({"anios": ANIOS[:-1]}, "CONTRACT_EXCLUSION_INVALID"),
        ({"tratamiento": "media"}, "CONTRACT_EXCLUSION_INVALID"),
        ({"serie": [], "anios": [], "indices_excluidos": []}, "CONTRACT_SERIES_INVALID"),
        ({"serie": [1.0] * 501, "anios": list(range(501)), "indices_excluidos": []}, "CONTRACT_SERIES_INVALID"),
        ({"serie": [float("nan")] + SERIE[1:]}, "CONTRACT_SERIES_INVALID"),
        ({"etapas": [2]}, "CONTRACT_ETAPAS_INVALID"),
        ({"cramer_particion": "{\"n1_pct\": 20, \"n2_pct\": 60}"}, "CONTRACT_CRAMER_PARTICION_INVALID"),
    ],
    ids=[
        "indice-repetido", "indice-fuera", "largos-distintos", "tratamiento", "serie-vacia",
        "mas-de-500", "no-finito", "etapas", "cramer",
    ],
)  # fmt: skip
async def test_400_con_su_codigo(overrides, codigo):
    with pytest.raises(HTTPException) as exc_info:
        await simulate_exclusion(_body(**overrides))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == codigo
