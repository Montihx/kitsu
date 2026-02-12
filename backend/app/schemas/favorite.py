from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    anime_id: UUID


class FavoriteRead(BaseModel):
    id: UUID
    anime_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
