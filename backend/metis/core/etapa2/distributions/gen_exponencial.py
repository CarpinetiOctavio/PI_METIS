"""
Distribución Generalizada Exponencial.

Parámetros: α (escala), β (forma)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV, ML
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-77 a IV-89

  Momentos: IV-77 a IV-81
    β̂ por IV-78 (función de g)
    α̂ por IV-79
  MV: sistema iterativo IV-82 a IV-85
    Actualización de α, β via IV-83, IV-84
    Criterio de convergencia: IV-85
  ML (Momentos L): IV-86 a IV-88
    β̂ por IV-87 (función de λ₁, λ₂)
    α̂ por IV-88
  Cuantil:
    xT = -(α/β)·ln(1 - F(x)^(1/β))  (IV-89)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")
PENDING_ZEROS_CONFIRMATION: bool = True  # ver constraints.md — pendiente Facundo


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima α y β según el método indicado.

    Momentos: IV-77 a IV-81
    MV:       IV-82 a IV-85 (iterativo)
    ML:       IV-86 a IV-88

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = -(α/β)·ln(1 - F(x)^(1/β))  (IV-89)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float}
    """
    raise NotImplementedError
