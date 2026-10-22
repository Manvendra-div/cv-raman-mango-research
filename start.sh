#!/usr/bin/env bash
# ==============================================================================
# Zone-Aware Mango Soil Intelligence and Yield Gap DSS
# Start script for Linux / macOS
#
#   ./start.sh                 -> install if needed, start API + dashboard
#   ./start.sh --install       -> force (re)install dependencies
#   ./start.sh --tests         -> run pytest before starting
#   ./start.sh --backend-only  -> API only
#   ./start.sh --frontend-only -> dashboard only
#   ./start.sh --simple-frontend -> minimal frontend/app.py instead of full dashboard
#   ./start.sh --api-port 9000 --ui-port 8601
# ==============================================================================
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

API_PORT="${API_PORT:-8000}"
UI_PORT="${STREAMLIT_PORT:-8501}"
API_HOST="${API_HOST:-127.0.0.1}"
DO_INSTALL=0
DO_TESTS=0
RUN_BACKEND=1
RUN_FRONTEND=1
SIMPLE_FRONTEND=0
API_PID=""
UI_PID=""

usage() {
  sed -n '2,13p' "$0" | sed 's/^#\{1,\} \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install)        DO_INSTALL=1 ;;
    --tests)          DO_TESTS=1 ;;
    --backend-only)   RUN_FRONTEND=0 ;;
    --frontend-only)  RUN_BACKEND=0 ;;
    --simple-frontend) SIMPLE_FRONTEND=1 ;;
    --api-port)       API_PORT="${2:?--api-port needs a value}"; shift ;;
    --ui-port)        UI_PORT="${2:?--ui-port needs a value}"; shift ;;
    -h|--help)        usage; exit 0 ;;
    *) echo "Unknown option: $1"; echo; usage; exit 1 ;;
  esac
  shift
done

say() { printf '\033[1;36m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$1"; }
die() { printf '\033[1;31m[x]\033[0m %s\n' "$1" >&2; exit 1; }

# ------------------------------------------------------------------------------
# 1. Python interpreter
# ------------------------------------------------------------------------------
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  PYTHON="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON="$(command -v python)"
else
  die "Python not found. Install Python 3.11+ and re-run."
fi
say "Python: $PYTHON ($("$PYTHON" --version 2>&1))"

if [[ ! -x "$PROJECT_ROOT/.venv/bin/python" ]] && [[ ! -d "$PROJECT_ROOT/.venv" ]]; then
  say "Creating virtual environment .venv"
  "$PYTHON" -m venv "$PROJECT_ROOT/.venv" || die "venv creation failed"
  PYTHON="$PROJECT_ROOT/.venv/bin/python"
fi

# ------------------------------------------------------------------------------
# 2. Dependencies
# ------------------------------------------------------------------------------
deps_ok=0
if "$PYTHON" -c "import fastapi, uvicorn, streamlit, pandas, sklearn" >/dev/null 2>&1; then
  deps_ok=1
fi
if [[ $DO_INSTALL -eq 1 || $deps_ok -eq 0 ]]; then
  say "Installing dependencies from requirements.txt (this can take a few minutes)"
  "$PYTHON" -m pip install --upgrade pip --quiet || warn "pip upgrade skipped"
  "$PYTHON" -m pip install -r requirements.txt || die "Dependency install failed"
else
  say "Dependencies already installed (use --install to force reinstall)"
fi

# ------------------------------------------------------------------------------
# 3. Optional tests
# ------------------------------------------------------------------------------
if [[ $DO_TESTS -eq 1 ]]; then
  say "Running tests"
  "$PYTHON" -m pytest -q || warn "Tests failed - continuing anyway"
fi

mkdir -p logs

cleanup() {
  [[ -n "$UI_PID" ]] && kill "$UI_PID" 2>/dev/null
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null
}
trap cleanup EXIT INT TERM

# ------------------------------------------------------------------------------
# 4. Backend API
# ------------------------------------------------------------------------------
if [[ $RUN_BACKEND -eq 1 ]]; then
  say "Starting API on http://${API_HOST}:${API_PORT}  (log: logs/api.log)"
  "$PYTHON" -m uvicorn backend.app.main:app --host "$API_HOST" --port "$API_PORT" \
      >logs/api.log 2>&1 &
  API_PID=$!

  ready=0
  for _ in $(seq 1 40); do
    if curl -fsS "http://${API_HOST}:${API_PORT}/health" >/dev/null 2>&1; then ready=1; break; fi
    kill -0 "$API_PID" 2>/dev/null || break
    sleep 1
  done
  if [[ $ready -eq 1 ]]; then
    say "API is up (pid $API_PID)"
  else
    warn "API did not answer /health in time. Check logs/api.log"
    tail -n 20 logs/api.log 2>/dev/null
  fi
fi

# ------------------------------------------------------------------------------
# 5. Frontend
# ------------------------------------------------------------------------------
if [[ $RUN_FRONTEND -eq 1 ]]; then
  export DSS_API_URL="${DSS_API_URL:-http://127.0.0.1:${API_PORT}}"
  if [[ $SIMPLE_FRONTEND -eq 1 ]]; then
    APP_FILE="frontend/app.py"
  else
    APP_FILE="src/dss/dashboard.py"
  fi
  say "Starting dashboard on http://127.0.0.1:${UI_PORT}  (${APP_FILE})"
  "$PYTHON" -m streamlit run "$APP_FILE" --server.port "$UI_PORT" \
      --server.address 127.0.0.1 >logs/frontend.log 2>&1 &
  UI_PID=$!
fi

echo
say "Ready."
[[ $RUN_BACKEND -eq 1 ]] && echo "    API      : http://${API_HOST}:${API_PORT}  (docs: /docs)"
[[ $RUN_FRONTEND -eq 1 ]] && echo "    Dashboard: http://127.0.0.1:${UI_PORT}"
echo "    Logs     : logs/api.log , logs/frontend.log"
echo "    Stop     : press Ctrl+C"
echo

if [[ $RUN_BACKEND -eq 1 || $RUN_FRONTEND -eq 1 ]]; then
  wait
fi
