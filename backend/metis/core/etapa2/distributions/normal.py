"""
Distribución Normal.

Parámetros: µ (media), σ (desvío estándar)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV, ML
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-92 a IV-105

  Momentos y MV (coinciden):
    µ̂ = x̄                           (IV-92)
    σ̂² = sum(xi - x̄)² / (n-1)      (IV-93)
  ML (Momentos L):
    µ̂ = λ1 = β0                      (IV-94, IV-96, IV-98)
    σ̂ = 1.772·λ2                     (IV-95)
    λ2 = 2·β1 - β0                   (IV-97)
  Cuantil:
    xT = µ̂ + σ̂·UT                    (IV-101)
    UT por aproximación racional      (IV-102 a IV-105)
    Coeficientes: b0=2.515517, b1=0.802853, b2=0.010328,
                  b3=1.432788, b4=0.189269, b5=0.001308

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima µ y σ según el método indicado.

    Momentos/MV: IV-92, IV-93
    ML:          IV-94 a IV-100

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = µ̂ + σ̂·UT  (IV-101), UT por aproximación racional IV-102 a IV-105.

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu": float, "sigma": float}
    """
    raise NotImplementedError
