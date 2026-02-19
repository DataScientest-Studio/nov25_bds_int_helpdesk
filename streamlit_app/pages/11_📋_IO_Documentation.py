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
        'sec_io': '🔌 Inputs & Outputs aller Module',
        'sec_models': '🤖 ML-Modell Hyperparameter',
        'sec_metrics': '📊 Trainings-Metriken',
        'sec_features': '📈 Feature Importance',
        'module': 'Modul', 'inputs': 'Inputs', 'outputs': 'Ausgaben', 'desc': 'Beschreibung',
        'model_name': 'Modell', 'component': 'Komponente', 'param': 'Parameter', 'value': 'Wert',
        'metric': 'Metrik', 'q1': 'Q1', 'q2': 'Q2', 'q3': 'Q3', 'rank': 'Rang',
        'feature': 'Feature', 'importance': 'Importance',
        'note_optimized': '⚡ **optimized_scorer.joblib** — Durch Optuna-Hyperparameter-Suche optimiertes Modell (kein RandomForest, nur XGB+LGB)',
        'note_perf': '**performance_scorer.joblib** / **q_score_model.joblib** — Identische Basis-Ensembles (RF+XGB+LGB)',
        'note_o': '**o_score_model.joblib** — Trainiert auf O-Score-Klassen 1–5 (7 aggregierte Features)',
    },
    'en': {
        'title': '📋 I/O Documentation',
        'subtitle': 'Inputs, outputs and hyperparameters of all pipeline components',
        'sec_io': '🔌 Inputs & Outputs of All Modules',
        'sec_models': '🤖 ML Model Hyperparameters',
        'sec_metrics': '📊 Training Metrics',
        'sec_features': '📈 Feature Importance',
        'module': 'Module', 'inputs': 'Inputs', 'outputs': 'Outputs', 'desc': 'Description',
        'model_name': 'Model', 'component': 'Component', 'param': 'Parameter', 'value': 'Value',
        'metric': 'Metric', 'q1': 'Q1', 'q2': 'Q2', 'q3': 'Q3', 'rank': 'Rank',
        'feature': 'Feature', 'importance': 'Importance',
        'note_optimized': '⚡ **optimized_scorer.joblib** — Optuna-optimized model (no RandomForest, XGB+LGB only)',
        'note_perf': '**performance_scorer.joblib** / **q_score_model.joblib** — Identical base ensembles (RF+XGB+LGB)',
        'note_o': '**o_score_model.joblib** — Trained on O-Score classes 1–5 (7 aggregated features)',
    },
}
T = TEXTS.get(lang, TEXTS['de'])

# ── Header ───────────────────────────────────────────────────────────────────
page_header(T['title'], T['subtitle'])

# ── 1. I/O aller Module ───────────────────────────────────────────────────────
section_header(T['sec_io'])

io_data = {
    T['module']: [
        'src/data_loader.py',
        'src/feature_engineering.py',
        'src/ml_model.py',
        'src/ml_model_q.py',
        'src/ml_model_o.py',
        'src/o_score.py',
        'src/bias_analysis.py',
        'src/nlp_analysis.py',
        'src/training_deficits.py',
        'src/process_compliance.py',
        'src/trend_analysis.py',
        'src/dialog_analysis.py',
        'src/generate_plots.py',
        'src/generate_pdf.py',
    ],
    T['inputs']: [
        'data/raw/issues.csv · issues_snapshot.csv · issues_change_history.csv · issues_snapshot_sample.xlsx · sample_utterances.csv | Parameter: data_dir="data/raw"',
        'issues_snapshot_sample.xlsx (scored_df: DataFrame) | Alle Spalten: contributors, turn_no, spent hours, steps, comments count, Q1, Q2, Q3',
        'data/processed/ml_dataset.csv | X: Features-DataFrame, y: Targets (Q1/Q2/Q3) | Parameter: test_size=0.2',
        'data/processed/ml_dataset.csv | X: Features-DataFrame, y: Targets (Q1/Q2/Q3) | Parameter: test_size=0.2',
        'data/processed/o_score_results.csv | o_score_df mit Spalten: ticket_count, median_time_hours, avg_steps, avg_comments, reopen_rate, first_touch_rate, success_rate, o_score | Parameter: test_size=0.2',
        'data/raw/issues_snapshot.csv | snapshot_df | Parameter: min_tickets=10',
        'issues_snapshot_sample.xlsx (scored_df) | score_cols=["Q1","Q2","Q3"] | expected_mean=3.0',
        'data/raw/sample_utterances.csv | Spalten: issueid, actionbody (oder body), author, author_role',
        'issues_snapshot_sample.xlsx | scored_df (Spalten: assignee, Q1, Q2, Q3)',
        'data/raw/issues.csv | Spalten: id + alle wfe_*-Spalten (wfe_reopened, etc.)',
        'issues_snapshot_sample.xlsx | scored_df (Spalten: assignee, Q1, Q2, Q3)',
        'data/raw/sample_utterances.csv | actionbody-Spalte als Textquelle',
        'data/processed/ml_dataset.csv · models/performance_scorer.joblib · data/raw/issues_snapshot_sample.xlsx · data/processed/workflow_analysis.csv',
        'reports/Projektdokumentation_DE.md · reports/Project_Documentation_EN.md · reports/plots/*.png',
    ],
    T['outputs']: [
        'dict: {"issues": DataFrame(66691×58), "snapshots": DataFrame(90963×60), "history": DataFrame(257508×6), "scored": DataFrame(747×19), "utterances": DataFrame(30104×9)}',
        'X (DataFrame: 603×6), y (DataFrame: 603×3 [Q1,Q2,Q3]), feature_cols (list) | data/processed/ml_dataset.csv | data/processed/feature_columns.txt',
        'dict: {models: {Q1,Q2,Q3: VotingClassifier}, scaler: StandardScaler, metrics: {accuracy,kappa,mae,cv_mean,cv_std,confusion_matrix}, feature_importance: {Q1,Q2,Q3: DataFrame}} → models/performance_scorer.joblib',
        'dict: {models, scaler, metrics: {accuracy,mae,f1_macro,f1_weighted,kappa,qwk,cv_mean,cv_std,confusion_matrix}, feature_importance} → models/q_score_model.joblib',
        'dict: {classifier: VotingClassifier, scaler: StandardScaler, feature_cols: list, metrics: {classifier: {...}}, feature_importance: DataFrame, model_type: "o_score"} → models/o_score_model.joblib',
        'data/processed/o_score_results.csv (Spalten: employee, ticket_count, median_time, avg_steps, avg_comments, reopen_rate, first_touch_rate, success_rate, median_time_hours, quality_score, efficiency_score, productivity_score, communication_score, o_score_raw, o_score, o_score_int) · q_vs_o_score_comparison.csv · o_score_risk_classification.csv',
        'dict: {distribution: {Q1,Q2,Q3: {mean,std,median,min,max,count}}, halo_effect: {avg_inter_correlation,is_halo_effect,severity,correlation_matrix}, leniency: {Q1,Q2,Q3: {mean,expected,deviation,bias_type,is_biased}}, central_tendency: {Q1,Q2,Q3: {std,extreme_ratio,is_central_tendency}}, bias_flags: list}',
        'data/processed/nlp_features.csv (Spalten: issueid, sentiment_compound_mean/std/min/max, sentiment_pos_mean, sentiment_neg_mean, word_count_mean/sum, question_count_sum, politeness_score_sum, urgency_score_sum, technical_score_sum, solution_score_sum)',
        'reports/training_report.csv (Spalten: employee, overall_score, ticket_count, risk_level, training_areas, flags, recommendations)',
        'data/processed/workflow_analysis.csv (Spalten: issue_id, total_steps, reopens, backward_steps, compliance_score, is_compliant)',
        'reports/trend_analysis.csv (Spalten: employee, avg_q1, std_q1, ticket_count, avg_q2, avg_q3, overall_score, variance, risk_level)',
        'data/processed/dialog_acts.csv (Spalten: issueid, author, author_role, dialog_act, dialog_act_name, confidence, text_preview)',
        '10 PNG-Dateien in reports/plots/: 01_score_distribution.png … 10_model_metrics.png (je 300 dpi)',
        'reports/Projektdokumentation_DE.html · reports/Projektdokumentation_DE.pdf · reports/Project_Documentation_EN.html · reports/Project_Documentation_EN.pdf',
    ],
    T['desc']: [
        'Lädt alle 5 Rohdatensätze aus data/raw/. Gibt Summary-Dict zurück. Prüft Dateipfade vor dem Laden.',
        'Erstellt numerische Features für das ML-Modell aus dem bewerteten Sample. Filtert Zeilen mit Q>0. Ersetzt NaN durch Median.',
        'Basismodell-Training: RF+XGB+LGB Ensemble (soft voting) für Q1, Q2, Q3. StandardScaler. 80/20 Split + 5-Fold CV.',
        'Wie ml_model.py, aber mit zusätzlichen Metriken: F1 (macro/weighted), QWK (Quadratic Weighted Kappa).',
        'Trainiert einen Ensemble-Classifier auf diskreten O-Score-Klassen 1–5. Verwendet 7 aggregierte Employee-Metriken.',
        'Berechnet datenbasierten Performance-Score pro Mitarbeiter. Gewichtetes Scoring aus 4 Komponenten (Qualität 35%, Effizienz 25%, Produktivität 20%, Kommunikation 20%).',
        'Erkennt Rating-Verzerrungen: Halo-Effekt (Inter-Korrelation >0.8), Leniency (Mean>3.5) / Severity (Mean<2.5), Central Tendency (Std<0.8).',
        'VADER Sentiment-Analyse + Wort-Pattern-Matching für Höflichkeit, Dringlichkeit, Technikalität, Lösungsorientierung. Aggregiert pro Issue.',
        'Bewertet jeden Mitarbeiter nach overall_score (Q1+Q2)/2*0.5 + Q3*0.5. Klassifiziert nach Thresholds in GREEN/YELLOW/RED.',
        'Analysiert Workflow-Compliance via wfe_*-Spalten. Berechnet Compliance-Score aus Reopens (×0.1) und Backward-Steps (×0.05).',
        'Aggregiert Performance-Scores pro Mitarbeiter, berechnet Risk-Levels (GREEN≥3.0, YELLOW≥2.0, RED<2.0), Top/Bottom-Performer.',
        'Regex-basierte Klassifikation von Dialog-Akten in 12 Kategorien. Unterstützt Englisch und Deutsch. Konfidenz-Score 0–1.',
        'Erzeugt 10 matplotlib-Visualisierungen für die Projektdokumentation (Score-Verteilung, Correlation, Employee-Performance, Workflow, Confusion Matrix, Feature Importance, Trend, Risk, Workflow-Diagramm, Model-Vergleich).',
        'Konvertiert Markdown+Bilder zu HTML (mit base64-eingebetteten Bildern) und anschließend zu PDF via WeasyPrint.',
    ],
}

df_io = pd.DataFrame(io_data)
st.dataframe(
    df_io, use_container_width=True, hide_index=True,
    column_config={
        T['module']: st.column_config.TextColumn(width="small"),
        T['inputs']: st.column_config.TextColumn(width="large"),
        T['outputs']: st.column_config.TextColumn(width="large"),
        T['desc']: st.column_config.TextColumn(width="large"),
    }
)

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

st.markdown("---")

# ── 2b. performance_scorer.joblib / q_score_model.joblib ─────────────────────
st.markdown("### 📊 performance_scorer.joblib / q_score_model.joblib (identisch)")
st.info(T['note_perf'])
st.markdown("**Architektur:** VotingClassifier (soft voting) — RF + XGB + LGB, je ein Modell pro Target (Q1, Q2, Q3)")

# Diese beiden Modelle sind identisch
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
st.markdown("### 🎯 o_score_model.joblib")
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

# ── 3. Trainings-Metriken ──────────────────────────────────────────────────────
section_header(T['sec_metrics'])

st.markdown("#### optimized_scorer.joblib")
opt_metrics = pd.DataFrame({
    T['metric']: ['Accuracy', "Cohen's Kappa", 'MAE', 'Weighted F1', 'CV Mean', 'CV Std'],
    T['q1']: ['66.1%', '0.383', '0.595', '0.648', '64.5%', '±2.3%'],
    T['q2']: ['66.9%', '0.379', '0.545', '0.629', '64.0%', '±2.3%'],
    T['q3']: ['75.2%', '0.512', '0.471', '0.732', '65.5%', '±1.8%'],
})
st.dataframe(opt_metrics, use_container_width=True, hide_index=True)

st.markdown("#### performance_scorer.joblib / q_score_model.joblib (identisch)")
base_metrics = pd.DataFrame({
    T['metric']: ['Accuracy', "Cohen's Kappa", 'MAE', 'Macro F1', 'Weighted F1', 'QWK', 'CV Mean', 'CV Std'],
    T['q1']: ['65.3%', '0.337', '0.595', '0.378', '0.615', '0.624', '64.2%', '±2.6%'],
    T['q2']: ['66.1%', '0.339', '0.570', '0.364', '0.613', '0.634', '65.3%', '±2.1%'],
    T['q3']: ['66.1%', '0.363', '0.603', '0.443', '0.649', '0.597', '65.8%', '±2.7%'],
})
st.dataframe(base_metrics, use_container_width=True, hide_index=True)

st.markdown("#### o_score_model.joblib (Klassifikation O-Score 1–5)")
o_metrics_df = pd.DataFrame({
    T['metric']: ['Accuracy', "Cohen's Kappa", 'MAE', 'Macro F1', 'Weighted F1', 'QWK', 'CV Mean', 'CV Std'],
    'O-Score Classifier': ['72.3%', '0.555', '0.298', '0.579', '0.713', '0.749', '80.9%', '±4.7%'],
})
st.dataframe(o_metrics_df, use_container_width=True, hide_index=True)

# ── 4. Feature Importance ──────────────────────────────────────────────────────
section_header(T['sec_features'])

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Q-Score Modelle — RandomForest Feature Importance (Q1)")
    fi_q_df = pd.DataFrame({
        T['rank']: [1, 2, 3, 4, 5, 6],
        T['feature']: ['spent_hours', 'comments_count', 'turn_no', 'steps', 'contributors', 'priority_numeric'],
        T['importance']: ['45.3%', '25.3%', '12.1%', '11.0%', '4.4%', '1.9%'],
    })
    st.dataframe(fi_q_df, use_container_width=True, hide_index=True)

    st.markdown("#### optimized_scorer — Feature Importance (Q1, top 10 von 17)")
    fi_opt_df = pd.DataFrame({
        T['rank']: list(range(1, 11)),
        T['feature']: [
            'spent hours', 'contributors', 'assignee_avg_time', 'spent_hours',
            'assignee_std_time', 'steps_count', 'comments_count', 'turn_no',
            'comments count', 'assignee_ticket_count',
        ],
        T['importance']: ['9.6%', '9.4%', '8.6%', '7.6%', '7.5%', '6.6%', '6.4%', '5.7%', '5.6%', '5.4%'],
    })
    st.dataframe(fi_opt_df, use_container_width=True, hide_index=True)

with col2:
    st.markdown("#### O-Score Modell — RandomForest Feature Importance (alle 7 Features)")
    fi_o_df = pd.DataFrame({
        T['rank']: list(range(1, 8)),
        T['feature']: [
            'median_time_hours', 'avg_comments', 'ticket_count',
            'first_touch_rate', 'reopen_rate', 'success_rate', 'avg_steps',
        ],
        T['importance']: ['30.1%', '16.6%', '13.2%', '11.8%', '11.2%', '9.3%', '7.9%'],
    })
    st.dataframe(fi_o_df, use_container_width=True, hide_index=True)

    st.markdown("#### O-Score Gewichtungen (Formel)")
    weights_df = pd.DataFrame({
        'Komponente': ['Qualität (quality)', 'Effizienz (efficiency)', 'Produktivität (productivity)', 'Kommunikation (communication)'],
        'Gewicht': ['35%', '25%', '20%', '20%'],
        'Sub-Metriken': [
            '60% Reopen-Rate (invertiert) + 40% Success-Rate',
            '100% Bearbeitungszeit (Perzentil, invertiert)',
            '60% Ticket-Volumen + 40% Bearbeitungsschritte (invertiert)',
            '50% First-Touch-Rate + 50% Kommentar-Deviation (optimal = Median)',
        ],
    })
    st.dataframe(weights_df, use_container_width=True, hide_index=True)

# Abschluss-Info
st.markdown("---")
if lang == 'de':
    st.info("""
    **Hinweise zur I/O-Dokumentation:**
    - Alle Hyperparameter wurden direkt aus den `.joblib`-Dateien via `joblib.load()` + `.get_params(deep=True)` extrahiert
    - `optimized_scorer.joblib` wurde durch Optuna-Hyperparameter-Suche (Bayessche Optimierung) optimiert
    - `performance_scorer.joblib` und `q_score_model.joblib` sind funktional identisch (verschiedene Trainingsskripte, gleiche Konfiguration)
    - Der O-Score ist komplett regelbasiert (keine ML-Optimierung der Gewichte) — das ML-Modell lernt nur, den O-Score nachzubilden
    - Feature-Importance aus RandomForest-Komponente des VotingClassifiers (Gini-Importance)
    """)
else:
    st.info("""
    **Notes on I/O documentation:**
    - All hyperparameters were extracted directly from `.joblib` files via `joblib.load()` + `.get_params(deep=True)`
    - `optimized_scorer.joblib` was optimized through Optuna hyperparameter search (Bayesian optimization)
    - `performance_scorer.joblib` and `q_score_model.joblib` are functionally identical (different training scripts, same configuration)
    - The O-Score is completely rule-based (no ML optimization of weights) — the ML model only learns to replicate the O-Score
    - Feature importance from RandomForest component of VotingClassifier (Gini importance)
    """)

render_footer()
