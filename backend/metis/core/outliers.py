import numpy as np
from scipy.stats import t as t_dist

from metis.core.types import TestResult

ALPHA = 0.05


def calcular_chow(serie: list[float], tipo_variable: str) -> TestResult:
    arr = np.array(serie, dtype=float)

    # Ceros en caudal_precipitacion → no ejecutar
    if tipo_variable == "caudal_precipitacion" and np.any(arr == 0):
        return TestResult(
            prueba="chow",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_ZEROS",
            warning_nivel="normal",
        )

    # Valores ≤ 0 por cualquier causa → log no definido
    if np.any(arr <= 0):
        return TestResult(
            prueba="chow",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_CONDITION",
            warning_nivel="normal",
        )

    # Chow aplica sobre logaritmos
    log_serie = np.log(arr)
    n = len(log_serie)
    media = np.mean(log_serie)
    s = np.std(log_serie, ddof=1)

    z_scores = np.abs((log_serie - media) / s) if s != 0 else np.zeros(n)
    estadistico = float(np.max(z_scores))

    # Valor crítico con corrección de Bonferroni — ν = n-1 (Ec. 7/8a, Chow)
    nu = n - 1
    valor_critico = float(t_dist.ppf(1 - ALPHA / (2 * n), df=nu))

    atipico_detectado = estadistico > valor_critico
    veredicto = "rechazada" if atipico_detectado else "aprobada"

    # Chow nunca genera warning crítico — siempre normal
    warning_codigo = "TEST_WARNING_OUTLIER_DETECTED" if atipico_detectado else None
    warning_nivel = "normal" if atipico_detectado else None

    # Valor original de la serie (no el log) correspondiente al z-score máximo
    valor_atipico: float | None = None
    if atipico_detectado:
        idx = int(np.argmax(z_scores))
        valor_atipico = float(arr[idx])

    return TestResult(
        prueba="chow",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
        valor_atipico=valor_atipico,
    )
