FROM python:3.12-slim

# Install uv and curl (curl is used by the healthcheck)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies into the system Python (no venv)
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
