"""add oauth fields to users

Revision ID: a1b2c3d4e5f6
Revises: 45794e81999c
Create Date: 2026-04-29 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '45794e81999c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('auth_source', sa.String(length=20), server_default='email', nullable=False))
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('google_refresh_token', sa.String(length=512), nullable=True))
    op.add_column('users', sa.Column('azure_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('azure_refresh_token', sa.String(length=512), nullable=True))
    op.alter_column('users', 'hashed_password', existing_type=sa.String(length=128), nullable=True)
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])
    op.create_unique_constraint('uq_users_azure_id', 'users', ['azure_id'])
    op.create_index('ix_users_google_id', 'users', ['google_id'])
    op.create_index('ix_users_azure_id', 'users', ['azure_id'])


def downgrade() -> None:
    op.drop_index('ix_users_azure_id', table_name='users')
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_constraint('uq_users_azure_id', 'users', type_='unique')
    op.drop_constraint('uq_users_google_id', 'users', type_='unique')
    op.alter_column('users', 'hashed_password', existing_type=sa.String(length=128), nullable=False)
    op.drop_column('users', 'azure_refresh_token')
    op.drop_column('users', 'azure_id')
    op.drop_column('users', 'google_refresh_token')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'auth_source')
