"""Tests for the paginator module."""

from paginator import paginate


def test_first_page():
    items = list(range(1, 26))  # 1-25
    result = paginate(items, page=1, per_page=10)
    assert result["items"] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert result["page"] == 1
    assert result["total"] == 25
    assert result["total_pages"] == 3


def test_second_page():
    items = list(range(1, 26))
    result = paginate(items, page=2, per_page=10)
    assert result["items"] == [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    assert result["page"] == 2


def test_last_page_partial():
    items = list(range(1, 26))
    result = paginate(items, page=3, per_page=10)
    assert result["items"] == [21, 22, 23, 24, 25]
    assert result["page"] == 3


def test_single_page():
    items = [1, 2, 3]
    result = paginate(items, page=1, per_page=10)
    assert result["items"] == [1, 2, 3]
    assert result["total_pages"] == 1


def test_empty_list():
    result = paginate([], page=1, per_page=10)
    assert result["items"] == []
    assert result["total"] == 0


def test_page_beyond_range():
    items = list(range(1, 11))
    result = paginate(items, page=5, per_page=10)
    assert result["page"] == 1  # clamped to last valid page
    assert result["items"] == items
