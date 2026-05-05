import numpy as np
from scipy.stats import skew

from metis.core.types import DescriptiveStats


def calcular_descriptiva(serie: list[float]) -> DescriptiveStats:
    arr = np.array(serie, dtype=float)
    n = len(arr)
    media = float(np.mean(arr))
    mediana = float(np.median(arr))
    desvio = float(np.std(arr, ddof=1))
    cv = desvio / media if media != 0 else float("nan")
    asimetria = float(skew(arr, bias=False))

    return DescriptiveStats(
        n=n,
        media=media,
        mediana=mediana,
        desvio_estandar=desvio,
        coef_variacion=cv,
        coef_asimetria=asimetria,
        minimo=float(np.min(arr)),
        maximo=float(np.max(arr)),
    )
