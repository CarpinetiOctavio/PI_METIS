"""
Distribución Gamma 3 parámetros (equivalente a Pearson III en escala original).

Parámetros: α (forma), β (escala), x0 (umbral)
N_PARAMETROS = 3

Métodos aplicables: Momentos, MV
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-137 a IV-144

  Momentos: IV-137 a IV-140
    α̂ = 4/g²             (IV-137)
    β̂ = S·g/2            (IV-138)
    x̂0 = x̄ - 2S/g        (IV-139)
  MV: sistema iterativo IV-141 a IV-143
    Igual que Gamma 2p desplazada por x0; iteración sobre IV-141 a IV-143
  Cuantil:
    xT = x0 + β·Γ⁻¹(α, F(x))  (IV-144)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
PENDING_ZEROS_CONFIRMATION: bool = True  # ver constraints.md — pendiente Facundo


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima α, β y x0 según el método indicado.

    Momentos: IV-137 a IV-139
    MV:       IV-141 a IV-143 (iterativo)

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 + β·Γ⁻¹(α, F(x))  (IV-144)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float, "x0": float}
    """
    raise NotImplementedError
