"""
Live Ticket Monitor
Real-time monitoring of all tickets with filters.
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
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

st.set_page_config(page_title="Ticket Monitor", page_icon="🎫", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Auto-Refresh
REFRESH_INTERVAL = 10

# Database
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_tickets(status_filter=None, priority_filter=None, assignee_filter=None, limit=100):
    """Load tickets with filters."""
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


@st.cache_data(ttl=60)
def get_filter_options():
    """Load filter options."""
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


def get_ticket_details(ticket_id):
    """Load ticket details including comments."""
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


# Header
col1, col2, col3 = st.columns([6, 2, 2])
with col1:
    page_header(e("🎫 ") + get_text('ticket_monitor'), help_key='tickets')
with col2:
    auto_refresh = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=True, key="ticket_refresh")
with col3:
    st.caption(f"{e('🕐')} {datetime.now().strftime('%H:%M:%S')}")

# Load filter options
statuses, priorities, assignees = get_filter_options()

# Filter bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox(get_text('status'), [get_text('all')] + statuses)
with col2:
    priority_filter = st.selectbox(get_text('priority'), [get_text('all')] + priorities)
with col3:
    assignee_filter = st.selectbox(get_text('assignee'), [get_text('all')] + assignees[:50])
with col4:
    limit = st.selectbox(get_text('count'), [50, 100, 200, 500], index=1)

# Load tickets
tickets = load_tickets(status_filter, priority_filter, assignee_filter, limit)

if tickets.empty:
    st.warning(e("⚠️ ") + get_text('no_data'))
    st.info("`python src/database/db_setup.py`")
    st.stop()

# KPIs
section_header(e("📊 ") + get_text('overview'), 'ticket_stats')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(e("🎫 ") + get_text('tickets'), len(tickets))
with col2:
    open_count = len(tickets[tickets['status'].isin(['Open', 'In Progress', 'Waiting'])])
    st.metric(e("📂 ") + get_text('open'), open_count)
with col3:
    critical = len(tickets[pd.to_numeric(tickets['priority'], errors='coerce') == 1])
    st.metric(e("🚨 ") + get_text('critical'), critical)
with col4:
    avg_comments = tickets['comments_count'].mean()
    st.metric(e("💬 ") + f"Ø {get_text('comments')}", f"{avg_comments:.1f}")
with col5:
    avg_steps = tickets['steps_count'].mean()
    st.metric(e("📍 ") + f"Ø {get_text('steps')}", f"{avg_steps:.1f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs([
    e("📋 ") + get_text('ticket_list'), 
    e("📊 ") + get_text('statistics'), 
    e("🔍 ") + get_text('details')
])

with tab1:
    # Ticket list
    section_header(e("📋 ") + f"{get_text('tickets')} ({len(tickets)})")
    
    # Formatting
    display_df = tickets[['ticket_num', 'title', 'status', 'priority', 'assignee', 'comments_count', 'created_at']].copy()
    
    priority_map = {1: e('🔴'), 2: e('🟠'), 3: e('🟡'), 4: e('🟢'), 5: e('⚪')}
    display_df['priority'] = pd.to_numeric(display_df['priority'], errors='coerce').fillna(3).astype(int)
    display_df['priority'] = display_df['priority'].map(lambda x: priority_map.get(x, e('⚪')))
    
    status_colors = {
        'Open': e('🟢'), 'In Progress': e('🔵'), 'Waiting': e('🟡'),
        'In Review': e('🟣'), 'Resolved': e('✅'), 'Closed': e('⚫')
    }
    display_df['status'] = display_df['status'].map(lambda x: f"{status_colors.get(x, e('⚪'))} {x}")
    
    st.dataframe(
        display_df,
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

with tab2:
    # Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        section_header(e("📊 ") + get_text('status_distribution'))
        status_counts = tickets['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, hole=0.4)
        fig.update_layout(height=300)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        section_header(e("📈 ") + get_text('priority_distribution'))
        priority_series = pd.to_numeric(tickets['priority'], errors='coerce').dropna().astype(int)
        priority_counts = priority_series.value_counts().sort_index()
        priority_names = {
            1: get_text('critical'), 
            2: get_text('high'), 
            3: get_text('medium'), 
            4: get_text('low'), 
            5: get_text('minimal')
        }
        fig = px.bar(
            x=[priority_names.get(int(p), f'P{p}') for p in priority_counts.index],
            y=priority_counts.values,
            color=priority_counts.values,
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, width="stretch")
    
    # Top assignees
    section_header(e("👥 ") + get_text('top_assignees'))
    top_assignees = tickets['assignee'].value_counts().head(10)
    fig = px.bar(x=top_assignees.index, y=top_assignees.values)
    fig.update_layout(height=300)
    st.plotly_chart(fig, width="stretch")

with tab3:
    # Ticket details
    section_header(e("🔍 ") + get_text('ticket_details'))
    
    ticket_options = tickets[['id', 'ticket_num', 'title']].copy()
    ticket_options['display'] = ticket_options['ticket_num'] + " - " + ticket_options['title'].str[:50]
    
    selected = st.selectbox(f"{get_text('select_ticket')}:", ticket_options['display'].tolist())
    
    if selected:
        ticket_id = ticket_options[ticket_options['display'] == selected]['id'].iloc[0]
        ticket, comments, history = get_ticket_details(ticket_id)
        
        if not ticket.empty:
            t = ticket.iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Ticket:** {t['ticket_num']}")
                st.markdown(f"**{get_text('title_col')}:** {t['title']}")
                st.markdown(f"**{get_text('type')}:** {t['type']}")
            with col2:
                st.markdown(f"**{get_text('status')}:** {t['status']}")
                prio_int = int(pd.to_numeric(t['priority'], errors='coerce') or 3)
                st.markdown(f"**{get_text('priority')}:** {priority_map.get(prio_int, '?')}")
                st.markdown(f"**{get_text('assignee')}:** {t['assignee']}")
            with col3:
                st.markdown(f"**{get_text('created')}:** {t['created_at']}")
                st.markdown(f"**{get_text('comments')}:** {t['comments_count']}")
                st.markdown(f"**{get_text('steps')}:** {t['steps_count']}")
            
            # Comments
            if not comments.empty:
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

# Auto-Refresh
if auto_refresh:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Footer
render_footer()
