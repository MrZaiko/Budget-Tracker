import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring import RecurringRule
from app.repositories.base import BaseRepository


class RecurringRepository(BaseRepository[RecurringRule]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RecurringRule, session)

    async def get_by_user(self, user_id: uuid.UUID) -> list[RecurringRule]:
        result = await self.session.execute(
            select(RecurringRule).where(RecurringRule.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, id: uuid.UUID, user_id: uuid.UUID
    ) -> RecurringRule | None:
        result = await self.session.execute(
            select(RecurringRule).where(
                RecurringRule.id == id, RecurringRule.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_due_today(self, today: date) -> list[RecurringRule]:
        """Return all active rules whose next_occurrence <= today."""
        result = await self.session.execute(
            select(RecurringRule).where(
                RecurringRule.status == "active",
                RecurringRule.next_occurrence <= today,
            )
        )
        return list(result.scalars().all())

    async def get_subscriptions(self, user_id: uuid.UUID) -> list[RecurringRule]:
        result = await self.session.execute(
            select(RecurringRule).where(
                RecurringRule.user_id == user_id,
                RecurringRule.is_subscription.is_(True),
                RecurringRule.status != "cancelled",
            )
        )
        return list(result.scalars().all())

    async def get_upcoming(self, user_id: uuid.UUID, days: int = 30) -> list[RecurringRule]:
        from datetime import timedelta
        today = date.today()
        cutoff = today + timedelta(days=days)
        result = await self.session.execute(
            select(RecurringRule).where(
                RecurringRule.user_id == user_id,
                RecurringRule.is_subscription.is_(True),
                RecurringRule.status == "active",
                RecurringRule.next_occurrence <= cutoff,
            ).order_by(RecurringRule.next_occurrence)
        )
        return list(result.scalars().all())
