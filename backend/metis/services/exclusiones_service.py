"""Exclusiones guardadas en el historial — DECISIÓN 080.

Una exclusión de puntos hecha después del análisis ("Excluir puntos de la serie",
DECISIÓN 071) se puede guardar a pedido en `analysis_results.exclusiones`. Se
guarda **aparte** del resultado: no modifica `etapa1`, `etapa2` ni `decisiones`
(DECISIÓN 062, "explorar no es decidir"). Tampoco se guardan los resultados de la
simulación: `simulate-exclusion` es determinístico y se recalcula al abrirla.

Los años y los valores de cada punto salen del análisis persistido, no del
cliente: del cliente llegan solo los índices, posiciones en
`etapa1.datos.serie_efectiva`.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metis.core.etapa1.significancia import ALFA_DEFECTO
from metis.core.pipeline.exclusiones import ExclusionInvalidaError, aplicar_exclusiones
from metis.db.models import Analysis, AnalysisResult


class ExclusionNoEncontradaError(LookupError):
    """La exclusión pedida no existe en ese análisis. 404 ANALYSIS_EXCLUSION_NOT_FOUND."""


async def _cargar(
    analysis_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
) -> tuple[Analysis, AnalysisResult] | None:
    """Mismo guard de pertenencia que `get_analysis_by_id()`: un análisis ajeno
    o inexistente devuelve None sin distinguir los dos casos."""
    stmt = (
        select(Analysis, AnalysisResult)
        .join(AnalysisResult, AnalysisResult.analysis_id == Analysis.id)
        .where(Analysis.id == analysis_id, Analysis.user_id == user_id)
    )
    row = (await db.execute(stmt)).first()
    return None if row is None else (row[0], row[1])


def _puntos(result: AnalysisResult, indices: list[int]) -> list[dict]:
    """Valida los índices contra la serie analizada y devuelve cada punto con su
    año y su valor. Levanta `ExclusionInvalidaError` (→ 400 CONTRACT_EXCLUSION_INVALID)."""
    datos = (result.etapa1 or {}).get("datos") or {}
    serie = datos.get("serie_efectiva")
    timestamps = datos.get("timestamps_efectivos")
    if not serie:
        raise ExclusionInvalidaError(
            "Este análisis no tiene registrada la serie analizada: no se puede guardar "
            "una exclusión de puntos."
        )
    if not indices:
        raise ExclusionInvalidaError("indices_excluidos no puede estar vacío.")
    if len(set(indices)) >= len(serie):
        raise ExclusionInvalidaError(
            "La exclusión no puede quitar todos los puntos de la serie."
        )
    anios = (
        [t.get("anio") for t in timestamps]
        if timestamps and len(timestamps) == len(serie)
        else [None] * len(serie)
    )
    # core/ valida rango y repetidos, igual que en simulate-exclusion.
    recortada = aplicar_exclusiones(serie, anios, indices)
    return [
        {"indice": e.indice, "periodo": e.periodo, "valor": e.valor_original}
        for e in recortada.excluidos
    ]


async def guardar_exclusion(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    indices: list[int],
    db: AsyncSession,
) -> dict | None:
    """Guarda la exclusión y la devuelve. Si la misma selección ya estaba
    guardada, devuelve la existente sin duplicarla. None si el análisis no
    existe o no es del usuario."""
    cargado = await _cargar(analysis_id, user_id, db)
    if cargado is None:
        return None
    analysis, result = cargado
    puntos = _puntos(result, indices)
    ordenados = sorted(indices)

    existentes = list(result.exclusiones or [])
    for entrada in existentes:
        if entrada.get("indices") == ordenados:
            return entrada

    configuracion = analysis.configuracion or {}
    entrada = {
        "id": str(uuid.uuid4()),
        "creado_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        "indices": ordenados,
        "puntos": puntos,
        "alfa": configuracion.get("alfa", ALFA_DEFECTO),
        "cramer_particion": configuracion.get("cramer_particion", "default"),
    }
    # Lista nueva, no append: SQLAlchemy no detecta la mutación in situ de un JSONB.
    result.exclusiones = [*existentes, entrada]
    await db.commit()
    return entrada


async def quitar_exclusion(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    exclusion_id: str,
    db: AsyncSession,
) -> bool:
    """False si el análisis no existe o no es del usuario. Levanta
    `ExclusionNoEncontradaError` si el análisis es suyo pero no tiene esa exclusión."""
    cargado = await _cargar(analysis_id, user_id, db)
    if cargado is None:
        return False
    _, result = cargado
    existentes = list(result.exclusiones or [])
    restantes = [e for e in existentes if e.get("id") != exclusion_id]
    if len(restantes) == len(existentes):
        raise ExclusionNoEncontradaError(exclusion_id)
    result.exclusiones = restantes
    await db.commit()
    return True
