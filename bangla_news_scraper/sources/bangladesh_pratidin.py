import logging
from collections.abc import Iterator

from bs4 import BeautifulSoup
from requests import RequestException

from bangla_news_scraper.http import build_session
from bangla_news_scraper.models import ArticleRecord, ScrapeConfig
from bangla_news_scraper.normalizers import normalize_text
from bangla_news_scraper.sources.base import SourceScraper
from bangla_news_scraper.sources.sitemap import fetch_sitemap_urls

log = logging.getLogger(__name__)


def _parse_bd_pratidin_article(url: str, html: str) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    headline = normalize_text(h1.get_text(" ", strip=True)) if h1 else ""
    if not headline:
        return None
    meta_pub = soup.find("meta", attrs={"property": "article:published_time"})
    date_pub = ""
    if meta_pub:
        date_pub = meta_pub.get("content", "")
    article_tag = soup.find("article")
    if article_tag is None:
        article_tag = soup.select_one("div.detailsArea")
    if article_tag is None:
        return None
    paragraphs = article_tag.find_all("p")
    if paragraphs:
        body = normalize_text(" ".join(p.get_text(" ", strip=True) for p in paragraphs))
    else:
        body = normalize_text(article_tag.get_text(" ", strip=True))
    if not body:
        return None
    return ArticleRecord(
        source="bangladesh-pratidin",
        url=url,
        date_published=date_pub or "",
        headline=headline,
        article_body=body,
    )


class BangladeshPratidinScraper(SourceScraper):
    source_name = "bangladesh-pratidin"

    SITEMAP_TEMPLATE = "https://www.bd-pratidin.com/daily-sitemap/{date}/sitemap.xml"

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
            record = _parse_bd_pratidin_article(url, resp.text)
            if record is None:
                continue
            yield record
            total += 1
            if total >= config.max_articles:
                return
