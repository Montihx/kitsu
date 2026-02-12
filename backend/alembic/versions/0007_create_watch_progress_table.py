"""create watch_progress table

Revision ID: 0007
Revises: 0006
Create Date: 2026-01-12 06:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "watch_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("anime_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("episode", sa.Integer(), nullable=False),
        sa.Column("position_seconds", sa.Integer(), nullable=True),
        sa.Column("progress_percent", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "last_watched_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_watch_progress_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["anime_id"],
            ["anime.id"],
            name=op.f("fk_watch_progress_anime_id_anime"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watch_progress")),
        sa.UniqueConstraint("user_id", "anime_id", name=op.f("uq_watch_progress_user_id")),
    )
    op.create_index(
        op.f("ix_watch_progress_user_id"), "watch_progress", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_watch_progress_anime_id"), "watch_progress", ["anime_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_watch_progress_anime_id"), table_name="watch_progress")
    op.drop_index(op.f("ix_watch_progress_user_id"), table_name="watch_progress")
    op.drop_table("watch_progress")
