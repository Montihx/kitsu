"""
Admin Role Contracts - Read-only schemas for role management.

Defines data structures for viewing roles and role assignments.
NO logic, NO validators - ONLY data structures.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminRoleRead(BaseModel):
    """Complete role information for admin viewing."""

    id: UUID
    name: str
    display_name: str
    permissions: list[str]  # Permission identifiers
    is_system: bool
    is_active: bool
    created_at: datetime  # Timezone-aware

    model_config = ConfigDict(from_attributes=True)


class AdminRoleList(BaseModel):
    """List of roles for admin viewing."""

    roles: list[AdminRoleRead]
    total: int

    model_config = ConfigDict(from_attributes=True)


class AdminRoleAssignment(BaseModel):
    """Role assignment information for users."""

    user_id: UUID
    role_id: UUID
    role_name: str
    assigned_at: datetime  # Timezone-aware
    assigned_by: UUID | None  # User who assigned the role, nullable

    model_config = ConfigDict(from_attributes=True)
