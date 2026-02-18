"""
Trend Analysis
Performance development over time - based on Q-Scores (Manager ratings).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Trend Analysis", page_icon="📈", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()


def t(de_text, en_text):
    """Simple translation helper."""
    return en_text if st.session_state.get('language') == 'en' else de_text


# Page header
page_header(
    e("📈 ") + get_text('trend_analysis'),
    get_text('trend_subtitle'),
    help_key='trends'
)

# Load data
@st.cache_data
def load_data():
    project_root = Path(__file__).parent.parent.parent
    
    # Q vs O Score Comparison (has Q-Scores per employee)
    comparison_path = project_root / "data" / "processed" / "q_vs_o_score_comparison.csv"
    employee_df = pd.DataFrame()
    
    if comparison_path.exists():
        employee_df = pd.read_csv(comparison_path)
        
        # Calculate Risk Level based on Q-Score average
        employee_df['Risk Level'] = pd.cut(
            employee_df['q_score_avg'],
            bins=[0, 2.5, 3.5, 5.01],
            labels=['RED', 'YELLOW', 'GREEN']
        )
        
        # Rename for compatibility
        employee_df['Employee'] = employee_df['employee']
        employee_df['Avg Score'] = employee_df['q_score_avg']
        employee_df['Tickets'] = employee_df['ticket_count']
        employee_df['Q1'] = employee_df['q1']
        employee_df['Q2'] = employee_df['q2']
        employee_df['Q3'] = employee_df['q3']
    
    # Workflow Analysis
    workflow_path = project_root / "data" / "processed" / "workflow_analysis.csv"
    workflow_df = pd.read_csv(workflow_path) if workflow_path.exists() else pd.DataFrame()
    
    return employee_df, workflow_df

employee_df, workflow_df = load_data()

# Tabs
tab1, tab2, tab3 = st.tabs([
    e("👥 ") + get_text('employee_trends'), 
    e("📊 ") + "Q-Score Details",
    e("🔮 ") + get_text('forecast')
])

with tab1:
    section_header(e("👥 ") + get_text('performance_per_employee'), 'trend_employees')
    
    if not employee_df.empty:
        # Risk Level Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            risk_counts = employee_df['Risk Level'].value_counts()
            
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title=get_text('risk_distribution') + " (Q-Score)",
                color=risk_counts.index,
                color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Score distribution by Risk Level
            fig = px.box(
                employee_df,
                x='Risk Level',
                y='Avg Score',
                title=get_text('scores_by_risk') + " (Q-Score Avg)",
                color='Risk Level',
                color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top & Bottom Performers
        st.markdown(f"### {e('🏆')} Top & Bottom Performer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{e('🥇')} {get_text('top_10_highest')}**")
            top10 = employee_df.nlargest(10, 'Avg Score')[['Employee', 'Q1', 'Q2', 'Q3', 'Avg Score', 'Tickets', 'Risk Level']]
            st.dataframe(top10, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown(f"**{e('⚠️')} {get_text('bottom_10_lowest')}**")
            bottom10 = employee_df.nsmallest(10, 'Avg Score')[['Employee', 'Q1', 'Q2', 'Q3', 'Avg Score', 'Tickets', 'Risk Level']]
            st.dataframe(bottom10, use_container_width=True, hide_index=True)
        
        # Ticket Volume vs Score
        section_header(e("📊 ") + get_text('ticket_volume_vs_performance'))
        
        fig = px.scatter(
            employee_df,
            x='Tickets',
            y='Avg Score',
            color='Risk Level',
            size='Tickets',
            hover_data=['Employee', 'Q1', 'Q2', 'Q3'],
            title=get_text('relationship_tickets_performance') + " (Q-Score)",
            color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate correlation
        corr = employee_df['Tickets'].corr(employee_df['Avg Score'])
        
        if corr > 0.3:
            st.success(f"{e('📈')} {get_text('positive_correlation')} ({corr:.2f}): {get_text('more_tickets_higher')}")
        elif corr < -0.3:
            st.warning(f"{e('📉')} {get_text('negative_correlation')} ({corr:.2f}): {get_text('more_tickets_lower')}")
        else:
            st.info(f"➡️ {get_text('weak_correlation')} ({corr:.2f}): {get_text('little_influence')}")
    else:
        st.info(get_text('no_data'))

with tab2:
    q_score_dimensions = t("Q-Score Dimensionen", "Q-Score Dimensions")
    section_header(e("📊 ") + q_score_dimensions)
    
    if not employee_df.empty:
        dimensions_desc = t(
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
        )
        st.markdown(dimensions_desc)
        
        col1, col2, col3 = st.columns(3)
        
        q1_title = t("Q1: Genauigkeit Verteilung", "Q1: Accuracy Distribution")
        q2_title = t("Q2: Gründlichkeit Verteilung", "Q2: Thoroughness Distribution")
        q3_title = t("Q3: Reaktionsfähigkeit Verteilung", "Q3: Responsiveness Distribution")
        
        with col1:
            fig = px.histogram(
                employee_df, x='Q1', nbins=5,
                title=q1_title,
                color_discrete_sequence=['#2196F3']
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
            st.metric(t("Ø Q1", "Avg Q1"), f"{employee_df['Q1'].mean():.2f}")
        
        with col2:
            fig = px.histogram(
                employee_df, x='Q2', nbins=5,
                title=q2_title,
                color_discrete_sequence=['#9C27B0']
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
            st.metric(t("Ø Q2", "Avg Q2"), f"{employee_df['Q2'].mean():.2f}")
        
        with col3:
            fig = px.histogram(
                employee_df, x='Q3', nbins=5,
                title=q3_title,
                color_discrete_sequence=['#FF9800']
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
            st.metric(t("Ø Q3", "Avg Q3"), f"{employee_df['Q3'].mean():.2f}")
        
        # Q-Score Correlation Matrix
        corr_title = t("Q-Score Korrelationen", "Q-Score Correlations")
        section_header(e("🔗 ") + corr_title)
        
        q_cols = ['Q1', 'Q2', 'Q3', 'Avg Score', 'Tickets']
        corr_matrix = employee_df[q_cols].corr()
        
        corr_chart_title = t("Korrelation zwischen Q-Scores", "Correlation between Q-Scores")
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title=corr_chart_title
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Q-Score vs O-Score Comparison
        if 'o_score' in employee_df.columns:
            qo_title = t("Q-Score vs O-Score", "Q-Score vs O-Score")
            section_header(e("⚖️ ") + qo_title)
            
            scatter_title = t(
                "Manager-Bewertung (Q) vs Objektive Metriken (O)",
                "Manager Rating (Q) vs Objective Metrics (O)"
            )
            q_label = t("Q-Score (Manager)", "Q-Score (Manager)")
            o_label = t("O-Score (Objektiv)", "O-Score (Objective)")
            
            fig = px.scatter(
                employee_df,
                x='q_score_avg',
                y='o_score',
                color='Risk Level',
                hover_data=['Employee'],
                title=scatter_title,
                labels={'q_score_avg': q_label, 'o_score': o_label},
                color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            )
            # Add diagonal reference line
            fig.add_trace(go.Scatter(
                x=[1, 5], y=[1, 5],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='Ideal (Q=O)'
            ))
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Bias indicator
            avg_diff = employee_df['score_diff'].mean()
            if avg_diff < -0.5:
                leniency_msg = t(
                    f"**Leniency Bias erkannt:** Manager bewerten im Schnitt {abs(avg_diff):.1f} Punkte höher als objektive Metriken",
                    f"**Leniency Bias detected:** Managers rate on average {abs(avg_diff):.1f} points higher than objective metrics"
                )
                st.warning(e("⚠️ ") + leniency_msg)
            elif avg_diff > 0.5:
                severity_msg = t(
                    f"**Severity Bias erkannt:** Manager bewerten im Schnitt {avg_diff:.1f} Punkte niedriger als objektive Metriken",
                    f"**Severity Bias detected:** Managers rate on average {avg_diff:.1f} points lower than objective metrics"
                )
                st.warning(e("⚠️ ") + severity_msg)
            else:
                low_diff_msg = t(
                    f"Geringe Abweichung zwischen Q-Score und O-Score ({avg_diff:.2f})",
                    f"Low deviation between Q-Score and O-Score ({avg_diff:.2f})"
                )
                st.success(e("✅ ") + low_diff_msg)
    else:
        st.info(get_text('no_data'))

with tab3:
    section_header(e("🔮 ") + get_text('forecast_recommendations'), 'forecast')
    
    if not employee_df.empty:
        # Simulated forecast (based on current trends)
        st.markdown(f"""
        ### {get_text('what_if_scenario')}
        
        {get_text('simulate_interventions')}
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            training_effect = st.slider(
                get_text('training_effect'),
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1
            )
        
        with col2:
            target_employees = st.multiselect(
                get_text('target_group'),
                options=['RED', 'YELLOW', 'GREEN'],
                default=['RED', 'YELLOW']
            )
        
        # Calculate simulation
        simulated_df = employee_df.copy()
        mask = simulated_df['Risk Level'].isin(target_employees)
        simulated_df.loc[mask, 'Avg Score'] = simulated_df.loc[mask, 'Avg Score'] * (1 + training_effect)
        simulated_df.loc[simulated_df['Avg Score'] > 5, 'Avg Score'] = 5  # Cap at 5
        
        # Recalculate Risk Levels
        simulated_df['New Risk Level'] = pd.cut(
            simulated_df['Avg Score'],
            bins=[0, 2.5, 3.5, 5.01],
            labels=['RED', 'YELLOW', 'GREEN']
        )
        
        # Show impact
        st.markdown(f"### {get_text('simulation_results')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            old_red = (employee_df['Risk Level'] == 'RED').sum()
            new_red = (simulated_df['New Risk Level'] == 'RED').sum()
            delta = new_red - old_red
            st.metric(
                e("🔴 ") + "RED",
                new_red,
                delta=delta,
                delta_color="inverse"
            )
        
        with col2:
            old_yellow = (employee_df['Risk Level'] == 'YELLOW').sum()
            new_yellow = (simulated_df['New Risk Level'] == 'YELLOW').sum()
            delta = new_yellow - old_yellow
            st.metric(
                e("🟡 ") + "YELLOW",
                new_yellow,
                delta=delta,
                delta_color="inverse"
            )
        
        with col3:
            old_green = (employee_df['Risk Level'] == 'GREEN').sum()
            new_green = (simulated_df['New Risk Level'] == 'GREEN').sum()
            delta = new_green - old_green
            st.metric(
                e("🟢 ") + "GREEN",
                new_green,
                delta=delta,
                delta_color="normal"
            )
        
        # Comparison chart
        fig = go.Figure()
        
        for risk, color in [('RED', '#f44336'), ('YELLOW', '#FF9800'), ('GREEN', '#4CAF50')]:
            fig.add_trace(go.Bar(
                name=f'{risk} (Current)',
                x=[risk],
                y=[(employee_df['Risk Level'] == risk).sum()],
                marker_color=color,
                opacity=0.5
            ))
            fig.add_trace(go.Bar(
                name=f'{risk} (After)',
                x=[risk],
                y=[(simulated_df['New Risk Level'] == risk).sum()],
                marker_color=color
            ))
        
        fig.update_layout(
            title=get_text('before_after_comparison'),
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.markdown(f"### {e('💡')} {get_text('recommendations')}")
        
        improvements = old_red - new_red + old_yellow - new_yellow
        if improvements > 0:
            st.success(f"""
            {get_text('with_training_effect')} **{training_effect*100:.0f}%** {get_text('on_employees')} 
            **{', '.join(target_employees)}** {get_text('categories')}:
            
            - **{improvements}** {get_text('employees_would_improve')}
            - **{new_green - old_green}** {get_text('more_in_green')}
            """)
        else:
            st.info(get_text('adjust_parameters'))
    else:
        st.info(get_text('no_data'))

# Footer
render_footer()
