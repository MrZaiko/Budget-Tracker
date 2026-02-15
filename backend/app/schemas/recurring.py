import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class RecurringRuleCreate(BaseModel):
    account_id: uuid.UUID
    category_id: uuid.UUID | None = None
    budget_id: uuid.UUID | None = None
    name: str
    type: str  # income, expense
    amount: Decimal
    currency: str
    frequency: str  # daily, weekly, monthly, yearly
    start_date: date
    end_date: date | None = None
    is_subscription: bool = False
    notes: str | None = None


class RecurringRuleUpdate(BaseModel):
    name: str | None = None
    amount: Decimal | None = None
    category_id: uuid.UUID | None = None
    budget_id: uuid.UUID | None = None
    end_date: date | None = None
    is_subscription: bool | None = None
    status: str | None = None
    notes: str | None = None


class RecurringRuleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    category_id: uuid.UUID | None
    budget_id: uuid.UUID | None
    name: str
    type: str
    amount: Decimal
    currency: str
    frequency: str
    start_date: date
    end_date: date | None
    next_occurrence: date
    is_subscription: bool
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpcomingSubscription(BaseModel):
    id: uuid.UUID
    name: str
    amount: Decimal
    currency: str
    next_occurrence: date
    frequency: str
    days_until: int
