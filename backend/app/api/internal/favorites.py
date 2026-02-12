from fastapi import APIRouter

from ...routers import favorites as base_favorites

router = APIRouter()
router.include_router(base_favorites.router)
