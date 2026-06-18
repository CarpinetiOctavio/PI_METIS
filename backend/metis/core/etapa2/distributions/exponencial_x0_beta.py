"""
Distribución Exponencial 2 parámetros (x0, β).

Parámetros: x0 (umbral), β (escala)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-70 a IV-74

  Momentos:
    β̂ = S           (IV-70)
    x̂0 = x̄ - S     (IV-71)

  MV:
    β̂ = (sum(xi) - n·x1) / (n·(n-1))    (IV-72)  x1 = mínimo de la muestra
    x̂0 = x1 - β̂/n                        (IV-73)

  Cuantil:
    xT = x0 - β·ln[1 - F(x)]    (IV-74)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
Hasta confirmar: si algún xi = 0 → STATUS_DISABLED_ZEROS.
"""

import numpy as np

from metis.core.etapa2.types import (
    STATUS_DISABLED_ZEROS,
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
PENDING_ZEROS_CONFIRMATION: bool = True  # pendiente Facundo — ver constraints.md

_DENOM_GUARD = 1e-10


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if np.any(serie == 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_DISABLED_ZEROS
        )

    if metodo == "momentos":
        xbar = float(np.mean(serie))
        S = float(np.std(serie, ddof=1))
        if S == 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta = S  # IV-70
        x0 = xbar - S  # IV-71
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
