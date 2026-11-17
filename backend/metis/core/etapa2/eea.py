import numpy as np


def calcular_eea(
    observados: np.ndarray,
    estimados: np.ndarray,
    n_parametros: int,
) -> float:
    """
    EEA = sqrt( sum(QT_obs - QT_est)² / (n - mp) )
    Fuente: Tesis Facundo, Ecuación IV-263

    observados:   cuantiles observados (serie ordenada ASC)
    estimados:    cuantiles teóricos a las mismas probabilidades empíricas
    n_parametros: mp — número de parámetros de la distribución ajustada

    Retorna inf si n <= n_parametros (denominador inválido).
    """
    n = len(observados)
    if n <= n_parametros:
        return float("inf")
    return float(np.sqrt(np.sum((observados - estimados) ** 2) / (n - n_parametros)))


def es_high_eea(eea: float, media: float) -> bool:
    """
    EEA > 5% de la media → warning DIST_HIGH_EEA.

    Umbral del 5% es una decisión de diseño de METIS — no proviene
    de la tesis de Facundo. El usuario experto del dominio interpreta
    el EEA y toma la decisión final sobre el ajuste.
    """
    return eea > 0.05 * abs(media)
