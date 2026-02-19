"""
A – Overview
A1: Tickets Snapshot | A2: People Snapshot
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

st.set_page_config(page_title="Overview", page_icon="🏠", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Auto-Refresh interval
REFRESH_INTERVAL = 10  # seconds

# Database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


def get_db_connection():
    """Database connection."""
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data_a1():
    """Load dashboard data from DB (A1)."""
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
        'recent_tickets': pd.read_sql("""
            SELECT ticket_num, title, status, priority, assignee, created_at
            FROM tickets
            ORDER BY created_at DESC
            LIMIT 10
        """, conn),
        'priority_distribution': pd.read_sql("""
            SELECT priority, COUNT(*) as count
            FROM tickets
            GROUP BY priority
        """, conn),
    }

    conn.close()
    return data


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data_a2():
    """Load people snapshot data (A2)."""
    if not DB_PATH.exists():
        return None

    conn = get_db_connection()

    data = {
        'employees': pd.read_sql("SELECT COUNT(*) as count FROM employees", conn).iloc[0]['count'],
        'red_employees': pd.read_sql(
            "SELECT COUNT(*) as count FROM employees WHERE risk_level = 'RED'",
            conn
        ).iloc[0]['count'],
        'yellow_employees': pd.read_sql(
            "SELECT COUNT(*) as count FROM employees WHERE risk_level = 'YELLOW'",
            conn
        ).iloc[0]['count'],
        'green_employees': pd.read_sql(
            "SELECT COUNT(*) as count FROM employees WHERE risk_level = 'GREEN'",
            conn
        ).iloc[0]['count'],
        'risk_dist': pd.read_sql("""
            SELECT risk_level, COUNT(*) as count
            FROM employees
            GROUP BY risk_level
        """, conn),
        'top_employees': pd.read_sql("""
            SELECT name, avg_score, ticket_count, risk_level
            FROM employees
            ORDER BY avg_score DESC
            LIMIT 10
        """, conn),
        'bottom_employees': pd.read_sql("""
            SELECT name, avg_score, ticket_count, risk_level
            FROM employees
            WHERE risk_level IN ('RED', 'YELLOW')
            ORDER BY avg_score ASC
            LIMIT 10
        """, conn),
        'alerts': pd.read_sql("""
            SELECT * FROM alerts
            WHERE acknowledged = 0
            ORDER BY created_at DESC
            LIMIT 5
        """, conn),
    }

    conn.close()
    return data


# ─── Page Header ────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([6, 2, 2])
with col1:
    page_header(e("🏠 ") + "Overview – Tickets & People Snapshot", help_key='dashboard')
with col2:
    auto_refresh = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=True)
with col3:
    st.caption(f"{get_text('last_update')}: {datetime.now().strftime('%H:%M:%S')}")


# ════════════════════════════════════════════════════════════════════════════
# A1 – Tickets Snapshot
# ════════════════════════════════════════════════════════════════════════════
st.header("A1 – Tickets Snapshot")

data_a1 = load_data_a1()

if data_a1 is None:
    st.error(e("❌ ") + get_text('database_not_found') + " `python src/database/db_setup.py`")
else:
    # KPI Cards – Ticket Status
    section_header(e("📊 ") + get_text('live_kpis'), 'live_kpis')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(e("🎫 ") + get_text('tickets_total'), data_a1['total_tickets'])
    with col2:
        st.metric(e("📂 ") + get_text('open'), data_a1['open_tickets'])
    with col3:
        st.metric(e("✅ ") + get_text('resolved_today'), data_a1['resolved_today'])
    with col4:
        st.metric(e("🚨 ") + get_text('critical'), data_a1['critical_open'],
                  delta=get_text('attention') if data_a1['critical_open'] > 0 else None,
                  delta_color="inverse")

    st.markdown("---")

    # Priority Distribution
    section_header(e("📈 ") + get_text('priority_distribution'), 'priority_dist')

    if not data_a1['priority_distribution'].empty:
        priority_names = {
            1: '🔴 ' + get_text('critical'),
            2: '🟠 ' + get_text('high'),
            3: '🟡 ' + get_text('medium'),
            4: '🟢 ' + get_text('low'),
            5: '⚪ ' + get_text('minimal'),
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
        data_a1['priority_distribution']['priority_name'] = data_a1['priority_distribution']['priority'].map(
            lambda x: priority_names.get(x, priority_names.get(str(x), f'❓ {x}'))
        )
        fig = px.bar(
            data_a1['priority_distribution'],
            x='priority_name',
            y='count'
        )
        fig.update_traces(marker_color='#3498db')
        fig.update_layout(height=300, margin=dict(t=20, b=20), showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Newest Tickets
    section_header(e("🎫 ") + get_text('newest_tickets'), 'ticket_list')

    if not data_a1['recent_tickets'].empty:
        df_a1 = data_a1['recent_tickets'].copy()
        df_a1['priority'] = df_a1['priority'].map({1: e('🔴'), 2: e('🟠'), 3: e('🟡'), 4: e('🟢'), 5: e('⚪')})
        st.dataframe(
            df_a1,
            column_config={
                'ticket_num': st.column_config.TextColumn("Ticket"),
                'title': st.column_config.TextColumn(get_text('title_col')),
                'status': st.column_config.TextColumn(get_text('status')),
                'priority': st.column_config.TextColumn(get_text('priority')),
                'assignee': st.column_config.TextColumn(get_text('assignee')),
                'created_at': st.column_config.DatetimeColumn(get_text('created'), format="DD.MM.YY HH:mm"),
            },
            width="stretch",
            hide_index=True
        )


# ════════════════════════════════════════════════════════════════════════════
# A2 – People Snapshot
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("A2 – People Snapshot")

data_a2 = load_data_a2()

if data_a2 is None:
    st.error(e("❌ ") + get_text('database_not_found'))
else:
    # Employee Risk KPIs
    section_header(e("👥 ") + get_text('team_overview'), 'team_stats')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(e("👥 ") + get_text('employees'), data_a2['employees'])
    with col2:
        st.metric("🟢 GREEN", data_a2['green_employees'])
    with col3:
        st.metric("🟡 YELLOW", data_a2['yellow_employees'],
                  delta="Training" if data_a2['yellow_employees'] > 0 else None)
    with col4:
        st.metric("🔴 Risk RED", data_a2['red_employees'],
                  delta=get_text('action_needed') if data_a2['red_employees'] > 0 else None,
                  delta_color="inverse")

    st.markdown("---")

    # Risk Distribution Chart
    col1, col2 = st.columns(2)

    with col1:
        section_header(e("📊 ") + get_text('risk_distribution'))
        if not data_a2['risk_dist'].empty:
            colors = {'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            fig = px.pie(
                data_a2['risk_dist'],
                values='count',
                names='risk_level',
                color='risk_level',
                color_discrete_map=colors,
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")

    with col2:
        section_header(e("⚠️ ") + "RED & YELLOW Employees")
        if not data_a2['bottom_employees'].empty:
            risk_icons = {'GREEN': e('🟢'), 'YELLOW': e('🟡'), 'RED': e('🔴')}
            display = data_a2['bottom_employees'].copy()
            display['risk_level'] = display['risk_level'].map(lambda x: f"{risk_icons.get(x, e('⚪'))} {x}")
            st.dataframe(
                display,
                column_config={
                    'name': st.column_config.TextColumn(get_text('employees')),
                    'avg_score': st.column_config.NumberColumn("Ø Score", format="%.2f"),
                    'ticket_count': st.column_config.NumberColumn(get_text('tickets')),
                    'risk_level': st.column_config.TextColumn(get_text('risk_level')),
                },
                width="stretch",
                hide_index=True,
                height=350
            )

    st.markdown("---")

    # Top Performers
    section_header(e("🏆 ") + get_text('top_performers'))
    if not data_a2['top_employees'].empty:
        risk_icons = {'GREEN': e('🟢'), 'YELLOW': e('🟡'), 'RED': e('🔴')}
        display = data_a2['top_employees'].copy()
        display['risk_level'] = display['risk_level'].map(lambda x: f"{risk_icons.get(x, e('⚪'))} {x}")
        st.dataframe(
            display,
            column_config={
                'name': st.column_config.TextColumn(get_text('employees')),
                'avg_score': st.column_config.NumberColumn("Ø Score", format="%.2f"),
                'ticket_count': st.column_config.NumberColumn(get_text('tickets')),
                'risk_level': st.column_config.TextColumn(get_text('risk_level')),
            },
            width="stretch",
            hide_index=True
        )


# ─── Auto-Refresh (once, at the bottom) ─────────────────────────────────────
if auto_refresh:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Footer
render_footer()
