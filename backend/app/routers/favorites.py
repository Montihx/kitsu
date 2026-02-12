from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from ..auth.enforcement_matrix import require_enforced_permission
from ..dependencies import (
    get_current_user,
    get_favorite_port,
    get_favorite_port_factory,
)
from ..models.user import User
from ..schemas.favorite import FavoriteCreate, FavoriteRead
from ..use_cases.favorites import (
    add_favorite as add_favorite_use_case,
    get_favorites as get_favorites_use_case,
    remove_favorite as remove_favorite_use_case,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/", response_model=list[FavoriteRead])
async def get_favorites(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    favorite_repo=Depends(get_favorite_port),
    current_user: User = Depends(get_current_user),
) -> list[FavoriteRead]:
    return await get_favorites_use_case(
        favorite_repo, user_id=current_user.id, limit=limit, offset=offset
    )


@router.post("/", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    payload: FavoriteCreate,
    favorite_repo=Depends(get_favorite_port),
    favorite_repo_factory=Depends(get_favorite_port_factory),
    current_user: User = Depends(get_current_user),
    _=Depends(require_enforced_permission("POST", "/favorites")),
) -> FavoriteRead:
    return await add_favorite_use_case(
        favorite_repo,
        user_id=current_user.id,
        anime_id=payload.anime_id,
        favorite_repo_factory=favorite_repo_factory,
    )


@router.delete("/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    anime_id: UUID,
    favorite_repo=Depends(get_favorite_port),
    favorite_repo_factory=Depends(get_favorite_port_factory),
    current_user: User = Depends(get_current_user),
    _=Depends(require_enforced_permission("DELETE", "/favorites/{anime_id}")),
) -> None:
    await remove_favorite_use_case(
        favorite_repo,
        user_id=current_user.id,
        anime_id=anime_id,
        favorite_repo_factory=favorite_repo_factory,
    )
