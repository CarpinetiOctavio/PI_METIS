import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from metis.db.base import Base


class ApiClient(Base):
    __tablename__ = "api_clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    auto_clean: Mapped[bool] = mapped_column(Boolean, default=False)
    report_frequency: Mapped[int] = mapped_column(Integer, default=1)
    cramer_particion: Mapped[str] = mapped_column(String(20), default="default")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (Index("idx_api_clients_client_id", "client_id"),)
