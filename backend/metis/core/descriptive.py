import numpy as np
from scipy.stats import skew

from metis.core.types import DescriptiveStats


def calcular_descriptiva(serie: list[float]) -> DescriptiveStats:
    arr = np.array(serie, dtype=float)
    n = len(arr)
    media = float(np.mean(arr))
    mediana = float(np.median(arr))

    # Varianzas y desvío (Ec. IV-2, IV-3, IV-8)
    var_sesgada = float(np.var(arr, ddof=0))
    var_no_sesgada = float(np.var(arr, ddof=1))
    desvio = float(np.sqrt(var_no_sesgada))

    # Coeficiente de variación (Ec. IV-9)
    cv = desvio / media if media != 0 else float("nan")

    # Asimetría sesgada y no sesgada (Ec. IV-4, IV-5)
    asimetria_sesgada = float(skew(arr, bias=True))
    asimetria_no_sesgada = float(skew(arr, bias=False))

    # Curtosis (Ec. IV-6, IV-7) — calculada directamente para evitar ambigüedad de scipy
    if var_sesgada > 0 and n >= 4:
        k_sesg = float(np.mean((arr - media) ** 4) / var_sesgada**2)
        k_insesg = float((n**3 / ((n - 1) * (n - 2) * (n - 3))) * k_sesg)
    elif var_sesgada > 0:
        k_sesg = float(np.mean((arr - media) ** 4) / var_sesgada**2)
        k_insesg = None
    else:
        k_sesg = None
        k_insesg = None

    # Σln(xi) — insumo para MV en distribuciones log; None si algún xi ≤ 0
    suma_log = float(np.sum(np.log(arr))) if np.all(arr > 0) else None

    # MPP — Momentos de Probabilidad Pesada (Ec. IV-21 a IV-24)
    # Serie ordenada de MAYOR a menor (i=1 es el valor más grande)
    xs = np.sort(arr)[::-1]
    idx = np.arange(1, n + 1)  # i = 1..n

    mpp_m0 = float(np.mean(xs))  # Ec. IV-21 (idéntico a media)

    # M̂₁: Σ_{i=1}^{n-1} (n-i) · x_i  /  [n(n-1)]  (Ec. IV-22)
    i1 = idx[: n - 1]
    mpp_m1 = float(np.sum((n - i1) * xs[: n - 1]) / (n * (n - 1))) if n >= 2 else None

    # M̂₂: Σ_{i=1}^{n-2} (n-i)(n-i-1) · x_i  /  [n(n-1)(n-2)]  (Ec. IV-23)
    i2 = idx[: n - 2]
    mpp_m2 = (
        float(np.sum((n - i2) * (n - i2 - 1) * xs[: n - 2]) / (n * (n - 1) * (n - 2)))
        if n >= 3
        else None
    )

    # M̂₃: Σ_{i=1}^{n-3} (n-i)(n-i-1)(n-i-2) · x_i  /  [n(n-1)(n-2)(n-3)]  (Ec. IV-24)
    i3 = idx[: n - 3]
    mpp_m3 = (
        float(
            np.sum((n - i3) * (n - i3 - 1) * (n - i3 - 2) * xs[: n - 3])
            / (n * (n - 1) * (n - 2) * (n - 3))
        )
        if n >= 4
        else None
    )

    return DescriptiveStats(
        n=n,
        media=media,
        mediana=mediana,
        desvio_estandar=desvio,
        coef_variacion=cv,
        coef_asimetria=asimetria_no_sesgada,
        minimo=float(np.min(arr)),
        maximo=float(np.max(arr)),
        varianza_sesgada=var_sesgada,
        varianza_no_sesgada=var_no_sesgada,
        asimetria_sesgada=asimetria_sesgada,
        curtosis_sesgada=k_sesg,
        curtosis_no_sesgada=k_insesg,
        suma_log=suma_log,
        mpp_m0=mpp_m0,
        mpp_m1=mpp_m1,
        mpp_m2=mpp_m2,
        mpp_m3=mpp_m3,
    )
