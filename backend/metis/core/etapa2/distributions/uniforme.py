"""
Distribución Uniforme.

Parámetros: α (mínimo de la distribución), β (máximo de la distribución)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-58 a IV-62

  Momentos:
    α̂ = x̄ - √3·S    (IV-58)
    β̂ = x̄ + √3·S    (IV-59)
  MV:
    α̂ = min(x)       (IV-60)
    β̂ = max(x)       (IV-61)
  Cuantil:
    xT = F(x)·(β - α) + α    (IV-62)

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import (
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if metodo == "momentos":
        xbar = float(np.mean(serie))
        S = float(np.std(serie, ddof=1))
        if S == 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        alpha = xbar - np.sqrt(3.0) * S  # IV-58
        beta = xbar + np.sqrt(3.0) * S  # IV-59
        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        alpha = float(np.min(serie))  # IV-60
        beta = float(np.max(serie))  # IV-61
        if alpha >= beta:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = F(x)·(β - α) + α    (IV-62)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return p * (parametros["beta"] - parametros["alpha"]) + parametros["alpha"]
