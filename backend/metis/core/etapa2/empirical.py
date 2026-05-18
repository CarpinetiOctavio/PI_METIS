import numpy as np


def probabilidades_weibull(
    serie: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fórmula de Weibull: T = (n+1)/m,  P = 1 - 1/T
    Fuente: Tesis Facundo, Cap. IV sección IV.1

    m = rango de la observación ordenada (1 = mínimo, n = máximo)

    Retorna (serie_ordenada, periodos_retorno, probabilidades)
    Los tres arrays tienen la misma longitud n y están ordenados ASC.
    """
    n = len(serie)
    serie_ordenada = np.sort(serie)
    m = np.arange(1, n + 1, dtype=float)
    periodos_retorno = (n + 1) / m
    probabilidades = 1.0 - 1.0 / periodos_retorno  # equivalente a m/(n+1)
    return serie_ordenada, periodos_retorno, probabilidades
