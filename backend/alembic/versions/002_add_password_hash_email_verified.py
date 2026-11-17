# Migración generada manualmente — sin --autogenerate porque Docker no estaba activo.
# Verificar contra los modelos reales con `alembic check` cuando Docker esté disponible.
"""add password_hash and email_verified to users

Revision ID: 002
Revises: 001
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=False))
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "email_verified")
    op.drop_column("users", "password_hash")
