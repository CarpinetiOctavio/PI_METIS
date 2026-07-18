import numpy as np
import pytest

from metis.core.etapa2.distributions import exponencial_x0_beta
from metis.core.etapa2.types import STATUS_OK


# ── MV — IV-72 denominador corregido (n-1, no n·(n-1)) ──────────────────────


@pytest.mark.unit
def test_exp_x0_beta_mv_beta_formula_correcta(serie_facundo):
    # IV-72: β̂ = (Σxi - n·x1) / (n-1).
    # El denominador viejo era n·(n-1), produciendo β 40x menor.
    arr = np.array(serie_facundo)
    n = len(arr)
    x1 = float(np.min(arr))
    beta_esp = (float(np.sum(arr)) - n * x1) / (n - 1)

    res = exponencial_x0_beta.ajustar(arr, "mv")

    assert res.status == STATUS_OK
    assert res.parametros["beta"] == pytest.approx(beta_esp, abs=1e-6)


@pytest.mark.unit
def test_exp_x0_beta_mv_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = exponencial_x0_beta.ajustar(arr, "mv")
    assert res.status == STATUS_OK
    assert res.parametros["beta"] == pytest.approx(22.2231, abs=1e-3)
    assert res.parametros["x0"] == pytest.approx(20.5444, abs=1e-3)


@pytest.mark.unit
def test_exp_x0_beta_mv_q100_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = exponencial_x0_beta.ajustar(arr, "mv")
    assert res.status == STATUS_OK
    q100 = exponencial_x0_beta.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(122.8855, abs=1e-1)
