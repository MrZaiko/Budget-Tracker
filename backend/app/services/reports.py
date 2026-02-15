import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.currency import ExchangeRateRepository
from app.repositories.reports import ReportsRepository
from app.schemas.reports import (
    AccountBalance,
    IncomeVsExpensePeriod,
    IncomeVsExpenseResponse,
    MonthlyTrend,
    NetWorthResponse,
    SpendingByCategory,
    SpendingReportResponse,
    TrendsReportResponse,
)
from app.utils.currency import convert


class ReportsService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ReportsRepository(session)
        self.rate_repo = ExchangeRateRepository(session)

    async def spending_report(
        self, user_id: uuid.UUID, from_date: date, to_date: date, currency: str
    ) -> SpendingReportResponse:
        rows = await self.repo.spending_by_category(user_id, from_date, to_date)
        total = sum(r["amount"] for r in rows)
        categories = []
        for row in rows:
            pct = (row["amount"] / total * 100) if total else Decimal("0")
            categories.append(
                SpendingByCategory(
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    amount=row["amount"],
                    percentage=pct,
                )
            )
        return SpendingReportResponse(
            from_date=from_date,
            to_date=to_date,
            currency=currency,
            total=total,
            categories=categories,
        )

    async def income_vs_expenses(
        self, user_id: uuid.UUID, from_date: date, to_date: date, currency: str
    ) -> IncomeVsExpenseResponse:
        rows = await self.repo.income_vs_expenses(user_id, from_date, to_date)
        periods = [
            IncomeVsExpensePeriod(
                period=r["period"],
                income=r["income"],
                expenses=r["expenses"],
                net=r["net"],
            )
            for r in rows
        ]
        total_income = sum(p.income for p in periods)
        total_expenses = sum(p.expenses for p in periods)
        return IncomeVsExpenseResponse(
            from_date=from_date,
            to_date=to_date,
            currency=currency,
            periods=periods,
            total_income=total_income,
            total_expenses=total_expenses,
            total_net=total_income - total_expenses,
        )

    async def trends_report(
        self, user_id: uuid.UUID, months: int, currency: str
    ) -> TrendsReportResponse:
        rows = await self.repo.monthly_trends(user_id, months)
        trends = [
            MonthlyTrend(
                month=r["period"],
                income=r["income"],
                expenses=r["expenses"],
                net=r["net"],
            )
            for r in rows
        ]
        return TrendsReportResponse(months=months, currency=currency, trends=trends)

    async def net_worth(self, user_id: uuid.UUID, currency: str) -> NetWorthResponse:
        from datetime import date as date_type

        balances_raw = await self.repo.account_balances(user_id)
        accounts = []
        total_assets = Decimal("0")
        total_liabilities = Decimal("0")

        for row in balances_raw:
            rate = await self.rate_repo.get_latest(row["currency"], currency)
            rate_val = Decimal(str(rate.rate)) if rate else Decimal("1")
            balance_base = row["balance"] * rate_val

            accounts.append(
                AccountBalance(
                    account_id=row["account_id"],
                    account_name=row["account_name"],
                    account_type=row["account_type"],
                    currency=row["currency"],
                    balance=row["balance"],
                    balance_base=balance_base,
                )
            )
            if balance_base >= 0:
                total_assets += balance_base
            else:
                total_liabilities += balance_base

        return NetWorthResponse(
            currency=currency,
            date=date_type.today(),
            accounts=accounts,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=total_assets + total_liabilities,
        )
