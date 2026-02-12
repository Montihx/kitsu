import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.anime import Anime


async def get_anime_list(
    session: AsyncSession, limit: int, offset: int
) -> list[Anime]:
    stmt = (
        select(Anime)
        .order_by(Anime.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_anime_by_id(session: AsyncSession, anime_id: uuid.UUID) -> Anime | None:
    return await session.get(Anime, anime_id)


async def search_anime(db: AsyncSession, query: str, limit: int, offset: int) -> list[Anime]:
    pattern = f"%{query}%"
    stmt = (
        select(Anime)
        .where(Anime.title.ilike(pattern))
        .order_by(Anime.title.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
