"""Re-export all models so Alembic sees full Base.metadata."""

from app.db.base import Base
from app.models.account import Account
from app.models.budget import Budget, BudgetCategory, BudgetCollaborator
from app.models.category import Category
from app.models.currency import Currency, ExchangeRate
from app.models.recurring import RecurringRule
from app.models.transaction import Transaction
from app.models.user import LocalUser, User

__all__ = [
    "Base",
    "User",
    "LocalUser",
    "Account",
    "Category",
    "Budget",
    "BudgetCategory",
    "BudgetCollaborator",
    "Transaction",
    "RecurringRule",
    "Currency",
    "ExchangeRate",
]
