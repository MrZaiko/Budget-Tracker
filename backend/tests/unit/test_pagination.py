"""Unit tests for pagination utility."""

import pytest

from app.utils.pagination import build_paginated_response


def test_paginated_response_single_page():
    items = [1, 2, 3]
    result = build_paginated_response(items, total=3, page=1, page_size=10)
    assert result.items == [1, 2, 3]
    assert result.total == 3
    assert result.page == 1
    assert result.page_size == 10
    assert result.pages == 1


def test_paginated_response_multiple_pages():
    items = list(range(10))
    result = build_paginated_response(items, total=25, page=1, page_size=10)
    assert result.pages == 3


def test_paginated_response_empty():
    result = build_paginated_response([], total=0, page=1, page_size=20)
    assert result.total == 0
    assert result.pages == 0
    assert result.items == []


def test_paginated_response_last_page():
    items = [1]
    result = build_paginated_response(items, total=21, page=3, page_size=10)
    assert result.pages == 3
    assert result.page == 3


def test_paginated_response_zero_page_size():
    result = build_paginated_response([], total=10, page=1, page_size=0)
    assert result.pages == 0
