"""
D – Performance Scores
D1: Score System | D2: Score Agreement | D3: Bias & Objectivity |
D4: Model Q | D5: Overall Performance | D7: Forecast
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import joblib
import sys

# Import components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Performance Scores", page_icon="📊", layout="wide")
init_session_state()
render_settings_sidebar()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


def t(de_text, en_text):
    return en_text if st.session_state.get('language') == 'en' else de_text


# ─── Cache functions ──────────────────────────────────────────────────────────

@st.cache_data
def load_data_d2():
    data = {}
    o_score_path = DATA_DIR / "processed" / "o_score_results.csv"
    if o_score_path.exists():
        data['o_scores'] = pd.read_csv(o_score_path)
    comparison_path = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    if comparison_path.exists():
        data['comparison'] = pd.read_csv(comparison_path)
        if 'q_score_avg' in data['comparison'].columns:
            data['comparison']['q_score'] = data['comparison']['q_score_avg']
        data['comparison']['score_diff'] = data['comparison']['o_score'] - data['comparison']['q_score']
        overrated_label = t('ÜBERBEWERTET', 'OVERRATED')
        underrated_label = t('UNTERBEWERTET', 'UNDERRATED')
        data['comparison']['bias_type'] = data['comparison']['score_diff'].apply(
            lambda x: overrated_label if x < -1 else (underrated_label if x > 1 else 'OK')
        )
    return data


@st.cache_data
def load_data_d3_scored():
    data_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
    if data_path.exists():
        df = pd.read_excel(data_path)
        return df[df['Q1'] > 0]
    return None


@st.cache_resource
def load_q_score_model():
    q_path = MODELS_DIR / "q_score_model.joblib"
    if q_path.exists():
        return joblib.load(q_path), "q_score"
    opt_path = MODELS_DIR / "optimized_scorer.joblib"
    if opt_path.exists():
        return joblib.load(opt_path), "optimized"
    return None, None


@st.cache_resource
def load_o_score_model():
    o_path = MODELS_DIR / "o_score_model.joblib"
    if o_path.exists():
        return joblib.load(o_path), "o_score"
    return None, None


@st.cache_data
def load_data_d6():
    o_score_path = DATA_DIR / "processed" / "o_score_results.csv"
    if o_score_path.exists():
        return pd.read_csv(o_score_path)
    return None


@st.cache_data
def load_data_d7():
    comparison_path = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    if comparison_path.exists():
        df = pd.read_csv(comparison_path)
        df['Risk Level'] = pd.cut(df['q_score_avg'], bins=[0, 2.5, 3.5, 5.01],
                                   labels=['RED', 'YELLOW', 'GREEN'])
        df['Employee'] = df['employee']
        df['Avg Score'] = df['q_score_avg']
        df['Tickets'] = df['ticket_count']
        df['Q1'] = df['q1']
        df['Q2'] = df['q2']
        df['Q3'] = df['q3']
        return df
    return pd.DataFrame()


@st.cache_data
def load_overall_performance():
    """
    Outer join of Q-Score, O-Score and Cluster data.
    Returns only employees with at least 2 of 3 dimensions available.
    """
    q_path  = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    o_path  = DATA_DIR / "processed" / "o_score_results.csv"
    km_path = DATA_DIR / "processed" / "cluster_results.csv"

    frames = {}
    if q_path.exists():
        q = pd.read_csv(q_path)
        col = 'q_score_avg' if 'q_score_avg' in q.columns else 'q_score'
        frames['q'] = q[['employee', col, 'q1', 'q2', 'q3']].rename(columns={col: 'q_score'})
    if o_path.exists():
        o = pd.read_csv(o_path)
        frames['o'] = o[['employee', 'o_score']]
    if km_path.exists():
        km = pd.read_csv(km_path)
        frames['km'] = km[['issue_assignee', 'cluster_label']].rename(columns={'issue_assignee': 'employee'})

    if not frames:
        return None

    # Build outer join
    result = None
    for key, df in frames.items():
        if result is None:
            result = df
        else:
            result = result.merge(df, on='employee', how='outer')

    # Filter: at least 2 of the 3 core dimensions present
    core_cols = [c for c in ['q_score', 'o_score', 'cluster_label'] if c in result.columns]
    result['_available'] = result[core_cols].notna().sum(axis=1)
    result = result[result['_available'] >= 2].drop(columns=['_available'])
    return result.reset_index(drop=True)


@st.cache_data
def load_overall_merged():
    q_path  = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    km_path = DATA_DIR / "processed" / "kmeans_cluster_results.csv"
    if not q_path.exists() or not km_path.exists():
        return None
    q  = pd.read_csv(q_path)
    km = pd.read_csv(km_path)
    if 'q_score_avg' in q.columns:
        q = q.rename(columns={'q_score_avg': 'q_score'})
    merged = q.merge(
        km[['issue_assignee', 'cluster_label',
            'median_resolution_days', 'resolution_rate',
            'pct_fast_resolved', 'pct_reopened', 'total_tickets',
            'tickets_per_month']],
        left_on='employee', right_on='issue_assignee', how='inner'
    )
    return merged


# ─── Helper functions ─────────────────────────────────────────────────────────

def render_metrics_interpretation(avg_acc, avg_mae, avg_cv, avg_f1_macro, avg_f1_weighted, avg_kappa, avg_qwk):
    metrics_data = [
        {'metric': 'Accuracy', 'value': f"{avg_acc*100:.1f}%",
         'rating': "🟢 " + t("Gut", "Good") if avg_acc >= 0.7 else "🟡 " + t("Akzeptabel", "Acceptable") if avg_acc >= 0.5 else "🔴 " + t("Verbesserungsbedarf", "Needs Improvement"),
         'description': t("Anteil korrekt klassifizierter Samples", "Proportion of correctly classified samples")},
        {'metric': 'MAE', 'value': f"{avg_mae:.3f}",
         'rating': "🟢 " + t("Sehr gut", "Very Good") if avg_mae < 0.5 else "🟡 " + t("Akzeptabel", "Acceptable") if avg_mae < 0.8 else "🔴 " + t("Hoch", "High"),
         'description': t("Mittlerer Fehler in Klassen", "Mean error in classes")},
        {'metric': 'CV Score', 'value': f"{avg_cv*100:.1f}%",
         'rating': "🟢 " + t("Stabil", "Stable") if avg_cv >= 0.6 else "🟡 " + t("Moderat", "Moderate") if avg_cv >= 0.5 else "🔴 " + t("Instabil", "Unstable"),
         'description': t("Cross-Validation Generalisierung", "Cross-validation generalization")},
        {'metric': 'Macro-F1', 'value': f"{avg_f1_macro:.3f}",
         'rating': "🟢 " + t("Gut", "Good") if avg_f1_macro >= 0.5 else "🟡 " + t("Moderat", "Moderate") if avg_f1_macro >= 0.3 else "🔴 " + t("Schwach", "Weak"),
         'description': t("Ungewichteter Ø aller Klassen", "Unweighted avg across classes")},
        {'metric': 'Weighted-F1', 'value': f"{avg_f1_weighted:.3f}",
         'rating': "🟢 " + t("Gut", "Good") if avg_f1_weighted >= 0.6 else "🟡 " + t("Moderat", "Moderate") if avg_f1_weighted >= 0.5 else "🔴 " + t("Schwach", "Weak"),
         'description': t("Nach Klassengröße gewichtet", "Weighted by class size")},
        {'metric': "Cohen's Kappa", 'value': f"{avg_kappa:.3f}",
         'rating': "🟢 " + t("Substanziell", "Substantial") if avg_kappa >= 0.5 else "🟡 " + t("Moderat", "Moderate") if avg_kappa >= 0.3 else "🔴 " + t("Schwach", "Weak"),
         'description': t("Übereinstimmung über Zufall hinaus", "Agreement beyond chance")},
        {'metric': 'QWK', 'value': f"{avg_qwk:.3f}",
         'rating': "🟢 " + t("Sehr gut", "Very Good") if avg_qwk >= 0.6 else "🟡 " + t("Gut", "Good") if avg_qwk >= 0.4 else "🔴 " + t("Moderat", "Moderate"),
         'description': t("Bestraft große Fehler stärker", "Penalizes larger errors more")},
    ]
    df = pd.DataFrame(metrics_data)
    df.columns = [t('Metrik', 'Metric'), t('Wert', 'Value'), t('Bewertung', 'Rating'), t('Beschreibung', 'Description')]
    st.dataframe(df, width="stretch", hide_index=True,
                 column_config={
                     t('Metrik', 'Metric'): st.column_config.TextColumn(width="medium"),
                     t('Wert', 'Value'): st.column_config.TextColumn(width="small"),
                     t('Bewertung', 'Rating'): st.column_config.TextColumn(width="medium"),
                     t('Beschreibung', 'Description'): st.column_config.TextColumn(width="large")
                 })


def render_overall_assessment(good_metrics):
    very_good = t("Sehr gut", "Very Good")
    good_label = t("Gut", "Good")
    improvement = t("Verbesserungspotential", "Improvement Potential")
    metrics_label = t("Metriken im grünen Bereich", "metrics in green zone")
    overall = t("Gesamtbewertung", "Overall Assessment")
    if good_metrics >= 5:
        st.success(e("✅ ") + f"**{overall}: {very_good}** ({good_metrics}/6 {metrics_label})")
    elif good_metrics >= 3:
        st.info(e("👍 ") + f"**{overall}: {good_label}** ({good_metrics}/6 {metrics_label})")
    else:
        st.warning(e("⚠️ ") + f"**{overall}: {improvement}** ({good_metrics}/6 {metrics_label})")


def render_feature_importance_chart(importance_df, title):
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(importance_df.head(15), x='importance', y='feature', orientation='h',
                     title=f"{get_text('top_features')} {title}", color='importance',
                     color_continuous_scale='Blues')
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.markdown(f"**{get_text('top_10_features')}:**")
        for i, (_, row) in enumerate(importance_df.head(10).iterrows()):
            st.markdown(f"{i+1}. **{row['feature']}**: {row['importance']*100:.1f}%")


def render_confusion_matrix(cm, title):
    cm = np.array(cm)
    fig = go.Figure(data=go.Heatmap(
        z=cm, x=[f"Pred {i+1}" for i in range(cm.shape[1])],
        y=[f"True {i+1}" for i in range(cm.shape[0])],
        colorscale='Blues', text=cm, texttemplate="%{text}", textfont={"size": 14}
    ))
    fig.update_layout(title=f"{get_text('confusion_matrix')} - {title}",
                      xaxis_title=get_text('predicted'), yaxis_title=get_text('actual'), height=400)
    st.plotly_chart(fig, width="stretch")
    st.markdown(f"""
**{get_text('reading_hint')}:**
- {get_text('diagonal_correct')}
- {get_text('adjacent_acceptable')}
- {get_text('far_problematic')}
""")


# ─── Page Header ─────────────────────────────────────────────────────────────
page_header(e("📊 ") + "Performance Scores – Score System, Models & Forecast", help_key='model')

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab_d1, tab_d2, tab_d3, tab_d4, tab_overall, tab_d7 = st.tabs([
    t("📋 Score System", "📋 Score System"),
    t("⚖️ Score Agreement Q vs O", "⚖️ Score Agreement Q vs O"),
    t("🔍 Bias & Objektivität", "🔍 Bias & Objectivity"),
    t("🧮 Model Performance Q-Score", "🧮 Model Performance Q-Score"),
    t("🏆 Overall Performance", "🏆 Overall Performance"),
    t("🔮 Forecast & Simulation", "🔮 Forecast & Simulation"),
])


# ════════════════════════════════════════════════════════════════════════════
# Tab 1: Score System (D1)
# ════════════════════════════════════════════════════════════════════════════
with tab_d1:
    q_desc = t(
        """
**Q-Score** basiert auf subjektiven Manager-Bewertungen mit drei Dimensionen:

| Dimension | Beschreibung | Skala |
|-----------|-------------|-------|
| **Q1** | Genauigkeit, Präzision, Sorgfalt | 1–5 |
| **Q2** | Gründlichkeit, Vollständigkeit, Umfassendheit | 1–5 |
| **Q3** | Reaktionsschnelligkeit, Verbindlichkeit, Höflichkeit | 1–5 |

**Q-Score Avg** = Durchschnitt von Q1, Q2, Q3

**Stärken:** Erfasst subjektive Qualitätsaspekte, Soft Skills, direktes Manager-Feedback

**Schwächen:** Anfällig für Bias, subjektive Interpretation, mangelnde Konsistenz
""",
        """
**Q-Score** is based on subjective manager ratings with three dimensions:

| Dimension | Description | Scale |
|-----------|-------------|-------|
| **Q1** | Accuracy, precision, attention to detail | 1–5 |
| **Q2** | Thoroughness, completeness, comprehensiveness | 1–5 |
| **Q3** | Responsiveness, promptness, courtesy | 1–5 |

**Q-Score Avg** = Average of Q1, Q2, Q3

**Strengths:** Captures subjective quality aspects, soft skills, direct manager feedback

**Weaknesses:** Susceptible to bias, subjective interpretation, lack of consistency
"""
    )

    o_desc = t(
        """
**O-Score** basiert auf objektiven, messbaren Kriterien:

| Komponente | Gewichtung | Sub-Metriken |
|------------|-----------|--------------|
| **Qualität** | 35% | 60% Reopen-Rate (invertiert) + 40% Success-Rate |
| **Effizienz** | 25% | 100% Bearbeitungszeit (Perzentil, invertiert) |
| **Produktivität** | 20% | 60% Ticket-Volumen + 40% Bearbeitungsschritte (invertiert) |
| **Kommunikation** | 20% | 50% First-Touch-Rate + 50% Kommentar-Deviation (optimal = Median) |

**O-Score** = Gewichteter Durchschnitt (Skala 1–5)

**Stärken:** Vollständig objektiv, keine Bias-Anfälligkeit, basiert auf messbaren Daten

**Schwächen:** Erfasst keine Soft Skills, kann Ticket-Komplexität nicht berücksichtigen
""",
        """
**O-Score** is based on objective, measurable criteria:

| Component | Weight | Sub-Metrics |
|-----------|--------|-------------|
| **Quality** | 35% | 60% Reopen Rate (inverted) + 40% Success Rate |
| **Efficiency** | 25% | 100% Processing Time (percentile, inverted) |
| **Productivity** | 20% | 60% Ticket Volume + 40% Processing Steps (inverted) |
| **Communication** | 20% | 50% First-Touch Rate + 50% Comment Deviation (optimal = Median) |

**O-Score** = Weighted average (scale 1–5)

**Strengths:** Completely objective, not susceptible to bias, based on measurable data

**Weaknesses:** Does not capture soft skills, cannot account for ticket complexity
"""
    )

    col_q, col_o = st.columns(2)
    with col_q:
        st.markdown(f"## {e('👔')} Q-Score (Manager Rating)")
        st.markdown(q_desc)
    with col_o:
        st.markdown(f"## {e('🎯')} O-Score (Objective Rating)")
        st.markdown(o_desc)


# ════════════════════════════════════════════════════════════════════════════
# Tab 2: Score Agreement Q vs O (D2)
# ════════════════════════════════════════════════════════════════════════════
with tab_d2:
    data_d2 = load_data_d2()

    if 'comparison' not in data_d2:
        st.error(t("Vergleichsdaten nicht gefunden. Bitte zuerst O-Score berechnen.",
                   "Comparison data not found. Please calculate O-Score first."))
        st.code("python src/o_score.py")
    else:
        comparison_d2 = data_d2['comparison']
        overrated_key_d2 = t('ÜBERBEWERTET', 'OVERRATED')
        underrated_key_d2 = t('UNTERBEWERTET', 'UNDERRATED')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Q-Score (Manager)", f"{comparison_d2['q_score'].mean():.2f}",
                      delta=t("Subjektiv", "Subjective"), delta_color="off")
        with col2:
            st.metric(t("O-Score (Objektiv)", "O-Score (Objective)"),
                      f"{comparison_d2['o_score'].mean():.2f}",
                      delta=f"{comparison_d2['score_diff'].mean():.2f} {t('Differenz', 'Difference')}")
        with col3:
            corr_d2 = comparison_d2['o_score'].corr(comparison_d2['q_score'])
            st.metric(t("Korrelation", "Correlation"), f"{corr_d2:.2f}",
                      delta=t("Moderat", "Moderate") if corr_d2 > 0.5 else t("Schwach", "Weak"))
        with col4:
            overrated_count_d2 = (comparison_d2['bias_type'] == overrated_key_d2).sum()
            st.metric(t("Überbewertet", "Overrated"),
                      f"{overrated_count_d2} / {len(comparison_d2)}",
                      delta=f"{overrated_count_d2/len(comparison_d2)*100:.0f}%",
                      delta_color="inverse")

        st.markdown("---")
        section_header(e("📊 ") + t("Q vs O Score Beziehung", "Q vs O Score Relationship"))

        col1, col2 = st.columns(2)
        with col1:
            section_header(e("📊 ") + "Q-Score vs O-Score")
            colors_d2 = comparison_d2['bias_type'].map({
                overrated_key_d2: 'red', underrated_key_d2: 'green', 'OK': 'blue'
            })
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=comparison_d2['q_score'], y=comparison_d2['o_score'],
                mode='markers',
                marker=dict(size=10, color=colors_d2, opacity=0.7),
                text=comparison_d2['employee'],
                hovertemplate='<b>%{text}</b><br>Q-Score: %{x:.2f}<br>O-Score: %{y:.2f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(x=[1, 5], y=[1, 5], mode='lines',
                                     line=dict(color='gray', dash='dash'),
                                     name=t("Perfekte Korrelation", "Perfect Correlation")))
            fig.update_layout(
                xaxis_title="Q-Score (Manager)",
                yaxis_title=t("O-Score (Objektiv)", "O-Score (Objective)"),
                xaxis=dict(range=[0.5, 5.5]), yaxis=dict(range=[0.5, 5.5]),
                showlegend=False, height=400
            )
            st.plotly_chart(fig, width="stretch")
            st.caption(t("🔴 = Überbewertet (Q > O+1) | 🟢 = Unterbewertet (O > Q+1) | 🔵 = OK",
                         "🔴 = Overrated (Q > O+1) | 🟢 = Underrated (O > Q+1) | 🔵 = OK"))

        with col2:
            section_header(e("📈 ") + t("Score-Verteilungen", "Score Distributions"))
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=comparison_d2['q_score'], name='Q-Score (Manager)',
                                       opacity=0.6, marker_color='#ff6b6b'))
            fig.add_trace(go.Histogram(x=comparison_d2['o_score'],
                                       name=t('O-Score (Objektiv)', 'O-Score (Objective)'),
                                       opacity=0.6, marker_color='#4ecdc4'))
            fig.update_layout(barmode='overlay', xaxis_title="Score",
                              yaxis_title=get_text('count'), height=400)
            st.plotly_chart(fig, width="stretch")

            stats_d2 = pd.DataFrame({
                get_text('metric'): [get_text('mean'), get_text('median'), get_text('std_dev'),
                                     get_text('min'), get_text('max')],
                'Q-Score': [f"{comparison_d2['q_score'].mean():.2f}",
                            f"{comparison_d2['q_score'].median():.2f}",
                            f"{comparison_d2['q_score'].std():.2f}",
                            f"{comparison_d2['q_score'].min():.1f}",
                            f"{comparison_d2['q_score'].max():.1f}"],
                'O-Score': [f"{comparison_d2['o_score'].mean():.2f}",
                            f"{comparison_d2['o_score'].median():.2f}",
                            f"{comparison_d2['o_score'].std():.2f}",
                            f"{comparison_d2['o_score'].min():.1f}",
                            f"{comparison_d2['o_score'].max():.1f}"]
            })
            st.dataframe(stats_d2, width="stretch", hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# Tab 3: Bias & Objectivity (D3)
# ════════════════════════════════════════════════════════════════════════════
with tab_d3:
    df_d3 = load_data_d3_scored()
    comparison_data_d3 = load_data_d2()

    section_header(e("🚨 ") + t("Bias-Typen", "Bias Types"))

    if df_d3 is not None:
        col1, col2 = st.columns(2)
        with col1:
            corr_matrix_d3 = df_d3[['Q1', 'Q2', 'Q3']].corr()
            avg_corr_d3 = (corr_matrix_d3.values.sum() - 3) / 6
            severity_d3 = get_text('bias_high') if avg_corr_d3 > 0.9 else get_text('bias_medium') if avg_corr_d3 > 0.8 else get_text('bias_low')
            severity_color_d3 = "red" if avg_corr_d3 > 0.9 else "orange" if avg_corr_d3 > 0.8 else "green"
            st.markdown(f"""
### {e('🔄')} {get_text('bias_halo')}

**{get_text('inter_correlation')}:** `{avg_corr_d3:.3f}`

**{get_text('bias_severity')}:** :{severity_color_d3}[{severity_d3}]

> {get_text('manager_rates_identical')}
""")
        with col2:
            avg_q1_d3 = df_d3['Q1'].mean()
            bias_type_d3 = get_text('bias_leniency') if avg_q1_d3 > 3.5 else get_text('severity') if avg_q1_d3 < 2.5 else get_text('neutral')
            bias_color_d3 = "orange" if avg_q1_d3 > 3.5 else "blue" if avg_q1_d3 < 2.5 else "green"
            interp_d3 = get_text('manager_rates_mild') if avg_q1_d3 > 3.5 else get_text('manager_rates_strict') if avg_q1_d3 < 2.5 else get_text('rating_balanced')
            st.markdown(f"""
### {e('📊')} {get_text('bias_leniency')}/{get_text('severity')} Bias

**{get_text('average')} Score:** `{avg_q1_d3:.2f}` ({t("erwartet", "expected")}: 3.0)

**{get_text('type')}:** :{bias_color_d3}[{bias_type_d3}]

> {interp_d3}
""")

        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            section_header(e("📊 ") + get_text('correlation_matrix'), 'correlation')
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix_d3.values, x=['Q1', 'Q2', 'Q3'], y=['Q1', 'Q2', 'Q3'],
                colorscale='RdYlGn_r', zmin=0, zmax=1,
                text=np.round(corr_matrix_d3.values, 3), texttemplate="%{text}",
                textfont={"size": 16}
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
        with col2:
            section_header(e("📈 ") + get_text('score_distribution'))
            fig = go.Figure()
            for q in ['Q1', 'Q2', 'Q3']:
                fig.add_trace(go.Histogram(x=df_d3[q], name=q, opacity=0.6, nbinsx=5))
            fig.update_layout(barmode='overlay', xaxis_title="Score (1-5)",
                              yaxis_title=get_text('count'), height=350)
            st.plotly_chart(fig, width="stretch")

        st.markdown("---")
        section_header(e("🔗 ") + get_text('score_relationships'))
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(df_d3, x='Q1', y='Q2', color='Q3',
                             title="Q1 vs Q2 (Color = Q3)", color_continuous_scale='RdYlGn')
            fig.add_trace(go.Scatter(x=[1, 5], y=[1, 5], mode='lines',
                                     name=get_text('perfect_correlation'),
                                     line=dict(dash='dash', color='gray')))
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = go.Figure()
            for q in ['Q1', 'Q2', 'Q3']:
                fig.add_trace(go.Box(y=df_d3[q], name=q))
            fig.update_layout(
                title=get_text('score_distribution') + " " + t("pro Dimension", "per Dimension"),
                yaxis_title="Score")
            st.plotly_chart(fig, width="stretch")

        st.markdown("---")
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
        section_header(e("📋 ") + get_text('statistical_summary'))
        stats_d3 = pd.DataFrame({
            get_text('metric'): [get_text('sample_count'), get_text('mean'), get_text('std_dev'),
                                 get_text('median'), get_text('min'), get_text('max')],
            'Q1': [len(df_d3), df_d3['Q1'].mean(), df_d3['Q1'].std(), df_d3['Q1'].median(),
                   df_d3['Q1'].min(), df_d3['Q1'].max()],
            'Q2': [len(df_d3), df_d3['Q2'].mean(), df_d3['Q2'].std(), df_d3['Q2'].median(),
                   df_d3['Q2'].min(), df_d3['Q2'].max()],
            'Q3': [len(df_d3), df_d3['Q3'].mean(), df_d3['Q3'].std(), df_d3['Q3'].median(),
                   df_d3['Q3'].min(), df_d3['Q3'].max()],
        }).round(2)
        st.dataframe(stats_d3, width="stretch")
    else:
        st.warning(e("⚠️ ") + get_text('no_data') + " (Q-Score data)")

    if 'comparison' in comparison_data_d3:
        comparison_d3 = comparison_data_d3['comparison']
        overrated_key_d3 = t('ÜBERBEWERTET', 'OVERRATED')
        underrated_key_d3 = t('UNTERBEWERTET', 'UNDERRATED')

        st.markdown("---")
        section_header(e("🔍 ") + t("Q vs O Bias-Analyse", "Q vs O Bias Analysis"))
        col1, col2 = st.columns(2)
        with col1:
            section_header(e("📊 ") + t("Bias-Verteilung", "Bias Distribution"))
            bias_counts_d3 = comparison_d3['bias_type'].value_counts()
            fig = go.Figure(data=[go.Pie(labels=bias_counts_d3.index, values=bias_counts_d3.values,
                                         marker_colors=['#4ecdc4', '#ff6b6b', '#45b7d1'], hole=0.4)])
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
            overrated_c = bias_counts_d3.get(overrated_key_d3, 0)
            underrated_c = bias_counts_d3.get(underrated_key_d3, 0)
            ok_c = bias_counts_d3.get('OK', 0)
            employees_word = t("Mitarbeiter", "employees")
            st.info(f"""
**{get_text('interpretation')}:**
- {overrated_c} {employees_word} {t("überbewertet", "overrated")}
- {underrated_c} {employees_word} {t("unterbewertet", "underrated")}
- {ok_c} {employees_word} {t("fair bewertet", "fairly rated")} (±1)
""")
        with col2:
            section_header(e("⚠️ ") + t("Bias-Verteilung", "Bias Distribution"))
            st.info(t(
                f"**{overrated_c}** überbewertet (Q > O+1) · **{underrated_c}** unterbewertet (O > Q+1) · **{ok_c}** fair (±1)",
                f"**{overrated_c}** overrated (Q > O+1) · **{underrated_c}** underrated (O > Q+1) · **{ok_c}** fair (±1)"
            ))

        st.markdown("---")

        # ── Top 10 Überbewertete ─────────────────────────────────────────
        section_header(e("⚠️ ") + t("Top 10 Überbewertete: Q-Score vs O-Score", "Top 10 Overrated: Q-Score vs O-Score"))
        st.markdown(t(
            "Mitarbeiter mit der größten positiven Abweichung zwischen Manager-Bewertung (Q) und objektivem Score (O). "
            "**Überbewertet** = Q-Score > O-Score um mehr als 1 Punkt.",
            "Employees with the largest positive gap between manager rating (Q) and objective score (O). "
            "**Overrated** = Q-Score exceeds O-Score by more than 1 point."
        ))

        # Language-safe: use score_diff directly, not bias_type label
        overrated_top10 = comparison_d3[comparison_d3['score_diff'] < -1].nsmallest(10, 'score_diff').copy()
        overrated_top10['delta'] = (overrated_top10['score_diff']).round(2)

        if overrated_top10.empty:
            st.info(t(
                "Keine stark überbewerteten Mitarbeiter gefunden (Differenz Q−O > 1).",
                "No significantly overrated employees found (Q−O gap > 1)."
            ))
        else:
            fig_ov = go.Figure()

            # O-Score bars (lower, objective)
            fig_ov.add_trace(go.Bar(
                name='O-Score (' + t('Objektiv', 'Objective') + ')',
                y=overrated_top10['employee'],
                x=overrated_top10['o_score'],
                orientation='h',
                marker=dict(color='#4ecdc4', line=dict(color='white', width=1)),
                text=overrated_top10['o_score'].round(2),
                textposition='inside',
                hovertemplate='<b>%{y}</b><br>O-Score: %{x:.2f}<extra></extra>'
            ))

            # Q-Score bars (higher, subjective — the "inflated" one)
            fig_ov.add_trace(go.Bar(
                name='Q-Score (' + t('Manager', 'Manager') + ')',
                y=overrated_top10['employee'],
                x=overrated_top10['q_score'],
                orientation='h',
                marker=dict(color='#ff6b6b', line=dict(color='white', width=1)),
                text=overrated_top10['q_score'].round(2),
                textposition='inside',
                hovertemplate='<b>%{y}</b><br>Q-Score: %{x:.2f}<br>Δ: %{customdata:+.2f}<extra></extra>',
                customdata=overrated_top10['delta']
            ))

            # Delta annotations
            for _, row in overrated_top10.iterrows():
                fig_ov.add_annotation(
                    x=max(row['q_score'], row['o_score']) + 0.15,
                    y=row['employee'],
                    text=f"Δ {row['delta']:+.2f}",
                    showarrow=False,
                    font=dict(size=11, color='#c0392b', family='monospace'),
                    xanchor='left'
                )

            fig_ov.update_layout(
                barmode='group',
                xaxis=dict(
                    title=t("Score (1–5)", "Score (1–5)"),
                    range=[0, 6.2]
                ),
                yaxis=dict(autorange='reversed', title=''),
                height=max(350, len(overrated_top10) * 42),
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                plot_bgcolor='rgba(0,0,0,0)',
            )
            fig_ov.add_vline(x=0, line_color='gray', line_width=0.5)
            st.plotly_chart(fig_ov, width="stretch")

            st.caption(t(
                "🔴 Q-Score = Manager-Bewertung (subjektiv) · 🟩 O-Score = Objektive Messung · "
                "Δ = O−Q (je negativer, desto stärker überbewertet)",
                "🔴 Q-Score = Manager rating (subjective) · 🟩 O-Score = Objective measurement · "
                "Δ = O−Q (more negative = more overrated)"
            ))

        st.markdown("---")
        section_header(e("📈 ") + t("Score-Differenz Histogramm", "Score Difference Histogram"))
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=comparison_d3['score_diff'], nbinsx=20,
                                   marker_color='purple', opacity=0.7))
        fig.add_vline(x=0, line_dash="dash", line_color="red",
                      annotation_text=t("Keine Differenz", "No Difference"))
        fig.add_vline(x=comparison_d3['score_diff'].mean(), line_dash="solid", line_color="orange",
                      annotation_text=f"{get_text('mean')}: {comparison_d3['score_diff'].mean():.2f}")
        fig.update_layout(
            xaxis_title=f"O-Score - Q-Score ({t('negativ = überbewertet', 'negative = overrated')})",
            yaxis_title=get_text('count'), height=300
        )
        st.plotly_chart(fig, width="stretch")


# ════════════════════════════════════════════════════════════════════════════
# Tab 4: Model Performance Q-Score (D4)
# ════════════════════════════════════════════════════════════════════════════
with tab_d4:
    section_header(e("🧮 ") + t("Q-Score Metriken, Feature Importance, Konfusionsmatrix",
                                 "Q-Score metrics, feature importance, confusion matrix"))
    st.markdown(t(
        """
**Q-Score** basiert auf subjektiven Manager-Bewertungen mit drei Dimensionen:
- **Q1**: Genauigkeit, Präzision, Sorgfalt
- **Q2**: Gründlichkeit, Vollständigkeit, Umfassendheit
- **Q3**: Reaktionsschnelligkeit, Verbindlichkeit, Höflichkeit
""",
        """
**Q-Score** is based on subjective manager ratings with three dimensions:
- **Q1**: Accuracy, precision, attention to detail
- **Q2**: Thoroughness, completeness, comprehensiveness
- **Q3**: Responsiveness, promptness, courtesy
"""
    ))

    q_model_data, q_model_type = load_q_score_model()

    if q_model_data is None:
        st.warning(e("⚠️ ") + t("Q-Score Modell nicht gefunden", "Q-Score Model not found"))
    else:
        st.success(e("✅ ") + f"{t('Modell geladen', 'Model loaded')}: **{q_model_type.upper()}**")
        targets_q = ['Q1', 'Q2', 'Q3']
        metrics_q = q_model_data.get('metrics', {})

        section_header(e("📊 ") + get_text('performance_metrics'), 'metrics_q_score')

        if metrics_q:
            cols_q = st.columns(len(targets_q))
            for idx, (target, col) in enumerate(zip(targets_q, cols_q)):
                if target in metrics_q:
                    m = metrics_q[target]
                    with col:
                        st.markdown(f"### {target}")
                        st.metric(get_text('accuracy'), f"{m.get('accuracy', 0)*100:.1f}%")
                        st.metric(get_text('mae'), f"{m.get('mae', 0):.3f}")
                        st.metric("CV Score", f"{m.get('cv_mean', 0)*100:.1f}%")
                        st.metric("Macro-F1", f"{m.get('f1_macro', 0):.3f}")
                        st.metric("Weighted-F1", f"{m.get('f1_weighted', 0):.3f}")
                        st.metric("Cohen's Kappa", f"{m.get('kappa', 0):.3f}")
                        st.metric("QWK", f"{m.get('qwk', 0):.3f}")

            st.markdown("---")
            available_targets_q = [tn for tn in targets_q if tn in metrics_q]
            if available_targets_q:
                avg_acc_q = np.mean([metrics_q[tn].get('accuracy', 0) for tn in available_targets_q])
                avg_mae_q = np.mean([metrics_q[tn].get('mae', 0) for tn in available_targets_q])
                avg_cv_q = np.mean([metrics_q[tn].get('cv_mean', 0) for tn in available_targets_q])
                avg_f1_macro_q = np.mean([metrics_q[tn].get('f1_macro', 0) for tn in available_targets_q])
                avg_f1_weighted_q = np.mean([metrics_q[tn].get('f1_weighted', 0) for tn in available_targets_q])
                avg_kappa_q = np.mean([metrics_q[tn].get('kappa', 0) for tn in available_targets_q])
                avg_qwk_q = np.mean([metrics_q[tn].get('qwk', 0) for tn in available_targets_q])

                st.markdown(f"### {t('Ø Durchschnitt (Q1, Q2, Q3)', 'Avg (Q1, Q2, Q3)')}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(e("📈 ") + t("Ø Accuracy", "Avg Accuracy"), f"{avg_acc_q*100:.1f}%")
                with col2:
                    st.metric(e("📉 ") + t("Ø MAE", "Avg MAE"), f"{avg_mae_q:.3f}")
                with col3:
                    st.metric(e("🔄 ") + t("Ø CV Score", "Avg CV Score"), f"{avg_cv_q*100:.1f}%")
                with col4:
                    st.metric(e("📊 ") + t("Ø Macro-F1", "Avg Macro-F1"), f"{avg_f1_macro_q:.3f}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(t("Ø Weighted-F1", "Avg Weighted-F1"), f"{avg_f1_weighted_q:.3f}")
                with col2:
                    st.metric(t("Ø Cohen's Kappa", "Avg Cohen's Kappa"), f"{avg_kappa_q:.3f}")
                with col3:
                    st.metric(t("Ø QWK", "Avg QWK"), f"{avg_qwk_q:.3f}")

                st.markdown("---")
                st.markdown("### " + e("📋 ") + t("Metriken-Interpretation (Durchschnitt)", "Metrics Interpretation (Average)"))
                render_metrics_interpretation(avg_acc_q, avg_mae_q, avg_cv_q, avg_f1_macro_q,
                                              avg_f1_weighted_q, avg_kappa_q, avg_qwk_q)
                st.markdown("---")
                good_metrics_q = sum([avg_acc_q >= 0.65, avg_mae_q < 0.6, avg_cv_q >= 0.6,
                                       avg_f1_weighted_q >= 0.6, avg_kappa_q >= 0.4, avg_qwk_q >= 0.6])
                render_overall_assessment(good_metrics_q)

        st.markdown("---")
        section_header(e("📈 ") + get_text('feature_importance'), 'feature_imp_q_score')
        feature_importance_q = q_model_data.get('feature_importance', {})
        if isinstance(feature_importance_q, dict) and feature_importance_q:
            available_fi_q = [tn for tn in targets_q if tn in feature_importance_q]
            if available_fi_q:
                target_select_q = st.selectbox(get_text('select_target') + ":", available_fi_q, key='fi_select_q')
                if target_select_q in feature_importance_q:
                    render_feature_importance_chart(feature_importance_q[target_select_q], target_select_q)
            else:
                st.info(get_text('feature_importance') + " " + get_text('not_available'))
        else:
            st.info(get_text('feature_importance') + " " + get_text('not_available'))

        st.markdown("---")
        section_header(e("🔢 ") + get_text('confusion_matrix'), 'confusion_q_score')
        if metrics_q:
            available_cm_q = [tn for tn in targets_q if tn in metrics_q and
                               'confusion_matrix' in metrics_q.get(tn, {})]
            if available_cm_q:
                target_cm_q = st.selectbox(get_text('target_for_cm') + ":", available_cm_q, key='cm_select_q')
                render_confusion_matrix(metrics_q[target_cm_q]['confusion_matrix'], target_cm_q)
            else:
                st.info(get_text('confusion_matrix') + " " + get_text('not_available'))


# ════════════════════════════════════════════════════════════════════════════
# Tab 5: Overall Performance
# ════════════════════════════════════════════════════════════════════════════
with tab_overall:
    section_header(
        e("🏆 ") + t("Overall Performance: Q-Score · O-Score · Cluster", "Overall Performance: Q-Score · O-Score · Cluster")
    )
    st.caption(t(
        "Alle Mitarbeiter mit mindestens zwei verfügbaren Datenpunkten (Q-Score, O-Score, Cluster). "
        "Employee = Assignee-ID · Q-Score = Ø Q1/Q2/Q3 · O-Score = gewichteter Composite-Score · Cluster = K-Means Klassifikation",
        "All employees with at least two available data points (Q-Score, O-Score, Cluster). "
        "Employee = Assignee ID · Q-Score = avg Q1/Q2/Q3 · O-Score = weighted composite score · Cluster = K-Means classification"
    ))

    df_all = load_overall_performance()

    if df_all is None or df_all.empty:
        st.error(e("⚠️ ") + t(
            "Daten nicht gefunden. Bitte o_score.py und clustering_unsuper.py ausführen.",
            "Data not found. Please run o_score.py and clustering_unsuper.py first."
        ))
        st.code("python src/o_score.py\npython src/unsuper_clustering.py")
    else:
        n_total = len(df_all)
        n_all3  = df_all[['q_score','o_score','cluster_label']].notna().all(axis=1).sum()
        n_q     = df_all['q_score'].notna().sum()     if 'q_score'     in df_all.columns else 0
        n_o     = df_all['o_score'].notna().sum()     if 'o_score'     in df_all.columns else 0
        n_km    = df_all['cluster_label'].notna().sum() if 'cluster_label' in df_all.columns else 0

        # ── KPI row ────────────────────────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric(t("👥 Mitarbeiter (≥2)", "👥 Employees (≥2)"), n_total)
        c2.metric(t("🔢 Alle 3 Quellen", "🔢 All 3 sources"), n_all3)
        c3.metric(t("📋 Q-Score vorhanden", "📋 Q-Score present"), n_q)
        c4.metric(t("🎯 O-Score vorhanden", "🎯 O-Score present"), n_o)
        c5.metric(t("🔬 Cluster vorhanden", "🔬 Cluster present"), n_km)

        st.markdown("---")

        # ── Filter row ─────────────────────────────────────────────────
        col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
        with col_f1:
            cluster_opts = [t("Alle Cluster", "All Clusters")]
            if 'cluster_label' in df_all.columns:
                cluster_opts += sorted(df_all['cluster_label'].dropna().unique().tolist())
            sel_cluster = st.selectbox(
                t("Cluster filtern:", "Filter by cluster:"),
                options=cluster_opts,
                key='op_cluster_filter'
            )
        with col_f2:
            avail_opts = [
                t("Alle (≥2)", "All (≥2)"),
                t("Alle 3 vorhanden", "All 3 present"),
                t("Nur Q + O (kein Cluster)", "Q + O only (no cluster)"),
                t("Nur O + Cluster (kein Q)", "O + Cluster only (no Q)"),
            ]
            sel_avail = st.selectbox(
                t("Verfügbarkeit filtern:", "Filter by availability:"),
                options=avail_opts,
                key='op_avail_filter'
            )
        with col_f3:
            search_term = st.text_input(
                t("🔍 Mitarbeiter suchen:", "🔍 Search employee:"),
                key='op_search',
                placeholder="Assignee ID..."
            )

        # Apply filters
        df_view = df_all.copy()
        if sel_cluster != t("Alle Cluster", "All Clusters") and 'cluster_label' in df_view.columns:
            df_view = df_view[df_view['cluster_label'] == sel_cluster]
        if sel_avail == t("Alle 3 vorhanden", "All 3 present"):
            df_view = df_view[df_view[['q_score','o_score','cluster_label']].notna().all(axis=1)]
        elif sel_avail == t("Nur Q + O (kein Cluster)", "Q + O only (no cluster)"):
            df_view = df_view[df_view['q_score'].notna() & df_view['o_score'].notna() & df_view['cluster_label'].isna()]
        elif sel_avail == t("Nur O + Cluster (kein Q)", "O + Cluster only (no Q)"):
            df_view = df_view[df_view['o_score'].notna() & df_view['cluster_label'].notna() & df_view['q_score'].isna()]
        if search_term:
            df_view = df_view[df_view['employee'].str.contains(search_term, case=False, na=False)]

        df_view = df_view.sort_values(
            ['cluster_label', 'o_score'],
            ascending=[True, False],
            na_position='last'
        ).reset_index(drop=True)
        df_view.index = df_view.index + 1

        # ── Display table ──────────────────────────────────────────────
        disp_cols = [c for c in ['employee','q_score','o_score','cluster_label'] if c in df_view.columns]
        rename_map = {
            'employee':     t('Employee (Assignee ID)', 'Employee (Assignee ID)'),
            'q_score':      t('Q-Score (Ø Q1/Q2/Q3)', 'Q-Score (avg Q1/Q2/Q3)'),
            'o_score':      t('O-Score (Composite)', 'O-Score (Composite)'),
            'cluster_label': t('Cluster', 'Cluster'),
        }
        df_disp = df_view[disp_cols].rename(columns=rename_map)

        q_col = t('Q-Score (Ø Q1/Q2/Q3)', 'Q-Score (avg Q1/Q2/Q3)')
        o_col = t('O-Score (Composite)',   'O-Score (Composite)')

        st.dataframe(
            df_disp,
            width="stretch",
            hide_index=False,
            column_config={
                t('Employee (Assignee ID)', 'Employee (Assignee ID)'):
                    st.column_config.TextColumn(width="medium"),
                q_col: st.column_config.ProgressColumn(
                    min_value=1, max_value=5, format="%.2f", width="medium"
                ),
                o_col: st.column_config.ProgressColumn(
                    min_value=1, max_value=5, format="%.2f", width="medium"
                ),
                t('Cluster', 'Cluster'):
                    st.column_config.TextColumn(width="large"),
            }
        )

        st.caption(t(
            f"📋 {len(df_view)} von {n_total} Mitarbeitern werden angezeigt · "
            "Leere Felder = Datenpunkt nicht verfügbar · "
            "Sortiert nach: Cluster → O-Score (absteigend)",
            f"📋 Showing {len(df_view)} of {n_total} employees · "
            "Empty fields = data point not available · "
            "Sorted by: Cluster → O-Score (descending)"
        ))


# ════════════════════════════════════════════════════════════════════════════
# Tab 6: Forecast & Simulation (D7)
# ════════════════════════════════════════════════════════════════════════════
with tab_d7:
    section_header(e("🔮 ") + get_text('forecast_recommendations'), 'forecast')
    employee_df_d7 = load_data_d7()

    if not employee_df_d7.empty:
        st.markdown(f"""
### {get_text('what_if_scenario')}

{get_text('simulate_interventions')}
""")
        col1, col2 = st.columns(2)
        with col1:
            training_effect = st.slider(
                get_text('training_effect'),
                min_value=0.0, max_value=1.0, value=0.3, step=0.1, key="d7_training_effect"
            )
        with col2:
            target_employees_d7 = st.multiselect(
                get_text('target_group'),
                options=['RED', 'YELLOW', 'GREEN'],
                default=['RED', 'YELLOW'], key="d7_target"
            )

        simulated_df = employee_df_d7.copy()
        mask = simulated_df['Risk Level'].isin(target_employees_d7)
        simulated_df.loc[mask, 'Avg Score'] = simulated_df.loc[mask, 'Avg Score'] * (1 + training_effect)
        simulated_df.loc[simulated_df['Avg Score'] > 5, 'Avg Score'] = 5
        simulated_df['New Risk Level'] = pd.cut(
            simulated_df['Avg Score'], bins=[0, 2.5, 3.5, 5.01], labels=['RED', 'YELLOW', 'GREEN']
        )

        st.markdown(f"### {get_text('simulation_results')}")
        col1, col2, col3 = st.columns(3)
        with col1:
            old_red_d7 = (employee_df_d7['Risk Level'] == 'RED').sum()
            new_red_d7 = (simulated_df['New Risk Level'] == 'RED').sum()
            st.metric(e("🔴 ") + "RED", new_red_d7, delta=int(new_red_d7 - old_red_d7), delta_color="inverse")
        with col2:
            old_yellow_d7 = (employee_df_d7['Risk Level'] == 'YELLOW').sum()
            new_yellow_d7 = (simulated_df['New Risk Level'] == 'YELLOW').sum()
            st.metric(e("🟡 ") + "YELLOW", new_yellow_d7, delta=int(new_yellow_d7 - old_yellow_d7), delta_color="inverse")
        with col3:
            old_green_d7 = (employee_df_d7['Risk Level'] == 'GREEN').sum()
            new_green_d7 = (simulated_df['New Risk Level'] == 'GREEN').sum()
            st.metric(e("🟢 ") + "GREEN", new_green_d7, delta=int(new_green_d7 - old_green_d7), delta_color="normal")

        fig = go.Figure()
        for risk, color in [('RED', '#f44336'), ('YELLOW', '#FF9800'), ('GREEN', '#4CAF50')]:
            fig.add_trace(go.Bar(name=f'{risk} (Current)', x=[risk],
                                 y=[(employee_df_d7['Risk Level'] == risk).sum()],
                                 marker_color=color, opacity=0.5))
            fig.add_trace(go.Bar(name=f'{risk} (After)', x=[risk],
                                 y=[(simulated_df['New Risk Level'] == risk).sum()],
                                 marker_color=color))
        fig.update_layout(title=get_text('before_after_comparison'), barmode='group', height=400)
        st.plotly_chart(fig, width="stretch")

        st.markdown(f"### {e('💡')} {get_text('recommendations')}")
        improvements_d7 = old_red_d7 - new_red_d7 + old_yellow_d7 - new_yellow_d7
        if improvements_d7 > 0:
            st.success(f"""
{get_text('with_training_effect')} **{training_effect*100:.0f}%** {get_text('on_employees')}
**{', '.join(target_employees_d7)}** {get_text('categories')}:

- **{improvements_d7}** {get_text('employees_would_improve')}
- **{new_green_d7 - old_green_d7}** {get_text('more_in_green')}
""")
        else:
            st.info(get_text('adjust_parameters'))
    else:
        st.info(get_text('no_data'))


# Footer
render_footer()
