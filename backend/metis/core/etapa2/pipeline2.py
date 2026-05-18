"""
Pipeline de Etapa 2 — ajuste exhaustivo de distribuciones.

Recorre las 13 distribuciones × sus métodos aplicables, calcula EEA
para cada ajuste exitoso, y retorna un Etapa2Result con el ranking
ordenado por EEA ascendente (menor EEA = mejor ajuste).

Casos especiales (no_converge, no_aplicable, disabled_zeros) nunca
detienen el pipeline — se registran y se continúa.
"""

import numpy as np

from metis.core.etapa2.distributions import DISABLED_WITH_ZEROS
from metis.core.etapa2.distributions import (
    exponencial_beta,
    exponencial_x0_beta,
    gamma2p,
    gamma3p,
    gen_exponencial,
    gen_pareto,
    gumbel,
    gve,
    logpearson3,
    lognormal2p,
    lognormal3p,
    normal,
    uniforme,
)
from metis.core.etapa2.eea import calcular_eea, es_high_eea
from metis.core.etapa2.empirical import probabilidades_weibull
from metis.core.etapa2.types import (
    STATUS_DISABLED_ZEROS,
    STATUS_OK,
    DistResult,
    Etapa2Result,
    MetodoResult,
)
from metis.core.types import WarningItem

_DISTRIBUCIONES = [
    ("uniforme", uniforme),
    ("normal", normal),
    ("gumbel", gumbel),
    ("gve", gve),
    ("lognormal2p", lognormal2p),
    ("lognormal3p", lognormal3p),
    ("logpearson3", logpearson3),
    ("gamma2p", gamma2p),
    ("gamma3p", gamma3p),
    ("exponencial_beta", exponencial_beta),
    ("exponencial_x0_beta", exponencial_x0_beta),
    ("gen_pareto", gen_pareto),
    ("gen_exponencial", gen_exponencial),
]


def ejecutar_etapa2(serie: np.ndarray, tiene_ceros: bool = False) -> Etapa2Result:
    """
    Ajusta todas las distribuciones sobre la serie y retorna el ranking por EEA.

    serie:       array de valores positivos ya validados por Etapa 1
    tiene_ceros: True si algún xi == 0 — deshabilita las distribuciones marcadas
    """
    serie_arr = np.asarray(serie, dtype=float)
    media = float(np.mean(serie_arr))
    _, _, probs_empiricas = probabilidades_weibull(serie_arr)

    ranking: list[DistResult] = []
    warnings: list[WarningItem] = []

    for nombre, modulo in _DISTRIBUCIONES:
        # Determinar si la distribución está deshabilitada por ceros
        deshabilitada = tiene_ceros and nombre in DISABLED_WITH_ZEROS

        metodos_resultado: list[MetodoResult] = []

        for metodo in modulo.METODOS_APLICABLES:
            if deshabilitada:
                metodos_resultado.append(
                    MetodoResult(
                        metodo=metodo,
                        parametros=None,
                        eea=None,
                        status=STATUS_DISABLED_ZEROS,
                    )
                )
                continue

            resultado = modulo.ajustar(serie_arr, metodo)

            if resultado.status == STATUS_OK and resultado.parametros is not None:
                try:
                    valores_estimados = np.array(
                        [
                            modulo.cuantil(float(p), resultado.parametros)
                            for p in probs_empiricas
                        ]
                    )
                    eea = calcular_eea(
                        np.sort(serie_arr), valores_estimados, modulo.N_PARAMETROS
                    )
                    resultado = MetodoResult(
                        metodo=metodo,
                        parametros=resultado.parametros,
                        eea=eea,
                        status=STATUS_OK,
                    )
                    if es_high_eea(eea, media):
                        warnings.append(
                            WarningItem(
                                codigo="DIST_HIGH_EEA",
                                nivel="normal",
                                descripcion=(
                                    f"{nombre}/{metodo}: EEA={eea:.4f} supera el 5% de la media"
                                ),
                            )
                        )
                except (NotImplementedError, Exception):
                    pass

            metodos_resultado.append(resultado)

        # EEA del mejor método — solo entre los STATUS_OK
        eeas_ok = [
            r.eea
            for r in metodos_resultado
            if r.status == STATUS_OK and r.eea is not None
        ]
        mejor_eea = min(eeas_ok) if eeas_ok else None
        mejor_metodo = None
        if mejor_eea is not None:
            for r in metodos_resultado:
                if r.status == STATUS_OK and r.eea == mejor_eea:
                    mejor_metodo = r.metodo
                    break

        ranking.append(
            DistResult(
                distribucion=nombre,
                n_parametros=modulo.N_PARAMETROS,
                metodos=metodos_resultado,
                mejor_eea=mejor_eea,
                mejor_metodo=mejor_metodo,
            )
        )

    # Ordenar: distribuciones con EEA primero (asc), luego las sin EEA al final
    ranking.sort(
        key=lambda d: (
            d.mejor_eea is None,
            d.mejor_eea if d.mejor_eea is not None else float("inf"),
            d.n_parametros,
        )
    )

    return Etapa2Result(ranking=ranking, warnings=warnings)
