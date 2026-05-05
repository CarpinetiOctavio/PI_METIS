import math


def es_numerico(v) -> bool:
    if v is None:
        return False
    try:
        return not math.isnan(float(v))
    except (TypeError, ValueError):
        return False


def filtrar_numericos(serie: list) -> list[float]:
    return [float(v) for v in serie if es_numerico(v)]
