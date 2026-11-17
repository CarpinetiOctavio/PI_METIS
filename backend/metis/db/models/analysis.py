import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from metis.db.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    serie: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # PR 3 del plan de cierre de pendientes no-test (DECISIÓN 058) —
    # timestamps de `serie` tal como se subieron, normalizados a ISO-8601
    # antes de persistir (services/analysis_service.py). Nullable sin
    # backfill: las filas de antes de esta migración quedan en NULL, el
    # frontend degrada explícitamente para esos análisis (DECISIÓN 058 §4).
    timestamps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tipo_variable: Mapped[str] = mapped_column(String(50), nullable=False)
    etapas: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    modo: Mapped[str | None] = mapped_column(String(20))
    configuracion: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    archivado_at: Mapped[datetime | None] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_analyses_user_id", "user_id"),
        Index("idx_analyses_created_at", "created_at"),
    )
