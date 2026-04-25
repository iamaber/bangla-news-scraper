from datetime import date

from bangla_news_scraper.date_utils import date_range


def test_date_range_single_day():
    result = date_range(date(2024, 1, 1), date(2024, 1, 1))
    assert result == [date(2024, 1, 1)]


def test_date_range_multiple_days():
    result = date_range(date(2024, 1, 1), date(2024, 1, 3))
    assert result == [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]


def test_date_range_inverted_returns_empty():
    result = date_range(date(2024, 1, 5), date(2024, 1, 1))
    assert result == []
