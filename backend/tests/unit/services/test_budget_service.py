"""Unit tests for BudgetService (beyond role tests)."""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.budget import BudgetCreate, BudgetUpdate, CollaboratorInvite, CollaboratorUpdate
from app.services.budget import BudgetService


def make_budget(owner_id=None):
    b = MagicMock()
    b.id = uuid.uuid4()
    b.owner_id = owner_id or uuid.uuid4()
    b.name = "Test Budget"
    b.period_type = "monthly"
    b.start_date = date(2024, 1, 1)
    b.end_date = None
    b.currency = "USD"
    b.budget_categories = []
    return b


def make_collaborator(user_id, role="viewer", accepted=True):
    c = MagicMock()
    c.id = uuid.uuid4()
    c.user_id = user_id
    c.role = role
    c.accepted_at = datetime.now(timezone.utc) if accepted else None
    return c


@pytest.mark.asyncio
async def test_list_budgets():
    session = AsyncMock()
    service = BudgetService(session)
    service.repo = AsyncMock()
    service.repo.get_accessible.return_value = [make_budget(), make_budget()]

    result = await service.list_budgets(uuid.uuid4())
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_budget_not_found():
    session = AsyncMock()
    service = BudgetService(session)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.get_budget(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_budget_success():
    owner_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    updated = make_budget(owner_id)
    updated.name = "Updated"
    service.repo = AsyncMock()
    # First call (_require_owner → _require_access) returns budget
    # Second call (reload after update) returns updated
    service.repo.get_by_id_with_categories.side_effect = [budget, updated]
    service.repo.update.return_value = updated

    data = BudgetUpdate(name="Updated")
    result = await service.update_budget(budget.id, owner_id, data)
    assert result is updated


@pytest.mark.asyncio
async def test_update_budget_no_changes():
    owner_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget

    result = await service.update_budget(budget.id, owner_id, BudgetUpdate())
    assert result is budget
    service.repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_get_summary_no_categories():
    owner_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    budget.budget_categories = []
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.get_spending_by_category.return_value = {}

    result = await service.get_summary(budget.id, owner_id)
    assert result.total_limit == Decimal("0")
    assert result.total_spent == Decimal("0")
    assert result.categories == []


@pytest.mark.asyncio
async def test_invite_collaborator_already_exists():
    owner_id = uuid.uuid4()
    invitee_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    invitee = MagicMock()
    invitee.id = invitee_id
    existing_collab = make_collaborator(invitee_id)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.get_collaborator.return_value = existing_collab
    service.user_repo = AsyncMock()
    service.user_repo.get_by_email.return_value = invitee

    with pytest.raises(HTTPException) as exc:
        await service.invite_collaborator(
            budget.id, owner_id, CollaboratorInvite(email="invitee@example.com")
        )
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "already_collaborator"


@pytest.mark.asyncio
async def test_remove_collaborator_not_found():
    owner_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.get_collaborator.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.remove_collaborator(budget.id, uuid.uuid4(), owner_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_collaborator_role_not_found():
    owner_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.get_collaborator.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.update_collaborator_role(
            budget.id, uuid.uuid4(), owner_id, CollaboratorUpdate(role="editor")
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_collaborators():
    owner_id = uuid.uuid4()
    session = AsyncMock()
    service = BudgetService(session)
    budget = make_budget(owner_id)
    collabs = [make_collaborator(uuid.uuid4()), make_collaborator(uuid.uuid4())]
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.list_collaborators.return_value = collabs

    result = await service.list_collaborators(budget.id, owner_id)
    assert len(result) == 2
