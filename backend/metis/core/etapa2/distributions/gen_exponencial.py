"""
Distribución Generalizada Exponencial.

Parámetros: α (forma), λ (escala)
N_PARAMETROS = 2

Métodos aplicables: momentos, mv, ml
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-77 a IV-89

  Momentos:
    α̂ por IV-77: S/x̄ = √(ψ'(1) - ψ'(α+1)) / (ψ(α+1) - ψ(1))
    ψ = digamma, ψ' = trigamma. Raíz cuadrada solo en numerador.
    λ̂ por IV-78: µ = (ψ(α+1) - ψ(1)) / λ  →  λ̂ = (ψ(α+1) - ψ(1)) / x̄

  MV: IV-79 a IV-82
    IV-80: n/α + Σln(1 - e^(-λ·xi)) = 0
    IV-81: n/λ + (α-1)·Σ xi·e^(-λ·xi)/(1-e^(-λ·xi)) - Σxi = 0
    α̂(λ) = -n / Σln(1 - e^(-λ·xi))    (IV-82)
    Resuelto vía fsolve sobre IV-80/IV-81. Residual verificado (DECISIÓN 010).

  ML (Momentos L): IV-83 a IV-88
    α̂ de: β2/β1 = (ψ(2α+1) - ψ(α+1)) / (ψ(α+1) - ψ(1))    (IV-83)
    λ̂ = (ψ(α̂+1) + ψ(1)) / β1                                 (IV-84)
    β1 = M1 (IV-85) = x̄
    β2 = M2 (IV-86/87) = [1/(n(n-1))]·Σ_{i=1}^{n-1}(n-i)·x_{(i)}  (descendente)

  Cuantil: IV-89
    xT = -ln[1 - F(x)^(1/α)] / λ

RESTRICCIÓN ante ceros: distinta por método, no uniforme.
  - Momentos: pregunta de dominio pendiente de Facundo, no de cálculo —
    IV-77/78 no aplican log(xi) crudo (digamma/trigamma de α, CV de la
    serie). Tolera cero — DECISIÓN 060.
  - MV: bloqueo por NECESIDAD MATEMÁTICA, no pendiente de dominio —
    log(1-e^(-λ·xi)) = log(1-e^0) = log(0), indefinido en x=0. Sigue
    devolviendo STATUS_DISABLED_ZEROS, sin cambios de DECISIÓN 060.
  - ML: mismo caso que Momentos — IV-83/84 no aplican log(xi) crudo. Tolera
    cero — DECISIÓN 060.
Ver docs/auditoria/hallazgos/restricciones-dominio-etapa2.md.
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
PENDING_ZEROS_CONFIRMATION: bool = (
    True  # solo Momentos/ML — MV bloquea por cálculo, ver DECISIÓN 060
)

_DENOM_GUARD = 1e-10
_RESIDUAL_TOL = 1e-4


def _momentos_l(serie: np.ndarray) -> tuple[float, float, float]:
    """
    Momentos de probabilidad pesada muestrales M̂(0), M̂(1), M̂(2)
    (β0, β1, β2 en la convención de Hosking, E[X·F(X)^r]).

    M̂(0) = (1/n)·Σ x_i                                            (media)
    M̂(1) = 1/(n(n-1))·Σ_{i=1}^{n-1} x_(i)·(n-i)                   IV-87
    M̂(2) = 1/(n(n-1)(n-2))·Σ_{i=1}^{n-2} x_(i)·(n-i)·(n-i-1)     IV-88
    con la serie ordenada de mayor a menor (x_(1) = máximo).

    TODO K-4.1 / DECISIÓN 022: consolidar con gve.py::_momentos_L —
    idéntica término a término (allá IV-243/244, misma estructura).
    """
    n = len(serie)
    xs = np.sort(serie)[::-1]
    m0 = float(np.mean(xs))
    j = np.arange(n - 1)
    m1 = float(np.dot(xs[: n - 1], n - 1 - j) / (n * (n - 1)))
    if n < 3:
        return m0, m1, 0.0
    k = np.arange(n - 2)
    m2 = float(np.dot(xs[: n - 2], (n - 1 - k) * (n - 2 - k)) / (n * (n - 1) * (n - 2)))
    return m0, m1, m2


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
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
        # IV-77: S/x̄ = √(ψ'(1) - ψ'(α+1)) / (ψ(α+1) - ψ(1))
        cv = S / xbar
        psi_1 = float(digamma(1.0))
        dpsi_1 = float(polygamma(1, 1.0))

        def _eq77(alpha: float) -> float:
            if alpha <= 0:
                return 1e10
            psi_a1 = float(digamma(alpha + 1.0))
            dpsi_a1 = float(polygamma(1, alpha + 1.0))
            num = dpsi_1 - dpsi_a1  # ψ'(1) - ψ'(α+1)
            den = psi_a1 - psi_1  # ψ(α+1) - ψ(1)
            if num <= 0 or abs(den) < _DENOM_GUARD:
                return 1e10
            return float(np.sqrt(num) / den) - cv

        try:
            alpha = float(brentq(_eq77, 1e-3, 1e6, xtol=CONVERGENCIA))
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        # IV-78: λ̂ = (ψ(α+1) - ψ(1)) / x̄
        psi_a1 = float(digamma(alpha + 1.0))
        den_lam = psi_a1 - psi_1
        if abs(den_lam) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        lam = den_lam / xbar
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
        if np.any(serie == 0):
            # log(1-e^(-λ·xi)) = log(1-e^0) = log(0), indefinido en x=0 —
            # a diferencia de Momentos/ML, acá el bloqueo es necesidad
            # matemática real, no una decisión de dominio pendiente.
            # Ver DECISIÓN 060, docs/auditoria/hallazgos/restricciones-dominio-etapa2.md.
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_DISABLED_ZEROS
            )

        # IV-80/IV-81 vía fsolve. Residual verificado (DECISIÓN 010).
        def _system(params: list) -> list:
            alpha, lam = params
            if alpha <= 0 or lam <= 0:
                return [1e10, 1e10]
            ev = np.exp(-lam * serie)
            one_ev = 1.0 - ev
            if np.any(one_ev <= 0):
                return [1e10, 1e10]
            log_t = np.log(one_ev)
            f1 = float(n / alpha + np.sum(log_t))  # IV-80
            f2 = float(
                n / lam + (alpha - 1.0) * np.sum(serie * ev / one_ev) - np.sum(serie)
            )  # IV-81
            return [f1, f2]

        try:
            sol, info, ier, _ = fsolve(_system, [1.0, 1.0 / xbar], full_output=True)
        except Exception:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        if ier != 1 or float(np.max(np.abs(info["fvec"]))) > _RESIDUAL_TOL:
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
        # Momentos-L. IV-83 tal como la imprime la tesis (p.67):
        #   α = β2/β1 = (ψ(2α+1) − ψ(α+1)) / (ψ(α+1) − ψ(1))
        # con β1 = M̂(1) (IV-87) y β2 = M̂(2) (IV-88) — los PWM de primer y
        # segundo orden, NO la media.
        #
        # DECISIÓN 069 — se corrige un desfasaje de índice de la implementación
        # anterior: usaba (media, M̂(1)) en el lugar de (M̂(1), M̂(2)), nunca
        # calculaba M̂(2), y resolvía la RHS ψ como ecuación. Verificado sobre
        # las 9 estaciones de la tesis (docs/auditoria/regresion/):
        #   · α̂ = M̂(2)/M̂(1) usado DIRECTO reproduce el α publicado con error
        #     <0.5% en 9/9 — la tesis usa la LHS de IV-83 como estimador, no
        #     resuelve la RHS.
        #   · resolver la RHS ψ como ecuación da un α (0.14–0.32) sin relación
        #     con la tesis (0.71–0.84) — se sospecha errata de transcripción en
        #     la RHS de IV-83, escalado a Facundo, no bloqueante.
        #   · λ̂ por IV-84 tal cual (ψ(1) = −γ) sobre el M̂(1) correcto
        #     reproduce el signo negativo de la tesis en 9/9.
        # Ver .claude/rules/core/formulas-etapa2.md §4.
        if n < 3:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        _, m1, m2 = _momentos_l(serie)
        if m1 <= _DENOM_GUARD or m2 <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        alpha = m2 / m1  # IV-83, LHS como estimador directo

        # IV-84: λ̂ = (ψ(α̂+1) + ψ(1)) / M̂(1)   [verbatim tesis; ψ(1) = −γ]
        lam = (float(digamma(alpha + 1.0)) + float(digamma(1.0))) / m1

        # DECISIÓN 069 — α̂ = M̂(2)/M̂(1) < 1 para toda muestra no degenerada
        # (el peso de x_(i) en M̂(2) relativo a M̂(1) es (i−2)/(n−2) ≤ 1), así
        # que el numerador de IV-84 es ψ(α̂+1) − γ ≤ ψ(2) − γ = −0.1544 < 0
        # SIEMPRE. Con λ̂ ≤ 0, F(x) = (1 − e^(−λx))^α no es real para x>0 (base
        # negativa) — distribución degenerada, sin cuantil válido. Criterio de
        # diseño de METIS (mismo que DECISIÓN 060): no se devuelve un ajuste
        # cuando la matemática de fondo no se sostiene. En la práctica el método
        # queda NO_APLICABLE para toda serie hidrológica real — la tesis reporta
        # λ<0 en sus 9 estaciones de referencia.
        if lam <= 0.0:
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

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"alpha": float, "lambda": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(-np.log(1.0 - p ** (1.0 / parametros["alpha"])) / parametros["lambda"])
