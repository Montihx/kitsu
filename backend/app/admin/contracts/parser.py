"""
Admin Parser Contracts - Read-only schemas for parser monitoring.

Defines data structures for viewing parser status and job information.
NO logic, NO validators - ONLY data structures.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParserJobStatusRead(BaseModel):
    """Status of a single parser job."""

    job_name: str
    state: str  # "idle", "running", "success", "failed"
    last_run_at: datetime | None  # Timezone-aware, nullable
    next_run_at: datetime | None  # Timezone-aware, nullable
    last_duration_ms: int | None  # Duration in milliseconds, nullable
    error: str | None  # Error message if failed, nullable

    model_config = ConfigDict(from_attributes=True)


class ParserJobSummary(BaseModel):
    """Summary statistics for a parser job."""

    job_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_duration_ms: int | None  # Average duration in milliseconds, nullable
    last_success_at: datetime | None  # Timezone-aware, nullable
    last_failure_at: datetime | None  # Timezone-aware, nullable

    model_config = ConfigDict(from_attributes=True)


class ParserStatusRead(BaseModel):
    """Overall parser system status."""

    is_enabled: bool
    is_healthy: bool
    jobs: list[ParserJobStatusRead]
    last_check_at: datetime  # Timezone-aware

    model_config = ConfigDict(from_attributes=True)
