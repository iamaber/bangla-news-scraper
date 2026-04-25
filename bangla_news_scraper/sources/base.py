from abc import ABC, abstractmethod
from collections.abc import Iterator

from bangla_news_scraper.models import ArticleRecord, ScrapeConfig, SourceName


class SourceScraper(ABC):
    source_name: SourceName

    @abstractmethod
    def scrape(self, config: ScrapeConfig) -> Iterator[ArticleRecord]:
        raise NotImplementedError
