# Project Alpha — Overview

## Purpose

Project Alpha is a personal finance and household budgeting application designed to give individuals and families full visibility and control over their financial life. It enables users to track income and expenses, plan budgets by category, monitor recurring costs (especially subscriptions), and understand spending patterns through clear visualizations — all with multi-currency support.

---

## Target Users

- **Individuals** managing their personal finances
- **Families** sharing a household budget across multiple members

---

## Core Features

### Income & Expense Tracking
- Log income and expense transactions manually or via import
- Assign transactions to categories (e.g., Groceries, Rent, Salary)
- Support for notes and attachments on transactions

### Budget Management
- Set monthly (or custom period) budgets per category
- Track budget usage in real time
- Alerts when approaching or exceeding a budget limit

### Spending Visualizations
- Dashboard with spending summaries by period and category
- Charts: bar, pie, and trend line views
- Comparison across periods (e.g., this month vs. last month)

### Recurring Transactions & Subscriptions
- Define recurring transactions with frequency (daily, weekly, monthly, yearly)
- Dedicated subscription tracker: name, cost, renewal date, status (active/paused/cancelled)
- Upcoming renewals view and alerts

### Multi-Currency Support
- Transactions can be recorded in any currency
- Automatic conversion to a user-defined base currency using exchange rates
- Historical rate tracking for accurate past reporting

---

## Tech Stack

| Layer     | Technology        |
|-----------|-------------------|
| Backend   | Python (FastAPI)  |
| Frontend  | React             |
| Database  | TBD               |
| Auth      | TBD               |

---

## Out of Scope (v1)

- Bank/account sync via open banking APIs
- Investment or asset tracking
- Tax reporting
- Mobile native apps (web-responsive only)

---

## Document Index

| File | Description |
|------|-------------|
| `01_overview.md` | This document — project goals and high-level scope |
| `02_backend.md` | Python backend requirements and API design |
| `03_frontend.md` | React frontend requirements and UI structure |
| `04_data_model.md` | Database schema and entity relationships |
| `05_auth.md` | Authentication and authorization design |
