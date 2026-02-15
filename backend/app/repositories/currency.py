from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency, ExchangeRate
from app.repositories.base import BaseRepository


class CurrencyRepository(BaseRepository[Currency]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Currency, session)

    async def get_all(self) -> list[Currency]:
        result = await self.session.execute(select(Currency).order_by(Currency.code))
        return list(result.scalars().all())


class ExchangeRateRepository(BaseRepository[ExchangeRate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ExchangeRate, session)

    async def get_latest(self, base: str, target: str) -> ExchangeRate | None:
        result = await self.session.execute(
            select(ExchangeRate)
            .where(
                ExchangeRate.base_currency == base,
                ExchangeRate.target_currency == target,
            )
            .order_by(ExchangeRate.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_all(self, base: str) -> list[ExchangeRate]:
        """Get the most recent rate for each target currency from this base."""
        from sqlalchemy import func

        subq = (
            select(
                ExchangeRate.target_currency,
                func.max(ExchangeRate.date).label("max_date"),
            )
            .where(ExchangeRate.base_currency == base)
            .group_by(ExchangeRate.target_currency)
            .subquery()
        )
        result = await self.session.execute(
            select(ExchangeRate).join(
                subq,
                (ExchangeRate.target_currency == subq.c.target_currency)
                & (ExchangeRate.date == subq.c.max_date)
                & (ExchangeRate.base_currency == base),
            )
        )
        return list(result.scalars().all())

    async def get_for_date_range(
        self, base: str, from_date: date, to_date: date
    ) -> list[ExchangeRate]:
        result = await self.session.execute(
            select(ExchangeRate).where(
                ExchangeRate.base_currency == base,
                ExchangeRate.date >= from_date,
                ExchangeRate.date <= to_date,
            ).order_by(ExchangeRate.date)
        )
        return list(result.scalars().all())
