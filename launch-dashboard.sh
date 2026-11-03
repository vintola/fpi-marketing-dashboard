#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${FPI_DASHBOARD_PORT:-8765}"
HOST="${FPI_DASHBOARD_HOST:-127.0.0.1}"
URL="http://${HOST}:${PORT}"
VENV_STREAMLIT="${APP_DIR}/.venv/bin/streamlit"
PID_FILE="${APP_DIR}/.streamlit.pid"
LOG_FILE="${APP_DIR}/.streamlit.log"

open_url() {
  if [[ "${FPI_NO_BROWSER:-0}" == "1" ]]; then
    return 0
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
  fi
}

notify() {
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "FPI Marketing Dashboard" "$1" >/dev/null 2>&1 || true
  fi
}

is_healthy() {
  [[ "$(curl -fsS "${URL}/_stcore/health" 2>/dev/null || true)" == "ok" ]]
}

if [[ "${1:-}" == "stop" ]]; then
  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    notify "Dashboard stopped."
  else
    notify "No running dashboard found."
  fi
  exit 0
fi

if is_healthy; then
  open_url
  exit 0
fi

if [[ ! -x "$VENV_STREAMLIT" ]]; then
  notify "Streamlit environment is missing. Follow the setup steps in README.md."
  exit 1
fi

cd "$APP_DIR"
nohup "$VENV_STREAMLIT" run app.py \
  --server.address "$HOST" \
  --server.port "$PORT" \
  --server.headless true \
  >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

for _ in $(seq 1 60); do
  if is_healthy; then
    open_url
    exit 0
  fi
  sleep 0.5
done

notify "Dashboard failed to start. See ${LOG_FILE}."
exit 1
