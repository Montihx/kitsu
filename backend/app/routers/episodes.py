from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.episode import get_episodes_by_release
from ..crud.release import get_release_by_id
from ..dependencies import get_db
from ..schemas.episode import EpisodeListItem

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("/", response_model=list[EpisodeListItem])
async def list_episodes(
    release_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[EpisodeListItem]:
    release = await get_release_by_id(db, release_id)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return await get_episodes_by_release(db, release_id)
