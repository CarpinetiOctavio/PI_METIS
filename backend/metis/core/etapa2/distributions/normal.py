"""
Distribución Normal.

Parámetros: µ (media), σ (desvío estándar)
N_PARAMETROS = 2

Métodos aplicables: Momentos, MV, ML
NOTA: Momentos y MV producen los mismos estimadores (Tesis Facundo).
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-92 a IV-105

  Momentos y MV (coinciden):
    µ̂ = x̄                              (IV-92)
    σ̂² = sum(xi - x̄)² / (n-1)         (IV-93)
  ML (Momentos L):
    µ̂ = λ1                             (IV-94)
    σ̂ = 1.772·λ2                       (IV-95)
    λ1 = β0                             (IV-96)
    λ2 = 2·β1 - β0                     (IV-97)
    β0 = M(0) (IV-98),  β1 = M(1) (IV-99)
    M(0) = (1/n)·sum(xi)               (IV-100)
  Cuantil:
    xT = µ̂ + σ̂·UT                     (IV-101)
    UT por aproximación racional IV-102 a IV-105:
      Para F(x) ≤ 0.5: V = sqrt(ln(1/F²)), UT = -(V - num/den)  (IV-102, IV-103)
      Para F(x) > 0.5: usar 1-F(x) en V, UT = +(V - num/den)    (IV-105)
      Coeficientes: b0=2.515517, b1=0.802853, b2=0.010328,
                    b3=1.432788, b4=0.189269, b5=0.001308

Sin restricción por ceros.
"""

import numpy as np

from metis.core.etapa2.types import MetodoResult, STATUS_NO_APLICABLE, STATUS_OK
from metis.core.etapa2.utils import _ut

N_PARAMETROS: int = 2
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    n = len(serie)

    if metodo in ("momentos", "mv"):
        # µ̂ = x̄  (IV-92),  σ̂² = sum((xi-µ̂)²)/(n-1)  (IV-93)
        mu = float(np.mean(serie))
        sigma = float(np.std(serie, ddof=1))
        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "sigma": sigma},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "ml":
        xi = np.sort(serie)
        # β0 = M(0) = (1/n)·sum(xi)  (IV-98, IV-100)
        beta0 = float(np.mean(xi))
        # β1 = M(1) = (1/(n·(n-1)))·sum(i·xi) para i=0..n-1  (IV-99)
        # Fórmula explícita: Hosking (1990) — la tesis la referencia sin transcribirla
        beta1 = float(np.sum(xi * np.arange(n)) / (n * (n - 1)))
        # λ1 = β0  (IV-96),  λ2 = 2·β1 - β0  (IV-97)
        lambda2 = 2.0 * beta1 - beta0
        # µ̂ = λ1 = β0  (IV-94),  σ̂ = 1.772·λ2  (IV-95)
        mu = beta0
        sigma = 1.772 * lambda2
        if sigma <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        return MetodoResult(
            metodo=metodo,
            parametros={"mu": mu, "sigma": sigma},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = µ̂ + σ̂·UT  (IV-101)
    UT por aproximación racional IV-102 a IV-105.

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"mu": float, "sigma": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return parametros["mu"] + parametros["sigma"] * _ut(p)
