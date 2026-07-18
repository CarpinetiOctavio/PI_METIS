"""
Distribución Log-Normal 3 parámetros.

Parámetros: x0 (umbral), µy (media de ln(x-x0)), σy (desvío de ln(x-x0))
N_PARAMETROS = 3

Métodos aplicables: momentos, mv
Fuente: Tesis Facundo, Cap. IV — Ecuaciones IV-111 a IV-120

  Momentos: sistema IV-111 a IV-116
    n̂x = S/x̄                                   (IV-112)
    w = ((g²+4)^(1/2) - g) / 2               (IV-113)
    n̂z = (1 - w^(2/3)) / w^(1/3)             (IV-114)
    µ̂y = ln(S/n̂z) - (1/2)·ln(n̂z²+1)         (IV-115)
    σ̂y = [ln(n̂z²+1)]^(1/2)                   (IV-116)
    x̂0 = x̄·(1 - n̂x/n̂z)                       (IV-111)
    STATUS_NO_APLICABLE si w≤0, |n̂z|<ε, S/n̂z≤0, o x̂0≥min(xi)
  MV: perfil de verosimilitud sobre x0 (IV-117 a IV-119)
    Para x0 fijo: µ̂y = mean(ln(xi-x0)) (IV-117)
                  σ̂²y = mean((ln(xi-x0)-µ̂y)²) (IV-118)  [ddof=0, MV]
    x0 por minimización del perfil de verosimilitud negativo (IV-119)
    bounds: (min(xi) - 20·S, min(xi) - 1e-9)
    Guard de forma (DECISIÓN 025, docs/decisiones/decision025.md): ver
    _tiene_optimo_interior — rechaza el resultado de minimize_scalar si
    el escaneo no muestra un mínimo genuino en un punto interior.
    NOTA: puede No Converger — comportamiento esperado
  Cuantil:
    xT = x0 + exp(µ̂y + UT·σ̂y)               (IV-120)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo.
"""

import numpy as np
from scipy.optimize import minimize_scalar

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
PENDING_ZEROS_CONFIRMATION: bool = (
    True  # pendiente Facundo — ver core-etapa2-implementation.md
)

_DENOM_GUARD = 1e-10

# DECISIÓN 025 (docs/decisiones/decision025.md) — guard de ausencia de óptimo finito.
# A diferencia de DECISIÓN019 (logpearson3.py, detecta falsa convergencia
# EN un borde — el óptimo genuino existe cerca del borde) y de DECISIÓN023
# (gamma3p.py, detecta raíz espuria de un residuo por magnitud de S2), acá
# el problema es que la verosimilitud perfilada puede no tener mínimo
# finito en absoluto (diverge a -∞ acercándose a xi_min — verificado en
# est_09, n=7). minimize_scalar converge igual, en un punto donde la
# función todavía decrece sin haber encontrado un giro real — no es un
# óptimo, es donde Brent se detuvo por su tolerancia de convergencia.
#
# Se detecta con un escaneo grueso de _N_SCAN_OPTIMO puntos sobre
# (lo, hi): si el mínimo del escaneo cae exactamente en el primer o el
# último punto finito, la función no giró en ningún punto interior del
# dominio — no hay evidencia de óptimo genuino, se rechaza el resultado
# de minimize_scalar aunque haya "convergido" numéricamente.
#
# Verificado sin regresión contra est_01 a est_08 (las 8 estaciones donde
# lognormal3p/mv converge hoy) con densidades de escaneo 50/100/200/500/
# 1000 puntos — el mínimo siempre cae en un índice interior para las 8,
# nunca en el primero o el último. Para est_09 cae exactamente en el
# último en las 5 densidades probadas.
#
# Diseño descartado antes de este: un chequeo de margen porcentual fijo
# (2% de los puntos del escaneo desde cada borde) daba falsos positivos
# en 6 de las 8 estaciones buenas (est_01, est_02, est_03, est_04, est_05,
# est_06) — el mínimo genuino de esas series cae legítimamente muy cerca
# de `hi` (a veces en el penúltimo o antepenúltimo punto del escaneo), y
# un margen fijo las rechazaba de más. El criterio correcto no depende de
# cuán cerca del borde esté el mínimo, solo de si hay al menos un punto
# de recuperación (la función vuelve a subir) antes de llegar al borde
# mismo — de ahí el chequeo de "no está exactamente en el primer/último
# índice", sin margen porcentual.
_N_SCAN_OPTIMO = 200


def _tiene_optimo_interior(neg_profile_ll, lo: float, hi: float) -> bool:
    """True si el escaneo grueso de neg_profile_ll sobre (lo, hi) muestra
    un mínimo en un punto interior (no en el primer ni el último punto
    finito evaluado) — evidencia de que la función gira genuinamente en
    algún punto del dominio, no que decrece sin límite hasta un borde."""
    scan = np.linspace(lo, hi, _N_SCAN_OPTIMO)
    vals = np.array([neg_profile_ll(float(x)) for x in scan])
    finite_mask = np.isfinite(vals)
    if np.sum(finite_mask) < 3:
        return False
    vals_f = vals[finite_mask]
    argmin_local = int(np.argmin(vals_f))
    return argmin_local != 0 and argmin_local != len(vals_f) - 1


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

    if metodo == "momentos":
        xbar = float(np.mean(serie))
        S = float(np.std(serie, ddof=1))
        if S == 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        g = _skewness(serie)
        nx = S / xbar  # IV-112 — coeficiente de variación

        # IV-113
        w = ((g**2 + 4.0) ** 0.5 - g) / 2.0
        if w <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        # IV-114
        nz = (1.0 - w ** (2.0 / 3.0)) / w ** (1.0 / 3.0)
        if abs(nz) < _DENOM_GUARD:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        # IV-115: ln(S/nz) requiere S/nz > 0
        arg_log = S / nz
        if arg_log <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )
        mu_y = float(np.log(arg_log) - 0.5 * np.log(nz**2 + 1.0))  # IV-115

        # IV-116: tesis Facundo pág. 70 usa [ln(nz²+1)]^(1/2) directamente como σ̂y
        sigma_y = float(np.log(nz**2 + 1.0) ** 0.5)

        # IV-111
        x0 = float(xbar * (1.0 - nx / nz))

        # x0 debe ser menor que todos los xi para que ln(xi-x0) esté definido
        if x0 >= float(np.min(serie)):
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
            )

        return MetodoResult(
            metodo=metodo,
            parametros={"x0": x0, "mu_y": mu_y, "sigma_y": sigma_y},
            eea=None,
            status=STATUS_OK,
        )

    if metodo == "mv":
        S = float(np.std(serie, ddof=1))
        xi_min = float(np.min(serie))

        def _neg_profile_ll(x0: float) -> float:
            diff = serie - x0
            if np.any(diff <= 0.0):
                return np.inf
            zi = np.log(diff)
            mu_y = float(np.mean(zi))  # IV-117
            sigma2 = float(np.mean((zi - mu_y) ** 2))  # IV-118, ddof=0
            if sigma2 <= 0.0:
                return np.inf
            # perfil: n/2·ln(σ²) + sum(ln(xi-x0))  (∝ -LL)
            return float(n / 2.0 * np.log(sigma2) + np.sum(np.log(diff)))

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

        lo = xi_min - 20.0 * S
        hi = xi_min - 1e-9
        if not _tiene_optimo_interior(_neg_profile_ll, lo, hi):
            # DECISIÓN 025 — la verosimilitud perfilada no tiene mínimo
            # finito en este dominio; minimize_scalar "convergió" en un
            # punto sin haber encontrado un giro real.
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )

        x0 = float(result.x)
        diff = serie - x0
        zi = np.log(diff)
        mu_y = float(np.mean(zi))  # IV-117
        sigma2 = float(np.mean((zi - mu_y) ** 2))  # IV-118
        if sigma2 <= 0.0:
            return MetodoResult(
                metodo=metodo, parametros=None, eea=None, status=STATUS_NO_CONVERGE
            )
        sigma_y = float(np.sqrt(sigma2))

        return MetodoResult(
            metodo=metodo,
            parametros={"x0": x0, "mu_y": mu_y, "sigma_y": sigma_y},
            eea=None,
            status=STATUS_OK,
        )

    return MetodoResult(
        metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE
    )


def cuantil(p: float, parametros: dict) -> float:
    """
    xT = x0 + exp(µ̂y + UT·σ̂y)    (IV-120)

    p:          probabilidad de no excedencia F(x) ∈ (0, 1)
    parametros: {"x0": float, "mu_y": float, "sigma_y": float}
    """
    if not (0.0 < p < 1.0):
        raise ValueError(f"p debe estar en (0, 1), recibido: {p}")
    return float(
        parametros["x0"] + np.exp(parametros["mu_y"] + _ut(p) * parametros["sigma_y"])
    )
