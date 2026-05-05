import uuid

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from metis.db.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    etapa1: Mapped[dict | None] = mapped_column(JSONB)
    etapa2: Mapped[dict | None] = mapped_column(JSONB)
    decisiones: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (Index("idx_analysis_results_analysis_id", "analysis_id"),)
