"""
Admin System Contracts - Read-only schemas for system health monitoring.

Defines data structures for viewing system health and component status.
NO logic, NO validators - ONLY data structures.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SystemComponentStatus(BaseModel):
    """Status of a single system component."""

    name: str  # Component name (e.g., "database", "redis", "parser")
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: int | None  # Response time in milliseconds, nullable
    error: str | None  # Error message if unhealthy, nullable
    details: dict[str, str] | None  # Additional component-specific details, nullable

    model_config = ConfigDict(from_attributes=True)


class SystemHealthRead(BaseModel):
    """Overall system health status."""

    status: str  # "healthy", "degraded", "unhealthy"
    components: list[SystemComponentStatus]
    checked_at: datetime  # Timezone-aware

    model_config = ConfigDict(from_attributes=True)
