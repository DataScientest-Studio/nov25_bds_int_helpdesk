"""
Communication Analysis (NLP)
Sentiment, politeness and communication patterns.
"""

import streamlit as st
import pandas as pd
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

st.set_page_config(page_title="Communication & NLP", page_icon="💬", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Page header
page_header(
    e("💬 ") + get_text('communication_analysis'),
    get_text('communication_subtitle'),
    help_key='nlp'
)

# Load data
@st.cache_data
def load_nlp_data():
    nlp_path = Path(__file__).parent.parent.parent / "data" / "processed" / "nlp_features.csv"
    if nlp_path.exists():
        return pd.read_csv(nlp_path)
    return None

@st.cache_data
def load_scored_data():
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "issues_snapshot_sample.xlsx"
    if data_path.exists():
        return pd.read_excel(data_path)
    return None

nlp_df = load_nlp_data()
scored_df = load_scored_data()

if nlp_df is None:
    st.warning(e("⚠️ ") + get_text('nlp_not_found'))
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(e("📝 ") + get_text('analyzed_issues'), len(nlp_df))

with col2:
    avg_sentiment = nlp_df['sentiment_compound_mean'].mean()
    sentiment_label = get_text('positive') if avg_sentiment > 0.1 else get_text('neutral') if avg_sentiment > -0.1 else get_text('negative')
    st.metric(e("😊 ") + get_text('avg_sentiment'), f"{avg_sentiment:.3f}", sentiment_label)

with col3:
    if 'politeness_score_sum' in nlp_df.columns:
        avg_polite = nlp_df['politeness_score_sum'].mean()
        st.metric(e("🙏 ") + get_text('avg_politeness'), f"{avg_polite:.1f}")
    else:
        st.metric(e("🙏 ") + get_text('avg_politeness'), "N/A")

with col4:
    if 'word_count_sum' in nlp_df.columns:
        avg_words = nlp_df['word_count_sum'].mean()
        st.metric(e("📖 ") + get_text('avg_words'), f"{avg_words:.0f}")
    else:
        st.metric(e("📖 ") + get_text('avg_words'), "N/A")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    section_header(e("📊 ") + get_text('sentiment_distribution'), 'sentiment')
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=nlp_df['sentiment_compound_mean'],
        nbinsx=30,
        marker_color='steelblue'
    ))
    fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text=get_text('neutral'))
    fig.update_layout(
        xaxis_title=get_text('sentiment_score'),
        yaxis_title=get_text('issues_count'),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation
    complaints_label = "Complaints" if st.session_state.get('language') == 'en' else "Beschwerden"
    factual_label = "Factual" if st.session_state.get('language') == 'en' else "Sachlich"
    friendly_label = "Friendly" if st.session_state.get('language') == 'en' else "Freundlich"
    
    st.markdown(f"""
    - **< -0.1**: {get_text('negative')} ({complaints_label})
    - **-0.1 to 0.1**: {get_text('neutral')} ({factual_label})
    - **> 0.1**: {get_text('positive')} ({friendly_label}, {get_text('solution_oriented')})
    """)

with col2:
    section_header(e("📈 ") + get_text('communication_patterns'), 'patterns')
    
    # Aggregated patterns
    patterns = {
        get_text('politeness'): nlp_df['politeness_score_sum'].mean() if 'politeness_score_sum' in nlp_df.columns else 0,
        get_text('urgency'): nlp_df['urgency_score_sum'].mean() if 'urgency_score_sum' in nlp_df.columns else 0,
        get_text('technical'): nlp_df['technical_score_sum'].mean() if 'technical_score_sum' in nlp_df.columns else 0,
        get_text('solution_oriented'): nlp_df['solution_score_sum'].mean() if 'solution_score_sum' in nlp_df.columns else 0,
    }
    
    fig = go.Figure(data=[go.Bar(
        x=list(patterns.keys()),
        y=list(patterns.values()),
        marker_color=['green', 'orange', 'blue', 'purple']
    )])
    fig.update_layout(
        xaxis_title=get_text('pattern'),
        yaxis_title=get_text('avg_score_per_issue'),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Correlation Sentiment vs Performance
section_header(e("🔗 ") + get_text('sentiment_vs_performance'))

if scored_df is not None and 'id' in scored_df.columns:
    # Merge NLP with Scores
    merged = nlp_df.merge(
        scored_df[['id', 'Q1', 'Q2', 'Q3', 'assignee']].rename(columns={'id': 'issueid'}),
        on='issueid',
        how='inner'
    )
    
    if len(merged) > 0:
        import numpy as np
        from scipy import stats
        
        valid_data = merged[merged['Q1'] > 0].copy()
        
        # KDE line chart
        fig = go.Figure()
        
        colors = {1: '#d73027', 2: '#fc8d59', 3: '#fee08b', 4: '#91cf60', 5: '#1a9850'}
        
        # X-axis for KDE
        x_range = np.linspace(-1, 1, 200)
        
        for score in sorted(valid_data['Q1'].unique()):
            score_data = valid_data[valid_data['Q1'] == score]['sentiment_compound_mean'].dropna()
            if len(score_data) > 2:
                # Calculate KDE
                kde = stats.gaussian_kde(score_data)
                y_kde = kde(x_range)
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_kde,
                    mode='lines',
                    name=f'Score {score}',
                    line=dict(color=colors.get(score, '#888'), width=2.5)
                ))
        
        fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text=get_text('neutral'))
        fig.update_layout(
            title=get_text('sentiment_density'),
            xaxis_title=get_text('sentiment') + " (-1 to +1)",
            yaxis_title=get_text('density'),
            height=450,
            legend_title="Q1 Score"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(get_text('no_overlap'))
else:
    st.info(get_text('scored_not_available'))

st.markdown("---")

# Top/Bottom Issues
section_header(e("📋 ") + get_text('extreme_cases'))

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**{e('🔝')} {get_text('most_positive')}:**")
    top_positive = nlp_df.nlargest(5, 'sentiment_compound_mean')[['issueid', 'sentiment_compound_mean']]
    top_positive.columns = ['Issue ID', get_text('sentiment')]
    st.dataframe(top_positive, use_container_width=True)

with col2:
    st.markdown(f"**{e('🔻')} {get_text('most_negative')}:**")
    top_negative = nlp_df.nsmallest(5, 'sentiment_compound_mean')[['issueid', 'sentiment_compound_mean']]
    top_negative.columns = ['Issue ID', get_text('sentiment')]
    st.dataframe(top_negative, use_container_width=True)

# Footer
render_footer()
