import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


async def stream_etapa1(
    content: bytes,
    filename: str,
    columna_x: str,
    columna_y: str,
    tipo_variable: str,
    modo: str,
    cramer_particion: dict | str,
    session_id: str,
    user_id: uuid.UUID | None,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    # stub — implementación en feature/services-sse
    yield "event: progress\ndata: {}\n\n"


async def registrar_outlier_decision(
    session_id: str,
    decision: str,
    dato_atipico: float,
    db: AsyncSession,
) -> dict:
    # stub — implementación en feature/services-sse
    return {"ok": True, "pipeline_continua": True}


async def get_analysis_by_id(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict | None:
    # stub — consulta BD, retorna None si no existe o no pertenece al usuario
    return None


async def get_history(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> list[dict]:
    # stub — lista de análisis del usuario ordenados por created_at DESC
    return []
