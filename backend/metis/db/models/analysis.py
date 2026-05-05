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
    tipo_variable: Mapped[str] = mapped_column(String(50), nullable=False)
    etapas: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    modo: Mapped[str | None] = mapped_column(String(20))
    configuracion: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_analyses_user_id", "user_id"),
        Index("idx_analyses_created_at", "created_at"),
    )
