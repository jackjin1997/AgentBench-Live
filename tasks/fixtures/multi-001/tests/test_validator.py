import pytest
from src.validator import InputValidator


@pytest.fixture
def validator():
    return InputValidator()


def test_valid_email(validator):
    assert validator.is_email("user@example.com") is True
    assert validator.is_email("a.b+c@foo.org") is True


def test_invalid_email(validator):
    assert validator.is_email("not-an-email") is False
    assert validator.is_email("@missing.com") is False


def test_positive_int(validator):
    assert validator.is_positive_int("5") is True
    assert validator.is_positive_int("100") is True


def test_zero_not_positive(validator):
    assert validator.is_positive_int("0") is False


def test_negative_not_positive(validator):
    assert validator.is_positive_int("-3") is False


def test_non_numeric(validator):
    assert validator.is_positive_int("abc") is False
