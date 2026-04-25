from datetime import date

import pytest

from bangla_news_scraper.models import ScrapeConfig


def test_valid_config():
    cfg = ScrapeConfig(start_date=date(2024, 1, 1), end_date=date(2024, 1, 5))
    assert cfg.max_articles == 100


def test_end_before_start_raises():
    with pytest.raises(ValueError, match="end_date"):
        ScrapeConfig(
            start_date=date(2024, 1, 10),
            end_date=date(2024, 1, 1),
        )


def test_zero_max_articles_raises():
    with pytest.raises(ValueError, match="max_articles"):
        ScrapeConfig(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
            max_articles=0,
        )
