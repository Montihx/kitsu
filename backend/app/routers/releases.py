from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.release import get_release_by_id, get_releases
from ..dependencies import get_db
from ..schemas.release import ReleaseListItem, ReleaseRead

router = APIRouter(prefix="/releases", tags=["releases"])


@router.get("/", response_model=list[ReleaseListItem])
async def list_releases(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ReleaseListItem]:
    return await get_releases(db, limit=limit, offset=offset)


@router.get("/{release_id}", response_model=ReleaseRead)
async def get_release(
    release_id: UUID, db: AsyncSession = Depends(get_db)
) -> ReleaseRead:
    release = await get_release_by_id(db, release_id)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return release
