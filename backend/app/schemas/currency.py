import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class CurrencyResponse(BaseModel):
    code: str
    name: str
    symbol: str

    model_config = {"from_attributes": True}


class ExchangeRateResponse(BaseModel):
    id: uuid.UUID
    base_currency: str
    target_currency: str
    rate: Decimal
    date: date
    fetched_at: datetime

    model_config = {"from_attributes": True}


class LatestRatesResponse(BaseModel):
    base: str
    date: date
    rates: dict[str, Decimal]


class HistoricalRatesResponse(BaseModel):
    base: str
    rates: dict[date, dict[str, Decimal]]
