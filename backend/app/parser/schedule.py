from datetime import datetime
from typing import Any, Optional

from bs4 import BeautifulSoup

from .common import safe_int


def parse_schedule_html(
    html: str, target_date: str, current_time: Optional[datetime] = None
) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    now = current_time or datetime.now()
    for el in soup.select("li"):
        time_el = el.select_one("a .time")
        anime_link = el.select_one("a")
        name_el = el.select_one(".film-name.dynamic-name")
        time_text = time_el.text.strip() if time_el else ""
        episode_button = el.select_one(".fd-play button")
        episode_button_text = episode_button.get_text(strip=True) if episode_button else ""
        airing_ts = None
        seconds_until = None
        if time_text:
            try:
                airing_dt = datetime.fromisoformat(f"{target_date}T{time_text}:00")
                airing_ts = int(airing_dt.timestamp() * 1000)
                seconds_until = int(airing_dt.timestamp() - now.timestamp())
            except ValueError:
                airing_ts = None
                seconds_until = None
        items.append(
            {
                "id": anime_link.get("href", "").lstrip("/") if anime_link else None,
                "time": time_text or None,
                "name": name_el.text.strip() if name_el else None,
                "jname": name_el.get("data-jname") if name_el else None,
                "airingTimestamp": airing_ts or 0,
                "secondsUntilAiring": seconds_until or 0,
                "episode": safe_int(
                    episode_button_text.split(" ")[1]
                    if episode_button_text and " " in episode_button_text
                    else None
                )
                or 0,
            }
        )

    return {"scheduledAnimes": items}
