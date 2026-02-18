"""
Score Comparison Dashboard - Q-Score vs O-Score
Parallel comparison: Manager Rating vs Objective Metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Project path (pages -> streamlit_app -> project)
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.settings import (
    render_settings_sidebar, init_session_state, get_text, e, 
    page_header, section_header, render_footer
)

st.set_page_config(page_title="Score Comparison", page_icon="🔬", layout="wide")

# Initialize and render sidebar
init_session_state()
render_settings_sidebar()

# Paths - from pages: parent = streamlit_app, parent.parent = project root
DATA_DIR = Path(__file__).parent.parent.parent / "data"


@st.cache_data
def load_comparison_data():
    """Load comparison data."""
    data = {}
    
    # O-Score Results
    o_score_path = DATA_DIR / "processed" / "o_score_results.csv"
    if o_score_path.exists():
        data['o_scores'] = pd.read_csv(o_score_path)
    
    # Comparison Q vs O
    comparison_path = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    if comparison_path.exists():
        data['comparison'] = pd.read_csv(comparison_path)
        # Rename for consistency
        if 'q_score_avg' in data['comparison'].columns:
            data['comparison']['q_score'] = data['comparison']['q_score_avg']
        # Calculate bias
        data['comparison']['score_diff'] = data['comparison']['o_score'] - data['comparison']['q_score']
        data['comparison']['bias_type'] = data['comparison']['score_diff'].apply(
            lambda x: get_text('overrated').upper() if x < -1 else (get_text('underrated').upper() if x > 1 else 'OK')
        )
    
    # Q-Scores Original
    scored_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
    if scored_path.exists():
        data['scored'] = pd.read_excel(scored_path)
    
    return data


def main():
    # Page header
    page_header(
        e("🔬 ") + get_text('score_comparison'),
        get_text('score_comparison_subtitle'),
        help_key='bias'
    )
    
    # Load data
    data = load_comparison_data()
    
    if 'comparison' not in data or 'o_scores' not in data:
        st.error(get_text('comparison_data_not_found'))
        st.code(get_text('run_o_score'))
        return
    
    comparison = data['comparison']
    o_scores = data['o_scores']
    
    st.markdown("---")
    
    # === KPI CARDS ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            get_text('q_score_manager'),
            f"{comparison['q_score'].mean():.2f}",
            delta=get_text('subjective'),
            delta_color="off"
        )
    
    with col2:
        st.metric(
            get_text('o_score_objective'),
            f"{comparison['o_score'].mean():.2f}",
            delta=f"{comparison['score_diff'].mean():.2f} {get_text('difference')}"
        )
    
    with col3:
        corr = comparison['o_score'].corr(comparison['q_score'])
        st.metric(
            get_text('correlation'),
            f"{corr:.2f}",
            delta=get_text('moderate') if corr > 0.5 else get_text('weak')
        )
    
    with col4:
        overrated = (comparison['bias_type'] == get_text('overrated').upper()).sum()
        st.metric(
            get_text('overrated'),
            f"{overrated} / {len(comparison)}",
            delta=f"{overrated/len(comparison)*100:.0f}%",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # === TABS ===
    tab1, tab2, tab3, tab4 = st.tabs([
        e("📊 ") + get_text('overview'), 
        e("👥 ") + get_text('details'), 
        e("🔍 ") + get_text('bias_analysis'),
        e("📈 ") + get_text('o_score_components')
    ])
    
    # === TAB 1: COMPARISON ===
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            section_header(e("📊 ") + get_text('q_vs_o_score'))
            
            fig = go.Figure()
            
            # Scatter with colors by bias
            colors = comparison['bias_type'].map({
                get_text('overrated').upper(): 'red',
                get_text('underrated').upper(): 'green',
                'OK': 'blue'
            })
            
            fig.add_trace(go.Scatter(
                x=comparison['q_score'],
                y=comparison['o_score'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=colors,
                    opacity=0.7
                ),
                text=comparison['employee'],
                hovertemplate='<b>%{text}</b><br>Q-Score: %{x:.2f}<br>O-Score: %{y:.2f}<extra></extra>'
            ))
            
            # Perfect correlation line
            fig.add_trace(go.Scatter(
                x=[1, 5], y=[1, 5],
                mode='lines',
                line=dict(color='gray', dash='dash'),
                name=get_text('perfect_correlation')
            ))
            
            fig.update_layout(
                xaxis_title=get_text('q_score_manager'),
                yaxis_title=get_text('o_score_objective'),
                xaxis=dict(range=[0.5, 5.5]),
                yaxis=dict(range=[0.5, 5.5]),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            legend_overrated = get_text('overrated')
            legend_underrated = get_text('underrated')
            st.caption(f"""
            🔴 {get_text('critical')} = {legend_overrated} (Q > O+1) | 
            🟢 {get_text('success')} = {legend_underrated} (O > Q+1) | 
            🔵 OK
            """)
        
        with col2:
            section_header(e("📈 ") + get_text('score_distributions'))
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=comparison['q_score'],
                name=get_text('q_score_manager'),
                opacity=0.6,
                marker_color='#ff6b6b'
            ))
            
            fig.add_trace(go.Histogram(
                x=comparison['o_score'],
                name=get_text('o_score_objective'),
                opacity=0.6,
                marker_color='#4ecdc4'
            ))
            
            fig.update_layout(
                barmode='overlay',
                xaxis_title="Score",
                yaxis_title=get_text('count'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics table
            stats_df = pd.DataFrame({
                get_text('metric'): [get_text('mean'), get_text('median'), get_text('std_dev'), get_text('min'), get_text('max')],
                'Q-Score': [
                    f"{comparison['q_score'].mean():.2f}",
                    f"{comparison['q_score'].median():.2f}",
                    f"{comparison['q_score'].std():.2f}",
                    f"{comparison['q_score'].min():.1f}",
                    f"{comparison['q_score'].max():.1f}"
                ],
                'O-Score': [
                    f"{comparison['o_score'].mean():.2f}",
                    f"{comparison['o_score'].median():.2f}",
                    f"{comparison['o_score'].std():.2f}",
                    f"{comparison['o_score'].min():.1f}",
                    f"{comparison['o_score'].max():.1f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # === TAB 2: EMPLOYEE DETAILS ===
    with tab2:
        section_header(e("🔍 ") + get_text('employee_search'))
        
        # Search field
        search = st.text_input(get_text('search_employee') + ":", "")
        
        if search:
            matches = comparison[comparison['employee'].str.contains(search, case=False)]
            if len(matches) > 0:
                for _, row in matches.iterrows():
                    with st.expander(f"📋 {row['employee']}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Q-Score", f"{row['q_score']:.2f}")
                        with col2:
                            st.metric("O-Score", f"{row['o_score']:.2f}")
                        with col3:
                            diff = row['score_diff']
                            st.metric(get_text('difference'), f"{diff:+.2f}", 
                                     delta=row['bias_type'])
            else:
                st.warning(get_text('no_employee_found'))
        
        st.markdown("---")
        
        # Ranking table
        section_header(e("📋 ") + get_text('complete_ranking'))
        
        sort_options = {
            get_text('o_score_high'): ('O-Score', False),
            get_text('o_score_low'): ('O-Score', True),
            get_text('q_score_high'): ('Q-Score', False),
            get_text('difference_large'): (get_text('difference'), True)
        }
        
        sort_by = st.selectbox(get_text('sort_by') + ":", list(sort_options.keys()))
        
        display_df = comparison[['employee', 'q_score', 'o_score', 'score_diff', 'bias_type', 'ticket_count']].copy()
        display_df.columns = [get_text('employees'), 'Q-Score', 'O-Score', get_text('difference'), get_text('bias'), get_text('tickets')]
        
        sort_col, ascending = sort_options[sort_by]
        if sort_col == get_text('difference'):
            display_df = display_df.sort_values(get_text('difference'), key=abs, ascending=ascending)
        else:
            display_df = display_df.sort_values(sort_col, ascending=ascending)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    # === TAB 3: BIAS ANALYSIS ===
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            section_header(e("📊 ") + get_text('bias_distribution'))
            
            bias_counts = comparison['bias_type'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=bias_counts.index,
                values=bias_counts.values,
                marker_colors=['#4ecdc4', '#ff6b6b', '#45b7d1'],
                hole=0.4
            )])
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            overrated_count = bias_counts.get(get_text('overrated').upper(), 0)
            underrated_count = bias_counts.get(get_text('underrated').upper(), 0)
            ok_count = bias_counts.get('OK', 0)
            
            interpretation_text = f"""
            **{get_text('interpretation')}:**
            - {overrated_count} {get_text('employees')} {get_text('overrated').lower()}
            - {underrated_count} {get_text('employees')} {get_text('underrated').lower()}
            - {ok_count} {get_text('employees')} {get_text('all_ok').lower()} (+/- 1 {get_text('steps')})
            """
            st.info(interpretation_text)
        
        with col2:
            section_header(e("⚠️ ") + get_text('top_10_overrated'))
            
            overrated_df = comparison[comparison['bias_type'] == get_text('overrated').upper()].nsmallest(10, 'score_diff')
            
            if len(overrated_df) > 0:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    y=overrated_df['employee'],
                    x=overrated_df['q_score'],
                    name='Q-Score',
                    orientation='h',
                    marker_color='#ff6b6b'
                ))
                
                fig.add_trace(go.Bar(
                    y=overrated_df['employee'],
                    x=overrated_df['o_score'],
                    name='O-Score',
                    orientation='h',
                    marker_color='#4ecdc4'
                ))
                
                fig.update_layout(
                    barmode='group',
                    xaxis_title="Score",
                    yaxis=dict(autorange="reversed"),
                    height=400,
                    legend=dict(orientation='h', yanchor='bottom', y=1.02)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        section_header(e("📈 ") + get_text('score_diff_histogram'))
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=comparison['score_diff'],
            nbinsx=20,
            marker_color='purple',
            opacity=0.7
        ))
        
        fig.add_vline(x=0, line_dash="dash", line_color="red", 
                      annotation_text=get_text('no_difference'))
        fig.add_vline(x=comparison['score_diff'].mean(), line_dash="solid", 
                      line_color="orange",
                      annotation_text=f"{get_text('mean')}: {comparison['score_diff'].mean():.2f}")
        
        fig.update_layout(
            xaxis_title=f"O-Score - Q-Score ({get_text('negative').lower()} = {get_text('overrated').lower()})",
            yaxis_title=get_text('count'),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # === TAB 4: O-SCORE COMPONENTS ===
    with tab4:
        section_header(e("📊 ") + get_text('o_score_composition'))
        
        component_table = f"""
        | {get_text('o_score_components')} | {get_text('weight')} | {get_text('description')} |
        |------------|---------|--------------|
        | **{get_text('quality')}** | 35% | {get_text('reopen_rate_success')} |
        | **{get_text('efficiency')}** | 25% | {get_text('processing_time')} |
        | **{get_text('productivity')}** | 20% | {get_text('ticket_volume_steps')} |
        | **{get_text('communication')}** | 20% | {get_text('first_touch_comments')} |
        """
        st.markdown(component_table)
        
        col1, col2 = st.columns(2)
        
        with col1:
            section_header(e("📊 ") + get_text('component_averages'))
            
            components = ['quality_score', 'efficiency_score', 
                         'productivity_score', 'communication_score']
            comp_means = o_scores[components].mean()
            
            labels = [
                f"{get_text('quality')}\n(35%)", 
                f"{get_text('efficiency')}\n(25%)", 
                f"{get_text('productivity')}\n(20%)", 
                f"{get_text('communication')}\n(20%)"
            ]
            
            fig = go.Figure(data=[go.Bar(
                x=labels,
                y=comp_means,
                marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'],
                text=[f'{v:.2f}' for v in comp_means],
                textposition='outside'
            )])
            
            fig.update_layout(
                yaxis_title=f"{get_text('average')} Score (0-1)",
                yaxis=dict(range=[0, 1]),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            section_header(e("🔗 ") + get_text('component_correlation'))
            
            corr_matrix = o_scores[components + ['o_score']].corr()
            
            labels_short = [get_text('quality'), get_text('efficiency'), 
                          get_text('productivity'), get_text('communication'), 'O-Score']
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=labels_short,
                y=labels_short,
                colorscale='RdYlGn',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate='%{text}',
                textfont={"size": 12}
            ))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        section_header(e("📈 ") + get_text('o_score_distribution'))
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=o_scores['o_score'],
            nbinsx=20,
            marker_color='#4ecdc4',
            opacity=0.8
        ))
        
        fig.add_vline(x=o_scores['o_score'].mean(), line_dash="dash", 
                      line_color="red",
                      annotation_text=f"{get_text('mean')}: {o_scores['o_score'].mean():.2f}")
        
        fig.update_layout(
            xaxis_title="O-Score",
            yaxis_title=get_text('count'),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"**{len(o_scores)} {get_text('employees_with_oscore')}**")
    
    # === FOOTER ===
    st.markdown("---")
    st.caption(get_text('score_legend'))
    
    render_footer()


if __name__ == "__main__":
    main()
