import numpy as np
import pytest

from metis.core.etapa2.distributions import DISABLED_WITH_ZEROS
from metis.core.etapa2.types import STATUS_DISABLED_ZEROS
from metis.core.pipeline import ejecutar_etapa2


@pytest.mark.unit
def test_ranking_incluye_las_13_distribuciones(serie_facundo):
    arr = np.array(serie_facundo)
    resultado = ejecutar_etapa2(arr, tiene_ceros=False)
    assert len(resultado.ranking) == 13


@pytest.mark.unit
def test_ranking_ordenado_ascendente_por_mejor_eea(serie_facundo):
    arr = np.array(serie_facundo)
    resultado = ejecutar_etapa2(arr, tiene_ceros=False)

    con_eea = [d.mejor_eea for d in resultado.ranking if d.mejor_eea is not None]
    assert con_eea == sorted(con_eea)

    # Las distribuciones sin ajuste válido (mejor_eea=None) van al final.
    posiciones_none = [
        i for i, d in enumerate(resultado.ranking) if d.mejor_eea is None
    ]
    posiciones_con_eea = [
        i for i, d in enumerate(resultado.ranking) if d.mejor_eea is not None
    ]
    if posiciones_none and posiciones_con_eea:
        assert min(posiciones_none) > max(posiciones_con_eea)


@pytest.mark.unit
def test_tiene_ceros_deshabilita_distribuciones_marcadas(serie_facundo):
    arr = np.array(serie_facundo)
    resultado = ejecutar_etapa2(arr, tiene_ceros=True)

    deshabilitadas = [
        d for d in resultado.ranking if d.distribucion in DISABLED_WITH_ZEROS
    ]
    assert len(deshabilitadas) == len(DISABLED_WITH_ZEROS)
    for dist in deshabilitadas:
        assert dist.mejor_eea is None
        assert dist.mejor_metodo is None
        assert all(m.status == STATUS_DISABLED_ZEROS for m in dist.metodos)


@pytest.mark.unit
def test_sin_ceros_no_deshabilita_distribuciones_marcadas(serie_facundo):
    arr = np.array(serie_facundo)
    resultado = ejecutar_etapa2(arr, tiene_ceros=False)

    afectadas = [d for d in resultado.ranking if d.distribucion in DISABLED_WITH_ZEROS]
    assert len(afectadas) == len(DISABLED_WITH_ZEROS)
    for dist in afectadas:
        assert not all(m.status == STATUS_DISABLED_ZEROS for m in dist.metodos)


@pytest.mark.unit
def test_mejor_eea_corresponde_al_minimo_entre_metodos_ok(serie_facundo):
    arr = np.array(serie_facundo)
    resultado = ejecutar_etapa2(arr, tiene_ceros=False)

    for dist in resultado.ranking:
        eeas_ok = [
            m.eea for m in dist.metodos if m.status == "ok" and m.eea is not None
        ]
        if eeas_ok:
            assert dist.mejor_eea == pytest.approx(min(eeas_ok))
        else:
            assert dist.mejor_eea is None
            assert dist.mejor_metodo is None
