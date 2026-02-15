import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import LocalUser, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_sub(self, sub: str) -> User | None:
        result = await self.session.execute(select(User).where(User.sub == sub))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[User]:
        result = await self.session.execute(
            select(User).order_by(User.created_at).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


class LocalUserRepository(BaseRepository[LocalUser]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LocalUser, session)

    async def get_by_email(self, email: str) -> LocalUser | None:
        result = await self.session.execute(
            select(LocalUser).where(LocalUser.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> LocalUser | None:
        result = await self.session.execute(
            select(LocalUser).where(LocalUser.user_id == user_id)
        )
        return result.scalar_one_or_none()
