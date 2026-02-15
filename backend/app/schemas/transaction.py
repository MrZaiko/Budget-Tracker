import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    type: str  # income, expense, transfer
    amount: Decimal
    currency: str
    date: date_type
    notes: Optional[str] = None
    transfer_to_account_id: Optional[uuid.UUID] = None


class TransactionUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    amount: Optional[Decimal] = None
    date: Optional[date_type] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID]
    budget_id: Optional[uuid.UUID]
    recurring_rule_id: Optional[uuid.UUID]
    type: str
    amount: Decimal
    currency: str
    account_currency: Optional[str]
    amount_account: Optional[Decimal]
    account_exchange_rate: Optional[Decimal]
    amount_base: Decimal
    exchange_rate: Decimal
    date: date_type
    notes: Optional[str]
    transfer_to_account_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionFilters(BaseModel):
    account_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    type: Optional[str] = None
    from_date: Optional[date_type] = None
    to_date: Optional[date_type] = None
    currency: Optional[str] = None
    page: int = 1
    page_size: int = 50
