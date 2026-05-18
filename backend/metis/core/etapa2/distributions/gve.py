"""
Distribución GVE (General de Valores Extremos).

Parámetros: α (escala), β (forma), ν (posición)
N_PARAMETROS = 3

Métodos aplicables: Momentos, MV, ML
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-203 a IV-245

  Momentos: polinomios en g según rango de asimetría
    Si -11.35 < g < 11.396: β̂ por IV-203
    Si 11.4  < g < 18.95:  β̂ por IV-204
    A, µ̂, B, Var por IV-205 a IV-207
    NOTA: frecuentemente No Converge (comportamiento esperado según tesis)
  MV: sistema iterativo IV-220 a IV-233
    Funciones auxiliares a, b, c, f, gs, h como polinomios en β̂ (IV-225 a IV-230)
    δν, δα, δβ por IV-222 a IV-224
    ν̂, α̂, β̂ actualizados por IV-231 a IV-233
  ML (Momentos L): IV-234 a IV-244
    E = (2·M0 - M1) / (3·M0 - M2)    (IV-234)
    β̂ = 7.859·E + 2.9554·E²          (IV-235)
    α̂ = C/(A·B)                       (IV-240)
    ν̂ = M0 + D·α̂                      (IV-241)
  Cuantil:
    xT = ν + α·{1 - [-ln F(x)]^β} / β  (IV-245)

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    """
    Estima α, β y ν según el método indicado.

    Momentos: IV-203 a IV-207 (puede no converger)
    MV:       IV-220 a IV-233 (iterativo)
    ML:       IV-234 a IV-244

    TODO: implementar en Fase 2.
    """
    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = ν + α·{1 - [-ln F(x)]^β} / β  (IV-245)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "beta": float, "nu": float}
    """
    raise NotImplementedError
