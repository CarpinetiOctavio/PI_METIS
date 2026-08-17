"""
Distribución Exponencial 2 parámetros (x0, β).

Parámetros: x0 (umbral), β (escala)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-70 a IV-74

  Momentos:
    β̂ = S           (IV-70)
    x̂0 = x̄ - S     (IV-71)
    STATUS_NO_APLICABLE si x̂0 ≥ min(xi) — ver docs/auditoria/hallazgos/
    restricciones-dominio-etapa2.md (17/08/2026)

  MV:
    β̂ = (sum(xi) - n·x1) / (n-1)    (IV-72)  x1 = mínimo de la muestra
    x̂0 = x1 - β̂/n                    (IV-73)

  Cuantil:
    xT = x0 - β·ln[1 - F(x)]    (IV-74)

RESTRICCIÓN ante ceros: pregunta de dominio pendiente de confirmación de
Facundo (¿tiene sentido físico un cero para esta variable?) — no de mecánica
de cálculo. Ninguna fórmula de este módulo (Momentos ni MV) aplica log(xi)
sobre datos crudos, así que un cero no rompe el cálculo — verificado en
docs/auditoria/hallazgos/restricciones-dominio-etapa2.md. DECISIÓN 060
estableció que, mientras se espera esa confirmación, el default es calcular
igual (con DIST_ZEROS_TOLERATED emitido por pipeline_etapa2.py, no acá) en
vez de bloquear — esto resuelve el default de implementación, no la pregunta
de dominio, que sigue abierta en pendientes-facundo.md.
"""

import numpy as np

from metis.core.etapa2.types import (
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
PENDING_ZEROS_CONFIRMATION: bool = (
    True  # pregunta de dominio, no de cálculo — ver DECISIÓN 060
)

_DENOM_GUARD = 1e-10


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if metodo == "momentos":
        xbar = float(np.mean(serie))
        S = float(np.std(serie, ddof=1))
        if S == 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta = S  # IV-70
        x0 = xbar - S  # IV-71

        # x0 debe ser menor que todos los xi para que el soporte de IV-68/69
        # (x > x0) se cumpla — mismo guard que gamma3p.py/lognormal3p.py.
        # DECISIÓN 060 — ver docs/decisiones/decision060.md y
        # docs/auditoria/hallazgos/restricciones-dominio-etapa2.md
        # (17/08/2026): sin este guard, 6 de las 9 estaciones de la tesis
        # producían x0 >= min(serie) sin marcarlo.
        if x0 >= float(np.min(serie)):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"x0": x0, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        n = len(serie)
        if n < 2:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        x1 = float(np.min(serie))  # mínimo de la muestra
        # IV-72: β̂ = Σ(xi - x1) / (n-1) = (Σxi - n·x1) / (n-1)
        beta = (float(np.sum(serie)) - n * x1) / (n - 1)  # IV-72
        if beta <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        x0 = x1 - beta / n  # IV-73
        return MetodoResult(
            metodo=metodo,
            parametros={"x0": x0, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 - β·ln[1 - F(x)]    (IV-74)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"x0": float, "beta": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(parametros["x0"] - parametros["beta"] * np.log(1.0 - p))
