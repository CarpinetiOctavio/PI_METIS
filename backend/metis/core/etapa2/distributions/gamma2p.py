"""
Distribución Gamma 2 parámetros.

Parámetros: α (forma/shape), β (escala/scale)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv, ml
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-123 a IV-135

  Momentos:
    α̂ = (x̄/S)²          (IV-123)  ← forma (shape)
    β̂ = S²/x̄             (IV-124)  ← escala (scale)

  MV (aproximación de Thom):
    C = ln(x̄) - (1/n)·sum(ln xi)    (IV-127, IV-128)
    α̂ = (1 + √(1 + 4C/3)) / (4C)   (IV-126)  ← forma (lo que tesis llama β̂)
    β̂ = x̄/α̂                         (IV-125)  ← escala (lo que tesis llama α̂)

  ML (Momentos L — Hosking 1990):
    τ2 = λ2/λ1                        (IV-129)
    Para 0 ≤ τ2 < 0.5:
      z = π²·τ2                        (IV-131)
      α̂ = (1 - 0.308·z) / (z - 0.05812·z² + 0.01765·z³)   (IV-130) ← forma
    Para 0.5 ≤ τ2 < 1:
      z = 1 - τ2                       (IV-133)
      α̂ = (0.7213·z - 0.59478·z²) / (1 - 2.1817·z + 1.2113·z²)  (IV-132) ← forma
    β̂ = x̄/α̂                          (IV-134)  ← escala

  Cuantil:
    xT = scipy.stats.gamma.ppf(p, a=α̂, scale=β̂)   (equivalente a IV-135, WH exacto)

NOTA de nomenclatura: la tesis usa β̂ como forma en MV/ML (ecuaciones IV-125/126)
y α̂ como forma en Momentos (IV-123). Este módulo unifica: alpha=forma, beta=escala.

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
"""

import numpy as np
from scipy.stats import gamma as _gamma_dist

from metis.core.etapa2.types import (
    STATUS_NO_APLICABLE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0

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
        alpha = (xbar / S) ** 2  # IV-123 — forma
        beta = S**2 / xbar  # IV-124 — escala
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
        # Thom's approximation — IV-126 resuelve la forma (lo que tesis llama β̂)
        alpha = (1.0 + np.sqrt(1.0 + 4.0 * C / 3.0)) / (4.0 * C)  # IV-126 — forma
        if alpha <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta = xbar / alpha  # IV-125 — escala
        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "ml":
        n = len(serie)
        xi = np.sort(serie)  # ascendente para PWM

        # β0 = M(0), β1 = M(1) con pesos ascendentes — misma convención que Normal ML
        beta0 = float(np.mean(xi))
        beta1 = float(np.sum(xi * np.arange(n)) / (n * (n - 1)))  # IV-129 → Hosking

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

        if tau2 < 0.5:  # IV-130/IV-131
            z = np.pi**2 * tau2  # IV-131
            denom = z - 0.05812 * z**2 + 0.01765 * z**3
            if abs(denom) < _DENOM_GUARD:
                return MetodoResult(
                    metodo=metodo,
                    parametros=None,
                    eea=None,
                    status=STATUS_NO_APLICABLE,
                )
            alpha = (1.0 - 0.308 * z) / denom  # IV-130 — forma
        else:  # IV-132/IV-133
            z = 1.0 - tau2  # IV-133
            denom = 1.0 - 2.1817 * z + 1.2113 * z**2
            if abs(denom) < _DENOM_GUARD:
                return MetodoResult(
                    metodo=metodo,
                    parametros=None,
                    eea=None,
                    status=STATUS_NO_APLICABLE,
                )
            alpha = (0.7213 * z - 0.59478 * z**2) / denom  # IV-132 — forma

        if alpha <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta = xbar / alpha  # IV-134 — escala
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
    xT via función gamma incompleta inversa — equivalente exacto a WH IV-135.

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float (forma/shape), "beta": float (escala/scale)}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(_gamma_dist.ppf(p, a=parametros["alpha"], scale=parametros["beta"]))
