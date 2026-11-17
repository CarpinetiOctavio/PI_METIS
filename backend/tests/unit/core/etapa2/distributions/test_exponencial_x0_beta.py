import numpy as np
import pytest

from metis.core.etapa2.distributions import exponencial_x0_beta
from metis.core.etapa2.types import STATUS_NO_APLICABLE, STATUS_OK


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


# ── Momentos — guard de dominio x0 >= min(serie) (DECISIÓN 060) ─────────────


@pytest.mark.unit
def test_exp_x0_beta_momentos_no_aplicable_si_x0_mayor_igual_min():
    # Serie sintética donde x0 = xbar - S = 10.4189 >= min(serie) = 10.0 —
    # violaría el soporte de IV-68/69 (x > x0) sin el guard. Reproduce el
    # caso real de est_04 (Las Tapias, x0=4.33 > min=2.0) verificado en
    # docs/auditoria/hallazgos/restricciones-dominio-etapa2.md.
    serie = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
    res = exponencial_x0_beta.ajustar(serie, "momentos")
    assert res.status == STATUS_NO_APLICABLE
    assert res.parametros is None


@pytest.mark.unit
def test_exp_x0_beta_momentos_ok_si_x0_menor_min():
    # est_02 (Vado de Río Seco) real — x0 Momentos=33.87 < min(serie)=42.0,
    # no viola el soporte. Control negativo del test de arriba — serie_facundo
    # NO sirve para esto: x0=25.04 > min=21.1, dispara el guard igual.
    serie = np.array(
        [
            98.0,
            44.0,
            97.0,
            52.0,
            90.0,
            247.0,
            191.0,
            54.0,
            112.0,
            42.0,
            60.0,
            157.0,
            61.0,
            45.0,
            91.0,
            257.0,
            458.0,
            381.0,
            251.0,
            151.0,
            122.0,
            58.0,
            145.0,
            158.0,
        ]
    )
    res = exponencial_x0_beta.ajustar(serie, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["x0"] < float(np.min(serie))


# ── Tolerancia a cero (DECISIÓN 061) — Momentos y MV calculan igual ────────


@pytest.mark.unit
def test_exp_x0_beta_momentos_tolera_cero(serie_facundo):
    # Antes de DECISIÓN 061: STATUS_DISABLED_ZEROS incondicional. Ninguna
    # fórmula de Momentos aplica log(xi) crudo — un cero no rompe el cálculo,
    # verificado en restricciones-dominio-etapa2.md.
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = exponencial_x0_beta.ajustar(arr, "momentos")
    assert res.status in (STATUS_OK, STATUS_NO_APLICABLE)  # nunca disabled_zeros
    assert np.isfinite(res.parametros["x0"]) if res.parametros else True


@pytest.mark.unit
def test_exp_x0_beta_mv_tolera_cero(serie_facundo):
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = exponencial_x0_beta.ajustar(arr, "mv")
    assert res.status == STATUS_OK
    assert np.isfinite(res.parametros["x0"])
    assert np.isfinite(res.parametros["beta"])
