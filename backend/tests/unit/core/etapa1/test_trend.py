import numpy as np
import pytest
from scipy.stats import ks_2samp

from metis.core.etapa1.trend import (
    calcular_ks_tendencia,
    calcular_mann_kendall,
    determinar_warnings_tendencia,
)
from metis.core.types import TestResult


def _make_trend_result(veredicto: str) -> TestResult:
    return TestResult(
        prueba="trend",
        estadistico=1.0,
        valor_critico=1.96,
        veredicto=veredicto,
        warning_codigo="TEST_WARNING_TREND" if veredicto == "rechazada" else None,
        warning_nivel="normal" if veredicto == "rechazada" else None,
    )


# ── calcular_mann_kendall ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_mann_kendall_n_menor_10_no_ejecutada():
    # n < 10 → no_ejecutada con TEST_NOT_EXECUTED_MIN_SAMPLES (Ec. formulas-etapa1 §7)
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    resultado = calcular_mann_kendall(serie)
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_MIN_SAMPLES"
    assert resultado.estadistico is None


@pytest.mark.unit
def test_mann_kendall_aprueba_sin_warning(serie_facundo):
    resultado = calcular_mann_kendall(serie_facundo)
    assert resultado.veredicto == "aprobada"
    assert resultado.warning_codigo is None


@pytest.mark.unit
def test_mann_kendall_rechaza_emite_warning():
    # Serie estrictamente creciente — tendencia monotónica garantizada.
    serie = [float(i) for i in range(1, 31)]
    resultado = calcular_mann_kendall(serie)
    assert resultado.veredicto == "rechazada"
    assert resultado.warning_codigo == "TEST_WARNING_TREND"


# ── calcular_ks_tendencia ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_ks_aprueba_sin_warning(serie_facundo):
    resultado = calcular_ks_tendencia(serie_facundo)
    assert resultado.veredicto == "aprobada"
    assert resultado.warning_codigo is None


@pytest.mark.unit
def test_ks_rechaza_emite_warning():
    # Primera mitad ~10, segunda mitad ~100 — CDFs empíricas claramente distintas.
    serie = [10.0] * 20 + [100.0] * 20
    resultado = calcular_ks_tendencia(serie)
    assert resultado.veredicto == "rechazada"
    assert resultado.warning_codigo == "TEST_WARNING_TREND"


@pytest.mark.unit
def test_ks_estadistico_es_z_tipificado_no_d(serie_facundo):
    # estadistico debe ser Z = D·√(n1·n2/(n1+n2)) (Ec. A.57), no D crudo
    # (Ec. A.56) — es lo que se compara contra valor_critico=1.358.
    arr = np.array(serie_facundo, dtype=float)
    n_total = len(arr)
    mitad = n_total // 2
    primera, segunda = arr[:mitad], arr[mitad:]
    n1, n2 = len(primera), len(segunda)

    d_stat, _ = ks_2samp(primera, segunda)
    z_esperado = d_stat * ((n1 * n2) / (n1 + n2)) ** 0.5

    resultado = calcular_ks_tendencia(serie_facundo)

    assert resultado.estadistico == pytest.approx(z_esperado, abs=1e-9)
    assert resultado.estadistico != pytest.approx(d_stat, abs=1e-6)


@pytest.mark.unit
def test_ks_criterio_z_difiere_de_criterio_p_valor():
    # Caso encontrado por búsqueda numérica (n1=25, n2=26) donde el
    # criterio viejo (p_valor>0.05 de scipy, D≈0.3738, p≈0.0403 → rechazada)
    # y el nuevo (Z=D·√(n1·n2/(n1+n2))≈1.3346 ≤ 1.358 → aprobada) discrepan.
    # Confirma que el fix aplica el criterio de la fuente (A.56/A.57),
    # no el de scipy.
    serie = [
        -0.7417, -1.0318, -1.8671, -1.2037, -1.0761, -1.427, 0.3085,
        -0.6639, -1.9883, 2.4835, -0.8349, -1.2555, 1.2398, 1.1654,
        -1.1513, -1.474, -1.0001, 1.1295, -0.3113, -0.8087, -0.0284,
        1.2042, -1.3896, -0.3838, -1.3835, 1.5694, 0.0528, 1.161,
        -2.6999, 0.6259, -1.629, -1.6131, -0.7461, -0.2504, 1.0423,
        1.2191, 0.6066, -1.0811, 1.1846, 0.0702, 1.8897, -1.0431,
        -3.6245, -0.4273, 3.2475, 0.8951, -0.0324, 1.4749, 0.9429,
        0.8844, -0.4788,
    ]
    arr = np.array(serie, dtype=float)
    mitad = len(arr) // 2
    primera, segunda = arr[:mitad], arr[mitad:]
    n1, n2 = len(primera), len(segunda)
    d_stat, p_valor = ks_2samp(primera, segunda)

    assert p_valor <= 0.05  # criterio viejo (scipy p-valor) rechazaría

    resultado = calcular_ks_tendencia(serie)

    z_esperado = d_stat * ((n1 * n2) / (n1 + n2)) ** 0.5
    assert z_esperado <= 1.358  # criterio nuevo aprueba
    assert resultado.estadistico == pytest.approx(z_esperado, abs=1e-9)
    assert resultado.veredicto == "aprobada"
    assert resultado.warning_codigo is None


# ── determinar_warnings_tendencia ─────────────────────────────────────────────


@pytest.mark.unit
def test_solo_mann_kendall_rechaza_genera_warning():
    warnings = determinar_warnings_tendencia(
        _make_trend_result("rechazada"), _make_trend_result("aprobada")
    )
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_TREND" in codigos


@pytest.mark.unit
def test_solo_ks_rechaza_genera_warning():
    warnings = determinar_warnings_tendencia(
        _make_trend_result("aprobada"), _make_trend_result("rechazada")
    )
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_TREND" in codigos


@pytest.mark.unit
def test_ninguno_rechaza_sin_warning():
    warnings = determinar_warnings_tendencia(
        _make_trend_result("aprobada"), _make_trend_result("aprobada")
    )
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_TREND" not in codigos
