"""
Distribución General de Valores Extremos (GVE).

Parámetros: ν (posición), α (escala), β (forma)
N_PARAMETROS = 3

Métodos aplicables: momentos, mv, ml
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-202 a IV-245

  Momentos: IV-203 a IV-215
    g = asimetría no sesgada de la serie
    β̂ por polinomio según rango de g:
      IV-203: -11.35 < g < 1.1396
      IV-204:  1.14 ≤ g < 18.95
      (hueco real, fiel a la tesis: 1.1396 ≤ g ≤ 1.14 → STATUS_NO_APLICABLE)
    E[y] = Γ(1+β̂),  Var(y) = Γ(1+2β̂) - Γ²(1+β̂)     (IV-208/209)
    B̂ = sqrt(Var(x)/Var(y))                            (IV-206/207)
    Â = x̄ + B̂·E[y]                                     (IV-205)
    Si β̂ < 0: α̂ = -β̂·B̂, ν̂ = Â + B̂                   (IV-210/211)
    Si β̂ > 0: α̂ =  β̂·B̂, ν̂ = Â - B̂                   (IV-212/213)
    Si β̂ ≈ 0: α̂ = 0.78·S, ν̂ = x̄ - 0.45·S             (IV-214/215)
    STATUS_NO_APLICABLE si g fuera de (-11.35, 18.95) o Var(y)≤0 o α̂≤0
  MV: sistema iterativo IV-216 a IV-233
    Inicializar con estimadores de momentos
    yi = -(1/β̂)·ln(1 - (xi-ν̂)/(α̂·β̂))               (IV-202)
    P, Q, R por IV-216/217/218
    Polinomios a,b,c,f,gs,h en β̂ (IV-225–230)
    δν, δα, δβ por IV-222–224 — convergencia max(|δ|) < 1×10⁻⁷
    NOTA: frecuentemente No Converge — comportamiento esperado según tesis
  ML (Momentos-L): IV-234 a IV-244 — cerrado, sin iteración
    M0, M1, M2 por IV-242–244 (serie ordenada descendente — ver NOTA)
    E = (2M̂(1)-M̂(0))/(3M̂(2)-M̂(0)) - ln(2)/ln(3)    (IV-234)
    β̂ = 7.859·E + 2.9554·E²                             (IV-235)
    A = Γ(1+β̂), B = 1-2^(-β̂), C = (2M̂(1)-M̂(0))·β̂   (IV-236/237/238)
    D = (A-1)/β̂                                         (IV-239)
    α̂ = C/(A·B), ν̂ = M̂(0) + D·α̂                       (IV-240/241)
  Cuantil: IV-245
    xT = ν + (α/β)·{1 - [-ln F(x)]^β}
"""

import numpy as np
from scipy.special import gamma as _gamma

from metis.core.etapa2.types import (
    CONVERGENCIA,
    STATUS_NO_APLICABLE,
    STATUS_NO_CONVERGE,
    STATUS_OK,
    MetodoResult,
)

N_PARAMETROS: int = 3
METODOS_APLICABLES: tuple[str, ...] = ("momentos", "mv", "ml")

_MAX_ITER = 200_000
_DENOM_GUARD = 1e-10
_SMALL_BETA = 1e-9


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


def _momentos_L(x: np.ndarray) -> tuple[float, float, float]:
    """M̂(0), M̂(1), M̂(2) con x ordenado descendente (IV-242 a IV-244)."""
    xs = np.sort(x)[::-1]
    n = len(xs)
    M0 = float(np.mean(xs))  # IV-242
    # IV-243: (1/(n*(n-1))) * sum_{i=1}^{n-1} x_i*(n-i)  [1-indexed]
    j = np.arange(n - 1)
    M1 = float(np.dot(xs[: n - 1], n - 1 - j) / (n * (n - 1)))
    if n < 3:
        return M0, M1, 0.0
    # IV-244: (1/(n*(n-1)*(n-2))) * sum_{i=1}^{n-2} x_i*(n-i)*(n-i-1)  [1-indexed]
    k = np.arange(n - 2)
    M2 = float(np.dot(xs[: n - 2], (n - 1 - k) * (n - 2 - k)) / (n * (n - 1) * (n - 2)))
    return M0, M1, M2


def _beta_from_g(g: float) -> float | None:
    """β̂ por polinomio en g (IV-203/204). None si g fuera de rango."""
    if -11.35 < g < 1.1396:  # IV-203
        return (
            0.279434
            - 0.333535 * g
            + 0.048306 * g**2
            - 0.023314 * g**3
            + 0.00376 * g**4
            - 0.000263 * g**5
        )
    if 1.14 < g < 18.95:  # IV-204
        return (
            0.25031
            - 0.29219 * g
            + 0.075357 * g**2
            - 0.010883 * g**3
            + 0.000904 * g**4
            - 0.000043 * g**5
        )
    return None  # g fuera de (-11.35, 18.95)


def _nu_alpha_from_beta(serie: np.ndarray, beta: float) -> tuple[float, float] | None:
    """
    (ν̂, α̂) dado β̂ por IV-205 a IV-215.
    Devuelve None si Var(y) ≤ 0 o α̂ ≤ 0.
    """
    try:
        E_y = float(_gamma(1.0 + beta))  # IV-208
        Var_y = float(_gamma(1.0 + 2.0 * beta)) - E_y**2  # IV-209
    except (ValueError, OverflowError):
        return None
    if Var_y <= 0.0:
        return None
    S = float(np.std(serie, ddof=1))
    B_hat = float(np.sqrt(S**2 / Var_y))  # IV-206/207
    A_hat = float(np.mean(serie)) + B_hat * E_y  # IV-205
    if abs(beta) < _SMALL_BETA:  # Gumbel degenerado (IV-214/215)
        alpha = 0.78 * S
        nu = float(np.mean(serie)) - 0.45 * S
    elif beta < 0.0:
        alpha = -beta * B_hat  # IV-210
        nu = A_hat + B_hat  # IV-211
    else:
        alpha = beta * B_hat  # IV-212
        nu = A_hat - B_hat  # IV-213
    if alpha <= 0.0:
        return None
    return nu, alpha


def ajustar(serie: np.ndarray, metodo: str) -> MetodoResult:
    n = len(serie)

    if metodo == "momentos":
        g = _skewness(serie)
        beta = _beta_from_g(g)
        if beta is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        result = _nu_alpha_from_beta(serie, beta)
        if result is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        nu, alpha = result
        return MetodoResult(
            metodo=metodo,
            parametros={"nu": nu, "alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        # Condiciones iniciales: momentos, con fallback a ML si el guard falla.
        # ML está más cerca del óptimo MV cuando g es grande y nu_momentos >> max(xi).
        nu, alpha, beta = None, None, None

        g = _skewness(serie)
        beta0 = _beta_from_g(g)
        if beta0 is not None:
            init = _nu_alpha_from_beta(serie, beta0)
            if init is not None:
                nu0, alpha0 = init
                # Verificar que el guard de IV-202 pase con condiciones iniciales
                if not np.any(1.0 - beta0 * (serie - nu0) / alpha0 <= 0.0):
                    nu, alpha, beta = nu0, alpha0, beta0

        if nu is None:
            # Fallback: ML (Momentos-L) como condición inicial para MV
            M0, M1, M2 = _momentos_L(serie)
            denom_234 = 3.0 * M2 - M0
            if abs(denom_234) > _DENOM_GUARD:
                E = (2.0 * M1 - M0) / denom_234 - np.log(2.0) / np.log(3.0)
                b_ml = 7.859 * E + 2.9554 * E**2
                if abs(b_ml) > _DENOM_GUARD:
                    try:
                        A_ml = float(_gamma(1.0 + b_ml))
                        B_ml = 1.0 - 2.0 ** (-b_ml)
                        C_ml = (2.0 * M1 - M0) * b_ml
                        D_ml = (A_ml - 1.0) / b_ml
                        a_ml = C_ml / (A_ml * B_ml)
                        n_ml = M0 + D_ml * a_ml
                        if a_ml > 0.0 and not np.any(
                            1.0 - b_ml * (serie - n_ml) / a_ml <= 0.0
                        ):
                            nu, alpha, beta = n_ml, a_ml, b_ml
                    except (ValueError, OverflowError):
                        pass

        if nu is None:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        for _ in range(_MAX_ITER):
            if abs(alpha * beta) < _DENOM_GUARD:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
            # IV-202: variable reducida
            arg_log = 1.0 - beta * (serie - nu) / alpha
            if np.any(arg_log <= 0.0):
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
            yi = -(1.0 / beta) * np.log(arg_log)

            # IV-216 a IV-218
            exp_neg = np.exp(-yi)
            exp_bm1 = np.exp((beta - 1.0) * yi)
            exp_b = np.exp(beta * yi)
            if not (np.all(np.isfinite(exp_bm1)) and np.all(np.isfinite(exp_b))):
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
            P = float(n - np.sum(exp_neg))  # IV-216
            Q = float(np.sum(exp_bm1) - (1.0 - beta) * np.sum(exp_b))  # IV-217
            R = float(n - np.sum(yi) + np.sum(yi * exp_neg))  # IV-218

            if abs(beta) < _DENOM_GUARD:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )
            # Polinomios auxiliares IV-225 a IV-230
            b2, b3 = beta**2, beta**3
            a = 0.661437 - 0.562798 * beta + 0.985803 * b2 - 0.059011 * b3  # IV-225
            b = 1.235356 - 0.162161 * beta - 0.115137 * b2 + 0.009577 * b3  # IV-226
            c = 0.4711 - 0.77627 * beta + 0.295825 * b2 - 0.009645 * b3  # IV-227
            f = 0.244435 - 0.10287 * beta - 0.19583 * b2 - 0.016837 * b3  # IV-228
            gs = 0.15373 - 0.411923 * beta - 0.479209 * b2 - 0.075004 * b3  # IV-229
            h = 0.338937 - 1.209555 * beta - 0.109822 * b2 - 0.019801 * b3  # IV-230

            PQ_beta = (P + Q) / beta
            R_corr = R - PQ_beta

            # Incrementos IV-222 a IV-224
            d_nu = -(alpha / n) * (b * Q + h * PQ_beta + (f / beta) * R_corr)
            d_alpha = -(alpha / n) * (h * Q + a * PQ_beta + (gs / beta) * R_corr)
            d_beta = -(1.0 / n) * (f * Q + gs * PQ_beta + (c / beta) * R_corr)

            if max(abs(d_nu), abs(d_alpha), abs(d_beta)) < CONVERGENCIA:
                return MetodoResult(
                    metodo=metodo,
                    parametros={"nu": nu, "alpha": alpha, "beta": beta},
                    eea=None,
                    status=STATUS_OK,
                )
            nu += d_nu  # IV-231
            alpha += d_alpha  # IV-232
            beta += d_beta  # IV-233
            if alpha <= 0.0:
                return MetodoResult(
                    metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
                )

        return MetodoResult(
            metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
        )

    if metodo == "ml":
        M0, M1, M2 = _momentos_L(serie)  # serie desc. — IV-242/243/244

        denom_234 = 3.0 * M2 - M0
        if abs(denom_234) < 1e-10:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        E = (2.0 * M1 - M0) / denom_234 - np.log(2.0) / np.log(3.0)  # IV-234
        beta = 7.859 * E + 2.9554 * E**2  # IV-235

        if abs(beta) < 1e-10:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        from scipy.special import gamma as _gfn

        A = float(_gfn(1.0 + beta))  # IV-236
        B = 1.0 - 2.0 ** (-beta)  # IV-237
        C = (2.0 * M1 - M0) * beta  # IV-238
        D = (A - 1.0) / beta  # IV-239

        denom_AB = A * B
        if abs(denom_AB) < 1e-10:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        alpha = C / denom_AB  # IV-240
        nu = M0 + D * alpha  # IV-241

        if alpha <= 0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"nu": nu, "alpha": alpha, "beta": beta},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = ν + (α/β)·{1 - [-ln F(x)]^β}    (IV-245)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"nu": float, "alpha": float, "beta": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    nu = parametros["nu"]
    alpha = parametros["alpha"]
    beta = parametros["beta"]
    if abs(beta) < _SMALL_BETA:
        return float(nu - alpha * np.log(-np.log(p)))  # límite β→0: Gumbel (L'Hôpital)
    return float(nu + (alpha / beta) * (1.0 - (-np.log(p)) ** beta))
