"""
Help Desk Performance Monitor - Streamlit Dashboard
Complete Multi-Page App with Live Data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings component
from components.settings import (
    init_session_state, render_settings_sidebar, render_footer,
    get_text, get_help, section_header, page_header, e, maybe_emoji
)

# Page configuration
st.set_page_config(
    page_title="HelpDesk Performance Monitor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"


@st.cache_data
def load_data():
    """Load all datasets."""
    data = {}
    
    raw_dir = DATA_DIR / "raw"
    if (raw_dir / "issues.csv").exists():
        data['issues'] = pd.read_csv(raw_dir / "issues.csv")
        data['snapshots'] = pd.read_csv(raw_dir / "issues_snapshot.csv")
        data['scored'] = pd.read_excel(raw_dir / "issues_snapshot_sample.xlsx")
        data['utterances'] = pd.read_csv(raw_dir / "sample_utterances.csv")
    
    processed_dir = DATA_DIR / "processed"
    if (processed_dir / "ml_dataset.csv").exists():
        data['ml_dataset'] = pd.read_csv(processed_dir / "ml_dataset.csv")
    
    return data


def main():
    """Main dashboard page."""
    
    # Initialize session state
    init_session_state()
    
    # === SIDEBAR: NAVIGATION & SETTINGS ===
    st.sidebar.title(e("🎯 ") + get_text('app_title'))
    
    # Render settings sidebar (includes navigation)
    render_settings_sidebar()
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **{get_text('project')}:** Help Desk Performance  
    **Status:** {get_text('production_ready')}
    """)
    
    # === HEADER ===
    st.title(e("🎯 ") + get_text('title'))
    st.markdown(f"**{get_text('subtitle')}**")
    
    # Load data
    try:
        data = load_data()
    except Exception as ex:
        st.error(f"{get_text('error')}: {ex}")
        return
    
    if not data:
        st.warning(f"""
        {e("⚠️ ")} {get_text('no_data')}
        
        Please ensure datasets are in `data/raw/`.
        """)
        return
    
    # === KPI CARDS ===
    st.markdown("---")
    
    # Section Header with help icon
    section_header(e("📊 ") + get_text('overview'), 'overview')
    
    col1, col2, col3, col4 = st.columns(4)
    
    issues = data.get('issues', pd.DataFrame())
    scored = data.get('scored', pd.DataFrame())
    
    with col1:
        st.metric(
            label=e("📋 ") + get_text('total_tickets'),
            value=f"{len(issues):,}",
            delta=f"66k+ {get_text('analyzed')}"
        )
    
    with col2:
        if 'wf_total_time' in issues.columns:
            avg_time = issues['wf_total_time'].mean() / 3600
            st.metric(
                label=e("⏱️ ") + get_text('avg_time'),
                value=f"{avg_time:.1f}h",
                delta=get_text('hours')
            )
        else:
            st.metric(label=e("⏱️ ") + get_text('avg_time'), value="N/A")
    
    with col3:
        st.metric(
            label=e("✅ ") + get_text('scored_samples'),
            value=f"{len(scored):,}",
            delta=get_text('ground_truth')
        )
    
    with col4:
        if 'Q1' in scored.columns:
            valid_scores = scored[scored['Q1'] > 0]['Q1']
            avg_score = valid_scores.mean()
            st.metric(
                label=e("⭐ ") + get_text('avg_score'),
                value=f"{avg_score:.2f}/5",
                delta=get_text('manager_rating')
            )
        else:
            st.metric(label=e("⭐ ") + get_text('avg_score'), value="N/A")
    
    st.markdown("---")
    
    # === TWO-COLUMN LAYOUT ===
    col1, col2 = st.columns(2)
    
    with col1:
        # Score Distribution with help icon
        section_header(e("📈 ") + get_text('score_dist'), 'score_dist')
        
        if 'Q1' in scored.columns:
            valid_scored = scored[scored['Q1'] > 0]
            
            fig = go.Figure()
            for q in ['Q1', 'Q2', 'Q3']:
                fig.add_trace(go.Histogram(
                    x=valid_scored[q],
                    name=q,
                    opacity=0.7
                ))
            
            fig.update_layout(
                barmode='overlay',
                xaxis_title="Score",
                yaxis_title=get_text('count'),
                legend_title="Dimension",
                height=350
            )
            st.plotly_chart(fig, width="stretch")
    
    with col2:
        # Bias Analysis with help icon
        section_header(e("🔍 ") + get_text('bias_analysis'), 'bias_section')
        
        if 'Q1' in scored.columns:
            valid_scored = scored[scored['Q1'] > 0]
            
            # Halo Effect
            corr_matrix = valid_scored[['Q1', 'Q2', 'Q3']].corr()
            avg_corr = (corr_matrix.values.sum() - 3) / 6
            
            halo_status = f"{e('⚠️ ')} {get_text('bias_high')}" if avg_corr > 0.8 else f"{e('✅ ')} {get_text('bias_ok')}"
            leniency_status = f"{e('⚠️ ')} {get_text('bias_too_mild')}" if valid_scored['Q1'].mean() > 3.5 else f"{e('✅ ')} {get_text('bias_ok')}"
            std_status = f"{e('⚠️ ')} {get_text('bias_central')}" if valid_scored['Q1'].std() < 0.8 else f"{e('✅ ')} {get_text('bias_ok')}"
            
            st.markdown(f"""
            | {get_text('bias_type')} | {get_text('bias_value')} | {get_text('status')} |
            |----------|------|--------|
            | **{get_text('bias_halo')}** | {avg_corr:.3f} | {halo_status} |
            | **{get_text('bias_leniency')}** (Q1) | Ø {valid_scored['Q1'].mean():.2f} | {leniency_status} |
            | **{get_text('bias_std')}** (Q1) | {valid_scored['Q1'].std():.2f} | {std_status} |
            """)
            
            st.warning(f"""
            {e("⚠️ ")} **{get_text('bias_problems')}**
            - {get_text('bias_problem1')}
            - {get_text('bias_problem2')}
            """)
    
    st.markdown("---")
    
    # === EMPLOYEE OVERVIEW ===
    section_header(e("👥 ") + get_text('employee_overview'), 'employees_section')
    
    if 'assignee' in scored.columns and 'Q1' in scored.columns:
        valid_scored = scored[scored['Q1'] > 0]
        
        assignee_stats = valid_scored.groupby('assignee').agg({
            'Q1': ['mean', 'count'],
            'Q2': 'mean',
            'Q3': 'mean'
        }).reset_index()
        assignee_stats.columns = ['Assignee', 'Ø Q1', get_text('count'), 'Ø Q2', 'Ø Q3']
        assignee_stats = assignee_stats.sort_values(get_text('count'), ascending=False).head(15)
        
        chart_title = "Top 15 Employees by Rated Tickets" if st.session_state.language == 'en' else "Top 15 Mitarbeiter nach Anzahl bewerteter Tickets"
        fig = px.bar(
            assignee_stats,
            x='Assignee',
            y=['Ø Q1', 'Ø Q2', 'Ø Q3'],
            title=chart_title,
            barmode='group',
            height=400
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, width="stretch")
    
    st.markdown("---")
    
    # === MODEL STATUS ===
    section_header(e("🤖 ") + get_text('model_status'), 'model_section')
    
    model_path = MODELS_DIR / "optimized_scorer.joblib"
    if not model_path.exists():
        model_path = MODELS_DIR / "q_score_model.joblib"
    
    if model_path.exists():
        st.success(e("✅ ") + get_text('model_trained'))
        
        import joblib
        model_data = joblib.load(model_path)
        metrics = model_data.get('metrics', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            acc = metrics.get('Q1', {}).get('accuracy', 0) * 100
            st.metric("Q1 Accuracy", f"{acc:.1f}%")
        with col2:
            acc = metrics.get('Q2', {}).get('accuracy', 0) * 100
            st.metric("Q2 Accuracy", f"{acc:.1f}%")
        with col3:
            acc = metrics.get('Q3', {}).get('accuracy', 0) * 100
            st.metric("Q3 Accuracy", f"{acc:.1f}%")
    else:
        st.warning(e("⚠️ ") + get_text('model_missing'))
    
    # === FOOTER ===
    render_footer()


if __name__ == "__main__":
    main()
