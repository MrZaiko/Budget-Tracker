import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CategoryRepository(session)

    async def list_categories(self, user_id: uuid.UUID) -> list[Category]:
        return await self.repo.get_visible_to_user(user_id)

    async def create_category(self, user_id: uuid.UUID, data: CategoryCreate) -> Category:
        return await self.repo.create(
            user_id=user_id,
            name=data.name,
            icon=data.icon,
            color=data.color,
            transaction_type=data.transaction_type,
            is_system=False,
        )

    async def update_category(
        self, id: uuid.UUID, user_id: uuid.UUID, data: CategoryUpdate
    ) -> Category:
        category = await self.repo.get_by_id_and_user(id, user_id)
        if not category:
            raise HTTPException(
                status_code=404, detail={"detail": "Category not found", "code": "not_found"}
            )
        if category.is_system:
            raise HTTPException(
                status_code=403,
                detail={"detail": "System categories cannot be modified", "code": "system_category"},
            )
        kwargs = data.model_dump(exclude_none=True)
        if not kwargs:
            return category
        return await self.repo.update(category, **kwargs)

    async def delete_category(self, id: uuid.UUID, user_id: uuid.UUID) -> None:
        category = await self.repo.get_by_id_and_user(id, user_id)
        if not category:
            raise HTTPException(
                status_code=404, detail={"detail": "Category not found", "code": "not_found"}
            )
        if category.is_system:
            raise HTTPException(
                status_code=403,
                detail={"detail": "System categories cannot be deleted", "code": "system_category"},
            )
        if await self.repo.has_transactions(id):
            raise HTTPException(
                status_code=409,
                detail={
                    "detail": "Cannot delete category with linked transactions",
                    "code": "category_has_transactions",
                },
            )
        await self.repo.delete(category)
