import json

from bs4 import BeautifulSoup


def extract_jsonld_article(soup: BeautifulSoup) -> dict | None:
    for tag in soup.find_all("script", type="application/ld+json"):
        text = (tag.string or tag.get_text()).strip()
        if not text:
            continue
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") in (
                "NewsArticle",
                "Article",
            ):
                return item
    return None
