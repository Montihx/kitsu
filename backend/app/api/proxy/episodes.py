from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from app.parser import episodes as episodes_parser

from .common import SRC_AJAX_URL, SRC_BASE_URL, get_client

router = APIRouter(prefix="/episode", tags=["Episodes"])


@router.get("/servers")
async def episode_servers(animeEpisodeId: str = Query(...)) -> dict[str, Any]:
    episode_id = animeEpisodeId
    if "?ep=" not in episode_id:
        episode_id = f"{episode_id}?ep={episode_id.split('-')[-1]}"
    ep_key = episode_id.split("?ep=")[1]
    try:
        async with await get_client() as client:
            resp = await client.get(
                f"{SRC_AJAX_URL}/v2/episode/servers",
                params={"episodeId": ep_key},
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{SRC_BASE_URL}/watch/{episode_id}",
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
            status_code=status_code,
            detail="Upstream request was rejected",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream service unavailable",
        ) from exc

    _, parsed = episodes_parser.parse_server_html(html, "sub", preferred=None)
    parsed["episodeId"] = episode_id
    return {"data": parsed}


@router.get("/sources")
async def episode_sources(
    animeEpisodeId: str = Query(...),
    server: Optional[str] = Query(None),
    category: str = Query("sub"),
) -> dict[str, Any]:
    episode_id = animeEpisodeId
    if "?ep=" not in episode_id:
        episode_id = f"{episode_id}?ep={episode_id.split('-')[-1]}"
    ep_key = episode_id.split("?ep=")[1]

    try:
        async with await get_client() as client:
            servers_resp = await client.get(
                f"{SRC_AJAX_URL}/v2/episode/servers",
                params={"episodeId": ep_key},
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{SRC_BASE_URL}/watch/{episode_id}",
                },
            )
            servers_resp.raise_for_status()
            servers_html = servers_resp.json().get("html", "")

            server_id, parsed_servers = episodes_parser.parse_server_html(
                servers_html, category or "sub", preferred=server
            )
            if not server_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No server found for requested episode",
                )
            source_resp = await client.get(
                f"{SRC_AJAX_URL}/v2/episode/sources",
                params={"id": server_id},
            )
            source_resp.raise_for_status()
            source_link = source_resp.json().get("link")

            watch_page = await client.get(
                f"{SRC_BASE_URL}/watch/{episode_id.split('?')[0]}",
                headers={"Referer": SRC_BASE_URL},
            )
            watch_page.raise_for_status()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        if 500 <= status_code < 600:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Upstream service unavailable",
            ) from exc
        raise HTTPException(
            status_code=status_code,
            detail="Upstream request was rejected",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream service unavailable",
        ) from exc

    payload = episodes_parser.build_sources_payload(
        source_link, watch_page.text, referer=SRC_BASE_URL
    )
    return {"data": payload}
