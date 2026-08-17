import numpy as np
import pytest

from metis.core.etapa2.distributions import gen_exponencial
from metis.core.etapa2.types import STATUS_DISABLED_ZEROS, STATUS_OK

# NOTA: este módulo no tenía tests unitarios antes de DECISIÓN 061 — el
# alcance de este archivo es cubrir el cambio de comportamiento ante ceros
# (bloqueo acotado a MV, Momentos/ML toleran), no backfillear cobertura
# completa de IV-77 a IV-89 (eso queda fuera de esta decisión puntual).


# ── Tolerancia a cero (DECISIÓN 061) — distinta por método ─────────────────


@pytest.mark.unit
def test_gen_exponencial_momentos_tolera_cero(serie_facundo):
    # Antes de DECISIÓN 061: STATUS_DISABLED_ZEROS incondicional para los 3
    # métodos. IV-77/78 no aplican log(xi) crudo (digamma/trigamma de α, CV
    # de la serie) — un cero no rompe el cálculo. Verificado en
    # docs/auditoria/hallazgos/restricciones-dominio-etapa2.md.
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = gen_exponencial.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert np.isfinite(res.parametros["alpha"])
    assert np.isfinite(res.parametros["lambda"])


@pytest.mark.unit
def test_gen_exponencial_ml_tolera_cero(serie_facundo):
    # Mismo caso que Momentos — IV-83/84 no aplican log(xi) crudo.
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = gen_exponencial.ajustar(arr, "ml")
    assert res.status == STATUS_OK
    assert np.isfinite(res.parametros["alpha"])
    assert np.isfinite(res.parametros["lambda"])


@pytest.mark.unit
def test_gen_exponencial_mv_sigue_bloqueando_cero(serie_facundo):
    # MV NO cambia con DECISIÓN 061 — log(1-e^(-λ·xi)) = log(1-e^0) = log(0),
    # indefinido en x=0. Es necesidad matemática, no pregunta de dominio.
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = gen_exponencial.ajustar(arr, "mv")
    assert res.status == STATUS_DISABLED_ZEROS
    assert res.parametros is None


@pytest.mark.unit
def test_gen_exponencial_mv_ok_sin_cero(serie_facundo):
    # Control negativo — MV funciona normalmente sin ceros en la serie.
    arr = np.array(serie_facundo)
    res = gen_exponencial.ajustar(arr, "mv")
    assert res.status == STATUS_OK
    assert np.isfinite(res.parametros["alpha"])
    assert np.isfinite(res.parametros["lambda"])
