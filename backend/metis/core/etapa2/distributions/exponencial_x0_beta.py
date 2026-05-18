"""
Distribución Exponencial 2 parámetros (x0, β).

Parámetros: x0 (umbral), β (escala)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-70 a IV-74

  Momentos: IV-70 a IV-72
    β̂ = S               (IV-70)
    x̂0 = x̄ - S          (IV-71)
  MV: IV-73, IV-74
    x̂0 = min(xi)        (IV-73)
    β̂ = x̄ - x̂0          (IV-74)
  Cuantil:
    xT = x0 - β̂·ln(1 - F(x))  (IV-74 extendida)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
PENDING_ZEROS_CONFIRMATION: bool = True  # ver constraints.md — pendiente Facundo


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima x0 y β según el método indicado.

    Momentos: IV-70, IV-71
    MV:       IV-73, IV-74

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 - β̂·ln(1 - F(x))  (IV-74)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"x0": float, "beta": float}
    """
    raise NotImplementedError
