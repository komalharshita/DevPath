"""Shared helpers for parsing and clamping pagination query parameters.

Pagination values come straight from the query string and are used in
arithmetic (division, slicing) before any bounds check.  That let
``GET /explore?per_page=0`` raise a ``ZeroDivisionError`` (HTTP 500).
Centralizing parsing/clamping here keeps every paginated route (``/explore``,
``/admin``, future routes) behaving identically and never throwing on
malformed input.
"""

DEFAULT_PER_PAGE = 12
MAX_PER_PAGE = 100


def parse_pagination(page, per_page):
    """Clamp raw ``page``/``per_page`` values into a safe ``(page, per_page)``.

    Args:
        page: raw ``page`` query parameter (``int`` or ``None``).
        per_page: raw ``per_page`` query parameter (``int`` or ``None``).

    Returns:
        A tuple ``(page, per_page)`` where ``page >= 1`` and
        ``1 <= per_page <= MAX_PER_PAGE``.  Values that are missing,
        zero, negative, or unreasonably large are replaced with a sensible
        default or clamped to the nearest valid value.
    """
    if per_page is None:
        per_page = DEFAULT_PER_PAGE
    else:
        per_page = max(1, min(per_page, MAX_PER_PAGE))

    if page is None:
        page = 1
    else:
        page = max(page, 1)

    return page, per_page
