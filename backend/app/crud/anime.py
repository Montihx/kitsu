import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.anime import Anime


async def get_anime_list(
    session: AsyncSession, limit: int, offset: int
) -> list[Anime]:
    stmt = (
        select(Anime)
        .where(Anime.is_deleted.is_(False), Anime.state == "published")
        .order_by(Anime.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_anime_by_id(session: AsyncSession, anime_id: uuid.UUID) -> Anime | None:
    stmt = select(Anime).where(
        Anime.id == anime_id,
        Anime.is_deleted.is_(False),
        Anime.state == "published",
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def search_anime(db: AsyncSession, query: str, limit: int, offset: int) -> list[Anime]:
    pattern = f"%{query}%"
    stmt = (
        select(Anime)
        .where(
            Anime.title.ilike(pattern),
            Anime.is_deleted.is_(False),
            Anime.state == "published",
        )
        .order_by(Anime.title.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
