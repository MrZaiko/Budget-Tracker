import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_admin_user
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.user import UserRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.user import AdminUserUpdate, UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    _admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
) -> list[UserResponse]:
    user_repo = UserRepository(session)
    return await user_repo.list_all(skip=skip, limit=limit)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
) -> UserResponse:
    if payload.is_admin is False and admin.id == user_id:
        raise HTTPException(status_code=400, detail={"code": "self_demotion_not_allowed"})

    user_repo = UserRepository(session)
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"code": "user_not_found"})

    kwargs = {k: v for k, v in payload.model_dump().items() if v is not None}
    if kwargs:
        user = await user_repo.update(user, **kwargs)
    await session.commit()
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
) -> None:
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail={"code": "self_delete_not_allowed"})

    user_repo = UserRepository(session)
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"code": "user_not_found"})

    await user_repo.delete(user)
    await session.commit()


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_system_category(
    payload: CategoryCreate,
    _admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
) -> CategoryResponse:
    cat_repo = CategoryRepository(session)
    category = await cat_repo.create(
        name=payload.name,
        icon=payload.icon,
        color=payload.color,
        transaction_type=payload.transaction_type,
        is_system=True,
        user_id=None,
    )
    await session.commit()
    return category


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_system_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    _admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
) -> CategoryResponse:
    cat_repo = CategoryRepository(session)
    category = await cat_repo.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail={"code": "category_not_found"})

    kwargs = {k: v for k, v in payload.model_dump().items() if v is not None}
    if kwargs:
        category = await cat_repo.update(category, **kwargs)
    await session.commit()
    return category


@router.delete("/categories/{category_id}", status_code=204)
async def delete_system_category(
    category_id: uuid.UUID,
    _admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
) -> None:
    cat_repo = CategoryRepository(session)
    category = await cat_repo.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail={"code": "category_not_found"})

    await cat_repo.delete(category)
    await session.commit()
