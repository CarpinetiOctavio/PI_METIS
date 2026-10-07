import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db
from metis.core.pipeline.exclusiones import ExclusionInvalidaError
from metis.db.models.user import User
from metis.schemas.export import ExportSimulacionRequest
from metis.services.export_service import (
    SimulacionNoDisponibleError,
    exportar_pdf,
    exportar_pdf_simulacion,
)

router = APIRouter(prefix="/export", tags=["export"])

_RESPUESTA_PDF = {200: {"content": {"application/pdf": {}}}}

# Los errores se arman con JSONResponse y no con HTTPException para que el
# body sea la estructura estándar ({"error": {...}}, api-contracts.md) y no
# {"detail": {"error": {...}}}.


def _error(status_code: int, codigo: str, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"codigo": codigo, "mensaje": mensaje}},
    )


def _no_encontrado() -> JSONResponse:
    return _error(
        404, "ANALYSIS_NOT_FOUND", "El análisis no existe o no pertenece al usuario."
    )


def _autor(user: User) -> str:
    return f"{user.nombre} ({user.email})" if user.nombre else user.email


def _pdf(contenido: bytes, nombre: str) -> Response:
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/{analysis_id}", response_class=Response, responses=_RESPUESTA_PDF)
async def exportar_analisis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # DECISIÓN 075 — solo CU-01: JWT obligatorio y pertenencia del análisis,
    # mismo guard que GET /history/{id}.
    resultado = await exportar_pdf(
        analysis_id=analysis_id,
        user_id=current_user.id,
        db=db,
        autor=_autor(current_user),
    )
    if resultado is None:
        return _no_encontrado()
    return _pdf(*resultado)


@router.post(
    "/{analysis_id}/simulacion", response_class=Response, responses=_RESPUESTA_PDF
)
async def exportar_analisis_con_simulacion(
    analysis_id: uuid.UUID,
    body: ExportSimulacionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # DECISIÓN 075, addendum — el análisis registrado más los resultados sin
    # los puntos excluidos (DECISIÓN 071). Recalcula, no guarda nada.
    if not body.indices_excluidos:
        return _error(
            400,
            "CONTRACT_EXCLUSION_INVALID",
            "indices_excluidos tiene que traer al menos un punto.",
        )
    try:
        resultado = await exportar_pdf_simulacion(
            analysis_id=analysis_id,
            user_id=current_user.id,
            db=db,
            indices_excluidos=body.indices_excluidos,
            autor=_autor(current_user),
        )
    except (SimulacionNoDisponibleError, ExclusionInvalidaError) as error:
        return _error(400, "CONTRACT_EXCLUSION_INVALID", str(error))
    if resultado is None:
        return _no_encontrado()
    return _pdf(*resultado)
