from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)

from app.models.base import Base

metadata = Base.metadata

parser_sources = Table(
    "parser_sources",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("code", String(32), nullable=False),
    Column("enabled", Boolean, nullable=False, server_default="true"),
    Column("rate_limit_per_min", Integer, nullable=False, server_default="60"),
    Column("max_concurrency", Integer, nullable=False, server_default="2"),
    Column("last_synced_at", DateTime(timezone=True)),
    UniqueConstraint("code", name="uq_parser_sources_code"),
)

parser_settings = Table(
    "parser_settings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("mode", String(16), nullable=False, server_default="manual"),
    Column("stage_only", Boolean, nullable=False, server_default="true"),
    Column("publish_enabled", Boolean, nullable=False, server_default="false"),
    Column("enable_autoupdate", Boolean, nullable=False, server_default="false"),
    Column("update_interval_minutes", Integer, nullable=False, server_default="60"),
    Column("dry_run", Boolean, nullable=False, server_default="false"),
    Column("allowed_translation_types", JSON),
    Column("allowed_translations", JSON),
    Column("allowed_qualities", JSON),
    Column("preferred_translation_priority", JSON),
    Column("preferred_quality_priority", JSON),
    Column("blacklist_titles", JSON),
    Column("blacklist_external_ids", JSON),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

parser_jobs = Table(
    "parser_jobs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("source_id", Integer, ForeignKey("parser_sources.id"), nullable=False),
    Column("job_type", String(32), nullable=False),
    Column("status", String(16), nullable=False),
    Column("started_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("finished_at", DateTime(timezone=True)),
    Column("error_summary", Text),
)

parser_job_logs = Table(
    "parser_job_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("job_id", Integer, ForeignKey("parser_jobs.id"), nullable=False),
    Column("level", String(16), nullable=False),
    Column("message", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

anime_external = Table(
    "anime_external",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("anime_id", String(36)),
    Column("source_id", Integer, ForeignKey("parser_sources.id"), nullable=False),
    Column("external_id", String(64), nullable=False),
    Column("title_raw", String(255)),
    Column("title_ru", String(255)),
    Column("title_en", String(255)),
    Column("title_original", String(255)),
    Column("description", Text),
    Column("poster_url", Text),
    Column("year", Integer),
    Column("season", String(32)),
    Column("status", String(32)),
    Column("genres", JSON),
    Column("match_confidence", Float),
    Column("matched_by", String(16)),
    Column("last_seen_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("source_hash", String(64)),
    UniqueConstraint("source_id", "external_id", name="uq_anime_external_source_id"),
)

anime_schedule = Table(
    "anime_schedule",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("anime_id", Integer, ForeignKey("anime_external.id"), nullable=False),
    Column("source_id", Integer, ForeignKey("parser_sources.id"), nullable=False),
    Column("episode_number", Integer),
    Column("air_datetime_utc", DateTime(timezone=True)),
    Column("status", String(32)),
    Column("source_hash", String(64)),
    Column(
        "last_checked_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    UniqueConstraint(
        "anime_id", "source_id", "episode_number", name="uq_anime_schedule_anime_id"
    ),
)

anime_episodes_external = Table(
    "anime_episodes_external",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("anime_id", Integer, ForeignKey("anime_external.id"), nullable=False),
    Column("source_id", Integer, ForeignKey("parser_sources.id"), nullable=False),
    Column("episode_number", Integer, nullable=False),
    Column("iframe_url", Text),
    Column("available_qualities", JSON),
    Column("available_translations", JSON),
    Column("needs_review", Boolean, nullable=False, server_default="false"),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    UniqueConstraint(
        "anime_id",
        "source_id",
        "episode_number",
        name="uq_anime_episodes_external_anime_id",
    ),
)

anime_translations = Table(
    "anime_translations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("anime_id", Integer, ForeignKey("anime_external.id"), nullable=False),
    Column("source_id", Integer, ForeignKey("parser_sources.id"), nullable=False),
    Column("translation_code", String(64), nullable=False),
    Column("translation_name", String(255)),
    Column("type", String(16)),
    Column("enabled", Boolean, nullable=False, server_default="true"),
    Column("priority", Integer, nullable=False, server_default="0"),
    UniqueConstraint(
        "anime_id",
        "source_id",
        "translation_code",
        name="uq_anime_translations_anime_id",
    ),
)

anime_external_binding = Table(
    "anime_external_binding",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("anime_external_id", Integer, ForeignKey("anime_external.id"), nullable=False),
    Column("anime_id", String(36), nullable=False),
    Column("bound_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    UniqueConstraint(
        "anime_external_id",
        name="uq_anime_external_binding_anime_external_id",
    ),
)
