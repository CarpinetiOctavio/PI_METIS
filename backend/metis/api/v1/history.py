import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db
from metis.db.models.user import User
from metis.services.analysis_service import get_analysis_by_id, get_history

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/")
async def list_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_history(user_id=current_user.id, db=db)


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
