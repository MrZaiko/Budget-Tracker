"""Unit tests for CurrencyService."""

import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.currency import CurrencyService


def make_exchange_rate(base, target, rate, rate_date=None):
    r = MagicMock()
    r.base_currency = base
    r.target_currency = target
    r.rate = rate
    r.date = rate_date or date.today()
    return r


def make_currency(code, name, symbol):
    c = MagicMock()
    c.code = code
    c.name = name
    c.symbol = symbol
    return c


@pytest.mark.asyncio
async def test_list_currencies():
    session = AsyncMock()
    service = CurrencyService(session)
    service.currency_repo = AsyncMock()
    service.currency_repo.get_all.return_value = [
        make_currency("USD", "US Dollar", "$"),
        make_currency("EUR", "Euro", "€"),
    ]

    result = await service.list_currencies()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_latest_rates_with_data():
    session = AsyncMock()
    service = CurrencyService(session)
    service.rate_repo = AsyncMock()

    today = date.today()
    service.rate_repo.get_latest_all.return_value = [
        make_exchange_rate("USD", "EUR", 0.92, today),
        make_exchange_rate("USD", "GBP", 0.78, today),
    ]

    result = await service.get_latest_rates("USD")
    assert result.base == "USD"
    assert "EUR" in result.rates
    assert "GBP" in result.rates
    assert result.rates["EUR"] == Decimal("0.92")


@pytest.mark.asyncio
async def test_get_latest_rates_empty():
    session = AsyncMock()
    service = CurrencyService(session)
    service.rate_repo = AsyncMock()
    service.rate_repo.get_latest_all.return_value = []

    result = await service.get_latest_rates("USD")
    assert result.base == "USD"
    assert result.rates == {}


@pytest.mark.asyncio
async def test_get_historical_rates():
    session = AsyncMock()
    service = CurrencyService(session)
    service.rate_repo = AsyncMock()

    d1 = date(2024, 1, 1)
    d2 = date(2024, 1, 2)
    service.rate_repo.get_for_date_range.return_value = [
        make_exchange_rate("USD", "EUR", 0.91, d1),
        make_exchange_rate("USD", "EUR", 0.92, d2),
    ]

    result = await service.get_historical_rates("USD", d1, d2)
    assert result.base == "USD"
    assert d1 in result.rates
    assert d2 in result.rates
    assert result.rates[d1]["EUR"] == Decimal("0.91")
    assert result.rates[d2]["EUR"] == Decimal("0.92")


@pytest.mark.asyncio
async def test_get_historical_rates_empty():
    session = AsyncMock()
    service = CurrencyService(session)
    service.rate_repo = AsyncMock()
    service.rate_repo.get_for_date_range.return_value = []

    result = await service.get_historical_rates("USD", date(2024, 1, 1), date(2024, 1, 31))
    assert result.rates == {}
