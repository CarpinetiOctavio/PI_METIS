import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db, get_optional_user
from metis.db.models.user import User
from metis.schemas.analysis import OutlierDecisionRequest, OutlierDecisionResponse
from metis.services.analysis_service import (
    get_analysis_by_id,
    registrar_outlier_decision,
    stream_etapa1,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/stream")
async def stream_analysis(
    archivo: UploadFile = File(...),
    columna_x: str = Form(...),
    columna_y: str = Form(...),
    tipo_variable: str = Form(...),
    etapas: str = Form("1"),
    modo: str = Form("experto"),
    cramer_particion: str = Form("default"),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    content = await archivo.read()
    session_id = str(uuid.uuid4())

    return StreamingResponse(
        stream_etapa1(
            content=content,
            filename=archivo.filename or "upload",
            columna_x=columna_x,
            columna_y=columna_y,
            tipo_variable=tipo_variable,
            modo=modo,
            cramer_particion=cramer_particion,
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            db=db,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/outlier-decision", response_model=OutlierDecisionResponse)
async def outlier_decision(
    body: OutlierDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await registrar_outlier_decision(
        session_id=str(body.session_id),
        decision=body.decision,
        dato_atipico=body.dato_atipico,
        db=db,
    )
    return OutlierDecisionResponse(**result)


@router.get("/{analysis_id}")
async def get_analysis(
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
