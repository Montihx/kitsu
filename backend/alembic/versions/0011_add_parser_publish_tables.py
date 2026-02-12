"""add parser publish tables

Revision ID: 0011
Revises: 0010
Create Date: 2026-01-19 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("anime", sa.Column("title_ru", sa.String(length=255)))
    op.add_column("anime", sa.Column("title_en", sa.String(length=255)))
    op.add_column("anime", sa.Column("poster_url", sa.Text()))
    op.add_column("anime", sa.Column("season", sa.String(length=32)))
    op.add_column("anime", sa.Column("genres", sa.JSON()))

    op.add_column("episodes", sa.Column("iframe_url", sa.Text()))
    op.add_column("episodes", sa.Column("available_translations", sa.JSON()))
    op.add_column("episodes", sa.Column("available_qualities", sa.JSON()))

    op.add_column("anime_external", sa.Column("title_ru", sa.String(length=255)))
    op.add_column("anime_external", sa.Column("title_en", sa.String(length=255)))
    op.add_column("anime_external", sa.Column("title_original", sa.String(length=255)))
    op.add_column("anime_external", sa.Column("description", sa.Text()))
    op.add_column("anime_external", sa.Column("poster_url", sa.Text()))
    op.add_column("anime_external", sa.Column("season", sa.String(length=32)))
    op.add_column("anime_external", sa.Column("genres", sa.JSON()))

    op.create_table(
        "anime_external_binding",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anime_external_id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.String(length=36), nullable=False),
        sa.Column("bound_by", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["anime_external_id"],
            ["anime_external.id"],
            name=op.f("fk_anime_external_binding_anime_external_id_anime_external"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anime_external_binding")),
        sa.UniqueConstraint(
            "anime_external_id",
            name=op.f("uq_anime_external_binding_anime_external_id"),
        ),
    )


def downgrade() -> None:
    op.drop_table("anime_external_binding")

    op.drop_column("anime_external", "genres")
    op.drop_column("anime_external", "season")
    op.drop_column("anime_external", "poster_url")
    op.drop_column("anime_external", "description")
    op.drop_column("anime_external", "title_original")
    op.drop_column("anime_external", "title_en")
    op.drop_column("anime_external", "title_ru")

    op.drop_column("episodes", "available_qualities")
    op.drop_column("episodes", "available_translations")
    op.drop_column("episodes", "iframe_url")

    op.drop_column("anime", "genres")
    op.drop_column("anime", "season")
    op.drop_column("anime", "poster_url")
    op.drop_column("anime", "title_en")
    op.drop_column("anime", "title_ru")
