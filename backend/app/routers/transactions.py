import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transaction import TransactionService
from datetime import date

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=PaginatedResponse[TransactionResponse])
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    account_id: uuid.UUID | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
    budget_id: uuid.UUID | None = Query(default=None),
    type: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    currency: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> PaginatedResponse[TransactionResponse]:
    filters = TransactionFilters(
        account_id=account_id,
        category_id=category_id,
        budget_id=budget_id,
        type=type,
        from_date=from_date,
        to_date=to_date,
        currency=currency,
        page=page,
        page_size=page_size,
    )
    service = TransactionService(session)
    result = await service.list_transactions(current_user.id, filters)
    return PaginatedResponse[TransactionResponse](
        items=[TransactionResponse.model_validate(t) for t in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.post("", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    data: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    service = TransactionService(session)
    tx = await service.create_transaction(current_user.id, data, current_user.base_currency)
    return TransactionResponse.model_validate(tx)


@router.get("/{id}", response_model=TransactionResponse)
async def get_transaction(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    service = TransactionService(session)
    tx = await service.get_transaction(id, current_user.id)
    return TransactionResponse.model_validate(tx)


@router.patch("/{id}", response_model=TransactionResponse)
async def update_transaction(
    id: uuid.UUID,
    data: TransactionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    service = TransactionService(session)
    tx = await service.update_transaction(id, current_user.id, data)
    return TransactionResponse.model_validate(tx)


@router.delete("/{id}", status_code=204)
async def delete_transaction(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = TransactionService(session)
    await service.delete_transaction(id, current_user.id)
