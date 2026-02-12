import uuid

from ...domain.ports.favorite import FavoriteData, FavoriteRepository


async def get_favorites(
    favorite_repo: FavoriteRepository, user_id: uuid.UUID, limit: int, offset: int
) -> list[FavoriteData]:
    return await favorite_repo.list(user_id=user_id, limit=limit, offset=offset)
