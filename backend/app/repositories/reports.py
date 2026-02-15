import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction


class ReportsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def spending_by_category(
        self,
        user_id: uuid.UUID,
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        result = await self.session.execute(
            select(
                Transaction.category_id,
                Category.name.label("category_name"),
                func.sum(Transaction.amount_base).label("total"),
            )
            .outerjoin(Category, Category.id == Transaction.category_id)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.date >= from_date,
                Transaction.date <= to_date,
            )
            .group_by(Transaction.category_id, Category.name)
            .order_by(func.sum(Transaction.amount_base).desc())
        )
        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name or "Uncategorized",
                "amount": Decimal(str(row.total)),
            }
            for row in result.all()
        ]

    async def income_vs_expenses(
        self,
        user_id: uuid.UUID,
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        """Return income/expense totals grouped by year-month."""
        result = await self.session.execute(
            select(
                func.extract("year", Transaction.date).label("year"),
                func.extract("month", Transaction.date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount_base).label("total"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.type.in_(["income", "expense"]),
                Transaction.date >= from_date,
                Transaction.date <= to_date,
            )
            .group_by(
                func.extract("year", Transaction.date),
                func.extract("month", Transaction.date),
                Transaction.type,
            )
            .order_by(
                func.extract("year", Transaction.date),
                func.extract("month", Transaction.date),
            )
        )
        rows = result.all()

        periods: dict[str, dict] = {}
        for row in rows:
            year = int(row.year)
            month = int(row.month)
            period_key = f"{year:04d}-{month:02d}"
            if period_key not in periods:
                periods[period_key] = {
                    "period": period_key,
                    "income": Decimal("0"),
                    "expenses": Decimal("0"),
                }
            if row.type == "income":
                periods[period_key]["income"] = Decimal(str(row.total))
            elif row.type == "expense":
                periods[period_key]["expenses"] = Decimal(str(row.total))

        for p in periods.values():
            p["net"] = p["income"] - p["expenses"]

        return list(periods.values())

    async def monthly_trends(
        self,
        user_id: uuid.UUID,
        months: int = 12,
    ) -> list[dict]:
        from datetime import date as date_type
        from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

        today = date_type.today()
        from_date = today - relativedelta(months=months)
        return await self.income_vs_expenses(user_id, from_date, today)

    async def account_balances(
        self,
        user_id: uuid.UUID,
    ) -> list[dict]:
        accounts_result = await self.session.execute(
            select(Account).where(Account.user_id == user_id, Account.is_active.is_(True))
        )
        accounts = list(accounts_result.scalars().all())

        from app.repositories.account import AccountRepository
        account_repo = AccountRepository(self.session)

        balances = []
        for account in accounts:
            balance = await account_repo.compute_balance(account.id)
            balances.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": account.type,
                "currency": account.currency,
                "balance": balance,
            })
        return balances
