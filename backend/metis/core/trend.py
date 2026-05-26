import numpy as np
import pymannkendall as mk
from scipy.stats import ks_2samp, norm

from metis.core.types import TestResult, WarningItem

ALPHA = 0.05
Z_CRIT = norm.ppf(1 - ALPHA / 2)  # 1.96
KS_Z_CRIT = 1.358  # Tabla A.5, α=0.05


# ── Mann-Kendall ──────────────────────────────────────────────────────────────


def calcular_mann_kendall(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)

    if n < 10:
        return TestResult(
            prueba="mann_kendall",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_MIN_SAMPLES",
            warning_nivel="normal",
        )

    resultado = mk.original_test(arr, alpha=ALPHA)
    estadistico = float(resultado.z)
    valor_critico = float(Z_CRIT)
    aprobada = not bool(resultado.h)
    veredicto = "aprobada" if aprobada else "rechazada"

    if not aprobada:
        warning_codigo = "TEST_WARNING_TREND"
        warning_nivel = "normal"
    elif 10 <= n <= 30:
        warning_codigo = "TEST_WARNING_SMALL_SAMPLE"
        warning_nivel = "normal"
    else:
        warning_codigo = None
        warning_nivel = None

    return TestResult(
        prueba="mann_kendall",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
    )


# ── Kolmogorov-Smirnov (tendencia) ───────────────────────────────────────────


def calcular_ks_tendencia(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n_total = len(arr)

    mitad = n_total // 2
    primera = arr[:mitad]
    segunda = arr[mitad:]

    # D: máxima diferencia entre CDFs empíricas (Ec. A.56–A.57)
    d_stat, p_valor = ks_2samp(primera, segunda)

    estadistico = float(d_stat)
    valor_critico = KS_Z_CRIT  # 1.358 — Tabla A.5, α=0.05 (referencia bibliográfica)
    aprobada = p_valor > 0.05  # equivalente a Z = D·√(nm/(n+m)) ≤ 1.358

    veredicto = "aprobada" if aprobada else "rechazada"
    warning_codigo = "TEST_WARNING_TREND" if not aprobada else None
    warning_nivel = "normal" if not aprobada else None

    return TestResult(
        prueba="kolmogorov_smirnov",
        estadistico=estadistico,
        valor_critico=float(valor_critico),
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
    )


# ── Warnings de tendencia ─────────────────────────────────────────────────────


def determinar_warnings_tendencia(
    mann_kendall: TestResult,
    ks: TestResult,
) -> list[WarningItem]:
    warnings: list[WarningItem] = []
    if mann_kendall.veredicto == "rechazada" or ks.veredicto == "rechazada":
        warnings.append(
            WarningItem(
                codigo="TEST_WARNING_TREND",
                nivel="normal",
                descripcion="Tendencia detectada en la serie (Mann-Kendall o KS)",
            )
        )
    return warnings
