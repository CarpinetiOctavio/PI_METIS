"""
Distribución Uniforme.

Parámetros: α (mínimo de la distribución), β (máximo de la distribución)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-58 a IV-62

  Momentos:  α̂ = x̄ - √3·S  (IV-58)
             β̂ = x̄ + √3·S  (IV-59)
  MV:        α̂ = min(x)     (IV-60)
             β̂ = max(x)     (IV-61)
  Cuantil:   xT = F(x)·(β - α) + α  (IV-62)

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima parámetros α y β según el método indicado.

    Momentos: IV-58, IV-59
    MV:       IV-60, IV-61

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = F(x)·(β - α) + α  (IV-62)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float}
    """
    raise NotImplementedError
