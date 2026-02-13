"""
Kitsu Backend — Test Configuration (S0: minimal).

Sets environment variables BEFORE any app.* import so that
Settings.from_env() picks up test values instead of requiring
a real .env file.

No DB fixtures, no model imports — those belong to future levels.
"""
import os

# ── Environment overrides (BEFORE any app import) ──────────────
# These satisfy Settings.from_env() validation without a .env file.

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://kitsu:kitsu@localhost:5432/kitsu_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-chars-long!")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
