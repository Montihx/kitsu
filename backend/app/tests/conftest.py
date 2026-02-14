import os
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "x" * 32)
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/kitsu")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

import app.main as app_main


@asynccontextmanager
async def _test_lifespan(_app):
    yield


@pytest.fixture
def api_client() -> TestClient:
    original_lifespan = app_main.app.router.lifespan_context
    original_db_check = app_main.check_database_connection

    async def _ok_db_check(*args, **kwargs):
        return None

    app_main.app.router.lifespan_context = _test_lifespan
    app_main.check_database_connection = _ok_db_check
    try:
        with TestClient(app_main.app) as client:
            yield client
    finally:
        app_main.app.router.lifespan_context = original_lifespan
        app_main.check_database_connection = original_db_check
