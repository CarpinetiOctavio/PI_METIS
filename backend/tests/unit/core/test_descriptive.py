import numpy as np
import pytest

from metis.core.descriptive import calcular_descriptiva


# ── Curtosis no sesgada — Ec. IV-7 directa ───────────────────────────────────


@pytest.mark.unit
def test_curtosis_no_sesgada_ec_iv7_directo(serie_facundo):
    # Ec. IV-6: k_sesg = mean((xi-x̄)⁴) / var_sesgada²
    # Ec. IV-7: k_insesg = n³/[(n-1)(n-2)(n-3)] · k_sesg
    # scipy.kurtosis(bias=False) usa corrección de bias distinta → implementar directo.
    arr = np.array(serie_facundo, dtype=float)
    n = len(arr)
    media = float(np.mean(arr))
    var_sesgada = float(np.var(arr, ddof=0))
    k_sesg = float(np.mean((arr - media) ** 4) / var_sesgada**2)
    k_insesg_esperado = float((n**3 / ((n - 1) * (n - 2) * (n - 3))) * k_sesg)

    resultado = calcular_descriptiva(serie_facundo)

    assert resultado.curtosis_no_sesgada == pytest.approx(k_insesg_esperado, abs=1e-6)


# ── MPP — ordenamiento de mayor a menor ──────────────────────────────────────


@pytest.mark.unit
def test_mpp_m1_ordenamiento_descendente():
    # serie = [3, 1, 2] → ordenada desc: [3, 2, 1]
    # M̂₁ = 1/[3·2] · [(3-1)·3 + (3-2)·2] = 1/6 · [6+2] = 8/6 = 4/3
    # Si se ordenara ascendente: [1, 2, 3] → M̂₁ = 1/6 · [2+2] = 4/6 = 2/3 (incorrecto)
    serie = [3.0, 1.0, 2.0]
    resultado = calcular_descriptiva(serie)
    assert resultado.mpp_m1 == pytest.approx(4.0 / 3.0, abs=1e-10)


@pytest.mark.unit
def test_mpp_m1_serie_facundo(serie_facundo):
    # M̂₁ calculado independientemente con numpy (orden descendente, Ec. IV-22)
    arr = np.array(serie_facundo, dtype=float)
    n = len(arr)
    xs = np.sort(arr)[::-1]
    idx = np.arange(1, n + 1)
    i1 = idx[: n - 1]
    m1_esperado = float(np.sum((n - i1) * xs[: n - 1]) / (n * (n - 1)))

    resultado = calcular_descriptiva(serie_facundo)
    assert resultado.mpp_m1 == pytest.approx(m1_esperado, abs=1e-6)


# ── suma_log — None cuando hay ceros o negativos ─────────────────────────────


@pytest.mark.unit
def test_suma_log_none_con_cero():
    serie = [1.0, 2.0, 0.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    resultado = calcular_descriptiva(serie)
    assert resultado.suma_log is None


@pytest.mark.unit
def test_suma_log_none_con_negativo():
    serie = [1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    resultado = calcular_descriptiva(serie)
    assert resultado.suma_log is None


@pytest.mark.unit
def test_suma_log_calculada_cuando_todo_positivo(serie_facundo):
    arr = np.array(serie_facundo, dtype=float)
    suma_esperada = float(np.sum(np.log(arr)))
    resultado = calcular_descriptiva(serie_facundo)
    assert resultado.suma_log == pytest.approx(suma_esperada, abs=1e-10)
