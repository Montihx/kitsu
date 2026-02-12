from dataclasses import dataclass
from logging import getLogger

from sqlalchemy import column, select, table, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

logger = getLogger(__name__)

POSTGRES_BACKEND = "postgresql"
ALEMBIC_VERSION_TABLE = "alembic_version"
ALEMBIC_VERSION_COLUMN = "version_num"
ALEMBIC_VERSION = table(ALEMBIC_VERSION_TABLE, column(ALEMBIC_VERSION_COLUMN))
USERS_TABLE = table("users")


@dataclass
class DatabaseStatus:
    database: str | None
    schema: str | None
    alembic_revision: str | None


async def check_database_connection(
    engine: AsyncEngine, *, include_metadata: bool = False
) -> DatabaseStatus:
    """Check database connectivity and the presence of the users table.

    Raises:
        SQLAlchemyError: when the database is unreachable or the probe query fails.
    """
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
        await connection.execute(select(1).select_from(USERS_TABLE).limit(1))

        database = schema = revision = None
        metadata_available = include_metadata and engine.url.get_backend_name() == POSTGRES_BACKEND
        if metadata_available:
            try:
                database = await connection.scalar(text("SELECT current_database()"))
                schema = await connection.scalar(text("SELECT current_schema()"))
            except SQLAlchemyError as exc:
                logger.debug("Database metadata not available: %s", exc)
            try:
                revision = await connection.scalar(select(ALEMBIC_VERSION.c.version_num))
            except SQLAlchemyError as exc:  # Alembic table might be missing
                logger.debug("Alembic revision not available: %s", exc)

    return DatabaseStatus(database=database, schema=schema, alembic_revision=revision)
