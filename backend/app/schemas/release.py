from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReleaseRead(BaseModel):
    id: UUID
    anime_id: UUID
    title: str
    year: int | None = None
    status: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReleaseListItem(BaseModel):
    id: UUID
    anime_id: UUID
    title: str
    year: int | None = None
    status: str | None = None

    model_config = ConfigDict(from_attributes=True)
