import pytest

from metis.core.trend import (
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
def test_mann_kendall_n7_no_ejecutada():
    # n=7 — valor crítico de Tabla A.4 pendiente de confirmar con Facundo.
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    resultado = calcular_mann_kendall(serie)
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_CONDITION"
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
