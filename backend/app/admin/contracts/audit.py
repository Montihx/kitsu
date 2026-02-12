"""
Admin Audit Contracts - Read-only schemas for audit log viewing.

Defines data structures for viewing audit logs in admin panel.
NO logic, NO validators - ONLY data structures.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminAuditActor(BaseModel):
    """Information about who performed the action."""

    actor_id: UUID | None  # Nullable for system actions
    actor_type: str  # "user" or "system"
    actor_email: str | None  # User email if available

    model_config = ConfigDict(from_attributes=True)


class AdminAuditTarget(BaseModel):
    """Information about what was affected by the action."""

    entity_type: str  # Type of entity (e.g., "user", "role", "parser")
    entity_id: str  # Entity identifier
    entity_name: str | None  # Human-readable name if available

    model_config = ConfigDict(from_attributes=True)


class AdminAuditLogRead(BaseModel):
    """Complete audit log entry for admin viewing."""

    id: UUID
    action: str  # Action performed (e.g., "create", "update", "delete")
    actor: AdminAuditActor
    target: AdminAuditTarget
    payload: dict[str, Any]  # Additional context and changes
    ip_address: str | None  # Client IP if available
    user_agent: str | None  # Client user agent if available
    created_at: datetime  # Timezone-aware

    model_config = ConfigDict(from_attributes=True)
