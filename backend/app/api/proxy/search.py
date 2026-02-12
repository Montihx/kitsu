from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
import httpx

from app.parser import search as search_parser

from .common import SRC_AJAX_URL, SRC_BASE_URL, get_client

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search() -> dict[str, Any]:
    # The existing UI uses backend search endpoints; keep a placeholder.
    return {"data": []}


async def fetch_search_suggestions(query: str) -> dict[str, Any]:
    try:
        async with await get_client() as client:
            resp = await client.get(
                f"{SRC_AJAX_URL}/search/suggest",
                params={"keyword": query},
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
                detail="Upstream service unavailable",
            ) from exc
        raise HTTPException(
            status_code=status_code, detail="Upstream request was rejected"
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream service unavailable",
        ) from exc
    return search_parser.parse_search_suggestions(html)


@router.get("/suggestion")
async def search_suggestion(q: str = Query(...)) -> dict[str, Any]:
    if not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query"
        )
    data = await fetch_search_suggestions(q.strip())
    return {"data": data}
