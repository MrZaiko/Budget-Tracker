# Project Alpha — Frontend Requirements

## Technology Stack

| Concern            | Choice                  | Notes                                                  |
|--------------------|-------------------------|--------------------------------------------------------|
| Language           | TypeScript              |                                                        |
| Framework          | React 18+               |                                                        |
| UI Components      | Material UI (MUI) v6    | MUI X for data grids and date pickers                  |
| Charts             | Recharts                | React-native, composable, good TypeScript support      |
| Server State       | TanStack Query v5       | Caching, background refetch, pagination                |
| Client State       | Zustand                 | UI state: modals, sidebar, selected filters            |
| Routing            | React Router v6         |                                                        |
| Auth               | OIDC / OAuth2 PKCE      | `oidc-client-ts` library, redirect flow to Authentik   |
| HTTP Client        | Axios                   | Centralized instance with JWT interceptor              |
| Form Handling      | React Hook Form + Zod   | Schema-based validation aligned with backend Pydantic  |
| Containerization   | Docker                  | Single container serving the built static assets via Nginx |

---

## Authentication Flow

### OIDC (Authentik)
1. User visits the app — if no valid token is found, redirect to Authentik login.
2. Authentik handles authentication (SSO, MFA, etc.) and redirects back with an auth code.
3. The frontend exchanges the code for tokens using PKCE (no client secret needed in the browser).
4. The access token is stored in memory (not `localStorage`) and attached to all API requests via an Axios interceptor.
5. A silent refresh mechanism renews the token before expiry using a hidden iframe.
6. On logout, tokens are revoked and the user is redirected to Authentik's end-session endpoint.

### Local Login (Dev / Debug)
- Available only when the runtime env flag `LOCAL_AUTH_ENABLED=true` is set.
- The `/login/local` page renders a simple email + password form.
- On submit, credentials are posted to `POST /api/v1/auth/local/token`; the returned JWT is stored in memory and used identically to an OIDC token.
- A visible **"Dev / Local Auth"** banner is shown in the app shell when local auth is active, as a clear reminder that SSO is bypassed.
- Logout clears the in-memory token and redirects to `/login/local`.

---

## Pages & Routes

### Public

| Route | Page | Description |
|-------|------|-------------|
| `/callback` | Auth Callback | Handles the OIDC redirect, exchanges code for tokens |
| `/logout` | Logout | Clears session, redirects to Authentik end-session |
| `/login/local` | Local Login | Email/password form; only rendered when `LOCAL_AUTH_ENABLED=true` |

### Authenticated (protected routes — redirect to Authentik if unauthenticated)

| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Overview of financial health |
| `/accounts` | Accounts | List and manage financial accounts |
| `/transactions` | Transactions | Full transaction list with filtering |
| `/budgets` | Budgets | List of budgets (owned + shared) |
| `/budgets/:id` | Budget Detail | Spending breakdown and collaborator management |
| `/recurring` | Recurring | Recurring transaction rules |
| `/subscriptions` | Subscriptions | Subscription tracker with renewal calendar |
| `/reports` | Reports | Charts and analytics |
| `/settings` | Settings | User profile, preferences, categories |

---

## Page Descriptions

### Dashboard (`/`)
The landing page after login. Provides a snapshot of the user's financial status.

**Sections:**
- **Net worth bar** — total balance across all accounts in base currency
- **Budget status cards** — one card per active budget showing used/total with a progress bar
- **Spending by category** — pie chart for the current month
- **Income vs. Expenses** — bar chart comparing this month vs. last month
- **Recent transactions** — last 5–10 transactions with quick-add button
- **Upcoming subscriptions** — renewals due in the next 30 days

---

### Accounts (`/accounts`)
Manage financial accounts (bank accounts, cash wallets, credit cards, etc.).

**Features:**
- List of accounts with current balance and currency
- Add / edit / delete account via a slide-in drawer
- Account type badge (checking, savings, credit card, cash, other)
- Total balance across all accounts shown in base currency at the top

---

### Transactions (`/transactions`)
Full paginated list of all transactions.

**Features:**
- Filter bar: date range, account, category, type (income/expense), currency
- Sortable columns: date, amount, category
- Inline quick-edit for amount, category, and notes
- Add transaction button → opens modal with full form
- Import transactions via CSV (deferred — post v1)
- Bulk delete with confirmation

**Transaction form fields:**
- Type (income / expense / transfer)
- Amount + currency
- Date
- Account
- Category
- Budget (optional)
- Notes
- Recurring toggle (links to a recurring rule)

---

### Budgets (`/budgets`)
Overview of all budgets the user owns or has been shared with them.

**Features:**
- Budget cards showing: name, period, total limit, amount spent, % used
- Visual progress bar (color-coded: green < 75%, amber 75–99%, red ≥ 100%)
- Owned vs. shared badge
- Create budget button → opens modal

---

### Budget Detail (`/budgets/:id`)
Deep-dive into a single budget.

**Sections:**
- **Summary header** — period, total limit, total spent, remaining
- **Category breakdown table** — each category's allocated vs. spent amount
- **Spending trend chart** — daily cumulative spend over the budget period
- **Linked transactions list** — filterable, paginated
- **Collaborators panel** (owner only) — invite by email, manage roles, revoke access

---

### Recurring (`/recurring`)
Manage all recurring transaction rules.

**Features:**
- List with frequency, next occurrence, linked category, amount, status
- Add / edit / delete via drawer
- Pause / resume toggle per rule
- Filter by status (active / paused / cancelled)

---

### Subscriptions (`/subscriptions`)
Dedicated view for recurring rules flagged as subscriptions.

**Features:**
- Subscription cards: name, cost, frequency, next renewal date, status
- **Upcoming renewals timeline** — visual list of renewals in the next 30 days
- Monthly cost summary (total active subscription spend)
- Quick-add subscription button (pre-fills `is_subscription: true`)
- Status filter: active / paused / cancelled

---

### Reports (`/reports`)

Tab-based report views:

| Tab | Chart type | Description |
|-----|-----------|-------------|
| Spending by Category | Pie + table | Category breakdown for a selected period |
| Income vs. Expenses | Grouped bar | Monthly income and expense totals side by side |
| Trends | Line chart | Rolling 12-month net balance trend |
| Net Worth | Bar chart | Account balances over time (monthly snapshot) |

**Common controls:** date range picker, currency selector (show in base or selected currency).

---

### Settings (`/settings`)

Tab-based settings page:

| Tab | Description |
|-----|-------------|
| Profile | Display name, email (read-only from OIDC), avatar |
| Preferences | Base currency, date format, first day of week |
| Categories | Add / edit / delete custom categories with icon and color |
| Notifications | Subscription alert lead time (e.g., 7 days before renewal) |

---

## Layout & Navigation

- **App shell**: persistent left sidebar (desktop) / bottom navigation bar (mobile)
- **Sidebar items**: Dashboard, Accounts, Transactions, Budgets, Recurring, Subscriptions, Reports, Settings
- **Top bar**: page title, user avatar menu (profile link + logout)
- **Theme**: MUI default theme with light/dark mode toggle stored in user preferences
- **Responsive**: all pages usable on mobile (≥ 375px width); tables collapse to card lists on small screens

---

## State Management

| State type | Tool | Examples |
|------------|------|---------|
| Server data | TanStack Query | Transactions, budgets, accounts — fetched, cached, invalidated on mutation |
| UI / ephemeral | Zustand | Modal open state, active filters, sidebar collapse, selected date range |
| Auth tokens | In-memory (`oidc-client-ts`) | Access token, refresh token, user profile |

---

## Error Handling

- API errors surface as MUI `Snackbar` / `Alert` toasts (error, warning, success variants)
- 401 responses trigger a silent token refresh; if that fails, redirect to login
- 403 responses show an inline "You don't have access to this resource" message
- 404 routes render a friendly "Page not found" screen with a home link
- Network errors show a persistent banner with a retry button

---

## Docker

The frontend is packaged as a single Docker image serving the production build via **Nginx**.

- **Build stage**: Node 20 Alpine — runs `npm run build`
- **Serve stage**: Nginx Alpine — serves the `dist/` folder
- **SPA routing**: Nginx config rewrites all routes to `index.html`
- **Runtime config**: OIDC authority URL, API base URL, and client ID are injected at container startup via environment variables into a `window.__ENV__` config object (avoids rebuilding the image per environment)

```
docker-compose.yml (dev only)
└── web      (React + Nginx)

External dependencies:
├── api      (Project Alpha backend)
└── Authentik (SSO provider)
```
