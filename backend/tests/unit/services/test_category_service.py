"""Unit tests for CategoryService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import CategoryService


def make_category(is_system=False, user_id=None):
    cat = MagicMock()
    cat.id = uuid.uuid4()
    cat.user_id = user_id or uuid.uuid4()
    cat.name = "Test Category"
    cat.is_system = is_system
    return cat


@pytest.mark.asyncio
async def test_list_categories():
    session = AsyncMock()
    service = CategoryService(session)
    service.repo = AsyncMock()
    service.repo.get_visible_to_user.return_value = [make_category()]

    result = await service.list_categories(uuid.uuid4())
    assert len(result) == 1


@pytest.mark.asyncio
async def test_create_category():
    session = AsyncMock()
    service = CategoryService(session)
    new_cat = make_category()
    service.repo = AsyncMock()
    service.repo.create.return_value = new_cat

    data = CategoryCreate(name="Groceries")
    result = await service.create_category(new_cat.user_id, data)
    assert result is new_cat
    call_kwargs = service.repo.create.call_args.kwargs
    assert call_kwargs["is_system"] is False


@pytest.mark.asyncio
async def test_update_category_not_found_raises_404():
    session = AsyncMock()
    service = CategoryService(session)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.update_category(uuid.uuid4(), uuid.uuid4(), CategoryUpdate(name="X"))
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_system_category_raises_403():
    session = AsyncMock()
    service = CategoryService(session)
    system_cat = make_category(is_system=True)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = system_cat

    with pytest.raises(HTTPException) as exc:
        await service.update_category(system_cat.id, system_cat.user_id, CategoryUpdate(name="X"))
    assert exc.value.status_code == 403
    assert exc.value.detail["code"] == "system_category"


@pytest.mark.asyncio
async def test_update_category_no_changes():
    session = AsyncMock()
    service = CategoryService(session)
    existing = make_category()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing

    result = await service.update_category(existing.id, existing.user_id, CategoryUpdate())
    assert result is existing
    service.repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_category_with_changes():
    session = AsyncMock()
    service = CategoryService(session)
    existing = make_category()
    updated = make_category()
    updated.name = "Updated"
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing
    service.repo.update.return_value = updated

    result = await service.update_category(
        existing.id, existing.user_id, CategoryUpdate(name="Updated")
    )
    assert result is updated


@pytest.mark.asyncio
async def test_delete_category_not_found_raises_404():
    session = AsyncMock()
    service = CategoryService(session)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.delete_category(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_system_category_raises_403():
    session = AsyncMock()
    service = CategoryService(session)
    system_cat = make_category(is_system=True)
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = system_cat

    with pytest.raises(HTTPException) as exc:
        await service.delete_category(system_cat.id, system_cat.user_id)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_category_with_transactions_raises_409():
    session = AsyncMock()
    service = CategoryService(session)
    existing = make_category()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing
    service.repo.has_transactions.return_value = True

    with pytest.raises(HTTPException) as exc:
        await service.delete_category(existing.id, existing.user_id)
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "category_has_transactions"


@pytest.mark.asyncio
async def test_delete_category_success():
    session = AsyncMock()
    service = CategoryService(session)
    existing = make_category()
    service.repo = AsyncMock()
    service.repo.get_by_id_and_user.return_value = existing
    service.repo.has_transactions.return_value = False

    await service.delete_category(existing.id, existing.user_id)
    service.repo.delete.assert_called_once_with(existing)
