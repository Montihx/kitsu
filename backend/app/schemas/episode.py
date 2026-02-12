from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EpisodeRead(BaseModel):
    id: UUID
    release_id: UUID
    number: int
    title: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EpisodeListItem(BaseModel):
    id: UUID
    number: int
    title: str | None = None

    model_config = ConfigDict(from_attributes=True)
