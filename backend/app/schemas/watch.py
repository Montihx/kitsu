from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WatchProgressUpdate(BaseModel):
    anime_id: UUID
    episode: int
    position_seconds: int | None = None
    progress_percent: float | None = None


class WatchProgressRead(BaseModel):
    id: UUID
    anime_id: UUID
    episode: int
    position_seconds: int | None
    progress_percent: float | None
    created_at: datetime
    last_watched_at: datetime

    model_config = ConfigDict(from_attributes=True)
