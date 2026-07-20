# Migración generada con --autogenerate (Docker activo, BD real).
#
# Origen del problema:
#   La migración 001 fue escrita manualmente sin Docker activo, lo que impidió
#   usar --autogenerate. En esa escritura manual se usó nullable=True por
#   defecto para columnas opcionales o con server_default, sin considerar que
#   SQLAlchemy infiere NOT NULL a partir del tipo Mapped[T] (sin Optional).
#
# Qué hace esta migración:
#   Corrige las 9 columnas donde el esquema de la BD (nullable=True, creado
#   por 001) diverge de lo que los modelos SQLAlchemy declaran (NOT NULL).
#   Aplica ALTER COLUMN ... SET NOT NULL sobre una BD sin datos reales, por lo
#   que no hay riesgo de violación de la constraint.
#
# Regla que se establece:
#   En SQLAlchemy con Mapped[T], si T no es Optional, la columna es NOT NULL.
#   Las columnas con server_default (func.now(), false, true, etc.) son NOT NULL
#   porque siempre tendrán valor — el default lo garantiza.
#   Solo Mapped[T | None] o Mapped[Optional[T]] produce columnas nullable.
#
# Detalle por tabla:
#
#   analyses:
#     - user_id:    FK obligatoria. Analyses solo se persisten en CU-01 (con JWT),
#                   por lo que siempre tienen un user_id asociado.
#     - created_at: timestamp con server_default=now(). Siempre presente.
#
#   analysis_results:
#     - analysis_id: FK obligatoria al análisis padre. No puede existir un
#                    resultado sin su análisis.
#
#   api_clients:
#     - auto_clean, report_frequency, cramer_particion: configuración con
#       valores por defecto. NOT NULL porque el default siempre los cubre.
#     - created_at: timestamp con server_default=now(). Siempre presente.
#     - activo:     flag booleano con default=True. NOT NULL.
#
#   users:
#     - created_at: timestamp con server_default=now(). Siempre presente.
#
# Verificación post-aplicación:
#   `alembic check` debe retornar exit code 0 sin diferencias detectadas.
"""fix_nullability_baseline

Revision ID: 003
Revises: 002
Create Date: 2026-05-15 01:59:08.637661

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # analyses — user_id y created_at pasan a NOT NULL
    op.alter_column("analyses", "user_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column(
        "analyses",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )

    # analysis_results — analysis_id pasa a NOT NULL
    op.alter_column(
        "analysis_results", "analysis_id", existing_type=sa.UUID(), nullable=False
    )

    # api_clients — todas las columnas con default pasan a NOT NULL
    op.alter_column(
        "api_clients",
        "auto_clean",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text("false"),
    )
    op.alter_column(
        "api_clients",
        "report_frequency",
        existing_type=sa.INTEGER(),
        nullable=False,
        existing_server_default=sa.text("1"),
    )
    op.alter_column(
        "api_clients",
        "cramer_particion",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
        existing_server_default=sa.text("'default'::character varying"),
    )
    op.alter_column(
        "api_clients",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "api_clients",
        "activo",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text("true"),
    )

    # users — created_at pasa a NOT NULL
    op.alter_column(
        "users",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )


def downgrade() -> None:
    # Revierte en orden inverso — restaura nullable=True en las 9 columnas.
    # Útil si se necesita volver al estado de migración 002.
    op.alter_column(
        "users",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "api_clients",
        "activo",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=sa.text("true"),
    )
    op.alter_column(
        "api_clients",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "api_clients",
        "cramer_particion",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
        existing_server_default=sa.text("'default'::character varying"),
    )
    op.alter_column(
        "api_clients",
        "report_frequency",
        existing_type=sa.INTEGER(),
        nullable=True,
        existing_server_default=sa.text("1"),
    )
    op.alter_column(
        "api_clients",
        "auto_clean",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=sa.text("false"),
    )
    op.alter_column(
        "analysis_results", "analysis_id", existing_type=sa.UUID(), nullable=True
    )
    op.alter_column(
        "analyses",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column("analyses", "user_id", existing_type=sa.UUID(), nullable=True)
