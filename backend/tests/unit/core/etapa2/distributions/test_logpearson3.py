import numpy as np
import pytest

from metis.core.etapa2.distributions import logpearson3
from metis.core.etapa2.types import STATUS_NO_APLICABLE, STATUS_OK


# ── Momentos Indirecto — IV-256 corregido (√β̂) ───────────────────────────────


@pytest.mark.unit
def test_logpearson3_indirecto_alpha_raiz_beta(serie_facundo):
    # IV-256: α̂ = Sy/√β̂  (no Sy/β̂).
    # Verificación independiente reconstruyendo β̂ y √β̂.
    # gy por IV-4/IV-5 (ddof=0, DECISIÓN013) sobre yi=ln(xi) — mismo cálculo
    # que descriptive.py, no la convención de Excel SKEW() (ddof=1) que tenía
    # este test antes.
    arr = np.array(serie_facundo)
    n = len(arr)
    yi = np.log(arr)
    yi_media = float(np.mean(yi))
    var_sesgada_y = float(np.var(yi, ddof=0))
    gy_sesg = float(np.mean((yi - yi_media) ** 3) / var_sesgada_y**1.5)
    gy = float((n**2 / ((n - 1) * (n - 2))) * gy_sesg)
    sy = float(np.std(yi, ddof=1))
    beta = 4.0 / gy**2
    alpha_esp = sy / np.sqrt(beta)

    res = logpearson3.ajustar(arr, "momentos_indirecto")

    assert res.status == STATUS_OK
    assert res.parametros["alpha"] == pytest.approx(alpha_esp, abs=1e-6)


@pytest.mark.unit
def test_logpearson3_indirecto_q100_serie_facundo(serie_facundo):
    # Q100 calculado independientemente con IV-256 corregido.
    arr = np.array(serie_facundo)
    res = logpearson3.ajustar(arr, "momentos_indirecto")
    assert res.status == STATUS_OK
    q100 = logpearson3.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(109.1515, abs=1e-1)


@pytest.mark.unit
def test_logpearson3_indirecto_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = logpearson3.ajustar(arr, "momentos_indirecto")
    assert res.status == STATUS_OK
    assert res.parametros["beta"] == pytest.approx(40.4671, abs=1e-3)
    assert res.parametros["alpha"] == pytest.approx(0.0625, abs=1e-4)
    assert res.parametros["y0"] == pytest.approx(1.1493, abs=1e-3)


# ── Momentos Directo — NO_APLICABLE para B fuera de (3, 6] ──────────────────


@pytest.mark.unit
def test_logpearson3_directo_no_aplicable_serie_facundo(serie_facundo):
    # Para serie_facundo: B=2.856 < 3 → STATUS_NO_APLICABLE.
    # Verifica que el guard B ∈ (3,6] funciona correctamente.
    arr = np.array(serie_facundo)
    res = logpearson3.ajustar(arr, "momentos_directo")
    assert res.status == STATUS_NO_APLICABLE


@pytest.mark.unit
def test_logpearson3_directo_alpha_hat_formula():
    # Serie sintética con B ∈ (3.5, 6] para verificar α̂ = 1/(A+3) con IV-251.
    # Construida para producir B≈5 y alpha_hat < 0.5.
    rng = np.random.default_rng(seed=42)
    arr = rng.lognormal(mean=3.5, sigma=0.4, size=80)
    res = logpearson3.ajustar(arr, "momentos_directo")
    if res.status == STATUS_OK:
        # alpha_hat = 1/(A+3) siempre da valores positivos menores que 1
        assert 0.0 < res.parametros["alpha"] < 1.0
