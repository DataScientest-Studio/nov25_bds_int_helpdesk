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
    
    # Training Report
    training_path = project_root / "reports" / "training_report.csv"
    training_df = pd.read_csv(training_path) if training_path.exists() else pd.DataFrame()
    
    return ml_df, workflow_df, training_df

ml_df, workflow_df, training_df = load_data()

# Tabs
tab1, tab2 = st.tabs([
    e("👥 ") + get_text('employee_trends'), 
    e("🔮 ") + get_text('forecast')
])

with tab1:
    section_header(e("👥 ") + get_text('performance_per_employee'), 'trend_employees')
    
    if not training_df.empty:
        # Risk Level Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            risk_counts = training_df['Risk Level'].value_counts()
            
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
                training_df,
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
            top10 = training_df.nlargest(10, 'Avg Score')[['Employee', 'Avg Score', 'Tickets', 'Risk Level']]
            st.dataframe(top10, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown(f"**{e('⚠️')} {get_text('bottom_10_lowest')}**")
            bottom10 = training_df.nsmallest(10, 'Avg Score')[['Employee', 'Avg Score', 'Tickets', 'Risk Level']]
            st.dataframe(bottom10, use_container_width=True, hide_index=True)
        
        # Ticket Volume vs Score
        section_header(e("📊 ") + get_text('ticket_volume_vs_performance'))
        
        fig = px.scatter(
            training_df,
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
        corr = training_df['Tickets'].corr(training_df['Avg Score'])
        
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
    
    if not training_df.empty:
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
            training_coverage = st.slider(
                get_text('training_coverage'),
                min_value=0,
                max_value=100,
                value=50,
                step=10
            )
        
        # Simulation
        yellow_count = len(training_df[training_df['Risk Level'] == 'YELLOW'])
        trained = int(yellow_count * training_coverage / 100)
        improved = int(trained * 0.8)  # 80% success rate assumed
        
        st.markdown("---")
        
        current_green = len(training_df[training_df['Risk Level'] == 'GREEN'])
        
        st.markdown(f"""
        ### {e('📊')} {get_text('forecast_at')} {training_coverage}% Training Coverage:
        
        | {get_text('metric')} | {get_text('current')} | {get_text('after_training')} |
        |--------|---------|---------------|
        | YELLOW {get_text('employees')} | {yellow_count} | {yellow_count - improved} |
        | GREEN {get_text('employees')} | {current_green} | {current_green + improved} |
        | {get_text('expected_improvement')} | - | +{training_effect:.1f} {get_text('average')} |
        
        **{get_text('roi_estimate')}:**
        - {get_text('trained_employees')}: {trained}
        - {get_text('expected_improvements')}: {improved} (80% {get_text('success_rate')})
        - {get_text('potential_productivity')}: ~{improved * 5}% {get_text('team_performance')}
        """)
        
        # Temporal trend (simulated)
        st.markdown("---")
        section_header(e("📈 ") + get_text('simulated_6month_trend'))
        
        # Generate simulated trend data
        months = pd.date_range(start='2026-01', periods=6, freq='M')
        
        current_avg = training_df['Avg Score'].mean()
        trend_data = []
        
        for i, month in enumerate(months):
            # Simulate gradual improvement trend
            improvement = (training_effect * training_coverage / 100) * (i / 5)
            trend_data.append({
                get_text('month'): month.strftime('%b %Y'),
                get_text('without_intervention'): current_avg + np.random.normal(0, 0.1),
                get_text('with_training'): current_avg + improvement + np.random.normal(0, 0.1)
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_df[get_text('month')],
            y=trend_df[get_text('without_intervention')],
            name=get_text('without_intervention'),
            line=dict(color='#f44336', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=trend_df[get_text('month')],
            y=trend_df[get_text('with_training')],
            name=get_text('with_training'),
            line=dict(color='#4CAF50')
        ))
        
        fig.update_layout(
            title=get_text('forecast_score_development'),
            xaxis_title=get_text('month'),
            yaxis_title="Ø Score",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(get_text('no_data'))

# Footer
render_footer()
