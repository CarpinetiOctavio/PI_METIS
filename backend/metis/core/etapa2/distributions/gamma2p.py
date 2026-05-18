"""
Distribución Gamma 2 parámetros.

Parámetros: α (forma), β (escala)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV, ML
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-123 a IV-135

  Momentos: IV-123 a IV-127
    α̂ = (x̄/S)²          (IV-123)
    β̂ = S²/x̄             (IV-124)
  MV: sistema iterativo IV-128 a IV-131
    ln(α̂) - ψ(α̂) = ln(x̄) - (1/n)·sum(ln xi)  (IV-128)
    β̂ = x̄/α̂              (IV-129)
    ψ(α): digamma approx IV-130, IV-131
  ML (Momentos L): IV-132 a IV-135
    τ₂ = λ₂/λ₁           (IV-132)
    α̂ por IV-133, β̂ por IV-134, cuantil IV-135
  Cuantil:
    xT via función gamma incompleta inversa — F(x;α,β) = F(x/β; α)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima α y β según el método indicado.

    Momentos: IV-123, IV-124
    MV:       IV-128 a IV-131 (iterativo)
    ML:       IV-132 a IV-135

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT via función gamma incompleta inversa — F(x;α,β) = F(x/β; α)  (IV-135)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float}
    """
    raise NotImplementedError
