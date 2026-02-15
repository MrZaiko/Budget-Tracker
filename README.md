# Budget Tracker

Full-stack personal finance app with a FastAPI backend, React frontend, and PostgreSQL database.

## Tech Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL 16
- Orchestration: Docker Compose

## Backend Test Coverage

<!-- coverage-start -->
- `pytest` coverage (`backend/app`): **88%**
- Last measured from local run: **141 passed**
<!-- coverage-end -->

- Command used:

```bash
cd backend
./.venv/bin/pytest --cov=app --cov-report=term
```

## Quick Start (Docker)

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Local Development

Use the helper script to start backend + frontend in parallel:

```bash
./dev.sh
```

Default local URLs:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

## Running Backend Tests

```bash
cd backend
./.venv/bin/pytest
```

With coverage:

```bash
cd backend
./.venv/bin/pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov
```

## Continuous Integration

GitHub Actions workflow: `.github/workflows/ci-build-containers.yml`

What it checks:
- Pull request and push validation that both containers build successfully:
  - `api` image (`backend/Dockerfile`)
  - `web` image (`frontend/Dockerfile`)
