"""Exclusión de puntos de una serie ya analizada — DECISIÓN 071.

Función pura: recibe la serie efectiva (ya agregada a máximos anuales) y sus años,
y devuelve la serie sin los puntos pedidos. No sabe nada de HTTP ni de sesiones.

Política: un punto excluido se ELIMINA junto con su año, en cualquier posición —
la misma operación que ya hace el rechazo de un atípico de Chow en
`services/analysis_service.py` (quitar el valor y su timestamp por índice), y el
mismo criterio que aplican los faltantes y la agregación temporal: eliminar y
compactar, nunca imputar. El reemplazo por la media quedó postergado, no
descartado (DECISIÓN 071); `tratamiento` es el punto de extensión si se aprueba.
"""

from dataclasses import dataclass, field

TRATAMIENTOS: frozenset[str] = frozenset({"eliminar"})


class ExclusionInvalidaError(ValueError):
    """El pedido de exclusión no es aplicable a esta serie: índices fuera de rango
    o repetidos, `anios` de otro largo que `serie`, o un `tratamiento` que no
    existe. El borde del endpoint la traduce a 400 CONTRACT_EXCLUSION_INVALID."""


@dataclass
class Excluido:
    indice: int  # posición en la serie de entrada (no en la serie cruda subida)
    periodo: int  # año del punto excluido
    valor_original: float


@dataclass
class SerieConExclusiones:
    serie: list[float]
    anios: list[int]
    excluidos: list[Excluido] = field(default_factory=list)


def aplicar_exclusiones(
    serie: list[float],
    anios: list[int],
    indices_excluidos: list[int],
    tratamiento: str = "eliminar",
) -> SerieConExclusiones:
    """Devuelve `serie` y `anios` sin las posiciones de `indices_excluidos`.

    Las dos listas de salida tienen siempre el mismo largo, igual que las de
    entrada. Excluir todo es válido acá (devuelve listas vacías): que queden
    menos de 10 datos lo decide `ejecutar_etapa1()` con su error bloqueante de
    siempre (CONTRACT_SERIES_TOO_SHORT), no esta función.
    """
    if tratamiento not in TRATAMIENTOS:
        raise ExclusionInvalidaError(
            f"tratamiento {tratamiento!r} no existe; el único disponible es 'eliminar'."
        )
    if len(anios) != len(serie):
        raise ExclusionInvalidaError("anios tiene que tener el mismo largo que serie.")
    if len(set(indices_excluidos)) != len(indices_excluidos):
        raise ExclusionInvalidaError("indices_excluidos tiene índices repetidos.")
    if any(i < 0 or i >= len(serie) for i in indices_excluidos):
        raise ExclusionInvalidaError(
            "indices_excluidos tiene índices fuera de la serie."
        )

    excluir = set(indices_excluidos)
    return SerieConExclusiones(
        serie=[v for i, v in enumerate(serie) if i not in excluir],
        anios=[a for i, a in enumerate(anios) if i not in excluir],
        excluidos=[
            Excluido(indice=i, periodo=anios[i], valor_original=float(serie[i]))
            for i in sorted(excluir)
        ],
    )
