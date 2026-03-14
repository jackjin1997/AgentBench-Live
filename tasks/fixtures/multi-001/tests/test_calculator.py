import pytest
from src.calculator import Calculator


@pytest.fixture
def calc():
    return Calculator()


def test_add(calc):
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0


def test_subtract(calc):
    assert calc.subtract(10, 4) == 6
    assert calc.subtract(0, 5) == -5


def test_multiply(calc):
    assert calc.multiply(3, 4) == 12
    assert calc.multiply(-2, 3) == -6


def test_divide_float(calc):
    assert calc.divide(7, 2) == 3.5
    assert calc.divide(1, 4) == 0.25


def test_divide_by_zero(calc):
    with pytest.raises(ValueError):
        calc.divide(5, 0)
