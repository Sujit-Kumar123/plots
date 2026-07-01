"""initial plot_unified tables

Revision ID: 0001_plot
Revises:
Create Date: 2026-06-30

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_plot"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS plot_unified")

    op.create_table(
        "plots",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False, server_default="Untitled Plot"),
        sa.Column("sheet_w", sa.Float(), nullable=False, server_default="20.0"),
        sa.Column("sheet_d", sa.Float(), nullable=False, server_default="20.0"),
        sa.Column("grid_step", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("elements", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("element_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        schema="plot_unified",
    )
    op.create_index("ix_plot_user", "plots", ["user_id"], schema="plot_unified")
    op.create_index("ix_plot_session", "plots", ["session_id"], schema="plot_unified")


def downgrade() -> None:
    op.drop_index("ix_plot_session", table_name="plots", schema="plot_unified")
    op.drop_index("ix_plot_user", table_name="plots", schema="plot_unified")
    op.drop_table("plots", schema="plot_unified")
    op.execute("DROP SCHEMA IF EXISTS plot_unified")
