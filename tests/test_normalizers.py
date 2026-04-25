from bangla_news_scraper.normalizers import normalize_text


def test_normalize_text_none():
    assert normalize_text(None) == ""


def test_normalize_text_empty():
    assert normalize_text("") == ""


def test_normalize_text_strips_whitespace():
    assert normalize_text("  hello   world  ") == "hello world"


def test_normalize_text_list_returns_empty():
    assert normalize_text(["not", "a", "string"]) == ""


def test_normalize_text_int_returns_empty():
    assert normalize_text(42) == ""
