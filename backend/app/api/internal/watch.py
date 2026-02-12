from fastapi import APIRouter

from ...routers import watch as base_watch

router = APIRouter()
router.include_router(base_watch.router)
