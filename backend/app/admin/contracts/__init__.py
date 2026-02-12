"""
Admin Data Contracts - Read-only schemas for future admin panel.

This module defines data contracts (Pydantic models) for admin functionality.
NO logic, NO validators, NO computed fields - ONLY data structures.

Python 3.12+ required.
"""
from __future__ import annotations

from app.admin.contracts.audit import (
    AdminAuditActor,
    AdminAuditLogRead,
    AdminAuditTarget,
)
from app.admin.contracts.parser import (
    ParserJobStatusRead,
    ParserJobSummary,
    ParserStatusRead,
)
from app.admin.contracts.permissions import AdminPermission
from app.admin.contracts.roles import (
    AdminRoleAssignment,
    AdminRoleList,
    AdminRoleRead,
)
from app.admin.contracts.system import (
    SystemComponentStatus,
    SystemHealthRead,
)
from app.admin.contracts.users import (
    AdminUserList,
    AdminUserRead,
    AdminUserShort,
)

__all__ = [
    # Users
    "AdminUserRead",
    "AdminUserShort",
    "AdminUserList",
    # Roles
    "AdminRoleRead",
    "AdminRoleList",
    "AdminRoleAssignment",
    # Permissions
    "AdminPermission",
    # Audit
    "AdminAuditLogRead",
    "AdminAuditActor",
    "AdminAuditTarget",
    # Parser
    "ParserStatusRead",
    "ParserJobStatusRead",
    "ParserJobSummary",
    # System
    "SystemHealthRead",
    "SystemComponentStatus",
]
