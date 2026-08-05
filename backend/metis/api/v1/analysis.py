import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db, get_optional_user
from metis.core.validacion.parser import leer_columnas_preview
from metis.db.models.user import User
from metis.schemas.analysis import (
    OutlierDecisionRequest,
    OutlierDecisionResponse,
    PreviewColumnsResponse,
)
from metis.services.analysis_service import (
    get_analysis_by_id,
    registrar_outlier_decision,
    stream_etapa1,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

# DECISIÓN 050 — mismo valor que client_max_body_size en nginx/nginx.conf y
# frontend/nginx.conf. nginx no es el único camino: :8000 está mapeado al
# host por diseño (architecture.md, "Exposición de puertos en desarrollo"),
# así que un cliente que salte el proxy tiene que encontrar el mismo límite acá.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024

_ARCHIVO_DEMASIADO_GRANDE = HTTPException(
    status_code=400,
    detail={
        "error": {
            "codigo": "PARSE_FILE_TOO_LARGE",
            "mensaje": f"El archivo supera el límite de {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        }
    },
)


async def _leer_archivo_limitado(archivo: UploadFile) -> bytes:
    """Lee un UploadFile en chunks, cortando apenas se supera MAX_UPLOAD_BYTES
    — nunca buferea un archivo entero por encima del límite en memoria, ni
    siquiera si el cliente miente el Content-Length (DECISIÓN 050)."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await archivo.read(_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise _ARCHIVO_DEMASIADO_GRANDE
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/preview-columns", response_model=PreviewColumnsResponse)
async def preview_columns(archivo: UploadFile = File(...)):
    # DECISIÓN 047 — stateless, sin dependencia de usuario: no hay ninguna
    # diferencia de comportamiento según quién llama, así que "JWT opcional"
    # se cumple por no inspeccionar la cookie en absoluto, no por leerla y
    # descartarla. No toca session_store ni BD.
    content = await _leer_archivo_limitado(archivo)
    try:
        columnas, filas = leer_columnas_preview(content, archivo.filename or "upload")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "codigo": "PARSE_ERROR",
                    "mensaje": "No se pudo leer el archivo. Verificá que sea un CSV o Excel válido.",
                }
            },
        ) from exc

    return PreviewColumnsResponse(columnas=columnas, filas=filas)


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
    # DECISIÓN 036 (Bloque D) — cramer_particion distinto de "default" llega
    # como str vía multipart y calcular_cramer() indexa particion["n1_pct"]
    # asumiendo dict, lo que producía TypeError -> 500 no manejado. Esto NO
    # implementa la partición personalizada (ninguna de las tres opciones de
    # la decisión fue elegida) — solo cierra el 500 con un 400 controlado.
    if cramer_particion != "default":
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "codigo": "CONTRACT_CRAMER_PARTICION_UNSUPPORTED",
                    "mensaje": (
                        "La partición personalizada de Cramer todavía no está"
                        " implementada. Usá 'default'."
                    ),
                }
            },
        )

    content = await _leer_archivo_limitado(archivo)
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
