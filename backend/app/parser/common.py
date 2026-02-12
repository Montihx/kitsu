import json
from typing import Optional

from bs4 import BeautifulSoup


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
