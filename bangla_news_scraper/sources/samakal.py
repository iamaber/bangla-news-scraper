import logging
from collections.abc import Iterator

from bs4 import BeautifulSoup
from requests import RequestException

from bangla_news_scraper.http import build_session
from bangla_news_scraper.models import ArticleRecord, ScrapeConfig
from bangla_news_scraper.normalizers import normalize_text
from bangla_news_scraper.sources.base import SourceScraper
from bangla_news_scraper.sources.jsonld import extract_jsonld_article
from bangla_news_scraper.sources.sitemap import fetch_sitemap_urls

log = logging.getLogger(__name__)


def _parse_samakal_article(url: str, html: str) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "html.parser")
    ld = extract_jsonld_article(soup)
    if ld is None:
        return None
    headline = normalize_text(ld.get("headline"))
    body = normalize_text(ld.get("articleBody"))
    if not headline or not body:
        return None
    date_pub = ld.get("datePublished", "")
    author_raw = ld.get("author")
    writer = "Unknown"
    if isinstance(author_raw, dict):
        writer = normalize_text(author_raw.get("name")) or "Unknown"
    elif isinstance(author_raw, str):
        writer = normalize_text(author_raw) or "Unknown"
    return ArticleRecord(
        source="samakal",
        url=url,
        date_published=date_pub or "",
        headline=headline,
        article_body=body,
        writer=writer,
    )


class SamakalScraper(SourceScraper):
    source_name = "samakal"

    SITEMAP_TEMPLATE = "https://samakal.com/sitemap/sitemap-daily-{date}.xml"

    def scrape(self, config: ScrapeConfig) -> Iterator[ArticleRecord]:
        session = build_session()
        headers = {"User-Agent": config.user_agent}
        seen: set[str] = set()
        total = 0
        for url in fetch_sitemap_urls(self.SITEMAP_TEMPLATE, config, session):
            if url in seen:
                continue
            seen.add(url)
            try:
                resp = session.get(url, headers=headers, timeout=config.request_timeout_seconds)
            except RequestException:
                continue
            if resp.status_code >= 400:
                continue
            record = _parse_samakal_article(url, resp.text)
            if record is None:
                continue
            yield record
            total += 1
            if total >= config.max_articles:
                return
