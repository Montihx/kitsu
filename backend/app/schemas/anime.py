from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnimeCreate(BaseModel):
    title: str
    title_original: str | None = None
    description: str | None = None
    year: int | None = None
    status: str | None = None


class AnimeRead(BaseModel):
    id: UUID
    title: str
    title_original: str | None = None
    description: str | None = None
    year: int | None = None
    status: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnimeListItem(BaseModel):
    id: UUID
    title: str
    year: int | None = None
    status: str | None = None

    model_config = ConfigDict(from_attributes=True)
