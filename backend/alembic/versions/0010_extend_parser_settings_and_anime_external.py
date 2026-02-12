"""extend parser settings and anime external

Revision ID: 0010
Revises: 0009
Create Date: 2026-01-17 20:05:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parser_settings", sa.Column("allowed_translation_types", sa.JSON()))
    op.add_column("parser_settings", sa.Column("allowed_translations", sa.JSON()))
    op.add_column("parser_settings", sa.Column("allowed_qualities", sa.JSON()))
    op.add_column(
        "parser_settings", sa.Column("preferred_translation_priority", sa.JSON())
    )
    op.add_column(
        "parser_settings", sa.Column("preferred_quality_priority", sa.JSON())
    )
    op.add_column("parser_settings", sa.Column("blacklist_titles", sa.JSON()))
    op.add_column("parser_settings", sa.Column("blacklist_external_ids", sa.JSON()))
    op.add_column("anime_external", sa.Column("year", sa.Integer()))
    op.add_column("anime_external", sa.Column("status", sa.String(length=32)))


def downgrade() -> None:
    op.drop_column("anime_external", "status")
    op.drop_column("anime_external", "year")
    op.drop_column("parser_settings", "blacklist_external_ids")
    op.drop_column("parser_settings", "blacklist_titles")
    op.drop_column("parser_settings", "preferred_quality_priority")
    op.drop_column("parser_settings", "preferred_translation_priority")
    op.drop_column("parser_settings", "allowed_qualities")
    op.drop_column("parser_settings", "allowed_translations")
    op.drop_column("parser_settings", "allowed_translation_types")
