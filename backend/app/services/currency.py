from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency, ExchangeRate
from app.repositories.currency import CurrencyRepository, ExchangeRateRepository
from app.schemas.currency import HistoricalRatesResponse, LatestRatesResponse
from decimal import Decimal


class CurrencyService:
    def __init__(self, session: AsyncSession) -> None:
        self.currency_repo = CurrencyRepository(session)
        self.rate_repo = ExchangeRateRepository(session)

    async def list_currencies(self) -> list[Currency]:
        return await self.currency_repo.get_all()

    async def get_latest_rates(self, base: str) -> LatestRatesResponse:
        rates = await self.rate_repo.get_latest_all(base)
        rate_date = date.today()
        rate_map: dict[str, Decimal] = {}
        for r in rates:
            if r.date > rate_date or not rate_map:
                rate_date = r.date
            rate_map[r.target_currency] = Decimal(str(r.rate))
        return LatestRatesResponse(base=base, date=rate_date, rates=rate_map)

    async def get_historical_rates(
        self, base: str, from_date: date, to_date: date
    ) -> HistoricalRatesResponse:
        rates = await self.rate_repo.get_for_date_range(base, from_date, to_date)
        grouped: dict[date, dict[str, Decimal]] = {}
        for r in rates:
            if r.date not in grouped:
                grouped[r.date] = {}
            grouped[r.date][r.target_currency] = Decimal(str(r.rate))
        return HistoricalRatesResponse(base=base, rates=grouped)
