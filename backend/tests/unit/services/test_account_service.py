"""Unit tests for AccountService."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.account import AccountService
from app.schemas.account import AccountCreate, AccountUpdate


def make_account(user_id=None):
    acc = MagicMock()
    acc.id = uuid.uuid4()
    acc.user_id = user_id or uuid.uuid4()
    acc.name = "Test Account"
    acc.type = "checking"
    acc.currency = "USD"
    acc.initial_balance = Decimal("0")
    acc.is_active = True
    return acc


@pytest.mark.asyncio
async def test_get_account_not_found_raises_404():
    session = AsyncMock()
    service = AccountService(session)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.get_account(uuid.uuid4(), uuid.uuid4())

    assert exc.value.status_code == 404
    assert exc.value.detail["code"] == "not_found"


@pytest.mark.asyncio
async def test_create_account():
    session = AsyncMock()
    service = AccountService(session)
    new_acc = make_account()
    service.repo = AsyncMock()
    service.repo.create.return_value = new_acc

    data = AccountCreate(name="Savings", type="savings", currency="EUR")
    result = await service.create_account(new_acc.user_id, data)

    assert result is new_acc
    service.repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_update_account_no_changes():
    """update_account with empty data returns existing account unchanged."""
    session = AsyncMock()
    service = AccountService(session)
    existing = make_account()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing

    data = AccountUpdate()
    result = await service.update_account(existing.id, existing.user_id, data)

    assert result is existing
    service.repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_account_with_transactions_raises_409():
    session = AsyncMock()
    service = AccountService(session)
    existing = make_account()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing
    service.repo.has_transactions.return_value = True

    with pytest.raises(HTTPException) as exc:
        await service.delete_account(existing.id, existing.user_id)

    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "account_has_transactions"


@pytest.mark.asyncio
async def test_delete_account_success():
    session = AsyncMock()
    service = AccountService(session)
    existing = make_account()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing
    service.repo.has_transactions.return_value = False

    await service.delete_account(existing.id, existing.user_id)
    service.repo.delete.assert_called_once_with(existing)


@pytest.mark.asyncio
async def test_list_accounts_includes_balance():
    session = AsyncMock()
    service = AccountService(session)
    acc = make_account()
    service.repo = AsyncMock()
    service.repo.get_by_user.return_value = [acc]
    service.repo.compute_balance.return_value = Decimal("1234.56")

    # Patch AccountResponse.model_validate to avoid SQLAlchemy attribute issues
    with patch("app.services.account.AccountResponse") as MockResp:
        mock_resp = MagicMock()
        MockResp.model_validate.return_value = mock_resp

        result = await service.list_accounts(acc.user_id)

    assert len(result) == 1
    assert mock_resp.balance == Decimal("1234.56")
