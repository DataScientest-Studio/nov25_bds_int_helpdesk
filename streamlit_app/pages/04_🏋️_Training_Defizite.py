"""
Training & Deficits
Identification of training needs and disciplinary actions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import components
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Training & Deficits", page_icon="🏋️", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Training area translations
TRAINING_AREA_TRANSLATIONS = {
    'Qualität': 'Quality',
    'Effizienz': 'Efficiency', 
    'Kommunikation': 'Communication',
    'Prozess': 'Process',
    'Genauigkeit': 'Accuracy',
    'Gründlichkeit': 'Thoroughness',
    'Reaktionszeit': 'Response Time',
    'Kundenzufriedenheit': 'Customer Satisfaction',
    'Problemlösung': 'Problem Solving',
    'Dokumentation': 'Documentation',
    'Quality': 'Quality',
    'Efficiency': 'Efficiency',
    'Communication': 'Communication',
    'Process': 'Process',
    'Accuracy': 'Accuracy',
    'Thoroughness': 'Thoroughness',
    'Response Time': 'Response Time',
    'Customer Satisfaction': 'Customer Satisfaction',
    'Problem Solving': 'Problem Solving',
    'Documentation': 'Documentation'
}

def translate_training_area(area, lang='en'):
    """Translate training area names."""
    area = area.strip()
    if lang == 'en':
        return TRAINING_AREA_TRANSLATIONS.get(area, area)
    return area

# Page header
page_header(
    e("🏋️ ") + get_text('training_deficits'),
    get_text('training_subtitle'),
    help_key='training'
)

# Load data
@st.cache_data
def load_training_report():
    report_path = Path(__file__).parent.parent.parent / "reports" / "training_report.csv"
    if report_path.exists():
        df = pd.read_csv(report_path)
        # Normalize column names for compatibility
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
def load_scored_data():
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "issues_snapshot_sample.xlsx"
    if data_path.exists():
        return pd.read_excel(data_path)
    return None

report_df = load_training_report()
scored_df = load_scored_data()

if report_df is None:
    st.warning(e("⚠️ ") + get_text('training_report_not_found'))
    st.stop()

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

green_count = len(report_df[report_df['Risk Level'] == 'GREEN'])
yellow_count = len(report_df[report_df['Risk Level'] == 'YELLOW'])
red_count = len(report_df[report_df['Risk Level'] == 'RED'])
total = len(report_df)

with col1:
    st.metric(e("👥 ") + get_text('total_employees'), total)
    
with col2:
    st.metric(e("🟢 ") + get_text('ok'), green_count, f"{green_count/total*100:.0f}%")
    
with col3:
    st.metric(e("🟡 ") + get_text('training'), yellow_count, f"{yellow_count/total*100:.0f}%")
    
with col4:
    st.metric(e("🔴 ") + get_text('disciplinary'), red_count, f"{red_count/total*100:.0f}%")

st.markdown("---")

# Pie Chart
col1, col2 = st.columns([1, 2])

with col1:
    section_header(e("📊 ") + get_text('risk_overview'))
    
    fig = go.Figure(data=[go.Pie(
        labels=['GREEN', 'YELLOW', 'RED'],
        values=[green_count, yellow_count, red_count],
        hole=0.4,
        marker_colors=['#28a745', '#ffc107', '#dc3545']
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header(e("📈 ") + get_text('score_by_risk'))
    
    fig = px.box(
        report_df, 
        x='Risk Level', 
        y='Avg Score',
        color='Risk Level',
        color_discrete_map={'GREEN': '#28a745', 'YELLOW': '#ffc107', 'RED': '#dc3545'},
        title=""
    )
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    e("🔴 ") + get_text('urgent'), 
    e("🟡 ") + get_text('training_recommended'), 
    e("📋 ") + get_text('all_employees'),
    e("📖 ") + get_text('risk_level_def')
])

with tab1:
    section_header(e("🔴 ") + get_text('immediate_action'))
    
    red_employees = report_df[report_df['Risk Level'] == 'RED'].copy()
    
    if len(red_employees) == 0:
        st.success(e("✅ ") + get_text('no_critical'))
    else:
        st.error(e("⚠️ ") + f"{len(red_employees)} {get_text('critical_attention')}")
        
        for _, row in red_employees.iterrows():
            with st.expander(f"{e('👤')} {row['Employee']} - Score: {row['Avg Score']:.2f}"):
                # Translate training areas
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

with tab2:
    section_header(e("🟡 ") + get_text('training_recommended'))
    
    yellow_employees = report_df[report_df['Risk Level'] == 'YELLOW'].copy()
    
    if len(yellow_employees) == 0:
        st.success(e("✅ ") + get_text('no_training_needed'))
    else:
        st.warning(e("📚 ") + f"{len(yellow_employees)} {get_text('should_receive_training')}")
        
        # Group by training areas
        training_areas_all = []
        for areas in yellow_employees['Training Areas'].dropna():
            for a in str(areas).split(','):
                area = a.strip()
                if st.session_state.get('language') == 'en':
                    area = translate_training_area(area, 'en')
                training_areas_all.append(area)
        
        if training_areas_all:
            area_counts = pd.Series(training_areas_all).value_counts()
            
            fig = px.bar(
                x=area_counts.values,
                y=area_counts.index,
                orientation='h',
                title=get_text('common_training_needs'),
                labels={'x': get_text('count'), 'y': get_text('training_areas')}
            )
            fig.update_layout(yaxis_title=get_text('training_areas'), xaxis_title=get_text('count'))
            st.plotly_chart(fig, use_container_width=True)
        
        # Translate training areas in dataframe
        display_df = yellow_employees[['Employee', 'Avg Score', 'Tickets', 'Training Areas']].copy()
        if st.session_state.get('language') == 'en':
            display_df['Training Areas'] = display_df['Training Areas'].apply(
                lambda x: ', '.join([translate_training_area(a.strip(), 'en') for a in str(x).split(',')]) if pd.notna(x) else x
            )
        
        st.dataframe(display_df, use_container_width=True)

with tab3:
    section_header(e("📋 ") + get_text('all_employees'))
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.multiselect(
            get_text('risk_level') + " " + get_text('filter'),
            options=['GREEN', 'YELLOW', 'RED'],
            default=['GREEN', 'YELLOW', 'RED']
        )
    
    with col2:
        min_tickets = st.slider(get_text('min_tickets'), 0, int(report_df['Tickets'].max()), 0)
    
    filtered_df = report_df[
        (report_df['Risk Level'].isin(risk_filter)) &
        (report_df['Tickets'] >= min_tickets)
    ]
    
    st.dataframe(
        filtered_df.style.apply(
            lambda x: ['background-color: #d4edda' if v == 'GREEN' 
                      else 'background-color: #fff3cd' if v == 'YELLOW'
                      else 'background-color: #f8d7da' if v == 'RED'
                      else '' for v in x],
            subset=['Risk Level']
        ),
        use_container_width=True
    )

with tab4:
    section_header(e("📖 ") + get_text('risk_level_def'))
    
    intro_text = (
        "The Risk Level classification is based on objective criteria."
        if st.session_state.get('language') == 'en' else
        "Die Risk Level Klassifikation basiert auf objektiven Kriterien."
    )
    st.markdown(intro_text)
    
    # RED Definition
    st.markdown(f"### {e('🔴')} RED - {get_text('critical')}")
    
    red_table = (
        f"""
    **RED** classification when **at least one** condition is met:
    
    | {get_text('criterion')} | {get_text('threshold')} | {get_text('meaning')} |
    |-----------|---------------|-----------|
    | Critical low score | Ø < **1.5** | Performance extremely poor |
    | Critical reopen rate | > **30%** | Every 3rd ticket reopened |
    | Repeated violations | > **5** in 30 days | Constant process violations |
    | Consecutively low | **3x** in a row < 2 | Persistently poor performance |
    """
        if st.session_state.get('language') == 'en' else
        f"""
    **RED** Klassifikation wenn **mindestens eine** Bedingung erfüllt ist:
    
    | {get_text('criterion')} | {get_text('threshold')} | {get_text('meaning')} |
    |-----------|---------------|-----------|
    | Kritisch niedriger Score | Ø < **1.5** | Performance extrem schlecht |
    | Kritische Reopen-Rate | > **30%** | Jedes 3. Ticket wiedereröffnet |
    | Wiederholte Verstöße | > **5** in 30 Tagen | Ständige Prozessverstöße |
    | Konsekutiv niedrig | **3x** hintereinander < 2 | Anhaltend schlechte Performance |
    """
    )
    st.error(red_table)
    
    # YELLOW Definition
    st.markdown(f"### {e('🟡')} YELLOW - {get_text('training_recommended')}")
    
    yellow_table = (
        f"""
    **YELLOW** classification when **at least one** condition is met (but no RED):
    
    | {get_text('criterion')} | {get_text('threshold')} | Training |
    |-----------|---------------|---------------------|
    | Low score | Ø < **2.5** | General quality training |
    | High reopen rate | > **15%** | Quality assurance training |
    | Low compliance | < **70%** | Process training |
    | Slow processing | > **2x** team avg | Efficiency training |
    | Weak communication | Score < **2.0** | Communication training |
    """
        if st.session_state.get('language') == 'en' else
        f"""
    **YELLOW** Klassifikation wenn **mindestens eine** Bedingung erfüllt ist (aber keine RED):
    
    | {get_text('criterion')} | {get_text('threshold')} | Training |
    |-----------|---------------|---------------------|
    | Niedriger Score | Ø < **2.5** | Allgemeines Qualitätstraining |
    | Hohe Reopen-Rate | > **15%** | Qualitätssicherungstraining |
    | Niedrige Compliance | < **70%** | Prozesstraining |
    | Langsame Bearbeitung | > **2x** Team-Durchschnitt | Effizienztraining |
    | Schwache Kommunikation | Score < **2.0** | Kommunikationstraining |
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
    
    st.dataframe(thresholds_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Recommendations
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

# Footer
render_footer()
