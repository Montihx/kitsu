from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter(prefix="/health", tags=["v1-health"])


@router.get("", response_model=ApiResponse[dict[str, str]])
async def health_v1() -> ApiResponse[dict[str, str]]:
    return ApiResponse.ok(data={"status": "ok"})
