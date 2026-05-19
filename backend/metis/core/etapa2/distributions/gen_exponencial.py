"""
Distribución Generalizada Exponencial.

Parámetros: α (forma), λ (escala)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv, ml
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-77 a IV-89

  Momentos:
    α̂ por resolución de IV-77:
      (ψ'(α+1) - ψ'(α)) / (ψ(α+1) - ψ(α)) = x̄/S
    λ̂ por IV-78:
      µ = [ψ(α+1) - ψ(1)] / λ

    NOTA IV-77: la ecuación como está reduce a -1/α = x̄/S (sin solución
    válida para x̄ > 0). Por recurrencia: ψ(α+1)-ψ(α)=1/α y
    ψ'(α+1)-ψ'(α)=-1/α², por lo que el cociente es -1/α < 0 siempre.
    Se implementa la ecuación de CV-matching que surge de los momentos
    teóricos de la GE (media e varianza conocidas):
      sqrt(ψ'(1) - ψ'(α+1)) / (ψ(α+1) - ψ(1)) = S/x̄
    Pendiente confirmar IV-77 con Facundo.

  MV: sistema de primeras condiciones de IV-79 a IV-82
    LL = n·ln(α) + n·ln(λ) + (α-1)·sum(ln(1-e^(-λ·xi))) - λ·sum(xi)  (IV-79)
    Condiciones de primer orden simultáneas:
      n/α + sum(ln(1 - e^(-λ·xi))) = 0          (∂LL/∂α = 0, IV-80)
      n/λ + (α-1)·sum(xi·e^(-λ·xi)/(1-e^(-λ·xi))) - sum(xi) = 0  (∂LL/∂λ = 0, IV-81)
    α̂(λ) = -n / sum(ln(1 - e^(-λ·xi)))          (IV-82)
    Resuelto con scipy.optimize.fsolve sobre IV-80/IV-81.

  ML (Momentos L): IV-83 a IV-88
    β2/β1 = (ψ(α+1)-ψ(1)) / (ψ'(α)-ψ'(α+1))    (IV-83)
    Por recurrencia ψ'(α)-ψ'(α+1) = 1/α², por lo que IV-83 = α²·(ψ(α+1)-ψ(1))
    λ̂ = (ψ(α̂+1) - ψ(1)) / β1                     (IV-84)
    β1 = M1 (IV-85), β2 = M2 (IV-86): PWMs ascendentes (convención Hosking)

    NOTA IV-84: la tesis escribe "(ψ(1)+ψ(α̂+1))/β1", lo que da ψ(α+1)−γ.
    La media teórica de la GE es µ = (ψ(α+1)−ψ(1))/λ = (ψ(α+1)+γ)/λ,
    por lo que la forma correcta es (ψ(α+1)−ψ(1))/β1. Se implementa
    la forma correcta. Pendiente confirmar IV-84 con Facundo.

  Cuantil:
    xT = -ln[1 - F(x)^(1/α)] / λ    (IV-89)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np
from scipy.optimize import brentq, fsolve
from scipy.special import digamma, polygamma

from metis.core.etapa2.types import (
    CONVERGENCIA,
    STATUS_DISABLED_ZEROS,
    STATUS_NO_APLICABLE,
    STATUS_NO_CONVERGE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")
PENDING_ZEROS_CONFIRMATION: bool = True  # pendiente Facundo — ver constraints.md

_DENOM_GUARD = 1e-10


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if np.any(serie == 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_DISABLED_ZEROS
        )
    if np.any(serie < 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    n = len(serie)
    xbar = float(np.mean(serie))
    S = float(np.std(serie, ddof=1))

    if S == 0.0 or xbar <= 0.0:
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    if metodo == "momentos":
        # IV-77 (ver NOTA): CV-matching con momentos teóricos de la GE
        # solve: sqrt(ψ'(1) - ψ'(α+1)) / (ψ(α+1) - ψ(1)) = S/x̄
        cv = S / xbar
        psi_1 = float(digamma(1.0))
        dpsi_1 = float(polygamma(1, 1.0))  # ψ'(1) = π²/6

        def _eq_momentos(alpha: float) -> float:
            psi_a1 = float(digamma(alpha + 1.0))
            dpsi_a1 = float(polygamma(1, alpha + 1.0))
            num = dpsi_1 - dpsi_a1
            den = psi_a1 - psi_1
            if num <= 0 or den <= 0:
                return -cv
            return float(np.sqrt(num) / den) - cv

        try:
            alpha = float(brentq(_eq_momentos, 1e-3, 1e6, xtol=CONVERGENCIA))
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        # IV-78: µ = [ψ(α+1) - ψ(1)] / λ → λ = [ψ(α+1) - ψ(1)] / x̄
        psi_a1 = float(digamma(alpha + 1.0))
        denom_lam = psi_a1 - psi_1
        if abs(denom_lam) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        lam = denom_lam / xbar  # IV-78
        if lam <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "lambda": lam},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        # Sistema IV-80/IV-81 resuelto con fsolve
        def _system(params: list) -> list:
            alpha, lam = params
            if alpha <= 0 or lam <= 0:
                return [1e10, 1e10]
            evals = np.exp(-lam * serie)
            one_minus = 1.0 - evals
            if np.any(one_minus <= 0):
                return [1e10, 1e10]
            log_terms = np.log(one_minus)
            f1 = float(n / alpha + np.sum(log_terms))  # IV-80
            ratio = evals / one_minus
            f2 = float(
                n / lam + (alpha - 1.0) * np.sum(serie * ratio) - np.sum(serie)
            )  # IV-81
            return [f1, f2]

        x0 = [1.0, 1.0 / xbar]
        try:
            sol, _, ier, _ = fsolve(_system, x0, full_output=True)
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        if ier != 1:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        alpha, lam = float(sol[0]), float(sol[1])
        if alpha <= 0 or lam <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "lambda": lam},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "ml":
        # PWMs ascendentes — convención Hosking
        xi = np.sort(serie)
        beta0 = float(np.mean(xi))  # M1 en numeración de la tesis (IV-85)
        beta1 = float(np.sum(xi * np.arange(n)) / (n * (n - 1)))  # M2 en tesis (IV-86)

        if abs(beta0) < _DENOM_GUARD or beta1 <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        ratio_sample = beta1 / beta0  # β2/β1 en numeración de la tesis

        # IV-83: β2/β1 = (ψ(α+1)-ψ(1)) / (ψ'(α)-ψ'(α+1))
        # Por recurrencia ψ'(α)-ψ'(α+1) = 1/α² → RHS = α²·(ψ(α+1)-ψ(1))
        psi_1 = float(digamma(1.0))

        def _eq_ml(alpha: float) -> float:
            psi_a1 = float(digamma(alpha + 1.0))
            rhs = alpha**2 * (psi_a1 - psi_1)  # IV-83 simplificado por recurrencia
            return rhs - ratio_sample

        try:
            alpha = float(brentq(_eq_ml, 1e-4, 1e4, xtol=CONVERGENCIA))
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        if alpha <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        # IV-84: λ = (ψ(α+1) - ψ(1)) / β1 (ver NOTA en docstring)
        psi_a1 = float(digamma(alpha + 1.0))
        denom_lam = psi_a1 - psi_1
        if abs(denom_lam) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        lam = denom_lam / beta0  # IV-84
        if lam <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"alpha": alpha, "lambda": lam},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = -ln[1 - F(x)^(1/α)] / λ    (IV-89)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)  ← REQUERIDO
    parametros: {"alpha": float, "lambda": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(-np.log(1.0 - p ** (1.0 / parametros["alpha"])) / parametros["lambda"])
