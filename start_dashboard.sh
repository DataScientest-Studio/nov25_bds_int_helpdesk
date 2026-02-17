#!/bin/bash
# Start Help Desk Performance Dashboard - Employee Performance 2
cd "/home/openclaw/.openclaw/workspace/projects/Employee performance 2/Employee performance"
source venv/bin/activate
exec streamlit run streamlit_app/app.py --server.port 8502 --server.headless true --server.address 0.0.0.0
