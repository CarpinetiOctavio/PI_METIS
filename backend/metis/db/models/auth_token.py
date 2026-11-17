import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from metis.db.base import Base


class AuthToken(Base):
    """Token de un solo uso enviado por mail (DECISIÓN 085).

    Hoy solo lo usa la recuperación de contraseña (`purpose = "password_reset"`). El token en claro
    viaja únicamente en el link del mail: en la base queda su SHA-256, así que un volcado de la base
    (o un respaldo) no alcanza para restablecer la contraseña de nadie.

    Las fechas son UTC sin zona, igual que `users.last_login`.
    """

    __tablename__ = "auth_tokens"
    __table_args__ = (Index("ix_auth_tokens_user_purpose", "user_id", "purpose"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
