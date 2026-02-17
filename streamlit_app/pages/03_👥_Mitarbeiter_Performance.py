"""
Live Employee Performance
Real-time monitoring of employee performance.
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

st.set_page_config(page_title="Employee Performance", page_icon="👥", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

REFRESH_INTERVAL = 15

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_employee_data():
    """Load employee data from DB."""
    if not DB_PATH.exists():
        return None
    
    conn = get_db_connection()
    
    # Employees
    employees = pd.read_sql("SELECT * FROM employees ORDER BY avg_score DESC", conn)
    
    # Ticket statistics per employee
    ticket_stats = pd.read_sql("""
        SELECT 
            assignee,
            COUNT(*) as total_tickets,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open,
            AVG(comments_count) as avg_comments,
            AVG(steps_count) as avg_steps
        FROM tickets
        GROUP BY assignee
    """, conn)
    
    # Risk Level distribution
    risk_dist = pd.read_sql("""
        SELECT risk_level, COUNT(*) as count
        FROM employees
        GROUP BY risk_level
    """, conn)
    
    # Top/Bottom Performers
    top_performers = employees.nlargest(5, 'avg_score')
    bottom_performers = employees.nsmallest(5, 'avg_score')
    
    conn.close()
    
    return {
        'employees': employees,
        'ticket_stats': ticket_stats,
        'risk_dist': risk_dist,
        'top_performers': top_performers,
        'bottom_performers': bottom_performers
    }


# Header
col1, col2, col3 = st.columns([6, 2, 2])
with col1:
    page_header(e("👥 ") + get_text('employee_performance'), help_key='employees')
with col2:
    auto_refresh = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=True, key="emp_refresh")
with col3:
    st.caption(f"{e('🕐')} {datetime.now().strftime('%H:%M:%S')}")

# Load data
data = load_employee_data()

if data is None:
    st.error(e("❌ ") + get_text('database_not_found'))
    st.stop()

employees = data['employees']
ticket_stats = data['ticket_stats']
risk_dist = data['risk_dist']
risk_icons = {'GREEN': e('🟢'), 'YELLOW': e('🟡'), 'RED': e('🔴')}

# KPIs
section_header(e("📊 ") + get_text('team_overview'), 'team_stats')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(e("👥 ") + get_text('employees'), len(employees))
with col2:
    green = len(employees[employees['risk_level'] == 'GREEN'])
    st.metric(e("🟢 ") + "GREEN", green)
with col3:
    yellow = len(employees[employees['risk_level'] == 'YELLOW'])
    st.metric(e("🟡 ") + "YELLOW", yellow, delta="Training" if yellow > 0 else None)
with col4:
    red = len(employees[employees['risk_level'] == 'RED'])
    st.metric(e("🔴 ") + "RED", red, delta=get_text('critical') if red > 0 else None, delta_color="inverse")
with col5:
    avg_score = employees['avg_score'].mean()
    st.metric(e("📊 ") + f"Ø Score", f"{avg_score:.2f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    e("📋 ") + get_text('all_employees'), 
    e("🏆 ") + get_text('top_bottom'), 
    e("📊 ") + get_text('analyses'), 
    e("🔍 ") + get_text('details'),
    e("📖 ") + get_text('risk_level_def')
])

with tab1:
    section_header(e("📋 ") + get_text('employee_list'))
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.multiselect(get_text('risk_level') + ":", ['GREEN', 'YELLOW', 'RED'], default=['GREEN', 'YELLOW', 'RED'])
    with col2:
        search = st.text_input(e("🔍 ") + get_text('search') + ":", "")
    
    # Filter
    filtered = employees[employees['risk_level'].isin(risk_filter)]
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
    
    # Display
    display_df = filtered[['name', 'avg_score', 'ticket_count', 'risk_level']].copy()
    
    # Colored Risk Levels
    display_df['risk_level'] = display_df['risk_level'].map(lambda x: f"{risk_icons.get(x, e('⚪'))} {x}")
    
    st.dataframe(
        display_df,
        column_config={
            'name': st.column_config.TextColumn(get_text('employees'), width="large"),
            'avg_score': st.column_config.NumberColumn("Ø Score", format="%.2f"),
            'ticket_count': st.column_config.NumberColumn(get_text('tickets')),
            'risk_level': st.column_config.TextColumn(get_text('risk_level')),
        },
        use_container_width=True,
        hide_index=True,
        height=500
    )

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        section_header(e("🏆 ") + get_text('top_performers'))
        for i, row in data['top_performers'].iterrows():
            medal = e("🥇") if i == 0 else e("🥈") if i == 1 else e("🥉") if i == 2 else e("⭐")
            st.markdown(f"{medal} **{row['name']}** - Score: {row['avg_score']:.2f}")
    
    with col2:
        section_header(e("⚠️ ") + get_text('bottom_performers'))
        for _, row in data['bottom_performers'].iterrows():
            risk_icon = risk_icons.get(row['risk_level'], e('⚪'))
            st.markdown(f"{risk_icon} **{row['name']}** - Score: {row['avg_score']:.2f}")

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        section_header(e("📊 ") + get_text('risk_distribution'))
        if not risk_dist.empty:
            colors = {'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            fig = px.pie(
                risk_dist,
                values='count',
                names='risk_level',
                color='risk_level',
                color_discrete_map=colors,
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        section_header(e("📈 ") + get_text('score_distribution'))
        fig = px.histogram(
            employees,
            x='avg_score',
            nbins=20,
            color_discrete_sequence=['#2196F3']
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Scatter: Tickets vs Score
    section_header(e("📊 ") + get_text('tickets_vs_score'))
    
    if not ticket_stats.empty:
        merged = employees.merge(ticket_stats, left_on='name', right_on='assignee', how='left')
        scatter_data = merged.dropna(subset=['total_tickets', 'avg_score'])
        
        if not scatter_data.empty:
            fig = px.scatter(
                scatter_data,
                x='total_tickets',
                y='avg_score',
                color='risk_level',
                size='total_tickets',
                hover_data=['name'],
                color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_text('no_data'))

with tab4:
    section_header(e("🔍 ") + get_text('ticket_details'))
    
    selected_employee = st.selectbox(get_text('select_employee') + ":", employees['name'].tolist())
    
    if selected_employee:
        emp = employees[employees['name'] == selected_employee].iloc[0]
        stats = ticket_stats[ticket_stats['assignee'] == selected_employee]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"### {emp['name']}")
            st.markdown(f"**{get_text('risk_level')}:** {risk_icons.get(emp['risk_level'], e('⚪'))} {emp['risk_level']}")
            st.markdown(f"**Ø Score:** {emp['avg_score']:.2f}")
        
        with col2:
            if not stats.empty:
                s = stats.iloc[0]
                st.metric(e("🎫 ") + get_text('total'), int(s['total_tickets']))
                st.metric(e("✅ ") + get_text('resolved'), int(s['resolved']))
                st.metric(e("📂 ") + get_text('open'), int(s['open']))
        
        with col3:
            if not stats.empty:
                s = stats.iloc[0]
                st.metric(e("💬 ") + f"Ø {get_text('comments')}", f"{s['avg_comments']:.1f}")
                st.metric(e("📍 ") + f"Ø {get_text('steps')}", f"{s['avg_steps']:.1f}")
        
        # Recommendations
        st.markdown("---")
        st.markdown(f"### {e('💡')} {get_text('recommendations')}")
        
        if emp['risk_level'] == 'RED':
            st.error(f"""
            **{get_text('immediate_action')}:**
            1. Individual meeting with HR and supervisor
            2. Create Performance Improvement Plan
            3. Weekly progress monitoring
            """)
        elif emp['risk_level'] == 'YELLOW':
            st.warning(f"""
            **{get_text('training_recommended')}:**
            1. Individual needs analysis
            2. Targeted coaching
            3. Monthly progress check
            """)
        else:
            st.success(e("✅ ") + get_text('all_ok'))

with tab5:
    section_header(e("📖 ") + get_text('risk_level_def'))
    
    st.markdown(get_text('interpretation') if st.session_state.language == 'en' else 
                "Die Risk Level Klassifikation basiert auf objektiven Kriterien.")
    
    # RED Definition
    st.markdown(f"### {e('🔴')} RED - {get_text('critical')}")
    st.error(f"""
    **RED** classification when **at least one** of these conditions is met:
    
    | Criterion | Threshold | Meaning |
    |-----------|-----------|---------|
    | **Critical low score** | Ø < **1.5** | Performance extremely poor |
    | **Critical reopen rate** | > **30%** | Every 3rd ticket reopened |
    | **Repeated violations** | > **5** in 30 days | Constant process violations |
    | **Consecutively low** | **3x** in a row < 2 | Persistently poor performance |
    """)
    
    # YELLOW Definition
    st.markdown(f"### {e('🟡')} YELLOW - {get_text('training_recommended')}")
    st.warning(f"""
    **YELLOW** classification when **at least one** of these conditions is met (but no RED condition):
    
    | Criterion | Threshold | Recommended Training |
    |-----------|-----------|---------------------|
    | **Low score** | Ø < **2.5** | General quality training |
    | **High reopen rate** | > **15%** | Quality assurance training |
    | **Low compliance** | < **70%** | Process training |
    | **Slow processing** | > **2x** team avg | Efficiency training |
    | **Weak communication** | Score < **2.0** | Communication training |
    """)
    
    # GREEN Definition
    st.markdown(f"### {e('🟢')} GREEN - {get_text('all_ok')}")
    st.success(f"""
    **GREEN** classification when:
    - **No** YELLOW conditions are met
    - **No** RED conditions are met
    """)
    
    # Logic overview
    st.markdown(f"### {e('🔄')} {get_text('classification_logic')}")
    st.code("""
    IF (critical flags present) → RED
    ELSE IF (training flags present) → YELLOW  
    ELSE → GREEN
    """, language="text")

# Auto-Refresh
if auto_refresh:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Footer
render_footer()
