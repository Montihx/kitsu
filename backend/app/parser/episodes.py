from typing import Any, Optional

from bs4 import BeautifulSoup

from .common import parse_sync_ids, safe_int


def parse_server_html(
    html: str, category: str, preferred: Optional[str]
) -> tuple[Optional[int], dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    episode_no_el = soup.select_one(".server-notice strong")
    episode_text = episode_no_el.get_text(strip=True) if episode_no_el else ""
    parts = episode_text.split(" ") if episode_text else []
    episode_no = next(reversed(parts), "")
    result = {
        "episodeId": "",
        "episodeNo": episode_no,
        "sub": [],
        "dub": [],
        "raw": [],
    }
    mapping = [
        ("servers-sub", "sub"),
        ("servers-dub", "dub"),
        ("servers-raw", "raw"),
    ]
    for cls, key in mapping:
        container = soup.select_one(f".ps_-block.{cls} .ps__-list") or soup.select_one(
            f".ps_-block.{cls}"
        )
        if not container:
            continue
        for item in container.select(".server-item"):
            server_id = safe_int(item.get("data-server-id"))
            server_name = (item.get_text() or "").strip().lower()
            result[key].append({"serverId": server_id, "serverName": server_name})

    target_list = result.get(category, []) or result.get("sub", [])
    chosen_id = None
    if preferred:
        preferred_lower = preferred.lower()
        for srv in target_list:
            if srv["serverName"] == preferred_lower:
                chosen_id = srv["serverId"]
                break
    if chosen_id is None and target_list:
        chosen_id = target_list[0]["serverId"]
    return chosen_id, result


def build_sources_payload(
    source_link: Optional[str], watch_page_html: str, referer: str
) -> dict[str, Any]:
    ids = parse_sync_ids(watch_page_html)
    return {
        "headers": {"Referer": referer},
        "tracks": [],
        "intro": {"start": 0, "end": 0},
        "outro": {"start": 0, "end": 0},
        "sources": [{"url": source_link, "type": "iframe"}] if source_link else [],
        "anilistID": ids["anilistID"],
        "malID": ids["malID"],
    }
