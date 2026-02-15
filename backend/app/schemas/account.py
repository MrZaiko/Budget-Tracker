import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

ACCOUNT_TYPES = ["checking", "savings", "credit_card", "cash", "other"]


class AccountCreate(BaseModel):
    name: str
    type: str
    currency: str
    initial_balance: Decimal = Decimal("0")
    is_active: bool = True


class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    is_active: bool | None = None


class AccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    type: str
    currency: str
    initial_balance: Decimal
    is_active: bool
    balance: Decimal | None = None  # Computed field
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
