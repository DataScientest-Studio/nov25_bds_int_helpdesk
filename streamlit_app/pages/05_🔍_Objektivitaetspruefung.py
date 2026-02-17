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

# Page header
page_header(
    e("🔍 ") + get_text('nav_bias'),
    "Analysis of fairness and objectivity of manager ratings" if st.session_state.language == 'en' else 
    "Analyse der Fairness und Objektivität der Manager-Bewertungen",
    help_key='bias'
)

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

# Bias Overview
section_header(e("🚨 ") + "Detected Bias Types" if st.session_state.language == 'en' else "Erkannte Bias-Typen")

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
    
    > {"The manager rates all three dimensions (Q1, Q2, Q3) almost identically. This indicates that the overall impression dominates the individual ratings." if st.session_state.language == 'en' else "Der Manager bewertet alle drei Dimensionen (Q1, Q2, Q3) fast identisch. Dies deutet darauf hin, dass der Gesamteindruck die Einzelbewertungen dominiert."}
    """)

with col2:
    # Leniency/Severity
    avg_q1 = df['Q1'].mean()
    
    bias_type = get_text('bias_leniency') if avg_q1 > 3.5 else "Severity" if avg_q1 < 2.5 else get_text('neutral')
    bias_color = "orange" if avg_q1 > 3.5 else "blue" if avg_q1 < 2.5 else "green"
    
    interpretation = (
        "The manager rates systematically too mild." if st.session_state.language == 'en' else "Der Manager bewertet systematisch zu mild."
    ) if avg_q1 > 3.5 else (
        "The manager rates systematically too strict." if st.session_state.language == 'en' else "Der Manager bewertet systematisch zu streng."
    ) if avg_q1 < 2.5 else (
        "The rating is balanced." if st.session_state.language == 'en' else "Die Bewertung ist ausgeglichen."
    )
    
    st.markdown(f"""
    ### {e('📊')} {get_text('bias_leniency')}/Severity Bias
    
    **{get_text('average')} Score:** `{avg_q1:.2f}` (expected: 3.0)
    
    **Type:** :{bias_color}[{bias_type}]
    
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
    fig.update_layout(title=get_text('score_distribution') + " per Dimension", yaxis_title="Score")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recommendations
section_header(e("💡 ") + get_text('recommendations'))

col1, col2 = st.columns(2)

with col1:
    against_halo = "Against Halo Effect" if st.session_state.language == 'en' else "Gegen Halo-Effekt"
    st.markdown(f"""
    ### {against_halo}:
    1. **Separate rating rounds** for each dimension
    2. **Time gap** between ratings
    3. **Structured rating forms** with concrete criteria
    4. **Anonymization** of employee names during rating
    """)

with col2:
    against_leniency = "Against Leniency Bias" if st.session_state.language == 'en' else "Gegen Leniency Bias"
    st.markdown(f"""
    ### {against_leniency}:
    1. **Calibration sessions** with multiple managers
    2. **Concrete benchmarks** for each score level (1-5)
    3. Consider **forced distribution**
    4. Introduce **peer reviews** as second opinion
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
