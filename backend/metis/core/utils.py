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


def filtrar_numericos_alineados(
    serie: list, timestamps: list | None
) -> tuple[list[float], list | None]:
    """Como `filtrar_numericos()`, pero descarta el timestamp de cada valor
    que descarta — así `serie_efectiva` y `timestamps_efectivos` (Etapa1Result)
    quedan siempre del mismo largo y alineados uno a uno.

    El parser conserva los `None` a propósito (validar_contrato() los cuenta
    como CONTRACT_MISSING_VALUES), así que una carga anual con una celda
    vacía llega acá con la serie y los timestamps completos. Filtrar solo la
    serie dejaba los timestamps un elemento más largos: las etiquetas de año
    posteriores al faltante se corrían y rechazar un atípico de Chow borraba
    el año equivocado (docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md).

    `timestamps=None` (CU-03 sin columna de fecha) se devuelve como `None`.
    Si los largos no coinciden no hay forma de emparejar por posición: se
    conservan los timestamps tal cual llegaron (comportamiento previo) en
    vez de adivinar."""
    if timestamps is None:
        return filtrar_numericos(serie), None
    if len(timestamps) != len(serie):
        return filtrar_numericos(serie), timestamps
    pares = [(float(v), t) for v, t in zip(serie, timestamps) if es_numerico(v)]
    return [v for v, _ in pares], [t for _, t in pares]
