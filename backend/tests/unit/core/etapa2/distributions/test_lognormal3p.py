import numpy as np
import pytest

from metis.core.etapa2.distributions import lognormal3p
from metis.core.etapa2.types import STATUS_OK


# ── Momentos IV-116 — raíz cuadrada ──────────────────────────────────────────


@pytest.mark.unit
def test_lognormal3p_momentos_sigma_y_raiz_cuadrada(serie_facundo):
    # IV-116 define σ̂y = [ln(nz²+1)]^(1/2) directo, no σ̂²y — ver DECISIÓN015
    # (docs/decisiones/decision015.md). Exponente 1/2, no 1/4.
    # Verificación independiente: reconstruir nz a partir de g, nx, w.
    # g por IV-4/IV-5 (ddof=0, DECISIÓN013) — mismo cálculo que descriptive.py,
    # no la convención de Excel SKEW() (ddof=1) que tenía este test antes.
    arr = np.array(serie_facundo)
    n = len(arr)
    xbar = float(np.mean(arr))
    S = float(np.std(arr, ddof=1))
    var_sesgada = float(np.var(arr, ddof=0))
    g_sesg = float(np.mean((arr - xbar) ** 3) / var_sesgada**1.5)
    g = float((n**2 / ((n - 1) * (n - 2))) * g_sesg)
    w = ((g**2 + 4.0) ** 0.5 - g) / 2.0
    nz = (1.0 - w ** (2.0 / 3.0)) / w ** (1.0 / 3.0)
    sigma_y_esp = float(np.log(nz**2 + 1.0) ** 0.5)

    res = lognormal3p.ajustar(arr, "momentos")

    assert res.status == STATUS_OK
    assert res.parametros["sigma_y"] == pytest.approx(sigma_y_esp, abs=1e-6)


@pytest.mark.unit
def test_lognormal3p_momentos_q100_serie_facundo(serie_facundo):
    # Q100 calculado independientemente con IV-116 corregido.
    arr = np.array(serie_facundo)
    res = lognormal3p.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    q100 = lognormal3p.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(94.8172, abs=1e-1)


@pytest.mark.unit
def test_lognormal3p_momentos_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = lognormal3p.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["mu_y"] == pytest.approx(4.1277, abs=1e-3)
    assert res.parametros["sigma_y"] == pytest.approx(0.2704, abs=1e-3)
    assert res.parametros["x0"] == pytest.approx(-21.5810, abs=1e-2)
