import numpy as np
import pytest

from metis.core.etapa2.distributions import gumbel
from metis.core.etapa2.types import STATUS_OK


# ── Momentos ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gumbel_momentos_parametros(serie_facundo):
    arr = np.array(serie_facundo)
    xbar = float(np.mean(arr))
    S = float(np.std(arr, ddof=1))
    mu_esp = xbar - 0.45 * S  # IV-177
    alpha_esp = 0.78 * S  # IV-178

    res = gumbel.ajustar(arr, "momentos")

    assert res.status == STATUS_OK
    assert res.parametros["mu"] == pytest.approx(mu_esp, abs=1e-6)
    assert res.parametros["alpha"] == pytest.approx(alpha_esp, abs=1e-6)


# ── MV ────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gumbel_mv_converge_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gumbel.ajustar(arr, "mv")
    assert res.status == STATUS_OK


@pytest.mark.unit
def test_gumbel_mv_parametros_serie_facundo(serie_facundo):
    # Valores calculados independientemente con coeficiente IV-184 = 1.11.
    # Fuente: iteración manual en smoke test — delta_mu = alpha*(1.11·P - 0.26·R)/n.
    arr = np.array(serie_facundo)
    res = gumbel.ajustar(arr, "mv")
    assert res.parametros["mu"] == pytest.approx(34.7998, abs=1e-3)
    assert res.parametros["alpha"] == pytest.approx(12.8654, abs=1e-3)


@pytest.mark.unit
def test_gumbel_mv_q100_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gumbel.ajustar(arr, "mv")
    q100 = gumbel.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(93.9828, abs=1e-2)


# ── Cuantil ───────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gumbel_cuantil_p_fuera_rango_levanta_error(serie_facundo):
    arr = np.array(serie_facundo)
    res = gumbel.ajustar(arr, "momentos")
    with pytest.raises(ValueError):
        gumbel.cuantil(0.0, res.parametros)
    with pytest.raises(ValueError):
        gumbel.cuantil(1.0, res.parametros)
