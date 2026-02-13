"""Add pg_trgm GIN index for anime.title ILIKE search

Revision ID: 0016
Revises: 0015
Create Date: 2026-02-13 10:20:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str | None = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TRGM_INDEX_NAME = "ix_anime_title_trgm"


def upgrade() -> None:
    """Apply schema changes."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        f"CREATE INDEX IF NOT EXISTS {TRGM_INDEX_NAME} "
        "ON anime USING gin (title gin_trgm_ops)"
    )


def downgrade() -> None:
    """Revert schema changes."""
    op.execute(f"DROP INDEX IF EXISTS {TRGM_INDEX_NAME}")
