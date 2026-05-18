"""
Distribución Exponencial 1 parámetro (β).

Parámetros: β (escala)
N_PARAMETROS = 1

Métodos aplicables: Momentos, MV
NOTA: Momentos y MV producen el mismo estimador (Tesis Facundo).
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-65 a IV-67

  Momentos y MV (coinciden):
    β̂ = x̄               (IV-65)
  Cuantil:
    xT = -β̂·ln(1 - F(x))  (IV-67)
    O equivalentemente: xT = β̂·ln(T)  donde T = 1/(1-F(x))

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 1
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima β según el método indicado.

    Momentos/MV: IV-65 (coinciden)

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = -β̂·ln(1 - F(x))  (IV-67)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"beta": float}
    """
    raise NotImplementedError
