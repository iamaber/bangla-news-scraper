import logging
from collections.abc import Iterator
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from requests import RequestException, Session

from bangla_news_scraper.date_utils import date_range
from bangla_news_scraper.http import build_session
from bangla_news_scraper.models import ScrapeConfig

log = logging.getLogger(__name__)

_ALLOWED_SCHEMES = {"https", "http"}


def _validate_url(url: str, allowed_hosts: set[str] | None = None) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False
    if allowed_hosts and parsed.hostname not in allowed_hosts:
        return False
    return True


def fetch_sitemap_urls(
    sitemap_template: str,
    config: ScrapeConfig,
    session: Session | None = None,
    allowed_hosts: set[str] | None = None,
) -> Iterator[str]:
    if session is None:
        session = build_session()
    headers = {"User-Agent": config.user_agent}
    template_host = urlparse(sitemap_template.split("{date}")[0]).hostname
    if allowed_hosts is None and template_host:
        allowed_hosts = {template_host}
    for current_date in date_range(config.start_date, config.end_date):
        sitemap_url = sitemap_template.format(date=current_date.isoformat())
        try:
            response = session.get(
                sitemap_url,
                headers=headers,
                timeout=config.request_timeout_seconds,
            )
        except RequestException:
            log.debug("sitemap request failed: %s", sitemap_url)
            continue
        if response.status_code >= 400:
            log.debug("sitemap status %s: %s", response.status_code, sitemap_url)
            continue
        soup = BeautifulSoup(response.text, "xml")
        for entry in soup.find_all("url"):
            loc = entry.find("loc")
            if loc and loc.text:
                url = loc.text.strip()
                if _validate_url(url, allowed_hosts):
                    yield url
