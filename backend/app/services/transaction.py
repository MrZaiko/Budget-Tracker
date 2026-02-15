from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.account import AccountRepository
from app.repositories.currency import ExchangeRateRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionFilters, TransactionUpdate
from app.schemas.common import PaginatedResponse
from app.utils.currency import get_rate_or_1
from app.utils.pagination import build_paginated_response


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TransactionRepository(session)
        self.rate_repo = ExchangeRateRepository(session)
        self.account_repo = AccountRepository(session)

    async def list_transactions(
        self,
        user_id: uuid.UUID,
        filters: TransactionFilters,
    ) -> PaginatedResponse[Transaction]:
        items, total = await self.repo.list_paginated(user_id, filters)
        return build_paginated_response(items, total, filters.page, filters.page_size)

    async def get_transaction(self, id: uuid.UUID, user_id: uuid.UUID) -> Transaction:
        tx = await self.repo.get_by_id_and_user(id, user_id)
        if not tx:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Transaction not found", "code": "not_found"},
            )
        return tx

    async def create_transaction(
        self, user_id: uuid.UUID, data: TransactionCreate, base_currency: str
    ) -> Transaction:
        if data.type == "transfer" and not data.transfer_to_account_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "detail": "transfer_to_account_id is required for transfers",
                    "code": "transfer_account_required",
                },
            )

        # Look up account to get its currency
        account = await self.account_repo.get(data.account_id)
        account_currency = account.currency if account else data.currency

        # Snapshot rate to account currency at write time
        account_rate = await get_rate_or_1(self.rate_repo, data.currency, account_currency)
        amount_account = Decimal(str(data.amount)) * account_rate

        # Snapshot rate to user's base currency at write time
        base_rate = await get_rate_or_1(self.rate_repo, data.currency, base_currency)
        amount_base = Decimal(str(data.amount)) * base_rate

        return await self.repo.create(
            user_id=user_id,
            account_id=data.account_id,
            category_id=data.category_id,
            budget_id=data.budget_id,
            type=data.type,
            amount=data.amount,
            currency=data.currency,
            account_currency=account_currency,
            amount_account=amount_account,
            account_exchange_rate=account_rate,
            amount_base=amount_base,
            exchange_rate=base_rate,
            date=data.date,
            notes=data.notes,
            transfer_to_account_id=data.transfer_to_account_id,
        )

    async def update_transaction(
        self, id: uuid.UUID, user_id: uuid.UUID, data: TransactionUpdate
    ) -> Transaction:
        tx = await self.get_transaction(id, user_id)
        kwargs = data.model_dump(exclude_none=True)
        if not kwargs:
            return tx
        # If amount changed, recompute account and base currency amounts using stored rates
        if "amount" in kwargs and tx.account_exchange_rate is not None:
            new_amount = Decimal(str(kwargs["amount"]))
            kwargs["amount_account"] = new_amount * Decimal(str(tx.account_exchange_rate))
        if "amount" in kwargs and tx.exchange_rate is not None:
            new_amount = Decimal(str(kwargs["amount"]))
            kwargs["amount_base"] = new_amount * Decimal(str(tx.exchange_rate))
        return await self.repo.update(tx, **kwargs)

    async def delete_transaction(self, id: uuid.UUID, user_id: uuid.UUID) -> None:
        tx = await self.get_transaction(id, user_id)
        await self.repo.delete(tx)
