"""Simple list paginator."""


def paginate(items: list, page: int = 1, per_page: int = 10) -> dict:
    """Return a page of items from the list.

    Args:
        items: The full list of items.
        page: Page number (1-indexed).
        per_page: Number of items per page.

    Returns:
        Dict with 'items', 'page', 'per_page', 'total', 'total_pages'.
    """
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    # BUG: offset calculation doesn't account for 1-indexed pages
    start = page * per_page
    end = start + per_page

    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
