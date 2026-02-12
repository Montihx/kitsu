from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """
    Generic CRUD interface to be extended per model.
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int) -> ModelType | None:
        return await session.get(self.model, obj_id)

    async def list(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> list[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, obj_in: dict) -> ModelType:
        instance = self.model(**obj_in)
        session.add(instance)
        await session.flush()
        # Committing is left to the caller to allow transactional control.
        return instance
