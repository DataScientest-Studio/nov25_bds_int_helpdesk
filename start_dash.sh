#!/bin/bash
# HelpDesk Performance Monitor - Dash Dashboard Starter
# Port: 8502

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/dash_app.log"
PID_FILE="$SCRIPT_DIR/logs/dash_app.pid"

echo "=========================================="
echo "  HelpDesk Performance Monitor (Dash)"
echo "  Port: 8502"
echo "  Log:  $LOG_FILE"
echo "=========================================="

mkdir -p "$SCRIPT_DIR/logs"

# Try systemd first
if systemctl --user is-active --quiet dash-helpdesk.service 2>/dev/null; then
    echo "Service already running via systemd"
    echo "Use: systemctl --user status dash-helpdesk.service"
    echo "Dashboard: http://localhost:8502"
    exit 0
fi

# Kill existing process if running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping existing process (PID: $OLD_PID)..."
        kill "$OLD_PID"
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# Start via systemd if available
if systemctl --user list-unit-files dash-helpdesk.service &>/dev/null; then
    echo "Starting via systemd..."
    systemctl --user start dash-helpdesk.service
    sleep 3
    systemctl --user status dash-helpdesk.service --no-pager | head -10
else
    # Fallback: start directly
    echo "Starting directly..."
    export PYTHONPATH="$SCRIPT_DIR/venv/lib/python3.12/site-packages"
    cd "$SCRIPT_DIR/dash_app"
    /usr/bin/python3.12 app.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Started with PID: $(cat $PID_FILE)"
fi

echo ""
echo "Dashboard URL: http://localhost:8502"
echo "Logs: journalctl --user -u dash-helpdesk.service -f"
