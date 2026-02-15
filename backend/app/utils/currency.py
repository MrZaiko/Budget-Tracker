from decimal import Decimal

from app.repositories.currency import ExchangeRateRepository


async def get_rate_or_1(
    repo: ExchangeRateRepository, from_currency: str, to_currency: str
) -> Decimal:
    """Return the latest exchange rate, or 1.0 if same currency or not found."""
    if from_currency == to_currency:
        return Decimal("1")
    rate = await repo.get_latest(from_currency, to_currency)
    if rate:
        return Decimal(str(rate.rate))
    return Decimal("1")


async def convert(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    repo: ExchangeRateRepository,
) -> Decimal:
    """Convert amount from one currency to another using latest rate."""
    rate = await get_rate_or_1(repo, from_currency, to_currency)
    return amount * rate
