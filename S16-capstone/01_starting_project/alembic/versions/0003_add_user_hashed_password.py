"""add users.hashed_password (session 9)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-24

Existing users get the value '!', which is not a valid hash: nobody can log
in with it, so those users must set a new password. Never invent real
passwords in a migration.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '0003'
down_revision: str | None = '0002'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('hashed_password', sa.String(length=255), nullable=False, server_default='!')
        )


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('hashed_password')
