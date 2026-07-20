import numpy as np
import pytest

from metis.core.etapa2.distributions import gve
from metis.core.etapa2.types import STATUS_OK


# ── Momentos — IV-203/204 rangos de g ────────────────────────────────────────


@pytest.mark.unit
def test_gve_momentos_converge_serie_facundo(serie_facundo):
    # g=0.816 < 1.1396 → IV-203. El fix de rangos no cambia el resultado.
    arr = np.array(serie_facundo)
    res = gve.ajustar(arr, "momentos")
    assert res.status == STATUS_OK


@pytest.mark.unit
def test_gve_momentos_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gve.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["nu"] == pytest.approx(34.8565, abs=1e-3)
    assert res.parametros["alpha"] == pytest.approx(14.1620, abs=1e-3)
    assert res.parametros["beta"] == pytest.approx(0.0191, abs=1e-3)


@pytest.mark.unit
def test_gve_momentos_g_en_rango_iv204_usa_polinomio_correcto():
    # Con g=4.65 (> 1.1396) el fix cambia de IV-203 a IV-204.
    # IV-203 daría beta=-1.386; IV-204 correcto da beta≈-0.244.
    # Serie: log-normal seed=7, sigma=1.5, n=50.
    # g por IV-4/IV-5 (ddof=0, DECISIÓN013) — mismo cálculo que descriptive.py,
    # no la convención de Excel SKEW() (ddof=1) que tenía este test antes.
    rng = np.random.default_rng(7)
    arr = rng.lognormal(0, 1.5, size=50)
    n = len(arr)
    xbar, S = float(np.mean(arr)), float(np.std(arr, ddof=1))
    var_sesgada = float(np.var(arr, ddof=0))
    g_sesg = float(np.mean((arr - xbar) ** 3) / var_sesgada**1.5)
    g = float((n**2 / ((n - 1) * (n - 2))) * g_sesg)
    assert 1.14 < g < 18.95, f"g={g} fuera del rango IV-204"

    # Beta esperado por IV-204
    beta_iv204 = (
        0.25031
        - 0.29219 * g
        + 0.075357 * g**2
        - 0.010883 * g**3
        + 0.000904 * g**4
        - 0.000043 * g**5
    )

    res = gve.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["beta"] == pytest.approx(beta_iv204, abs=1e-6)


# ── ML ────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gve_ml_converge_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gve.ajustar(arr, "ml")
    assert res.status == STATUS_OK


@pytest.mark.unit
def test_gve_ml_q100_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gve.ajustar(arr, "ml")
    assert res.status == STATUS_OK
    q100 = gve.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(109.0541, abs=1e-1)


# ── Cuantil β→0: límite Gumbel, no ValueError ────────────────────────────────


@pytest.mark.unit
def test_gve_cuantil_beta_cero_retorna_gumbel():
    # Antes del fix levantaba ValueError. Ahora debe retornar el límite de Gumbel.
    # Para β→0: xT = ν - α·ln(-ln(F(x)))  (idéntico a cuantil Gumbel)
    nu, alpha = 35.0, 13.0
    params = {"nu": nu, "alpha": alpha, "beta": 1e-12}
    p = 0.99
    esperado = float(nu - alpha * np.log(-np.log(p)))
    resultado = gve.cuantil(p, params)
    assert resultado == pytest.approx(esperado, abs=1e-6)


@pytest.mark.unit
def test_gve_cuantil_p_fuera_rango_levanta_error(serie_facundo):
    arr = np.array(serie_facundo)
    res = gve.ajustar(arr, "ml")
    with pytest.raises(ValueError):
        gve.cuantil(0.0, res.parametros)
    with pytest.raises(ValueError):
        gve.cuantil(1.0, res.parametros)
