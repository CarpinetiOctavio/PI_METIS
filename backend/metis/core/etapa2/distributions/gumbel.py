"""
Distribución Gumbel (Valor Extremo Tipo I).

Parámetros: µ (posición), α (escala)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV, ML, ME
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-177 a IV-199

  Momentos:
    µ̂ = x̄ - 0.45·S    (IV-177)
    α̂ = 0.78·S         (IV-178)
  MV: sistema iterativo IV-179 a IV-187
    yi = (xi - µ̂) / α̂                              (IV-181)
    P  = n - sum(e^(-yi))             → 0 al converger  (IV-179)
    R  = n - sum(yi) + sum(yi·e^(-yi)) → 0 al converger  (IV-180)
    δµ = α̂j·(1.11·P - 0.26·R) / n                   (IV-184)
    δα = α̂j·(0.26·P - 0.61·R) / n                  (IV-185)
    µ̂j+1 = µ̂j + δµj                                (IV-186)
    α̂j+1 = α̂j + δαj                                (IV-187)
    Convergencia: max(|δµ|, |δα|) < 1×10⁻⁷
  ML (Momentos L):
    µ̂ = λ1 - γ·α̂      (IV-188),  γ = 0.577216 (Euler-Mascheroni)
    α̂ = λ2 / ln(2)     (IV-189)
  ME (Máxima Entropía): sistema iterativo IV-190 a IV-198
    P  = (1/n)·sum(yi)           (IV-190)
    R  = (1/n)·sum(e^(-yi))      (IV-191)
    yi = (xi - µ̂) / α̂           (IV-192)
    δα = 0.4228 + P + ln(R)      (IV-195)  ← factor multiplicativo
    δµ = P - γ·δα                (IV-196)  ← factor aditivo (escalado por α̂)
    Convergencia: |δα-1| < 1×10⁻⁷, |δµ| < 1×10⁻⁷  (equivalente IV-193, IV-194)
    µ̂j+1 = µ̂j + α̂j·δµj          (IV-197)
    α̂j+1 = α̂j·δαj               (IV-198)
  Cuantil:
    xT = µ̂ - α̂·ln{-ln[F(x)]}   (IV-199)

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import (
    CONVERGENCIA,
    STATUS_NO_APLICABLE,
    STATUS_NO_CONVERGE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml", "me")

_EULER = 0.577216  # constante de Euler-Mascheroni — IV-188, IV-193, IV-196
_MAX_ITER = 200


def _momentos_params(serie: np.ndarray) -> tuple[float, float]:
    """µ̂ y α̂ por momentos — IV-177, IV-178. Usado como punto de partida iterativo."""
    s = float(np.std(serie, ddof=1))
    return float(np.mean(serie)) - 0.45 * s, 0.78 * s


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    n = len(serie)

    if metodo == "momentos":
        mu, alpha = _momentos_params(serie)
        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "alpha": alpha},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "ml":
        # β0, β1 — Hosking (1990), tesis referencia sin transcribir fórmula de β1
        xi = np.sort(serie)
        beta0 = float(np.mean(xi))
        beta1 = float(np.sum(xi * np.arange(n)) / (n * (n - 1)))  # IV-99
        lambda2 = 2.0 * beta1 - beta0  # IV-97
        alpha = lambda2 / np.log(2.0)  # IV-189
        if alpha <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        mu = beta0 - _EULER * alpha  # IV-188
        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "alpha": alpha},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        mu, alpha = _momentos_params(serie)
        for _ in range(_MAX_ITER):
            yi = (serie - mu) / alpha  # IV-181
            P = float(n - np.sum(np.exp(-yi)))  # IV-179
            R = float(n - np.sum(yi) + np.sum(yi * np.exp(-yi)))  # IV-180
            delta_mu = alpha * (1.11 * P - 0.26 * R) / n  # IV-184
            delta_alpha = alpha * (0.26 * P - 0.61 * R) / n  # IV-185
            if max(abs(delta_mu), abs(delta_alpha)) < CONVERGENCIA:
                return MetodoResult(
                    metodo=metodo,
                    parametros={"mu": mu, "alpha": alpha},
                    eea=None,
                    status=STATUS_OK,
                )
            mu += delta_mu  # IV-186
            alpha += delta_alpha  # IV-187
            if alpha <= 0:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
        )

    if metodo == "me":
        mu, alpha = _momentos_params(serie)
        for _ in range(_MAX_ITER):
            yi = (serie - mu) / alpha  # IV-192
            P = float(np.mean(yi))  # IV-190
            R = float(np.mean(np.exp(-yi)))  # IV-191
            if R <= 0:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
            delta_alpha = 0.4228 + P + np.log(R)  # IV-195
            delta_mu = P - _EULER * delta_alpha  # IV-196
            if (
                abs(delta_mu) < CONVERGENCIA and abs(delta_alpha - 1.0) < CONVERGENCIA
            ):  # IV-193, IV-194
                return MetodoResult(
                    metodo=metodo,
                    parametros={"mu": mu, "alpha": alpha},
                    eea=None,
                    status=STATUS_OK,
                )
            mu = mu + alpha * delta_mu  # IV-197
            alpha = alpha * delta_alpha  # IV-198
            if alpha <= 0:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = µ̂ - α̂·ln{-ln[F(x)]}  (IV-199)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu": float, "alpha": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return parametros["mu"] - parametros["alpha"] * np.log(-np.log(p))
