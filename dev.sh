#!/usr/bin/env bash
# dev.sh — start backend + frontend in parallel for local development
#
# Usage: ./dev.sh
#
# Requirements:
#   Backend:  uv (https://github.com/astral-sh/uv), Python 3.12+, running PostgreSQL
#   Frontend: Node.js 20+
#
# The script forwards SIGINT (Ctrl-C) to both child processes and waits
# for both to exit cleanly before returning.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

# ── Colour helpers ────────────────────────────────────────────────────────────
# $'...' (ANSI-C quoting) makes bash expand \033 into the real ESC byte so
# that the variables work correctly inside sed substitutions.
RESET=$'\033[0m'
BOLD=$'\033[1m'
BLUE=$'\033[0;34m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
RED=$'\033[0;31m'

info()    { echo -e "${BOLD}${BLUE}[dev]${RESET} $*"; }
success() { echo -e "${BOLD}${GREEN}[dev]${RESET} $*"; }
warn()    { echo -e "${BOLD}${YELLOW}[dev]${RESET} $*"; }
error()   { echo -e "${BOLD}${RED}[dev]${RESET} $*" >&2; }

# ── Pre-flight checks ─────────────────────────────────────────────────────────
check_command() {
    if ! command -v "$1" &>/dev/null; then
        error "Required command not found: $1"
        error "Install it and try again."
        exit 1
    fi
}

check_command uv
check_command node
check_command npm

# ── Dev uses SQLite in-memory — no external database required ─────────────────
# DATABASE_URL is set in the environment below; backend/.env is NOT needed for
# dev because we override the database URL here. Other settings (OIDC etc.)
# fall back to their defaults, and LOCAL_AUTH_ENABLED is forced on.
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export LOCAL_AUTH_ENABLED="true"
export LOCAL_AUTH_SECRET="${LOCAL_AUTH_SECRET:-dev-secret-change-in-production}"
export DEBUG="true"

# ── Frontend node_modules check ───────────────────────────────────────────────
if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    info "Installing frontend dependencies..."
    (cd "$FRONTEND_DIR" && npm install)
fi

# ── Backend venv / deps check ─────────────────────────────────────────────────
if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
    info "Installing backend dependencies..."
    (cd "$BACKEND_DIR" && uv sync)
fi

# ── Process management ────────────────────────────────────────────────────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    info "Shutting down..."
    [[ -n "$BACKEND_PID" ]]  && kill "$BACKEND_PID"  2>/dev/null || true
    [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID"  2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
    success "All processes stopped."
}

trap cleanup SIGINT SIGTERM

# ── Dev user credentials ──────────────────────────────────────────────────────
DEV_EMAIL="${DEV_EMAIL:-dev@example.com}"
DEV_PASSWORD="${DEV_PASSWORD:-password}"
DEV_NAME="${DEV_NAME:-Dev User}"

# ── Start backend ─────────────────────────────────────────────────────────────
info "Starting backend on http://localhost:8000 ..."
info "Database: SQLite in-memory (schema created automatically on startup)"
(
    cd "$BACKEND_DIR"
    # No Alembic needed — main.py creates the schema via Base.metadata.create_all
    # when DATABASE_URL starts with "sqlite".
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
        2>&1 | sed "s/^/${BLUE}[api]${RESET} /"
) &
BACKEND_PID=$!

# ── Start frontend ────────────────────────────────────────────────────────────
info "Starting frontend on http://localhost:5173 ..."
(
    cd "$FRONTEND_DIR"
    npm run dev 2>&1 | sed "s/^/${GREEN}[web]${RESET} /"
) &
FRONTEND_PID=$!

# ── Print banner after both services have had time to start ──────────────────
# Dev user is seeded automatically by the backend on startup (see main.py).
(
    sleep 5

    # Print the ready banner as the very last output
    echo ""
    success "Everything is up."
    echo ""
    echo -e "  ${BOLD}API${RESET}      → http://localhost:8000"
    echo -e "  ${BOLD}API docs${RESET} → http://localhost:8000/docs"
    echo -e "  ${BOLD}Frontend${RESET} → http://localhost:5173"
    echo ""
    echo -e "  ${BOLD}Dev login${RESET}"
    echo -e "    Email:    ${YELLOW}${DEV_EMAIL}${RESET}"
    echo -e "    Password: ${YELLOW}${DEV_PASSWORD}${RESET}"
    echo ""
    echo -e "  Override with DEV_EMAIL / DEV_PASSWORD env vars."
    echo -e "  Press ${BOLD}Ctrl-C${RESET} to stop all services."
    echo ""
) &

# ── Wait — exit if either child dies unexpectedly ─────────────────────────────
wait -n "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
STATUS=$?

if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    error "Backend process exited unexpectedly (exit $STATUS)"
fi
if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    error "Frontend process exited unexpectedly (exit $STATUS)"
fi

cleanup
exit $STATUS
