import uuid
from datetime import datetime

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None
    color: str | None = None
    transaction_type: str = "both"  # income, expense, both


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    color: str | None = None
    transaction_type: str | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    name: str
    icon: str | None
    color: str | None
    transaction_type: str
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
