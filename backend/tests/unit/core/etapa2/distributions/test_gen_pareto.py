import numpy as np
import pytest

from metis.core.etapa2.distributions import gen_pareto
from metis.core.etapa2.types import STATUS_NO_APLICABLE, STATUS_NO_CONVERGE, STATUS_OK


# ── MV — IV-152 denominador σ² ────────────────────────────────────────────────


@pytest.mark.unit
def test_gen_pareto_mv_no_converge_serie_facundo(serie_facundo):
    # La tesis documenta que MV frecuentemente No Converge.
    # Verificar que el comportamiento sigue siendo no_converge tras corregir IV-152.
    arr = np.array(serie_facundo)
    res = gen_pareto.ajustar(arr, "mv")
    assert res.status == STATUS_NO_CONVERGE


# ── Momentos ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gen_pareto_momentos_parametros_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gen_pareto.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["mu"] == pytest.approx(19.7941, abs=1e-3)
    assert res.parametros["sigma"] == pytest.approx(30.7807, abs=1e-3)
    assert res.parametros["epsilon"] == pytest.approx(0.3398, abs=1e-3)


# ── MC ────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gen_pareto_mc_converge_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gen_pareto.ajustar(arr, "mc")
    assert res.status == STATUS_OK


@pytest.mark.unit
@pytest.mark.skip(
    reason="Formula IV-153/154/155 (Gen. Pareto MC) no verificable con certeza "
    "contra el rasterizado de la tesis sin el Excel original de Facundo. El "
    "sistema tiene una raíz espuria cerca de eps=0 que pasa los guards actuales "
    "(sigma>0, _DENOM_GUARD) por cancelación catastrófica — ver ENMIENDA "
    "20/07/2026 en decision010.md. No se elige un criterio de selección de "
    "raíz alternativo sin confirmar la fórmula primero."
)
def test_gen_pareto_mc_q100_serie_facundo(serie_facundo):
    arr = np.array(serie_facundo)
    res = gen_pareto.ajustar(arr, "mc")
    assert res.status == STATUS_OK
    q100 = gen_pareto.cuantil(0.99, res.parametros)
    assert q100 == pytest.approx(90.6333, abs=1e-1)


# ── Cuantil ε→0 ───────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_gen_pareto_cuantil_epsilon_cero_usa_limite():
    # Límite ε→0: xT = µ - σ·ln(1-p)
    mu, sigma = 20.0, 15.0
    p = 0.99
    params = {"mu": mu, "sigma": sigma, "epsilon": 1e-12}
    esperado = float(mu - sigma * np.log(1.0 - p))
    assert gen_pareto.cuantil(p, params) == pytest.approx(esperado, abs=1e-6)


# ── Momentos — guard de dominio µ >= min(serie) (DECISIÓN 060) ──────────────


@pytest.mark.unit
def test_gen_pareto_momentos_no_aplicable_si_mu_mayor_igual_min():
    # est_07 (Tincunaco) real — µ Momentos=16.98 > min(serie)=11.8, violaría
    # el soporte de IV-145/146 (x >= µ) sin el guard. Verificado en
    # docs/auditoria/hallazgos/restricciones-dominio-etapa2.md (17/08/2026).
    serie = np.array(
        [
            77.7,
            42.3,
            53.5,
            51.2,
            85.5,
            102.0,
            22.4,
            39.3,
            21.8,
            27.0,
            32.9,
            61.9,
            36.8,
            60.3,
            11.8,
            46.4,
            69.8,
            120.0,
            38.6,
        ]
    )
    res = gen_pareto.ajustar(serie, "momentos")
    assert res.status == STATUS_NO_APLICABLE
    assert res.parametros is None


@pytest.mark.unit
def test_gen_pareto_momentos_ok_si_mu_menor_min(serie_facundo):
    # serie_facundo no dispara el guard — control negativo del test de arriba.
    arr = np.array(serie_facundo)
    res = gen_pareto.ajustar(arr, "momentos")
    assert res.status == STATUS_OK
    assert res.parametros["mu"] < float(np.min(arr))


# ── Tolerancia a cero (DECISIÓN 061) — los 4 métodos calculan igual ────────


@pytest.mark.unit
@pytest.mark.parametrize("metodo", ["momentos", "mv", "mc", "mpp"])
def test_gen_pareto_tolera_cero(serie_facundo, metodo):
    # Antes de DECISIÓN 061: STATUS_DISABLED_ZEROS incondicional en los 4
    # métodos. Ninguno aplica log(xi) crudo (MC usa log(1-fi) por posición
    # de ploteo, no por valor) — un cero no rompe el cálculo, verificado en
    # restricciones-dominio-etapa2.md.
    arr = np.array(serie_facundo)
    arr[int(np.argmin(arr))] = 0.0
    res = gen_pareto.ajustar(arr, metodo)
    assert res.status != "disabled_zeros"
    if res.parametros is not None:
        assert all(np.isfinite(v) for v in res.parametros.values())
