"""
Distribución Log-Pearson III.

Trabaja sobre yi = ln(xi). Parámetros: β (forma), α (escala), y0 (posición)
N_PARAMETROS = 3

Métodos aplicables: momentos_directo, momentos_indirecto, MV
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-247 a IV-260

  Momentos Método Indirecto: IV-255, IV-256  ← preferido en la práctica (tesis)
    yi = ln(xi),  gy = asimetría no sesgada de yi,  Sy = std(yi, ddof=1)
    β̂ = 4 / gy²                          (IV-255)
    α̂ = Sy / β̂                            (IV-256)
    ŷ0 = ȳ - α̂·β̂    (derivado de E[yi] = y0 + α̂·β̂)
  Momentos Método Directo: IV-247 a IV-254
    µr = (1/n)·sum(xi^r),  r = 1, 2, 3   (IV-248)
    B  = (3·ln µ1 - ln µ3) / (2·ln µ1 - ln µ2)    (IV-249)
    C  = 1/(B-3)                                    (IV-250)
    Si 3 < B ≤ 3.5: A = -0.45157 + 1.99955·C      (IV-252)
    Si 3.5 < B ≤ 6: A = -0.23019 + 1.65262·C + 0.20911·C² - 0.04557·C³  (IV-251)
    α̂ = 1/(A+3)                                    (IV-247)
    β̂ = (ln µ2 - 2·ln µ1) / (2·ln(1-α̂) - ln(1-2·α̂))  (IV-253)
    ŷ0 = ln(µ1) + β̂·ln(1 - α̂)                    (IV-254)
    STATUS_NO_APLICABLE si B ∉ (3,6], α̂ ≥ 1 (IV-254 indefinido), o
    arg de cualquier log ≤ 0, o |denom de β̂| < _DENOM_GUARD.
  MV: perfil de verosimilitud sobre y0 — scipy.optimize (IV-257 a IV-259)
    NOTA: frecuentemente No Converge — comportamiento esperado según tesis
  Cuantil:
    xT = exp( Y0 + β·α·(1 - 1/(9·β) + UT·sqrt(1/(9·β)))³ )  (IV-260)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0. Confirmado con Facundo.
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
METODOS_APLICABLES: tuple[str, ...] = ("momentos_directo", "momentos_indirecto", "mv")
DISABLED_WITH_ZEROS: bool = True  # confirmado — no aplicable si algún xi ≤ 0

_DENOM_GUARD = 1e-10


def _skewness(yi: np.ndarray) -> float:
    # IV-4: g_sesg = mean((yi-ybar)³) / (var_sesgada)^(3/2)
    # IV-5: g_insesg = n²/((n-1)(n-2)) * g_sesg
    n = len(yi)
    if n < 3:
        return 0.0
    ybar = float(np.mean(yi))
    var_sesgada = float(np.var(yi, ddof=0))
    if var_sesgada == 0.0:
        return 0.0
    g_sesg = float(np.mean((yi - ybar) ** 3) / var_sesgada**1.5)
    return float((n**2 / ((n - 1) * (n - 2))) * g_sesg)


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    if np.any(serie <= 0):
        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
        )

    yi = np.log(serie)

    if metodo == "momentos_indirecto":
        gy = _skewness(yi)
        if abs(gy) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        sy = float(np.std(yi, ddof=1))
        beta = 4.0 / gy**2  # IV-255
        alpha = sy / np.sqrt(beta)  # IV-256: α̂ = Sy/√β̂
        y0 = float(np.mean(yi)) - alpha * beta
        return MetodoResult(
            metodo=metodo,
            parametros={"beta": beta, "alpha": alpha, "y0": y0},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "momentos_directo":
        mu1 = float(np.mean(serie))  # IV-248, r=1
        mu2 = float(np.mean(serie**2))  # IV-248, r=2
        mu3 = float(np.mean(serie**3))  # IV-248, r=3

        denom_B = 2.0 * np.log(mu1) - np.log(mu2)  # IV-249 denominador
        if abs(denom_B) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        B = (3.0 * np.log(mu1) - np.log(mu3)) / denom_B  # IV-249
        if B <= 3.0 or B > 6.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        C = 1.0 / (B - 3.0)  # IV-250
        if B <= 3.5:
            A = -0.45157 + 1.99955 * C  # IV-252
        else:
            A = -0.23019 + 1.65262 * C + 0.20911 * C**2 - 0.04557 * C**3  # IV-251

        alpha_hat = 1.0 / (A + 3.0)  # IV-247: α̂ = 1/(A+3)

        # IV-254 requiere ln(1-α̂) → α̂ < 1. Guard explícito antes de calcular
        # IV-253 (ln(µ1·(α̂-1)) → -∞ cuando α̂ → 1 puede causar overflow).
        if alpha_hat >= 1.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        # IV-253: denominador = ln(1-α̂)² - ln(1-2·α̂) = 2·ln(1-α̂) - ln(1-2·α̂)
        # Requiere α̂ < 0.5 para que 1-2·α̂ > 0 (α̂ < 1 ya está guardado arriba)
        if alpha_hat >= 0.5:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        denom_beta = 2.0 * np.log(1.0 - alpha_hat) - np.log(
            1.0 - 2.0 * alpha_hat
        )  # IV-253 denominador
        if abs(denom_beta) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        beta_hat = (np.log(mu2) - 2.0 * np.log(mu1)) / denom_beta  # IV-253
        y0 = float(np.log(mu1) + beta_hat * np.log(1.0 - alpha_hat))  # IV-254

        return MetodoResult(
            metodo=metodo,
            parametros={"beta": beta_hat, "alpha": alpha_hat, "y0": y0},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        # IV-257 a IV-259 — perfil de verosimilitud sobre y0 (scipy.optimize)
        # Para y0 fijo: β̂(y0) por IV-126 (aprox. Gamma MV), α̂ = mean(zi)/β̂
        gy = _skewness(yi)
        if abs(gy) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )
        sy = float(np.std(yi, ddof=1))
        n = len(yi)
        yi_min = float(np.min(yi))
        sigma_y = float(sy)

        def _neg_loglik(y0: float) -> float:
            zi = yi - y0
            if np.any(zi <= 0.0):
                return np.inf
            mean_z = float(np.mean(zi))
            if mean_z <= 0.0:
                return np.inf
            C = float(np.log(mean_z) - np.mean(np.log(zi)))
            if C <= 0.0:
                return np.inf
            beta = (1.0 + np.sqrt(1.0 + 4.0 * C / 3.0)) / (4.0 * C)  # IV-126
            alpha = mean_z / beta
            if alpha <= 0.0 or beta <= 0.0:
                return np.inf
            return float(
                -(
                    (beta - 1.0) * np.sum(np.log(zi))
                    - np.sum(zi) / alpha
                    - n * beta * np.log(alpha)
                    - n * gammaln(beta)
                )
            )

        try:
            result = minimize_scalar(
                _neg_loglik,
                bounds=(yi_min - 20.0 * sigma_y, yi_min - 1e-9),
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

        lower_bound = yi_min - 20.0 * sigma_y
        upper_bound = yi_min - 1e-9
        # Brent (xatol=1e-7) termina a < 1e-7 del borde cuando la función
        # es monótona — nunca llega a 1e-4 con mínimo interior real.
        # Si result.x está a < 1e-4 de CUALQUIERA de los dos bordes, no hay
        # mínimo interior genuino: NO_CONVERGE. Guard simétrico — antes solo
        # protegía el borde inferior, lo que dejaba pasar como "convergencia"
        # casos de borde superior disfrazados (causa de la divergencia con
        # la tesis en est_05, donde la tesis reporta NO_CONVERGE).
        if (
            abs(result.x - lower_bound) < 1e-4
            or abs(upper_bound - result.x) < 1e-4
        ):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        y0 = float(result.x)
        zi = yi - y0
        mean_z = float(np.mean(zi))
        C = float(np.log(mean_z) - np.mean(np.log(zi)))
        if C <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )
        beta = (1.0 + np.sqrt(1.0 + 4.0 * C / 3.0)) / (4.0 * C)
        alpha = mean_z / beta
        return MetodoResult(
            metodo=metodo,
            parametros={"beta": beta, "alpha": alpha, "y0": y0},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = exp( Y0 + β·α·(1 - 1/(9·β) + UT·sqrt(1/(9·β)))³ )  (IV-260)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"beta": float, "alpha": float, "y0": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    beta = parametros["beta"]
    alpha = parametros["alpha"]
    y0 = parametros["y0"]
    t = 1.0 / (9.0 * beta)
    wh = (1.0 - t + _ut(p) * np.sqrt(t)) ** 3
    return float(np.exp(y0 + beta * alpha * wh))
