"""
Distribución Exponencial 1 parámetro (β).

Parámetros: β (tasa = 1/media)
N_PARAMETROS = 1

Métodos aplicables: momentos, mv
NOTA: Momentos y MV producen el mismo estimador (Tesis Facundo).
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-65 a IV-67

  Momentos y MV (coinciden):
    β̂ = 1/x̄    (IV-66)
  Cuantil:
    xT = -ln[1 - F(x)] / β    (IV-67)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np

from metis.core.etapa2.types import (
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 1
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if metodo not in ("momentos", "mv"):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )
    if np.any(serie <= 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )
    beta = 1.0 / float(np.mean(serie))  # IV-66
    return MetodoResult(
        metodo=metodo,
        parametros={"beta": beta},
        eea=None,
        status=STATUS_OK,
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = -ln[1 - F(x)] / β    (IV-67)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"beta": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(-np.log(1.0 - p) / parametros["beta"])
