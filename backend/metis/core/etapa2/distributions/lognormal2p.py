"""
Distribución Log-Normal 2 parámetros.

Parámetros: µy (media de ln(x)), σy (desvío estándar de ln(x))
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV
NOTA: Momentos y MV producen los mismos estimadores (Tesis Facundo).
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-107 a IV-109

  Momentos y MV (coinciden):
    µ̂y = (1/n)·sum(ln xi)               (IV-107)
    σ̂y = sqrt( sum((ln xi - µ̂y)²) / (n-1) )  (IV-108, ddof=1)
  Cuantil:
    xT = exp(µ̂y + UT·σ̂y)               (IV-109)
    UT por aproximación racional IV-102 a IV-105 (igual que Normal)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np

from metis.core.etapa2.types import (
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)
from metis.core.etapa2.utils import _ut

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if metodo not in ("momentos", "mv"):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    if np.any(serie <= 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    ln_x = np.log(serie)
    mu_y = float(np.mean(ln_x))  # IV-107
    sigma_y = float(np.std(ln_x, ddof=1))  # IV-108
    return MetodoResult(
        metodo=metodo,
        parametros={"mu_y": mu_y, "sigma_y": sigma_y},
        eea=None,
        status=STATUS_OK,
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = exp(µ̂y + UT·σ̂y)  (IV-109)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu_y": float, "sigma_y": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(np.exp(parametros["mu_y"] + _ut(p) * parametros["sigma_y"]))
