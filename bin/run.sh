#!/usr/bin/env bash
set -e

PORT="${PORT:-5000}"
VENV="flask-metrics-venv"
SCRIPT_DIR="$(dirname "$0")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Create venv if missing
if [ ! -d "$VENV" ]; then
    echo ">>> Creating virtual environment: $VENV ..."
    python3 -m venv "$VENV"
fi

# Activate and install deps
source "$VENV/bin/activate"
pip install -q flask prometheus-client

# Kill old process on the same port
OLD_PID=$(lsof -ti :"$PORT" 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
    echo ">>> Killing old process on port $PORT (PID: $OLD_PID) ..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
fi

echo ">>> Starting app on port $PORT ..."
python app.py
