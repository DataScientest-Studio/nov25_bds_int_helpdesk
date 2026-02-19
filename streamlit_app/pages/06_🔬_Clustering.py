"""
F – Mitarbeiter-Clustering (Leakage-freies Unsupervised Learning)
=================================================================
Gruppenbildung basierend auf natürlichen Arbeitsmustern — kein O-Score, kein Data Leakage.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, init_session_state, e, maybe_emoji
)

st.set_page_config(page_title="Employee Clustering", page_icon="🔬", layout="wide")

init_session_state()
render_settings_sidebar()

PROJECT_ROOT = Path(__file__).parent.parent.parent

# ─── Cache functions ──────────────────────────────────────────────────────────

@st.cache_data
def load_cluster_data():
    path = PROJECT_ROOT / "data" / "processed" / "employee_clusters.csv"
    if path.exists():
        return pd.read_csv(path)
    return None

@st.cache_data
def load_cluster_model():
    try:
        import joblib
        path = PROJECT_ROOT / "models" / "employee_clustering.joblib"
        if path.exists():
            return joblib.load(path)
    except Exception:
        pass
    return None

@st.cache_data
def load_comparison_data():
    path = PROJECT_ROOT / "data" / "processed" / "clustering_comparison.csv"
    if path.exists():
        return pd.read_csv(path)
    return None

# ─── Language Helper ──────────────────────────────────────────────────────────

def _t(de: str, en: str) -> str:
    """Return DE or EN text based on current language setting."""
    lang = st.session_state.get('language', 'en')
    return de if lang == 'de' else en

# ─── Page Header ─────────────────────────────────────────────────────────────
page_header(
    e("🔬 ") + _t("Mitarbeiter-Clustering", "Employee Clustering"),
    subtitle=_t(
        "Unsupervised Learning — Leakage-freie Gruppenbildung nach Arbeitsmustern",
        "Unsupervised Learning — Leakage-free grouping by work patterns"
    )
)

# ─── Data Loading ────────────────────────────────────────────────────────────
cluster_df = load_cluster_data()
model_data = load_cluster_model()
comparison_df = load_comparison_data()

if cluster_df is None or model_data is None:
    st.error(_t(
        "⚠️ Clustering-Daten nicht gefunden. Bitte `src/clustering.py` ausführen.",
        "⚠️ Clustering data not found. Please run `src/clustering.py` first."
    ))
    st.stop()

# Detect coordinate columns
coord_x = 'umap_1' if 'umap_1' in cluster_df.columns else 'pca_1'
coord_y = 'umap_2' if 'umap_2' in cluster_df.columns else 'pca_2'
coord_label = "UMAP" if coord_x == 'umap_1' else "PCA"

# Feature columns (numeric, no coordinates/cluster columns)
exclude_cols = {'employee', 'cluster', 'cluster_name', 'umap_1', 'umap_2', 'pca_1', 'pca_2'}
feature_cols = [c for c in cluster_df.columns if c not in exclude_cols and
                pd.api.types.is_numeric_dtype(cluster_df[c])]

# ═══════════════════════════════════════════════════════════════════════════════
# SEKTION 1: KPI-Übersicht
# ═══════════════════════════════════════════════════════════════════════════════
section_header(e("📊 ") + _t("Übersicht", "Overview"))

n_employees = len(cluster_df)
n_clusters = cluster_df['cluster_name'].nunique()
silhouette = model_data.get('silhouette', 0)
algorithm = model_data.get('algorithm', 'N/A')
n_k = model_data.get('n_clusters', 'N/A')

# Quality label
if silhouette >= 0.7:
    sil_label = _t("Exzellent", "Excellent")
    sil_color = "🟢"
elif silhouette >= 0.5:
    sil_label = _t("Gut", "Good")
    sil_color = "🟡"
elif silhouette >= 0.2:
    sil_label = _t("Akzeptabel", "Acceptable")
    sil_color = "🟠"
else:
    sil_label = _t("Schwach", "Weak")
    sil_color = "🔴"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label=_t("Analysierte Mitarbeiter", "Employees Analyzed"),
        value=n_employees
    )
with col2:
    st.metric(
        label=_t("Gefundene Cluster", "Clusters Found"),
        value=n_clusters
    )
with col3:
    st.metric(
        label=_t("Silhouette Score", "Silhouette Score"),
        value=f"{silhouette:.3f}",
        help=_t(
            f"Qualität der Cluster-Trennung: {sil_color} {sil_label} (Skala: -1 bis 1, höher = besser)",
            f"Cluster separation quality: {sil_color} {sil_label} (scale: -1 to 1, higher = better)"
        )
    )
with col4:
    st.metric(
        label=_t("Algorithmus", "Algorithm"),
        value=f"{algorithm} (k={n_k})"
    )

# Methodik-Erklärung
with st.expander(_t("ℹ️ Methodik & Leakage-Freiheit", "ℹ️ Methodology & Leakage Freedom"), expanded=False):
    st.markdown(_t(
        """
        **Warum Clustering statt O-Score?**

        Das bisherige O-Score-Modell hatte zwei kritische Data-Science-Probleme:
        1. **Tautologisches Modell:** Der Zielwert war eine deterministische Funktion der Features
        2. **Data Leakage:** Rang-basierte Features wurden über den Gesamtdatensatz berechnet, bevor der Train/Test-Split erfolgte

        **Diese Clustering-Lösung ist leakage-frei weil:**
        - 🔒 **Unsupervised Learning** — keine Zielvariable, kein Zirkelschluss
        - 📊 **Direkte Aggregationen** — Features sind einfache Mittelwerte/Anteile aus Rohdaten (kein O-Score)
        - 🚫 **Keine Rang-Funktionen** die Train/Test kontaminieren könnten
        - ✅ **Kein Train/Test-Split nötig** — Clustering ist beschreibend, nicht prädiktiv

        **Features:** Ticket-Volumen, Bearbeitungszeit, Prozessschritte, Kommentare, Wiederöffnungsrate, Erfolgsrate, Erstkontaktrate, Prioritäts-Mix, Ticket-Typ-Mix
        """,
        """
        **Why Clustering instead of O-Score?**

        The previous O-Score model had two critical data science problems:
        1. **Tautological model:** The target value was a deterministic function of features
        2. **Data Leakage:** Rank-based features were computed over the full dataset before train/test split

        **This clustering solution is leakage-free because:**
        - 🔒 **Unsupervised Learning** — no target variable, no circular reasoning
        - 📊 **Direct aggregations** — features are simple means/rates from raw data (no O-Score)
        - 🚫 **No rank functions** that could contaminate train/test sets
        - ✅ **No train/test split needed** — clustering is descriptive, not predictive

        **Features:** Ticket volume, processing time, process steps, comments, reopen rate, success rate, first-touch rate, priority mix, ticket type mix
        """
    ))

# ═══════════════════════════════════════════════════════════════════════════════
# SEKTION 2: Cluster-Visualisierung
# ═══════════════════════════════════════════════════════════════════════════════
section_header(e("🗺️ ") + _t("Cluster-Visualisierung", "Cluster Visualization"))

if coord_x in cluster_df.columns and coord_y in cluster_df.columns:
    hover_cols = ['employee', 'ticket_count', 'median_time_hours', 'success_rate', 'reopen_rate']
    hover_cols = [c for c in hover_cols if c in cluster_df.columns]

    fig_scatter = px.scatter(
        cluster_df,
        x=coord_x,
        y=coord_y,
        color='cluster_name',
        hover_data=hover_cols,
        title=_t(
            f"Mitarbeiter-Cluster ({coord_label}-Projektion)",
            f"Employee Clusters ({coord_label} Projection)"
        ),
        labels={
            coord_x: f"{coord_label} 1",
            coord_y: f"{coord_label} 2",
            'cluster_name': _t("Cluster", "Cluster"),
        },
        height=520,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_scatter.update_traces(marker=dict(size=8, opacity=0.8))
    fig_scatter.update_layout(
        legend=dict(title=_t("Cluster", "Cluster"), orientation="v"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Cluster-Größen-Balken
    vc = cluster_df['cluster_name'].value_counts().reset_index()
    vc.columns = ['cluster_name', 'count']
    vc['pct'] = (vc['count'] / vc['count'].sum() * 100).round(1)
    vc['label'] = vc.apply(lambda r: f"{r['count']} ({r['pct']}%)", axis=1)

    fig_bar = px.bar(
        vc, x='cluster_name', y='count',
        text='label',
        color='cluster_name',
        title=_t("Cluster-Größen", "Cluster Sizes"),
        labels={'cluster_name': _t("Cluster", "Cluster"), 'count': _t("Mitarbeiter", "Employees")},
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=320
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning(_t("Koordinaten für Visualisierung fehlen.", "Coordinate columns not found."))

# ═══════════════════════════════════════════════════════════════════════════════
# SEKTION 3: Cluster-Profile (Radar-Chart)
# ═══════════════════════════════════════════════════════════════════════════════
section_header(e("🕸️ ") + _t("Cluster-Profile", "Cluster Profiles"))

# Normalisierte Feature-Mittelwerte pro Cluster
profile_df = cluster_df.groupby('cluster_name')[feature_cols].mean()

# Normalisieren auf 0-1 für Radar
profile_norm = (profile_df - profile_df.min()) / (profile_df.max() - profile_df.min() + 1e-9)

# Leserliche Feature-Labels
feature_labels = {
    'ticket_count': _t("Ticket-Volumen", "Ticket Volume"),
    'median_time_hours': _t("Ø Bearbeitungszeit (h)", "Avg Processing Time (h)"),
    'std_time_hours': _t("Zeitvariabilität", "Time Variability"),
    'avg_steps': _t("Ø Prozessschritte", "Avg Process Steps"),
    'avg_comments': _t("Ø Kommentare", "Avg Comments"),
    'reopen_rate': _t("Wiederöffnungsrate", "Reopen Rate"),
    'success_rate': _t("Erfolgsrate", "Success Rate"),
    'first_touch_rate': _t("Erstkontakt-Rate", "First-Touch Rate"),
    'pct_high': _t("Anteil Hohe Priorität", "High Priority Share"),
    'pct_low': _t("Anteil Niedrige Priorität", "Low Priority Share"),
    'pct_hd_service': _t("Anteil HD Service", "HD Service Share"),
}
display_labels = [feature_labels.get(c, c) for c in feature_cols]

# Radar-Chart
col_radar, col_heatmap = st.columns([1, 1])

with col_radar:
    fig_radar = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, (cluster_name, row) in enumerate(profile_norm.iterrows()):
        fig_radar.add_trace(go.Scatterpolar(
            r=row.values.tolist() + [row.values[0]],  # close the loop
            theta=display_labels + [display_labels[0]],
            fill='toself',
            name=cluster_name,
            line=dict(color=colors[i % len(colors)], width=2),
            fillcolor=colors[i % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.15)') if 'rgb' in colors[i % len(colors)] else colors[i % len(colors)],
        ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 1],
                tickfont=dict(size=9)
            ),
            angularaxis=dict(tickfont=dict(size=9))
        ),
        title=_t("Cluster-Profile (normalisiert)", "Cluster Profiles (normalized)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        height=450,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_heatmap:
    # Heatmap der absoluten Werte
    profile_display = profile_df.copy()
    profile_display.columns = display_labels
    profile_display = profile_display.round(3)

    fig_heat = px.imshow(
        profile_display.T,
        text_auto='.2f',
        color_continuous_scale='RdYlGn',
        title=_t("Feature-Mittelwerte pro Cluster", "Feature Means per Cluster"),
        labels=dict(x=_t("Cluster", "Cluster"), y=_t("Feature", "Feature"), color="Wert"),
        height=450,
        aspect="auto"
    )
    fig_heat.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_heat, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEKTION 4: Cluster-Details
# ═══════════════════════════════════════════════════════════════════════════════
section_header(e("👥 ") + _t("Cluster-Details", "Cluster Details"))

cluster_options = sorted(cluster_df['cluster_name'].unique().tolist())
selected_cluster = st.selectbox(
    _t("Cluster auswählen:", "Select cluster:"),
    options=cluster_options
)

cluster_subset = cluster_df[cluster_df['cluster_name'] == selected_cluster].copy()

col_info, col_metrics = st.columns([1, 2])

with col_info:
    st.metric(_t("Mitarbeiter in Cluster", "Employees in Cluster"), len(cluster_subset))
    st.metric(_t("Anteil Gesamt", "Share of Total"), f"{len(cluster_subset)/len(cluster_df)*100:.1f}%")

    # Cluster-Charakteristika
    if feature_cols:
        means = cluster_subset[feature_cols].mean()
        st.markdown(_t("**Ø Feature-Werte:**", "**Avg Feature Values:**"))
        for col in ['success_rate', 'reopen_rate', 'first_touch_rate', 'ticket_count']:
            if col in means.index:
                label = feature_labels.get(col, col)
                val = means[col]
                if col in ['success_rate', 'reopen_rate', 'first_touch_rate']:
                    st.write(f"• {label}: {val:.1%}")
                else:
                    st.write(f"• {label}: {val:.0f}")

with col_metrics:
    # Top 5 nach ticket_count
    display_cols = ['employee', 'ticket_count', 'median_time_hours', 'success_rate', 'reopen_rate']
    display_cols = [c for c in display_cols if c in cluster_subset.columns]

    top5 = cluster_subset.nlargest(5, 'ticket_count')[display_cols].reset_index(drop=True)
    top5.index = top5.index + 1  # 1-based index

    # Format for display
    if 'success_rate' in top5.columns:
        top5['success_rate'] = top5['success_rate'].apply(lambda x: f"{x:.1%}")
    if 'reopen_rate' in top5.columns:
        top5['reopen_rate'] = top5['reopen_rate'].apply(lambda x: f"{x:.1%}")
    if 'median_time_hours' in top5.columns:
        top5['median_time_hours'] = top5['median_time_hours'].apply(lambda x: f"{x:.0f}h")

    top5.columns = [feature_labels.get(c, c) if c != 'employee' else _t("Mitarbeiter", "Employee") for c in top5.columns]

    st.markdown(_t("**Top 5 nach Ticket-Volumen:**", "**Top 5 by Ticket Volume:**"))
    st.dataframe(top5, use_container_width=True)

# Vollständige Tabelle
with st.expander(_t(f"Alle {len(cluster_subset)} Mitarbeiter in '{selected_cluster}'", f"All {len(cluster_subset)} employees in '{selected_cluster}'")):
    display_all = cluster_subset[display_cols].copy().reset_index(drop=True)
    display_all.index = display_all.index + 1
    if 'success_rate' in display_all.columns:
        display_all['success_rate'] = display_all['success_rate'].apply(lambda x: f"{x:.1%}")
    if 'reopen_rate' in display_all.columns:
        display_all['reopen_rate'] = display_all['reopen_rate'].apply(lambda x: f"{x:.1%}")
    if 'median_time_hours' in display_all.columns:
        display_all['median_time_hours'] = display_all['median_time_hours'].apply(lambda x: f"{x:.0f}h")
    st.dataframe(display_all, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEKTION 5: Algorithmus-Vergleich
# ═══════════════════════════════════════════════════════════════════════════════
section_header(e("⚖️ ") + _t("Algorithmus-Vergleich", "Algorithm Comparison"))

if comparison_df is not None and not comparison_df.empty:
    best_algo = model_data.get('algorithm', '')
    best_k = model_data.get('n_clusters', 0)

    # Highlight-Funktion
    def highlight_best(row):
        is_best = (row.get('algorithm', '') == best_algo and row.get('k', 0) == best_k)
        return ['background-color: #d4edda; font-weight: bold' if is_best else '' for _ in row]

    display_comp = comparison_df.copy()
    display_comp.columns = [
        _t("Algorithmus", "Algorithm") if c == 'algorithm' else
        'k' if c == 'k' else
        _t("Silhouette ↑", "Silhouette ↑") if c == 'silhouette' else
        _t("Davies-Bouldin ↓", "Davies-Bouldin ↓") if c == 'davies_bouldin' else
        _t("Calinski-Harabasz ↑", "Calinski-Harabasz ↑") if c == 'calinski_harabasz' else c
        for c in display_comp.columns
    ]

    styled = display_comp.style.apply(
        lambda row: ['background-color: #d4edda; font-weight: bold'
                     if (row.iloc[0] == best_algo and row.iloc[1] == best_k) else ''
                     for _ in row],
        axis=1
    )

    st.dataframe(display_comp.style.apply(highlight_best, axis=1), use_container_width=True)

    st.caption(_t(
        "↑ höher = besser  |  ↓ niedriger = besser  |  🟢 Gewinner-Konfiguration",
        "↑ higher = better  |  ↓ lower = better  |  🟢 Winner configuration"
    ))

    # Score-Vergleich Plot
    comp_plot = comparison_df.copy()
    comp_plot['config'] = comp_plot['algorithm'] + " k=" + comp_plot['k'].astype(str)
    comp_plot['is_best'] = (comp_plot['algorithm'] == best_algo) & (comp_plot['k'] == best_k)

    fig_comp = px.scatter(
        comp_plot,
        x='davies_bouldin',
        y='silhouette',
        color='algorithm',
        symbol='algorithm',
        size=[15 if b else 8 for b in comp_plot['is_best']],
        text='config',
        title=_t("Silhouette vs. Davies-Bouldin (Gewinner: oben links)", "Silhouette vs. Davies-Bouldin (Winner: top left)"),
        labels={
            'silhouette': _t("Silhouette Score ↑", "Silhouette Score ↑"),
            'davies_bouldin': _t("Davies-Bouldin Score ↓", "Davies-Bouldin Score ↓"),
            'algorithm': _t("Algorithmus", "Algorithm"),
        },
        height=420,
    )
    fig_comp.update_traces(textposition='top center', textfont=dict(size=9))
    fig_comp.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.info(_t("Vergleichs-Daten nicht verfügbar.", "Comparison data not available."))

# ═══════════════════════════════════════════════════════════════════════════════
# SEKTION 6: Leakage-Freiheits-Hinweis
# ═══════════════════════════════════════════════════════════════════════════════
st.success(_t(
    """✅ **Dieses Clustering ist data-leakage-frei:**
    Unsupervised Learning (kein Target) + direkte Feature-Aggregationen aus Rohdaten (kein O-Score) + keine Rang-Funktionen = keine Datenkontamination.
    Silhouette Score {:.3f} — {}""".format(
        silhouette,
        "Exzellente Cluster-Trennung 🟢" if silhouette >= 0.7 else
        "Gute Cluster-Trennung 🟡" if silhouette >= 0.5 else
        "Akzeptable Cluster-Trennung 🟠"
    ),
    """✅ **This clustering is data-leakage-free:**
    Unsupervised Learning (no target) + direct feature aggregations from raw data (no O-Score) + no rank functions = no data contamination.
    Silhouette Score {:.3f} — {}""".format(
        silhouette,
        "Excellent cluster separation 🟢" if silhouette >= 0.7 else
        "Good cluster separation 🟡" if silhouette >= 0.5 else
        "Acceptable cluster separation 🟠"
    )
))

render_footer()
