"""create releases and episodes tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-11 05:38:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "releases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("anime_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["anime_id"],
            ["anime.id"],
            name=op.f("fk_releases_anime_id_anime"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_releases")),
    )
    op.create_index(op.f("ix_releases_anime_id"), "releases", ["anime_id"], unique=False)

    op.create_table(
        "episodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("release_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["release_id"],
            ["releases.id"],
            name=op.f("fk_episodes_release_id_releases"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_episodes")),
    )
    op.create_index(
        op.f("ix_episodes_release_id"), "episodes", ["release_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_episodes_release_id"), table_name="episodes")
    op.drop_table("episodes")
    op.drop_index(op.f("ix_releases_anime_id"), table_name="releases")
    op.drop_table("releases")
