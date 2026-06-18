"""
Distribución Gamma 3 parámetros (equivalente a Pearson III en escala original).

Parámetros: β (forma), α (escala), x0 (umbral)
N_PARAMETROS = 3

Métodos aplicables: momentos, mv
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-137 a IV-144

  Momentos:
    β̂ = 4/g²          (IV-137)
    α̂ = S/√β̂          (IV-138)
    x̂0 = x̄ - S·√β̂    (IV-139)
    g = asimetría no sesgada de la serie

  MV: sistema iterativo IV-140 a IV-143
    Para x0 fijo:
      S1 = Σ(xi-x0),  S2 = Σ(1/(xi-x0))
      β̂ = 1 / (1 - n²/(S1·S2))            (IV-140)
      α̂ = (1/n)·S1 - n/S2                  (IV-141)
    x0 por brentq sobre IV-142:
      F(x0) = Σln(xi-x0) - n·ln(α̂) - n·ψ(β̂) = 0
    ψ(β) ≈ ln(β) - 1/(2β) - 1/(12β²)      (IV-143, Thom)
    NOTA: puede No Converger — comportamiento esperado

  Cuantil:
    xT = x0 + α̂·β̂·(1 - 1/(9·β̂) + UT·√(1/(9·β̂)))³    (IV-144)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np
from scipy.optimize import brentq

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
PENDING_ZEROS_CONFIRMATION: bool = True

_DENOM_GUARD = 1e-10


def _skewness(x: np.ndarray) -> float:
    # IV-4: g_sesg = mean((xi-xbar)³) / (var_sesgada)^(3/2)
    # IV-5: g_insesg = n²/((n-1)(n-2)) * g_sesg
    n = len(x)
    if n < 3:
        return 0.0
    xbar = float(np.mean(x))
    var_sesgada = float(np.var(x, ddof=0))
    if var_sesgada == 0.0:
        return 0.0
    g_sesg = float(np.mean((x - xbar) ** 3) / var_sesgada**1.5)
    return float((n**2 / ((n - 1) * (n - 2))) * g_sesg)


def _psi_thom(beta: float) -> float:
    """IV-143: ψ(β) ≈ ln(β) - 1/(2β) - 1/(12β²)"""
    return float(np.log(beta) - 1.0 / (2.0 * beta) - 1.0 / (12.0 * beta**2))


def _params_from_x0(zi: np.ndarray, n: int):
    """IV-140, IV-141: β̂ y α̂ dados zi = xi - x0 > 0. Retorna (beta, alpha) o None."""
    S1 = float(np.sum(zi))
    S2 = float(np.sum(1.0 / zi))
    denom = 1.0 - n**2 / (S1 * S2)
    if abs(denom) < _DENOM_GUARD:
        return None
    beta = 1.0 / denom  # IV-140
    if beta <= 0.0:
        return None
    alpha = S1 / n - n / S2  # IV-141
    if alpha <= 0.0:
        return None
    return beta, alpha


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    n = len(serie)
    xbar = float(np.mean(serie))
    S = float(np.std(serie, ddof=1))
    if S == 0.0:
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    if metodo == "momentos":
        g = _skewness(serie)
        if abs(g) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta = 4.0 / g**2  # IV-137
        alpha = S / np.sqrt(beta)  # IV-138
        x0 = xbar - S * np.sqrt(beta)  # IV-139

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

        def _iv142(x0: float) -> float:
            zi = serie - x0
            if np.any(zi <= 0.0):
                return np.inf
            fit = _params_from_x0(zi, n)
            if fit is None:
                return np.inf
            beta_hat, alpha_hat = fit
            return float(
                np.sum(np.log(zi)) - n * np.log(alpha_hat) - n * _psi_thom(beta_hat)
            )  # IV-142

        lo = xi_min - 20.0 * S
        hi = xi_min - 1e-9

        _scan = np.linspace(lo, hi, 200)
        _vals = np.array([_iv142(float(x)) for x in _scan])
        _finite = np.isfinite(_vals)
        if not np.any(_finite):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        _signs = np.sign(_vals)
        _idx = np.where((_finite[:-1] & _finite[1:]) & (np.diff(_signs) != 0))[0]
        if len(_idx) == 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        x0_hat = None
        for _i in _idx:
            try:
                x0_hat = float(
                    brentq(
                        _iv142,
                        float(_scan[_i]),
                        float(_scan[_i + 1]),
                        xtol=CONVERGENCIA,
                    )
                )
                break
            except Exception:
                continue

        if x0_hat is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        zi = serie - x0_hat
        if np.any(zi <= 0.0):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )
        fit = _params_from_x0(zi, n)
        if fit is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )
        beta, alpha = fit

        return MetodoResult(
            metodo=metodo,
            parametros={"beta": beta, "alpha": alpha, "x0": x0_hat},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 + α̂·β̂·(1 - 1/(9·β̂) + UT·√(1/(9·β̂)))³    (IV-144)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"beta": float (forma), "alpha": float (escala), "x0": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    x0 = parametros["x0"]
    beta = parametros["beta"]
    alpha = parametros["alpha"]
    t = 1.0 / (9.0 * beta)
    wh = (1.0 - t + _ut(p) * np.sqrt(t)) ** 3
    return float(x0 + alpha * beta * wh)
