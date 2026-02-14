"""Backward-compatible DB exports.

Phase 2 keeps public imports stable while moving canonical DB primitives
into `app.db.session`.
"""

from app.db.session import AsyncSessionLocal, engine, get_session

__all__ = ["engine", "AsyncSessionLocal", "get_session"]
