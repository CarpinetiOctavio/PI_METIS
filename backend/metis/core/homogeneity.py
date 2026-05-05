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

    mu = (n - 1) / 2
    sigma = np.sqrt((n - 1) / 4)

    estadistico = (cambios - mu) / sigma if sigma != 0 else 0.0
    valor_critico = 1.96  # normal estándar, α=5% — ver core-implementation.md

    aprobada = abs(estadistico) <= valor_critico
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


def calcular_cramer(
    serie: list[float],
    particion: dict | str = "default",
) -> TestResult:
    arr = np.array(serie, dtype=float)
    n = len(arr)

    if particion == "default":
        n1 = int(np.ceil(n * 0.60))
        n2 = int(np.ceil(n * 0.30))
    else:
        n1 = int(np.ceil(n * particion["n1_pct"] / 100))
        n2 = int(np.ceil(n * particion["n2_pct"] / 100))

    n2 = min(n2, n - n1)

    s1 = arr[:n1]
    s2 = arr[n1 : n1 + n2]

    media1, media2 = np.mean(s1), np.mean(s2)
    var1, var2 = np.var(s1, ddof=1), np.var(s2, ddof=1)

    nu = n1 + n2 - 2
    sp2 = ((n1 - 1) * var1 + (n2 - 1) * var2) / nu
    sp = np.sqrt(sp2)

    tau = (media1 - media2) / (sp * np.sqrt(1 / n1 + 1 / n2)) if sp != 0 else 0.0
    valor_critico = float(t_dist.ppf(1 - ALPHA / 2, df=nu))

    aprobada = abs(tau) <= valor_critico
    veredicto = "aprobada" if aprobada else "rechazada"

    return TestResult(
        prueba="cramer",
        estadistico=float(tau),
        valor_critico=valor_critico,
        veredicto=veredicto,
        warning_codigo="TEST_CRITICAL_HOMOGENEITY" if not aprobada else None,
        warning_nivel="critico" if not aprobada else None,
        n1=n1,
        n2=n2,
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
