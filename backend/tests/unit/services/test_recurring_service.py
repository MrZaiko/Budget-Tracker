"""Unit tests for RecurringService."""

import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.recurring import RecurringRuleCreate, RecurringRuleUpdate
from app.services.recurring import RecurringService


def make_rule(user_id=None, is_subscription=False):
    rule = MagicMock()
    rule.id = uuid.uuid4()
    rule.user_id = user_id or uuid.uuid4()
    rule.name = "Test Rule"
    rule.type = "expense"
    rule.amount = Decimal("9.99")
    rule.currency = "USD"
    rule.frequency = "monthly"
    rule.next_occurrence = date.today()
    rule.is_subscription = is_subscription
    rule.status = "active"
    return rule


@pytest.mark.asyncio
async def test_get_rule_not_found_raises_404():
    session = AsyncMock()
    service = RecurringService(session)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.get_rule(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404
    assert exc.value.detail["code"] == "not_found"


@pytest.mark.asyncio
async def test_list_rules():
    session = AsyncMock()
    service = RecurringService(session)
    service.repo = AsyncMock()
    service.repo.get_by_user.return_value = [make_rule(), make_rule()]

    result = await service.list_rules(uuid.uuid4())
    assert len(result) == 2


@pytest.mark.asyncio
async def test_create_rule():
    session = AsyncMock()
    service = RecurringService(session)
    new_rule = make_rule()
    service.repo = AsyncMock()
    service.repo.create.return_value = new_rule

    data = RecurringRuleCreate(
        account_id=uuid.uuid4(),
        name="Netflix",
        type="expense",
        amount=Decimal("15.99"),
        currency="USD",
        frequency="monthly",
        start_date=date.today(),
    )
    result = await service.create_rule(new_rule.user_id, data)
    assert result is new_rule
    call_kwargs = service.repo.create.call_args.kwargs
    assert call_kwargs["status"] == "active"
    assert call_kwargs["next_occurrence"] == data.start_date


@pytest.mark.asyncio
async def test_update_rule_no_changes():
    session = AsyncMock()
    service = RecurringService(session)
    existing = make_rule()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing

    result = await service.update_rule(existing.id, existing.user_id, RecurringRuleUpdate())
    assert result is existing
    service.repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_rule_with_changes():
    session = AsyncMock()
    service = RecurringService(session)
    existing = make_rule()
    updated = make_rule()
    updated.name = "Updated"
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing
    service.repo.update.return_value = updated

    result = await service.update_rule(
        existing.id, existing.user_id, RecurringRuleUpdate(name="Updated")
    )
    assert result is updated


@pytest.mark.asyncio
async def test_delete_rule():
    session = AsyncMock()
    service = RecurringService(session)
    existing = make_rule()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing

    await service.delete_rule(existing.id, existing.user_id)
    service.repo.delete.assert_called_once_with(existing)


@pytest.mark.asyncio
async def test_list_subscriptions():
    session = AsyncMock()
    service = RecurringService(session)
    sub = make_rule(is_subscription=True)
    service.repo = AsyncMock()
    service.repo.get_subscriptions.return_value = [sub]

    result = await service.list_subscriptions(sub.user_id)
    assert len(result) == 1
    assert result[0].is_subscription is True


@pytest.mark.asyncio
async def test_get_upcoming_subscriptions():
    session = AsyncMock()
    service = RecurringService(session)
    sub = make_rule(is_subscription=True)
    sub.next_occurrence = date.today()
    service.repo = AsyncMock()
    service.repo.get_upcoming.return_value = [sub]

    result = await service.get_upcoming(sub.user_id, days=7)
    assert len(result) == 1
    assert result[0].name == sub.name
    assert result[0].days_until == 0


@pytest.mark.asyncio
async def test_get_upcoming_empty():
    session = AsyncMock()
    service = RecurringService(session)
    service.repo = AsyncMock()
    service.repo.get_upcoming.return_value = []

    result = await service.get_upcoming(uuid.uuid4(), days=30)
    assert result == []
