"""
Admin User Contracts - Read-only schemas for user management.

Defines data structures for viewing and listing users in admin panel.
NO logic, NO validators - ONLY data structures.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminUserShort(BaseModel):
    """Minimal user information for lists and references."""

    id: UUID
    email: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AdminUserRead(BaseModel):
    """Complete user information for admin viewing."""

    id: UUID
    email: str
    is_active: bool
    roles: list[str]  # Role names
    created_at: datetime  # Timezone-aware
    last_login_at: datetime | None  # Timezone-aware, nullable

    model_config = ConfigDict(from_attributes=True)


class AdminUserList(BaseModel):
    """Paginated list of users."""

    users: list[AdminUserShort]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)
