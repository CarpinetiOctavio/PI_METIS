import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db
from metis.db.models.user import User
from metis.services.analysis_service import (
    archive_analysis,
    get_analysis_by_id,
    get_history,
    unarchive_analysis,
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
