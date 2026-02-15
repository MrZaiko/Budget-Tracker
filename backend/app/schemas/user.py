import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: uuid.UUID
    sub: str
    email: str
    display_name: str
    base_currency: str
    auth_provider: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
    base_currency: str | None = None


class AdminUserUpdate(BaseModel):
    is_admin: bool | None = None
