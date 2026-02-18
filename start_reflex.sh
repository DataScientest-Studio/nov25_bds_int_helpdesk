#!/bin/bash
# ============================================================
# HelpDesk Performance Monitor - Reflex Dashboard
# Port: 3000 (frontend) | 8000 (backend)
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFLEX_DIR="$PROJECT_DIR/reflex_app"
VENV="$PROJECT_DIR/venv"
PYTHON="$VENV/bin/python3"

echo "==================================================="
echo " HelpDesk Performance Monitor (Reflex)"
echo " Dir: $REFLEX_DIR"
echo " Frontend: http://localhost:3000"
echo " Backend:  http://localhost:8000"
echo "==================================================="

# Check venv
if [ ! -f "$PYTHON" ]; then
    echo "[ERROR] Python venv not found at $VENV"
    exit 1
fi

# Check Reflex
if ! "$PYTHON" -c "import reflex" 2>/dev/null; then
    echo "[INFO] Installing Reflex..."
    "$PYTHON" -m pip install reflex
fi

# Change to reflex app directory
cd "$REFLEX_DIR"

# Initialize if needed (first run - checks for .web dir)
if [ ! -d ".web" ]; then
    echo "[INFO] Initializing Reflex project (downloading Bun/Node.js)..."
    "$PYTHON" -m reflex init
fi

# Run in production mode
echo "[INFO] Starting Reflex on port 3000..."
exec "$PYTHON" -m reflex run \
    --env prod \
    --frontend-port 3000 \
    --backend-port 8000 \
    --backend-host 0.0.0.0
