"""add_user_type

Revision ID: 216181ee4c1e
Revises: 078f706f40a5
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '216181ee4c1e'
down_revision: Union[str, None] = '078f706f40a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('user_type', sa.String(20), nullable=False, server_default='REGULAR'))


def downgrade() -> None:
    op.drop_column('users', 'user_type')

