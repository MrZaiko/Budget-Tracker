import uuid
from decimal import Decimal

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.budget import Budget, BudgetCategory, BudgetCollaborator
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Budget, session)

    async def get_accessible(self, user_id: uuid.UUID) -> list[Budget]:
        """Return budgets owned by user OR where user is an accepted collaborator."""
        result = await self.session.execute(
            select(Budget)
            .outerjoin(BudgetCollaborator, BudgetCollaborator.budget_id == Budget.id)
            .where(
                or_(
                    Budget.owner_id == user_id,
                    (
                        (BudgetCollaborator.user_id == user_id)
                        & BudgetCollaborator.accepted_at.is_not(None)
                    ),
                )
            )
            .options(
                selectinload(Budget.budget_categories).selectinload(BudgetCategory.category)
            )
            .distinct()
        )
        return list(result.scalars().all())

    async def get_by_id_with_categories(self, id: uuid.UUID) -> Budget | None:
        result = await self.session.execute(
            select(Budget)
            .where(Budget.id == id)
            .options(
                selectinload(Budget.budget_categories).selectinload(BudgetCategory.category),
                selectinload(Budget.collaborators),
            )
        )
        return result.scalar_one_or_none()

    async def get_collaborator(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> BudgetCollaborator | None:
        result = await self.session.execute(
            select(BudgetCollaborator).where(
                BudgetCollaborator.budget_id == budget_id,
                BudgetCollaborator.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_collaborators(self, budget_id: uuid.UUID) -> list[BudgetCollaborator]:
        result = await self.session.execute(
            select(BudgetCollaborator).where(BudgetCollaborator.budget_id == budget_id)
        )
        return list(result.scalars().all())

    async def get_spending_by_category(
        self,
        budget_id: uuid.UUID,
        budget_currency: str | None = None,
        from_date: "date | None" = None,
        to_date: "date | None" = None,
    ) -> dict[uuid.UUID, Decimal]:
        """Return {category_id: total_spent} for the given budget.

        When budget_currency is supplied, cross-currency transactions are converted
        to the budget currency using the stored account amount (amount_account) when
        the account currency matches the budget currency.  Otherwise the original
        transaction amount is used.
        """
        # Choose the amount column that best represents spending in the budget currency.
        if budget_currency:
            amount_col = case(
                (
                    (Transaction.account_currency == budget_currency)
                    & Transaction.amount_account.isnot(None),
                    Transaction.amount_account,
                ),
                else_=Transaction.amount,
            )
        else:
            amount_col = Transaction.amount

        stmt = select(
            Transaction.category_id,
            func.sum(amount_col).label("total"),
        ).where(
            Transaction.budget_id == budget_id,
            Transaction.type == "expense",
        )
        if from_date:
            stmt = stmt.where(Transaction.date >= from_date)
        if to_date:
            stmt = stmt.where(Transaction.date <= to_date)
        stmt = stmt.group_by(Transaction.category_id)

        result = await self.session.execute(stmt)
        return {row.category_id: Decimal(str(row.total)) for row in result.all()}
