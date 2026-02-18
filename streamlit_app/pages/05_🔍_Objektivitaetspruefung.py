"""
Objectivity Check
Bias analysis of manager ratings.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Objectivity Check", page_icon="🔍", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Page header (without subtitle)
st.title(e("🔍 ") + get_text('nav_bias'))
st.markdown("---")

# Load data
@st.cache_data
def load_scored_data():
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "issues_snapshot_sample.xlsx"
    if data_path.exists():
        df = pd.read_excel(data_path)
        return df[df['Q1'] > 0]  # Only valid scores
    return None

df = load_scored_data()

if df is None:
    st.error(get_text('no_data'))
    st.stop()

# Bias Overview (section header without "detected_bias_types")
bias_title = "Bias Types" if st.session_state.get('language') == 'en' else "Bias-Typen"
section_header(e("🚨 ") + bias_title)

col1, col2 = st.columns(2)

with col1:
    # Halo Effect
    corr_matrix = df[['Q1', 'Q2', 'Q3']].corr()
    avg_corr = (corr_matrix.values.sum() - 3) / 6
    
    severity = get_text('bias_high') if avg_corr > 0.9 else get_text('bias_medium') if avg_corr > 0.8 else get_text('bias_low')
    severity_color = "red" if avg_corr > 0.9 else "orange" if avg_corr > 0.8 else "green"
    
    st.markdown(f"""
    ### {e('🔄')} {get_text('bias_halo')}
    
    **{get_text('inter_correlation')}:** `{avg_corr:.3f}`
    
    **{get_text('bias_severity')}:** :{severity_color}[{severity}]
    
    > {get_text('manager_rates_identical')}
    """)

with col2:
    # Leniency/Severity
    avg_q1 = df['Q1'].mean()
    
    bias_type = get_text('bias_leniency') if avg_q1 > 3.5 else get_text('severity') if avg_q1 < 2.5 else get_text('neutral')
    bias_color = "orange" if avg_q1 > 3.5 else "blue" if avg_q1 < 2.5 else "green"
    
    if avg_q1 > 3.5:
        interpretation = get_text('manager_rates_mild')
    elif avg_q1 < 2.5:
        interpretation = get_text('manager_rates_strict')
    else:
        interpretation = get_text('rating_balanced')
    
    expected_label = "expected" if st.session_state.get('language') == 'en' else "erwartet"
    
    st.markdown(f"""
    ### {e('📊')} {get_text('bias_leniency')}/{get_text('severity')} Bias
    
    **{get_text('average')} Score:** `{avg_q1:.2f}` ({expected_label}: 3.0)
    
    **{get_text('type')}:** :{bias_color}[{bias_type}]
    
    > {interpretation}
    """)

st.markdown("---")

# Correlation Matrix
col1, col2 = st.columns([1, 1])

with col1:
    section_header(e("📊 ") + get_text('correlation_matrix'), 'correlation')
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=['Q1', 'Q2', 'Q3'],
        y=['Q1', 'Q2', 'Q3'],
        colorscale='RdYlGn_r',
        zmin=0, zmax=1,
        text=np.round(corr_matrix.values, 3),
        texttemplate="%{text}",
        textfont={"size": 16}
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header(e("📈 ") + get_text('score_distribution'))
    
    fig = go.Figure()
    for q in ['Q1', 'Q2', 'Q3']:
        fig.add_trace(go.Histogram(
            x=df[q],
            name=q,
            opacity=0.6,
            nbinsx=5
        ))
    
    fig.update_layout(
        barmode='overlay',
        xaxis_title="Score (1-5)",
        yaxis_title=get_text('count'),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Scatter Plot: Q1 vs Q2 vs Q3
section_header(e("🔗 ") + get_text('score_relationships'))

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(df, x='Q1', y='Q2', color='Q3', 
                     title="Q1 vs Q2 (Color = Q3)",
                     color_continuous_scale='RdYlGn')
    fig.add_trace(go.Scatter(x=[1,5], y=[1,5], mode='lines', 
                             name=get_text('perfect_correlation'), 
                             line=dict(dash='dash', color='gray')))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Box-Plot per Score
    fig = go.Figure()
    for q in ['Q1', 'Q2', 'Q3']:
        fig.add_trace(go.Box(y=df[q], name=q))
    per_dimension = "per Dimension" if st.session_state.get('language') == 'en' else "pro Dimension"
    fig.update_layout(title=get_text('score_distribution') + " " + per_dimension, yaxis_title="Score")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recommendations
section_header(e("💡 ") + get_text('recommendations'))

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    ### {get_text('against_halo')}:
    1. **{get_text('separate_rating_rounds')}**
    2. **{get_text('time_gap')}**
    3. **{get_text('structured_forms')}**
    4. **{get_text('anonymization')}**
    """)

with col2:
    st.markdown(f"""
    ### {get_text('against_leniency')}:
    1. **{get_text('calibration_sessions')}**
    2. **{get_text('concrete_benchmarks')}**
    3. **{get_text('forced_distribution')}**
    4. **{get_text('peer_reviews')}**
    """)

st.markdown("---")

# Statistics Table
section_header(e("📋 ") + get_text('statistical_summary'))

stats = pd.DataFrame({
    get_text('metric'): [
        get_text('sample_count'), 
        get_text('mean'), 
        get_text('std_dev'), 
        get_text('median'), 
        get_text('min'), 
        get_text('max')
    ],
    'Q1': [len(df), df['Q1'].mean(), df['Q1'].std(), df['Q1'].median(), df['Q1'].min(), df['Q1'].max()],
    'Q2': [len(df), df['Q2'].mean(), df['Q2'].std(), df['Q2'].median(), df['Q2'].min(), df['Q2'].max()],
    'Q3': [len(df), df['Q3'].mean(), df['Q3'].std(), df['Q3'].median(), df['Q3'].min(), df['Q3'].max()],
}).round(2)

st.dataframe(stats, use_container_width=True)

# Footer
render_footer()
