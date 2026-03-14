import pytest
from src.formatter import TextFormatter


@pytest.fixture
def formatter():
    return TextFormatter()


def test_capitalize_words(formatter):
    assert formatter.capitalize_words("hello world") == "Hello World"
    assert formatter.capitalize_words("foo bar baz") == "Foo Bar Baz"


def test_truncate_short_text(formatter):
    assert formatter.truncate("hi", 10) == "hi"


def test_truncate_length(formatter):
    result = formatter.truncate("hello world foo bar", 10)
    assert len(result) <= 10
    assert result.endswith("...")
