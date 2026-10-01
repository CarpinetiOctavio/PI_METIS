"""DECISIÓN 073 — disabled_negatives.

Una serie con valores negativos deja sin ajuste a las cinco distribuciones que no
están definidas para ellos, y lo dice con su propio estado en vez del no_aplicable
genérico. No cambia ningún número. Depende de los datos, no de tipo_variable.
"""

import numpy as np
import pytest

from metis.core.etapa2.distributions import DISABLED_WITH_NEGATIVES, DISABLED_WITH_ZEROS
from metis.core.etapa2.types import (
    STATUS_DISABLED_NEGATIVES,
    STATUS_DISABLED_ZEROS,
    STATUS_OK,
)
from metis.core.pipeline import ejecutar_etapa2

# docs/series prueba/serie_con_negativos_otro.csv — sintética, 5 negativos, sin ceros.
CON_NEGATIVOS = np.array(
    [0.50, 1.27, 0.04, 0.73, 1.72, 0.22, 0.86, 2.33, 2.19, -0.36, 0.35, 1.30, 0.19, 0.89,
     0.97, 0.59, 2.46, 0.89, 1.97, 1.57, 2.19, 0.08, 0.85, 0.70, 1.77, -0.21, -0.74, 0.93,
     0.65, 1.73, 1.55, 1.01, 2.88, 0.89, 2.53, -0.29, 1.08, 0.07, 1.66, -0.37]
)  # fmt: skip
CON_NEGATIVOS_Y_CERO = np.where(CON_NEGATIVOS == 0.04, 0.0, CON_NEGATIVOS)


def _por_nombre(ranking):
    return {d.distribucion: d for d in ranking}


@pytest.mark.unit
def test_las_cinco_quedan_en_disabled_negatives_en_todos_sus_metodos():
    ranking = _por_nombre(ejecutar_etapa2(CON_NEGATIVOS, tiene_negativos=True).ranking)

    assert DISABLED_WITH_NEGATIVES == {
        "lognormal2p", "logpearson3", "gamma2p", "exponencial_beta", "gen_exponencial",
    }  # fmt: skip
    for nombre in DISABLED_WITH_NEGATIVES:
        d = ranking[nombre]
        assert {m.status for m in d.metodos} == {STATUS_DISABLED_NEGATIVES}, nombre
        assert d.mejor_eea is None and d.mejor_metodo is None


@pytest.mark.unit
@pytest.mark.parametrize("nombre", ["normal", "gumbel", "gve", "uniforme"])
def test_las_que_admiten_negativos_siguen_ajustando(nombre):
    d = _por_nombre(ejecutar_etapa2(CON_NEGATIVOS, tiene_negativos=True).ranking)[nombre]
    assert any(m.status == STATUS_OK for m in d.metodos)


@pytest.mark.unit
@pytest.mark.parametrize("nombre", ["lognormal3p", "gamma3p", "exponencial_x0_beta", "gen_pareto"])
def test_las_de_tres_parametros_deciden_por_su_cuenta(nombre):
    # Estiman un parámetro de posición: no reciben el estado nuevo.
    d = _por_nombre(ejecutar_etapa2(CON_NEGATIVOS, tiene_negativos=True).ranking)[nombre]
    assert all(m.status != STATUS_DISABLED_NEGATIVES for m in d.metodos)


@pytest.mark.unit
def test_con_negativos_y_ceros_gana_disabled_negatives():
    ranking = _por_nombre(
        ejecutar_etapa2(CON_NEGATIVOS_Y_CERO, tiene_ceros=True, tiene_negativos=True).ranking
    )
    for nombre in DISABLED_WITH_ZEROS | DISABLED_WITH_NEGATIVES:
        assert {m.status for m in ranking[nombre].metodos} == {STATUS_DISABLED_NEGATIVES}, nombre


@pytest.mark.unit
def test_solo_ceros_no_cambia(serie_facundo):
    serie = np.array(serie_facundo, dtype=float)
    serie[0] = 0.0
    ranking = _por_nombre(ejecutar_etapa2(serie, tiene_ceros=True).ranking)
    for nombre in DISABLED_WITH_ZEROS:
        assert {m.status for m in ranking[nombre].metodos} == {STATUS_DISABLED_ZEROS}, nombre


@pytest.mark.unit
def test_sin_negativos_ningun_numero_cambia(serie_facundo):
    serie = np.array(serie_facundo, dtype=float)
    antes = ejecutar_etapa2(serie).ranking
    despues = ejecutar_etapa2(serie, tiene_negativos=False).ranking
    assert [(d.distribucion, d.mejor_eea) for d in antes] == [
        (d.distribucion, d.mejor_eea) for d in despues
    ]
