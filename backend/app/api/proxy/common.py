import json
from typing import Optional

import httpx
from bs4 import BeautifulSoup

SRC_BASE_URL = "https://hianimez.to"
SRC_AJAX_URL = f"{SRC_BASE_URL}/ajax"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


async def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=10.0, headers=DEFAULT_HEADERS, follow_redirects=True)


def parse_sync_ids(html: str) -> dict[str, Optional[int]]:
    soup = BeautifulSoup(html, "html.parser")
    sync_el = soup.select_one("#syncData")
    if not sync_el or not sync_el.text:
        return {"anilistID": None, "malID": None}
    try:
        data = json.loads(sync_el.text)
        return {
            "anilistID": data.get("anilist_id"),
            "malID": data.get("mal_id"),
        }
    except (json.JSONDecodeError, AttributeError):
        return {"anilistID": None, "malID": None}


def safe_int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None
