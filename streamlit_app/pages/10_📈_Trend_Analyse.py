"""
Trend Analysis
Performance development over time.
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
    
    # ML Dataset
    ml_path = project_root / "data" / "processed" / "ml_dataset.csv"
    ml_df = pd.read_csv(ml_path) if ml_path.exists() else pd.DataFrame()
    
    # Workflow Analysis (has timestamps)
    workflow_path = project_root / "data" / "processed" / "workflow_analysis.csv"
    workflow_df = pd.read_csv(workflow_path) if workflow_path.exists() else pd.DataFrame()
    
    # O-Score Results (employee performance)
    o_score_path = project_root / "data" / "processed" / "o_score_results.csv"
    o_score_df = pd.DataFrame()
    if o_score_path.exists():
        o_score_df = pd.read_csv(o_score_path)
        # Add Risk Level based on o_score
        o_score_df['Risk Level'] = pd.cut(
            o_score_df['o_score'],
            bins=[0, 2.5, 3.5, 5],
            labels=['RED', 'YELLOW', 'GREEN']
        )
        # Rename for compatibility
        o_score_df['Employee'] = o_score_df['employee']
        o_score_df['Avg Score'] = o_score_df['o_score']
        o_score_df['Tickets'] = o_score_df['ticket_count']
    
    return ml_df, workflow_df, o_score_df

ml_df, workflow_df, employee_df = load_data()

# Tabs
tab1, tab2 = st.tabs([
    e("👥 ") + get_text('employee_trends'), 
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
                title=get_text('risk_distribution'),
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
                title=get_text('scores_by_risk'),
                color='Risk Level',
                color_discrete_map={'GREEN': '#4CAF50', 'YELLOW': '#FF9800', 'RED': '#f44336'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top & Bottom Performers
        st.markdown(f"### {e('🏆')} Top & Bottom Performer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{e('🥇')} {get_text('top_10_highest')}**")
            top10 = employee_df.nlargest(10, 'Avg Score')[['Employee', 'Avg Score', 'Tickets', 'Risk Level']]
            st.dataframe(top10, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown(f"**{e('⚠️')} {get_text('bottom_10_lowest')}**")
            bottom10 = employee_df.nsmallest(10, 'Avg Score')[['Employee', 'Avg Score', 'Tickets', 'Risk Level']]
            st.dataframe(bottom10, use_container_width=True, hide_index=True)
        
        # Ticket Volume vs Score
        section_header(e("📊 ") + get_text('ticket_volume_vs_performance'))
        
        fig = px.scatter(
            employee_df,
            x='Tickets',
            y='Avg Score',
            color='Risk Level',
            size='Tickets',
            hover_data=['Employee'],
            title=get_text('relationship_tickets_performance'),
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
            bins=[0, 2.5, 3.5, 5],
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
