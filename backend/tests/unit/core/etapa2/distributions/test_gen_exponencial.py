import numpy as np
import pytest

from metis.core.etapa2.distributions import gen_exponencial, gve
from metis.core.etapa2.distributions.gen_exponencial import _momentos_l
from metis.core.etapa2.types import (
    STATUS_DISABLED_ZEROS,
    STATUS_NO_APLICABLE,
    STATUS_OK,
)

# NOTA: este módulo estrenó tests unitarios con DECISIÓN 061 (comportamiento
# ante ceros). DECISIÓN 069 (09/09/2026) suma la cobertura de Momentos-L:
# el helper _momentos_l (IV-87/88) y el guard λ̂<0 → NO_APLICABLE. No se
# backfillea cobertura completa de IV-77 a IV-89 fuera de esos dos ejes.


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
def test_gen_exponencial_ml_no_aplicable_con_cero(serie_facundo):
    # Reemplaza a test_gen_exponencial_ml_tolera_cero — su premisa ("ML
    # tolera ceros") dejó de existir con DECISIÓN 069: ML es NO_APLICABLE
    # con o sin ceros. El guard λ̂<0 se evalúa antes que cualquier
    # consideración de ceros.
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = gen_exponencial.ajustar(arr, "ml")
    assert res.status == STATUS_NO_APLICABLE
    assert res.parametros is None


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


# ── Momentos-L (IV-83/84) — DECISIÓN 069 ───────────────────────────────────


@pytest.mark.unit
def test_momentos_l_valores_a_mano():
    # El helper ordena descendente: [10, 7, 4, 2], n=4
    #   M̂0 = 23/4 = 5.75
    #   M̂1 = (10·3 + 7·2 + 4·1) / (4·3) = 48/12 = 4.0            (IV-87)
    #   M̂2 = (10·3·2 + 7·2·1) / (4·3·2) = 74/24                  (IV-88)
    m0, m1, m2 = _momentos_l(np.array([2.0, 10.0, 4.0, 7.0]))
    assert m0 == pytest.approx(5.75)
    assert m1 == pytest.approx(4.0)
    assert m2 == pytest.approx(74.0 / 24.0)


@pytest.mark.unit
def test_momentos_l_n_menor_a_3():
    # IV-88 no está definida para n<3 — M̂2 = 0.0 (defensivo; ajustar() ya
    # cortó antes con NO_APLICABLE por el guard n<3).
    m0, m1, m2 = _momentos_l(np.array([8.0, 5.0]))
    assert (m0, m1, m2) == pytest.approx((6.5, 4.0, 0.0))


@pytest.mark.unit
def test_momentos_l_identico_a_gve(serie_facundo):
    # _momentos_l y gve._momentos_L son idénticos término a término
    # (IV-87/88 == IV-243/244). Protege esa equivalencia hasta la
    # consolidación K-4.1 / DECISIÓN 022.
    arr = np.array(serie_facundo)
    assert _momentos_l(arr) == pytest.approx(gve._momentos_L(arr))


@pytest.mark.unit
def test_gen_exponencial_ml_no_aplicable_serie_valida(serie_facundo):
    # DECISIÓN 069 — α̂ = M̂2/M̂1 < 1 para toda muestra no degenerada ⇒
    # λ̂ (IV-84) < 0 ⇒ F(x) = (1-e^{-λx})^α no real para x>0 ⇒ NO_APLICABLE.
    res = gen_exponencial.ajustar(np.array(serie_facundo), "ml")
    assert res.status == STATUS_NO_APLICABLE
    assert res.parametros is None


@pytest.mark.unit
def test_gen_exponencial_ml_no_aplicable_n_menor_a_3():
    res = gen_exponencial.ajustar(np.array([5.0, 8.0]), "ml")
    assert res.status == STATUS_NO_APLICABLE
    assert res.parametros is None
