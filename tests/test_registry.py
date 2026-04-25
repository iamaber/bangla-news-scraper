from bangla_news_scraper.errors import SourceNotSupportedError
from bangla_news_scraper.sources.registry import available_sources, create_scraper


def test_available_sources_returns_all():
    sources = available_sources()
    assert "prothomalo" in sources
    assert "samakal" in sources
    assert "bangladesh-pratidin" in sources
    assert "jugantor" in sources


def test_create_scraper_unknown_raises():
    try:
        create_scraper("nonexistent-source")
        assert False, "should have raised"
    except SourceNotSupportedError:
        pass


def test_create_scraper_known_sources():
    for name in available_sources():
        scraper = create_scraper(name)
        assert scraper.source_name == name
