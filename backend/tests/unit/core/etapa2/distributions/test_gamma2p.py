import numpy as np
import pytest

from metis.core.etapa2.distributions import gamma2p
from metis.core.etapa2.types import STATUS_OK


# ── Momentos ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gamma2p_momentos_parametros_serie_facundo(serie_facundo):
    # alpha = S²/x̄ es la escala (IV-123), beta = (x̄/S)² es la forma (IV-124).
    arr = np.array(serie_facundo)
    xbar = float(np.mean(arr))
    S = float(np.std(arr, ddof=1))
    alpha_esp = S**2 / xbar
    beta_esp = (xbar / S) ** 2

    res = gamma2p.ajustar(arr, "momentos")

    assert res.status == STATUS_OK
    assert res.parametros["alpha"] == pytest.approx(alpha_esp, abs=1e-6)
    assert res.parametros["beta"] == pytest.approx(beta_esp, abs=1e-6)


# ── ML — IV-131 corregido (π·τ₂² en vez de π²·τ₂) ───────────────────────────


@pytest.mark.unit
def test_gamma2p_ml_z_correcto_pi_tau2_cuadrado(serie_facundo):
    # IV-131: z = π·τ₂² (no π²·τ₂).
    # El valor incorrecto (π²·τ₂ ≈ 2.29) produce alpha≈0.13.
    # El valor correcto (π·τ₂² ≈ 0.169) produce alpha≈5.66.
    arr = np.array(serie_facundo)
    res = gamma2p.ajustar(arr, "ml")
    assert res.status == STATUS_OK
    # alpha > 1 verifica que se usó el z correcto (z incorrecto daba alpha≈0.13)
    assert res.parametros["alpha"] > 1.0


@pytest.mark.unit
def test_gamma2p_ml_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gamma2p.ajustar(arr, "ml")
    assert res.status == STATUS_OK
    assert res.parametros["alpha"] == pytest.approx(7.5504, abs=1e-3)
    assert res.parametros["beta"] == pytest.approx(5.6643, abs=1e-3)


@pytest.mark.unit
def test_gamma2p_ml_q100_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gamma2p.ajustar(arr, "ml")
    assert res.status == STATUS_OK
    q100 = gamma2p.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(95.3259, abs=1e-1)
