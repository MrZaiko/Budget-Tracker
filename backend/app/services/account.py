import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AccountRepository(session)

    async def list_accounts(self, user_id: uuid.UUID) -> list[AccountResponse]:
        accounts = await self.repo.get_by_user(user_id)
        result = []
        for account in accounts:
            balance = await self.repo.compute_balance(account.id)
            resp = AccountResponse.model_validate(account)
            resp.balance = balance
            result.append(resp)
        return result

    async def get_account(self, id: uuid.UUID, user_id: uuid.UUID) -> Account:
        account = await self.repo.get_by_id_and_user(id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail={"detail": "Account not found", "code": "not_found"})
        return account

    async def create_account(self, user_id: uuid.UUID, data: AccountCreate) -> Account:
        return await self.repo.create(
            user_id=user_id,
            name=data.name,
            type=data.type,
            currency=data.currency,
            initial_balance=data.initial_balance,
            is_active=data.is_active,
        )

    async def update_account(
        self, id: uuid.UUID, user_id: uuid.UUID, data: AccountUpdate
    ) -> Account:
        account = await self.get_account(id, user_id)
        kwargs = data.model_dump(exclude_none=True)
        if not kwargs:
            return account
        return await self.repo.update(account, **kwargs)

    async def delete_account(self, id: uuid.UUID, user_id: uuid.UUID) -> None:
        account = await self.get_account(id, user_id)
        if await self.repo.has_transactions(id):
            raise HTTPException(
                status_code=409,
                detail={
                    "detail": "Cannot delete account with linked transactions",
                    "code": "account_has_transactions",
                },
            )
        await self.repo.delete(account)
