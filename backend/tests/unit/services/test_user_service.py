"""Unit tests for UserService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.user import UserUpdate
from app.services.user import UserService


def make_user():
    u = MagicMock()
    u.id = uuid.uuid4()
    u.email = "user@example.com"
    u.display_name = "Test User"
    u.base_currency = "USD"
    return u


@pytest.mark.asyncio
async def test_get_by_id():
    session = AsyncMock()
    service = UserService(session)
    user = make_user()
    service.repo = AsyncMock()
    service.repo.get.return_value = user

    result = await service.get_by_id(user.id)
    assert result is user


@pytest.mark.asyncio
async def test_get_by_id_not_found():
    session = AsyncMock()
    service = UserService(session)
    service.repo = AsyncMock()
    service.repo.get.return_value = None

    result = await service.get_by_id(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_user_with_changes():
    session = AsyncMock()
    service = UserService(session)
    user = make_user()
    updated = make_user()
    updated.display_name = "New Name"
    service.repo = AsyncMock()
    service.repo.update.return_value = updated

    data = UserUpdate(display_name="New Name")
    result = await service.update(user, data)

    assert result is updated
    service.repo.update.assert_called_once_with(user, display_name="New Name")


@pytest.mark.asyncio
async def test_update_user_no_changes():
    session = AsyncMock()
    service = UserService(session)
    user = make_user()
    service.repo = AsyncMock()

    data = UserUpdate()
    result = await service.update(user, data)

    assert result is user
    service.repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_currency():
    session = AsyncMock()
    service = UserService(session)
    user = make_user()
    updated = make_user()
    updated.base_currency = "EUR"
    service.repo = AsyncMock()
    service.repo.update.return_value = updated

    data = UserUpdate(base_currency="EUR")
    result = await service.update(user, data)

    service.repo.update.assert_called_once_with(user, base_currency="EUR")
