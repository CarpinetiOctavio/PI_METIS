import numpy as np
import pymannkendall as mk
from scipy.stats import ks_2samp, norm

from metis.core.types import TestResult, WarningItem

ALPHA = 0.05
Z_CRIT = norm.ppf(1 - ALPHA / 2)  # 1.96
KS_Z_CRIT = 1.358  # Tabla A.5, α=0.05

# Tabla A.4 — Mann-Kendall para n ≤ 10, valores críticos de S (α=0.05, two-tailed)
# Fuente: Tabla A.4 tesis Facundo
# n=7: pendiente confirmar con Facundo — ver core-implementation.md
MANN_KENDALL_TABLA_A4 = {
    4: 4,
    5: 6,
    6: 7,
    7: None,  # pendiente confirmar con Facundo
    8: 11,
    9: 12,
    10: 13,
}


# ── Mann-Kendall ──────────────────────────────────────────────────────────────


def calcular_mann_kendall(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)

    if n > 10:
        resultado = mk.original_test(arr, alpha=ALPHA)
        estadistico = float(resultado.z)
        valor_critico = float(Z_CRIT)
        aprobada = not bool(resultado.h)
    else:
        s_crit = MANN_KENDALL_TABLA_A4.get(n)
        if s_crit is None:
            return TestResult(
                prueba="mann_kendall",
                estadistico=None,
                valor_critico=None,
                veredicto="no_ejecutada",
                warning_codigo="TEST_NOT_EXECUTED_CONDITION",
                warning_nivel="normal",
            )
        s = _calcular_s(arr)
        estadistico = float(abs(s))
        valor_critico = float(s_crit)
        aprobada = abs(s) <= s_crit

    veredicto = "aprobada" if aprobada else "rechazada"
    warning_codigo = "TEST_WARNING_TREND" if not aprobada else None
    warning_nivel = "normal" if not aprobada else None

    return TestResult(
        prueba="mann_kendall",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
    )


def _calcular_s(arr: np.ndarray) -> int:
    n = len(arr)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = arr[j] - arr[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1
    return s


# ── Kolmogorov-Smirnov (tendencia) ───────────────────────────────────────────


def calcular_ks_tendencia(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n_total = len(arr)

    mitad = n_total // 2
    primera = arr[:mitad]
    segunda = arr[mitad:]
    n = len(primera)
    m = len(segunda)

    # D: máxima diferencia entre CDFs empíricas de cada mitad
    d_stat, _ = ks_2samp(primera, segunda)

    # Z = D * sqrt(n*m / (n+m)) — fórmula Tabla A.5
    z_stat = float(d_stat * np.sqrt((n * m) / (n + m)))
    valor_critico = KS_Z_CRIT  # 1.358

    aprobada = z_stat <= valor_critico
    veredicto = "aprobada" if aprobada else "rechazada"
    warning_codigo = "TEST_WARNING_TREND" if not aprobada else None
    warning_nivel = "normal" if not aprobada else None

    return TestResult(
        prueba="kolmogorov_smirnov",
        estadistico=z_stat,
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
