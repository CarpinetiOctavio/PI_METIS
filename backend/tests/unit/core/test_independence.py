import pytest

from metis.core.independence import (
    calcular_wald_wolfowitz,
    determinar_nivel_independencia,
)
from metis.core.types import TestResult


def _make_anderson(veredicto: str) -> TestResult:
    return TestResult(
        prueba="anderson",
        estadistico=0.1,
        valor_critico=0.3,
        veredicto=veredicto,
        warning_codigo="TEST_CRITICAL_INDEPENDENCE"
        if veredicto == "rechazada"
        else None,
        warning_nivel="critico" if veredicto == "rechazada" else None,
    )


def _make_wald(veredicto: str, warning_codigo: str | None = None) -> TestResult:
    return TestResult(
        prueba="wald_wolfowitz",
        estadistico=0.5,
        valor_critico=1.96,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel="normal" if warning_codigo else None,
    )


# ── determinar_nivel_independencia ───────────────────────────────────────────


@pytest.mark.unit
def test_anderson_aprueba_wald_aprueba_nivel_independiente():
    nivel, warnings = determinar_nivel_independencia(
        _make_anderson("aprobada"), _make_wald("aprobada")
    )
    assert nivel == "independiente"
    codigos = [w.codigo for w in warnings]
    assert "TEST_CRITICAL_INDEPENDENCE" not in codigos


@pytest.mark.unit
def test_anderson_aprueba_wald_rechaza_nivel_independiente():
    # Anderson manda — Wald rechazado no cambia el nivel.
    nivel, warnings = determinar_nivel_independencia(
        _make_anderson("aprobada"), _make_wald("rechazada")
    )
    assert nivel == "independiente"


@pytest.mark.unit
def test_anderson_aprueba_wald_rechaza_sin_warning_independence():
    # El resultado de Wald está en la lista independencia, no en warnings.
    # No debe emitirse ningún WarningItem por el rechazo de Wald.
    nivel, warnings = determinar_nivel_independencia(
        _make_anderson("aprobada"), _make_wald("rechazada")
    )
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_INDEPENDENCE" not in codigos
    assert "TEST_CRITICAL_INDEPENDENCE" not in codigos


@pytest.mark.unit
def test_anderson_rechaza_nivel_dependiente():
    nivel, warnings = determinar_nivel_independencia(
        _make_anderson("rechazada"), _make_wald("aprobada")
    )
    assert nivel == "dependiente"
    criticos = [w for w in warnings if w.codigo == "TEST_CRITICAL_INDEPENDENCE"]
    assert len(criticos) == 1
    assert criticos[0].nivel == "critico"


@pytest.mark.unit
def test_small_sample_warning_propagado(serie_facundo):
    # serie_facundo tiene n=40 — Wald emite TEST_WARNING_SMALL_SAMPLE.
    wald_con_small_sample = _make_wald("aprobada", "TEST_WARNING_SMALL_SAMPLE")
    _, warnings = determinar_nivel_independencia(
        _make_anderson("aprobada"), wald_con_small_sample
    )
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_SMALL_SAMPLE" in codigos


# ── calcular_wald_wolfowitz ───────────────────────────────────────────────────


@pytest.mark.unit
def test_wald_n_mayor_40_sin_small_sample():
    serie = [float(i % 30 + 10) for i in range(41)]
    resultado = calcular_wald_wolfowitz(serie)
    assert resultado.warning_codigo != "TEST_WARNING_SMALL_SAMPLE"


@pytest.mark.unit
def test_wald_n_igual_40_emite_small_sample(serie_facundo):
    # serie_facundo tiene exactamente n=40.
    resultado = calcular_wald_wolfowitz(serie_facundo)
    assert resultado.warning_codigo == "TEST_WARNING_SMALL_SAMPLE"
    assert resultado.warning_nivel == "normal"


@pytest.mark.unit
def test_wald_valores_iguales_no_ejecutada():
    # Con todos los valores iguales n1=0 — la prueba no puede ejecutarse.
    serie = [50.0] * 15
    resultado = calcular_wald_wolfowitz(serie)
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_CONDITION"
    assert resultado.estadistico is None
