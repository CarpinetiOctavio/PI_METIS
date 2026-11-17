# PR 3 del plan de cierre de pendientes no-test (docs/decisiones/decision058.md)
# — timestamps de la serie subida, normalizados a ISO-8601 antes de
# persistir. Columna nullable sin default: aditiva y reversible, sin
# backfill (DECISIÓN 058 §4) — mismo precedente que "004"
# (archivado_at) sentó para columnas nuevas de `analyses`.
"""add_timestamps_analyses

Revision ID: 005
Revises: 004
Create Date: 2026-08-12 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analyses",
        sa.Column("timestamps", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analyses", "timestamps")
