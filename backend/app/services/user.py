import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        return await self.repo.get(id)

    async def update(self, user: User, data: UserUpdate) -> User:
        kwargs = data.model_dump(exclude_none=True)
        if not kwargs:
            return user
        return await self.repo.update(user, **kwargs)
