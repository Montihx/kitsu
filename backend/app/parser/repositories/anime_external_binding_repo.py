from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..tables import anime_external_binding


def _insert_for(session: AsyncSession):
    bind = session.get_bind()
    dialect = bind.dialect.name if bind is not None else "postgresql"
    if dialect == "sqlite":
        return sqlite_insert
    return pg_insert


class AnimeExternalBindingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_external_id(
        self, anime_external_id: int
    ) -> Mapping[str, object] | None:
        result = await self._session.execute(
            select(anime_external_binding).where(
                anime_external_binding.c.anime_external_id == anime_external_id
            )
        )
        return result.mappings().first()

    async def get_by_anime_id(self, anime_id: str) -> Mapping[str, object] | None:
        result = await self._session.execute(
            select(anime_external_binding).where(
                anime_external_binding.c.anime_id == anime_id
            )
        )
        return result.mappings().first()

    async def ensure_binding(
        self, anime_external_id: int, anime_id: str, *, bound_by: str
    ) -> Mapping[str, object]:
        insert_fn = _insert_for(self._session)
        stmt = insert_fn(anime_external_binding).values(
            anime_external_id=anime_external_id,
            anime_id=anime_id,
            bound_by=bound_by,
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["anime_external_id"])
        await self._session.execute(stmt)
        result = await self._session.execute(
            select(anime_external_binding).where(
                anime_external_binding.c.anime_external_id == anime_external_id
            )
        )
        return result.mappings().one()
