# Project Alpha — Backend Requirements

## Technology Stack

| Concern            | Choice                        | Notes                                              |
|--------------------|-------------------------------|----------------------------------------------------|
| Language           | Python 3.12+                  |                                                    |
| Framework          | FastAPI                       | Async-first, automatic OpenAPI docs                |
| Database           | PostgreSQL 16+                |                                                    |
| ORM                | SQLAlchemy 2.x (async)        | With Alembic for migrations                        |
| Authentication     | OpenID Connect (OIDC) + Local | Authentik as SSO; local credentials for dev/debug  |
| Background Jobs    | APScheduler                   | In-process scheduler, no extra service required    |
| Exchange Rates     | Frankfurter API               | Free, no API key, ECB-sourced rates                |
| Containerization   | Docker                        | Single app container; connects to external PostgreSQL |

---

## Authentication & Authorization

### OpenID Connect with Authentik

- The backend acts as an **OIDC Resource Server** — it does not issue tokens.
- All API requests must carry a **Bearer JWT** issued by Authentik.
- On each request the backend:
  1. Validates the JWT signature against Authentik's JWKS endpoint.
  2. Checks `exp`, `iss`, and `aud` claims.
  3. Extracts the user identity (`sub` claim) and maps it to a local `User` record.
- On first login (JWT valid but no local user record), a user profile is auto-created from the token claims (`sub`, `email`, `name`).
- The JWKS URI and issuer URL are provided via environment variables (see Configuration).

### Local Authentication (Dev / Debug)

A secondary auth path using local credentials is available for development, debugging, and scenarios where Authentik is unreachable.

- **Enabled** only when the environment variable `LOCAL_AUTH_ENABLED=true` is set. It is **disabled by default** and must never be enabled in production.
- Local users are stored in the `local_users` table with `bcrypt`-hashed passwords.
- Login endpoint: `POST /auth/local/token` — accepts `email` + `password`, returns a short-lived JWT signed with an application secret key (`LOCAL_AUTH_SECRET`).
- The issued JWT uses the same claims structure (`sub`, `email`, `name`) as OIDC tokens, so the rest of the auth middleware is unchanged.
- A separate validation path checks the token's issuer: `local` vs. the Authentik issuer URL.
- Local accounts are created via a CLI management command (`python manage.py create-local-user`) — there is no self-registration UI.
- Local users are flagged in the `User` record (`auth_provider: local`) and can be identified in logs.

### Authorization Model

- Every resource (transaction, budget, category, etc.) is owned by a `user_id`.
- Users can only access their own resources **except** for shared budgets (see Budget Sharing).
- No admin role in v1 — all users are peers.

### Budget Sharing

- A budget can have multiple **collaborators** beyond the owner.
- Collaborator roles:
  - `viewer` — read-only access to the budget and its transactions
  - `editor` — can add/edit/delete transactions within the budget
- Sharing is done by inviting another registered user by email.
- The owner can revoke access at any time.
- Collaborators cannot delete or modify the budget definition itself.

---

## API Design

Base path: `/api/v1`

All endpoints return JSON. Errors follow the format:
```json
{
  "detail": "Human-readable message",
  "code": "machine_readable_code"
}
```

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Get current user profile |
| PATCH | `/users/me` | Update profile (display name, base currency) |

### Accounts

An account represents a financial account (bank account, cash wallet, credit card, etc.).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/accounts` | List user's accounts |
| POST | `/accounts` | Create an account |
| GET | `/accounts/{id}` | Get account details |
| PATCH | `/accounts/{id}` | Update account |
| DELETE | `/accounts/{id}` | Delete account |

### Transactions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/transactions` | List transactions (filterable by date, category, account, type) |
| POST | `/transactions` | Create a transaction |
| GET | `/transactions/{id}` | Get transaction detail |
| PATCH | `/transactions/{id}` | Update a transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |

Query parameters for listing: `account_id`, `category_id`, `budget_id`, `type` (income/expense), `from_date`, `to_date`, `currency`, `page`, `page_size`.

### Categories

| Method | Path | Description |
|--------|------|-------------|
| GET | `/categories` | List categories (user-defined + system defaults) |
| POST | `/categories` | Create a custom category |
| PATCH | `/categories/{id}` | Update a category |
| DELETE | `/categories/{id}` | Delete a category |

### Budgets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/budgets` | List budgets (owned + shared) |
| POST | `/budgets` | Create a budget |
| GET | `/budgets/{id}` | Get budget with current usage |
| PATCH | `/budgets/{id}` | Update budget |
| DELETE | `/budgets/{id}` | Delete budget (owner only) |
| GET | `/budgets/{id}/summary` | Spending vs. budget breakdown by category |

#### Budget Sharing

| Method | Path | Description |
|--------|------|-------------|
| GET | `/budgets/{id}/collaborators` | List collaborators |
| POST | `/budgets/{id}/collaborators` | Invite a collaborator by email |
| PATCH | `/budgets/{id}/collaborators/{user_id}` | Change collaborator role |
| DELETE | `/budgets/{id}/collaborators/{user_id}` | Remove a collaborator |

### Recurring Transactions & Subscriptions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/recurring` | List recurring rules |
| POST | `/recurring` | Create a recurring rule |
| GET | `/recurring/{id}` | Get rule detail |
| PATCH | `/recurring/{id}` | Update a rule |
| DELETE | `/recurring/{id}` | Delete a rule |
| GET | `/subscriptions` | Filtered view of recurring rules marked as subscriptions |
| GET | `/subscriptions/upcoming` | Renewals due in the next N days (default 30) |

A recurring rule has:
- `frequency`: `daily` | `weekly` | `monthly` | `yearly`
- `next_occurrence`: date of next scheduled transaction
- `is_subscription`: boolean flag
- `status`: `active` | `paused` | `cancelled`

### Currencies & Exchange Rates

| Method | Path | Description |
|--------|------|-------------|
| GET | `/currencies` | List supported currencies |
| GET | `/currencies/rates` | Latest rates relative to user's base currency |
| GET | `/currencies/rates/history` | Historical rates for a date range |

Rates are cached in the database and refreshed daily by the background scheduler.

### Reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports/spending` | Spending by category for a period |
| GET | `/reports/income-vs-expenses` | Income vs. expense totals by period |
| GET | `/reports/trends` | Monthly totals over a rolling window |
| GET | `/reports/net-worth` | Account balances summed (in base currency) |

---

## Background Jobs (APScheduler)

APScheduler runs inside the FastAPI process using `AsyncIOScheduler`.

| Job | Schedule | Description |
|-----|----------|-------------|
| `refresh_exchange_rates` | Daily at 00:30 UTC | Fetch latest rates from Frankfurter API and store in DB |
| `generate_recurring_transactions` | Daily at 01:00 UTC | Create transactions for any recurring rules due today |
| `send_subscription_alerts` | Daily at 08:00 UTC | Notify users of subscriptions renewing within 7 days |

Jobs are idempotent — re-running them on the same day produces no duplicate data.

---

## Configuration (Environment Variables)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OIDC_ISSUER_URL` | Authentik issuer URL (e.g. `https://auth.example.com/application/o/alpha/`) |
| `OIDC_AUDIENCE` | Expected `aud` claim value |
| `BASE_CURRENCY` | Default base currency for new users (e.g. `USD`) |
| `FRANKFURTER_BASE_URL` | Exchange rate API base URL (default: `https://api.frankfurter.app`) |
| `SCHEDULER_TIMEZONE` | Timezone for scheduled jobs (default: `UTC`) |
| `LOCAL_AUTH_ENABLED` | Enable local login (`true` / `false`, default: `false`) |
| `LOCAL_AUTH_SECRET` | Secret key for signing local JWTs (required if `LOCAL_AUTH_ENABLED=true`) |

---

## Docker

The backend is packaged as a single Docker image. PostgreSQL is **external** — the app does not manage or bundle a database container.

- **Base image**: `python:3.12-slim`
- **Entrypoint**: Uvicorn serving the FastAPI app
- **Migrations**: Run via `alembic upgrade head` as an entrypoint step before the server starts
- **Database**: Provided externally (self-hosted, managed cloud instance, etc.) and referenced via `DATABASE_URL`
- **Compose**: A `docker-compose.yml` is provided for local development convenience only — it does **not** include a `db` service; developers are expected to supply their own PostgreSQL instance

No separate worker container is needed — APScheduler runs within the `api` process.

```
docker-compose.yml (dev only)
└── api      (FastAPI + APScheduler)

External dependency:
└── PostgreSQL (not managed by this project)
```

---

## Error Handling & Validation

- Request bodies are validated by **Pydantic v2** models.
- HTTP status codes:
  - `400` — validation error or bad request
  - `401` — missing or invalid token
  - `403` — authenticated but not authorized
  - `404` — resource not found
  - `409` — conflict (e.g. duplicate resource)
  - `422` — unprocessable entity (Pydantic schema violation)
  - `500` — unexpected server error (logged, generic message returned)
- All unhandled exceptions are caught by a global exception handler and logged with a request trace ID.
