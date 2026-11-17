import numpy as np
import pymannkendall as mk
from scipy.stats import ks_2samp

from metis.core.etapa1.significancia import (
    ALFA_DEFECTO,
    KS_Z_CRIT,
    validar_alfa,
    z_bilateral,
)
from metis.core.types import Explicacion, TestResult, WarningItem


# ── Mann-Kendall ──────────────────────────────────────────────────────────────


def calcular_mann_kendall(serie: list[float], alfa: float = ALFA_DEFECTO) -> TestResult:
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

    # Ec. A.55: |Z| ≤ z_{1−α/2}. pymannkendall decide `h` con el mismo α
    # (DECISIÓN 078).
    valor_critico = z_bilateral(alfa)
    resultado = mk.original_test(arr, alpha=alfa)
    estadistico = float(resultado.z)
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

    explicacion = Explicacion(
        ecuacion="A.55",
        terminos={
            "n": n,
            "s": float(resultado.s),
            "var_s": float(resultado.var_s),
            "alfa": alfa,
            "z_critico": valor_critico,
        },
    )

    return TestResult(
        prueba="mann_kendall",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
        explicacion=explicacion,
    )


# ── Kolmogorov-Smirnov (tendencia) ───────────────────────────────────────────


def calcular_ks_tendencia(serie: list[float], alfa: float = ALFA_DEFECTO) -> TestResult:
    # Valor crítico de Ec. A.57 para α (Tabla A.5 a 5 %; DECISIÓN 078).
    ks_z_crit = KS_Z_CRIT[validar_alfa(alfa)]
    arr = np.array(serie, dtype=float)
    n_total = len(arr)

    mitad = n_total // 2
    primera = arr[:mitad]
    segunda = arr[mitad:]

    # D: máxima diferencia entre CDFs empíricas (Ec. A.56)
    d_stat, _ = ks_2samp(primera, segunda)
    n1, n2 = len(primera), len(segunda)

    # Z tipificado (Ec. A.57) — comparado contra el valor crítico fijo de
    # Tabla A.5. El criterio p_valor>0.05 de scipy NO es equivalente: usa
    # la distribución exacta/asintótica de KS de dos muestras, mientras
    # A.57 es una aproximación asintótica más simple con valor crítico de
    # tabla. Se sigue el procedimiento literal de la fuente (Caamaño Nelli
    # & Colladon, Apéndice A.5.2) en ausencia de caso de referencia real
    # que justifique apartarse de él.
    z_stat = d_stat * ((n1 * n2) / (n1 + n2)) ** 0.5

    estadistico = float(z_stat)
    valor_critico = ks_z_crit
    aprobada = z_stat <= ks_z_crit

    veredicto = "aprobada" if aprobada else "rechazada"
    warning_codigo = "TEST_WARNING_TREND" if not aprobada else None
    warning_nivel = "normal" if not aprobada else None

    explicacion = Explicacion(
        ecuacion="A.57",
        terminos={
            "n1": n1,
            "n2": n2,
            "d": float(d_stat),
            "alfa": alfa,
            "z_critico": ks_z_crit,
        },
    )

    return TestResult(
        prueba="kolmogorov_smirnov",
        estadistico=estadistico,
        valor_critico=float(valor_critico),
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
        explicacion=explicacion,
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
    # Mismo criterio que Wald-Wolfowitz en determinar_nivel_independencia: el warning de muestra
    # chica del TestResult llega a la lista agregada (defecto D-10, issue #123; DECISIÓN 038).
    if mann_kendall.warning_codigo == "TEST_WARNING_SMALL_SAMPLE":
        warnings.append(
            WarningItem(
                codigo="TEST_WARNING_SMALL_SAMPLE",
                nivel="normal",
                descripcion="Mann-Kendall ejecutado con 10 ≤ n ≤ 30 — resultado no garantizable "
                "por el tamaño de la muestra",
            )
        )
    return warnings
