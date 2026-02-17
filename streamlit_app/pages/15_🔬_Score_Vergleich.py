"""
Score-Vergleich Dashboard - Q-Score vs O-Score
Paralleler Vergleich: Manager-Bewertung vs Objektive Metriken
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Projekt-Pfad (pages -> streamlit_app -> project)
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.settings import (
    render_settings_sidebar, init_session_state, get_text, e
)

st.set_page_config(page_title="Score-Vergleich", page_icon="🔬", layout="wide")

# Initialize and render sidebar
init_session_state()
render_settings_sidebar()

# Pfade - von pages aus: parent = streamlit_app, parent.parent = project root
DATA_DIR = Path(__file__).parent.parent.parent / "data"


@st.cache_data
def load_comparison_data():
    """Laedt Vergleichsdaten."""
    data = {}
    
    # O-Score Ergebnisse
    o_score_path = DATA_DIR / "processed" / "o_score_results.csv"
    if o_score_path.exists():
        data['o_scores'] = pd.read_csv(o_score_path)
    
    # Vergleich Q vs O
    comparison_path = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    if comparison_path.exists():
        data['comparison'] = pd.read_csv(comparison_path)
        # Rename fuer Konsistenz
        if 'q_score_avg' in data['comparison'].columns:
            data['comparison']['q_score'] = data['comparison']['q_score_avg']
        # Bias berechnen
        data['comparison']['score_diff'] = data['comparison']['o_score'] - data['comparison']['q_score']
        data['comparison']['bias_type'] = data['comparison']['score_diff'].apply(
            lambda x: 'UEBERBEWERTET' if x < -1 else ('UNTERBEWERTET' if x > 1 else 'OK')
        )
    
    # Q-Scores Original
    scored_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
    if scored_path.exists():
        data['scored'] = pd.read_excel(scored_path)
    
    return data


def main():
    st.title("🔬 Score-Vergleich: Q-Score vs O-Score")
    st.markdown("**Paralleler Vergleich: Manager-Bewertung (subjektiv) vs Objektive Metriken**")
    
    # Daten laden
    data = load_comparison_data()
    
    if 'comparison' not in data or 'o_scores' not in data:
        st.error("Vergleichsdaten nicht gefunden. Bitte zuerst O-Score berechnen.")
        st.code("python src/o_score.py")
        return
    
    comparison = data['comparison']
    o_scores = data['o_scores']
    
    st.markdown("---")
    
    # === KPI CARDS ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Q-Score (Manager)",
            f"{comparison['q_score'].mean():.2f}",
            delta="Subjektiv",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "O-Score (Objektiv)",
            f"{comparison['o_score'].mean():.2f}",
            delta=f"{comparison['score_diff'].mean():.2f} Differenz"
        )
    
    with col3:
        corr = comparison['o_score'].corr(comparison['q_score'])
        st.metric(
            "Korrelation",
            f"{corr:.2f}",
            delta="Moderat" if corr > 0.5 else "Schwach"
        )
    
    with col4:
        overrated = (comparison['bias_type'] == 'UEBERBEWERTET').sum()
        st.metric(
            "Ueberbewertet",
            f"{overrated} / {len(comparison)}",
            delta=f"{overrated/len(comparison)*100:.0f}%",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # === TABS ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Vergleich", 
        "👥 Mitarbeiter-Detail", 
        "🔍 Bias-Analyse",
        "📈 O-Score Komponenten"
    ])
    
    # === TAB 1: VERGLEICH ===
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Q-Score vs O-Score")
            
            fig = go.Figure()
            
            # Scatter mit Farben nach Bias
            colors = comparison['bias_type'].map({
                'UEBERBEWERTET': 'red',
                'UNTERBEWERTET': 'green',
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
            
            # Perfekte Korrelation Linie
            fig.add_trace(go.Scatter(
                x=[1, 5], y=[1, 5],
                mode='lines',
                line=dict(color='gray', dash='dash'),
                name='Perfekte Korrelation'
            ))
            
            fig.update_layout(
                xaxis_title="Q-Score (Manager)",
                yaxis_title="O-Score (Objektiv)",
                xaxis=dict(range=[0.5, 5.5]),
                yaxis=dict(range=[0.5, 5.5]),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("""
            🔴 Rot = Ueberbewertet (Q > O+1) | 
            🟢 Gruen = Unterbewertet (O > Q+1) | 
            🔵 Blau = OK
            """)
        
        with col2:
            st.subheader("Score-Verteilungen")
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=comparison['q_score'],
                name='Q-Score (Manager)',
                opacity=0.6,
                marker_color='#ff6b6b'
            ))
            
            fig.add_trace(go.Histogram(
                x=comparison['o_score'],
                name='O-Score (Objektiv)',
                opacity=0.6,
                marker_color='#4ecdc4'
            ))
            
            fig.update_layout(
                barmode='overlay',
                xaxis_title="Score",
                yaxis_title="Anzahl",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistik-Tabelle
            stats_df = pd.DataFrame({
                'Metrik': ['Mean', 'Median', 'Std', 'Min', 'Max'],
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
    
    # === TAB 2: MITARBEITER-DETAIL ===
    with tab2:
        st.subheader("Mitarbeiter-Suche")
        
        # Suchfeld
        search = st.text_input("Mitarbeiter-ID suchen:", "")
        
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
                            st.metric("Differenz", f"{diff:+.2f}", 
                                     delta=row['bias_type'])
            else:
                st.warning("Kein Mitarbeiter gefunden.")
        
        st.markdown("---")
        
        # Ranking-Tabelle
        st.subheader("Vollstaendiges Ranking")
        
        sort_by = st.selectbox("Sortieren nach:", 
                               ['O-Score (hoch)', 'O-Score (niedrig)', 
                                'Q-Score (hoch)', 'Differenz (gross)'])
        
        display_df = comparison[['employee', 'q_score', 'o_score', 'score_diff', 'bias_type', 'ticket_count']].copy()
        display_df.columns = ['Mitarbeiter', 'Q-Score', 'O-Score', 'Differenz', 'Bias', 'Tickets']
        
        if sort_by == 'O-Score (hoch)':
            display_df = display_df.sort_values('O-Score', ascending=False)
        elif sort_by == 'O-Score (niedrig)':
            display_df = display_df.sort_values('O-Score', ascending=True)
        elif sort_by == 'Q-Score (hoch)':
            display_df = display_df.sort_values('Q-Score', ascending=False)
        else:
            display_df = display_df.sort_values('Differenz', key=abs, ascending=False)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    # === TAB 3: BIAS-ANALYSE ===
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Bias-Verteilung")
            
            bias_counts = comparison['bias_type'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=bias_counts.index,
                values=bias_counts.values,
                marker_colors=['#4ecdc4', '#ff6b6b', '#45b7d1'],
                hole=0.4
            )])
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            **Interpretation:**
            - {bias_counts.get('UEBERBEWERTET', 0)} Mitarbeiter wurden vom Manager zu gut bewertet
            - {bias_counts.get('UNTERBEWERTET', 0)} Mitarbeiter wurden vom Manager zu schlecht bewertet
            - {bias_counts.get('OK', 0)} Mitarbeiter wurden fair bewertet (+/- 1 Punkt)
            """)
        
        with col2:
            st.subheader("Top 10 Ueberbewertete")
            
            overrated = comparison[comparison['bias_type'] == 'UEBERBEWERTET'].nsmallest(10, 'score_diff')
            
            if len(overrated) > 0:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    y=overrated['employee'],
                    x=overrated['q_score'],
                    name='Q-Score',
                    orientation='h',
                    marker_color='#ff6b6b'
                ))
                
                fig.add_trace(go.Bar(
                    y=overrated['employee'],
                    x=overrated['o_score'],
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
        st.subheader("Score-Differenz Histogramm")
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=comparison['score_diff'],
            nbinsx=20,
            marker_color='purple',
            opacity=0.7
        ))
        
        fig.add_vline(x=0, line_dash="dash", line_color="red", 
                      annotation_text="Keine Differenz")
        fig.add_vline(x=comparison['score_diff'].mean(), line_dash="solid", 
                      line_color="orange",
                      annotation_text=f"Mean: {comparison['score_diff'].mean():.2f}")
        
        fig.update_layout(
            xaxis_title="O-Score minus Q-Score (negativ = ueberbewertet)",
            yaxis_title="Anzahl",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # === TAB 4: O-SCORE KOMPONENTEN ===
    with tab4:
        st.subheader("O-Score Zusammensetzung")
        
        st.markdown("""
        Der **O-Score** basiert auf 4 objektiven Komponenten:
        
        | Komponente | Gewicht | Beschreibung |
        |------------|---------|--------------|
        | **Qualitaet** | 35% | Reopen-Rate (niedrig = gut), Success-Rate |
        | **Effizienz** | 25% | Bearbeitungszeit (schnell = gut) |
        | **Produktivitaet** | 20% | Ticket-Volumen, Processing Steps |
        | **Kommunikation** | 20% | First-Touch-Rate, Kommentar-Aktivitaet |
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Komponenten-Durchschnitte
            components = ['quality_score', 'efficiency_score', 
                         'productivity_score', 'communication_score']
            comp_means = o_scores[components].mean()
            
            fig = go.Figure(data=[go.Bar(
                x=['Qualitaet\n(35%)', 'Effizienz\n(25%)', 
                   'Produktivitaet\n(20%)', 'Kommunikation\n(20%)'],
                y=comp_means,
                marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'],
                text=[f'{v:.2f}' for v in comp_means],
                textposition='outside'
            )])
            
            fig.update_layout(
                yaxis_title="Durchschn. Score (0-1)",
                yaxis=dict(range=[0, 1]),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Korrelation der Komponenten
            corr_matrix = o_scores[components + ['o_score']].corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=['Quality', 'Efficiency', 'Productivity', 'Communication', 'O-Score'],
                y=['Quality', 'Efficiency', 'Productivity', 'Communication', 'O-Score'],
                colorscale='RdYlGn',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate='%{text}',
                textfont={"size": 12}
            ))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("O-Score Verteilung (alle Mitarbeiter)")
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=o_scores['o_score'],
            nbinsx=20,
            marker_color='#4ecdc4',
            opacity=0.8
        ))
        
        fig.add_vline(x=o_scores['o_score'].mean(), line_dash="dash", 
                      line_color="red",
                      annotation_text=f"Mean: {o_scores['o_score'].mean():.2f}")
        
        fig.update_layout(
            xaxis_title="O-Score",
            yaxis_title="Anzahl Mitarbeiter",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"**{len(o_scores)} Mitarbeiter** mit O-Score bewertet (min. 10 Tickets)")
    
    # === FOOTER ===
    st.markdown("---")
    st.caption("""
    **Legende:**
    - **Q-Score:** Subjektive Bewertung durch den Manager (Q1, Q2, Q3 gemittelt)
    - **O-Score:** Objektive Bewertung basierend auf messbaren Metriken aus issues_snapshot.csv
    - **Bias:** Differenz > 1 Punkt gilt als signifikante Ueber-/Unterbewertung
    """)


if __name__ == "__main__":
    main()
