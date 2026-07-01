"""initial chat_write tables

Revision ID: 0001_chat_write
Revises:
Create Date: 2026-06-30

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_chat_write"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False, server_default="New Chat"),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        schema="chat_write",
    )
    op.create_index("ix_chat_write_sessions_user_id", "chat_sessions", ["user_id"], schema="chat_write")

    op.create_table(
        "chat_messages",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(64), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        schema="chat_write",
    )
    op.create_index("ix_chat_write_messages_session_id", "chat_messages", ["session_id"], schema="chat_write")
    op.create_index("ix_chat_write_messages_user_id", "chat_messages", ["user_id"], schema="chat_write")


def downgrade() -> None:
    op.drop_index("ix_chat_write_messages_user_id", table_name="chat_messages", schema="chat_write")
    op.drop_index("ix_chat_write_messages_session_id", table_name="chat_messages", schema="chat_write")
    op.drop_table("chat_messages", schema="chat_write")
    op.drop_index("ix_chat_write_sessions_user_id", table_name="chat_sessions", schema="chat_write")
    op.drop_table("chat_sessions", schema="chat_write")
