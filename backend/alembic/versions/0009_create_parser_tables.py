"""create parser staging tables

Revision ID: 0009
Revises: 0008
Create Date: 2026-01-17 19:23:59.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parser_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "rate_limit_per_min", sa.Integer(), server_default="60", nullable=False
        ),
        sa.Column("max_concurrency", sa.Integer(), server_default="2", nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_parser_sources")),
        sa.UniqueConstraint("code", name=op.f("uq_parser_sources_code")),
    )
    op.create_table(
        "parser_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "mode", sa.String(length=16), server_default="manual", nullable=False
        ),
        sa.Column("stage_only", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "publish_enabled", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column("dry_run", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_parser_settings")),
    )
    op.create_table(
        "parser_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["parser_sources.id"],
            name=op.f("fk_parser_jobs_source_id_parser_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_parser_jobs")),
    )
    op.create_table(
        "parser_job_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["parser_jobs.id"],
            name=op.f("fk_parser_job_logs_job_id_parser_jobs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_parser_job_logs")),
    )
    op.create_table(
        "anime_external",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.String(length=36), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("title_raw", sa.String(length=255), nullable=True),
        sa.Column("match_confidence", sa.Float(), nullable=True),
        sa.Column("matched_by", sa.String(length=16), nullable=True),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("source_hash", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["parser_sources.id"],
            name=op.f("fk_anime_external_source_id_parser_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anime_external")),
        sa.UniqueConstraint(
            "source_id", "external_id", name=op.f("uq_anime_external_source_id")
        ),
    )
    op.create_table(
        "anime_schedule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=True),
        sa.Column("air_datetime_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column(
            "last_checked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["anime_id"],
            ["anime_external.id"],
            name=op.f("fk_anime_schedule_anime_id_anime_external"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["parser_sources.id"],
            name=op.f("fk_anime_schedule_source_id_parser_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anime_schedule")),
        sa.UniqueConstraint(
            "anime_id",
            "source_id",
            "episode_number",
            name=op.f("uq_anime_schedule_anime_id"),
        ),
    )
    op.create_table(
        "anime_episodes_external",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=False),
        sa.Column("iframe_url", sa.Text(), nullable=True),
        sa.Column("available_qualities", sa.JSON(), nullable=True),
        sa.Column("available_translations", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["anime_id"],
            ["anime_external.id"],
            name=op.f("fk_anime_episodes_external_anime_id_anime_external"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["parser_sources.id"],
            name=op.f("fk_anime_episodes_external_source_id_parser_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anime_episodes_external")),
        sa.UniqueConstraint(
            "anime_id",
            "source_id",
            "episode_number",
            name=op.f("uq_anime_episodes_external_anime_id"),
        ),
    )
    op.create_table(
        "anime_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("translation_code", sa.String(length=64), nullable=False),
        sa.Column("translation_name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=16), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(
            ["anime_id"],
            ["anime_external.id"],
            name=op.f("fk_anime_translations_anime_id_anime_external"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["parser_sources.id"],
            name=op.f("fk_anime_translations_source_id_parser_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anime_translations")),
        sa.UniqueConstraint(
            "anime_id",
            "source_id",
            "translation_code",
            name=op.f("uq_anime_translations_anime_id"),
        ),
    )


def downgrade() -> None:
    op.drop_table("anime_translations")
    op.drop_table("anime_episodes_external")
    op.drop_table("anime_schedule")
    op.drop_table("anime_external")
    op.drop_table("parser_job_logs")
    op.drop_table("parser_jobs")
    op.drop_table("parser_settings")
    op.drop_table("parser_sources")
