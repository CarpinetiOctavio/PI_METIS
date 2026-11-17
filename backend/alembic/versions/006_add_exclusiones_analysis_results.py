# DECISIÓN 080 (bloque C2 de docs/historico/planes/plan-revision-manual-21-10-2026.md) —
# exclusiones de puntos guardadas a pedido sobre un análisis ya persistido.
# Lista JSONB con default '[]': aditiva, sin backfill (los análisis anteriores
# quedan con la lista vacía). No toca etapa1, etapa2 ni decisiones.
"""add_exclusiones_analysis_results

Revision ID: 006
Revises: 005
Create Date: 2026-10-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "analysis_results",
        sa.Column(
            "exclusiones",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("analysis_results", "exclusiones")
