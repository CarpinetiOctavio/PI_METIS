"""
Distribución Gumbel (Valor Extremo Tipo I).

Parámetros: µ (posición), α (escala)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV, ML, ME
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-177 a IV-199

  Momentos:
    µ̂ = x̄ - 0.45·S    (IV-177)
    α̂ = 0.78·S         (IV-178)
  MV: sistema iterativo IV-179 a IV-187
    yi = (xi - µ̂) / α̂              (IV-181)
    δµ, δα por IV-184, IV-185
    µ̂j+1, α̂j+1 por IV-186, IV-187
  ML (Momentos L):
    µ̂ = λ1 - 0.577216·α̂    (IV-188)
    α̂ = λ2 / ln(2)          (IV-189)
  ME (Máxima Entropía): sistema iterativo IV-190 a IV-198
    Criterios: 0.577216 - P ≈ 0,  1 - R ≈ 0  (IV-193, IV-194)
    δα, δµ por IV-195, IV-196
    µ̂j+1, α̂j+1 por IV-197, IV-198
  Cuantil:
    xT = µ̂ - α̂·ln{-ln[F(x)]}  (IV-199)

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml", "me")


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima µ y α según el método indicado.

    Momentos: IV-177, IV-178
    MV:       IV-179 a IV-187 (iterativo)
    ML:       IV-188, IV-189
    ME:       IV-190 a IV-198 (iterativo)

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = µ̂ - α̂·ln{-ln[F(x)]}  (IV-199)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu": float, "alpha": float}
    """
    raise NotImplementedError
