import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db
from metis.core.pipeline.exclusiones import ExclusionInvalidaError
from metis.db.models.user import User
from metis.schemas.export import GuardarExclusionRequest
from metis.services.analysis_service import (
    archive_analysis,
    get_analysis_by_id,
    get_history,
    unarchive_analysis,
)
from metis.services.exclusiones_service import (
    ExclusionNoEncontradaError,
    guardar_exclusion,
    quitar_exclusion,
)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/")
async def list_history(
    archivados: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_history(
        user_id=current_user.id, db=db, incluir_archivados=archivados
    )


@router.get("/{analysis_id}")
async def get_history_item(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_analysis_by_id(
        analysis_id=analysis_id,
        user_id=current_user.id,
        db=db,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return result


@router.post("/{analysis_id}/archive")
async def archive_history_item(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = await archive_analysis(analysis_id=analysis_id, user_id=current_user.id, db=db)
    if not ok:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return {"ok": True}


@router.post("/{analysis_id}/unarchive")
async def unarchive_history_item(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = await unarchive_analysis(
        analysis_id=analysis_id, user_id=current_user.id, db=db
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return {"ok": True}


# DECISIÓN 080 — exclusiones guardadas. Errores con la estructura estándar
# ({"error": {...}}, api/errors.py), a diferencia de los 404 de arriba.


def _error(status_code: int, codigo: str, mensaje: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"error": {"codigo": codigo, "mensaje": mensaje}},
    )


_ANALISIS_NO_ENCONTRADO = (
    404,
    "ANALYSIS_NOT_FOUND",
    "El análisis no existe o no pertenece al usuario.",
)


@router.post("/{analysis_id}/exclusiones")
async def guardar_exclusion_item(
    analysis_id: uuid.UUID,
    body: GuardarExclusionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Guarda una exclusión de puntos aparte del resultado (no toca etapa1,
    etapa2 ni decisiones). La misma selección no se duplica: devuelve la
    existente."""
    try:
        entrada = await guardar_exclusion(
            analysis_id=analysis_id,
            user_id=current_user.id,
            indices=body.indices_excluidos,
            db=db,
        )
    except ExclusionInvalidaError as error:
        raise _error(400, "CONTRACT_EXCLUSION_INVALID", str(error)) from None
    if entrada is None:
        raise _error(*_ANALISIS_NO_ENCONTRADO)
    return entrada


@router.delete("/{analysis_id}/exclusiones/{exclusion_id}")
async def quitar_exclusion_item(
    analysis_id: uuid.UUID,
    exclusion_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ok = await quitar_exclusion(
            analysis_id=analysis_id,
            user_id=current_user.id,
            exclusion_id=exclusion_id,
            db=db,
        )
    except ExclusionNoEncontradaError:
        raise _error(
            404,
            "ANALYSIS_EXCLUSION_NOT_FOUND",
            "La exclusión no existe en este análisis.",
        ) from None
    if not ok:
        raise _error(*_ANALISIS_NO_ENCONTRADO)
    return {"ok": True}
