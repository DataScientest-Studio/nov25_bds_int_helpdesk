#!/bin/bash
# Systemd-compatible runner (no space issues)
export PYTHONPATH="/home/openclaw/.openclaw/workspace/projects/Employee performance 3/venv/lib/python3.12/site-packages"
export VIRTUAL_ENV="/home/openclaw/.openclaw/workspace/projects/Employee performance 3/venv"
export PORT=8502
export PYTHONUNBUFFERED=1
cd "/home/openclaw/.openclaw/workspace/projects/Employee performance 3/dash_app"
exec /usr/bin/python3.12 app.py
