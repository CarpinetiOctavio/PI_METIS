"""Nivel de significancia de la Etapa 1 — DECISIÓN 078.

α es elegible entre 1 %, 5 % (por defecto, el estándar en hidrología según
Facundo Ganancias Martínez, comunicación del 18/10/2026) y 10 %. Se aplica a las
ocho pruebas de la Etapa 1; Helmert y la tolerancia de Anderson no dependen de α.
La Etapa 2 no tiene nivel de significancia.
"""

from scipy.stats import norm

ALFA_DEFECTO = 0.05
NIVELES_ALFA: tuple[float, ...] = (0.01, 0.05, 0.10)

# Kolmogorov-Smirnov de tendencia (Ec. A.57): la Tabla A.5 de Caamaño Nelli y
# Colladon da 1,358 para α = 0,05, el valor que METIS usó siempre. Para 1 % y
# 10 % se usa c(α) = √(−ln(α/2)/2), la misma aproximación asintótica de la que
# sale 1,358, redondeada igual a tres decimales.
KS_Z_CRIT: dict[float, float] = {0.01: 1.628, 0.05: 1.358, 0.10: 1.224}


def validar_alfa(alfa: float) -> float:
    """Devuelve `alfa` si es uno de `NIVELES_ALFA`; si no, ValueError. El borde
    de la API valida antes con su propio código (CONTRACT_ALFA_INVALID): esto
    es la red de seguridad del núcleo."""
    if alfa not in NIVELES_ALFA:
        raise ValueError(f"alfa={alfa!r} no es uno de {NIVELES_ALFA}")
    return alfa


def z_bilateral(alfa: float) -> float:
    """Cuantil z_{1−α/2} de la normal estándar (Anderson, Ec. III-3;
    Wald-Wolfowitz, Ec. III-4; Mann-Kendall, Ec. A.55). Con α = 0,05 es
    exactamente el `norm.ppf(0.975)` que se usaba antes: 1,959963…"""
    return float(norm.ppf(1 - validar_alfa(alfa) / 2))
