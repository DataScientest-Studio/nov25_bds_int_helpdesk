"""
Settings & Admin
System settings and admin functions.
Cloud-compatible version.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sqlite3
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"

# Detect if running on Streamlit Cloud
IS_CLOUD = os.environ.get('STREAMLIT_SHARING_MODE') or '/mount/src' in str(PROJECT_ROOT)

# Page header
page_header(
    e("⚙️ ") + get_text('settings_admin'),
    help_key='settings_page'
)

# Show environment info
if IS_CLOUD:
    st.info("☁️ Running on Streamlit Cloud - Some local features are disabled")

st.markdown("---")

# Database Info
section_header(e("🗄️ ") + get_text('database'))

if DB_PATH.exists():
    try:
        conn = sqlite3.connect(DB_PATH)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            count = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
            st.metric(e("🎫 ") + get_text('tickets'), count)
        
        with col2:
            count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            st.metric(e("👥 ") + get_text('employees'), count)
        
        with col3:
            count = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
            st.metric(e("💬 ") + get_text('comments'), count)
        
        with col4:
            count = conn.execute("SELECT COUNT(*) FROM status_history").fetchone()[0]
            st.metric(e("📜 ") + get_text('status_changes'), count)
        
        conn.close()
        
        # DB file size
        size_mb = DB_PATH.stat().st_size / (1024 * 1024)
        st.caption(f"{e('💾')} {get_text('file_size')}: {size_mb:.2f} MB")
    except Exception as ex:
        st.warning(f"Database read error: {ex}")
else:
    st.warning(e("⚠️ ") + get_text('database_not_found'))

st.markdown("---")

# Local-only features (hidden on cloud)
if not IS_CLOUD:
    import subprocess
    
    # Simulation Controls
    section_header(e("🎬 ") + get_text('simulation'), 'simulation')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{get_text('database_simulator')}**")
        
        if st.button(e("🔄 ") + get_text('simulation_reset'), type="primary", use_container_width=True):
            with st.spinner(get_text('resetting_database')):
                venv_python = PROJECT_ROOT / "venv" / "bin" / "python"
                
                if venv_python.exists():
                    result = subprocess.run(
                        [str(venv_python), "src/database/db_setup.py"],
                        cwd=str(PROJECT_ROOT),
                        capture_output=True,
                        text=True
                    )
                    
                    subprocess.run(
                        ["systemctl", "--user", "restart", "helpdesk-simulator"],
                        capture_output=True
                    )
                    
                    st.cache_data.clear()
                    
                    if result.returncode == 0:
                        st.success(e("✅ ") + get_text('simulation_restarted'))
                        st.balloons()
                    else:
                        st.error(e("❌ ") + f"{get_text('error')}: {result.stderr}")
                else:
                    st.error("venv not found")

    with col2:
        st.markdown(f"**{get_text('simulator_service')}**")
        
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button(e("▶️ ") + get_text('start'), use_container_width=True):
                subprocess.run(["systemctl", "--user", "start", "helpdesk-simulator"])
                st.success(get_text('started'))
        with col2b:
            if st.button(e("⏹️ ") + get_text('stop'), use_container_width=True):
                subprocess.run(["systemctl", "--user", "stop", "helpdesk-simulator"])
                st.warning(get_text('stopped'))

    with col3:
        st.markdown(f"**{get_text('status')}**")
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "helpdesk-simulator"],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        if status == "active":
            st.success(e("🟢 ") + get_text('simulator_running'))
        else:
            st.error(e("🔴 ") + get_text('simulator_stopped'))

    st.markdown("---")

    # Services Status
    section_header(e("🔧 ") + get_text('services'), 'services')

    services = ['helpdesk-dashboard', 'helpdesk-api', 'helpdesk-simulator']

    for service in services:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", service],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            icon = e("🟢") if status == "active" else e("🔴")
            st.markdown(f"{icon} **{service}**")
        with col2:
            st.caption(status)
        with col3:
            if st.button(e("🔄"), key=f"restart_{service}", help=f"{get_text('restart')} {service}"):
                subprocess.run(["systemctl", "--user", "restart", service])
                st.rerun()

# App Info (always visible)
st.markdown("---")
section_header(e("ℹ️ ") + "App Info")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    - **Python:** {sys.version.split()[0]}
    - **Streamlit:** {st.__version__}
    - **Environment:** {'☁️ Cloud' if IS_CLOUD else '🖥️ Local'}
    """)
with col2:
    st.markdown(f"""
    - **Project:** Employee Performance
    - **Version:** 2.0
    - **Last Update:** Feb 2026
    """)

# Footer
render_footer()
