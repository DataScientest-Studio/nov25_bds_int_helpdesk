#!/bin/bash
cd "/home/openclaw/.openclaw/workspace/projects/Employee performance 5"
exec ./venv/bin/streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
