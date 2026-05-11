import numpy as np
from scipy.stats import norm

from metis.core.types import TestResult, WarningItem

ALPHA = 0.05
Z_CRIT = norm.ppf(1 - ALPHA / 2)  # 1.96


# ── Anderson ──────────────────────────────────────────────────────────────────


def calcular_anderson(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)
    media = np.mean(arr)
    denominador = np.sum((arr - media) ** 2)

    k_max = n // 3
    r_values = []
    r_crit_upper_values = []

    for k in range(1, k_max + 1):
        numerador = np.sum((arr[: n - k] - media) * (arr[k:] - media))
        r_k = numerador / denominador if denominador != 0 else 0.0
        r_crit_upper = (-1 + Z_CRIT * np.sqrt(n - k - 1)) / (n - k)
        r_values.append(r_k)
        r_crit_upper_values.append(r_crit_upper)

    idx_max = int(np.argmax(np.abs(r_values)))
    estadistico = float(r_values[idx_max])
    valor_critico = float(min(r_crit_upper_values))

    aprobada = all(
        (-1 - Z_CRIT * np.sqrt(n - k - 1)) / (n - k)
        <= r_values[k - 1]
        <= r_crit_upper_values[k - 1]
        for k in range(1, k_max + 1)
    )

    veredicto = "aprobada" if aprobada else "rechazada"
    warning_codigo = None
    warning_nivel = None

    if not aprobada:
        warning_codigo = "TEST_CRITICAL_INDEPENDENCE"
        warning_nivel = "critico"

    return TestResult(
        prueba="anderson",
        estadistico=estadistico,
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
    )


# ── Wald-Wolfowitz ────────────────────────────────────────────────────────────


def calcular_wald_wolfowitz(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)
    media = np.mean(arr)

    signos = arr > media
    runs = 1 + int(np.sum(signos[1:] != signos[:-1]))
    n1 = int(np.sum(signos))
    n2 = n - n1

    if n1 == 0 or n2 == 0:
        return TestResult(
            prueba="wald_wolfowitz",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_CONDITION",
            warning_nivel="normal",
        )

    mu_u = (2 * n1 * n2) / (n1 + n2) + 1
    sigma2_u = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (
        (n1 + n2) ** 2 * (n1 + n2 - 1)
    )
    sigma_u = np.sqrt(sigma2_u)
    z_stat = (runs - mu_u) / sigma_u if sigma_u != 0 else 0.0

    valor_critico = Z_CRIT
    aprobada = abs(z_stat) <= valor_critico
    veredicto = "aprobada" if aprobada else "rechazada"

    warning_codigo = None
    warning_nivel = None
    if n <= 40:
        warning_codigo = "TEST_WARNING_SMALL_SAMPLE"
        warning_nivel = "normal"

    return TestResult(
        prueba="wald_wolfowitz",
        estadistico=float(z_stat),
        valor_critico=float(valor_critico),
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel=warning_nivel,
    )


# ── Nivel de independencia ────────────────────────────────────────────────────


def determinar_nivel_independencia(
    anderson: TestResult,
    wald: TestResult,
) -> tuple[str, list[WarningItem]]:
    warnings: list[WarningItem] = []

    if anderson.veredicto == "aprobada":
        nivel = "independiente"
    else:
        nivel = "dependiente"
        warnings.append(
            WarningItem(
                codigo="TEST_CRITICAL_INDEPENDENCE",
                nivel="critico",
                descripcion="Anderson rechazó independencia",
            )
        )

    if wald.warning_codigo == "TEST_WARNING_SMALL_SAMPLE":
        warnings.append(
            WarningItem(
                codigo="TEST_WARNING_SMALL_SAMPLE",
                nivel="normal",
                descripcion="Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa",
            )
        )

    return nivel, warnings
