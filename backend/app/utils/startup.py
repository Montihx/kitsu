import asyncio
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from .health import check_database_connection
from .migrations import run_migrations

logger = logging.getLogger("kitsu.startup")


async def run_required_startup_checks(engine: AsyncEngine) -> None:
    try:
        db_status = await check_database_connection(engine, include_metadata=True)
    except SQLAlchemyError as exc:
        logger.exception("Database readiness check failed during startup")
        raise RuntimeError(
            "Database not ready. Ensure DATABASE_URL is reachable and migrations are applied (e.g. with 'alembic upgrade head')."
        ) from exc

    logger.info(
        "Database ready (current_database=%s, current_schema=%s, alembic_revision=%s)",
        db_status.database or "unknown",
        db_status.schema or "unknown",
        db_status.alembic_revision or "unavailable",
    )


async def run_optional_startup_tasks() -> None:
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, run_migrations)
    except Exception as exc:  # noqa: BLE001 — optional startup tasks must not crash app
        logger.warning(
            "Migration task failed during optional startup; continuing application startup.",
            exc_info=exc,
        )
