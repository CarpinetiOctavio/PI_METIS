import numpy as np
import pytest

from metis.core.etapa2.distributions import gamma3p
from metis.core.etapa2.types import STATUS_OK


# ── Momentos — IV-138/139 corregidos (√β̂) ────────────────────────────────────


@pytest.mark.unit
def test_gamma3p_momentos_alpha_raiz_beta(serie_facundo):
    # IV-138: α̂ = S/√β̂  (no S/β̂).
    # g por IV-4/IV-5 (ddof=0, DECISIÓN013) — mismo cálculo que descriptive.py,
    # no la convención de Excel SKEW() (ddof=1) que tenía este test antes.
    arr = np.array(serie_facundo)
    n = len(arr)
    xbar = float(np.mean(arr))
    S = float(np.std(arr, ddof=1))
    var_sesgada = float(np.var(arr, ddof=0))
    g_sesg = float(np.mean((arr - xbar) ** 3) / var_sesgada**1.5)
    g = float((n**2 / ((n - 1) * (n - 2))) * g_sesg)
    beta = 4.0 / g**2
    alpha_esp = S / np.sqrt(beta)

    res = gamma3p.ajustar(arr, "momentos")

    assert res.status == STATUS_OK
    assert res.parametros["alpha"] == pytest.approx(alpha_esp, abs=1e-6)


@pytest.mark.unit
def test_gamma3p_momentos_x0_raiz_beta(serie_facundo):
    # IV-139: x̂₀ = x̄ - S·√β̂  (no x̄ - S·β̂).
    # g por IV-4/IV-5 (ddof=0, DECISIÓN013) — mismo cálculo que descriptive.py,
    # no la convención de Excel SKEW() (ddof=1) que tenía este test antes.
    arr = np.array(serie_facundo)
    n = len(arr)
    xbar = float(np.mean(arr))
    S = float(np.std(arr, ddof=1))
    var_sesgada = float(np.var(arr, ddof=0))
    g_sesg = float(np.mean((arr - xbar) ** 3) / var_sesgada**1.5)
    g = float((n**2 / ((n - 1) * (n - 2))) * g_sesg)
    beta = 4.0 / g**2
    x0_esp = xbar - S * np.sqrt(beta)

    res = gamma3p.ajustar(arr, "momentos")

    assert res.status == STATUS_OK
    assert res.parametros["x0"] == pytest.approx(x0_esp, abs=1e-6)


@pytest.mark.unit
def test_gamma3p_momentos_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gamma3p.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["beta"] == pytest.approx(5.5715, abs=1e-3)
    assert res.parametros["alpha"] == pytest.approx(7.5098, abs=1e-3)
    assert res.parametros["x0"] == pytest.approx(0.9269, abs=1e-3)


@pytest.mark.unit
def test_gamma3p_momentos_q100_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gamma3p.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    q100 = gamma3p.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(94.6964, abs=1e-1)
