"""
Live Dashboard
Real-time overview with auto-refresh.
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import time
import sys

# Import components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e, maybe_emoji
)

st.set_page_config(page_title="Live Dashboard", page_icon="🏠", layout="wide")

# Initialize settings
init_session_state()

# Auto-Refresh interval
REFRESH_INTERVAL = 10  # seconds

# Database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


def get_db_connection():
    """Database connection."""
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_dashboard_data():
    """Load dashboard data from DB."""
    if not DB_PATH.exists():
        return None
    
    conn = get_db_connection()
    
    data = {
        'total_tickets': pd.read_sql("SELECT COUNT(*) as count FROM tickets", conn).iloc[0]['count'],
        'open_tickets': pd.read_sql(
            "SELECT COUNT(*) as count FROM tickets WHERE status IN ('Open', 'In Progress', 'Waiting', 'In Review')", 
            conn
        ).iloc[0]['count'],
        'resolved_today': pd.read_sql(
            "SELECT COUNT(*) as count FROM tickets WHERE DATE(resolved_at) = DATE('now')", 
            conn
        ).iloc[0]['count'],
        'critical_open': pd.read_sql(
            "SELECT COUNT(*) as count FROM tickets WHERE priority = 1 AND status NOT IN ('Closed', 'Resolved')", 
            conn
        ).iloc[0]['count'],
        'employees': pd.read_sql("SELECT COUNT(*) as count FROM employees", conn).iloc[0]['count'],
        'red_employees': pd.read_sql(
            "SELECT COUNT(*) as count FROM employees WHERE risk_level = 'RED'", 
            conn
        ).iloc[0]['count'],
        'recent_tickets': pd.read_sql("""
            SELECT ticket_num, title, status, priority, assignee, created_at 
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 10
        """, conn),
        'status_distribution': pd.read_sql("""
            SELECT status, COUNT(*) as count 
            FROM tickets 
            GROUP BY status
        """, conn),
        'priority_distribution': pd.read_sql("""
            SELECT priority, COUNT(*) as count 
            FROM tickets 
            GROUP BY priority
        """, conn),
        'alerts': pd.read_sql("""
            SELECT * FROM alerts 
            WHERE acknowledged = 0 
            ORDER BY created_at DESC 
            LIMIT 5
        """, conn),
        'recent_activity': pd.read_sql("""
            SELECT 'Status' as type, ticket_num, old_status || ' → ' || new_status as detail, changed_at as time
            FROM status_history sh
            JOIN tickets t ON sh.ticket_id = t.id
            ORDER BY changed_at DESC
            LIMIT 10
        """, conn),
    }
    
    conn.close()
    return data


# Render settings sidebar
render_settings_sidebar()

# Header with auto-refresh indicator
col1, col2, col3 = st.columns([6, 2, 2])
with col1:
    page_header(e("🏠 ") + get_text('live_dashboard'), help_key='dashboard')
with col2:
    auto_refresh = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=True)
with col3:
    st.caption(f"{get_text('last_update')}: {datetime.now().strftime('%H:%M:%S')}")

# Load data
data = load_dashboard_data()

if data is None:
    st.error(e("❌ ") + get_text('database_not_found') + " `python src/database/db_setup.py`")
    st.stop()

# KPI Cards
section_header(e("📊 ") + get_text('live_kpis'), 'live_kpis')

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(e("🎫 ") + get_text('tickets_total'), data['total_tickets'])
with col2:
    st.metric(e("📂 ") + get_text('open'), data['open_tickets'])
with col3:
    st.metric(e("✅ ") + get_text('resolved_today'), data['resolved_today'])
with col4:
    st.metric(e("🚨 ") + get_text('critical'), data['critical_open'], 
              delta=get_text('attention') if data['critical_open'] > 0 else None,
              delta_color="inverse")
with col5:
    st.metric(e("👥 ") + get_text('employees'), data['employees'])
with col6:
    st.metric(e("🔴 ") + "Risk RED", data['red_employees'],
              delta=get_text('action_needed') if data['red_employees'] > 0 else None,
              delta_color="inverse")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    section_header(e("📊 ") + get_text('status_distribution'), 'status_dist')
    
    if not data['status_distribution'].empty:
        fig = px.pie(
            data['status_distribution'],
            values='count',
            names='status',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header(e("📈 ") + get_text('priority_distribution'), 'priority_dist')
    
    if not data['priority_distribution'].empty:
        # Map both numeric and string priority values
        priority_names = {
            # Numeric
            1: '🔴 ' + get_text('critical'), 
            2: '🟠 ' + get_text('high'), 
            3: '🟡 ' + get_text('medium'), 
            4: '🟢 ' + get_text('low'), 
            5: '⚪ ' + get_text('minimal'),
            # String values from database
            'Blocker': '🔴 ' + get_text('critical'),
            'blocker': '🔴 ' + get_text('critical'),
            'pblocker': '🔴 ' + get_text('critical'),
            'High': '🟠 ' + get_text('high'),
            'high': '🟠 ' + get_text('high'),
            'phigh': '🟠 ' + get_text('high'),
            'Medium': '🟡 ' + get_text('medium'),
            'medium': '🟡 ' + get_text('medium'),
            'pmedium': '🟡 ' + get_text('medium'),
            'Low': '🟢 ' + get_text('low'),
            'low': '🟢 ' + get_text('low'),
            'plow': '🟢 ' + get_text('low'),
            'Minimal': '⚪ ' + get_text('minimal'),
            'minimal': '⚪ ' + get_text('minimal'),
            'unknown': '❓ ' + get_text('unknown'),
            'punknown': '❓ ' + get_text('unknown'),
        }
        data['priority_distribution']['priority_name'] = data['priority_distribution']['priority'].map(
            lambda x: priority_names.get(x, priority_names.get(str(x), f'❓ {x}'))
        )
        
        fig = px.bar(
            data['priority_distribution'],
            x='priority_name',
            y='count'
        )
        fig.update_traces(marker_color='#3498db')
        fig.update_layout(height=300, margin=dict(t=20, b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Newest Tickets
section_header(e("🎫 ") + get_text('newest_tickets'), 'ticket_list')

if not data['recent_tickets'].empty:
    # Formatting
    df = data['recent_tickets'].copy()
    df['priority'] = df['priority'].map({1: e('🔴'), 2: e('🟠'), 3: e('🟡'), 4: e('🟢'), 5: e('⚪')})
    
    st.dataframe(
        df,
        column_config={
            'ticket_num': st.column_config.TextColumn("Ticket"),
            'title': st.column_config.TextColumn(get_text('title_col')),
            'status': st.column_config.TextColumn(get_text('status')),
            'priority': st.column_config.TextColumn(get_text('priority')),
            'assignee': st.column_config.TextColumn(get_text('assignee')),
            'created_at': st.column_config.DatetimeColumn(get_text('created'), format="DD.MM.YY HH:mm"),
        },
        use_container_width=True,
        hide_index=True
    )

# Auto-Refresh
if auto_refresh:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Footer
render_footer()
