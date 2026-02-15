import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class SpendingByCategory(BaseModel):
    category_id: uuid.UUID | None
    category_name: str
    amount: Decimal
    percentage: Decimal


class SpendingReportResponse(BaseModel):
    from_date: date
    to_date: date
    currency: str
    total: Decimal
    categories: list[SpendingByCategory]


class IncomeVsExpensePeriod(BaseModel):
    period: str  # e.g. "2024-01" for monthly
    income: Decimal
    expenses: Decimal
    net: Decimal


class IncomeVsExpenseResponse(BaseModel):
    from_date: date
    to_date: date
    currency: str
    periods: list[IncomeVsExpensePeriod]
    total_income: Decimal
    total_expenses: Decimal
    total_net: Decimal


class MonthlyTrend(BaseModel):
    month: str  # "YYYY-MM"
    income: Decimal
    expenses: Decimal
    net: Decimal


class TrendsReportResponse(BaseModel):
    months: int
    currency: str
    trends: list[MonthlyTrend]


class AccountBalance(BaseModel):
    account_id: uuid.UUID
    account_name: str
    account_type: str
    currency: str
    balance: Decimal
    balance_base: Decimal


class NetWorthResponse(BaseModel):
    currency: str
    date: date
    accounts: list[AccountBalance]
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
