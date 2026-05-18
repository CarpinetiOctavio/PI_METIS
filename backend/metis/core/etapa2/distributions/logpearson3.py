"""
Distribución Log-Pearson III.

Trabaja sobre yi = ln(xi). Parámetros: α, β, y0
N_PARAMETROS = 3

Métodos aplicables: momentos_directo, momentos_indirecto, MV
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-247 a IV-260

  Momentos Método Directo: IV-247 a IV-254
    µr = (1/n)·sum(xi^r)  (IV-248)
    B = (3·ln(µ1) - ln(µ3)) / (2·ln(µ1) - ln(µ2))  (IV-249)
    Si 3 < B ≤ 5.3: A por IV-252
    Si 5.3 < B ≤ 6: A por IV-251
    α̂ = (A+1)^(1/3)  (IV-247), β̂ por IV-253, ŷ0 por IV-254
  Momentos Método Indirecto: IV-255 a IV-256  ← preferido en la práctica (tesis)
    yi = ln(xi)
    β̂ = 4/gy²  (IV-255),  α̂ = Sy/β̂  (IV-256)
  MV: sistema iterativo IV-257 a IV-259
    NOTA: frecuentemente No Converge — comportamiento esperado según tesis
  Cuantil:
    xT = exp( y0 + α̂·β̂·(1 - UT/(9β̂) + 1/(9β̂))³ )  (IV-260)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos_directo", "momentos_indirecto", "mv")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima α, β e y0 según el método indicado.

    momentos_directo:   IV-247 a IV-254
    momentos_indirecto: IV-255, IV-256 (preferido en la práctica)
    mv:                 IV-257 a IV-259 (puede no converger)

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = exp( y0 + α̂·β̂·(1 - UT/(9β̂) + 1/(9β̂))³ )  (IV-260)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float, "y0": float}
    """
    raise NotImplementedError
