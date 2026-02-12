"""
Admin Permission Contracts - Permission enumeration for admin operations.

Defines all available admin permissions as an enum.
NO logic, NO helper functions - ONLY permission identifiers.
"""
from __future__ import annotations

from enum import Enum


class AdminPermission(str, Enum):
    """Admin-specific permissions."""

    USERS_VIEW = "admin.users.view"
    USERS_MANAGE = "admin.users.manage"
    ROLES_VIEW = "admin.roles.view"
    ROLES_MANAGE = "admin.roles.manage"
    PARSER_VIEW = "admin.parser.view"
    PARSER_MANAGE = "admin.parser.manage"
