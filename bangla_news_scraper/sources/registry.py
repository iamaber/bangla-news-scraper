from bangla_news_scraper.errors import SourceNotSupportedError
from bangla_news_scraper.models import SOURCE_NAMES, SourceName
from bangla_news_scraper.sources.base import SourceScraper
from bangla_news_scraper.sources.bangladesh_pratidin import BangladeshPratidinScraper
from bangla_news_scraper.sources.jugantor import JugantorScraper
from bangla_news_scraper.sources.prothomalo import ProthomAloScraper
from bangla_news_scraper.sources.samakal import SamakalScraper


def create_scraper(source: SourceName) -> SourceScraper:
    if source == "bangladesh-pratidin":
        return BangladeshPratidinScraper()
    if source == "prothomalo":
        return ProthomAloScraper()
    if source == "jugantor":
        return JugantorScraper()
    if source == "samakal":
        return SamakalScraper()
    raise SourceNotSupportedError(f"Unsupported source: {source}")


def available_sources() -> tuple[SourceName, ...]:
    return SOURCE_NAMES
