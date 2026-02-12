from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status

from .search import fetch_search_suggestions

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("/{provider}")
async def import_provider(provider: str, payload: dict[str, Any]) -> dict[str, Any]:
    if provider != "anilist":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid provider"
        )

    anime_list = payload.get("animes") or []
    if not anime_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No anime list provided"
        )

    status_map = {
        "CURRENT": "watching",
        "COMPLETED": "completed",
        "PLANNING": "plan to watch",
        "DROPPED": "dropped",
        "PAUSED": "on hold",
        "REPEATING": "watching",
    }

    mapped = []
    for item in anime_list:
        entries = item.get("entries") or []
        for entry in entries:
            media = entry.get("media") or {}
            title_obj = media.get("title") or {}
            english_title = title_obj.get("english")
            if not english_title:
                continue
            try:
                suggestions = await fetch_search_suggestions(english_title)
            except httpx.HTTPStatusError as exc:
                upstream_status = exc.response.status_code
                if 500 <= upstream_status < 600:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Upstream service failed",
                    ) from exc
                raise HTTPException(
                    status_code=upstream_status,
                    detail="Upstream request was rejected",
                ) from exc
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to contact upstream service",
                ) from exc
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to parse upstream response",
                ) from exc
            suggestions_list = suggestions.get("suggestions") or []
            if not suggestions_list:
                continue
            first = suggestions_list[0]
            mapped.append(
                {
                    "id": first.get("id"),
                    "thumbnail": first.get("poster"),
                    "title": first.get("name"),
                    "status": status_map.get(item.get("status"), "watching"),
                }
            )

    return {"animes": mapped}
