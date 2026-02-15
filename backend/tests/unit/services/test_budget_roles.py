"""Unit tests for budget collaborator role enforcement."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.services.budget import BudgetService


def make_budget(owner_id: uuid.UUID) -> MagicMock:
    budget = MagicMock()
    budget.id = uuid.uuid4()
    budget.owner_id = owner_id
    budget.budget_categories = []
    return budget


def make_collab(user_id: uuid.UUID, role: str, accepted: bool = True) -> MagicMock:
    collab = MagicMock()
    collab.user_id = user_id
    collab.role = role
    collab.accepted_at = datetime.now(timezone.utc) if accepted else None
    return collab


@pytest.mark.asyncio
async def test_viewer_cannot_delete_budget():
    """A viewer collaborator should get 403 when trying to delete."""
    owner_id = uuid.uuid4()
    viewer_id = uuid.uuid4()
    budget = make_budget(owner_id)
    collab = make_collab(viewer_id, "viewer")

    mock_session = AsyncMock()
    service = BudgetService(mock_session)

    # Patch the internal repo
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.get_collaborator.return_value = collab

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_budget(budget.id, viewer_id)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "budget_role_insufficient"


@pytest.mark.asyncio
async def test_owner_can_delete_budget():
    """The owner should be able to delete their budget."""
    owner_id = uuid.uuid4()
    budget = make_budget(owner_id)

    mock_session = AsyncMock()
    service = BudgetService(mock_session)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.delete = AsyncMock()

    # Should not raise
    await service.delete_budget(budget.id, owner_id)
    service.repo.delete.assert_called_once_with(budget)


@pytest.mark.asyncio
async def test_non_collaborator_cannot_access_budget():
    """A user with no access gets 403."""
    owner_id = uuid.uuid4()
    stranger_id = uuid.uuid4()
    budget = make_budget(owner_id)

    mock_session = AsyncMock()
    service = BudgetService(mock_session)
    service.repo = AsyncMock()
    service.repo.get_by_id_with_categories.return_value = budget
    service.repo.get_collaborator.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_budget(budget.id, stranger_id)

    assert exc_info.value.status_code == 403
