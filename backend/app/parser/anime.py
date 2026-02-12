from typing import Any

from bs4 import BeautifulSoup

from .common import parse_sync_ids, safe_int


def parse_anime_page(html: str, anime_id: str) -> dict[str, Any]:
    ids = parse_sync_ids(html)
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(".film-name.dynamic-name") or soup.select_one("title")
    poster_el = soup.select_one(".film-poster-img")
    description_el = soup.select_one(".film-description .text")
    return {
        "id": anime_id,
        "title": title_el.text.strip() if title_el else anime_id,
        "poster": poster_el.get("src") if poster_el else None,
        "description": description_el.text.strip() if description_el else "",
        "anilistID": ids["anilistID"],
        "malID": ids["malID"],
    }


def parse_episodes_html(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    episodes = []
    for link in soup.select(".detail-infor-content .ss-list a"):
        episodes.append(
            {
                "title": link.get("title"),
                "episodeId": (link.get("href") or "").split("/")[-1],
                "number": safe_int(link.get("data-number")) or 0,
                "isFiller": "ssl-item-filler" in link.get("class", []),
            }
        )
    return {"totalEpisodes": len(episodes), "episodes": episodes}
