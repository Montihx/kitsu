"""add parser autoupdate fields

Revision ID: 0012
Revises: 0011
Create Date: 2026-01-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parser_settings",
        sa.Column(
            "enable_autoupdate",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column(
        "parser_settings",
        sa.Column(
            "update_interval_minutes",
            sa.Integer(),
            server_default="60",
            nullable=False,
        ),
    )
    op.add_column("anime_schedule", sa.Column("source_hash", sa.String(length=64)))
    op.add_column(
        "anime_episodes_external",
        sa.Column(
            "needs_review",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("anime_episodes_external", "needs_review")
    op.drop_column("anime_schedule", "source_hash")
    op.drop_column("parser_settings", "update_interval_minutes")
    op.drop_column("parser_settings", "enable_autoupdate")
