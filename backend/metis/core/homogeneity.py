import numpy as np
from scipy.stats import t as t_dist

from metis.core.types import TestResult, WarningItem

ALPHA = 0.05


# ── Helmert ───────────────────────────────────────────────────────────────────


def calcular_helmert(serie: list[float]) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)
    media = np.mean(arr)

    signos = arr > media
    cambios = int(np.sum(signos[1:] != signos[:-1]))
    secuencias = (n - 1) - cambios

    diferencia = secuencias - cambios
    limite = float(np.sqrt(n - 1))

    estadistico = float(diferencia)
    valor_critico = limite
    aprobada = abs(diferencia) <= limite
    veredicto = "aprobada" if aprobada else "rechazada"

    return TestResult(
        prueba="helmert",
        estadistico=float(estadistico),
        valor_critico=float(valor_critico),
        veredicto=veredicto,
        warning_codigo="TEST_WARNING_HOMOGENEITY" if not aprobada else None,
        warning_nivel="normal" if not aprobada else None,
    )


# ── t de Student ──────────────────────────────────────────────────────────────


def calcular_t_student(
    serie: list[float],
    n1: int,
    n2: int,
) -> TestResult:
    arr = np.array(serie, dtype=float)
    s1 = arr[:n1]
    s2 = arr[n1 : n1 + n2]

    media1, media2 = np.mean(s1), np.mean(s2)
    var1, var2 = np.var(s1, ddof=1), np.var(s2, ddof=1)

    nu = n1 + n2 - 2
    sp2 = ((n1 - 1) * var1 + (n2 - 1) * var2) / nu
    sp = np.sqrt(sp2)

    estadistico = (
        (media1 - media2) / (sp * np.sqrt(1 / n1 + 1 / n2)) if sp != 0 else 0.0
    )
    valor_critico = float(t_dist.ppf(1 - ALPHA / 2, df=nu))

    aprobada = abs(estadistico) <= valor_critico
    veredicto = "aprobada" if aprobada else "rechazada"

    return TestResult(
        prueba="t_student",
        estadistico=float(estadistico),
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo="TEST_WARNING_HOMOGENEITY" if not aprobada else None,
        warning_nivel="normal" if not aprobada else None,
        n1=n1,
        n2=n2,
    )


# ── Cramer ────────────────────────────────────────────────────────────────────


def _cramer_bloque(
    arr: np.ndarray,
    n_w: int,
    media_global: float,
    s_global: float,
) -> tuple[float, float] | None:
    """(tau_w, t_w) para los últimos n_w datos de arr (Ec. III-13/14/15), o None si denom ≤ 0."""
    n = len(arr)
    tau_w = (float(np.mean(arr[-n_w:])) - media_global) / s_global
    denom = n - n_w * (1 + tau_w**2)
    if denom <= 0:
        return None
    t_w = float(np.sqrt((n_w * (n - 2)) / denom) * abs(tau_w))
    return tau_w, t_w


def calcular_cramer(
    serie: list[float],
    particion: dict | str = "default",
) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)

    if particion == "default":
        n_w1 = int(np.ceil(n * 0.60))
        n_w2 = int(np.ceil(n * 0.30))
    else:
        n_w1 = int(np.ceil(n * particion["n1_pct"] / 100))
        n_w2 = int(np.ceil(n * particion["n2_pct"] / 100))

    n_w2 = min(n_w2, n - n_w1)

    media_global = float(np.mean(arr))
    s_global = float(np.std(arr, ddof=1))

    if s_global == 0:
        return TestResult(
            prueba="cramer",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_CONDITION",
            warning_nivel="normal",
            n1=n_w1,
            n2=n_w2,
        )

    bloque1 = _cramer_bloque(arr, n_w1, media_global, s_global)
    bloque2 = _cramer_bloque(arr, n_w2, media_global, s_global)

    if bloque1 is None or bloque2 is None:
        return TestResult(
            prueba="cramer",
            estadistico=None,
            valor_critico=None,
            veredicto="no_ejecutada",
            warning_codigo="TEST_NOT_EXECUTED_CONDITION",
            warning_nivel="normal",
            n1=n_w1,
            n2=n_w2,
        )

    tau_w1, t_w1 = bloque1
    tau_w2, t_w2 = bloque2

    nu_w1 = n + n_w1 - 2
    nu_w2 = n + n_w2 - 2

    vc_w1 = float(t_dist.ppf(1 - ALPHA / 2, df=nu_w1))
    vc_w2 = float(t_dist.ppf(1 - ALPHA / 2, df=nu_w2))

    aprobada = (t_w1 <= vc_w1) and (t_w2 <= vc_w2)
    veredicto = "aprobada" if aprobada else "rechazada"

    # Reportar el estadístico binding (el de mayor ratio t/vc)
    if (t_w1 / vc_w1) >= (t_w2 / vc_w2):
        estadistico_rep, vc_rep = t_w1, vc_w1
    else:
        estadistico_rep, vc_rep = t_w2, vc_w2

    return TestResult(
        prueba="cramer",
        estadistico=estadistico_rep,
        valor_critico=vc_rep,
        veredicto=veredicto,
        warning_codigo="TEST_CRITICAL_HOMOGENEITY" if not aprobada else None,
        warning_nivel="critico" if not aprobada else None,
        n1=n_w1,
        n2=n_w2,
    )


# ── Nivel de homogeneidad ─────────────────────────────────────────────────────


def determinar_nivel_homogeneidad(
    helmert: TestResult,
    t_student: TestResult,
    cramer: TestResult,
) -> tuple[str, list[WarningItem]]:
    warnings: list[WarningItem] = []

    if cramer.veredicto == "rechazada":
        nivel = "homogeneidad_critica"
        warnings.append(
            WarningItem(
                codigo="TEST_CRITICAL_HOMOGENEITY",
                nivel="critico",
                descripcion="Cramer rechazó homogeneidad",
            )
        )
    elif helmert.veredicto == "rechazada" or t_student.veredicto == "rechazada":
        nivel = "homogeneidad_warning"
        warnings.append(
            WarningItem(
                codigo="TEST_WARNING_HOMOGENEITY",
                nivel="normal",
                descripcion="Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron",
            )
        )
    else:
        nivel = "homogeneidad_ok"

    return nivel, warnings
