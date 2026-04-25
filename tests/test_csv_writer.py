from pathlib import Path

from bangla_news_scraper.models import ArticleRecord
from bangla_news_scraper.services.csv_writer import write_articles_to_csv


def test_write_articles_to_csv(tmp_path: Path):
    articles = [
        ArticleRecord(
            source="prothomalo",
            url="https://example.com/a",
            date_published="2024-01-01",
            headline="Test Headline",
            article_body="Test body content",
            writer="Writer One",
        ),
    ]
    csv_path = tmp_path / "out.csv"
    count = write_articles_to_csv(csv_path, articles)
    assert count == 1
    assert csv_path.exists()
    text = csv_path.read_text(encoding="utf-8")
    assert "Date Published" in text
    assert "Test Headline" in text
    assert "Test body content" in text


def test_write_empty_list(tmp_path: Path):
    csv_path = tmp_path / "empty.csv"
    count = write_articles_to_csv(csv_path, [])
    assert count == 0
    text = csv_path.read_text(encoding="utf-8")
    assert "Date Published" in text
