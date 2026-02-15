import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Category, session)

    async def get_visible_to_user(self, user_id: uuid.UUID) -> list[Category]:
        """Return user-defined categories + system defaults (user_id IS NULL)."""
        result = await self.session.execute(
            select(Category).where(
                or_(Category.user_id == user_id, Category.user_id.is_(None))
            )
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: uuid.UUID, user_id: uuid.UUID) -> Category | None:
        """Get a user-owned category (not system)."""
        result = await self.session.execute(
            select(Category).where(Category.id == id, Category.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def has_transactions(self, category_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(Transaction.id).where(Transaction.category_id == category_id).limit(1)
        )
        return result.scalar_one_or_none() is not None
