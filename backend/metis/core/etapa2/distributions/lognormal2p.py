"""
Distribución Log-Normal 2 parámetros.

Parámetros: µy (media de ln(x)), σy (desvío estándar de ln(x))
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV
NOTA: Momentos y MV producen los mismos estimadores (Tesis Facundo).
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-107 a IV-109

  Momentos y MV (coinciden):
    µ̂y = (1/n)·sum(ln xi)               (IV-107)
    σ̂²y = sum((ln xi - µ̂y)²) / (n-1)   (IV-108)
  Cuantil:
    xT = exp(µ̂y + UT·σ̂y)               (IV-109)
    UT por aproximación racional IV-102 a IV-105 (igual que Normal)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima µy y σy según el método indicado.

    Momentos/MV: IV-107, IV-108

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = exp(µ̂y + UT·σ̂y)  (IV-109)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu_y": float, "sigma_y": float}
    """
    raise NotImplementedError
