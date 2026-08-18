import numpy as np
from scipy.stats import t as t_dist

from metis.core.types import Explicacion, TestResult

# Grubbs-Beck (Chow, Bulletin 17B Apéndice 4) usa 10% de significancia —
# distinto del 5% global de Etapa 1 (Anderson, Wald, Helmert, etc.).
# Decisión provisoria mientras se confirma con Facundo/Carlos — ver
# DECISIÓN 018, docs/decisiones/decision018.md.
ALPHA_CHOW = 0.10


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

    # Valor crítico K_N — Grubbs-Beck, Bulletin 17B Apéndice 4 (DECISIÓN 018).
    # El estadístico (desvío estandarizado máximo) es el de Grubbs; K_N
    # requiere la transformación geométrica completa, no el cuantil t crudo:
    #   K_N = (n-1)/√n · √(t² / (n-2+t²)),  t = t_{n-2, 1-α/(2n)}
    # (Bonferroni de dos colas corregido por n comparaciones simultáneas)
    nu = n - 2
    t_val = t_dist.ppf(1 - ALPHA_CHOW / (2 * n), df=nu)
    valor_critico = float(
        ((n - 1) / np.sqrt(n)) * np.sqrt(t_val**2 / (n - 2 + t_val**2))
    )

    atipico_detectado = estadistico > valor_critico
    veredicto = "rechazada" if atipico_detectado else "aprobada"

    # Chow nunca genera warning crítico — siempre normal
    warning_codigo = "TEST_WARNING_OUTLIER_DETECTED" if atipico_detectado else None
    warning_nivel = "normal" if atipico_detectado else None

    # Valor e índice originales de la serie (no el log) correspondientes al
    # z-score máximo — el índice es necesario para remover el dato correcto
    # en caso de que la serie tenga valores duplicados (ver analysis_service.py)
    valor_atipico: float | None = None
    indice_atipico: int | None = None
    if atipico_detectado:
        idx = int(np.argmax(z_scores))
        valor_atipico = float(arr[idx])
        indice_atipico = idx

    explicacion = Explicacion(
        ecuacion="Bulletin 17B, Apéndice 4 (Grubbs-Beck) — DECISIÓN 018",
        terminos={
            "n": n,
            "media_log": float(media),
            "s_log": float(s),
            "nu": nu,
            "t_bonferroni": float(t_val),
        },
    )

    return TestResult(
        prueba="chow",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
        valor_atipico=valor_atipico,
        indice_atipico=indice_atipico,
        explicacion=explicacion,
    )
