from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status

from app.parser import anime as anime_parser

from .common import SRC_AJAX_URL, SRC_BASE_URL, get_client

router = APIRouter(prefix="/anime", tags=["Anime"])


async def _fetch_episodes(anime_id: str) -> dict[str, Any]:
    episode_key = anime_id.split("-")[-1]
    try:
        async with await get_client() as client:
            resp = await client.get(
                f"{SRC_AJAX_URL}/v2/episode/list/{episode_key}",
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{SRC_BASE_URL}/watch/{anime_id}",
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

    return anime_parser.parse_episodes_html(html)


@router.get("/{anime_id}")
async def anime_info(anime_id: str) -> dict[str, Any]:
    try:
        async with await get_client() as client:
            resp = await client.get(f"{SRC_BASE_URL}/{anime_id.lstrip('/')}")
            resp.raise_for_status()
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

    data = anime_parser.parse_anime_page(resp.text, anime_id)
    return {"data": data}


@router.get("/{anime_id}/episodes")
async def anime_episodes(anime_id: str) -> dict[str, Any]:
    data = await _fetch_episodes(anime_id)
    return {"data": data}
