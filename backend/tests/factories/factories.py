"""factory-boy factories for test data generation."""

import uuid
from datetime import date, datetime, timezone

import factory


class UserFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    sub = factory.LazyAttribute(lambda o: f"oidc|{o.id}")
    email = factory.LazyAttribute(lambda o: f"user-{o.id}@example.com")
    display_name = factory.LazyAttribute(lambda o: f"User {str(o.id)[:8]}")
    base_currency = "USD"
    auth_provider = "oidc"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class AccountFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Account {n}")
    type = "checking"
    currency = "USD"
    initial_balance = 0
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class CategoryFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Category {n}")
    icon = None
    color = "#4CAF50"
    transaction_type = "expense"
    is_system = False
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class BudgetFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    owner_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Budget {n}")
    period_type = "monthly"
    start_date = factory.LazyFunction(lambda: date.today().replace(day=1))
    end_date = None
    currency = "USD"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class TransactionFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    account_id = factory.LazyFunction(uuid.uuid4)
    category_id = None
    budget_id = None
    recurring_rule_id = None
    type = "expense"
    amount = 50.00
    currency = "USD"
    amount_base = 50.00
    exchange_rate = 1.0
    date = factory.LazyFunction(date.today)
    notes = None
    transfer_to_account_id = None
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class RecurringRuleFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    account_id = factory.LazyFunction(uuid.uuid4)
    category_id = None
    budget_id = None
    name = factory.Sequence(lambda n: f"Rule {n}")
    type = "expense"
    amount = 9.99
    currency = "USD"
    frequency = "monthly"
    start_date = factory.LazyFunction(date.today)
    end_date = None
    next_occurrence = factory.LazyFunction(date.today)
    is_subscription = False
    status = "active"
    notes = None
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
