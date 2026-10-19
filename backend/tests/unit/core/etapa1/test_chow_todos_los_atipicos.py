"""Chow con todos los valores fuera de los umbrales — DECISIÓN 079.

Bulletin 17B: umbral alto ȳ + K_N·S y bajo ȳ − K_N·S sobre los logaritmos, y
todo valor más allá de su umbral es atípico, no solo el más extremo. Una sola
pasada. El gráfico de Chow dibuja exactamente `limite_inferior`/`limite_superior`,
así que lo que queda fuera de las franjas y la lista tienen que coincidir.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from metis.core.etapa1.outliers import calcular_chow

_BASE = list(np.random.default_rng(3).lognormal(4.6, 0.15, 37))
# Dos atípicos bajos (posiciones 5 y 21) y uno alto (posición 39).
SERIE_TRES = _BASE[:5] + [3.0] + _BASE[5:20] + [2.0] + _BASE[20:] + [9000.0]

REFERENCIA = json.loads(
    (Path(__file__).parents[1] / "pipeline/referencia_etapa1_alfa_005.json").read_text(
        encoding="utf-8"
    )
)


@pytest.mark.unit
def test_dos_bajos_y_uno_alto_salen_los_tres_con_su_lado_ordenados_por_z():
    r = calcular_chow(SERIE_TRES, "caudal_precipitacion")

    assert r.veredicto == "rechazada"
    assert [(a["indice"], a["lado"]) for a in r.valores_atipicos] == [
        (39, "alto"),
        (21, "bajo"),
        (5, "bajo"),
    ]
    assert [a["valor"] for a in r.valores_atipicos] == [9000.0, 2.0, 3.0]
    # Compatibilidad: valor_atipico/indice_atipico siguen siendo el más extremo.
    assert r.indice_atipico == 39
    assert r.valor_atipico == 9000.0
    assert r.estadistico == pytest.approx(abs(r.valores_atipicos[0]["z"]))


@pytest.mark.unit
def test_sin_atipicos_la_lista_queda_vacia():
    # La serie de test_persistencia.py: todas las pruebas aprueban.
    serie = list(np.random.default_rng(seed=9).uniform(10, 100, size=50))
    r = calcular_chow(serie, "caudal_precipitacion")
    assert r.veredicto == "aprobada"
    assert r.valores_atipicos == []
    assert r.valor_atipico is None


@pytest.mark.unit
def test_no_ejecutada_no_trae_lista():
    r = calcular_chow([0.0] + [10.0] * 14, "caudal_precipitacion")
    assert r.valores_atipicos is None


@pytest.mark.unit
def test_serie_diaria_de_40_anios_marca_1994_y_2005():
    # La serie de la captura del 18/10/2026, ya agregada a máximos anuales: el
    # gráfico mostraba dos puntos fuera de la franja y la prueba marcaba uno.
    caso = REFERENCIA["diaria_40anios_agregada"]["entrada"]
    r = calcular_chow(caso["serie"], caso["tipo_variable"])

    anios = sorted(caso["timestamps"][a["indice"]] for a in r.valores_atipicos)
    assert anios == [1994, 2005]


@pytest.mark.unit
@pytest.mark.parametrize("semilla", range(30))
@pytest.mark.parametrize("alfa", [0.01, 0.05, 0.10])
def test_fuera_de_las_franjas_si_y_solo_si_esta_en_la_lista(semilla, alfa):
    rng = np.random.default_rng(semilla)
    serie = list(rng.lognormal(4.5, 0.5, int(rng.integers(12, 60))))
    for _ in range(int(rng.integers(0, 4))):
        serie[int(rng.integers(0, len(serie)))] *= rng.choice([0.05, 12.0])

    r = calcular_chow(serie, "caudal_precipitacion", alfa=alfa)
    t = r.explicacion.terminos
    fuera = {
        i
        for i, v in enumerate(serie)
        if v < t["limite_inferior"] or v > t["limite_superior"]
    }

    assert fuera == {a["indice"] for a in r.valores_atipicos}
    for a in r.valores_atipicos:
        assert a["lado"] == (
            "alto" if serie[a["indice"]] > t["limite_superior"] else "bajo"
        )


@pytest.mark.unit
def test_las_9_estaciones_de_la_tesis_siguen_sin_atipicos():
    # est_09 tiene n = 7: el contrato la bloquea antes de llegar a Chow.
    for clave in (f"est_0{i}" for i in range(1, 9)):
        caso = REFERENCIA[clave]["entrada"]
        r = calcular_chow(caso["serie"], caso["tipo_variable"])
        assert r.valores_atipicos == [], clave
