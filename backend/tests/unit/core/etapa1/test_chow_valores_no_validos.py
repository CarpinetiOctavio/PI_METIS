"""Chow no ejecutada: los valores que impidieron la prueba — revisión del
19/10/2026 de la DECISIÓN 073 (bloque D del plan de significancia).

Un negativo o un cero no es un atípico de Chow: la prueba trabaja sobre
logaritmos y no se puede calcular. Lo que cambia es que el resultado dice
CUÁLES valores lo impidieron (`valores_no_validos`), para que el gráfico y el
panel de exclusión los señalen sin inferirlos en el navegador.
"""

import json
from pathlib import Path

import pytest

from metis.core.etapa1.outliers import calcular_chow

REFERENCIA = json.loads(
    (Path(__file__).parents[1] / "pipeline/referencia_etapa1_alfa_005.json").read_text(
        encoding="utf-8"
    )
)
BASE = [80.0 + (i * 7) % 30 for i in range(20)]


def _con(posiciones: dict[int, float]) -> list[float]:
    serie = list(BASE)
    for i, v in posiciones.items():
        serie[i] = v
    return serie


@pytest.mark.unit
@pytest.mark.parametrize("tipo", ["caudal_precipitacion", "otro"])
def test_negativos_listan_solo_los_negativos(tipo):
    # Un cero junto a los negativos: gana el motivo de los negativos (DECISIÓN 073)
    # y la lista trae solo los negativos, que son los que nombra el código.
    r = calcular_chow(_con({3: -2.0, 11: 0.0, 15: -0.5}), tipo)

    assert r.warning_codigo == "TEST_NOT_EXECUTED_NEGATIVES"
    assert r.explicacion is None
    assert r.valores_no_validos == [
        {"indice": 3, "valor": -2.0},
        {"indice": 15, "valor": -0.5},
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("tipo", "codigo"),
    [
        ("caudal_precipitacion", "TEST_NOT_EXECUTED_ZEROS"),
        ("otro", "TEST_NOT_EXECUTED_CONDITION"),
    ],
)
def test_ceros_listan_los_ceros(tipo, codigo):
    r = calcular_chow(_con({0: 0.0, 7: 0.0}), tipo)

    assert r.warning_codigo == codigo
    assert r.valores_no_validos == [
        {"indice": 0, "valor": 0.0},
        {"indice": 7, "valor": 0.0},
    ]


@pytest.mark.unit
def test_ejecutada_no_trae_lista():
    assert calcular_chow(BASE, "caudal_precipitacion").valores_no_validos is None


@pytest.mark.unit
def test_serie_con_negativos_otro_senala_los_cinco_negativos():
    caso = REFERENCIA["negativos_otro"]["entrada"]
    r = calcular_chow(caso["serie"], caso["tipo_variable"])

    anios = [caso["timestamps"][v["indice"]] for v in r.valores_no_validos]
    assert anios == [1989, 2005, 2006, 2015, 2019]
    assert all(v["valor"] < 0 for v in r.valores_no_validos)
