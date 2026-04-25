import logging
from collections.abc import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import RequestException

from bangla_news_scraper.date_utils import date_range
from bangla_news_scraper.http import build_session
from bangla_news_scraper.models import ArticleRecord, ScrapeConfig
from bangla_news_scraper.normalizers import normalize_text
from bangla_news_scraper.sources.base import SourceScraper
from bangla_news_scraper.sources.jsonld import extract_jsonld_article

log = logging.getLogger(__name__)


def _parse_jugantor_article(url: str, html: str, fallback_date: str) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "html.parser")
    ld = extract_jsonld_article(soup)

    headline = ""
    date_pub = fallback_date
    writer = "Unknown"
    if ld is not None:
        headline = normalize_text(ld.get("headline", ""))
        date_pub = ld.get("datePublished", fallback_date) or fallback_date
        author_raw = ld.get("author")
        if isinstance(author_raw, dict):
            writer = normalize_text(author_raw.get("name")) or "Unknown"

    if not headline:
        h1 = soup.find("h1")
        if h1:
            headline = normalize_text(h1.get_text(" ", strip=True))
    if not headline:
        return None

    body_container = (
        soup.select_one("div.detailBody.innerAdDiv")
        or soup.select_one("div.desktopDetailBody.innerAdDiv")
        or soup.select_one("div.detailBody")
    )
    if body_container is None:
        return None

    paragraphs = body_container.find_all("p")
    if paragraphs:
        body = normalize_text(
            " ".join(p.get_text(" ", strip=True) for p in paragraphs)
        )
    else:
        body = normalize_text(body_container.get_text(" ", strip=True))
    if not body:
        return None

    return ArticleRecord(
        source="jugantor",
        url=url,
        date_published=str(date_pub),
        headline=headline,
        article_body=body,
        writer=writer,
    )


class JugantorScraper(SourceScraper):
    source_name = "jugantor"

    def scrape(self, config: ScrapeConfig) -> Iterator[ArticleRecord]:
        session = build_session()
        headers = {"User-Agent": config.user_agent}
        seen: set[str] = set()
        total = 0

        for current_date in date_range(config.start_date, config.end_date):
            iso_date = current_date.isoformat()
            archive_url = f"https://www.jugantor.com/archive?date={iso_date}"
            try:
                archive_resp = session.get(
                    archive_url,
                    headers=headers,
                    timeout=config.request_timeout_seconds,
                )
            except RequestException:
                continue
            if archive_resp.status_code >= 400:
                continue

            archive_soup = BeautifulSoup(archive_resp.text, "html.parser")
            for link in archive_soup.select("a[href]"):
                href = link.get("href")
                if not href:
                    continue
                article_url = urljoin("https://www.jugantor.com", href)
                if not article_url.startswith("https://www.jugantor.com/"):
                    continue
                parts = article_url.rstrip("/").split("/")
                if len(parts) < 5 or not parts[-1].isdigit():
                    continue
                if article_url in seen:
                    continue
                seen.add(article_url)

                try:
                    art_resp = session.get(
                        article_url,
                        headers=headers,
                        timeout=config.request_timeout_seconds,
                    )
                except RequestException:
                    continue
                if art_resp.status_code >= 400:
                    continue

                record = _parse_jugantor_article(article_url, art_resp.text, iso_date)
                if record is None:
                    continue
                yield record
                total += 1
                if total >= config.max_articles:
                    return
