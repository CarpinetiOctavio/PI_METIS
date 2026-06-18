import numpy as np


def probabilidades_weibull(
    serie: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fórmula de Weibull: T = (n+1)/m,  P = 1 - 1/T
    Fuente: Tesis Facundo, Cap. IV sección IV.1

    Convención de la tesis: m=1 es el MÁXIMO (orden DESC).
    T[0] = n+1 (mayor período de retorno → observación mayor).
    P = 1 - 1/T es la probabilidad de no-excedencia.

    Retorna (serie_ordenada, periodos_retorno, probabilidades)
    Los tres arrays tienen la misma longitud n, ordenados DESC (mayor a menor).
    """
    n = len(serie)
    serie_ordenada = np.sort(serie)[::-1]  # DESC: m=1 es el máximo
    m = np.arange(1, n + 1, dtype=float)
    periodos_retorno = (n + 1) / m
    probabilidades = 1.0 - 1.0 / periodos_retorno
    return serie_ordenada, periodos_retorno, probabilidades
