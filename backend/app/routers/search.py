from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.anime import search_anime
from ..dependencies import get_db
from ..schemas.anime import AnimeListItem

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/anime", response_model=list[AnimeListItem])
async def search_anime_endpoint(
    q: str | None = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[AnimeListItem]:
    if q is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' is required",
        )
    if len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' must be at least 2 characters long",
        )

    return await search_anime(db, query=q, limit=limit, offset=offset)
