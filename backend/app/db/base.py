"""SQLAlchemy metadata export for Alembic autogenerate."""

from app.models.base import Base

# Ensure model modules are imported so metadata is populated.
from app.models import (  # noqa: F401
    anime,
    audit_log,
    episode,
    favorite,
    permission,
    refresh_token,
    release,
    role,
    role_permission,
    user,
    user_role,
    watch_progress,
)

metadata = Base.metadata
