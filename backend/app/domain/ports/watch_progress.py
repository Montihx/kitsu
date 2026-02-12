from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import uuid
from typing import AsyncContextManager, Protocol


class WatchProgressData(Protocol):
    id: uuid.UUID
    user_id: uuid.UUID
    anime_id: uuid.UUID
    episode: int
    position_seconds: int | None
    progress_percent: float | None
    created_at: datetime
    last_watched_at: datetime


class WatchProgressRepository(Protocol):
    async def anime_exists(self, anime_id: uuid.UUID) -> bool:
        ...

    async def get(
        self, user_id: uuid.UUID, anime_id: uuid.UUID
    ) -> WatchProgressData | None:
        ...

    async def list(self, user_id: uuid.UUID, limit: int) -> list[WatchProgressData]:
        ...

    async def add(
        self,
        user_id: uuid.UUID,
        anime_id: uuid.UUID,
        episode: int,
        position_seconds: int | None,
        progress_percent: float | None,
        *,
        progress_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        last_watched_at: datetime | None = None,
    ) -> WatchProgressData:
        ...

    async def update(
        self,
        progress: WatchProgressData,
        episode: int,
        position_seconds: int | None,
        progress_percent: float | None,
        *,
        last_watched_at: datetime | None = None,
    ) -> WatchProgressData:
        ...


WatchProgressRepositoryFactory = Callable[
    [], AsyncContextManager[WatchProgressRepository]
]
