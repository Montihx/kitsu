from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
import httpx

from app.parser import schedule as schedule_parser

from .common import SRC_AJAX_URL, SRC_BASE_URL, get_client

router = APIRouter(tags=["Schedule"])


@router.get("/home")
async def home() -> dict[str, Any]:
    # Home endpoint is not critical for current UI flows.
    return {"data": {}}


@router.get("/schedule")
async def schedule(date: Optional[str] = Query(None)) -> dict[str, Any]:
    target_date = date or datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    try:
        async with await get_client() as client:
            resp = await client.get(
                f"{SRC_AJAX_URL}/schedule/list",
                params={"tzOffset": -330, "date": target_date},
                headers={
                    "Accept": "*/*",
                    "Referer": SRC_BASE_URL,
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            resp.raise_for_status()
            html = resp.json().get("html", "")
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        if 500 <= status_code < 600:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Upstream schedule service failed",
            ) from exc
        raise HTTPException(
            status_code=status_code,
            detail="Upstream schedule request was rejected",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reach upstream schedule service",
        ) from exc

    data = schedule_parser.parse_schedule_html(html, target_date)
    return {"data": data}
