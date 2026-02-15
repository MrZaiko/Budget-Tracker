"""Unit tests for TransactionService."""

import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.transaction import TransactionCreate, TransactionFilters, TransactionUpdate
from app.services.transaction import TransactionService


def make_transaction():
    tx = MagicMock()
    tx.id = uuid.uuid4()
    tx.user_id = uuid.uuid4()
    tx.type = "expense"
    tx.amount = Decimal("50")
    tx.currency = "USD"
    tx.amount_base = Decimal("50")
    tx.exchange_rate = Decimal("1")
    return tx


@pytest.mark.asyncio
async def test_get_transaction_not_found():
    session = AsyncMock()
    service = TransactionService(session)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.get_transaction(uuid.uuid4(), uuid.uuid4())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_create_transaction_transfer_without_dest_raises_400():
    session = AsyncMock()
    service = TransactionService(session)

    data = TransactionCreate(
        account_id=uuid.uuid4(),
        type="transfer",
        amount=Decimal("100"),
        currency="USD",
        date=date.today(),
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_transaction(uuid.uuid4(), data, "USD")

    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "transfer_account_required"


@pytest.mark.asyncio
async def test_create_transaction_snapshots_exchange_rate():
    session = AsyncMock()
    service = TransactionService(session)
    service.repo = AsyncMock()
    service.rate_repo = AsyncMock()

    new_tx = make_transaction()
    service.repo.create.return_value = new_tx

    # Mock exchange rate
    mock_rate = MagicMock()
    mock_rate.rate = 1.2
    service.rate_repo.get_latest.return_value = mock_rate

    data = TransactionCreate(
        account_id=uuid.uuid4(),
        type="expense",
        amount=Decimal("100"),
        currency="EUR",
        date=date.today(),
    )
    result = await service.create_transaction(uuid.uuid4(), data, "USD")

    # Verify create was called with amount_base = 100 * 1.2 = 120
    call_kwargs = service.repo.create.call_args.kwargs
    assert call_kwargs["amount_base"] == pytest.approx(Decimal("120.0"))
    assert call_kwargs["exchange_rate"] == Decimal("1.2")


@pytest.mark.asyncio
async def test_update_transaction_no_changes_returns_existing():
    session = AsyncMock()
    service = TransactionService(session)
    existing = make_transaction()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing

    data = TransactionUpdate()
    result = await service.update_transaction(existing.id, existing.user_id, data)

    assert result is existing
    service.repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_transaction():
    session = AsyncMock()
    service = TransactionService(session)
    existing = make_transaction()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing

    await service.delete_transaction(existing.id, existing.user_id)
    service.repo.delete.assert_called_once_with(existing)


@pytest.mark.asyncio
async def test_list_transactions_uses_paginated_repo():
    session = AsyncMock()
    service = TransactionService(session)
    service.repo = AsyncMock()
    service.repo.list_paginated.return_value = ([], 0)

    filters = TransactionFilters(page=1, page_size=20)
    result = await service.list_transactions(uuid.uuid4(), filters)

    assert result.total == 0
    assert result.items == []
    assert result.page == 1
    assert result.pages == 0
