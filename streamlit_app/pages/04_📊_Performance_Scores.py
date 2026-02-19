"""
D – Performance Scores
D1: Score System | D2: Score Agreement | D3: Bias & Objectivity |
D4: Model Q | D5: Model O | D6: O-Score Components | D7: Forecast
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

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


def t(de_text, en_text):
    return en_text if st.session_state.get('language') == 'en' else de_text


# ─── Shared cache functions ──────────────────────────────────────────────────

@st.cache_data
def load_data_d2():
    """D2/D3: Load Q vs O score comparison data."""
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
    """D3: Load raw scored data."""
    data_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
    if data_path.exists():
        df = pd.read_excel(data_path)
        return df[df['Q1'] > 0]
    return None


@st.cache_resource
def load_q_score_model():
    """D4: Load Q-Score model."""
    q_path = MODELS_DIR / "q_score_model.joblib"
    if q_path.exists():
        return joblib.load(q_path), "q_score"
    opt_path = MODELS_DIR / "optimized_scorer.joblib"
    if opt_path.exists():
        return joblib.load(opt_path), "optimized"
    std_path = MODELS_DIR / "performance_scorer.joblib"
    if std_path.exists():
        return joblib.load(std_path), "standard"
    return None, None


@st.cache_resource
def load_o_score_model():
    """D5: Load O-Score model."""
    o_path = MODELS_DIR / "o_score_model.joblib"
    if o_path.exists():
        return joblib.load(o_path), "o_score"
    return None, None


@st.cache_data
def load_data_d6():
    """D6: Load O-Score results."""
    o_score_path = DATA_DIR / "processed" / "o_score_results.csv"
    if o_score_path.exists():
        return pd.read_csv(o_score_path)
    return None


@st.cache_data
def load_data_d7():
    """D7: Load Q vs O comparison for forecast."""
    comparison_path = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    if comparison_path.exists():
        df = pd.read_csv(comparison_path)
        df['Risk Level'] = pd.cut(
            df['q_score_avg'],
            bins=[0, 2.5, 3.5, 5.01],
            labels=['RED', 'YELLOW', 'GREEN']
        )
        df['Employee'] = df['employee']
        df['Avg Score'] = df['q_score_avg']
        df['Tickets'] = df['ticket_count']
        df['Q1'] = df['q1']
        df['Q2'] = df['q2']
        df['Q3'] = df['q3']
        return df
    return pd.DataFrame()


# ─── Shared helper functions (D4 & D5) ──────────────────────────────────────

def render_metrics_interpretation(avg_acc, avg_mae, avg_cv, avg_f1_macro, avg_f1_weighted, avg_kappa, avg_qwk):
    metrics_data = [
        {
            'metric': 'Accuracy',
            'value': f"{avg_acc*100:.1f}%",
            'rating': "🟢 " + t("Gut", "Good") if avg_acc >= 0.7 else "🟡 " + t("Akzeptabel", "Acceptable") if avg_acc >= 0.5 else "🔴 " + t("Verbesserungsbedarf", "Needs Improvement"),
            'description': t("Anteil korrekt klassifizierter Samples", "Proportion of correctly classified samples")
        },
        {
            'metric': 'MAE',
            'value': f"{avg_mae:.3f}",
            'rating': "🟢 " + t("Sehr gut", "Very Good") if avg_mae < 0.5 else "🟡 " + t("Akzeptabel", "Acceptable") if avg_mae < 0.8 else "🔴 " + t("Hoch", "High"),
            'description': t("Mittlerer Fehler in Klassen", "Mean error in classes")
        },
        {
            'metric': 'CV Score',
            'value': f"{avg_cv*100:.1f}%",
            'rating': "🟢 " + t("Stabil", "Stable") if avg_cv >= 0.6 else "🟡 " + t("Moderat", "Moderate") if avg_cv >= 0.5 else "🔴 " + t("Instabil", "Unstable"),
            'description': t("Cross-Validation Generalisierung", "Cross-validation generalization")
        },
        {
            'metric': 'Macro-F1',
            'value': f"{avg_f1_macro:.3f}",
            'rating': "🟢 " + t("Gut", "Good") if avg_f1_macro >= 0.5 else "🟡 " + t("Moderat", "Moderate") if avg_f1_macro >= 0.3 else "🔴 " + t("Schwach", "Weak"),
            'description': t("Ungewichteter Ø aller Klassen", "Unweighted avg across classes")
        },
        {
            'metric': 'Weighted-F1',
            'value': f"{avg_f1_weighted:.3f}",
            'rating': "🟢 " + t("Gut", "Good") if avg_f1_weighted >= 0.6 else "🟡 " + t("Moderat", "Moderate") if avg_f1_weighted >= 0.5 else "🔴 " + t("Schwach", "Weak"),
            'description': t("Nach Klassengröße gewichtet", "Weighted by class size")
        },
        {
            'metric': "Cohen's Kappa",
            'value': f"{avg_kappa:.3f}",
            'rating': "🟢 " + t("Substanziell", "Substantial") if avg_kappa >= 0.5 else "🟡 " + t("Moderat", "Moderate") if avg_kappa >= 0.3 else "🔴 " + t("Schwach", "Weak"),
            'description': t("Übereinstimmung über Zufall hinaus", "Agreement beyond chance")
        },
        {
            'metric': 'QWK',
            'value': f"{avg_qwk:.3f}",
            'rating': "🟢 " + t("Sehr gut", "Very Good") if avg_qwk >= 0.6 else "🟡 " + t("Gut", "Good") if avg_qwk >= 0.4 else "🔴 " + t("Moderat", "Moderate"),
            'description': t("Bestraft große Fehler stärker", "Penalizes larger errors more")
        }
    ]
    df = pd.DataFrame(metrics_data)
    df.columns = [t('Metrik', 'Metric'), t('Wert', 'Value'), t('Bewertung', 'Rating'), t('Beschreibung', 'Description')]
    st.dataframe(
        df, width="stretch", hide_index=True,
        column_config={
            t('Metrik', 'Metric'): st.column_config.TextColumn(width="medium"),
            t('Wert', 'Value'): st.column_config.TextColumn(width="small"),
            t('Bewertung', 'Rating'): st.column_config.TextColumn(width="medium"),
            t('Beschreibung', 'Description'): st.column_config.TextColumn(width="large")
        }
    )


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
        fig = px.bar(
            importance_df.head(15),
            x='importance', y='feature', orientation='h',
            title=f"{get_text('top_features')} {title}",
            color='importance', color_continuous_scale='Blues'
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.markdown(f"**{get_text('top_10_features')}:**")
        for i, (_, row) in enumerate(importance_df.head(10).iterrows()):
            pct = row['importance'] * 100
            st.markdown(f"{i+1}. **{row['feature']}**: {pct:.1f}%")


def render_confusion_matrix(cm, title):
    cm = np.array(cm)
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=[f"Pred {i+1}" for i in range(cm.shape[1])],
        y=[f"True {i+1}" for i in range(cm.shape[0])],
        colorscale='Blues',
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 14}
    ))
    fig.update_layout(
        title=f"{get_text('confusion_matrix')} - {title}",
        xaxis_title=get_text('predicted'),
        yaxis_title=get_text('actual'),
        height=400
    )
    st.plotly_chart(fig, width="stretch")
    st.markdown(f"""
**{get_text('reading_hint')}:**
- {get_text('diagonal_correct')}
- {get_text('adjacent_acceptable')}
- {get_text('far_problematic')}
""")


# ─── Page Header ────────────────────────────────────────────────────────────
page_header(e("📊 ") + "Performance Scores – Score System, Models & Forecast", help_key='model')


# ════════════════════════════════════════════════════════════════════════════
# D1 – Score System
# ════════════════════════════════════════════════════════════════════════════
st.header("D1 – " + t("Score-System", "Score System"))

# Q-Score Definition
st.markdown(f"## {e('👔')} Q-Score (Manager Rating)")
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
st.markdown(q_desc)

st.markdown("---")

# O-Score Definition
st.markdown(f"## {e('🎯')} O-Score (Objective Rating)")
o_desc = t(
    """
**O-Score** basiert auf objektiven, messbaren Kriterien:

| Komponente | Gewichtung | Beschreibung |
|------------|-----------|-------------|
| **Qualität** | 35% | Reopen-Rate (niedrig = gut), Success-Rate |
| **Effizienz** | 25% | Mediane Bearbeitungszeit (schnell = gut) |
| **Produktivität** | 20% | Ticket-Volumen, Processing Steps |
| **Kommunikation** | 20% | First-Touch-Rate, Kommentar-Aktivität |

**O-Score** = Gewichteter Durchschnitt (Skala 1–5)

**Stärken:** Vollständig objektiv, keine Bias-Anfälligkeit, basiert auf messbaren Daten

**Schwächen:** Erfasst keine Soft Skills, kann Ticket-Komplexität nicht berücksichtigen
""",
    """
**O-Score** is based on objective, measurable criteria:

| Component | Weight | Description |
|-----------|--------|-------------|
| **Quality** | 35% | Reopen rate (low = good), success rate |
| **Efficiency** | 25% | Median processing time (fast = good) |
| **Productivity** | 20% | Ticket volume, processing steps |
| **Communication** | 20% | First-touch rate, comment activity |

**O-Score** = Weighted average (scale 1–5)

**Strengths:** Completely objective, not susceptible to bias, based on measurable data

**Weaknesses:** Does not capture soft skills, cannot account for ticket complexity
"""
)
st.markdown(o_desc)

st.markdown("---")

# Comparison
st.markdown(f"## {e('⚖️')} " + t("Vergleich Q-Score vs O-Score", "Comparison Q-Score vs O-Score"))
comparison_text = t(
    """
**💡 Empfehlung:** Kombiniere beide Scores für ein vollständiges Bild!
- Q-Score erfasst subjektive Qualitätsaspekte, die nicht messbar sind
- O-Score liefert objektive, nachprüfbare Metriken ohne Bias

Wenn Q-Score >> O-Score: Manager bewertet zu wohlwollend (Leniency Bias)
Wenn Q-Score << O-Score: Manager bewertet zu streng (Severity Bias)
""",
    """
**💡 Recommendation:** Combine both scores for a complete picture!
- Q-Score captures subjective quality aspects that are not measurable
- O-Score provides objective, verifiable metrics without bias

When Q-Score >> O-Score: Manager rates too leniently (Leniency Bias)
When Q-Score << O-Score: Manager rates too strictly (Severity Bias)
"""
)
st.info(comparison_text)


# ════════════════════════════════════════════════════════════════════════════
# D2 – Score Agreement Q vs O
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("D2 – " + t("Score-Übereinstimmung Q vs O", "Score Agreement Q vs O"))

data_d2 = load_data_d2()

if 'comparison' not in data_d2:
    error_msg = t(
        "Vergleichsdaten nicht gefunden. Bitte zuerst O-Score berechnen.",
        "Comparison data not found. Please calculate O-Score first."
    )
    st.error(error_msg)
    st.code("python src/o_score.py")
else:
    comparison_d2 = data_d2['comparison']
    overrated_key_d2 = t('ÜBERBEWERTET', 'OVERRATED')
    underrated_key_d2 = t('UNTERBEWERTET', 'UNDERRATED')

    # KPI Cards
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

    # Q vs O Relationship
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
        fig.add_trace(go.Scatter(
            x=[1, 5], y=[1, 5], mode='lines',
            line=dict(color='gray', dash='dash'),
            name=t("Perfekte Korrelation", "Perfect Correlation")
        ))
        fig.update_layout(
            xaxis_title="Q-Score (Manager)",
            yaxis_title=t("O-Score (Objektiv)", "O-Score (Objective)"),
            xaxis=dict(range=[0.5, 5.5]), yaxis=dict(range=[0.5, 5.5]),
            showlegend=False, height=400
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(t(
            "🔴 = Überbewertet (Q > O+1) | 🟢 = Unterbewertet (O > Q+1) | 🔵 = OK",
            "🔴 = Overrated (Q > O+1) | 🟢 = Underrated (O > Q+1) | 🔵 = OK"
        ))

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
            get_text('metric'): [get_text('mean'), get_text('median'), get_text('std_dev'), get_text('min'), get_text('max')],
            'Q-Score': [f"{comparison_d2['q_score'].mean():.2f}", f"{comparison_d2['q_score'].median():.2f}",
                        f"{comparison_d2['q_score'].std():.2f}", f"{comparison_d2['q_score'].min():.1f}",
                        f"{comparison_d2['q_score'].max():.1f}"],
            'O-Score': [f"{comparison_d2['o_score'].mean():.2f}", f"{comparison_d2['o_score'].median():.2f}",
                        f"{comparison_d2['o_score'].std():.2f}", f"{comparison_d2['o_score'].min():.1f}",
                        f"{comparison_d2['o_score'].max():.1f}"]
        })
        st.dataframe(stats_d2, width="stretch", hide_index=True)

    st.markdown("---")

    # Employee Search
    section_header(e("🔍 ") + t("Mitarbeiter-Suche", "Employee Search"))
    search_d2 = st.text_input(t("Mitarbeiter-ID suchen", "Search Employee ID") + ":", "", key="d2_search")
    difference_label = t("Differenz", "Difference")

    if search_d2:
        matches = comparison_d2[comparison_d2['employee'].str.contains(search_d2, case=False)]
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
                        st.metric(difference_label, f"{diff:+.2f}", delta=row['bias_type'])
        else:
            st.warning(t("Kein Mitarbeiter gefunden", "No employee found"))

    st.markdown("---")

    # Complete Ranking
    section_header(e("📋 ") + t("Vollständiges Ranking", "Complete Ranking"))
    sort_options_d2 = [
        t('O-Score (hoch)', 'O-Score (high)'), t('O-Score (niedrig)', 'O-Score (low)'),
        t('Q-Score (hoch)', 'Q-Score (high)'), t('Differenz (groß)', 'Difference (large)')
    ]
    sort_by_d2 = st.selectbox(t("Sortieren nach", "Sort by") + ":", sort_options_d2, key="d2_sort")

    employees_label_d2 = t("Mitarbeiter", "Employee")
    display_d2 = comparison_d2[['employee', 'q_score', 'o_score', 'score_diff', 'bias_type', 'ticket_count']].copy()
    display_d2.columns = [employees_label_d2, 'Q-Score', 'O-Score', difference_label, 'Bias', get_text('tickets')]

    if sort_by_d2 == sort_options_d2[0]:
        display_d2 = display_d2.sort_values('O-Score', ascending=False)
    elif sort_by_d2 == sort_options_d2[1]:
        display_d2 = display_d2.sort_values('O-Score', ascending=True)
    elif sort_by_d2 == sort_options_d2[2]:
        display_d2 = display_d2.sort_values('Q-Score', ascending=False)
    else:
        display_d2 = display_d2.sort_values(difference_label, key=abs, ascending=False)

    st.dataframe(display_d2, width="stretch", hide_index=True, height=400)
    st.caption(t(
        "**Legende:** Q-Score = Subjektive Manager-Bewertung. O-Score = Objektive Bewertung. Bias = Differenz > 1 Punkt.",
        "**Legend:** Q-Score = Subjective manager rating. O-Score = Objective rating. Bias = Difference > 1 point."
    ))


# ════════════════════════════════════════════════════════════════════════════
# D3 – Bias & Objectivity
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("D3 – " + t("Bias & Objektivität", "Bias & Objectivity"))

df_d3 = load_data_d3_scored()
comparison_data_d3 = load_data_d2()  # reuse cached data

# Bias overview
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
        if avg_q1_d3 > 3.5:
            interp_d3 = get_text('manager_rates_mild')
        elif avg_q1_d3 < 2.5:
            interp_d3 = get_text('manager_rates_strict')
        else:
            interp_d3 = get_text('rating_balanced')
        st.markdown(f"""
### {e('📊')} {get_text('bias_leniency')}/{get_text('severity')} Bias

**{get_text('average')} Score:** `{avg_q1_d3:.2f}` ({t("erwartet", "expected")}: 3.0)

**{get_text('type')}:** :{bias_color_d3}[{bias_type_d3}]

> {interp_d3}
""")

    st.markdown("---")

    # Correlation Matrix + Score Distribution
    col1, col2 = st.columns([1, 1])
    with col1:
        section_header(e("📊 ") + get_text('correlation_matrix'), 'correlation')
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix_d3.values, x=['Q1', 'Q2', 'Q3'], y=['Q1', 'Q2', 'Q3'],
            colorscale='RdYlGn_r', zmin=0, zmax=1,
            text=np.round(corr_matrix_d3.values, 3), texttemplate="%{text}", textfont={"size": 16}
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

    # Scatter Q1 vs Q2 vs Q3
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
        fig.update_layout(title=get_text('score_distribution') + " " + t("pro Dimension", "per Dimension"),
                          yaxis_title="Score")
        st.plotly_chart(fig, width="stretch")

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

# Q vs O Bias Analysis
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
        fig = go.Figure(data=[go.Pie(
            labels=bias_counts_d3.index,
            values=bias_counts_d3.values,
            marker_colors=['#4ecdc4', '#ff6b6b', '#45b7d1'],
            hole=0.4
        )])
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
        section_header(e("⚠️ ") + t("Top 10 Überbewertete", "Top 10 Overrated"))
        overrated_df = comparison_d3[comparison_d3['bias_type'] == overrated_key_d3].nsmallest(10, 'score_diff')
        if len(overrated_df) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(y=overrated_df['employee'], x=overrated_df['q_score'],
                                 name='Q-Score', orientation='h', marker_color='#ff6b6b'))
            fig.add_trace(go.Bar(y=overrated_df['employee'], x=overrated_df['o_score'],
                                 name='O-Score', orientation='h', marker_color='#4ecdc4'))
            fig.update_layout(barmode='group', xaxis_title="Score",
                              yaxis=dict(autorange="reversed"), height=400,
                              legend=dict(orientation='h', yanchor='bottom', y=1.02))
            st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Score Diff Histogram
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
# D4 – Model Performance Q-Score
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("D4 – " + t("Model Performance Q-Score", "Model Performance Q-Score"))

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

    # Performance Metrics
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

    # Feature Importance
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

    # Confusion Matrix
    section_header(e("🔢 ") + get_text('confusion_matrix'), 'confusion_q_score')
    if metrics_q:
        available_cm_q = [tn for tn in targets_q if tn in metrics_q and 'confusion_matrix' in metrics_q.get(tn, {})]
        if available_cm_q:
            target_cm_q = st.selectbox(get_text('target_for_cm') + ":", available_cm_q, key='cm_select_q')
            render_confusion_matrix(metrics_q[target_cm_q]['confusion_matrix'], target_cm_q)
        else:
            st.info(get_text('confusion_matrix') + " " + get_text('not_available'))


# ════════════════════════════════════════════════════════════════════════════
# D5 – Model Performance O-Score
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("D5 – " + t("Model Performance O-Score", "Model Performance O-Score"))

section_header(e("🧮 ") + t("O-Score Metriken, Feature Importance, Konfusionsmatrix",
                              "O-Score metrics, feature importance, confusion matrix"))

st.markdown(t(
    """
**O-Score** basiert auf objektiven, messbaren Kriterien:
- **Qualität** (35%): Reopen-Rate, Success-Rate
- **Effizienz** (25%): Mediane Bearbeitungszeit
- **Produktivität** (20%): Ticket-Volumen
- **Kommunikation** (20%): First-Touch-Rate
""",
    """
**O-Score** is based on objective, measurable criteria:
- **Quality** (35%): Reopen rate, success rate
- **Efficiency** (25%): Median processing time
- **Productivity** (20%): Ticket volume
- **Communication** (20%): First-touch rate
"""
))

o_model_data, o_model_type = load_o_score_model()

if o_model_data is None:
    st.warning(e("⚠️ ") + t("O-Score Modell nicht gefunden", "O-Score Model not found"))
else:
    st.success(e("✅ ") + f"{t('Modell geladen', 'Model loaded')}: **{o_model_type.upper()}**")

    # Performance Metrics
    section_header(e("📊 ") + get_text('performance_metrics'), 'metrics_o_score')

    metrics_o = o_model_data.get('metrics', {})
    if metrics_o:
        classifier_metrics_o = metrics_o.get('classifier', {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(get_text('accuracy'), f"{classifier_metrics_o.get('accuracy', 0)*100:.1f}%")
        with col2:
            st.metric(get_text('mae'), f"{classifier_metrics_o.get('mae', 0):.3f}")
        with col3:
            st.metric("CV Score", f"{classifier_metrics_o.get('cv_mean', 0)*100:.1f}%")
        with col4:
            st.metric("CV Std", f"±{classifier_metrics_o.get('cv_std', 0)*100:.1f}%")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Macro-F1", f"{classifier_metrics_o.get('f1_macro', 0):.3f}")
        with col2:
            st.metric("Weighted-F1", f"{classifier_metrics_o.get('f1_weighted', 0):.3f}")
        with col3:
            st.metric("Cohen's Kappa", f"{classifier_metrics_o.get('kappa', 0):.3f}")
        with col4:
            st.metric("QWK", f"{classifier_metrics_o.get('qwk', 0):.3f}")

        st.markdown("---")
        st.markdown("### " + e("📋 ") + t("Metriken-Interpretation", "Metrics Interpretation"))

        acc_o = classifier_metrics_o.get('accuracy', 0)
        mae_o = classifier_metrics_o.get('mae', 0)
        cv_mean_o = classifier_metrics_o.get('cv_mean', 0)
        f1_macro_o = classifier_metrics_o.get('f1_macro', 0)
        f1_weighted_o = classifier_metrics_o.get('f1_weighted', 0)
        kappa_o = classifier_metrics_o.get('kappa', 0)
        qwk_o = classifier_metrics_o.get('qwk', 0)

        render_metrics_interpretation(acc_o, mae_o, cv_mean_o, f1_macro_o, f1_weighted_o, kappa_o, qwk_o)
        st.markdown("---")
        good_metrics_o = sum([acc_o >= 0.7, mae_o < 0.4, cv_mean_o >= 0.7,
                               f1_weighted_o >= 0.7, kappa_o >= 0.5, qwk_o >= 0.7])
        render_overall_assessment(good_metrics_o)

    st.markdown("---")

    # Feature Importance
    section_header(e("📈 ") + get_text('feature_importance'), 'feature_imp_o_score')
    feature_importance_o = o_model_data.get('feature_importance')
    if feature_importance_o is not None:
        if isinstance(feature_importance_o, pd.DataFrame) and not feature_importance_o.empty:
            render_feature_importance_chart(feature_importance_o, "O-Score")
        elif isinstance(feature_importance_o, dict) and feature_importance_o:
            st.info(t("Feature Importance als Dictionary vorhanden", "Feature Importance available as dictionary"))
        else:
            st.info(get_text('feature_importance') + " " + get_text('not_available'))
    else:
        st.info(get_text('feature_importance') + " " + get_text('not_available'))

    st.markdown("---")

    # Confusion Matrix
    section_header(e("🔢 ") + get_text('confusion_matrix'), 'confusion_o_score')
    if metrics_o and 'classifier' in metrics_o:
        cm_o = metrics_o['classifier'].get('confusion_matrix')
        if cm_o:
            render_confusion_matrix(cm_o, "O-Score")
        else:
            st.info(get_text('confusion_matrix') + " " + get_text('not_available'))
    else:
        st.info(get_text('confusion_matrix') + " " + get_text('not_available'))


# ════════════════════════════════════════════════════════════════════════════
# D6 – O-Score Components
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("D6 – " + t("O-Score Komponenten", "O-Score Components"))

o_scores_d6 = load_data_d6()

if o_scores_d6 is None:
    st.error(t(
        "O-Score Daten nicht gefunden. Bitte zuerst O-Score berechnen.",
        "O-Score data not found. Please calculate O-Score first."
    ))
    st.code("python src/o_score.py")
else:
    # O-Score Composition
    section_header(e("📊 ") + t("O-Score Zusammensetzung", "O-Score Composition"))

    quality_label_d6 = t("Qualität", "Quality")
    efficiency_label_d6 = t("Effizienz", "Efficiency")
    productivity_label_d6 = t("Produktivität", "Productivity")
    communication_label_d6 = t("Kommunikation", "Communication")

    st.markdown(f"""
| {t('Komponente', 'Component')} | {t('Gewicht', 'Weight')} | {t('Beschreibung', 'Description')} |
|------------|---------|--------------|
| **{quality_label_d6}** | 35% | {t("Reopen-Rate (niedrig = gut), Success-Rate", "Reopen rate (low = good), success rate")} |
| **{efficiency_label_d6}** | 25% | {t("Bearbeitungszeit (schnell = gut)", "Processing time (fast = good)")} |
| **{productivity_label_d6}** | 20% | {t("Ticket-Volumen, Processing Steps", "Ticket volume, processing steps")} |
| **{communication_label_d6}** | 20% | {t("First-Touch-Rate, Kommentar-Aktivität", "First-touch rate, comment activity")} |
""")

    st.markdown("---")

    components_d6 = ['quality_score', 'efficiency_score', 'productivity_score', 'communication_score']

    col1, col2 = st.columns(2)

    with col1:
        section_header(e("📊 ") + t("Komponenten-Durchschnitte", "Component Averages"))
        comp_means_d6 = o_scores_d6[components_d6].mean()
        labels_d6 = [
            f"{quality_label_d6}\n(35%)", f"{efficiency_label_d6}\n(25%)",
            f"{productivity_label_d6}\n(20%)", f"{communication_label_d6}\n(20%)"
        ]
        fig = go.Figure(data=[go.Bar(
            x=labels_d6, y=comp_means_d6,
            marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'],
            text=[f'{v:.2f}' for v in comp_means_d6], textposition='outside'
        )])
        fig.update_layout(yaxis_title=f"{get_text('average')} Score (0-1)",
                          yaxis=dict(range=[0, 1]), height=400)
        st.plotly_chart(fig, width="stretch")

    with col2:
        section_header(e("🔗 ") + t("Komponenten-Korrelation", "Component Correlation"))
        corr_matrix_d6 = o_scores_d6[components_d6 + ['o_score']].corr()
        labels_short_d6 = [quality_label_d6, efficiency_label_d6,
                            productivity_label_d6, communication_label_d6, 'O-Score']
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix_d6.values, x=labels_short_d6, y=labels_short_d6,
            colorscale='RdYlGn', zmid=0,
            text=corr_matrix_d6.round(2).values, texttemplate='%{text}', textfont={"size": 12}
        ))
        fig.update_layout(height=400)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # O-Score Distribution
    section_header(e("📈 ") + t("O-Score Verteilung (alle Mitarbeiter)", "O-Score Distribution (all employees)"))
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=o_scores_d6['o_score'], nbinsx=20, marker_color='#4ecdc4', opacity=0.8))
    fig.add_vline(x=o_scores_d6['o_score'].mean(), line_dash="dash", line_color="red",
                  annotation_text=f"{get_text('mean')}: {o_scores_d6['o_score'].mean():.2f}")
    fig.update_layout(xaxis_title="O-Score", yaxis_title=get_text('count'), height=300)
    st.plotly_chart(fig, width="stretch")
    st.success(f"**{len(o_scores_d6)} {t('Mitarbeiter mit O-Score bewertet (min. 10 Tickets)', 'employees with O-Score (min. 10 tickets)')}**")


# ════════════════════════════════════════════════════════════════════════════
# D7 – Forecast & Simulation
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("D7 – " + t("Forecast & Simulation", "Forecast & Simulation"))

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

    # Simulation
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

    # Comparison chart
    fig = go.Figure()
    for risk, color in [('RED', '#f44336'), ('YELLOW', '#FF9800'), ('GREEN', '#4CAF50')]:
        fig.add_trace(go.Bar(
            name=f'{risk} (Current)', x=[risk],
            y=[(employee_df_d7['Risk Level'] == risk).sum()],
            marker_color=color, opacity=0.5
        ))
        fig.add_trace(go.Bar(
            name=f'{risk} (After)', x=[risk],
            y=[(simulated_df['New Risk Level'] == risk).sum()],
            marker_color=color
        ))
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
