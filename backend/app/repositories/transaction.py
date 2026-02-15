import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository
from app.schemas.transaction import TransactionFilters


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    async def get_by_id_and_user(self, id: uuid.UUID, user_id: uuid.UUID) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == id, Transaction.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        user_id: uuid.UUID,
        filters: TransactionFilters,
    ) -> tuple[list[Transaction], int]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)

        if filters.account_id:
            stmt = stmt.where(Transaction.account_id == filters.account_id)
        if filters.category_id:
            stmt = stmt.where(Transaction.category_id == filters.category_id)
        if filters.budget_id:
            stmt = stmt.where(Transaction.budget_id == filters.budget_id)
        if filters.type:
            stmt = stmt.where(Transaction.type == filters.type)
        if filters.from_date:
            stmt = stmt.where(Transaction.date >= filters.from_date)
        if filters.to_date:
            stmt = stmt.where(Transaction.date <= filters.to_date)
        if filters.currency:
            stmt = stmt.where(Transaction.currency == filters.currency)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        offset = (filters.page - 1) * filters.page_size
        stmt = stmt.order_by(Transaction.date.desc()).offset(offset).limit(filters.page_size)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def exists_for_rule_and_date(
        self, recurring_rule_id: uuid.UUID, date: date
    ) -> bool:
        result = await self.session.execute(
            select(Transaction.id).where(
                Transaction.recurring_rule_id == recurring_rule_id,
                Transaction.date == date,
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None
