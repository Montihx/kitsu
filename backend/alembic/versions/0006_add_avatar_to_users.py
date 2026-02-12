"""add avatar column to users

Revision ID: 0006
Revises: 0005
Create Date: 2026-01-11 09:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar")
