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
    get_text, get_help, init_session_state, e, get_nav_items
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
    st.info(e("☁️ ") + get_text('cloud_info'))

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

# Page Visibility Settings
section_header(e("👁️ ") + get_text('page_visibility'))

nav_items = get_nav_items()
visible_pages = st.session_state.get('visible_pages', {})

# Create columns for toggles
col1, col2 = st.columns(2)

for i, (page_file, trans_key, emoji) in enumerate(nav_items):
    # Skip Settings page (always visible)
    if trans_key == 'nav_settings':
        continue
    
    page_name = get_text(trans_key)
    current_state = visible_pages.get(trans_key, True)
    
    with col1 if i % 2 == 0 else col2:
        new_state = st.toggle(
            f"{emoji} {page_name}",
            value=current_state,
            key=f"vis_{trans_key}"
        )
        
        if new_state != current_state:
            st.session_state.visible_pages[trans_key] = new_state
            st.rerun()

st.caption(get_text('page_visibility_hint'))

st.markdown("---")

# Local-only features (hidden on cloud)
if not IS_CLOUD:
    import subprocess
    
    # Simulation Controls
    section_header(e("🎬 ") + get_text('simulation'), 'simulation')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{get_text('database_simulator')}**")
        
        if st.button(e("🔄 ") + get_text('simulation_reset'), type="primary", width="stretch"):
            with st.spinner(get_text('resetting_database')):
                # Clear Streamlit cache
                st.cache_data.clear()
                
                # Restart simulator service if available
                subprocess.run(
                    ["systemctl", "--user", "restart", "helpdesk-simulator"],
                    capture_output=True
                )
                
                st.success(e("✅ ") + get_text('simulation_restarted'))
                st.balloons()

    with col2:
        st.markdown(f"**{get_text('simulator_service')}**")
        
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button(e("▶️ ") + get_text('start'), width="stretch"):
                subprocess.run(["systemctl", "--user", "start", "helpdesk-simulator"])
                st.success(get_text('started'))
        with col2b:
            if st.button(e("⏹️ ") + get_text('stop'), width="stretch"):
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
section_header(e("ℹ️ ") + get_text('app_info'))

col1, col2 = st.columns(2)
with col1:
    env_label = get_text('cloud') if IS_CLOUD else get_text('local')
    env_icon = "☁️" if IS_CLOUD else "🖥️"
    st.markdown(f"""
    - **Python:** {sys.version.split()[0]}
    - **Streamlit:** {st.__version__}
    - **{get_text('environment')}:** {env_icon} {env_label}
    """)
with col2:
    st.markdown(f"""
    - **{get_text('project')}:** Employee Performance
    - **{get_text('version')}:** 2.0
    - **{get_text('last_updated')}:** Feb 2026
    """)

# Footer
render_footer()
