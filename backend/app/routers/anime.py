from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.anime import get_anime_by_id, get_anime_list
from ..dependencies import get_db
from ..schemas.anime import AnimeListItem, AnimeRead

router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("/", response_model=list[AnimeListItem])
async def list_anime(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[AnimeListItem]:
    return await get_anime_list(db, limit=limit, offset=offset)


@router.get("/{anime_id}", response_model=AnimeRead)
async def get_anime(anime_id: UUID, db: AsyncSession = Depends(get_db)) -> AnimeRead:
    anime = await get_anime_by_id(db, anime_id)
    if anime is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found"
        )
    return anime
