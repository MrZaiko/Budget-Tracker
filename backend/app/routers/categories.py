import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[CategoryResponse]:
    service = CategoryService(session)
    return await service.list_categories(current_user.id)  # type: ignore[return-value]


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryResponse:
    service = CategoryService(session)
    return await service.create_category(current_user.id, data)  # type: ignore[return-value]


@router.patch("/{id}", response_model=CategoryResponse)
async def update_category(
    id: uuid.UUID,
    data: CategoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryResponse:
    service = CategoryService(session)
    return await service.update_category(id, current_user.id, data)  # type: ignore[return-value]


@router.delete("/{id}", status_code=204)
async def delete_category(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = CategoryService(session)
    await service.delete_category(id, current_user.id)
