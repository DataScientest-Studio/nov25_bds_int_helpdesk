"""
F – Mitarbeiter-Clustering (Leakage-freies Unsupervised Learning)
=================================================================
Gruppenbildung basierend auf natürlichen Arbeitsmustern — kein O-Score, kein Data Leakage.
Erweitert um K-Means Performance Clustering (90.963 Tickets, 302 Mitarbeiter, 4 Cluster).
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

# ─── Language Helper ──────────────────────────────────────────────────────────

def _t(de: str, en: str) -> str:
    lang = st.session_state.get('language', 'en')
    return de if lang == 'de' else en

# ─── Cache functions – Original Clustering ───────────────────────────────────

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

# ─── Cache functions – K-Means Deep Dive ─────────────────────────────────────

def _load_csv_with_fallback(canonical: str, fallback: str):
    """Load canonical (non-prefixed) file, fall back to kmeans_* version."""
    p = PROJECT_ROOT / "data" / "processed" / canonical
    if not p.exists():
        p = PROJECT_ROOT / "data" / "processed" / fallback
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def load_kmeans_results():
    return _load_csv_with_fallback("cluster_results.csv", "kmeans_cluster_results.csv")

@st.cache_data
def load_kmeans_profiles():
    return _load_csv_with_fallback("cluster_profiles.csv", "kmeans_cluster_profiles.csv")

@st.cache_data
def load_kmeans_pca():
    return _load_csv_with_fallback("pca_results.csv", "kmeans_pca_results.csv")

@st.cache_data
def load_kmeans_elbow():
    return _load_csv_with_fallback("elbow_silhouette.csv", "kmeans_elbow_silhouette.csv")

@st.cache_data
def load_kmeans_feature_importance():
    return _load_csv_with_fallback("feature_importance.csv", "kmeans_feature_importance.csv")

@st.cache_data
def load_kmeans_outliers():
    # Prefer canonical non-prefixed file (from unsuper pipeline), fallback to kmeans_ version
    p = PROJECT_ROOT / "data" / "processed" / "outlier_analysis.csv"
    if not p.exists():
        p = PROJECT_ROOT / "data" / "processed" / "kmeans_outlier_analysis.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    # Merge cluster labels if not present
    if 'cluster_label' not in df.columns:
        cr = PROJECT_ROOT / "data" / "processed" / "cluster_results.csv"
        if cr.exists():
            labels = pd.read_csv(cr)[['issue_assignee', 'cluster_label']]
            df = df.merge(labels, on='issue_assignee', how='left')
    return df

# ─── K-Means constants ───────────────────────────────────────────────────────

CLUSTER_COLORS = {
    "High Performer 🟢": "#2ecc71",
    "Solid Performer 🟡": "#f39c12",
    "Low Performer 🔴": "#e74c3c",
    "Specialist ⚫": "#2c3e50",
}

FEATURE_LABELS_KM = {
    'median_resolution_days': 'Median Resolution (days)',
    'avg_resolution_days': 'Avg Resolution (days)',
    'std_resolution_days': 'Std Dev Resolution (days)',
    'pct_fast_resolved': '% Fast Resolved',
    'total_tickets': 'Total Tickets',
    'tickets_per_month': 'Tickets/Month',
    'active_months': 'Active Months',
    'avg_priority': 'Avg Priority Score',
    'pct_high_priority': '% High Priority',
    'n_distinct_projects': 'Distinct Projects',
    'n_distinct_categories': 'Distinct Categories',
    'pct_reopened': '% Reopened',
    'resolution_rate': 'Resolution Rate',
    'avg_comments': 'Avg Comments',
    'pct_sole_resolver': '% Sole Resolver',
    'avg_first_response_days': 'Avg First Response (days)',
    'avg_processing_steps': 'Avg Processing Steps',
}

def hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ─── Page Header ─────────────────────────────────────────────────────────────
page_header(
    e("🔬 ") + _t("Mitarbeiter-Clustering", "Employee Clustering"),
    subtitle="Unsupervised Learning"
)

# ═══════════════════════════════════════════════════════════════════════════════
# HAUPT-TABS
# ═══════════════════════════════════════════════════════════════════════════════
(main_tab2,) = st.tabs([
    _t("🎯 K-Means Performance Clustering", "🎯 K-Means Performance Clustering"),
])

# ═══════════════════════════════════════════════════════════════════════════════
# K-MEANS PERFORMANCE CLUSTERING
# ═══════════════════════════════════════════════════════════════════════════════
with main_tab2:
    # Load data
    km_results = load_kmeans_results()
    km_profiles = load_kmeans_profiles()
    km_pca = load_kmeans_pca()
    km_elbow = load_kmeans_elbow()
    km_feat_imp = load_kmeans_feature_importance()

    if km_results is None or km_profiles is None:
        st.error(_t("⚠️ K-Means Clustering-Daten nicht gefunden. Stelle sicher, dass `data/processed/kmeans_cluster_results.csv` existiert.",
                    "⚠️ K-Means clustering data not found. Make sure `data/processed/kmeans_cluster_results.csv` exists."))
        st.info(_t("Führe `python src/feature_engineering_kmeans.py` und `python src/clustering_kmeans.py` aus.",
                   "Run `python src/feature_engineering_kmeans.py` and `python src/clustering_kmeans.py`."))
    else:
        FEATURE_COLS_KM = list(FEATURE_LABELS_KM.keys())

        # ── Sidebar Info
        n_emp_km = len(km_results)
        n_clust_km = km_results['cluster_label'].nunique()

        # KPI Banner
        st.markdown("### 🎯 " + _t("K-Means Mitarbeiter Performance Clustering", "K-Means Employee Performance Clustering"))
        st.markdown("*90.963 " + _t("Tickets · 302 Mitarbeiter · 4 Cluster · Silhouette Score 0.5807", "Tickets · 302 Employees · 4 Clusters · Silhouette Score 0.5807") + "*")

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        avg_res = km_results['median_resolution_days'].median()
        avg_rate = km_results['resolution_rate'].mean()
        avg_tick = km_results['total_tickets'].median()
        pct_fast = km_results['pct_fast_resolved'].mean()

        kpi1.metric("👥 " + _t("Mitarbeiter", "Employees"), f"{n_emp_km}")
        kpi2.metric("🔢 Cluster", f"{n_clust_km}")
        kpi3.metric("⏱ Med. Resolution", f"{avg_res:.1f} " + _t("Tage", "Days"))
        kpi4.metric("✅ " + _t("Ø Lösungsrate", "Avg Resolution Rate"), f"{avg_rate:.1%}")
        kpi5.metric("⚡ " + _t("Ø Schnell Gelöst", "Avg Fast Resolved"), f"{pct_fast:.1%}")

        st.markdown("---")

        # ── Cluster-Legende
        col_legend, col_pie = st.columns([1, 2])
        with col_legend:
            st.markdown("#### " + _t("Cluster-Übersicht", "Cluster Overview"))
            for label, color in CLUSTER_COLORS.items():
                if label in km_results['cluster_label'].values:
                    count = (km_results['cluster_label'] == label).sum()
                    pct = count / n_emp_km * 100
                    emp_word = _t("Mitarbeiter", "Employees")
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;margin:6px 0">'
                        f'<div style="width:16px;height:16px;background:{color};border-radius:50%"></div>'
                        f'<span><b>{label}</b><br><small>{count} {emp_word} ({pct:.1f}%)</small></span></div>',
                        unsafe_allow_html=True
                    )

        with col_pie:
            dist = km_results['cluster_label'].value_counts().reset_index()
            dist.columns = ['Cluster', 'Count']
            fig_pie = px.pie(
                dist, values='Count', names='Cluster',
                color='Cluster', color_discrete_map=CLUSTER_COLORS,
                hole=0.4, title=_t("Cluster-Verteilung", "Cluster Distribution")
            )
            fig_pie.update_layout(height=320, legend=dict(orientation='h', y=-0.2), margin=dict(t=40, b=50))
            fig_pie.update_traces(textinfo='percent+label', textfont_size=10)
            st.plotly_chart(fig_pie, use_container_width=True)

        # ── Cluster-Profil Summary
        st.markdown("---")
        st.subheader("📊 " + _t("Cluster Performance Übersicht", "Cluster Performance Summary"))
        disp_cols_km = ['cluster_label', 'median_resolution_days', 'avg_resolution_days',
                         'resolution_rate', 'pct_fast_resolved', 'total_tickets',
                         'tickets_per_month', 'pct_reopened', 'avg_priority']
        if all(c in km_profiles.columns for c in disp_cols_km):
            summary = km_profiles[disp_cols_km].copy()
            summary.columns = ['Cluster', 'Med Resolution (d)', 'Avg Resolution (d)',
                                'Resolution Rate', '% Fast Resolved', 'Avg Tickets',
                                'Tickets/Month', '% Reopened', 'Avg Priority']
            st.dataframe(
                summary.style.format({
                    'Med Resolution (d)': '{:.2f}', 'Avg Resolution (d)': '{:.2f}',
                    'Resolution Rate': '{:.1%}', '% Fast Resolved': '{:.1%}',
                    'Avg Tickets': '{:.0f}', 'Tickets/Month': '{:.1f}',
                    '% Reopened': '{:.1%}', 'Avg Priority': '{:.2f}',
                }).background_gradient(subset=['Med Resolution (d)', 'Avg Resolution (d)'], cmap='RdYlGn_r')
                .background_gradient(subset=['Resolution Rate', '% Fast Resolved'], cmap='RdYlGn'),
                use_container_width=True, hide_index=True
            )
        else:
            st.dataframe(km_profiles, use_container_width=True)

        st.markdown("---")

        # ── Tabs für Details
        km_tab1, km_tab2, km_tab3, km_tab4, km_tab5, km_tab6 = st.tabs([
            "🔬 PCA & Elbow",
            _t("📊 Feature Analyse", "📊 Feature Analysis"),
            _t("👥 Mitarbeiter Profile", "👥 Employee Profiles"),
            _t("📋 Cluster Details", "📋 Cluster Details"),
            "✅ Validation",
            _t("⚠️ Outlier Analyse", "⚠️ Outlier Analysis"),
        ])

        # ──── KM TAB 1: PCA & ELBOW
        with km_tab1:
            if km_pca is not None:
                st.subheader(_t("PCA Visualisierung (2D)", "PCA Visualization (2D)"))
                pca_plot = km_pca.merge(
                    km_results[['issue_assignee', 'total_tickets', 'median_resolution_days',
                                 'resolution_rate', 'tickets_per_month']],
                    on='issue_assignee', how='left'
                )
                PC1_LABEL = _t("Abschlussrate (→ höher = mehr Tickets abgeschlossen) [PC1, 54.9% Var.]",
                               "Completion Rate (→ higher = more tickets completed) [PC1, 54.9% Var.]")
                PC2_LABEL = _t("Bearbeitungszeit (↑ höher = langsamer) [PC2, 23.7% Var.]",
                               "Processing Time (↑ higher = slower) [PC2, 23.7% Var.]")

                fig_pca = px.scatter(
                    pca_plot, x='PC1', y='PC2',
                    color='cluster_label', color_discrete_map=CLUSTER_COLORS,
                    hover_data={'issue_assignee': True, 'total_tickets': True,
                                'median_resolution_days': ':.1f', 'resolution_rate': ':.2f', 'PC1': False, 'PC2': False},
                    labels={'PC1': PC1_LABEL, 'PC2': PC2_LABEL, 'cluster_label': 'Cluster'},
                    title=_t("Mitarbeiter-Cluster im Performance-Raum", "Employee Clusters in Performance Space"),
                    size='total_tickets', size_max=25, height=540
                )
                x_mid = float(pca_plot['PC1'].median())
                y_mid = float(pca_plot['PC2'].median())
                fig_pca.add_vline(x=x_mid, line_dash="dot", line_color="rgba(150,150,150,0.4)")
                fig_pca.add_hline(y=y_mid, line_dash="dot", line_color="rgba(150,150,150,0.4)")
                quad = dict(showarrow=False, font=dict(size=10, color="rgba(100,100,100,0.7)"),
                            bgcolor="rgba(255,255,255,0.6)", borderpad=3)
                xmax, xmin = float(pca_plot['PC1'].max()), float(pca_plot['PC1'].min())
                ymax, ymin = float(pca_plot['PC2'].max()), float(pca_plot['PC2'].min())
                fig_pca.add_annotation(x=xmax*0.85, y=ymin*0.85, text=_t("✅ Schnell & abgeschlossen", "✅ Fast & Completed"), **quad)
                fig_pca.add_annotation(x=xmin*0.85, y=ymin*0.85, text=_t("⚫ Spezialisten", "⚫ Specialists"), **quad)
                fig_pca.add_annotation(x=xmax*0.85, y=ymax*0.85, text=_t("🟡 Solide, aber langsam", "🟡 Solid, but slow"), **quad)
                fig_pca.add_annotation(x=xmin*0.85, y=ymax*0.85, text=_t("🔴 Kritisch", "🔴 Critical"), **quad)
                fig_pca.update_layout(legend=dict(orientation='h', y=-0.2))
                st.plotly_chart(fig_pca, use_container_width=True)
                st.caption(_t("💡 Punktgröße = Ticket-Volumen · PC1 = 54,9% Varianz (Abschlussrate) · PC2 = 23,7% Varianz (Geschwindigkeit)",
                              "💡 Dot size = Ticket volume · PC1 = 54.9% variance (completion rate) · PC2 = 23.7% variance (speed)"))

            if km_elbow is not None:
                st.markdown("---")
                col_elbow, col_sil = st.columns(2)
                k_best = km_results['cluster'].nunique() if 'cluster' in km_results.columns else 4

                with col_elbow:
                    st.subheader("📈 Elbow Curve (Inertia)")
                    fig_elbow = px.line(km_elbow, x='k', y='inertia', markers=True,
                                        labels={'k': _t('Anzahl Cluster (k)', 'Number of Clusters (k)'), 'inertia': 'Inertia'},
                                        title="Elbow Method")
                    fig_elbow.add_vline(x=k_best, line_dash="dash", line_color="red",
                                         annotation_text=f"k={k_best} (" + _t("gewählt", "selected") + ")")
                    fig_elbow.update_layout(height=320)
                    st.plotly_chart(fig_elbow, use_container_width=True)

                with col_sil:
                    st.subheader("📊 Silhouette Score")
                    fig_sil = px.bar(km_elbow, x='k', y='silhouette',
                                      color='silhouette', color_continuous_scale='RdYlGn',
                                      labels={'k': _t('Anzahl Cluster (k)', 'Number of Clusters (k)'), 'silhouette': 'Silhouette Score'},
                                      title="Silhouette Analysis")
                    fig_sil.add_vline(x=k_best, line_dash="dash", line_color="red",
                                       annotation_text=f"k={k_best} (" + _t("gewählt", "selected") + ")")
                    fig_sil.update_layout(height=320)
                    st.plotly_chart(fig_sil, use_container_width=True)

        # ──── KM TAB 2: FEATURE ANALYSE
        with km_tab2:
            col_feat_sel, col_feat_box = st.columns([1, 2])
            with col_feat_sel:
                st.subheader(_t("Feature auswählen", "Select Feature"))
                selected_feat = st.selectbox(
                    "Feature:",
                    options=[c for c in FEATURE_COLS_KM if c in km_results.columns],
                    format_func=lambda x: FEATURE_LABELS_KM.get(x, x),
                    key="km_feat_box"
                )

            with col_feat_box:
                st.subheader(f"Distribution: {FEATURE_LABELS_KM.get(selected_feat, selected_feat)}")
                fig_box = px.box(
                    km_results, x='cluster_label', y=selected_feat,
                    color='cluster_label', color_discrete_map=CLUSTER_COLORS,
                    labels={'cluster_label': 'Cluster', selected_feat: FEATURE_LABELS_KM.get(selected_feat, selected_feat)},
                    points="outliers", height=380
                )
                fig_box.update_layout(showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)

            if km_feat_imp is not None:
                st.markdown("---")
                st.subheader("🔍 Feature Importance (PCA Loadings)")
                fi = km_feat_imp.copy()
                fi['feature_label'] = fi['feature'].map(FEATURE_LABELS_KM)
                fi = fi.sort_values('importance', ascending=True).tail(10)
                fig_imp = px.bar(fi, x='importance', y='feature_label', orientation='h',
                                  color='importance', color_continuous_scale='Blues',
                                  labels={'importance': 'Importance', 'feature_label': 'Feature'},
                                  title=_t("Top 10 Features (PCA Loading Gewicht)", "Top 10 Features (PCA Loading Weight)"), height=380)
                fig_imp.update_layout(showlegend=False)
                st.plotly_chart(fig_imp, use_container_width=True)

            # Bar-Vergleich alle Cluster
            st.markdown("---")
            st.subheader(_t("Cluster Vergleich", "Cluster Comparison"))
            key_features = ['median_resolution_days', 'resolution_rate', 'pct_fast_resolved', 'pct_reopened', 'tickets_per_month']
            sel_feat2 = st.selectbox(_t("Feature für Balkendiagramm:", "Feature for bar chart:"),
                                      options=[c for c in key_features if c in km_profiles.columns],
                                      format_func=lambda x: FEATURE_LABELS_KM.get(x, x),
                                      key="km_bar_feat")
            if sel_feat2 in km_profiles.columns:
                bar_data = km_profiles[['cluster_label', sel_feat2]].sort_values(sel_feat2, ascending=False)
                fig_bar2 = px.bar(bar_data, x='cluster_label', y=sel_feat2,
                                   color='cluster_label', color_discrete_map=CLUSTER_COLORS,
                                   text_auto='.3f', height=340,
                                   labels={'cluster_label': 'Cluster', sel_feat2: FEATURE_LABELS_KM.get(sel_feat2, sel_feat2)})
                fig_bar2.update_layout(showlegend=False)
                st.plotly_chart(fig_bar2, use_container_width=True)

        # ──── KM TAB 3: EMPLOYEE PROFILES
        with km_tab3:
            st.subheader("👥 " + _t("Mitarbeiter-Profil Lookup", "Employee Profile Lookup"))
            col_srch, col_inf = st.columns([1, 2])
            with col_srch:
                all_assignees = sorted(km_results['issue_assignee'].astype(str).unique())
                sel_emp = st.selectbox(_t("Mitarbeiter auswählen:", "Select employee:"), options=[""] + all_assignees, key="km_emp_sel")
                manual_id = st.text_input(_t("Oder ID eingeben:", "Or enter ID:"), key="km_manual_id")
                if manual_id:
                    sel_emp = manual_id

            if sel_emp and str(sel_emp) in km_results['issue_assignee'].astype(str).values:
                emp = km_results[km_results['issue_assignee'].astype(str) == str(sel_emp)].iloc[0]
                clabel = emp['cluster_label']
                ccolor = CLUSTER_COLORS.get(clabel, "#999")

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,{ccolor}22,{ccolor}11);
                            border-left:4px solid {ccolor};padding:16px;border-radius:8px;margin:12px 0">
                    <h3 style="margin:0;color:{ccolor}">🆔 {sel_emp}</h3>
                    <p style="margin:4px 0;font-size:16px"><b>Cluster: {clabel}</b></p>
                </div>""", unsafe_allow_html=True)

                # Ranking
                all_ranked = km_results.sort_values('median_resolution_days')
                rank = (all_ranked['issue_assignee'].astype(str) == str(sel_emp)).argmax() + 1
                st.markdown(f"**" + _t("Ranking", "Ranking") + f"** (" + _t("nach Bearbeitungszeit", "by processing time") + f"): **#{rank}** " + _t("von", "of") + f" {len(km_results)} " + _t("Mitarbeitern", "Employees"))

                col_m, col_r = st.columns([1, 2])
                with col_m:
                    st.subheader("📋 " + _t("Kennzahlen", "Key Metrics"))
                    kms = [('total_tickets', '🎫 Total Tickets', '{:.0f}'),
                           ('tickets_per_month', '📅 ' + _t('Tickets/Monat', 'Tickets/Month'), '{:.1f}'),
                           ('median_resolution_days', '⏱ Med. Resolution', '{:.2f} ' + _t('Tage', 'Days')),
                           ('resolution_rate', '✅ Resolution Rate', '{:.1%}'),
                           ('pct_fast_resolved', '⚡ Fast Resolved', '{:.1%}'),
                           ('pct_reopened', '🔄 ' + _t('Wiedereröffnet', 'Reopened'), '{:.1%}'),
                           ('avg_priority', '🎯 ' + _t('Avg Priorität', 'Avg Priority'), '{:.2f}')]
                    for col_n, label, fmt in kms:
                        if col_n in emp.index:
                            try:
                                st.metric(label, fmt.format(emp[col_n]))
                            except:
                                st.metric(label, str(emp[col_n]))

                with col_r:
                    st.subheader("🕸 Radar Chart: " + _t("Mitarbeiter vs. Cluster-Durchschnitt", "Employee vs. Cluster Average"))
                    radar_feats = [f for f in ['pct_fast_resolved', 'resolution_rate', 'pct_sole_resolver',
                                               'avg_priority', 'pct_high_priority', 'tickets_per_month',
                                               'avg_processing_steps'] if f in km_results.columns]
                    radar_lbls = [FEATURE_LABELS_KM.get(f, f) for f in radar_feats]
                    clust_avg = km_profiles[km_profiles['cluster_label'] == clabel][radar_feats]
                    clust_avg = clust_avg.iloc[0] if len(clust_avg) else km_profiles[radar_feats].mean()
                    gmin = km_results[radar_feats].min()
                    gmax = km_results[radar_feats].max()

                    def norm_v(v, mn, mx):
                        return max(0, min(1, (v - mn) / (mx - mn))) if mx != mn else 0.5

                    emp_n = [norm_v(emp.get(f, 0), gmin[f], gmax[f]) for f in radar_feats]
                    cl_n = [norm_v(clust_avg.get(f, 0), gmin[f], gmax[f]) for f in radar_feats]

                    fig_rad = go.Figure()
                    fig_rad.add_trace(go.Scatterpolar(
                        r=cl_n + [cl_n[0]], theta=radar_lbls + [radar_lbls[0]],
                        fill='toself', name=f'Cluster Ø ({clabel})',
                        line_color=ccolor, fillcolor=hex_to_rgba(ccolor, 0.2), line_width=2
                    ))
                    fig_rad.add_trace(go.Scatterpolar(
                        r=emp_n + [emp_n[0]], theta=radar_lbls + [radar_lbls[0]],
                        fill='toself', name=_t(f'Mitarbeiter {sel_emp}', f'Employee {sel_emp}'),
                        line_color='#3498db', fillcolor=hex_to_rgba('#3498db', 0.2), line_width=2
                    ))
                    fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                                          height=420, showlegend=True)
                    st.plotly_chart(fig_rad, use_container_width=True)

                with st.expander("📊 " + _t("Alle Features", "All Features")):
                    feat_avail = [f for f in FEATURE_COLS_KM if f in emp.index]
                    emp_df = emp[feat_avail].to_frame(_t('Wert', 'Value'))
                    emp_df.index = [FEATURE_LABELS_KM.get(i, i) for i in emp_df.index]
                    clp = km_profiles[km_profiles['cluster_label'] == clabel][feat_avail]
                    if len(clp):
                        emp_df[_t('Cluster Ø', 'Cluster Avg')] = clp.iloc[0].values
                    st.dataframe(emp_df.round(4), use_container_width=True)

            elif sel_emp:
                st.warning(_t(f"Mitarbeiter '{sel_emp}' nicht gefunden (min. 5 Tickets erforderlich).",
                              f"Employee '{sel_emp}' not found (min. 5 tickets required)."))

        # ──── KM TAB 4: CLUSTER DETAILS
        with km_tab4:
            st.subheader("📋 " + _t("Cluster Details", "Cluster Details"))
            avail_clusters = sorted(km_results['cluster_label'].unique())
            sel_clust = st.selectbox(_t("Cluster auswählen:", "Select cluster:"), avail_clusters, key="km_clust_sel")
            clust_data = km_results[km_results['cluster_label'] == sel_clust]
            clust_prof = km_profiles[km_profiles['cluster_label'] == sel_clust]
            cc = CLUSTER_COLORS.get(sel_clust, "#999")

            st.markdown(f"""
            <div style="background:{cc}22;border-left:4px solid {cc};padding:12px 16px;border-radius:8px;margin:8px 0 16px 0">
                <h3 style="margin:0;color:{cc}">{sel_clust}</h3>
                <p style="margin:4px 0">{len(clust_data)} {_t("Mitarbeiter", "Employees")} ({len(clust_data)/len(km_results)*100:.1f}% {_t("gesamt", "total")})</p>
            </div>""", unsafe_allow_html=True)

            if len(clust_prof):
                p = clust_prof.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                if 'median_resolution_days' in p: c1.metric("⏱ Med. Resolution", f"{p['median_resolution_days']:.2f} " + _t("Tage", "Days"))
                if 'resolution_rate' in p: c2.metric("✅ Resolution Rate", f"{p['resolution_rate']:.1%}")
                if 'pct_fast_resolved' in p: c3.metric("⚡ % Fast Resolved", f"{p['pct_fast_resolved']:.1%}")
                if 'tickets_per_month' in p: c4.metric("📅 " + _t("Med. Tickets/Monat", "Med. Tickets/Month"), f"{clust_data['tickets_per_month'].median():.1f}")

            st.markdown("---")
            # Radar alle Cluster
            st.subheader("🕸 " + _t("Cluster Feature Profile (alle Cluster)", "Cluster Feature Profile (all Clusters)"))
            radar_feats2 = [f for f in ['pct_fast_resolved', 'resolution_rate', 'tickets_per_month',
                                         'avg_priority', 'pct_high_priority', 'avg_processing_steps',
                                         'n_distinct_projects', 'pct_sole_resolver'] if f in km_results.columns]
            radar_lbls2 = [FEATURE_LABELS_KM.get(f, f) for f in radar_feats2]
            gmin2 = km_results[radar_feats2].min()
            gmax2 = km_results[radar_feats2].max()

            fig_clust_rad = go.Figure()
            for lbl, color in CLUSTER_COLORS.items():
                if lbl not in km_results['cluster_label'].values: continue
                pr = km_profiles[km_profiles['cluster_label'] == lbl]
                if not len(pr): continue
                pr = pr.iloc[0]
                vals = [pr.get(f, 0) for f in radar_feats2]
                nvals = [max(0, min(1, (v - gmin2[f]) / max(gmax2[f] - gmin2[f], 1e-9))) for v, f in zip(vals, radar_feats2)]
                is_sel = lbl == sel_clust
                fig_clust_rad.add_trace(go.Scatterpolar(
                    r=nvals + [nvals[0]], theta=radar_lbls2 + [radar_lbls2[0]],
                    fill='toself' if is_sel else None, name=lbl,
                    line_color=color, fillcolor=hex_to_rgba(color, 0.25) if is_sel else 'rgba(0,0,0,0)',
                    line_width=3 if is_sel else 1.5, opacity=1 if is_sel else 0.5
                ))
            fig_clust_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                                         height=420, showlegend=True)
            st.plotly_chart(fig_clust_rad, use_container_width=True)

            # Mitarbeiter-Tabelle
            st.markdown("---")
            st.subheader("👥 " + _t(f"Alle Mitarbeiter in: {sel_clust}", f"All Employees in: {sel_clust}"))
            tbl_cols = [c for c in ['issue_assignee', 'total_tickets', 'tickets_per_month',
                                     'median_resolution_days', 'resolution_rate', 'pct_fast_resolved',
                                     'pct_reopened', 'avg_priority'] if c in clust_data.columns]
            tbl_df = clust_data[tbl_cols].copy()
            tbl_df.columns = [_t('Mitarbeiter ID', 'Employee ID'), 'Tickets',
                               _t('Tickets/Monat', 'Tickets/Month'), 'Med. Resolution (d)',
                               'Resolution Rate', '% Fast Resolved',
                               _t('% Wiedereröffnet', '% Reopened'), _t('Avg Priorität', 'Avg Priority')][:len(tbl_cols)]

            sort_col_km = st.selectbox(_t("Sortieren nach:", "Sort by:"), tbl_df.columns[1:], key="km_sort")
            sort_asc_km = st.checkbox(_t("Aufsteigend", "Ascending"), value=True, key="km_sort_asc")
            tbl_df = tbl_df.sort_values(sort_col_km, ascending=sort_asc_km)

            csv_dl = clust_data.to_csv(index=False)
            st.download_button(_t(f"⬇️ {sel_clust} als CSV", f"⬇️ {sel_clust} as CSV"),
                               data=csv_dl,
                               file_name=f"kmeans_{sel_clust.split()[0].lower()}.csv",
                               mime="text/csv")

            fmt_dict = {}
            for c in tbl_df.columns:
                if 'Rate' in c or '%' in c: fmt_dict[c] = '{:.1%}'
                elif '(d)' in c: fmt_dict[c] = '{:.2f}'
                elif 'Priorität' in c or 'Priority' in c: fmt_dict[c] = '{:.2f}'
                elif 'Monat' in c or 'Month' in c: fmt_dict[c] = '{:.1f}'

            st.dataframe(tbl_df.style.format(fmt_dict), use_container_width=True, hide_index=True, height=380)

        # ──── KM TAB 5: VALIDATION
        with km_tab5:
            st.subheader("✅ Validation & Benchmarking")

            if 'cluster_agg' in km_results.columns and 'cluster_dbscan' in km_results.columns:
                st.markdown("#### " + _t("Clustering-Methoden Vergleich", "Clustering Methods Comparison"))
                c1, c2, c3 = st.columns(3)
                count_label = _t("Anzahl", "Count")
                with c1:
                    st.markdown("**K-Means**")
                    st.dataframe(km_results['cluster_label'].value_counts().reset_index().rename(
                        columns={'cluster_label': 'Cluster', 'count': count_label}), hide_index=True)
                with c2:
                    st.markdown("**Agglomerative**")
                    st.dataframe(km_results['cluster_agg'].value_counts().reset_index().rename(
                        columns={'cluster_agg': 'Cluster', 'count': count_label}), hide_index=True)
                with c3:
                    st.markdown("**DBSCAN**")
                    db_vc = km_results['cluster_dbscan'].value_counts().reset_index()
                    db_vc.columns = ['Cluster', count_label]
                    db_vc['Cluster'] = db_vc['Cluster'].apply(lambda x: 'Noise' if x == -1 else f'Cluster {int(x)}')
                    st.dataframe(db_vc, hide_index=True)

                st.markdown("#### " + _t("Kreuztabelle: K-Means vs. Agglomerative", "Cross Table: K-Means vs. Agglomerative"))
                ct = pd.crosstab(km_results['cluster_label'], km_results['cluster_agg'],
                                  rownames=['K-Means'], colnames=['Agglomerative'])
                st.dataframe(ct, use_container_width=True)
            else:
                st.info(_t("Vergleichsdaten (cluster_agg, cluster_dbscan) nicht verfügbar.",
                           "Comparison data (cluster_agg, cluster_dbscan) not available."))

            st.markdown("---")
            st.markdown("#### 📊 " + _t("Ergebnis-Zusammenfassung", "Results Summary"))
            if st.session_state.get('language', 'en') == 'de':
                st.markdown("""
| Metrik | Wert |
|--------|------|
| Algorithmus | K-Means |
| Optimales k | **4 Cluster** |
| Silhouette Score (k=4) | **0.5807** |
| Bester Silhouette (k=2) | 0.7652 (trivial) |
| Datenbasis | 90.963 Tickets, 302 Mitarbeiter |
| Top Feature | `resolution_rate` (55.75%) |
| Verarbeitungszeitraum | 2016–heute |
                """)
            else:
                st.markdown("""
| Metric | Value |
|--------|-------|
| Algorithm | K-Means |
| Optimal k | **4 Clusters** |
| Silhouette Score (k=4) | **0.5807** |
| Best Silhouette (k=2) | 0.7652 (trivial) |
| Data basis | 90,963 Tickets, 302 Employees |
| Top Feature | `resolution_rate` (55.75%) |
| Time period | 2016–present |
                """)

        # ──── KM TAB 6: OUTLIER ANALYSIS
        with km_tab6:
            st.subheader("⚠️ " + _t("Outlier Analyse", "Outlier Analysis"))
            st.markdown(_t(
                "Erkennung statistischer Ausreißer mittels Z-Score (pro Feature) "
                "und Mahalanobis-Distanz (multivariat).",
                "Detection of statistical outliers using Z-Score (per feature) "
                "and Mahalanobis distance (multivariate)."
            ))

            outlier_df = load_kmeans_outliers()

            if outlier_df is None:
                st.warning(_t("Outlier-Daten nicht gefunden.", "Outlier data not found."))
                st.code("python src/unsuper_clustering.py")
            else:
                n_z   = int(outlier_df['is_outlier_z'].sum())
                n_mah = int(outlier_df['is_outlier_mah'].sum())
                n_both = int((outlier_df['is_outlier_z'] & outlier_df['is_outlier_mah']).sum())
                n_any  = int((outlier_df['is_outlier_z'] | outlier_df['is_outlier_mah']).sum())
                n_total_ol = len(outlier_df)

                # ── KPI row ───────────────────────────────────────────
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("👥 " + _t("Mitarbeiter", "Employees"), n_total_ol)
                c2.metric("📏 Z-Score Outlier", n_z,
                          delta=f"{n_z/n_total_ol*100:.1f}%", delta_color="inverse")
                c3.metric("📐 Mahalanobis Outlier", n_mah,
                          delta=f"{n_mah/n_total_ol*100:.1f}%", delta_color="inverse")
                c4.metric(_t("⚠️ Beide Methoden", "⚠️ Both Methods"), n_both,
                          delta_color="off")
                c5.metric(_t("🔍 Gesamt (mind. 1)", "🔍 Total (at least 1)"), n_any,
                          delta=f"{n_any/n_total_ol*100:.1f}%", delta_color="inverse")

                st.markdown("---")

                # ── Scatter: Mahalanobis vs Z-Score ──────────────────
                st.subheader("🔍 " + _t("Ausreißer-Map: Z-Score vs Mahalanobis", "Outlier Map: Z-Score vs Mahalanobis"))

                def get_ol_status(row):
                    if row['is_outlier_z'] and row['is_outlier_mah']:
                        return _t("⚠️ Beide", "⚠️ Both")
                    elif row['is_outlier_z']:
                        return "Z-Score"
                    elif row['is_outlier_mah']:
                        return "Mahalanobis"
                    else:
                        return _t("✅ Normal", "✅ Normal")

                outlier_df['ol_status'] = outlier_df.apply(get_ol_status, axis=1)

                ol_color_map = {
                    _t("⚠️ Beide", "⚠️ Both"):   "#e74c3c",
                    "Z-Score":                    "#f39c12",
                    "Mahalanobis":                "#9b59b6",
                    _t("✅ Normal", "✅ Normal"): "#2ecc71",
                }

                fig_ol_sc = go.Figure()
                for status, color in ol_color_map.items():
                    sub = outlier_df[outlier_df['ol_status'] == status]
                    if sub.empty:
                        continue
                    cluster_col = sub['cluster_label'] if 'cluster_label' in sub.columns else ['—'] * len(sub)
                    fig_ol_sc.add_trace(go.Scatter(
                        x=sub['z_max'],
                        y=sub['mahalanobis'],
                        mode='markers',
                        name=status,
                        marker=dict(size=9, color=color, opacity=0.8,
                                    line=dict(width=1, color='white')),
                        text=sub['issue_assignee'],
                        customdata=np.column_stack([
                            sub['cluster_label'] if 'cluster_label' in sub.columns else ['—'] * len(sub),
                            sub['z_feature'],
                            sub['total_tickets'],
                        ]),
                        hovertemplate=(
                            '<b>%{text}</b><br>'
                            'Z-Score Max: %{x:.2f}<br>'
                            'Mahalanobis: %{y:.2f}<br>'
                            'Cluster: %{customdata[0]}<br>'
                            'Kritisches Feature: %{customdata[1]}<br>'
                            'Tickets: %{customdata[2]}'
                            '<extra></extra>'
                        )
                    ))

                # Thresholds
                fig_ol_sc.add_vline(x=3.0, line_dash="dash", line_color="orange",
                                     annotation_text="Z=3.0 " + _t("Schwelle", "Threshold"))
                fig_ol_sc.add_hline(y=7.815, line_dash="dash", line_color="purple",
                                     annotation_text="Mah.=7.81 (χ²,p=0.05)")
                fig_ol_sc.update_layout(
                    xaxis_title=_t("Z-Score Max (höchster Feature-Z-Score)", "Z-Score Max (highest feature Z-score)"),
                    yaxis_title="Mahalanobis Distanz",
                    height=480,
                    legend=dict(orientation='h', yanchor='bottom', y=1.02)
                )
                st.plotly_chart(fig_ol_sc, use_container_width=True)
                st.caption(_t(
                    "🟡 Z-Score Outlier: max. Feature-Z > 3 | 🟣 Mahalanobis: χ²-Test p<0.05 (df=17) | "
                    "🔴 Beide: von beiden Methoden erkannt",
                    "🟡 Z-Score Outlier: max feature Z > 3 | 🟣 Mahalanobis: χ²-test p<0.05 (df=17) | "
                    "🔴 Both: detected by both methods"
                ))

                st.markdown("---")

                # ── Per-Cluster Outlier Distribution ─────────────────
                col_cl, col_feat = st.columns(2)

                with col_cl:
                    st.subheader("📊 " + _t("Ausreißer pro Cluster", "Outliers per Cluster"))
                    if 'cluster_label' in outlier_df.columns:
                        cluster_ol = outlier_df.groupby('cluster_label').agg(
                            total=('issue_assignee', 'count'),
                            z_outliers=('is_outlier_z', 'sum'),
                            mah_outliers=('is_outlier_mah', 'sum'),
                        ).reset_index()
                        cluster_ol['z_pct'] = cluster_ol['z_outliers'] / cluster_ol['total']
                        cluster_ol['mah_pct'] = cluster_ol['mah_outliers'] / cluster_ol['total']

                        fig_cl_ol = go.Figure()
                        fig_cl_ol.add_trace(go.Bar(
                            name='Z-Score',
                            x=cluster_ol['cluster_label'],
                            y=cluster_ol['z_pct'],
                            marker_color='#f39c12',
                            text=(cluster_ol['z_pct'] * 100).round(1).astype(str) + '%',
                            textposition='outside'
                        ))
                        fig_cl_ol.add_trace(go.Bar(
                            name='Mahalanobis',
                            x=cluster_ol['cluster_label'],
                            y=cluster_ol['mah_pct'],
                            marker_color='#9b59b6',
                            text=(cluster_ol['mah_pct'] * 100).round(1).astype(str) + '%',
                            textposition='outside'
                        ))
                        fig_cl_ol.update_layout(
                            barmode='group',
                            yaxis=dict(title=_t("Anteil Ausreißer", "Outlier Rate"),
                                       tickformat='.0%'),
                            height=380, showlegend=True,
                            legend=dict(orientation='h', yanchor='bottom', y=1.02)
                        )
                        st.plotly_chart(fig_cl_ol, use_container_width=True)

                with col_feat:
                    st.subheader("🏷️ " + _t("Kritische Features (Z-Score)", "Critical Features (Z-Score)"))
                    feat_counts = outlier_df[outlier_df['is_outlier_z']]['z_feature'].value_counts().reset_index()
                    feat_counts.columns = ['Feature', _t('Anzahl Outlier', 'Outlier Count')]
                    feat_counts['Feature'] = feat_counts['Feature'].map(
                        lambda x: FEATURE_LABELS_KM.get(x, x)
                    )
                    fig_feat_ol = px.bar(
                        feat_counts, x=_t('Anzahl Outlier', 'Outlier Count'), y='Feature',
                        orientation='h',
                        color=_t('Anzahl Outlier', 'Outlier Count'),
                        color_continuous_scale='Reds',
                        title=_t("Welches Feature ist am häufigsten auffällig?",
                                 "Which feature is most frequently extreme?"),
                        height=380
                    )
                    fig_feat_ol.update_layout(showlegend=False,
                                               yaxis=dict(categoryorder='total ascending'))
                    st.plotly_chart(fig_feat_ol, use_container_width=True)

                st.markdown("---")

                # ── Outlier Table ─────────────────────────────────────
                st.subheader("📋 " + _t("Ausreißer-Tabelle", "Outlier Table"))
                filter_ol = st.selectbox(
                    _t("Filtern nach:", "Filter by:"),
                    options=[
                        _t("Alle Ausreißer", "All Outliers"),
                        _t("Beide Methoden", "Both Methods"),
                        "Z-Score only",
                        "Mahalanobis only",
                        _t("Alle Mitarbeiter", "All Employees"),
                    ],
                    key="ol_filter"
                )

                if filter_ol == _t("Alle Ausreißer", "All Outliers"):
                    df_show = outlier_df[outlier_df['is_outlier_z'] | outlier_df['is_outlier_mah']]
                elif filter_ol == _t("Beide Methoden", "Both Methods"):
                    df_show = outlier_df[outlier_df['is_outlier_z'] & outlier_df['is_outlier_mah']]
                elif filter_ol == "Z-Score only":
                    df_show = outlier_df[outlier_df['is_outlier_z'] & ~outlier_df['is_outlier_mah']]
                elif filter_ol == "Mahalanobis only":
                    df_show = outlier_df[~outlier_df['is_outlier_z'] & outlier_df['is_outlier_mah']]
                else:
                    df_show = outlier_df

                disp_cols_ol = [c for c in [
                    'issue_assignee', 'cluster_label', 'z_max', 'z_feature',
                    'mahalanobis', 'is_outlier_z', 'is_outlier_mah',
                    'total_tickets', 'median_resolution_days', 'resolution_rate'
                ] if c in df_show.columns]

                rename_ol = {
                    'issue_assignee':        _t('Mitarbeiter', 'Employee'),
                    'cluster_label':         'Cluster',
                    'z_max':                 'Z-Score Max',
                    'z_feature':             _t('Krit. Feature', 'Crit. Feature'),
                    'mahalanobis':           'Mahalanobis',
                    'is_outlier_z':          'Z Outlier',
                    'is_outlier_mah':        'Mah Outlier',
                    'total_tickets':         'Tickets',
                    'median_resolution_days': 'Med. Resolution (d)',
                    'resolution_rate':       'Resolution Rate',
                }
                df_show_disp = df_show[disp_cols_ol].rename(columns=rename_ol).sort_values(
                    'Mahalanobis' if 'Mahalanobis' in df_show.rename(columns=rename_ol).columns
                    else _t('Mitarbeiter', 'Employee'),
                    ascending=False
                )

                st.dataframe(
                    df_show_disp,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'Z-Score Max': st.column_config.NumberColumn(format="%.2f", width="small"),
                        'Mahalanobis': st.column_config.ProgressColumn(
                            min_value=0, max_value=float(outlier_df['mahalanobis'].max()),
                            format="%.2f", width="medium"
                        ),
                        'Z Outlier':   st.column_config.CheckboxColumn(width="small"),
                        'Mah Outlier': st.column_config.CheckboxColumn(width="small"),
                        'Resolution Rate': st.column_config.NumberColumn(format="%.0%", width="small"),
                        'Med. Resolution (d)': st.column_config.NumberColumn(format="%.1f", width="small"),
                    }
                )

                st.markdown("---")
                st.caption(_t(
                    "💡 Z-Score > 3.0 = statistisch auffällig in mind. einem Feature | "
                    "Mahalanobis > 7.81 = multivariat auffällig (Chi²-Test, df=17, p<0.05) | "
                    "Ausreißer können auf fehlerhafte Daten, außergewöhnliche Arbeitsmuster oder "
                    "Spezialrollen hinweisen.",
                    "💡 Z-Score > 3.0 = statistically extreme in at least one feature | "
                    "Mahalanobis > 7.81 = multivariate outlier (Chi²-test, df=17, p<0.05) | "
                    "Outliers may indicate data errors, unusual work patterns, or specialist roles."
                ))

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:#888;font-size:12px'>"
            f"🎯 K-Means Performance Clustering | {n_emp_km} " + _t("Mitarbeiter", "Employees") + f" | {n_clust_km} " + _t("Cluster", "Clusters") +
            "</div>", unsafe_allow_html=True
        )

render_footer()
