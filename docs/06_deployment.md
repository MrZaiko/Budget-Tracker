# Project Alpha — Deployment

## Overview

Project Alpha is deployed as two Docker containers on a self-hosted host:

| Container | Image | Description |
|-----------|-------|-------------|
| `alpha-api` | `registry.<domain>/project-alpha/api:<tag>` | FastAPI backend + APScheduler |
| `alpha-web` | `registry.<domain>/project-alpha/web:<tag>` | React frontend served by Nginx |

**Not managed by this project:**
- PostgreSQL — external, pre-existing instance
- Reverse proxy — external (Traefik, Nginx, Caddy, etc.); TLS termination happens there
- Authentik — external SSO provider
- Container registry — private registry hosted alongside Gitea

The app receives plain HTTP from the reverse proxy. All HTTPS termination is handled upstream.

---

## Repository & CI/CD

### Source Control

Code is hosted on a self-hosted **Gitea** instance. The repository contains both the backend and frontend as a monorepo:

```
project-alpha/
├── backend/        # FastAPI app
├── frontend/       # React app
├── .gitea/
│   └── workflows/
│       ├── build-api.yml
│       └── build-web.yml
└── docker-compose.yml   # Production compose file (no db service)
```

### Gitea Actions (CI/CD)

Gitea Actions uses the same YAML syntax as GitHub Actions. Two workflows run on push to `main` (and on tagged releases):

#### `build-api.yml`

```yaml
name: Build & Push API

on:
  push:
    branches: [main]
    tags: ["v*"]
    paths:
      - "backend/**"
      - ".gitea/workflows/build-api.yml"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ vars.REGISTRY_HOST }}
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ vars.REGISTRY_HOST }}/project-alpha/api:latest
            ${{ vars.REGISTRY_HOST }}/project-alpha/api:${{ github.sha }}
```

#### `build-web.yml`

```yaml
name: Build & Push Web

on:
  push:
    branches: [main]
    tags: ["v*"]
    paths:
      - "frontend/**"
      - ".gitea/workflows/build-web.yml"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ vars.REGISTRY_HOST }}
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ vars.REGISTRY_HOST }}/project-alpha/web:latest
            ${{ vars.REGISTRY_HOST }}/project-alpha/web:${{ github.sha }}
```

### Image Tagging Strategy

| Tag | Description |
|-----|-------------|
| `latest` | Latest build from `main` |
| `<git-sha>` | Immutable reference to a specific commit |
| `v1.2.3` | Pushed when a semver tag is created in Gitea |

Production deployments should reference a specific SHA or version tag, not `latest`.

---

## Production Deployment

### Directory Structure on the Host

```
/opt/project-alpha/
├── docker-compose.yml
├── .env                  # Not committed to source control
└── logs/                 # Optional bind-mounted log directory
```

### `docker-compose.yml`

```yaml
services:
  api:
    image: registry.<domain>/project-alpha/api:${API_TAG:-latest}
    container_name: alpha-api
    restart: unless-stopped
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"   # Exposed only to localhost; reverse proxy connects here
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s

  web:
    image: registry.<domain>/project-alpha/web:${WEB_TAG:-latest}
    container_name: alpha-web
    restart: unless-stopped
    env_file: .env
    ports:
      - "127.0.0.1:3000:80"     # Exposed only to localhost; reverse proxy connects here
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Ports are bound to `127.0.0.1` only — containers are not reachable directly from the network; all traffic enters through the reverse proxy.

---

## Environment Variables

Both services are configured via a single `.env` file in `/opt/project-alpha/`.

```env
# ── Image tags ──────────────────────────────────────────────
API_TAG=v1.0.0
WEB_TAG=v1.0.0

# ── Backend ─────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/project_alpha
OIDC_ISSUER_URL=https://auth.example.com/application/o/alpha/
OIDC_AUDIENCE=project-alpha
BASE_CURRENCY=USD
FRANKFURTER_BASE_URL=https://api.frankfurter.app
SCHEDULER_TIMEZONE=UTC
ENVIRONMENT=production

# Local auth — disabled in production
LOCAL_AUTH_ENABLED=false
# LOCAL_AUTH_SECRET=  ← leave unset in production

# ── Frontend (runtime injection) ─────────────────────────────
VITE_API_BASE_URL=https://app.example.com/api/v1
VITE_OIDC_AUTHORITY=https://auth.example.com/application/o/alpha/
VITE_OIDC_CLIENT_ID=<authentik-client-id>
VITE_OIDC_REDIRECT_URI=https://app.example.com/callback
VITE_OIDC_POST_LOGOUT_URI=https://app.example.com/
```

> The `.env` file must never be committed to source control. Add it to `.gitignore`.

---

## Reverse Proxy Configuration

The reverse proxy (not managed by this project) should:

- Terminate TLS and forward plain HTTP to the containers
- Route traffic:

| Path prefix | Upstream |
|-------------|----------|
| `/api/` | `http://127.0.0.1:8000` |
| `/` (all other) | `http://127.0.0.1:3000` |

- Pass standard forwarding headers: `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Real-IP`
- The backend trusts these headers when `ENVIRONMENT=production` is set

---

## Database Setup

Before the first deployment, the external PostgreSQL instance requires a dedicated database and user:

```sql
CREATE DATABASE project_alpha;
CREATE USER alpha_user WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE project_alpha TO alpha_user;
```

Migrations are run automatically by the API container at startup via the entrypoint:

```
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Migrations are idempotent — restarting the container is safe.

---

## Deployment Procedure

### First Deploy

```bash
# On the host
mkdir -p /opt/project-alpha
cd /opt/project-alpha

# Create .env from the template above
nano .env

# Pull images and start
docker compose pull
docker compose up -d
```

### Updating to a New Version

```bash
cd /opt/project-alpha

# Update the tag(s) in .env
nano .env   # set API_TAG=v1.1.0 and/or WEB_TAG=v1.1.0

# Pull new images and recreate containers
docker compose pull
docker compose up -d --no-deps api    # rolling update, api only
docker compose up -d --no-deps web    # rolling update, web only
```

### Rollback

```bash
# In .env, revert the tag to the previous version
nano .env   # e.g. API_TAG=v1.0.0

docker compose pull
docker compose up -d --no-deps api
```

---

## Health Checks

| Endpoint | Container | Returns |
|----------|-----------|---------|
| `GET /health` | `alpha-api` | `200 {"status": "ok", "db": "ok", "scheduler": "ok"}` |
| `GET /` | `alpha-web` | `200` (Nginx default page) |

The `/health` endpoint checks:
- Database connectivity (simple `SELECT 1`)
- APScheduler running state

This endpoint is unauthenticated and should **not** be exposed publicly through the reverse proxy.

---

## Logging

- Both containers write logs to **stdout/stderr** (Docker default).
- View logs with:
  ```bash
  docker compose logs -f api
  docker compose logs -f web
  ```
- Log rotation is handled by Docker's default `json-file` driver. To configure limits, add to `docker-compose.yml`:
  ```yaml
  logging:
    driver: json-file
    options:
      max-size: "50m"
      max-file: "5"
  ```

---

## Security Notes

- Containers bind only to `127.0.0.1` — not exposed to the public network directly.
- `.env` file permissions should be restricted: `chmod 600 /opt/project-alpha/.env`
- `LOCAL_AUTH_ENABLED` must be `false` (or unset) in production.
- The `/health` endpoint must not be publicly routed through the reverse proxy.
- Registry credentials are stored as Gitea Actions secrets, not in any committed file.
