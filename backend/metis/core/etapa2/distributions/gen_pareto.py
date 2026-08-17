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
    STATUS_NO_APLICABLE si µ̂ ≥ min(xi) — ver docs/auditoria/hallazgos/
    restricciones-dominio-etapa2.md (17/08/2026)

  MV: sistema IV-150 a IV-152
    µ̂ = min(xi) (fijo antes de resolver)
    IV-151 (∂L/∂ε = 0) y IV-152 (∂L/∂σ = 0) simultáneamente via fsolve
    Residual verificado post-fsolve (DECISIÓN 010)

  MC: sistema IV-153 a IV-166
    fi = (i-0.4)/(n+0.2)     (IV-165, Cunnane)
    zi = (1-fi)^ε             (IV-163)
    yi = ln(1-fi)             (IV-164)
    IV-153: condición de optimalidad en ε — sistema trascendental porque
      zi depende de ε. Resolver con scan+brentq sobre IV-153 completo.
    σ̂ = ε·(x̄-xz̄+x1·(z̄-1)) / (z̄2-z̄-z1·(z̄-1))   (IV-154)
    µ̂ = x1 - (ε/µ_k)·(1-z1)   (IV-155, punto fijo en µ — µ en denom es iteración anterior)
    Valor inicial ε y µ: g≥0 → 0.3, g<0 → 0.6          (IV-166)

  MPP: IV-167 a IV-173
    Pi = (i-0.35)/n                                      (IV-173)
    M̂(0) = (1/n)·sum(xi) = x̄                           (IV-172, k=0)
    M̂(1) = (1/n)·sum((1-Pi)·xi_ord)                    (IV-172, k=1)
    I1 = M̂(0) - x1   (x1 = mínimo)                     (IV-170)
    I2 = M̂(0) - 2·M̂(1)                                 (IV-171)
    ε̂ = (n·I1 + 2·I2·(n-1)) / (I2·(n-1) - I1)          (IV-167)
    σ̂ = (1+ε̂)·(2+ε̂)·I2                                 (IV-168)
    µ̂ = x1 - σ̂/(n+ε̂)                                   (IV-169)

  Cuantil: IV-174
    xT = ((1/(1-F(x)))^ε - 1)·(σ/ε) + µ
    Límite ε→0: xT = µ - σ·ln(1-F(x))    [L'Hôpital]

RESTRICCIÓN ante ceros: pregunta de dominio pendiente de confirmación de
Facundo — no de mecánica de cálculo. Ninguna fórmula de este módulo aplica
log(xi) sobre datos crudos (MC usa log(1-fi) con fi = posición de ploteo por
rango, no por valor; el resto no usa log en absoluto), así que un cero no
rompe el cálculo en ningún método — verificado en docs/auditoria/hallazgos/
restricciones-dominio-etapa2.md. DECISIÓN 060 estableció que, mientras se
espera esa confirmación, el default es calcular igual (con
DIST_ZEROS_TOLERATED emitido por pipeline_etapa2.py, no acá) en vez de
bloquear — esto resuelve el default de implementación, no la pregunta de
dominio, que sigue abierta en pendientes-facundo.md.
NOTA: MV y MC frecuentemente No Converge según resultados de la tesis.
"""

import numpy as np
from scipy.optimize import brentq, fsolve

from metis.core.etapa2.types import (
    CONVERGENCIA,
    STATUS_NO_APLICABLE,
    STATUS_NO_CONVERGE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "mc", "mpp")
PENDING_ZEROS_CONFIRMATION: bool = (
    True  # pregunta de dominio, no de cálculo — ver DECISIÓN 060
)

_DENOM_GUARD = 1e-10
_RESIDUAL_TOL = 1e-4


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

        def _eq_momentos(eps: float) -> float:
            # IV-148: g = 2·(1-ε)·√(1+2ε) / (1+3ε)
            denom = 1.0 + 3.0 * eps
            inner = 1.0 + 2.0 * eps
            if abs(denom) < _DENOM_GUARD or inner < 0:
                return 1e10
            return 2.0 * (1.0 - eps) * np.sqrt(inner) / denom - g

        try:
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

        # mu debe ser menor o igual a todos los xi para que el soporte de
        # IV-145/146 (x >= mu) se cumpla — mismo guard que gamma3p.py/
        # lognormal3p.py sobre x0. DECISIÓN 060 — ver docs/decisiones/
        # decision060.md y docs/auditoria/hallazgos/
        # restricciones-dominio-etapa2.md (17/08/2026): sin este guard, 3
        # de las 9 estaciones de la tesis producían mu >= min(serie) sin
        # marcarlo.
        if mu >= float(np.min(serie)):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

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
                np.sum(np.log(ti)) / eps**2
                + ((1.0 - eps) / eps) * np.sum((serie - mu) / (sigma * ti))
            )
            # IV-152: ∂L/∂σ = 0  (primer término +n/σ, no -n/σ)
            f2 = float(
                n / sigma
                + ((1.0 - eps) / eps) * (eps / sigma**2) * np.sum((serie - mu) / ti)
            )
            return [f1, f2]

        try:
            sol, info, ier, _ = fsolve(_system_mv, [0.1, S], full_output=True)
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        if ier != 1 or float(np.max(np.abs(info["fvec"]))) > _RESIDUAL_TOL:
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
        g = _skewness(serie)
        xi = np.sort(serie)  # ascendente: xi[0] = mínimo
        x1 = float(xi[0])
        i_idx = np.arange(1, n + 1, dtype=float)
        fi = (i_idx - 0.4) / (n + 0.2)  # IV-165, Cunnane
        yi = np.log(1.0 - fi)  # IV-164, constante en ε

        def _avgs(eps_val: float):
            zi = (1.0 - fi) ** eps_val  # IV-163: zi depende de ε
            z1 = float(zi[0])
            zbar = float(np.mean(zi))  # IV-157
            z2bar = float(np.mean(zi**2))  # IV-158
            xzbar = float(np.mean(xi * zi))  # IV-159
            zybar = float(np.mean(zi * yi))  # IV-160
            z2ybar = float(np.mean(zi**2 * yi))  # IV-161
            xyzbar = float(np.mean(xi * yi * zi))  # IV-162
            return z1, zbar, z2bar, xzbar, zybar, z2ybar, xyzbar

        def _iv153(eps_val: float) -> float:
            # IV-153: (x̄·zȳ - xyz̄)·(z̄2 - z̄²) = (xz̄ - x̄·z̄)·(z̄·zȳ - z2ȳ)
            # Sistema trascendental: zi=(1-fi)^ε entra en todos los promedios
            if abs(eps_val) < _DENOM_GUARD:
                return 1e10
            z1, zbar, z2bar, xzbar, zybar, z2ybar, xyzbar = _avgs(eps_val)
            lhs = (xbar * zybar - xyzbar) * (z2bar - zbar**2)
            rhs = (xzbar - xbar * zbar) * (zbar * zybar - z2ybar)
            return lhs - rhs

        # IV-166: valor inicial de ε y µ según asimetría
        eps_init = 0.3 if g >= 0.0 else 0.6
        mu_init = eps_init  # mismo valor inicial para µ

        # Scan + brentq sobre IV-153 completo (DECISIÓN 010)
        _scan = np.linspace(-0.49, 50.0, 300)
        _vals = np.array([_iv153(float(e)) for e in _scan])
        _finite = np.isfinite(_vals)
        _signs = np.where(_finite, np.sign(_vals), 0)
        _idx = np.where((_finite[:-1] & _finite[1:]) & (np.diff(_signs) != 0))[0]

        if len(_idx) == 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        # Puede haber múltiples raíces (incluidas espurias cerca de ε=0).
        # Iterar sobre todos los brackets hasta encontrar parámetros válidos.
        eps_hat = sigma_hat = mu_hat = None
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

            z1, zbar, z2bar, xzbar, zybar, z2ybar, xyzbar = _avgs(_eps)

            # IV-154: σ̂ = ε·(x̄-xz̄+x1·(z̄-1)) / (z̄2-z̄-z1·(z̄-1))
            denom_sigma = z2bar - zbar - z1 * (zbar - 1.0)
            if abs(denom_sigma) < _DENOM_GUARD:
                continue
            _sigma = _eps * (xbar - xzbar + x1 * (zbar - 1.0)) / denom_sigma
            if _sigma <= 0:
                continue

            # IV-155: µ̂ = x1 - (ε/µ_k)·(1-z1) — punto fijo en µ
            # µ en el denominador es el valor de la iteración anterior
            _mu = mu_init
            converged_mu = False
            for _ in range(1000):
                if abs(_mu) < _DENOM_GUARD:
                    break
                _mu_next = x1 - (_eps / _mu) * (1.0 - z1)
                if abs(_mu_next - _mu) < CONVERGENCIA:
                    _mu = _mu_next
                    converged_mu = True
                    break
                _mu = _mu_next
            if not converged_mu:
                continue

            eps_hat = _eps
            sigma_hat = _sigma
            mu_hat = _mu
            break

        if eps_hat is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu_hat, "sigma": sigma_hat, "epsilon": eps_hat},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mpp":
        xi = np.sort(serie)
        x1 = float(xi[0])
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
    xT = ((1/(1-F(x)))^ε - 1)·(σ/ε) + µ    (IV-174)
    Límite ε→0: xT = µ - σ·ln(1-F(x))       [L'Hôpital]

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu": float, "sigma": float, "epsilon": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    mu = parametros["mu"]
    sigma = parametros["sigma"]
    eps = parametros["epsilon"]
    if abs(eps) < _DENOM_GUARD:
        return float(mu - sigma * np.log(1.0 - p))  # límite ε→0
    return float(((1.0 / (1.0 - p)) ** eps - 1.0) * (sigma / eps) + mu)  # IV-174
