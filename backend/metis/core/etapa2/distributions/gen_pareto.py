"""
Distribución Generalizada de Pareto.

Parámetros: α (escala), β (forma), x0 (umbral/posición)
N_PARAMETROS = 3

Métodos aplicables: Momentos, MV, MC
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-145 a IV-156

  Momentos: IV-145 a IV-149
    β̂ por IV-146 (función de g)
    α̂ por IV-147
    x̂0 por IV-148
  MV: sistema iterativo IV-150 a IV-153
    Actualización de β, α, x0 via IV-151 a IV-153
  MC (Mínimos Cuadrados): IV-153 a IV-155
    Minimiza sum[(xi - x̂i)²] sobre los parámetros — IV-154
    Sistema lineal resultante IV-155
  Cuantil:
    xT = x0 + (α/β)·[1 - (1-F(x))^β]  (IV-156)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "mc")
PENDING_ZEROS_CONFIRMATION: bool = True  # ver constraints.md — pendiente Facundo


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima α, β y x0 según el método indicado.

    Momentos: IV-145 a IV-149
    MV:       IV-150 a IV-153 (iterativo)
    MC:       IV-153 a IV-155 (Mínimos Cuadrados)

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 + (α/β)·[1 - (1-F(x))^β]  (IV-156)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float, "x0": float}
    """
    raise NotImplementedError
