import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Account, session)

    async def get_by_user(self, user_id: uuid.UUID) -> list[Account]:
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: uuid.UUID, user_id: uuid.UUID) -> Account | None:
        result = await self.session.execute(
            select(Account).where(Account.id == id, Account.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def compute_balance(self, account_id: uuid.UUID) -> Decimal:
        """Compute current balance as initial_balance + SUM of signed amounts in account currency.

        Uses amount_account (amount converted to the account's currency) when available,
        falling back to amount for legacy rows created before multi-currency support.
        """
        account = await self.get(account_id)
        if account is None:
            return Decimal("0")

        # Use amount_account when available; fall back to amount for legacy rows
        effective_amount = func.coalesce(Transaction.amount_account, Transaction.amount)

        income_sum = await self.session.execute(
            select(func.coalesce(func.sum(effective_amount), 0)).where(
                Transaction.account_id == account_id,
                Transaction.type == "income",
            )
        )
        expense_sum = await self.session.execute(
            select(func.coalesce(func.sum(effective_amount), 0)).where(
                Transaction.account_id == account_id,
                Transaction.type == "expense",
            )
        )
        transfer_out = await self.session.execute(
            select(func.coalesce(func.sum(effective_amount), 0)).where(
                Transaction.account_id == account_id,
                Transaction.type == "transfer",
            )
        )
        transfer_in = await self.session.execute(
            select(func.coalesce(func.sum(effective_amount), 0)).where(
                Transaction.transfer_to_account_id == account_id,
                Transaction.type == "transfer",
            )
        )

        balance = (
            Decimal(str(account.initial_balance))
            + Decimal(str(income_sum.scalar()))
            - Decimal(str(expense_sum.scalar()))
            - Decimal(str(transfer_out.scalar()))
            + Decimal(str(transfer_in.scalar()))
        )
        return balance

    async def has_transactions(self, account_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(Transaction.id).where(Transaction.account_id == account_id).limit(1)
        )
        return result.scalar_one_or_none() is not None
