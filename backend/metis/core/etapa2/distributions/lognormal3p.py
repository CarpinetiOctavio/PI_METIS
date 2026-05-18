"""
Distribución Log-Normal 3 parámetros.

Parámetros: x0 (umbral), µy (media de ln(x-x0)), σy (desvío de ln(x-x0))
N_PARAMETROS = 3

Métodos aplicables: Momentos, MV
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-111 a IV-120

  Momentos: sistema IV-111 a IV-116
    w = (g²/4 + 1)^(1/2) - g/2        (IV-113)
    ẑ = w^(1/3) - w^(-1/3)             (IV-114)
    µ̂y = ln(Sy/nz) - (1/2)·ln(ẑ²+1)  (IV-115)
    σ̂²y = ln(ẑ²+1)                    (IV-116)
    x̂0 = x̄ - (nx̂/ẑ)                  (IV-111)
  MV: sistema iterativo IV-117 a IV-119
    µ̂y = (1/n)·sum(ln(xi - x0))       (IV-117)
    σ̂²y = (1/n)·sum((ln(xi-x0)-µ̂y)²) (IV-118)
    x0 por resolución iterativa de IV-119
  Cuantil:
    xT = x0 + exp(µ̂y + UT·σ̂y)        (IV-120)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
PENDING_ZEROS_CONFIRMATION: bool = (
    True  # ver core-etapa2-implementation.md — pendiente Facundo
)


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima x0, µy y σy según el método indicado.

    Momentos: IV-111 a IV-116
    MV:       IV-117 a IV-119 (iterativo)

    TODO: implementar en Fase 2/4.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 + exp(µ̂y + UT·σ̂y)  (IV-120)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"x0": float, "mu_y": float, "sigma_y": float}
    """
    raise NotImplementedError
