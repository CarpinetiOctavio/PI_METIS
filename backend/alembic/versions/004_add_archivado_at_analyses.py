# DECISIÓN 048 (docs/decisiones/decision048.md) — archivado de análisis
# vía soft-delete, no borrado físico. Columna nullable sin default:
# aditiva y reversible, no rompe filas existentes. Numeración explícita
# "004" — mismo precedente que DECISIÓN 027 fijó para "003".
"""add_archivado_at_analyses

Revision ID: 004
Revises: 003
Create Date: 2026-07-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analyses",
        sa.Column("archivado_at", postgresql.TIMESTAMP(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analyses", "archivado_at")
