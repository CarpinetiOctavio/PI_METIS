"""
Distribución Gamma 3 parámetros (equivalente a Pearson III en escala original).

Parámetros: β (forma), α (escala), x0 (umbral)
N_PARAMETROS = 3

Métodos aplicables: momentos, mv
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-137 a IV-144

  Momentos:
    β̂ = 4/g²          (IV-137)
    α̂ = S/β̂           (IV-138)  ← usa β̂ de IV-137
    x̂0 = x̄ - S·β̂     (IV-139)  ← usa β̂ de IV-137
    g = asimetría no sesgada de la serie

  MV: perfil de verosimilitud sobre x0 (IV-140 a IV-143)
    Para x0 fijo: α̂ y β̂ de Gamma 2p sobre (xi - x0) via Thom (IV-126/IV-143)
    x0 por minimización del perfil de verosimilitud negativo
    bounds: (min(xi) - 20·S, min(xi) - 1e-9)
    ψ(β) ≈ ln(β) - 1/(2β) - 1/(12β²)   (IV-143, digamma de Thom)
    NOTA: puede No Converger — comportamiento esperado

  Cuantil:
    xT = x0 + α̂·β̂·(1 - 1/(9·β̂) + UT·sqrt(1/(9·β̂)))³    (IV-144)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import gammaln

from metis.core.etapa2.types import (
    CONVERGENCIA,
    STATUS_NO_APLICABLE,
    STATUS_NO_CONVERGE,
    STATUS_OK,
    MetodoResult,
)
from metis.core.etapa2.utils import _ut

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv")
PENDING_ZEROS_CONFIRMATION: bool = True  # pendiente Facundo — ver constraints.md

_DENOM_GUARD = 1e-10


def _skewness(x: np.ndarray) -> float:
    n = len(x)
    if n < 3:
        return 0.0
    xbar = float(np.mean(x))
    sx = float(np.std(x, ddof=1))
    if sx == 0.0:
        return 0.0
    return float(n * np.sum((x - xbar) ** 3) / ((n - 1) * (n - 2) * sx**3))


def _thom_beta(zi: np.ndarray):
    """Thom IV-126/IV-143: β̂ (forma) y α̂ (escala) de Gamma 2p sobre zi>0. Retorna (β, α) o None."""
    zbar = float(np.mean(zi))
    C = float(np.log(zbar) - np.mean(np.log(zi)))  # IV-127/128
    if abs(C) < _DENOM_GUARD:
        return None
    beta = (1.0 + np.sqrt(1.0 + 4.0 * C / 3.0)) / (4.0 * C)  # IV-126
    if beta <= 0.0:
        return None
    alpha = zbar / beta  # IV-125
    return beta, alpha


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    n = len(serie)
    xbar = float(np.mean(serie))
    S = float(np.std(serie, ddof=1))
    if S == 0.0:
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    g = _skewness(serie)
    if abs(g) < _DENOM_GUARD:
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    if metodo == "momentos":
        beta = 4.0 / g**2  # IV-137
        alpha = S / beta  # IV-138
        x0 = xbar - S * beta  # IV-139

        # NOTA: con g pequeño (cercano a 0), β̂=4/g² puede ser
        # muy grande produciendo x0 muy negativo y EEA alta.
        # Comportamiento correcto — el ranking lo deprioritiza
        # automáticamente. La tesis no define umbral mínimo de g.
        if x0 >= float(np.min(serie)):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"beta": beta, "alpha": alpha, "x0": x0},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        xi_min = float(np.min(serie))

        def _neg_profile_ll(x0: float) -> float:
            zi = serie - x0
            if np.any(zi <= 0.0):
                return np.inf
            fit = _thom_beta(zi)
            if fit is None:
                return np.inf
            beta_hat, alpha_hat = fit
            ll = (
                (beta_hat - 1.0) * np.sum(np.log(zi))
                - np.sum(zi) / alpha_hat
                - n * (beta_hat * np.log(alpha_hat) + float(gammaln(beta_hat)))
            )
            return -ll

        try:
            result = minimize_scalar(
                _neg_profile_ll,
                bounds=(xi_min - 20.0 * S, xi_min - 1e-9),
                method="bounded",
                options={"xatol": CONVERGENCIA},
            )
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        if not result.success:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        x0 = float(result.x)
        zi = serie - x0
        fit = _thom_beta(zi)
        if fit is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )
        beta, alpha = fit

        return MetodoResult(
            metodo=metodo,
            parametros={"beta": beta, "alpha": alpha, "x0": x0},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 + α̂·β̂·(1 - 1/(9·β̂) + UT·sqrt(1/(9·β̂)))³    (IV-144)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"beta": float (forma), "alpha": float (escala), "x0": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    x0 = parametros["x0"]
    beta = parametros["beta"]
    alpha = parametros["alpha"]
    wh = 1.0 - 1.0 / (9.0 * beta) + _ut(p) * np.sqrt(1.0 / (9.0 * beta))
    return x0 + alpha * beta * wh**3
