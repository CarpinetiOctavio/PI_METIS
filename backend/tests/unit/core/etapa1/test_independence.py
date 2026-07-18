import math

import numpy as np
import pytest

from metis.core.etapa1.independence import (
    calcular_anderson,
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
    assert warnings == []


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


@pytest.mark.unit
def test_wald_empates_con_media_se_excluyen_de_la_serie():
    # Valores exactamente iguales a la media no clasifican como éxito ni
    # fracaso — se excluyen de n, n1, n2 y del cálculo de rachas.
    # Criterio propio de METIS, no heredado de Facundo — DECISIÓN 017.
    #
    # serie: 12 valores por encima de 20, 12 por debajo, y 3 valores
    # exactamente en 20.0 (la media). media = 20.0 exacto.
    altos = [30.0] * 12
    bajos = [10.0] * 12
    empates = [20.0] * 3
    serie = altos + empates + bajos
    arr = np.array(serie, dtype=float)
    assert np.mean(arr) == 20.0
    assert int(np.sum(arr == 20.0)) == 3

    resultado = calcular_wald_wolfowitz(serie)

    # n efectivo tras excluir los 3 empates: 24 (no 27).
    # n1=12 (>media), n2=12 (<media) — reproducible a mano:
    # runs=2 (un bloque de 12 altos, un bloque de 12 bajos).
    n_efectivo = 24
    n1 = n2 = 12
    mu_u_esperado = (2 * n1 * n2) / (n1 + n2) + 1
    sigma2_u_esperado = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (
        (n1 + n2) ** 2 * (n1 + n2 - 1)
    )
    runs_esperado = 2
    z_esperado = (runs_esperado - mu_u_esperado) / np.sqrt(sigma2_u_esperado)

    assert resultado.veredicto != "no_ejecutada"
    assert resultado.estadistico == pytest.approx(z_esperado, abs=1e-9)
    # n_efectivo=24 ≤ 40 → warning de muestra chica (se calcula sobre n
    # efectivo, tras excluir empates — ver comentario en independence.py).
    assert n_efectivo <= 40
    assert resultado.warning_codigo == "TEST_WARNING_SMALL_SAMPLE"


@pytest.mark.unit
def test_wald_empates_con_media_reducen_n_bajo_umbral_small_sample():
    # Si la serie sin empates tiene n>40 pero excluir los empatados con la
    # media la deja en n≤40, el warning de muestra chica debe activarse
    # igual — se calcula sobre el n efectivo, no sobre len(serie) original.
    altos = [30.0] * 20
    bajos = [10.0] * 20
    empates = [20.0] * 2  # serie total: 42 datos, n efectivo: 40
    serie = altos + empates + bajos
    resultado = calcular_wald_wolfowitz(serie)
    assert resultado.warning_codigo == "TEST_WARNING_SMALL_SAMPLE"


# ── calcular_anderson ────────────────────────────────────────────────────────


@pytest.mark.unit
def test_anderson_un_lag_fuera_aprueba_tolerancia_10pct(serie_facundo):
    # Para serie_facundo (n=40): k_max=ceil(40/3)=14, lags_fuera=1 →
    # ceil(14*0.10)=2, 1≤2 → aprobada. DECISIÓN 016 (k_max=ceil, no floor).
    # Se verifican lags_fuera y estadístico de forma independiente al código.
    arr = np.array(serie_facundo, dtype=float)
    n = len(arr)
    media = np.mean(arr)
    k_max = math.ceil(n / 3)
    Z_CRIT = 1.96

    var = np.sum((arr - media) ** 2)
    r_values = [
        np.sum((arr[: n - k] - media) * (arr[k:] - media)) / var
        for k in range(1, k_max + 1)
    ]
    lags_fuera = sum(
        1
        for k, r_k in enumerate(r_values, start=1)
        if r_k > (-1 + Z_CRIT * np.sqrt(n - k - 1)) / (n - k)
        or r_k < (-1 - Z_CRIT * np.sqrt(n - k - 1)) / (n - k)
    )

    assert lags_fuera == 1

    resultado = calcular_anderson(serie_facundo)

    assert resultado.veredicto == "aprobada"
    assert resultado.estadistico == pytest.approx(
        max(abs(r) for r in r_values), abs=1e-4
    )


@pytest.mark.unit
def test_anderson_mayoria_lags_fuera_rechazada():
    # Serie creciente — autocorrelación ≈ 1 en todos los lags → k_max lags fuera → rechazada.
    serie = [float(i) for i in range(1, 51)]
    resultado = calcular_anderson(serie)
    assert resultado.veredicto == "rechazada"
    assert resultado.warning_codigo == "TEST_CRITICAL_INDEPENDENCE"
    assert resultado.warning_nivel == "critico"


@pytest.mark.unit
def test_anderson_k_max_ceil_no_floor_est03():
    # DECISIÓN 016 — k_max = ceil(n/3), no floor(n/3) = n//3.
    # est_03 (n=41): floor(41/3)=13, ceil(41/3)=14 — caso real del dataset
    # de regresión donde ambas convenciones difieren. Tesis: 1 punto fuera
    # de banda, "no supera el límite admisible de 1.4" → aprobada.
    serie_est03 = [
        114.0, 50.0, 54.0, 105.0, 45.0, 126.0, 14.0, 45.0, 14.0, 20.0, 34.0,
        47.0, 3.0, 32.0, 32.0, 179.0, 42.0, 402.0, 314.0, 36.0, 47.0, 21.0,
        44.0, 19.0, 32.0, 58.0, 83.0, 9.0, 13.0, 28.0, 2.0, 29.0, 71.0, 57.0,
        84.0, 34.0, 7.0, 34.0, 73.0, 70.0, 35.0,
    ]
    n = len(serie_est03)
    assert n // 3 == 13  # floor — lo que usaba el código antes del fix
    assert math.ceil(n / 3) == 14  # ceil — lo que usa el código ahora

    arr = np.array(serie_est03, dtype=float)
    media = np.mean(arr)
    var = np.sum((arr - media) ** 2)
    Z_CRIT = 1.9599639845400545
    k_max = 14  # ceil(41/3) — valor independiente esperado

    r_values = [
        np.sum((arr[: n - k] - media) * (arr[k:] - media)) / var
        for k in range(1, k_max + 1)
    ]
    lags_fuera_esperado = sum(
        1
        for k, rk in enumerate(r_values, start=1)
        if rk > (-1 + Z_CRIT * np.sqrt(n - k - 1)) / (n - k)
        or rk < (-1 - Z_CRIT * np.sqrt(n - k - 1)) / (n - k)
    )
    assert lags_fuera_esperado == 1

    resultado = calcular_anderson(serie_est03)
    assert resultado.veredicto == "aprobada"
    assert resultado.estadistico == pytest.approx(
        max(abs(r) for r in r_values), abs=1e-6
    )
