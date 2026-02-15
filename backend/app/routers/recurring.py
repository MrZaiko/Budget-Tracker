import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.recurring import (
    RecurringRuleCreate,
    RecurringRuleResponse,
    RecurringRuleUpdate,
    UpcomingSubscription,
)
from app.services.recurring import RecurringService

router = APIRouter(tags=["recurring"])


@router.get("/recurring", response_model=list[RecurringRuleResponse])
async def list_recurring(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[RecurringRuleResponse]:
    service = RecurringService(session)
    rules = await service.list_rules(current_user.id)
    return [RecurringRuleResponse.model_validate(r) for r in rules]


@router.post("/recurring", response_model=RecurringRuleResponse, status_code=201)
async def create_recurring(
    data: RecurringRuleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RecurringRuleResponse:
    service = RecurringService(session)
    rule = await service.create_rule(current_user.id, data)
    return RecurringRuleResponse.model_validate(rule)


@router.get("/recurring/{id}", response_model=RecurringRuleResponse)
async def get_recurring(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RecurringRuleResponse:
    service = RecurringService(session)
    rule = await service.get_rule(id, current_user.id)
    return RecurringRuleResponse.model_validate(rule)


@router.patch("/recurring/{id}", response_model=RecurringRuleResponse)
async def update_recurring(
    id: uuid.UUID,
    data: RecurringRuleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RecurringRuleResponse:
    service = RecurringService(session)
    rule = await service.update_rule(id, current_user.id, data)
    return RecurringRuleResponse.model_validate(rule)


@router.delete("/recurring/{id}", status_code=204)
async def delete_recurring(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = RecurringService(session)
    await service.delete_rule(id, current_user.id)


@router.get("/subscriptions", response_model=list[RecurringRuleResponse])
async def list_subscriptions(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[RecurringRuleResponse]:
    service = RecurringService(session)
    subs = await service.list_subscriptions(current_user.id)
    return [RecurringRuleResponse.model_validate(s) for s in subs]


@router.get("/subscriptions/upcoming", response_model=list[UpcomingSubscription])
async def upcoming_subscriptions(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(default=30, ge=1, le=365),
) -> list[UpcomingSubscription]:
    service = RecurringService(session)
    return await service.get_upcoming(current_user.id, days)
