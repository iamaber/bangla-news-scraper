import csv
import os
from collections.abc import Iterable
from pathlib import Path

from bangla_news_scraper.models import ArticleRecord

CSV_HEADERS = ["Date Published", "Headline", "Article Body", "Writer", "URL", "Source"]


def write_articles_to_csv(path: Path, articles: Iterable[ArticleRecord]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    count = 0
    with tmp_path.open("w", newline="", encoding="utf-8") as handle:
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
            count += 1
    os.replace(tmp_path, path)
    return count
