# Project Alpha — Data Model

## Overview

All tables use **UUID primary keys**. Timestamps (`created_at`, `updated_at`) are present on every mutable table. Monetary amounts are stored as `NUMERIC(18, 6)` to support multi-currency precision.

---

## Entity Relationship Summary

```
users
 ├── local_users          (1:1, optional — local auth only)
 ├── accounts             (1:N)
 ├── categories           (1:N, user-defined; system categories have user_id = NULL)
 ├── budgets              (1:N, as owner)
 │    ├── budget_categories  (1:N)
 │    └── budget_collaborators (1:N)
 ├── transactions         (1:N)
 └── recurring_rules      (1:N)

accounts        → transactions      (1:N)
categories      → transactions      (1:N)
categories      → budget_categories (1:N)
budgets         → transactions      (1:N, optional)
recurring_rules → transactions      (1:N, generated instances)

currencies      → exchange_rates    (1:N, as base and target)
```

---

## Tables

### `users`

Central identity record. Created on first successful login (OIDC or local).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, default `gen_random_uuid()` | |
| `sub` | VARCHAR(255) | UNIQUE, NOT NULL | OIDC `sub` claim or `local:<email>` for local users |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | |
| `display_name` | VARCHAR(255) | NOT NULL | |
| `base_currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | User's reporting currency |
| `auth_provider` | VARCHAR(16) | NOT NULL, CHECK (`oidc`, `local`) | |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

---

### `local_users`

Stores credentials for local auth accounts. Only populated when `LOCAL_AUTH_ENABLED=true`.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → `users.id`, UNIQUE, NOT NULL | |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Must match `users.email` |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hash |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

---

### `accounts`

A financial account owned by a user (bank account, cash wallet, credit card, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → `users.id`, NOT NULL | |
| `name` | VARCHAR(255) | NOT NULL | |
| `type` | VARCHAR(32) | NOT NULL, CHECK (`checking`, `savings`, `credit_card`, `cash`, `other`) | |
| `currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | Native currency of the account |
| `initial_balance` | NUMERIC(18,6) | NOT NULL, default `0` | Opening balance |
| `is_active` | BOOLEAN | NOT NULL, default `true` | Soft-disable without deleting |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

> Current balance is computed at query time as `initial_balance + SUM(signed transaction amounts)`.

---

### `categories`

Transaction categories. System defaults have `user_id = NULL` and `is_system = true`. Users can create custom categories.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → `users.id`, NULLABLE | NULL for system defaults |
| `name` | VARCHAR(100) | NOT NULL | |
| `icon` | VARCHAR(64) | NULLABLE | MUI icon name or emoji |
| `color` | CHAR(7) | NULLABLE | Hex color code (e.g. `#4CAF50`) |
| `transaction_type` | VARCHAR(16) | NOT NULL, CHECK (`income`, `expense`, `both`) | Which transaction types may use this category |
| `is_system` | BOOLEAN | NOT NULL, default `false` | System categories cannot be deleted |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Index**: `(user_id)` — for fast per-user category lookups including NULLs (system).

---

### `budgets`

A budget definition. Owned by one user but shareable with collaborators.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `owner_id` | UUID | FK → `users.id`, NOT NULL | |
| `name` | VARCHAR(255) | NOT NULL | |
| `period_type` | VARCHAR(16) | NOT NULL, CHECK (`monthly`, `weekly`, `yearly`, `custom`) | |
| `start_date` | DATE | NOT NULL | Start of the budget period |
| `end_date` | DATE | NULLABLE | NULL = repeating (rolls over each period) |
| `currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | Budget is defined in this currency |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

---

### `budget_categories`

Per-category spending limits within a budget.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `budget_id` | UUID | FK → `budgets.id`, NOT NULL | |
| `category_id` | UUID | FK → `categories.id`, NOT NULL | |
| `limit_amount` | NUMERIC(18,6) | NOT NULL | Spending cap in the budget's currency |

**Unique constraint**: `(budget_id, category_id)`.

---

### `budget_collaborators`

Users who have been granted access to a budget they do not own.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `budget_id` | UUID | FK → `budgets.id`, NOT NULL | |
| `user_id` | UUID | FK → `users.id`, NOT NULL | The collaborator |
| `role` | VARCHAR(16) | NOT NULL, CHECK (`viewer`, `editor`) | |
| `invited_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `accepted_at` | TIMESTAMPTZ | NULLABLE | NULL = invitation pending |

**Unique constraint**: `(budget_id, user_id)`.

---

### `transactions`

Individual financial events (income, expense, or transfer between accounts).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → `users.id`, NOT NULL | |
| `account_id` | UUID | FK → `accounts.id`, NOT NULL | Source account |
| `category_id` | UUID | FK → `categories.id`, NULLABLE | |
| `budget_id` | UUID | FK → `budgets.id`, NULLABLE | Budget this transaction counts toward |
| `recurring_rule_id` | UUID | FK → `recurring_rules.id`, NULLABLE | Set if auto-generated by a rule |
| `type` | VARCHAR(16) | NOT NULL, CHECK (`income`, `expense`, `transfer`) | |
| `amount` | NUMERIC(18,6) | NOT NULL | Positive value; sign derived from `type` |
| `currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | Currency of the transaction |
| `amount_base` | NUMERIC(18,6) | NOT NULL | Amount converted to user's base currency |
| `exchange_rate` | NUMERIC(18,8) | NOT NULL | Rate applied at time of entry |
| `date` | DATE | NOT NULL | Transaction date (not timestamp) |
| `notes` | TEXT | NULLABLE | |
| `transfer_to_account_id` | UUID | FK → `accounts.id`, NULLABLE | Required when `type = transfer` |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes**: `(user_id, date)`, `(account_id)`, `(budget_id)`, `(category_id)`, `(recurring_rule_id)`.

---

### `recurring_rules`

Defines a recurring transaction pattern. The scheduler generates `transactions` from these rules daily.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → `users.id`, NOT NULL | |
| `account_id` | UUID | FK → `accounts.id`, NOT NULL | |
| `category_id` | UUID | FK → `categories.id`, NULLABLE | |
| `budget_id` | UUID | FK → `budgets.id`, NULLABLE | |
| `name` | VARCHAR(255) | NOT NULL | e.g. "Netflix", "Monthly Rent" |
| `type` | VARCHAR(16) | NOT NULL, CHECK (`income`, `expense`) | Transfers cannot recur |
| `amount` | NUMERIC(18,6) | NOT NULL | |
| `currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | |
| `frequency` | VARCHAR(16) | NOT NULL, CHECK (`daily`, `weekly`, `monthly`, `yearly`) | |
| `start_date` | DATE | NOT NULL | |
| `end_date` | DATE | NULLABLE | NULL = no end |
| `next_occurrence` | DATE | NOT NULL | Updated by scheduler after each generation |
| `is_subscription` | BOOLEAN | NOT NULL, default `false` | Flags for the subscription tracker view |
| `status` | VARCHAR(16) | NOT NULL, CHECK (`active`, `paused`, `cancelled`) | |
| `notes` | TEXT | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Index**: `(user_id, status, next_occurrence)` — used by the daily scheduler job.

---

### `currencies`

Static reference table of supported ISO 4217 currencies. Seeded at startup.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `code` | CHAR(3) | PK | ISO 4217 code (e.g. `USD`, `EUR`) |
| `name` | VARCHAR(100) | NOT NULL | e.g. "US Dollar" |
| `symbol` | VARCHAR(8) | NOT NULL | e.g. "$", "€" |

---

### `exchange_rates`

Daily exchange rate snapshots fetched from Frankfurter API and cached in the database.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | |
| `base_currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | |
| `target_currency` | CHAR(3) | FK → `currencies.code`, NOT NULL | |
| `rate` | NUMERIC(18,8) | NOT NULL | How many `target` per 1 `base` |
| `date` | DATE | NOT NULL | Rate date (ECB publishes business days only) |
| `fetched_at` | TIMESTAMPTZ | NOT NULL, default `now()` | When this record was written |

**Unique constraint**: `(base_currency, target_currency, date)`.
**Index**: `(base_currency, date DESC)` — for fast latest-rate lookups.

---

## Notes

- **Soft deletes** are not used. Deleting an account or category checks for linked transactions first and returns a `409` if any exist.
- **Transfers** create a single `transaction` row with `type = transfer`; the debit from `account_id` and credit to `transfer_to_account_id` are inferred at query time.
- **Amount sign convention**: `amount` is always stored as a positive number. The `type` column determines its effect on the account balance (`income` → +, `expense` → −, `transfer` → − on source, + on destination).
- **Base currency amounts**: `amount_base` and `exchange_rate` are snapshotted at write time so historical reports remain accurate even as rates change.
