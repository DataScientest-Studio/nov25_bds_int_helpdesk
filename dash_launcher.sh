#!/bin/bash
# Dash Launcher - activates venv and starts app
set -e

SCRIPT_DIR="/home/openclaw/.openclaw/workspace/projects/Employee performance 3"
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR/dash_app"
exec python3.12 app.py
