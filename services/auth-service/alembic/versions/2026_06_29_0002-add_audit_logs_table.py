"""add audit_logs table

Revision ID: 2026_06_29_0002
Revises: 3a35d60cbd19
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op

revision: str = "2026_06_29_0002"
down_revision: Union[str, Sequence[str], None] = "3a35d60cbd19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # audit_logs table already created in 46c09bbbbb61 (initial_tables).
    # Only add indexes that were missing from the original creation.
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
