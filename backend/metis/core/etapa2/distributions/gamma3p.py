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


# DECISIÓN 023 (docs/decisiones/decision023.md) — cota de plausibilidad sobre S2=Σ(1/zi).
# Cuando x0 se acerca al mínimo observado, el zi más chico tiende a 0 y S2
# diverge — es una singularidad de borde de la verosimilitud perfilada
# (mismo tipo de patología que LN3p, DECISIÓN020), no una raíz genuina de
# IV-142. Verificado en est_04: raíz genuina S2/n≈0.20, raíz espuria de
# borde S2/n≈9.40 — casi 46x más grande. K_S2_MAX=2.0 deja margen amplio
# a ambos lados de esos dos valores concretos (10x por debajo de la
# genuina, 4.7x por encima de la espuria). No es un margen fijo tipo
# "últimos N puntos del borde" (eso no generaliza entre distribuciones,
# ver DECISIÓN 023) — es una cota sobre la magnitud de S2 en sí, que
# depende de la serie a través de n, no de una distancia fija a x0.
_K_S2_MAX = 2.0


def _validar_raiz(x0: float, serie: np.ndarray, n: int):
    """Valida un candidato a raíz de IV-142 más allá de β>0/α>0.

    Retorna (beta, alpha) si el candidato es plausible, None si no.
    """
    zi = serie - x0
    if np.any(zi <= 0.0):
        return None
    S2 = float(np.sum(1.0 / zi))
    if S2 > _K_S2_MAX * n:
        return None  # candidato pegado al borde — singularidad, no raíz genuina
    return _params_from_x0(zi, n)


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

        # DECISIÓN 023 — escaneo denso concentrado hacia el extremo superior
        # (hi = xi_min), en vez de uniforme sobre todo el dominio (~394
        # unidades en est_04). Verificado en est_04: la raíz genuina de
        # IV-142 y la singularidad de borde (S2 diverge cuando x0 → min(serie))
        # conviven en una ventana de ancho ~0.3 unidades pegada a hi — el
        # escaneo uniforme de 200 puntos (paso ~2 unidades sobre ~394) no
        # genera ningún bracket ahí porque el paso es ~7x más ancho que la
        # ventana entera. Se mantiene un escaneo grueso de cobertura sobre
        # todo el dominio (por si existiera una raíz lejos del borde en otra
        # serie) y se agrega un escaneo geométrico de distancias-a-hi, que
        # concentra la densidad exactamente donde hace falta sin fuerza
        # bruta pareja sobre las ~394 unidades.
        _ancho = hi - lo
        _scan_grueso = np.linspace(lo, hi, 200)
        _offsets_cerca_hi = np.geomspace(1e-6, 0.05 * _ancho, 400)
        _scan_fino = hi - _offsets_cerca_hi
        _scan = np.unique(np.concatenate([_scan_grueso, _scan_fino]))
        _scan = _scan[(_scan >= lo) & (_scan <= hi)]
        _scan.sort()

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

        # DECISIÓN 023 — no tomar el primer bracket sin validar (eso es lo
        # que hacía frágil la versión anterior: con más de un bracket, podía
        # quedarse con la raíz espuria de borde si aparecía primero en el
        # orden de escaneo). Se refinan TODOS los brackets encontrados y se
        # valida cada candidato (β>0, α>0 vía _params_from_x0, más la cota
        # de plausibilidad sobre S2) antes de aceptar ninguno.
        fit = None
        x0_hat = None
        for _i in _idx:
            try:
                _candidato = float(
                    brentq(
                        _iv142,
                        float(_scan[_i]),
                        float(_scan[_i + 1]),
                        xtol=CONVERGENCIA,
                    )
                )
            except Exception:
                continue
            _fit_candidato = _validar_raiz(_candidato, serie, n)
            if _fit_candidato is not None:
                x0_hat = _candidato
                fit = _fit_candidato
                break

        if fit is None or x0_hat is None:
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
