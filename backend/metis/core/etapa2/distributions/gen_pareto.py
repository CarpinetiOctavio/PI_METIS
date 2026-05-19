"""
Distribución Generalizada de Pareto.

Parámetros: µ (posición), σ (escala), ε (forma)
N_PARAMETROS = 3

Métodos aplicables: momentos, mv, mc, mpp
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-147 a IV-174

  Momentos: sistema IV-147 a IV-149
    g = 2·(1-ε)·(1+2ε)^(1/2) / (1+3ε)    (IV-148) → brentq para ε
    σ̂ = S·(1+ε)·√(1+2ε)                   [IV-149 despejado]
    µ̂ = x̄ - σ̂/(1+ε)                       [IV-147 despejado]

  MV: sistema IV-150 a IV-152
    µ̂ = min(xi) (fijo antes de resolver)
    IV-151 (∂L/∂ε = 0) y IV-152 (∂L/∂σ = 0) simultáneamente via fsolve

  MC: sistema IV-153 a IV-165
    fi = (i-0.4)/(n+0.2)    (IV-165, Cunnane)
    zi = (1-fi)^ε            (IV-163)
    yi = ln(1-fi)            (IV-164)
    IV-153: condición de optimalidad en ε del sistema LS —
      (x̄·zȳ - xyz̄)·(z̄2 - z̄²) = (xz̄ - x̄·z̄)·(z̄·zȳ - z2ȳ)
    σ̂ = -B̂·ε   donde B̂ = (xz̄ - x̄·z̄)/(z̄2 - z̄²)    (IV-154)
    µ̂ = x̄ + B̂·(1 - z̄)                                  (IV-155)
    Valor inicial de ε: g≥0 → 0.3, g<0 → 0.6            (IV-166)

  MPP: IV-167 a IV-173
    Pi = (i-0.35)/n                                       (IV-173)
    M̂(0) = (1/n)·sum(xi) = x̄                            (IV-172, k=0)
    M̂(1) = (1/n)·sum((1-Pi)·xi_ord)                     (IV-172, k=1)
    I1 = M̂(0) - x1   (x1 = mínimo)                      (IV-170)
    I2 = M̂(0) - 2·M̂(1)                                  (IV-171)
    ε̂ = (n·I1 + 2·I2·(n-1)) / (I2·(n-1) - I1)           (IV-167)
    σ̂ = (1+ε̂)·(2+ε̂)·I2                                  (IV-168)
    µ̂ = x1 - σ̂/(n+ε̂)                                    (IV-169)

  Cuantil:
    xT = µ + (σ/ε)·[1 - (1-F(x))^ε]    (IV-174)
    Límite ε→0: xT = µ - σ·ln(1-F(x))  [L'Hopital]

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
NOTA: frecuentemente No Converge según resultados de la tesis.
"""

import numpy as np
from scipy.optimize import brentq, fsolve

from metis.core.etapa2.types import (
    CONVERGENCIA,
    STATUS_DISABLED_ZEROS,
    STATUS_NO_APLICABLE,
    STATUS_NO_CONVERGE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "mc", "mpp")
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


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if np.any(serie == 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_DISABLED_ZEROS
        )

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

        def _eq_momentos(eps: float) -> float:
            # IV-148: g = 2(1-ε)·√(1+2ε) / (1+3ε)
            denom = 1.0 + 3.0 * eps
            inner = 1.0 + 2.0 * eps
            if abs(denom) < _DENOM_GUARD or inner < 0:
                return 1e10
            return 2.0 * (1.0 - eps) * np.sqrt(inner) / denom - g

        try:
            # g es monótona decreciente en (-1/3, +∞): +∞ en el extremo inferior, -∞ en el superior
            eps = float(brentq(_eq_momentos, -1.0 / 3.0 + 1e-9, 1e6, xtol=CONVERGENCIA))
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        sigma = S * (1.0 + eps) * np.sqrt(1.0 + 2.0 * eps)  # IV-149 despejado
        if sigma <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        mu = xbar - sigma / (1.0 + eps)  # IV-147 despejado

        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "sigma": sigma, "epsilon": eps},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        mu = float(np.min(serie))  # µ̂ = mínimo de la muestra (fijo)

        def _system_mv(params: list) -> list:
            eps, sigma = params
            if sigma <= 0 or abs(eps) < _DENOM_GUARD:
                return [1e10, 1e10]
            ti = 1.0 - (serie - mu) * eps / sigma
            if np.any(ti <= 0):
                return [1e10, 1e10]
            # IV-151: ∂L/∂ε = 0
            f1 = float(
                np.sum(
                    (1.0 / eps**2) * np.log(ti)
                    - (1.0 / eps + 1.0) * (serie - mu) / (sigma * ti)
                )
            )
            # IV-152: ∂L/∂σ = 0
            f2 = float(
                -n / sigma
                + (1.0 / eps + 1.0) * (eps / sigma) * np.sum((serie - mu) / ti)
            )
            return [f1, f2]

        try:
            sol, _, ier, _ = fsolve(_system_mv, [0.1, S], full_output=True)
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        if ier != 1:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        eps, sigma = float(sol[0]), float(sol[1])
        if sigma <= 0 or abs(eps) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "sigma": sigma, "epsilon": eps},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mc":
        xi = np.sort(serie)
        i_idx = np.arange(1, n + 1, dtype=float)
        fi = (i_idx - 0.4) / (n + 0.2)  # IV-165 — Cunnane
        yi = np.log(1.0 - fi)  # IV-164 — constante en ε

        def _avgs(eps: float):
            zi = (1.0 - fi) ** eps  # IV-163
            zbar = float(np.mean(zi))
            z2bar = float(np.mean(zi**2))
            xzbar = float(np.mean(xi * zi))
            zybar = float(np.mean(zi * yi))
            z2ybar = float(np.mean(zi**2 * yi))
            xyzbar = float(np.mean(xi * yi * zi))
            return zbar, z2bar, xzbar, zybar, z2ybar, xyzbar

        def _iv153(eps: float) -> float:
            # IV-153: (x̄·zȳ - xyz̄)·(z̄2 - z̄²) = (xz̄ - x̄·z̄)·(z̄·zȳ - z2ȳ)
            if abs(eps) < _DENOM_GUARD:
                return 1e10
            zbar, z2bar, xzbar, zybar, z2ybar, xyzbar = _avgs(eps)
            lhs = (xbar * zybar - xyzbar) * (z2bar - zbar**2)
            rhs = (xzbar - xbar * zbar) * (zbar * zybar - z2ybar)
            return lhs - rhs

        # Rango de búsqueda: ε > -0.5 es límite teórico de GPD.
        # Límite superior 50.0 es conservador — la tesis no define
        # restricción explícita en el valor máximo de ε.
        _scan = np.linspace(-0.49, 50.0, 300)
        _vals = np.array([_iv153(float(e)) for e in _scan])
        _signs = np.sign(_vals)
        _idx = np.where(np.diff(_signs) != 0)[0]
        if len(_idx) == 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        # Puede haber múltiples raíces (incluso espurias cerca de ε=0).
        # Iterar sobre todos los brackets hasta encontrar parámetros válidos.
        eps = mu = sigma = None
        for _i in _idx:
            try:
                _eps = float(
                    brentq(
                        _iv153,
                        float(_scan[_i]),
                        float(_scan[_i + 1]),
                        xtol=CONVERGENCIA,
                    )
                )
            except Exception:
                continue
            if abs(_eps) < _DENOM_GUARD:
                continue
            _zbar, _z2bar, _xzbar, _zybar, _z2ybar, _xyzbar = _avgs(_eps)
            _denom_b = _z2bar - _zbar**2
            if abs(_denom_b) < _DENOM_GUARD:
                continue
            _B_hat = (_xzbar - xbar * _zbar) / _denom_b
            _sigma = -_B_hat * _eps  # IV-154
            _mu = xbar + _B_hat * (1.0 - _zbar)  # IV-155
            if _sigma <= 0:
                continue
            eps, sigma, mu = _eps, _sigma, _mu
            break

        if eps is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "sigma": sigma, "epsilon": eps},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mpp":
        xi = np.sort(serie)
        x1 = float(xi[0])  # mínimo de la serie
        Pi = (np.arange(1, n + 1, dtype=float) - 0.35) / n  # IV-173

        M0 = xbar  # IV-172 k=0: (1/n)·Σxi = x̄
        M1 = float(np.mean((1.0 - Pi) * xi))  # IV-172 k=1

        I1 = M0 - x1  # IV-170
        I2 = M0 - 2.0 * M1  # IV-171

        denom_eps = I2 * (n - 1) - I1  # denominador IV-167
        if abs(denom_eps) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        eps = (n * I1 + 2.0 * I2 * (n - 1)) / denom_eps  # IV-167
        sigma = (1.0 + eps) * (2.0 + eps) * I2  # IV-168

        if sigma <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        denom_mu = n + eps
        if abs(denom_mu) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        mu = x1 - sigma / denom_mu  # IV-169

        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "sigma": sigma, "epsilon": eps},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = µ + (σ/ε)·[1 - (1-F(x))^ε]    (IV-174)
    Límite ε→0: xT = µ - σ·ln(1-F(x))   [L'Hopital]

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)  ← REQUERIDO
    parametros: {"mu": float, "sigma": float, "epsilon": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    mu = parametros["mu"]
    sigma = parametros["sigma"]
    eps = parametros["epsilon"]
    if abs(eps) < _DENOM_GUARD:
        return float(mu - sigma * np.log(1.0 - p))  # límite ε→0
    return float(mu + (sigma / eps) * (1.0 - (1.0 - p) ** eps))  # IV-174
