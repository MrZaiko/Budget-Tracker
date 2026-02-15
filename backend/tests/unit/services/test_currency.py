"""Unit tests for currency utilities."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.utils.currency import convert, get_rate_or_1


@pytest.mark.asyncio
async def test_get_rate_same_currency():
    """Returns 1.0 when currencies are the same."""
    mock_repo = AsyncMock()
    rate = await get_rate_or_1(mock_repo, "USD", "USD")
    assert rate == Decimal("1")
    mock_repo.get_latest.assert_not_called()


@pytest.mark.asyncio
async def test_get_rate_found():
    """Returns the rate from repo when available."""
    mock_rate = MagicMock()
    mock_rate.rate = 1.085

    mock_repo = AsyncMock()
    mock_repo.get_latest.return_value = mock_rate

    rate = await get_rate_or_1(mock_repo, "USD", "EUR")
    assert rate == Decimal("1.085")


@pytest.mark.asyncio
async def test_get_rate_not_found_returns_1():
    """Returns 1.0 as fallback when rate not found."""
    mock_repo = AsyncMock()
    mock_repo.get_latest.return_value = None

    rate = await get_rate_or_1(mock_repo, "USD", "XYZ")
    assert rate == Decimal("1")


@pytest.mark.asyncio
async def test_convert():
    """Convert uses get_rate_or_1 correctly."""
    mock_rate = MagicMock()
    mock_rate.rate = 2.0

    mock_repo = AsyncMock()
    mock_repo.get_latest.return_value = mock_rate

    result = await convert(Decimal("100"), "USD", "GBP", mock_repo)
    assert result == Decimal("200.0")
