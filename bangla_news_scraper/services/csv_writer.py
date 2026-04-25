import csv
from pathlib import Path

from bangla_news_scraper.models import ArticleRecord


CSV_HEADERS = ["Date Published", "Headline", "Article Body", "Writer", "URL", "Source"]


def write_articles_to_csv(path: Path, articles: list[ArticleRecord]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)
        for article in articles:
            writer.writerow(
                [
                    article.date_published,
                    article.headline,
                    article.article_body,
                    article.writer,
                    article.url,
                    article.source,
                ]
            )
    return len(articles)
