"""
B – Tickets
B1: Ticket Monitor | B2: Ticket Analytics | B3: Ticket Detail
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
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Tickets", page_icon="🎫", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

REFRESH_INTERVAL = 10

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


# ─── Shared cache functions ──────────────────────────────────────────────────

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_tickets_b1(status_filter=None, priority_filter=None, assignee_filter=None, limit=100):
    """Load tickets with filters for B1."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = get_db_connection()
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if status_filter and status_filter != get_text('all'):
        query += " AND status = ?"
        params.append(status_filter)

    if priority_filter and priority_filter != get_text('all'):
        query += " AND priority = ?"
        params.append(int(priority_filter.split()[0]))

    if assignee_filter and assignee_filter != get_text('all'):
        query += " AND assignee = ?"
        params.append(assignee_filter)

    query += f" ORDER BY created_at DESC LIMIT {limit}"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_tickets_b2(status_filter=None, priority_filter=None, assignee_filter=None, limit=500):
    """Load tickets with filters for B2 – supports large datasets (>500)."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = get_db_connection()
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if status_filter and status_filter != get_text('all'):
        query += " AND status = ?"
        params.append(status_filter)

    if priority_filter and priority_filter != get_text('all'):
        query += " AND priority = ?"
        params.append(int(priority_filter.split()[0]))

    if assignee_filter and assignee_filter != get_text('all'):
        query += " AND assignee = ?"
        params.append(assignee_filter)

    if limit > 0:
        query += f" ORDER BY created_at DESC LIMIT {limit}"
    else:
        query += " ORDER BY created_at DESC"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


@st.cache_data(ttl=60)
def get_filter_options_b():
    """Load filter options (shared for B1 and B2)."""
    if not DB_PATH.exists():
        return [], [], []

    conn = get_db_connection()
    statuses = pd.read_sql("SELECT DISTINCT status FROM tickets", conn)['status'].tolist()
    assignees = pd.read_sql("SELECT DISTINCT assignee FROM tickets ORDER BY assignee", conn)['assignee'].tolist()
    conn.close()

    priorities = [
        f"1 {e('🔴')} {get_text('critical')}",
        f"2 {e('🟠')} {get_text('high')}",
        f"3 {e('🟡')} {get_text('medium')}",
        f"4 {e('🟢')} {get_text('low')}",
        f"5 {e('⚪')} {get_text('minimal')}"
    ]
    return statuses, priorities, assignees


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_tickets_list_b3(limit=500):
    """Load ticket list for B3 selector."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = get_db_connection()
    df = pd.read_sql("SELECT id, ticket_num, title FROM tickets ORDER BY created_at DESC LIMIT ?", conn, params=[limit])
    conn.close()
    return df


def get_ticket_details_b3(ticket_id):
    """Load ticket details including comments (B3)."""
    conn = get_db_connection()
    ticket = pd.read_sql(f"SELECT * FROM tickets WHERE id = {ticket_id}", conn)
    comments = pd.read_sql(f"""
        SELECT author, body, sentiment, dialog_act, created_at
        FROM comments
        WHERE ticket_id = {ticket_id}
        ORDER BY created_at DESC
    """, conn)
    history = pd.read_sql(f"""
        SELECT old_status, new_status, changed_by, changed_at
        FROM status_history
        WHERE ticket_id = {ticket_id}
        ORDER BY changed_at DESC
    """, conn)
    conn.close()
    return ticket, comments, history


# ─── Page Header ────────────────────────────────────────────────────────────
page_header(e("🎫 ") + "Tickets – Monitor, Analytics & Detail", help_key='tickets')


# ════════════════════════════════════════════════════════════════════════════
# B1 – Ticket Monitor
# ════════════════════════════════════════════════════════════════════════════
st.header(get_text('ticket_monitor'))

col1, col2, col3 = st.columns([6, 2, 2])
with col1:
    pass  # header already set
with col2:
    auto_refresh_b1 = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=True, key="b1_refresh")
with col3:
    st.caption(f"{e('🕐')} {datetime.now().strftime('%H:%M:%S')}")

# Load filter options
statuses, priorities, assignees = get_filter_options_b()

# Filter bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    status_filter_b1 = st.selectbox(get_text('status'), [get_text('all')] + statuses, key="b1_status")
with col2:
    priority_filter_b1 = st.selectbox(get_text('priority'), [get_text('all')] + priorities, key="b1_priority")
with col3:
    assignee_filter_b1 = st.selectbox(get_text('assignee'), [get_text('all')] + assignees[:50], key="b1_assignee")
with col4:
    limit_b1 = st.selectbox(get_text('count'), [50, 100, 200, 500], index=3, key="b1_limit")

tickets_b1 = load_tickets_b1(status_filter_b1, priority_filter_b1, assignee_filter_b1, limit_b1)

if tickets_b1.empty:
    st.warning(e("⚠️ ") + get_text('no_data'))
    st.info("`python src/database/db_setup.py`")
else:
    # KPIs
    section_header(e("📊 ") + get_text('overview'), 'ticket_stats')

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(e("🎫 ") + get_text('tickets'), len(tickets_b1))
    with col2:
        open_count = len(tickets_b1[tickets_b1['status'].isin(['Open', 'In Progress', 'Waiting'])])
        st.metric(e("📂 ") + get_text('open'), open_count)
    with col3:
        critical = len(tickets_b1[pd.to_numeric(tickets_b1['priority'], errors='coerce') == 1])
        st.metric(e("🚨 ") + get_text('critical'), critical)
    with col4:
        avg_comments = tickets_b1['comments_count'].mean()
        st.metric(e("💬 ") + f"Ø {get_text('comments')}", f"{avg_comments:.1f}")
    with col5:
        avg_steps = tickets_b1['steps_count'].mean()
        st.metric(e("📍 ") + f"Ø {get_text('steps')}", f"{avg_steps:.1f}")

    st.markdown("---")

    # Ticket List
    section_header(e("📋 ") + f"{get_text('tickets')} ({len(tickets_b1)})")

    priority_map = {1: e('🔴'), 2: e('🟠'), 3: e('🟡'), 4: e('🟢'), 5: e('⚪')}
    display_b1 = tickets_b1[['ticket_num', 'title', 'status', 'priority', 'assignee', 'comments_count', 'created_at']].copy()
    display_b1['priority'] = pd.to_numeric(display_b1['priority'], errors='coerce').fillna(3).astype(int)
    display_b1['priority'] = display_b1['priority'].map(lambda x: priority_map.get(x, e('⚪')))

    status_colors = {
        'Open': e('🟢'), 'In Progress': e('🔵'), 'Waiting': e('🟡'),
        'In Review': e('🟣'), 'Resolved': e('✅'), 'Closed': e('⚫')
    }
    display_b1['status'] = display_b1['status'].map(lambda x: f"{status_colors.get(x, e('⚪'))} {x}")

    st.dataframe(
        display_b1,
        column_config={
            'ticket_num': st.column_config.TextColumn("Ticket #", width="small"),
            'title': st.column_config.TextColumn(get_text('title_col'), width="large"),
            'status': st.column_config.TextColumn(get_text('status'), width="medium"),
            'priority': st.column_config.TextColumn(get_text('priority'), width="small"),
            'assignee': st.column_config.TextColumn(get_text('assignee'), width="medium"),
            'comments_count': st.column_config.NumberColumn(e("💬"), width="small"),
            'created_at': st.column_config.DatetimeColumn(get_text('created'), format="DD.MM.YY HH:mm"),
        },
        width="stretch",
        hide_index=True,
        height=500
    )


# ════════════════════════════════════════════════════════════════════════════
# B2 – Ticket Analytics
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Ticket Analytics")

col1, col2, col3 = st.columns([6, 2, 2])
with col2:
    auto_refresh_b2 = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=False, key="b2_refresh")
with col3:
    st.caption(f"{e('🕐')} {datetime.now().strftime('%H:%M:%S')}")

# Filter bar B2
col1, col2, col3, col4 = st.columns(4)
with col1:
    status_filter_b2 = st.selectbox(get_text('status'), [get_text('all')] + statuses, key="b2_status")
with col2:
    priority_filter_b2 = st.selectbox(get_text('priority'), [get_text('all')] + priorities, key="b2_priority")
with col3:
    assignee_filter_b2 = st.selectbox(get_text('assignee'), [get_text('all')] + assignees[:50], key="b2_assignee")
with col4:
    limit_options = [100, 200, 500, 1000, 2000, 0]
    limit_labels = ['100', '200', '500', '1.000', '2.000', 'Alle / All']
    limit_choice = st.selectbox(get_text('count'), limit_labels, index=2, key="b2_limit")
    limit_b2 = limit_options[limit_labels.index(limit_choice)]

tickets_b2 = load_tickets_b2(status_filter_b2, priority_filter_b2, assignee_filter_b2, limit_b2)

if tickets_b2.empty:
    st.warning(e("⚠️ ") + get_text('no_data'))
else:
    st.info(f"{e('📊')} {len(tickets_b2):,} {get_text('tickets')} geladen / loaded")

    st.markdown("---")

    # Status Distribution + Priority Distribution
    col1, col2 = st.columns(2)

    with col1:
        section_header(e("📊 ") + get_text('status_distribution'))
        status_counts = tickets_b2['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, hole=0.4)
        fig.update_layout(height=300)
        st.plotly_chart(fig, width="stretch")

    with col2:
        section_header(e("📈 ") + get_text('priority_distribution'))
        priority_series = pd.to_numeric(tickets_b2['priority'], errors='coerce').dropna().astype(int)
        priority_counts = priority_series.value_counts().sort_index()
        priority_names_b2 = {
            1: get_text('critical'),
            2: get_text('high'),
            3: get_text('medium'),
            4: get_text('low'),
            5: get_text('minimal')
        }
        fig = px.bar(
            x=[priority_names_b2.get(int(p), f'P{p}') for p in priority_counts.index],
            y=priority_counts.values,
            color=priority_counts.values,
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Top Assignees
    section_header(e("👥 ") + get_text('top_assignees'))
    top_assignees = tickets_b2['assignee'].value_counts().head(10)
    fig = px.bar(x=top_assignees.index, y=top_assignees.values)
    fig.update_layout(height=300)
    st.plotly_chart(fig, width="stretch")


# ════════════════════════════════════════════════════════════════════════════
# B3 – Ticket Detail
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(get_text('ticket_details'))

section_header(e("🔍 ") + get_text('ticket_details'))

tickets_list_b3 = load_tickets_list_b3()

if tickets_list_b3.empty:
    st.warning(e("⚠️ ") + get_text('no_data'))
    st.info("`python src/database/db_setup.py`")
else:
    ticket_options = tickets_list_b3.copy()
    ticket_options['display'] = ticket_options['ticket_num'] + " - " + ticket_options['title'].str[:50]

    selected = st.selectbox(f"{get_text('select_ticket')}:", ticket_options['display'].tolist(), key="b3_select")

    priority_map_b3 = {1: e('🔴'), 2: e('🟠'), 3: e('🟡'), 4: e('🟢'), 5: e('⚪')}

    if selected:
        ticket_id = ticket_options[ticket_options['display'] == selected]['id'].iloc[0]
        ticket, comments, history = get_ticket_details_b3(ticket_id)

        if not ticket.empty:
            t_row = ticket.iloc[0]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Ticket:** {t_row['ticket_num']}")
                st.markdown(f"**{get_text('title_col')}:** {t_row['title']}")
                st.markdown(f"**{get_text('type')}:** {t_row['type']}")
            with col2:
                st.markdown(f"**{get_text('status')}:** {t_row['status']}")
                prio_int = int(pd.to_numeric(t_row['priority'], errors='coerce') or 3)
                st.markdown(f"**{get_text('priority')}:** {priority_map_b3.get(prio_int, '?')}")
                st.markdown(f"**{get_text('assignee')}:** {t_row['assignee']}")
            with col3:
                st.markdown(f"**{get_text('created')}:** {t_row['created_at']}")
                st.markdown(f"**{get_text('comments')}:** {t_row['comments_count']}")
                st.markdown(f"**{get_text('steps')}:** {t_row['steps_count']}")

            # Comments
            if not comments.empty:
                st.markdown("---")
                st.markdown(f"#### {e('💬')} {get_text('comments')}")
                for _, c in comments.iterrows():
                    sentiment_icon = e("😊") if c['sentiment'] > 0.2 else e("😐") if c['sentiment'] > -0.2 else e("😟")
                    st.markdown(f"**{c['author']}** ({c['dialog_act']}) {sentiment_icon}")
                    st.caption(c['body'])
                    st.markdown("---")

            # History
            if not history.empty:
                st.markdown(f"#### {e('📜')} {get_text('status_history')}")
                for _, h in history.iterrows():
                    st.markdown(f"• {h['old_status']} → {h['new_status']} ({h['changed_by']})")


# ─── Auto-Refresh (once, at the bottom) ─────────────────────────────────────
if auto_refresh_b1:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Footer
render_footer()
