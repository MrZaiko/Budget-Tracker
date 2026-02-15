import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.services.account import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountResponse])
async def list_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[AccountResponse]:
    service = AccountService(session)
    return await service.list_accounts(current_user.id)


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    data: AccountCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AccountResponse:
    service = AccountService(session)
    account = await service.create_account(current_user.id, data)
    from app.repositories.account import AccountRepository
    repo = AccountRepository(session)
    balance = await repo.compute_balance(account.id)
    resp = AccountResponse.model_validate(account)
    resp.balance = balance
    return resp


@router.get("/{id}", response_model=AccountResponse)
async def get_account(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AccountResponse:
    service = AccountService(session)
    account = await service.get_account(id, current_user.id)
    from app.repositories.account import AccountRepository
    repo = AccountRepository(session)
    balance = await repo.compute_balance(account.id)
    resp = AccountResponse.model_validate(account)
    resp.balance = balance
    return resp


@router.patch("/{id}", response_model=AccountResponse)
async def update_account(
    id: uuid.UUID,
    data: AccountUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AccountResponse:
    service = AccountService(session)
    account = await service.update_account(id, current_user.id, data)
    from app.repositories.account import AccountRepository
    repo = AccountRepository(session)
    balance = await repo.compute_balance(account.id)
    resp = AccountResponse.model_validate(account)
    resp.balance = balance
    return resp


@router.delete("/{id}", status_code=204)
async def delete_account(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = AccountService(session)
    await service.delete_account(id, current_user.id)
