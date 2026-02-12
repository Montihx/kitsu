import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.release import Release


async def get_releases(
    session: AsyncSession, limit: int, offset: int
) -> list[Release]:
    stmt = (
        select(Release)
        .order_by(Release.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_release_by_id(
    session: AsyncSession, release_id: uuid.UUID
) -> Release | None:
    return await session.get(Release, release_id)
