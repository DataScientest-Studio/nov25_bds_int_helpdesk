"""
I/O-Dokumentation — Inputs/Outputs aller Module und ML-Hyperparameter
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, init_session_state, e, maybe_emoji
)

st.set_page_config(page_title="I/O Dokumentation", page_icon="📋", layout="wide")

init_session_state()
render_settings_sidebar()

lang = st.session_state.get('language', 'de')

# ── Lokale Texte ─────────────────────────────────────────────────────────────
TEXTS = {
    'de': {
        'title': '📋 I/O-Dokumentation',
        'subtitle': 'Inputs, Outputs und Hyperparameter aller Pipeline-Komponenten',
        'sec_models': '🤖 ML-Modell Hyperparameter',
        'module': 'Modul', 'inputs': 'Inputs', 'outputs': 'Ausgaben', 'desc': 'Beschreibung',
        'model_name': 'Modell', 'component': 'Komponente', 'param': 'Parameter', 'value': 'Wert',
        'note_optimized': '⚡ **optimized_scorer.joblib** — Durch Optuna-Hyperparameter-Suche optimiertes Modell (kein RandomForest, nur XGB+LGB)',
        'note_perf': '**q_score_model.joblib** — Basis-Ensemble (RF+XGB+LGB)',
        'note_o': '**o_score_model.joblib** — Trainiert auf O-Score-Klassen 1–5 (7 aggregierte Features)',
    },
    'en': {
        'title': '📋 I/O Documentation',
        'subtitle': 'Inputs, outputs and hyperparameters of all pipeline components',
        'sec_models': '🤖 ML Model Hyperparameters',
        'module': 'Module', 'inputs': 'Inputs', 'outputs': 'Outputs', 'desc': 'Description',
        'model_name': 'Model', 'component': 'Component', 'param': 'Parameter', 'value': 'Value',
        'note_optimized': '⚡ **optimized_scorer.joblib** — Optuna-optimized model (no RandomForest, XGB+LGB only)',
        'note_perf': '**q_score_model.joblib** — Base ensemble (RF+XGB+LGB)',
        'note_o': '**o_score_model.joblib** — Trained on O-Score classes 1–5 (7 aggregated features)',
    },
}
T = TEXTS.get(lang, TEXTS['de'])

# ── Header ───────────────────────────────────────────────────────────────────
page_header(T['title'], T['subtitle'])

# ── 2. ML-Hyperparameter ──────────────────────────────────────────────────────
section_header(T['sec_models'])

# ── 2a. optimized_scorer.joblib ──────────────────────────────────────────────
st.markdown("### ⚡ optimized_scorer.joblib")
st.info(T['note_optimized'])

st.markdown("**Architektur:** VotingClassifier (soft voting) — Nur XGB + LGB (kein RandomForest), je ein Modell pro Target (Q1, Q2, Q3)")

tabs_opt = st.tabs(["Q1", "Q2", "Q3"])

opt_params = {
    'Q1': {
        'XGBClassifier': {
            'n_estimators': 81, 'max_depth': 6, 'learning_rate': 0.1250, 'subsample': 0.8283,
            'colsample_bytree': 0.9481, 'random_state': 42, 'verbosity': 0,
            'objective': 'multi:softmax', 'num_class': 5, 'eval_metric': None,
        },
        'LGBMClassifier': {
            'n_estimators': 76, 'max_depth': 4, 'learning_rate': 0.1302, 'num_leaves': 51,
            'random_state': 42, 'verbose': -1, 'boosting_type': 'gbdt',
            'colsample_bytree': 1.0, 'min_child_samples': 20, 'subsample': 1.0,
            'reg_alpha': 0.0, 'reg_lambda': 0.0,
        },
    },
    'Q2': {
        'XGBClassifier': {
            'n_estimators': 113, 'max_depth': 5, 'learning_rate': 0.1556, 'subsample': 0.7008,
            'colsample_bytree': 0.9378, 'random_state': 42, 'verbosity': 0,
            'objective': 'multi:softmax', 'num_class': 5, 'eval_metric': None,
        },
        'LGBMClassifier': {
            'n_estimators': 178, 'max_depth': 6, 'learning_rate': 0.1149, 'num_leaves': 51,
            'random_state': 42, 'verbose': -1, 'boosting_type': 'gbdt',
            'colsample_bytree': 1.0, 'min_child_samples': 20, 'subsample': 1.0,
            'reg_alpha': 0.0, 'reg_lambda': 0.0,
        },
    },
    'Q3': {
        'XGBClassifier': {
            'n_estimators': 153, 'max_depth': 3, 'learning_rate': 0.0825, 'subsample': 0.8757,
            'colsample_bytree': 0.7487, 'random_state': 42, 'verbosity': 0,
            'objective': 'multi:softmax', 'num_class': 5, 'eval_metric': None,
        },
        'LGBMClassifier': {
            'n_estimators': 122, 'max_depth': 4, 'learning_rate': 0.0570, 'num_leaves': 58,
            'random_state': 42, 'verbose': -1, 'boosting_type': 'gbdt',
            'colsample_bytree': 1.0, 'min_child_samples': 20, 'subsample': 1.0,
            'reg_alpha': 0.0, 'reg_lambda': 0.0,
        },
    },
}

for tab, q in zip(tabs_opt, ['Q1', 'Q2', 'Q3']):
    with tab:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**XGBClassifier**")
            rows = [[p, str(v)] for p, v in opt_params[q]['XGBClassifier'].items()]
            st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                         use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**LGBMClassifier**")
            rows = [[p, str(v)] for p, v in opt_params[q]['LGBMClassifier'].items()]
            st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                         use_container_width=True, hide_index=True)

# Scaler
st.markdown("**Scaler:** `RobustScaler(copy=True, quantile_range=(25.0, 75.0), unit_variance=False, with_centering=True, with_scaling=True)`")
st.markdown("**Feature-Spalten (17):** `contributors, turn_no, spent hours, steps, comments count, spent_hours, steps_count, comments_count, priority_numeric, type_Deployment, type_HD Service, type_Ticket, is_multi_assignee, is_first_turn, assignee_avg_time, assignee_std_time, assignee_ticket_count`")
st.caption("⚠️ Hinweis: Das Modell enthält sowohl Leerzeichen- als auch Unterstrich-Varianten desselben Features ('spent hours'/'spent_hours', 'comments count'/'comments_count', 'steps'/'steps_count'), da beide Schreibweisen beim Training im Datensatz vorhanden waren. Beide Spalten werden beim Inference benötigt." if lang == 'de' else "⚠️ Note: The model contains both space-separated and underscore-separated variants of the same feature ('spent hours'/'spent_hours', 'comments count'/'comments_count', 'steps'/'steps_count'), as both naming conventions were present in the training dataset. Both columns are required during inference.")

st.markdown("---")

# ── 2b. q_score_model.joblib ─────────────────────────────────────────────────
st.markdown("### 📊 q_score_model.joblib — Q-Score (Manager Rating)")
st.markdown("**Architektur:** VotingClassifier (soft voting) — RF + XGB + LGB, je ein Modell pro Target (Q1, Q2, Q3)")

base_params_rf = {
    'n_estimators': 100, 'max_depth': 6, 'random_state': 42, 'n_jobs': -1,
    'criterion': 'gini', 'max_features': 'sqrt', 'min_samples_split': 2,
    'min_samples_leaf': 1, 'bootstrap': True, 'oob_score': False,
    'warm_start': False, 'class_weight': None, 'ccp_alpha': 0.0,
    'max_leaf_nodes': None, 'min_impurity_decrease': 0.0, 'max_samples': None,
}
base_params_xgb = {
    'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'random_state': 42,
    'verbosity': 0, 'objective': 'binary:logistic', 'colsample_bytree': None,
    'subsample': None, 'reg_alpha': None, 'reg_lambda': None,
    'enable_categorical': False, 'eval_metric': None,
}
base_params_lgb = {
    'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'random_state': 42,
    'verbose': -1, 'boosting_type': 'gbdt', 'num_leaves': 31,
    'colsample_bytree': 1.0, 'min_child_samples': 20, 'subsample': 1.0,
    'reg_alpha': 0.0, 'reg_lambda': 0.0, 'subsample_freq': 0,
    'subsample_for_bin': 200000,
}

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**RandomForestClassifier**")
    rows = [[p, str(v)] for p, v in base_params_rf.items()]
    st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)
with col2:
    st.markdown("**XGBClassifier**")
    rows = [[p, str(v)] for p, v in base_params_xgb.items()]
    st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)
with col3:
    st.markdown("**LGBMClassifier**")
    rows = [[p, str(v)] for p, v in base_params_lgb.items()]
    st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)

st.markdown("**Scaler:** `StandardScaler(copy=True, with_mean=True, with_std=True)`")
st.markdown("**Feature-Spalten (6):** `contributors, turn_no, steps, spent_hours, comments_count, priority_numeric`")
st.markdown("**Trainings-Split:** 80 % Train / 20 % Test, stratifiziert nach Target · 5-Fold Stratified CV")

st.markdown("---")

# ── 2c. o_score_model.joblib ─────────────────────────────────────────────────
st.markdown("### 🎯 o_score_model.joblib — O-Score (Objective Rating)")
st.info(T['note_o'])
st.markdown("**Architektur:** VotingClassifier (soft voting) — RF + XGB + LGB, ein einziges Modell (kein Q1/Q2/Q3-Split)")

o_params_rf = {
    'n_estimators': 100, 'max_depth': 6, 'random_state': 42, 'n_jobs': -1,
    'criterion': 'gini', 'max_features': 'sqrt', 'min_samples_split': 2,
    'min_samples_leaf': 1, 'bootstrap': True, 'oob_score': False,
}
o_params_xgb = {
    'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'random_state': 42,
    'verbosity': 0, 'objective': 'binary:logistic', 'eval_metric': 'mlogloss',
    'use_label_encoder': False, 'colsample_bytree': None, 'subsample': None,
}
o_params_lgb = {
    'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1, 'random_state': 42,
    'verbose': -1, 'boosting_type': 'gbdt', 'num_leaves': 31,
    'colsample_bytree': 1.0, 'min_child_samples': 20, 'subsample': 1.0,
    'reg_alpha': 0.0, 'reg_lambda': 0.0,
}

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**RandomForestClassifier**")
    rows = [[p, str(v)] for p, v in o_params_rf.items()]
    st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)
with col2:
    st.markdown("**XGBClassifier**")
    rows = [[p, str(v)] for p, v in o_params_xgb.items()]
    st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)
with col3:
    st.markdown("**LGBMClassifier**")
    rows = [[p, str(v)] for p, v in o_params_lgb.items()]
    st.dataframe(pd.DataFrame(rows, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)

st.markdown("**Scaler:** `StandardScaler(copy=True, with_mean=True, with_std=True)`")
st.markdown("**Feature-Spalten (7):** `ticket_count, median_time_hours, avg_steps, avg_comments, reopen_rate, first_touch_rate, success_rate`")
st.markdown("**Diskretisierung:** O-Score → Klassen 1–5 via `pd.cut(bins=[0, 1.8, 2.6, 3.4, 4.2, 5.1])`")
st.markdown("**Trainings-Split:** 80 % Train / 20 % Test, stratifiziert · 5-Fold Stratified CV")

st.markdown("---")

# ── 2d. kmeans_model.joblib ──────────────────────────────────────────────────
st.markdown("### 🔬 kmeans_model.joblib — Clustering")
if lang == 'de':
    st.info("**kmeans_model.joblib** — K-Means Clustering auf 302 Mitarbeitern · 17 normalisierte Features · 4 semantische Cluster")
else:
    st.info("**kmeans_model.joblib** — K-Means clustering on 302 employees · 17 normalized features · 4 semantic clusters")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**KMeans**")
    kmeans_params = [
        ['n_clusters', '4'],
        ['n_init', '20'],
        ['random_state', '42'],
        ['init', 'k-means++'],
        ['max_iter', '300'],
        ['tol', '1e-4'],
        ['algorithm', 'lloyd'],
        ['Inertia', '6747.69'],
        ['Silhouette (k=4)', '0.5807'],
    ]
    st.dataframe(pd.DataFrame(kmeans_params, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)

with col2:
    st.markdown("**RobustScaler** (models/scaler.joblib)")
    scaler_params = [
        ['with_centering', 'True'],
        ['with_scaling', 'True'],
        ['quantile_range', '(25.0, 75.0)'],
        ['unit_variance', 'False'],
        ['copy', 'True'],
    ]
    st.dataframe(pd.DataFrame(scaler_params, columns=[T['param'], T['value']]),
                 use_container_width=True, hide_index=True)
    if lang == 'de':
        st.caption("⚠️ Vor dem Skalieren: Winsorisierung auf 99. Perzentil pro Feature (Schutz vor Ausreißern).")
    else:
        st.caption("⚠️ Prior to scaling: winsorizing at the 99th percentile per feature (outlier protection).")

if lang == 'de':
    st.markdown("""
**PCA:** `PCA(n_components=2)` → PC1=54,9% · PC2=23,7% · Gesamt=78,6% erklärte Varianz

**Feature-Spalten (17):**
`median_resolution_days, avg_resolution_days, std_resolution_days, pct_fast_resolved,
total_tickets, tickets_per_month, active_months, avg_priority, pct_high_priority,
n_distinct_projects, n_distinct_categories, pct_reopened, resolution_rate,
avg_comments, pct_sole_resolver, avg_first_response_days, avg_processing_steps`

**Cluster-Ausgabe:**

| Label | Anzahl | resolution_rate | median_resolution_days |
|-------|--------|-----------------|------------------------|
| High Performer 🟢 | 273 (90,4%) | ~98% | ~14 Tage |
| Solid Performer 🟡 | 16 (5,3%) | ~87% | ~45 Tage |
| Specialist ⚫ | 7 (2,3%) | ~17% | ~120 Tage |
| Needs Improvement 🔴 | 6 (2,0%) | ~62% | ~455 Tage |

**Vergleichsalgorithmen:** DBSCAN(eps=1.5, min_samples=5) · AgglomerativeClustering(n_clusters=4, linkage='ward')

**Outlier-Erkennung:**
- Z-Score: Schwellenwert >3,0 pro Feature → 37 Mitarbeiter
- Mahalanobis: χ²-Test, df=17, p<0,05 → 22 Mitarbeiter · 14 in beiden Methoden
    """)
else:
    st.markdown("""
**PCA:** `PCA(n_components=2)` → PC1=54.9% · PC2=23.7% · Total=78.6% explained variance

**Feature columns (17):**
`median_resolution_days, avg_resolution_days, std_resolution_days, pct_fast_resolved,
total_tickets, tickets_per_month, active_months, avg_priority, pct_high_priority,
n_distinct_projects, n_distinct_categories, pct_reopened, resolution_rate,
avg_comments, pct_sole_resolver, avg_first_response_days, avg_processing_steps`

**Cluster output:**

| Label | Count | resolution_rate | median_resolution_days |
|-------|-------|-----------------|------------------------|
| High Performer 🟢 | 273 (90.4%) | ~98% | ~14 days |
| Solid Performer 🟡 | 16 (5.3%) | ~87% | ~45 days |
| Specialist ⚫ | 7 (2.3%) | ~17% | ~120 days |
| Needs Improvement 🔴 | 6 (2.0%) | ~62% | ~455 days |

**Comparison algorithms:** DBSCAN(eps=1.5, min_samples=5) · AgglomerativeClustering(n_clusters=4, linkage='ward')

**Outlier detection:**
- Z-Score: threshold >3.0 per feature → 37 employees
- Mahalanobis: χ²-test, df=17, p<0.05 → 22 employees · 14 flagged by both methods
    """)

render_footer()
