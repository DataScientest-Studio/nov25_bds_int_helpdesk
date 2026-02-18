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
    section_header, render_footer
)

st.set_page_config(page_title="Score Comparison", page_icon="🔬", layout="wide")

# Initialize and render sidebar
init_session_state()
render_settings_sidebar()

# Paths - from pages: parent = streamlit_app, parent.parent = project root
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def t(de_text, en_text):
    """Simple translation helper."""
    return en_text if st.session_state.get('language') == 'en' else de_text


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
        
        overrated_label = t('ÜBERBEWERTET', 'OVERRATED')
        underrated_label = t('UNTERBEWERTET', 'UNDERRATED')
        data['comparison']['bias_type'] = data['comparison']['score_diff'].apply(
            lambda x: overrated_label if x < -1 else (underrated_label if x > 1 else 'OK')
        )
    
    # Q-Scores Original
    scored_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
    if scored_path.exists():
        data['scored'] = pd.read_excel(scored_path)
    
    return data


def main():
    # Page header (simple title without subtitle)
    title = t("Score-Vergleich", "Score Comparison")
    st.title(e("🔬 ") + title)
    st.markdown("---")
    
    # Load data
    data = load_comparison_data()
    
    if 'comparison' not in data or 'o_scores' not in data:
        error_msg = t(
            "Vergleichsdaten nicht gefunden. Bitte zuerst O-Score berechnen.",
            "Comparison data not found. Please calculate O-Score first."
        )
        st.error(error_msg)
        st.code("python src/o_score.py")
        return
    
    comparison = data['comparison']
    o_scores = data['o_scores']
    
    # === KPI CARDS ===
    col1, col2, col3, col4 = st.columns(4)
    
    subjective_label = t("Subjektiv", "Subjective")
    difference_label = t("Differenz", "Difference")
    correlation_label = t("Korrelation", "Correlation")
    moderate_label = t("Moderat", "Moderate")
    weak_label = t("Schwach", "Weak")
    overrated_label = t("Überbewertet", "Overrated")
    
    with col1:
        st.metric(
            "Q-Score (Manager)",
            f"{comparison['q_score'].mean():.2f}",
            delta=subjective_label,
            delta_color="off"
        )
    
    with col2:
        objective_label = t("O-Score (Objektiv)", "O-Score (Objective)")
        st.metric(
            objective_label,
            f"{comparison['o_score'].mean():.2f}",
            delta=f"{comparison['score_diff'].mean():.2f} {difference_label}"
        )
    
    with col3:
        corr = comparison['o_score'].corr(comparison['q_score'])
        st.metric(
            correlation_label,
            f"{corr:.2f}",
            delta=moderate_label if corr > 0.5 else weak_label
        )
    
    with col4:
        overrated_key = t('ÜBERBEWERTET', 'OVERRATED')
        overrated_count = (comparison['bias_type'] == overrated_key).sum()
        st.metric(
            overrated_label,
            f"{overrated_count} / {len(comparison)}",
            delta=f"{overrated_count/len(comparison)*100:.0f}%",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # === TABS ===
    overview_label = t("Vergleich", "Comparison")
    details_label = t("Mitarbeiter-Detail", "Employee Details")
    bias_label = t("Bias-Analyse", "Bias Analysis")
    components_label = t("O-Score Komponenten", "O-Score Components")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        e("📊 ") + overview_label, 
        e("👥 ") + details_label, 
        e("🔍 ") + bias_label,
        e("📈 ") + components_label
    ])
    
    # === TAB 1: COMPARISON ===
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            chart_title = t("Q-Score vs O-Score", "Q-Score vs O-Score")
            section_header(e("📊 ") + chart_title)
            
            fig = go.Figure()
            
            # Scatter with colors by bias
            overrated_key = t('ÜBERBEWERTET', 'OVERRATED')
            underrated_key = t('UNTERBEWERTET', 'UNDERRATED')
            
            colors = comparison['bias_type'].map({
                overrated_key: 'red',
                underrated_key: 'green',
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
            perfect_label = t("Perfekte Korrelation", "Perfect Correlation")
            fig.add_trace(go.Scatter(
                x=[1, 5], y=[1, 5],
                mode='lines',
                line=dict(color='gray', dash='dash'),
                name=perfect_label
            ))
            
            fig.update_layout(
                xaxis_title="Q-Score (Manager)",
                yaxis_title=t("O-Score (Objektiv)", "O-Score (Objective)"),
                xaxis=dict(range=[0.5, 5.5]),
                yaxis=dict(range=[0.5, 5.5]),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, width="stretch")
            
            legend_text = t(
                "🔴 = Überbewertet (Q > O+1) | 🟢 = Unterbewertet (O > Q+1) | 🔵 = OK",
                "🔴 = Overrated (Q > O+1) | 🟢 = Underrated (O > Q+1) | 🔵 = OK"
            )
            st.caption(legend_text)
        
        with col2:
            dist_title = t("Score-Verteilungen", "Score Distributions")
            section_header(e("📈 ") + dist_title)
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=comparison['q_score'],
                name='Q-Score (Manager)',
                opacity=0.6,
                marker_color='#ff6b6b'
            ))
            
            fig.add_trace(go.Histogram(
                x=comparison['o_score'],
                name=t('O-Score (Objektiv)', 'O-Score (Objective)'),
                opacity=0.6,
                marker_color='#4ecdc4'
            ))
            
            fig.update_layout(
                barmode='overlay',
                xaxis_title="Score",
                yaxis_title=get_text('count'),
                height=400
            )
            
            st.plotly_chart(fig, width="stretch")
            
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
            st.dataframe(stats_df, width="stretch", hide_index=True)
    
    # === TAB 2: EMPLOYEE DETAILS ===
    with tab2:
        search_title = t("Mitarbeiter-Suche", "Employee Search")
        section_header(e("🔍 ") + search_title)
        
        # Search field
        search_label = t("Mitarbeiter-ID suchen", "Search Employee ID")
        search = st.text_input(search_label + ":", "")
        
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
                            st.metric(difference_label, f"{diff:+.2f}", 
                                     delta=row['bias_type'])
            else:
                not_found = t("Kein Mitarbeiter gefunden", "No employee found")
                st.warning(not_found)
        
        st.markdown("---")
        
        # Ranking table
        ranking_title = t("Vollständiges Ranking", "Complete Ranking")
        section_header(e("📋 ") + ranking_title)
        
        sort_label = t("Sortieren nach", "Sort by")
        sort_options = [
            t('O-Score (hoch)', 'O-Score (high)'),
            t('O-Score (niedrig)', 'O-Score (low)'),
            t('Q-Score (hoch)', 'Q-Score (high)'),
            t('Differenz (groß)', 'Difference (large)')
        ]
        
        sort_by = st.selectbox(sort_label + ":", sort_options)
        
        employees_label = t("Mitarbeiter", "Employee")
        bias_col_label = "Bias"
        tickets_label = get_text('tickets')
        
        display_df = comparison[['employee', 'q_score', 'o_score', 'score_diff', 'bias_type', 'ticket_count']].copy()
        display_df.columns = [employees_label, 'Q-Score', 'O-Score', difference_label, bias_col_label, tickets_label]
        
        if sort_by == sort_options[0]:  # O-Score high
            display_df = display_df.sort_values('O-Score', ascending=False)
        elif sort_by == sort_options[1]:  # O-Score low
            display_df = display_df.sort_values('O-Score', ascending=True)
        elif sort_by == sort_options[2]:  # Q-Score high
            display_df = display_df.sort_values('Q-Score', ascending=False)
        else:  # Difference large
            display_df = display_df.sort_values(difference_label, key=abs, ascending=False)
        
        st.dataframe(display_df, width="stretch", hide_index=True, height=400)
    
    # === TAB 3: BIAS ANALYSIS ===
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            bias_dist_title = t("Bias-Verteilung", "Bias Distribution")
            section_header(e("📊 ") + bias_dist_title)
            
            bias_counts = comparison['bias_type'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=bias_counts.index,
                values=bias_counts.values,
                marker_colors=['#4ecdc4', '#ff6b6b', '#45b7d1'],
                hole=0.4
            )])
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
            
            overrated_key = t('ÜBERBEWERTET', 'OVERRATED')
            underrated_key = t('UNTERBEWERTET', 'UNDERRATED')
            
            overrated_count = bias_counts.get(overrated_key, 0)
            underrated_count = bias_counts.get(underrated_key, 0)
            ok_count = bias_counts.get('OK', 0)
            
            employees_word = t("Mitarbeiter", "employees")
            overrated_word = t("überbewertet", "overrated")
            underrated_word = t("unterbewertet", "underrated")
            fair_word = t("fair bewertet", "fairly rated")
            
            interpretation_text = f"""
            **{get_text('interpretation')}:**
            - {overrated_count} {employees_word} {overrated_word}
            - {underrated_count} {employees_word} {underrated_word}
            - {ok_count} {employees_word} {fair_word} (±1)
            """
            st.info(interpretation_text)
        
        with col2:
            top10_title = t("Top 10 Überbewertete", "Top 10 Overrated")
            section_header(e("⚠️ ") + top10_title)
            
            overrated_key = t('ÜBERBEWERTET', 'OVERRATED')
            overrated_df = comparison[comparison['bias_type'] == overrated_key].nsmallest(10, 'score_diff')
            
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
                
                st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        histogram_title = t("Score-Differenz Histogramm", "Score Difference Histogram")
        section_header(e("📈 ") + histogram_title)
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=comparison['score_diff'],
            nbinsx=20,
            marker_color='purple',
            opacity=0.7
        ))
        
        no_diff_label = t("Keine Differenz", "No Difference")
        fig.add_vline(x=0, line_dash="dash", line_color="red", 
                      annotation_text=no_diff_label)
        fig.add_vline(x=comparison['score_diff'].mean(), line_dash="solid", 
                      line_color="orange",
                      annotation_text=f"{get_text('mean')}: {comparison['score_diff'].mean():.2f}")
        
        negative_means = t("negativ = überbewertet", "negative = overrated")
        fig.update_layout(
            xaxis_title=f"O-Score - Q-Score ({negative_means})",
            yaxis_title=get_text('count'),
            height=300
        )
        
        st.plotly_chart(fig, width="stretch")
    
    # === TAB 4: O-SCORE COMPONENTS ===
    with tab4:
        composition_title = t("O-Score Zusammensetzung", "O-Score Composition")
        section_header(e("📊 ") + composition_title)
        
        quality_label = t("Qualität", "Quality")
        efficiency_label = t("Effizienz", "Efficiency")
        productivity_label = t("Produktivität", "Productivity")
        communication_label = t("Kommunikation", "Communication")
        weight_label = t("Gewicht", "Weight")
        description_label = t("Beschreibung", "Description")
        
        quality_desc = t("Reopen-Rate (niedrig = gut), Success-Rate", "Reopen rate (low = good), success rate")
        efficiency_desc = t("Bearbeitungszeit (schnell = gut)", "Processing time (fast = good)")
        productivity_desc = t("Ticket-Volumen, Processing Steps", "Ticket volume, processing steps")
        communication_desc = t("First-Touch-Rate, Kommentar-Aktivität", "First-touch rate, comment activity")
        
        component_table = f"""
        | {t('Komponente', 'Component')} | {weight_label} | {description_label} |
        |------------|---------|--------------|
        | **{quality_label}** | 35% | {quality_desc} |
        | **{efficiency_label}** | 25% | {efficiency_desc} |
        | **{productivity_label}** | 20% | {productivity_desc} |
        | **{communication_label}** | 20% | {communication_desc} |
        """
        st.markdown(component_table)
        
        col1, col2 = st.columns(2)
        
        with col1:
            averages_title = t("Komponenten-Durchschnitte", "Component Averages")
            section_header(e("📊 ") + averages_title)
            
            components = ['quality_score', 'efficiency_score', 
                         'productivity_score', 'communication_score']
            comp_means = o_scores[components].mean()
            
            labels = [
                f"{quality_label}\n(35%)", 
                f"{efficiency_label}\n(25%)", 
                f"{productivity_label}\n(20%)", 
                f"{communication_label}\n(20%)"
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
            
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            corr_title = t("Komponenten-Korrelation", "Component Correlation")
            section_header(e("🔗 ") + corr_title)
            
            corr_matrix = o_scores[components + ['o_score']].corr()
            
            labels_short = [quality_label, efficiency_label, 
                          productivity_label, communication_label, 'O-Score']
            
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
            st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        dist_title = t("O-Score Verteilung (alle Mitarbeiter)", "O-Score Distribution (all employees)")
        section_header(e("📈 ") + dist_title)
        
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
        
        st.plotly_chart(fig, width="stretch")
        
        employees_oscore = t("Mitarbeiter mit O-Score bewertet (min. 10 Tickets)", "employees with O-Score (min. 10 tickets)")
        st.success(f"**{len(o_scores)} {employees_oscore}**")
    
    # === FOOTER ===
    st.markdown("---")
    
    legend_text = t(
        "**Legende:** Q-Score = Subjektive Manager-Bewertung (Q1, Q2, Q3 gemittelt). O-Score = Objektive Bewertung basierend auf messbaren Metriken. Bias = Differenz > 1 Punkt gilt als signifikante Über-/Unterbewertung.",
        "**Legend:** Q-Score = Subjective manager rating (Q1, Q2, Q3 averaged). O-Score = Objective rating based on measurable metrics. Bias = Difference > 1 point is considered significant over-/underrating."
    )
    st.caption(legend_text)
    
    render_footer()


if __name__ == "__main__":
    main()
