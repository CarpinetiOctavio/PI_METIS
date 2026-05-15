# Migración generada manualmente — sin --autogenerate porque Docker no estaba activo.
# Verificar contra los modelos reales con `alembic check` cuando Docker esté disponible.
"""baseline schema

Revision ID: 001
Revises:
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "analyses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("serie", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tipo_variable", sa.String(50), nullable=False),
        sa.Column("etapas", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("modo", sa.String(20), nullable=True),
        sa.Column(
            "configuracion", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_analyses_user_id", "analyses", ["user_id"])
    op.create_index("idx_analyses_created_at", "analyses", ["created_at"])

    op.create_table(
        "analysis_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("etapa1", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("etapa2", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("decisiones", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_analysis_results_analysis_id", "analysis_results", ["analysis_id"]
    )

    op.create_table(
        "api_clients",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("client_id", sa.String(100), nullable=False),
        sa.Column("api_key_hash", sa.String(255), nullable=False),
        sa.Column(
            "auto_clean", sa.Boolean(), server_default=sa.text("false"), nullable=True
        ),
        sa.Column(
            "report_frequency", sa.Integer(), server_default=sa.text("1"), nullable=True
        ),
        sa.Column(
            "cramer_particion",
            sa.String(20),
            server_default=sa.text("'default'"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column(
            "activo", sa.Boolean(), server_default=sa.text("true"), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id"),
    )
    op.create_index("idx_api_clients_client_id", "api_clients", ["client_id"])


def downgrade() -> None:
    op.drop_index("idx_api_clients_client_id", table_name="api_clients")
    op.drop_table("api_clients")
    op.drop_index("idx_analysis_results_analysis_id", table_name="analysis_results")
    op.drop_table("analysis_results")
    op.drop_index("idx_analyses_created_at", table_name="analyses")
    op.drop_index("idx_analyses_user_id", table_name="analyses")
    op.drop_table("analyses")
    op.drop_table("users")
