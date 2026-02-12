from fastapi import APIRouter, Depends, Query

from ..auth.enforcement_matrix import require_enforced_permission
from ..dependencies import (
    get_current_user,
    get_watch_progress_port,
    get_watch_progress_port_factory,
)
from ..models.user import User
from ..schemas.watch import WatchProgressRead, WatchProgressUpdate
from ..use_cases.watch import get_continue_watching, update_progress

router = APIRouter(prefix="/watch", tags=["watch"])


@router.post("/progress", response_model=WatchProgressRead)
async def upsert_progress(
    payload: WatchProgressUpdate,
    watch_repo=Depends(get_watch_progress_port),
    watch_repo_factory=Depends(get_watch_progress_port_factory),
    current_user: User = Depends(get_current_user),
    _=Depends(require_enforced_permission("POST", "/watch/progress")),
) -> WatchProgressRead:
    return await update_progress(
        watch_repo,
        user_id=current_user.id,
        anime_id=payload.anime_id,
        episode=payload.episode,
        position_seconds=payload.position_seconds,
        progress_percent=payload.progress_percent,
        watch_repo_factory=watch_repo_factory,
    )


@router.get("/continue", response_model=list[WatchProgressRead])
async def continue_watching(
    limit: int = Query(20, ge=1, le=100),
    watch_repo=Depends(get_watch_progress_port),
    current_user: User = Depends(get_current_user),
) -> list[WatchProgressRead]:
    return await get_continue_watching(watch_repo, user_id=current_user.id, limit=limit)
