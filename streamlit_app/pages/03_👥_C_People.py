"""
C – People
C1: People Overview | C2: Performance | C3: Training Actions |
C4: Trends | C5: Employee Detail | C6: Risk Definition
"""

import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import time
import sys

# Import components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="People", page_icon="👥", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

REFRESH_INTERVAL = 15

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "helpdesk.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def t(de_text, en_text):
    return en_text if st.session_state.get('language') == 'en' else de_text


# ─── Cache functions ─────────────────────────────────────────────────────────

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data_c1():
    """C1: People Overview data."""
    if not DB_PATH.exists():
        return None
    conn = get_db_connection()
    employees = pd.read_sql("SELECT * FROM employees ORDER BY avg_score DESC", conn)
    risk_dist = pd.read_sql("""
        SELECT risk_level, COUNT(*) as count FROM employees GROUP BY risk_level
    """, conn)
    conn.close()
    return {'employees': employees, 'risk_dist': risk_dist}


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data_c2():
    """C2: Performance data."""
    if not DB_PATH.exists():
        return None
    conn = get_db_connection()
    employees = pd.read_sql("SELECT * FROM employees ORDER BY avg_score DESC", conn)
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
    conn.close()
    return {
        'employees': employees,
        'ticket_stats': ticket_stats,
        'top_performers': employees.nlargest(5, 'avg_score'),
        'bottom_performers': employees[employees['risk_level'] == 'RED'].nsmallest(5, 'avg_score')
    }


@st.cache_data
def load_data_c3():
    """C3: Training report."""
    report_path = PROJECT_ROOT / "reports" / "training_report.csv"
    if report_path.exists():
        df = pd.read_csv(report_path)
        df = df.rename(columns={
            'employee': 'Employee',
            'overall_score': 'Avg Score',
            'ticket_count': 'Tickets',
            'risk_level': 'Risk Level',
            'training_areas': 'Training Areas',
            'flags': 'Flags',
            'recommendations': 'Recommendations'
        })
        return df
    return None


@st.cache_data
def load_data_c4():
    """C4: Q vs O score comparison data for trends."""
    comparison_path = PROJECT_ROOT / "data" / "processed" / "q_vs_o_score_comparison.csv"
    if comparison_path.exists():
        df = pd.read_csv(comparison_path)
        df['Risk Level'] = pd.cut(
            df['q_score_avg'],
            bins=[0, 2.5, 3.5, 5.01],
            labels=['RED', 'YELLOW', 'GREEN']
        )
        df['Employee'] = df['employee']
        df['Avg Score'] = df['q_score_avg']
        df['Tickets'] = df['ticket_count']
        df['Q1'] = df['q1']
        df['Q2'] = df['q2']
        df['Q3'] = df['q3']
        return df
    return pd.DataFrame()


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data_c5():
    """C5: Employee detail data."""
    if not DB_PATH.exists():
        return None
    conn = get_db_connection()
    employees = pd.read_sql("SELECT * FROM employees ORDER BY avg_score DESC", conn)
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
    conn.close()
    return {'employees': employees, 'ticket_stats': ticket_stats}


def load_employee_tickets_c5(assignee):
    """Load tickets for a single employee (C5)."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = get_db_connection()
    df = pd.read_sql("""
        SELECT ticket_num, title, status, priority, comments_count, created_at
        FROM tickets
        WHERE assignee = ?
        ORDER BY created_at DESC
        LIMIT 50
    """, conn, params=[assignee])
    conn.close()
    return df


# Training area translations (C3)
TRAINING_AREA_TRANSLATIONS = {
    'Qualität': 'Quality', 'Effizienz': 'Efficiency', 'Kommunikation': 'Communication',
    'Prozess': 'Process', 'Genauigkeit': 'Accuracy', 'Gründlichkeit': 'Thoroughness',
    'Reaktionszeit': 'Response Time', 'Kundenzufriedenheit': 'Customer Satisfaction',
    'Problemlösung': 'Problem Solving', 'Dokumentation': 'Documentation',
    'Quality': 'Quality', 'Efficiency': 'Efficiency', 'Communication': 'Communication',
    'Process': 'Process', 'Accuracy': 'Accuracy', 'Thoroughness': 'Thoroughness',
    'Response Time': 'Response Time', 'Customer Satisfaction': 'Customer Satisfaction',
    'Problem Solving': 'Problem Solving', 'Documentation': 'Documentation'
}


def translate_training_area(area, lang='en'):
    area = area.strip()
    if lang == 'en':
        return TRAINING_AREA_TRANSLATIONS.get(area, area)
    return area


# ─── Page Header ────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([6, 2, 2])
with col1:
    page_header(e("👥 ") + "People – Overview, Performance & Training", help_key='employees')
with col2:
    auto_refresh = st.checkbox(e("🔄 ") + get_text('auto_refresh'), value=True, key="c_refresh")
with col3:
    st.caption(f"{e('🕐')} {datetime.now().strftime('%H:%M:%S')}")


# ════════════════════════════════════════════════════════════════════════════
# C1 – People Overview
# ════════════════════════════════════════════════════════════════════════════
st.header("C1 – People Overview")

data_c1 = load_data_c1()

if data_c1 is None:
    st.error(e("❌ ") + get_text('database_not_found'))
else:
    employees_c1 = data_c1['employees']
    risk_dist_c1 = data_c1['risk_dist']
    risk_icons = {'GREEN': e('🟢'), 'YELLOW': e('🟡'), 'RED': e('🔴')}

    # KPIs
    section_header(e("📊 ") + get_text('team_overview'), 'team_stats_c1')

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(e("👥 ") + get_text('employees'), len(employees_c1))
    with col2:
        green = len(employees_c1[employees_c1['risk_level'] == 'GREEN'])
        st.metric("🟢 GREEN", green)
    with col3:
        yellow = len(employees_c1[employees_c1['risk_level'] == 'YELLOW'])
        st.metric("🟡 YELLOW", yellow, delta="Training" if yellow > 0 else None)
    with col4:
        red = len(employees_c1[employees_c1['risk_level'] == 'RED'])
        st.metric("🔴 RED", red, delta=get_text('critical') if red > 0 else None, delta_color="inverse")
    with col5:
        avg_score_c1 = employees_c1['avg_score'].mean()
        st.metric(e("📊 ") + "Ø Score", f"{avg_score_c1:.2f}")

    st.markdown("---")

    # All Employees
    section_header(e("📋 ") + get_text('all_employees'))

    col1, col2 = st.columns(2)
    with col1:
        risk_filter_c1 = st.multiselect(get_text('risk_level') + ":", ['GREEN', 'YELLOW', 'RED'],
                                         default=['GREEN', 'YELLOW', 'RED'], key="c1_risk_filter")
    with col2:
        search_c1 = st.text_input(e("🔍 ") + get_text('search') + ":", "", key="c1_search")

    filtered_c1 = employees_c1[employees_c1['risk_level'].isin(risk_filter_c1)]
    if search_c1:
        filtered_c1 = filtered_c1[filtered_c1['name'].str.contains(search_c1, case=False, na=False)]

    display_c1 = filtered_c1[['name', 'avg_score', 'ticket_count', 'risk_level']].copy()
    display_c1['risk_level'] = display_c1['risk_level'].map(lambda x: f"{risk_icons.get(x, e('⚪'))} {x}")

    st.dataframe(
        display_c1,
        column_config={
            'name': st.column_config.TextColumn(get_text('employees'), width="large"),
            'avg_score': st.column_config.NumberColumn("Ø Score", format="%.2f"),
            'ticket_count': st.column_config.NumberColumn(get_text('tickets')),
            'risk_level': st.column_config.TextColumn(get_text('risk_level')),
        },
        width="stretch", hide_index=True, height=400
    )

    st.markdown("---")

    # Risk Level Distribution
    section_header(e("📊 ") + get_text('risk_distribution'))

    col1, col2 = st.columns(2)
    with col1:
        if not risk_dist_c1.empty:
            colors = {'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            fig = px.pie(risk_dist_c1, values='count', names='risk_level', color='risk_level',
                         color_discrete_map=colors, hole=0.4)
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
    with col2:
        if not risk_dist_c1.empty:
            fig = px.bar(risk_dist_c1, x='risk_level', y='count', color='risk_level',
                         color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'})
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, width="stretch")


# ════════════════════════════════════════════════════════════════════════════
# C2 – Performance
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("C2 – Performance")

data_c2 = load_data_c2()

if data_c2 is None:
    st.error(e("❌ ") + get_text('database_not_found'))
else:
    employees_c2 = data_c2['employees']
    ticket_stats_c2 = data_c2['ticket_stats']
    risk_icons_c2 = {'GREEN': e('🟢'), 'YELLOW': e('🟡'), 'RED': e('🔴')}

    # Employee List with filters
    section_header(e("📋 ") + get_text('employee_list'))

    col1, col2 = st.columns(2)
    with col1:
        risk_filter_c2 = st.multiselect(get_text('risk_level') + ":", ['GREEN', 'YELLOW', 'RED'],
                                         default=['GREEN', 'YELLOW', 'RED'], key="c2_risk_filter")
    with col2:
        search_c2 = st.text_input(e("🔍 ") + get_text('search') + ":", "", key="c2_search")

    filtered_c2 = employees_c2[employees_c2['risk_level'].isin(risk_filter_c2)]
    if search_c2:
        filtered_c2 = filtered_c2[filtered_c2['name'].str.contains(search_c2, case=False, na=False)]

    display_c2 = filtered_c2[['name', 'avg_score', 'ticket_count', 'risk_level']].copy()
    display_c2['risk_level'] = display_c2['risk_level'].map(lambda x: f"{risk_icons_c2.get(x, e('⚪'))} {x}")

    st.dataframe(
        display_c2,
        column_config={
            'name': st.column_config.TextColumn(get_text('employees'), width="large"),
            'avg_score': st.column_config.NumberColumn("Ø Score", format="%.2f"),
            'ticket_count': st.column_config.NumberColumn(get_text('tickets')),
            'risk_level': st.column_config.TextColumn(get_text('risk_level')),
        },
        width="stretch", hide_index=True, height=350
    )

    st.markdown("---")

    # Top & Bottom Performers
    col1, col2 = st.columns(2)
    with col1:
        section_header(e("🏆 ") + get_text('top_performers'))
        for i, row in data_c2['top_performers'].iterrows():
            medal = e("🥇") if i == 0 else e("🥈") if i == 1 else e("🥉") if i == 2 else e("⭐")
            st.markdown(f"{medal} **{row['name']}** - Score: {row['avg_score']:.2f}")

    with col2:
        section_header(e("🔴 ") + get_text('bottom_performers'))
        for _, row in data_c2['bottom_performers'].iterrows():
            risk_icon = risk_icons_c2.get(row['risk_level'], e('⚪'))
            st.markdown(f"{risk_icon} **{row['name']}** - Score: {row['avg_score']:.2f}")

    st.markdown("---")

    # Score Distribution barplot
    section_header(e("📈 ") + get_text('score_distribution'))
    fig = px.histogram(employees_c2, x='avg_score', nbins=20, color_discrete_sequence=['#2196F3'])
    fig.update_layout(height=350)
    st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Ticket Count vs Avg_Score
    section_header(e("📊 ") + get_text('tickets_vs_score'))

    if not ticket_stats_c2.empty:
        merged_c2 = employees_c2.merge(ticket_stats_c2, left_on='name', right_on='assignee', how='left')
        scatter_data = merged_c2.dropna(subset=['total_tickets', 'avg_score'])
        if not scatter_data.empty:
            fig = px.scatter(
                scatter_data, x='total_tickets', y='avg_score', color='risk_level',
                size='total_tickets', hover_data=['name'],
                color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(get_text('no_data'))


# ════════════════════════════════════════════════════════════════════════════
# C3 – Training Actions
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("C3 – " + get_text('training_deficits'))

section_header(e("🏋️ ") + get_text('training_subtitle'))

report_df = load_data_c3()

if report_df is None:
    st.warning(e("⚠️ ") + get_text('training_report_not_found'))
else:
    # KPI Cards
    green_count = len(report_df[report_df['Risk Level'] == 'GREEN'])
    yellow_count = len(report_df[report_df['Risk Level'] == 'YELLOW'])
    red_count = len(report_df[report_df['Risk Level'] == 'RED'])
    total_c3 = len(report_df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 " + get_text('total_employees'), total_c3)
    with col2:
        st.metric("🟢 " + get_text('ok_green'), green_count, f"{green_count/total_c3*100:.0f}%")
    with col3:
        st.metric("🟡 " + get_text('training_yellow'), yellow_count, f"{yellow_count/total_c3*100:.0f}%")
    with col4:
        st.metric("🔴 " + get_text('disciplinary') + " (RED)", red_count, f"{red_count/total_c3*100:.0f}%")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔴 " + get_text('urgent'),
        "🟡 " + get_text('training_recommended'),
        "📋 " + get_text('all_employees'),
        "💡 " + get_text('management_recommendations')
    ])

    # Tab 1: Urgent – RED employees
    with tab1:
        section_header("🔴 " + get_text('immediate_action'))
        red_employees_c3 = report_df[report_df['Risk Level'] == 'RED'].copy()

        if len(red_employees_c3) == 0:
            st.success(e("✅ ") + get_text('no_critical'))
        else:
            st.error(e("⚠️ ") + f"{len(red_employees_c3)} {get_text('critical_attention')}")
            for _, row in red_employees_c3.iterrows():
                with st.expander(f"{e('👤')} {row['Employee']} - Score: {row['Avg Score']:.2f}"):
                    training_areas = row['Training Areas']
                    if pd.notna(training_areas) and st.session_state.get('language') == 'en':
                        areas = [translate_training_area(a.strip(), 'en') for a in str(training_areas).split(',')]
                        training_areas = ', '.join(areas)
                    rec_text = (
                        "- Personal conversation with the employee\n- Root cause analysis of low scores\n- Create individual development plan"
                        if st.session_state.get('language') == 'en' else
                        "- Persönliches Gespräch mit dem Mitarbeiter\n- Ursachenanalyse der niedrigen Scores\n- Individuellen Entwicklungsplan erstellen"
                    )
                    st.markdown(f"""
**{get_text('flags')}:** {row['Flags']}

**{get_text('training_areas')}:** {training_areas}

**{get_text('recommendations')}:**
{rec_text}
""")

    # Tab 2: Most common training – YELLOW employees
    with tab2:
        section_header("🟡 " + get_text('training_recommended'))
        yellow_employees_c3 = report_df[report_df['Risk Level'] == 'YELLOW'].copy()

        if len(yellow_employees_c3) == 0:
            st.success(e("✅ ") + get_text('no_training_needed'))
        else:
            st.warning(e("📚 ") + f"{len(yellow_employees_c3)} {get_text('should_receive_training')}")
            training_areas_all = []
            for areas in yellow_employees_c3['Training Areas'].dropna():
                for a in str(areas).split(','):
                    area = a.strip()
                    if st.session_state.get('language') == 'en':
                        area = translate_training_area(area, 'en')
                    training_areas_all.append(area)

            if training_areas_all:
                area_counts = pd.Series(training_areas_all).value_counts()
                fig = px.bar(
                    x=area_counts.values, y=area_counts.index, orientation='h',
                    title=get_text('common_training_needs'),
                    labels={'x': get_text('count'), 'y': get_text('training_areas')}
                )
                fig.update_layout(yaxis_title=get_text('training_areas'), xaxis_title=get_text('count'))
                st.plotly_chart(fig, width="stretch")

            display_c3 = yellow_employees_c3[['Employee', 'Avg Score', 'Tickets', 'Training Areas']].copy()
            if st.session_state.get('language') == 'en':
                display_c3['Training Areas'] = display_c3['Training Areas'].apply(
                    lambda x: ', '.join([translate_training_area(a.strip(), 'en') for a in str(x).split(',')]) if pd.notna(x) else x
                )
            st.dataframe(display_c3, width="stretch")

    # Tab 3: All employees with risk filter
    with tab3:
        section_header(e("📋 ") + get_text('all_employees'))
        col1, col2 = st.columns(2)
        with col1:
            risk_filter_c3 = st.multiselect(
                get_text('risk_level') + " " + get_text('filter'),
                options=['GREEN', 'YELLOW', 'RED'],
                default=['GREEN', 'YELLOW', 'RED'],
                key="c3_risk_filter"
            )
        with col2:
            min_tickets_c3 = st.slider(get_text('min_tickets'), 0, int(report_df['Tickets'].max()), 0, key="c3_min_tickets")

        filtered_c3 = report_df[
            (report_df['Risk Level'].isin(risk_filter_c3)) &
            (report_df['Tickets'] >= min_tickets_c3)
        ]
        st.dataframe(filtered_c3, width="stretch", hide_index=True)

    # Tab 4: Management Recommendation
    with tab4:
        section_header(e("💡 ") + get_text('management_recommendations'))
        recommendations_text = (
            f"""
### {get_text('immediate_action')} (RED):
1. **Personal meeting** within 5 business days
2. **Root cause analysis** - External factors involved?
3. **Written development plan** with clear goals

### Training Programs (YELLOW):
1. **Workshop: Problem Analysis** - Systematic approach
2. **Mentoring Program** - Pair work with experienced colleagues
3. **Process Training** - Improve workflow compliance

### Preventive Measures:
1. Regular **feedback sessions** (monthly)
2. **Peer review** for critical tickets
3. **Automated alerts** on score deterioration
"""
            if st.session_state.get('language') == 'en' else
            f"""
### {get_text('immediate_action')} (RED):
1. **Persönliches Gespräch** innerhalb von 5 Werktagen
2. **Ursachenanalyse** - Sind externe Faktoren beteiligt?
3. **Schriftlicher Entwicklungsplan** mit klaren Zielen

### Training Programme (YELLOW):
1. **Workshop: Problemanalyse** - Systematischer Ansatz
2. **Mentoring-Programm** - Zusammenarbeit mit erfahrenen Kollegen
3. **Prozess-Training** - Workflow-Compliance verbessern

### Präventive Maßnahmen:
1. Regelmäßige **Feedback-Sitzungen** (monatlich)
2. **Peer Review** für kritische Tickets
3. **Automatische Alerts** bei Score-Verschlechterung
"""
        )
        st.markdown(recommendations_text)


# ════════════════════════════════════════════════════════════════════════════
# C4 – Trends
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("C4 – " + get_text('trend_analysis'))

section_header(e("📅 ") + get_text('trend_subtitle'))

employee_df_c4 = load_data_c4()

if not employee_df_c4.empty:
    section_header(e("👥 ") + get_text('performance_per_employee'), 'trend_employees')

    col1, col2 = st.columns(2)
    with col1:
        risk_counts_c4 = employee_df_c4['Risk Level'].value_counts()
        fig = px.pie(
            values=risk_counts_c4.values,
            names=risk_counts_c4.index,
            title=get_text('risk_distribution') + " (Q-Score)",
            color=risk_counts_c4.index,
            color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
        )
        st.plotly_chart(fig, width="stretch")
    with col2:
        fig = px.box(
            employee_df_c4, x='Risk Level', y='Avg Score',
            title=t("Scores nach Risk Level (Q-Score Avg)", "Scores by Risk Level (Q-Score Avg)"),
            color='Risk Level',
            color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
        )
        st.plotly_chart(fig, width="stretch")

    # Top & Bottom
    st.markdown(f"### {e('🏆')} Top & Bottom Performer")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{e('🥇')} {get_text('top_10_highest')}**")
        top10_c4 = employee_df_c4.nlargest(10, 'Avg Score')[['Employee', 'Q1', 'Q2', 'Q3', 'Avg Score', 'Tickets', 'Risk Level']]
        st.dataframe(top10_c4, width="stretch", hide_index=True)
    with col2:
        st.markdown(f"**{e('⚠️')} {get_text('bottom_10_lowest')}**")
        bottom10_c4 = employee_df_c4.nsmallest(10, 'Avg Score')[['Employee', 'Q1', 'Q2', 'Q3', 'Avg Score', 'Tickets', 'Risk Level']]
        st.dataframe(bottom10_c4, width="stretch", hide_index=True)

    # Ticket Volume vs Score
    section_header(e("📊 ") + get_text('ticket_volume_vs_performance'))
    fig = px.scatter(
        employee_df_c4, x='Tickets', y='Avg Score', color='Risk Level',
        size='Tickets', hover_data=['Employee', 'Q1', 'Q2', 'Q3'],
        title=t("Zusammenhang Tickets & Performance (Q-Score)", "Relationship Tickets & Performance (Q-Score)"),
        color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

    corr_c4 = employee_df_c4['Tickets'].corr(employee_df_c4['Avg Score'])
    if corr_c4 > 0.3:
        st.success(f"{e('📈')} {get_text('positive_correlation')} ({corr_c4:.2f}): {get_text('more_tickets_higher')}")
    elif corr_c4 < -0.3:
        st.warning(f"{e('📉')} {get_text('negative_correlation')} ({corr_c4:.2f}): {get_text('more_tickets_lower')}")
    else:
        st.info(f"➡️ {get_text('weak_correlation')} ({corr_c4:.2f}): {get_text('little_influence')}")

    st.markdown("---")

    # Q-Score Dimensions
    section_header(e("📊 ") + t("Q-Score Dimensionen", "Q-Score Dimensions"))
    st.markdown(t(
        """
**Q-Score Dimensionen (Manager-Bewertung 1-5):**
- **Q1** = Genauigkeit, Präzision
- **Q2** = Gründlichkeit, Vollständigkeit
- **Q3** = Reaktionsfähigkeit, Verbindlichkeit
""",
        """
**Q-Score Dimensions (Manager Rating 1-5):**
- **Q1** = Accuracy, Precision
- **Q2** = Thoroughness, Completeness
- **Q3** = Responsiveness, Reliability
"""
    ))

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.histogram(employee_df_c4, x='Q1', nbins=5,
                           title=t("Q1: Genauigkeit Verteilung", "Q1: Accuracy Distribution"),
                           color_discrete_sequence=['#2196F3'])
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, width="stretch")
        st.metric(t("Ø Q1", "Avg Q1"), f"{employee_df_c4['Q1'].mean():.2f}")
    with col2:
        fig = px.histogram(employee_df_c4, x='Q2', nbins=5,
                           title=t("Q2: Gründlichkeit Verteilung", "Q2: Thoroughness Distribution"),
                           color_discrete_sequence=['#9C27B0'])
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, width="stretch")
        st.metric(t("Ø Q2", "Avg Q2"), f"{employee_df_c4['Q2'].mean():.2f}")
    with col3:
        fig = px.histogram(employee_df_c4, x='Q3', nbins=5,
                           title=t("Q3: Reaktionsfähigkeit Verteilung", "Q3: Responsiveness Distribution"),
                           color_discrete_sequence=['#FF9800'])
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, width="stretch")
        st.metric(t("Ø Q3", "Avg Q3"), f"{employee_df_c4['Q3'].mean():.2f}")
else:
    st.info(get_text('no_data'))


# ════════════════════════════════════════════════════════════════════════════
# C5 – Employee Detail
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("C5 – " + get_text('ticket_details'))

section_header(e("🔍 ") + get_text('ticket_details'))

data_c5 = load_data_c5()

if data_c5 is None:
    st.error(e("❌ ") + get_text('database_not_found'))
else:
    employees_c5 = data_c5['employees']
    ticket_stats_c5 = data_c5['ticket_stats']
    risk_icons_c5 = {'GREEN': e('🟢'), 'YELLOW': e('🟡'), 'RED': e('🔴')}

    selected_employee_c5 = st.selectbox(get_text('select_employee') + ":", employees_c5['name'].tolist(), key="c5_select")

    if selected_employee_c5:
        emp_c5 = employees_c5[employees_c5['name'] == selected_employee_c5].iloc[0]
        stats_c5 = ticket_stats_c5[ticket_stats_c5['assignee'] == selected_employee_c5]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"### {emp_c5['name']}")
            st.markdown(f"**{get_text('risk_level')}:** {risk_icons_c5.get(emp_c5['risk_level'], e('⚪'))} {emp_c5['risk_level']}")
            st.markdown(f"**Ø Score:** {emp_c5['avg_score']:.2f}")
        with col2:
            if not stats_c5.empty:
                s = stats_c5.iloc[0]
                st.metric(e("🎫 ") + get_text('total'), int(s['total_tickets']))
                st.metric(e("✅ ") + get_text('resolved'), int(s['resolved']))
                st.metric(e("📂 ") + get_text('open'), int(s['open']))
        with col3:
            if not stats_c5.empty:
                s = stats_c5.iloc[0]
                st.metric(e("💬 ") + f"Ø {get_text('comments')}", f"{s['avg_comments']:.1f}")
                st.metric(e("📍 ") + f"Ø {get_text('steps')}", f"{s['avg_steps']:.1f}")

        st.markdown("---")

        # Recommendations
        st.markdown(f"### {e('💡')} {get_text('recommendations')}")
        if emp_c5['risk_level'] == 'RED':
            st.error(f"""
**{get_text('immediate_action')}:**
1. Individual meeting with HR and supervisor
2. Create Performance Improvement Plan
3. Weekly progress monitoring
""")
        elif emp_c5['risk_level'] == 'YELLOW':
            st.warning(f"""
**{get_text('training_recommended')}:**
1. Individual needs analysis
2. Targeted coaching
3. Monthly progress check
""")
        else:
            st.success(e("✅ ") + get_text('all_ok'))

        st.markdown("---")

        # Employee Tickets
        st.markdown(f"### {e('🎫')} {get_text('tickets')} – {selected_employee_c5}")
        emp_tickets_c5 = load_employee_tickets_c5(selected_employee_c5)

        if not emp_tickets_c5.empty:
            priority_map_c5 = {1: e('🔴'), 2: e('🟠'), 3: e('🟡'), 4: e('🟢'), 5: e('⚪')}
            display_c5 = emp_tickets_c5.copy()
            display_c5['priority'] = pd.to_numeric(display_c5['priority'], errors='coerce').fillna(3).astype(int)
            display_c5['priority'] = display_c5['priority'].map(lambda x: priority_map_c5.get(x, e('⚪')))
            st.dataframe(
                display_c5,
                column_config={
                    'ticket_num': st.column_config.TextColumn("Ticket #", width="small"),
                    'title': st.column_config.TextColumn(get_text('title_col'), width="large"),
                    'status': st.column_config.TextColumn(get_text('status'), width="medium"),
                    'priority': st.column_config.TextColumn(get_text('priority'), width="small"),
                    'comments_count': st.column_config.NumberColumn(e("💬"), width="small"),
                    'created_at': st.column_config.DatetimeColumn(get_text('created'), format="DD.MM.YY HH:mm"),
                },
                width="stretch", hide_index=True, height=400
            )
        else:
            st.info(get_text('no_data'))


# ════════════════════════════════════════════════════════════════════════════
# C6 – Risk Definition
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("C6 – " + get_text('risk_level_def'))

section_header(e("📖 ") + get_text('risk_level_def'))

st.markdown(get_text('interpretation') if st.session_state.language == 'en' else
            "Die Risk Level Klassifikation basiert auf objektiven Kriterien.")

# RED Definition
st.markdown(f"### {e('🔴')} RED - {get_text('critical')}")
red_table = (
    f"""
**RED** classification when **at least one** of these conditions is met:

| Criterion | Threshold | Meaning |
|-----------|-----------|---------|
| **Critical low score** | Ø < **1.5** | Performance extremely poor |
| **Critical reopen rate** | > **30%** | Every 3rd ticket reopened |
| **Repeated violations** | > **5** in 30 days | Constant process violations |
| **Consecutively low** | **3x** in a row < 2 | Persistently poor performance |
"""
    if st.session_state.get('language') == 'en' else
    f"""
**RED** Klassifikation wenn **mindestens eine** Bedingung erfüllt ist:

| Kriterium | Schwellwert | Bedeutung |
|-----------|-----------|---------|
| **Kritisch niedriger Score** | Ø < **1.5** | Performance extrem schlecht |
| **Kritische Reopen-Rate** | > **30%** | Jedes 3. Ticket wiedereröffnet |
| **Wiederholte Verstöße** | > **5** in 30 Tagen | Ständige Prozessverstöße |
| **Konsekutiv niedrig** | **3x** hintereinander < 2 | Anhaltend schlechte Performance |
"""
)
st.error(red_table)

# YELLOW Definition
st.markdown(f"### {e('🟡')} YELLOW - {get_text('training_recommended')}")
yellow_table = (
    f"""
**YELLOW** classification when **at least one** of these conditions is met (but no RED condition):

| Criterion | Threshold | Recommended Training |
|-----------|-----------|---------------------|
| **Low score** | Ø < **2.5** | General quality training |
| **High reopen rate** | > **15%** | Quality assurance training |
| **Low compliance** | < **70%** | Process training |
| **Slow processing** | > **2x** team avg | Efficiency training |
| **Weak communication** | Score < **2.0** | Communication training |
"""
    if st.session_state.get('language') == 'en' else
    f"""
**YELLOW** Klassifikation wenn **mindestens eine** Bedingung erfüllt ist (aber keine RED):

| Kriterium | Schwellwert | Empfohlenes Training |
|-----------|-----------|---------------------|
| **Niedriger Score** | Ø < **2.5** | Allgemeines Qualitätstraining |
| **Hohe Reopen-Rate** | > **15%** | Qualitätssicherungstraining |
| **Niedrige Compliance** | < **70%** | Prozesstraining |
| **Langsame Bearbeitung** | > **2x** Team-Durchschnitt | Effizienztraining |
| **Schwache Kommunikation** | Score < **2.0** | Kommunikationstraining |
"""
)
st.warning(yellow_table)

# GREEN Definition
st.markdown(f"### {e('🟢')} GREEN - {get_text('all_ok')}")
green_text = (
    """
**GREEN** classification when:
- **No** YELLOW conditions are met
- **No** RED conditions are met
"""
    if st.session_state.get('language') == 'en' else
    """
**GREEN** Klassifikation wenn:
- **Keine** YELLOW Bedingungen erfüllt sind
- **Keine** RED Bedingungen erfüllt sind
"""
)
st.success(green_text)

# Logic overview
st.markdown(f"### {e('🔄')} {get_text('classification_logic')}")
st.code("""
IF (critical flags present) → RED
ELSE IF (training flags present) → YELLOW
ELSE → GREEN
""", language="text")

st.markdown("---")

# Threshold table
st.markdown(f"### {e('📊')} {get_text('all_thresholds')}")
thresholds_df = pd.DataFrame({
    get_text('category'): ['Training', 'Training', 'Training', 'Training', 'Training',
                           get_text('disciplinary'), get_text('disciplinary'), get_text('disciplinary'), get_text('disciplinary')],
    get_text('criterion'): ['Low Score', 'High Reopen Rate', 'Low Compliance',
                            'Slow Processing', 'Weak Communication',
                            'Critical Low Score', 'Critical Reopen Rate',
                            'Repeated Violations', 'Consecutively Low'],
    get_text('threshold'): ['< 2.5', '> 15%', '< 70%', '> 2x Team Avg', '< 2.0',
                            '< 1.5', '> 30%', '> 5 in 30 days', '3x < 2'],
    get_text('risk_level'): ['YELLOW', 'YELLOW', 'YELLOW', 'YELLOW', 'YELLOW',
                             'RED', 'RED', 'RED', 'RED']
})
st.dataframe(thresholds_df, width="stretch", hide_index=True)


# ─── Auto-Refresh (once, at the bottom) ─────────────────────────────────────
if auto_refresh:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Footer
render_footer()
