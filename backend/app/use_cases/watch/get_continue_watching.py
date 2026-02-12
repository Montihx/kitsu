import uuid

from ...domain.ports.watch_progress import WatchProgressData, WatchProgressRepository


async def get_continue_watching(
    watch_repo: WatchProgressRepository, user_id: uuid.UUID, limit: int
) -> list[WatchProgressData]:
    return await watch_repo.list(user_id=user_id, limit=limit)
