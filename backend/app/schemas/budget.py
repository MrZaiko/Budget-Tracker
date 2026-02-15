import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class BudgetCategoryCreate(BaseModel):
    category_id: uuid.UUID
    limit_amount: Decimal


class BudgetCategoryResponse(BaseModel):
    id: uuid.UUID
    budget_id: uuid.UUID
    category_id: uuid.UUID
    limit_amount: Decimal

    model_config = {"from_attributes": True}


class BudgetCreate(BaseModel):
    name: str
    period_type: str  # monthly, weekly, yearly, custom
    start_date: date
    end_date: date | None = None
    currency: str
    budget_categories: list[BudgetCategoryCreate] = []


class BudgetUpdate(BaseModel):
    name: str | None = None
    period_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    currency: str | None = None


class BudgetResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    period_type: str
    start_date: date
    end_date: date | None
    currency: str
    budget_categories: list[BudgetCategoryResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CollaboratorInvite(BaseModel):
    email: EmailStr
    role: str = "viewer"  # viewer, editor


class CollaboratorUpdate(BaseModel):
    role: str  # viewer, editor


class CollaboratorResponse(BaseModel):
    id: uuid.UUID
    budget_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    invited_at: datetime
    accepted_at: datetime | None

    model_config = {"from_attributes": True}


class BudgetSummaryCategory(BaseModel):
    category_id: uuid.UUID
    category_name: str
    limit_amount: Decimal
    spent_amount: Decimal
    remaining: Decimal


class BudgetSummaryResponse(BaseModel):
    budget_id: uuid.UUID
    budget_name: str
    period_type: str
    start_date: date
    end_date: date | None
    currency: str
    categories: list[BudgetSummaryCategory]
    total_limit: Decimal
    total_spent: Decimal
    total_remaining: Decimal
