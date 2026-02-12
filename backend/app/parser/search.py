from typing import Any

from bs4 import BeautifulSoup


def parse_search_suggestions(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    suggestions = []
    for item in soup.select(".nav-item"):
        link = item.get("href", "")
        if "javascript" in link:
            continue
        suggestions.append(
            {
                "id": link.split("?")[0].lstrip("/"),
                "name": (item.select_one(".film-name") or {}).get_text(strip=True),
                "jname": (item.select_one(".film-name") or {}).get("data-jname"),
                "poster": (item.select_one(".film-poster-img") or {}).get("data-src"),
                "moreInfo": [
                    text.strip() for text in item.select_one(".film-infor").stripped_strings
                ]
                if item.select_one(".film-infor")
                else [],
            }
        )
    return {"suggestions": suggestions}
