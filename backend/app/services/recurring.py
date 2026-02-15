import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring import RecurringRule
from app.repositories.recurring import RecurringRepository
from app.schemas.recurring import RecurringRuleCreate, RecurringRuleUpdate, UpcomingSubscription
from app.utils.date_utils import next_occurrence


class RecurringService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = RecurringRepository(session)

    async def list_rules(self, user_id: uuid.UUID) -> list[RecurringRule]:
        return await self.repo.get_by_user(user_id)

    async def get_rule(self, id: uuid.UUID, user_id: uuid.UUID) -> RecurringRule:
        rule = await self.repo.get_by_id_and_user(id, user_id)
        if not rule:
            raise HTTPException(
                status_code=404, detail={"detail": "Recurring rule not found", "code": "not_found"}
            )
        return rule

    async def create_rule(self, user_id: uuid.UUID, data: RecurringRuleCreate) -> RecurringRule:
        return await self.repo.create(
            user_id=user_id,
            account_id=data.account_id,
            category_id=data.category_id,
            budget_id=data.budget_id,
            name=data.name,
            type=data.type,
            amount=data.amount,
            currency=data.currency,
            frequency=data.frequency,
            start_date=data.start_date,
            end_date=data.end_date,
            next_occurrence=data.start_date,
            is_subscription=data.is_subscription,
            status="active",
            notes=data.notes,
        )

    async def update_rule(
        self, id: uuid.UUID, user_id: uuid.UUID, data: RecurringRuleUpdate
    ) -> RecurringRule:
        rule = await self.get_rule(id, user_id)
        kwargs = data.model_dump(exclude_none=True)
        if not kwargs:
            return rule
        return await self.repo.update(rule, **kwargs)

    async def delete_rule(self, id: uuid.UUID, user_id: uuid.UUID) -> None:
        rule = await self.get_rule(id, user_id)
        await self.repo.delete(rule)

    async def list_subscriptions(self, user_id: uuid.UUID) -> list[RecurringRule]:
        return await self.repo.get_subscriptions(user_id)

    async def get_upcoming(self, user_id: uuid.UUID, days: int = 30) -> list[UpcomingSubscription]:
        from datetime import date as date_type

        rules = await self.repo.get_upcoming(user_id, days)
        today = date_type.today()
        result = []
        for rule in rules:
            days_until = (rule.next_occurrence - today).days
            result.append(
                UpcomingSubscription(
                    id=rule.id,
                    name=rule.name,
                    amount=rule.amount,  # type: ignore[arg-type]
                    currency=rule.currency,
                    next_occurrence=rule.next_occurrence,
                    frequency=rule.frequency,
                    days_until=days_until,
                )
            )
        return result
