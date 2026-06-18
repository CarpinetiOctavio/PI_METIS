"""
Distribución Gamma 2 parámetros.

Parámetros: α (escala), β (forma)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv, ml
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-123 a IV-135

  Momentos:
    α̂ = S²/x̄          (IV-123)  ← escala
    β̂ = (x̄/S)²        (IV-124)  ← forma

  MV (aproximación de Thom):
    ȳ = (1/n)·Σln(xi)   (IV-128)
    C = ln(x̄) - ȳ       (IV-127)
    β̂ = (1 + √(1 + 4C/3)) / (4C)   (IV-126)  ← forma
    α̂ = x̄/β̂             (IV-125)  ← escala

  ML (Momentos L):
    xs = serie ordenada de MAYOR a MENOR
    β0 = M̂(0) = x̄
    β1 = M̂(1) = (1/(n(n-1)))·Σ_{i=1}^{n-1}(n-i)·xs_{(i)}  (IV-87, desc.)
    λ1 = β0,  λ2 = 2·β1 - β0
    τ2 = λ2/λ1                        (IV-129)
    Para 0 ≤ τ2 < 0.5:
      z = π·τ2²                        (IV-131)
      β̂ = (1 - 0.308·z) / (z - 0.05812·z² + 0.01765·z³)   (IV-130)
    Para 0.5 ≤ τ2 < 1:
      z = 1 - τ2                       (IV-133)
      β̂ = (0.7213·z - 0.59478·z²) / (1 - 2.1817·z + 1.2113·z²)  (IV-132)
    α̂ = x̄/β̂                          (IV-134)  ← escala

  Cuantil:
    xT = α̂·β̂·(1 - 1/(9·β̂) + UT·√(1/(9·β̂)))³    (IV-135)

NOTA: la tesis usa α̂ para escala y β̂ para forma en esta distribución.
      El módulo respeta esa convención: alpha=escala, beta=forma.

RESTRICCIÓN: deshabilitada si algún xi = 0 (confirmado con Facundo)
"""

import numpy as np

from metis.core.etapa2.types import (
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)
from metis.core.etapa2.utils import _ut

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")
DISABLED_WITH_ZEROS: bool = True

_DENOM_GUARD = 1e-10


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if np.any(serie <= 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    xbar = float(np.mean(serie))
    S = float(np.std(serie, ddof=1))
    if S == 0.0:
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    if metodo == "momentos":
        alpha = S**2 / xbar  # IV-123 — escala
        beta = (xbar / S) ** 2  # IV-124 — forma
        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        y = float(np.mean(np.log(serie)))  # IV-128
        C = np.log(xbar) - y  # IV-127
        if abs(C) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta = (1.0 + np.sqrt(1.0 + 4.0 * C / 3.0)) / (4.0 * C)  # IV-126 — forma
        if beta <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        alpha = xbar / beta  # IV-125 — escala
        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "ml":
        n = len(serie)
        xs = np.sort(serie)[::-1]  # descendente: xs[0] = máximo

        beta0 = float(np.mean(xs))  # M̂(0)
        weights = np.arange(n - 1, 0, -1, dtype=float)  # [n-1, n-2, …, 1]
        beta1 = float(np.dot(xs[: n - 1], weights) / (n * (n - 1)))  # M̂(1) IV-87

        lambda1 = beta0
        lambda2 = 2.0 * beta1 - beta0
        if abs(lambda1) < _DENOM_GUARD or lambda2 <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        tau2 = lambda2 / lambda1  # IV-129
        if not (0.0 <= tau2 < 1.0):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        if tau2 < 0.5:
            z = np.pi * tau2**2  # IV-131
            denom = z - 0.05812 * z**2 + 0.01765 * z**3
            if abs(denom) < _DENOM_GUARD:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
                )
            beta = (1.0 - 0.308 * z) / denom  # IV-130 — forma
        else:
            z = 1.0 - tau2  # IV-133
            denom = 1.0 - 2.1817 * z + 1.2113 * z**2
            if abs(denom) < _DENOM_GUARD:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
                )
            beta = (0.7213 * z - 0.59478 * z**2) / denom  # IV-132 — forma

        if beta <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        alpha = xbar / beta  # IV-134 — escala
        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = α̂·β̂·(1 - 1/(9·β̂) + UT·√(1/(9·β̂)))³    (IV-135)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float (escala), "beta": float (forma)}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    alpha = parametros["alpha"]  # escala
    beta = parametros["beta"]  # forma
    t = 1.0 / (9.0 * beta)
    wh = (1.0 - t + _ut(p) * np.sqrt(t)) ** 3
    return float(alpha * beta * wh)
