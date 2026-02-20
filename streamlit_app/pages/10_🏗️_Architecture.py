"""
Projektarchitektur – Übersicht über das System, Datenfluss und Komponenten
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

st.set_page_config(page_title="Projektarchitektur", page_icon="🏗️", layout="wide")

init_session_state()
render_settings_sidebar()

lang = st.session_state.get('language', 'de')

# ── Texte ──────────────────────────────────────────────────────────────────
TEXTS = {
    'de': {
        'title': '🏗️ Projektarchitektur',
        'subtitle': 'Systemübersicht, Datenfluss und Komponentenstruktur des Helpdesk ML-Dashboards',
        'sec_overview':    '📋 Projektübersicht',
        'sec_dataflow':    '🔄 Datenfluß-Diagramm',
        'sec_datasources': '📂 Datenquellen & Verarbeitete Dateien',
        'sec_models':      '🗂️ Modelle & Artefakte',
        'sec_pipeline':    '🤖 Modell-Pipelines im Detail',
        'overview_text': """
**Help Desk Performance Monitor** ist ein KI-gestütztes Analyse-Dashboard für Helpdesk-Mitarbeiterdaten.

**Ziel:** Automatische Bewertung der Mitarbeiter-Performance auf Basis von Ticket-Daten — als Ergänzung 
zur subjektiven Manager-Bewertung (Q-Score) durch ein datenbasiertes Bewertungssystem (O-Score + ML-Modelle + Clustering).

**Technologie-Stack:**
- Python 3.x — Datenverarbeitung, ML-Training
- Streamlit — Web-Dashboard (Port 8501)
- Scikit-learn, XGBoost, LightGBM — ML-Modelle
- CSV / Excel → pandas DataFrames — Datenhaltung
- Joblib — Modell-Serialisierung
- SQLite — Simulations-Datenbank (helpdesk.db)

**Architekturprinzip:** Drei parallele ML-Pipelines (Q-Score, O-Score, Clustering) → Offline-Training → Online-Inferenz im Dashboard.
        """,
        'dataflow_title':    'Datenfluß: Von Rohdaten zum Dashboard',
        'datasources_title': 'Rohdateien und verarbeitete Daten',
        'models_title':      'Modelle und Artefakte',
        'pipeline_title':    'ML-Trainings-Pipelines im Detail',
        'file':        'Datei',
        'rows':        'Zeilen',
        'cols':        'Spalten',
        'description': 'Beschreibung',
        'model':       'Modell',
        'type':        'Typ',
        'size':        'Größe',
    },
    'en': {
        'title': '🏗️ Project Architecture',
        'subtitle': 'System overview, data flow and component structure of the Helpdesk ML Dashboard',
        'sec_overview':    '📋 Project Overview',
        'sec_dataflow':    '🔄 Data Flow Diagram',
        'sec_datasources': '📂 Data Sources & Processed Files',
        'sec_models':      '🗂️ Models & Artifacts',
        'sec_pipeline':    '🤖 Model Pipelines in Detail',
        'overview_text': """
**Help Desk Performance Monitor** is an AI-powered analytics dashboard for helpdesk employee data.

**Goal:** Automatic employee performance evaluation based on ticket data — complementing 
the subjective manager rating (Q-Score) with a data-driven rating system (O-Score + ML models + Clustering).

**Technology Stack:**
- Python 3.x — Data processing, ML training
- Streamlit — Web dashboard (port 8501)
- Scikit-learn, XGBoost, LightGBM — ML models
- CSV / Excel → pandas DataFrames — Data storage
- Joblib — Model serialization
- SQLite — Simulation database (helpdesk.db)

**Architecture Principle:** Three parallel ML pipelines (Q-Score, O-Score, Clustering) → Offline training → Online inference in the dashboard.
        """,
        'dataflow_title':    'Data Flow: From Raw Data to Dashboard',
        'datasources_title': 'Raw Files and Processed Data',
        'models_title':      'Models and Artifacts',
        'pipeline_title':    'ML Training Pipelines in Detail',
        'file':        'File',
        'rows':        'Rows',
        'cols':        'Columns',
        'description': 'Description',
        'model':       'Model',
        'type':        'Type',
        'size':        'Size',
    }
}

T = TEXTS.get(lang, TEXTS['de'])

# ── Header ─────────────────────────────────────────────────────────────────
page_header(T['title'], T['subtitle'])

# ── 1. Projektübersicht ────────────────────────────────────────────────────
section_header(T['sec_overview'])
st.markdown(T['overview_text'])

# ── 2. Datenfluß-Diagramm ──────────────────────────────────────────────────
section_header(T['sec_dataflow'])

if lang == 'de':
    st.markdown("#### Schritt-für-Schritt-Überblick des Datenflusses")
else:
    st.markdown("#### Step-by-step overview of the data flow")

# Lokalisierte Labels
if lang == 'de':
    _gv_issues    = "issues.csv\\n(66.691 Zeilen)"
    _gv_snapshot  = "issues_snapshot.csv\\n(90.963 Zeilen)"
    _gv_sample    = "issues_snapshot_sample.xlsx\\n(747 Zeilen, Ground Truth)"
    _gv_history   = "issues_change_history.csv\\n(257.508 Zeilen)"
    _gv_utterance = "sample_utterances.csv\\n(30.104 Zeilen)"
    _gv_feateng   = "feature_engineering.py\\nErstellt ML-Features"
    _gv_oscore    = "o_score.py\\nBerechnet O-Score"
    _gv_oresult   = "o_score_results.csv\\n(231 Mitarbeiter)"
    _gv_unsfeat   = "unsuper_feature_\\nengineering.py\\n17 Features/Mitarb."
    _gv_unsclu    = "unsuper_clustering.py\\nK-Means k=4\\nDBSCAN + Agglomerative"
    _gv_clures    = "cluster_results.csv\\n(302 Mitarbeiter)"
    _gv_app       = "app.py\\nHauptanwendung"
    _gv_analytics = "Analytics-Module\\nnlp · dialog · compliance\\nbias · trend · training"
else:
    _gv_issues    = "issues.csv\\n(66,691 rows)"
    _gv_snapshot  = "issues_snapshot.csv\\n(90,963 rows)"
    _gv_sample    = "issues_snapshot_sample.xlsx\\n(747 rows, Ground Truth)"
    _gv_history   = "issues_change_history.csv\\n(257,508 rows)"
    _gv_utterance = "sample_utterances.csv\\n(30,104 rows)"
    _gv_feateng   = "feature_engineering.py\\nCreates ML features"
    _gv_oscore    = "o_score.py\\nCalculates O-Score"
    _gv_oresult   = "o_score_results.csv\\n(231 employees)"
    _gv_unsfeat   = "unsuper_feature_\\nengineering.py\\n17 features/employee"
    _gv_unsclu    = "unsuper_clustering.py\\nK-Means k=4\\nDBSCAN + Agglomerative"
    _gv_clures    = "cluster_results.csv\\n(302 employees)"
    _gv_app       = "app.py\\nMain Application"
    _gv_analytics = "Analytics Modules\\nnlp · dialog · compliance\\nbias · trend · training"

st.graphviz_chart(f"""
digraph dataflow {{
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", fontsize=10];
    splines=ortho;
    nodesep=0.5;
    ranksep=0.6;

    subgraph cluster_raw {{
        label="Raw Data";
        style=filled; color=lightgrey;
        {{rank=same; issues; snapshot; sample; history; utterances;}}
        issues    [label="{_gv_issues}",    fillcolor="#AED6F1"];
        snapshot  [label="{_gv_snapshot}",  fillcolor="#AED6F1"];
        sample    [label="{_gv_sample}",    fillcolor="#A9DFBF"];
        history   [label="{_gv_history}",   fillcolor="#AED6F1"];
        utterances[label="{_gv_utterance}", fillcolor="#AED6F1"];
    }}

    subgraph cluster_qpipeline {{
        label="Q-Score Pipeline";
        style=filled; color="#FDEDEC";
        feat_eng    [label="{_gv_feateng}",        fillcolor="#FAD7A0"];
        ml_model_q  [label="ml_model_q.py\\nVotingClassifier (RF+XGB+LGB)\\nQ1/Q2/Q3 · QWK=0.618", fillcolor="#F1948A"];
        q_model     [label="q_score_model.joblib", fillcolor="#85C1E9"];
        opt_model   [label="optimized_scorer.joblib\\n(XGB+LGB, Optuna)",   fillcolor="#5DADE2"];
    }}

    subgraph cluster_opipeline {{
        label="O-Score Pipeline";
        style=filled; color="#EBF5FB";
        o_score    [label="{_gv_oscore}",  fillcolor="#FAD7A0"];
        o_result   [label="{_gv_oresult}", fillcolor="#AED6F1"];
        ml_model_o [label="ml_model_o.py\\nVotingClassifier (RF+XGB+LGB)", fillcolor="#F1948A"];
        o_model    [label="o_score_model.joblib",   fillcolor="#85C1E9"];
    }}

    subgraph cluster_clustering {{
        label="Clustering Pipeline";
        style=filled; color="#FEF9E7";
        uns_feat [label="{_gv_unsfeat}", fillcolor="#FAD7A0"];
        uns_clu  [label="{_gv_unsclu}",  fillcolor="#F39C12"];
        clu_res  [label="{_gv_clures}",  fillcolor="#AED6F1"];
        km_model [label="kmeans_model.joblib\\n(k=4, Silhouette=0.58)", fillcolor="#85C1E9"];
    }}

    analytics [label="{_gv_analytics}", fillcolor="#F9E79F", shape=box];

    subgraph cluster_dashboard {{
        label="Streamlit Dashboard (Port 8501)";
        style=filled; color="#E9F7EF";
        dashboard [label="{_gv_app}", fillcolor="#82E0AA"];
        subgraph cluster_pages {{
            label="pages/"; style=filled; color="#D5F5E3";
            {{rank=same; p1; p2; p3; p4; p5; p6; p7; p8;}}
            p1 [label="01_Overview",     fillcolor="#A9DFBF"];
            p2 [label="02_Tickets",      fillcolor="#A9DFBF"];
            p3 [label="03_People",       fillcolor="#A9DFBF"];
            p4 [label="04_Performance",  fillcolor="#A9DFBF"];
            p5 [label="05_Operations",   fillcolor="#A9DFBF"];
            p6 [label="06_Clustering",   fillcolor="#F9E79F"];
            p7 [label="10_Architecture", fillcolor="#A9DFBF"];
            p8 [label="11_IO_Docs",      fillcolor="#A9DFBF"];
        }}
    }}

    issues     -> feat_eng;
    sample     -> feat_eng;
    history    -> feat_eng;
    feat_eng   -> ml_model_q;
    ml_model_q -> q_model;
    ml_model_q -> opt_model;

    snapshot   -> o_score;
    o_score    -> o_result;
    o_result   -> ml_model_o;
    ml_model_o -> o_model;

    snapshot   -> uns_feat;
    history    -> uns_feat;
    uns_feat   -> uns_clu;
    uns_clu    -> clu_res;
    uns_clu    -> km_model;

    issues     -> analytics;
    snapshot   -> analytics;
    utterances -> analytics;

    q_model    -> dashboard;
    opt_model  -> dashboard;
    o_model    -> dashboard;
    clu_res    -> dashboard;
    km_model   -> dashboard;
    analytics  -> dashboard;

    dashboard -> p1; dashboard -> p2; dashboard -> p3; dashboard -> p4;
    dashboard -> p5; dashboard -> p6; dashboard -> p7; dashboard -> p8;
}}
""", use_container_width=True)

# ── 3. Datenquellen & Verarbeitete Dateien ─────────────────────────────────
section_header(T['sec_datasources'])

tab_raw, tab_proc = st.tabs(
    ["📁 Raw Data", "⚙️ Processed Data"] if lang == 'en'
    else ["📁 Rohdaten", "⚙️ Verarbeitete Daten"]
)

with tab_raw:
    _desc_raw_de = [
        'Haupt-Issue-Datensatz: Ticket-Metadaten, Workflow-Zeiten (wf_*), Workflow-Ereignisse (wfe_*), Bearbeitungsschritte',
        'Snapshot pro Mitarbeiter/Ticket-Kombination mit turn_no; Basis für O-Score & Clustering',
        'Ground Truth: 747 manuell bewertete Tickets mit Q1, Q2, Q3 (Manager-Bewertungen, Skala 1–5)',
        'Audit-Trail: Alle Feldänderungen pro Ticket mit Zeitstempel (Reassignments, Status, Priorität)',
        'Kommentar-Utterances: 30.104 einzelne Textbeiträge mit Autor-Rolle und Sequenzposition',
    ]
    _desc_raw_en = [
        'Main issue dataset: ticket metadata, workflow times (wf_*), workflow events (wfe_*), processing steps',
        'Snapshot per employee/ticket combination with turn_no; basis for O-Score & Clustering',
        'Ground truth: 747 manually rated tickets with Q1, Q2, Q3 (manager ratings, scale 1–5)',
        'Audit trail: all field changes per ticket with timestamp (reassignments, status, priority)',
        'Comment utterances: 30,104 individual text contributions with author role and sequence position',
    ]
    raw_data = {
        T['file']: [
            'data/raw/issues.csv',
            'data/raw/issues_snapshot.csv',
            'data/raw/issues_snapshot_sample.xlsx',
            'data/raw/issues_change_history.csv',
            'data/raw/sample_utterances.csv',
        ],
        T['rows']:        ['66.691', '90.963', '747', '257.508', '30.104'] if lang == 'de' else ['66,691', '90,963', '747', '257,508', '30,104'],
        T['cols']:        ['58', '60', '19', '6', '9'],
        T['description']: _desc_raw_de if lang == 'de' else _desc_raw_en,
    }
    st.dataframe(pd.DataFrame(raw_data), use_container_width=True, hide_index=True)

with tab_proc:
    _desc_proc_de = [
        'ML-Trainingsdatensatz: 6 Features + Q1/Q2/Q3 Targets (nur valide Ground-Truth-Samples)',
        'O-Score pro Mitarbeiter: 4 Komponenten (Qualität 35%, Effizienz 25%, Produktivität 20%, Kommunikation 20%) → O-Score 1–5',
        'Feature-Matrix für Clustering: 17 normalisierte Arbeits-Features pro Mitarbeiter (≥5 Tickets)',
        'K-Means Cluster-Zuordnungen: Cluster-Label, PCA-Koordinaten, DBSCAN, Agglomerative Vergleich',
        'Durchschnittliche Feature-Werte pro Cluster (4 Cluster × 17+ Features)',
        '2D PCA-Koordinaten + Cluster-Label für Streudiagramm-Visualisierung',
        'Inertia & Silhouette-Werte für k=2..8 (Elbow + Silhouette-Analyse)',
        'PCA-Loadings pro Feature: Beitrag zu PC1 und PC2 (Feature-Wichtigkeit im Clustering)',
        'Ausreißer-Analyse: Z-Score (>3,0) + Mahalanobis-Distanz (χ²-Test p<0,05) pro Mitarbeiter',
        'Q-Score vs. O-Score Vergleich: Nur Mitarbeiter mit beiden Scores (84 Mitarbeiter)',
        'Workflow-Compliance-Analyse: Compliance-Score, Reopens, Backward-Steps pro Ticket',
        'NLP-Features pro Issue: Sentiment (compound/pos/neg), Politeness, Urgency, Technikalität',
        'Dialog-Akt-Klassifikation: 12 Kategorien (QUESTION, COMPLAINT, THANKS, etc.)',
    ]
    _desc_proc_en = [
        'ML training dataset: 6 features + Q1/Q2/Q3 targets (valid ground-truth samples only)',
        'O-Score per employee: 4 components (Quality 35%, Efficiency 25%, Productivity 20%, Communication 20%) → O-Score 1–5',
        'Clustering feature matrix: 17 normalized work-behavior features per employee (≥5 tickets)',
        'K-Means cluster assignments: cluster label, PCA coordinates, DBSCAN, Agglomerative comparison',
        'Mean feature values per cluster (4 clusters × 17+ features)',
        '2D PCA coordinates + cluster label for scatter plot visualization',
        'Inertia & silhouette scores for k=2..8 (elbow + silhouette analysis)',
        'PCA loadings per feature: contribution to PC1 and PC2 (feature importance in clustering)',
        'Outlier analysis: Z-Score (>3.0) + Mahalanobis distance (χ²-test p<0.05) per employee',
        'Q-Score vs. O-Score comparison: employees with both scores only (84 employees)',
        'Workflow compliance analysis: compliance score, reopens, backward steps per ticket',
        'NLP features per issue: sentiment (compound/pos/neg), politeness, urgency, technicality',
        'Dialog-act classification: 12 categories (QUESTION, COMPLAINT, THANKS, etc.)',
    ]
    proc_data = {
        T['file']: [
            'data/processed/ml_dataset.csv',
            'data/processed/o_score_results.csv',
            'data/processed/employee_features.csv',
            'data/processed/cluster_results.csv',
            'data/processed/cluster_profiles.csv',
            'data/processed/pca_results.csv',
            'data/processed/elbow_silhouette.csv',
            'data/processed/feature_importance.csv',
            'data/processed/outlier_analysis.csv',
            'data/processed/q_vs_o_score_comparison.csv',
            'data/processed/workflow_analysis.csv',
            'data/processed/nlp_features.csv',
            'data/processed/dialog_acts.csv',
        ],
        T['rows']:        ['603', '231', '302', '302', '4', '302', '7', '17', '302', '84', '~variabel', '~variabel', '~variabel'] if lang == 'de'
                     else ['603', '231', '302', '302', '4', '302', '7', '17', '302', '84', '~variable', '~variable', '~variable'],
        T['cols']:        ['9', '19', '18', '22', '19', '5', '3', '4', '24', '24', '6', '~15', '7'],
        T['description']: _desc_proc_de if lang == 'de' else _desc_proc_en,
    }
    st.dataframe(pd.DataFrame(proc_data), use_container_width=True, hide_index=True)

# ── 4. Modelle & Artefakte ─────────────────────────────────────────────────
section_header(T['sec_models'])

_models_de = [
    ('models/q_score_model.joblib',    'VotingClassifier (RF+XGB+LGB)',  'Q-Score Klassifikation Q1/Q2/Q3 · Acc=65,8% · QWK=0,618'),
    ('models/optimized_scorer.joblib', 'VotingClassifier (XGB+LGB)',     'Optuna-optimierter Q-Score Scorer · XGB+LGB ohne RF'),
    ('models/o_score_model.joblib',    'VotingClassifier (RF+XGB+LGB)',  'O-Score Klassifikation (Klassen 1–5) · 7 aggregierte Features'),
    ('models/kmeans_model.joblib',     'KMeans(k=4, n_init=20)',         'Clustering-Modell · Silhouette=0,5807 · Inertia=6747,69'),
    ('models/scaler.joblib',           'RobustScaler',                   'Skalierung für Clustering (Winsorisierung auf 99. Perzentil vorher)'),
    ('models/scaler_kmeans.joblib',    'RobustScaler',                   'Alternative Scaler (kmeans_*-Dateinamen-Variante)'),
    ('models/scaler_unsuper.joblib',   'RobustScaler',                   'Skalierung für unsuper-Pipeline (Canonical)'),
]
_models_en = [
    ('models/q_score_model.joblib',    'VotingClassifier (RF+XGB+LGB)',  'Q-Score classification Q1/Q2/Q3 · Acc=65.8% · QWK=0.618'),
    ('models/optimized_scorer.joblib', 'VotingClassifier (XGB+LGB)',     'Optuna-optimized Q-Score scorer · XGB+LGB without RF'),
    ('models/o_score_model.joblib',    'VotingClassifier (RF+XGB+LGB)',  'O-Score classification (classes 1–5) · 7 aggregated features'),
    ('models/kmeans_model.joblib',     'KMeans(k=4, n_init=20)',         'Clustering model · Silhouette=0.5807 · Inertia=6747.69'),
    ('models/scaler.joblib',           'RobustScaler',                   'Scaler for clustering (winsorizing at 99th percentile applied prior)'),
    ('models/scaler_kmeans.joblib',    'RobustScaler',                   'Alternative scaler (kmeans_* filename variant)'),
    ('models/scaler_unsuper.joblib',   'RobustScaler',                   'Scaler for unsuper pipeline (canonical)'),
]
_models = _models_de if lang == 'de' else _models_en
df_models = pd.DataFrame(_models, columns=[T['file'], T['type'], T['description']])
st.dataframe(df_models, use_container_width=True, hide_index=True)

# ── 5. Modell-Pipelines im Detail ─────────────────────────────────────────
section_header(T['sec_pipeline'])

tab_q, tab_o, tab_c = st.tabs(["📊 Q-Score", "🎯 O-Score", "🔬 Clustering"])

# ── Q-Score ──
with tab_q:
    col1, col2 = st.columns([1, 1])
    with col1:
        if lang == 'de':
            st.markdown("""
#### Q-Score Pipeline (subjektive Bewertung)
```
issues_snapshot_sample.xlsx (747 Ground-Truth-Samples)
  ↓ feature_engineering.py
  ├── create_time_features()
  │   → spent_hours, total_days
  ├── create_process_features()
  │   → turn_no, steps, is_complex
  ├── create_communication_features()
  │   → comments_count
  └── create_priority_features()
      → priority_numeric
  ↓ ml_dataset.csv
    603 valide Samples · 6 Features + Q1/Q2/Q3
  ↓ ml_model_q.py
  ├── Train-Test Split (80/20, stratified)
  ├── StandardScaler
  ├── VotingClassifier (soft voting):
  │   ├── RandomForestClassifier
  │   │   n=100, depth=6, seed=42
  │   ├── XGBClassifier
  │   │   n=100, depth=6, lr=0.1
  │   └── LGBMClassifier
  │       n=100, depth=6, lr=0.1
  └── 5-Fold Stratified CV
  ↓ models/q_score_model.joblib
  ↓ Optuna (50 Trials, XGB+LGB)
  ↓ models/optimized_scorer.joblib
```
            """)
        else:
            st.markdown("""
#### Q-Score Pipeline (subjective rating)
```
issues_snapshot_sample.xlsx (747 ground-truth samples)
  ↓ feature_engineering.py
  ├── create_time_features()
  │   → spent_hours, total_days
  ├── create_process_features()
  │   → turn_no, steps, is_complex
  ├── create_communication_features()
  │   → comments_count
  └── create_priority_features()
      → priority_numeric
  ↓ ml_dataset.csv
    603 valid samples · 6 features + Q1/Q2/Q3
  ↓ ml_model_q.py
  ├── Train-Test Split (80/20, stratified)
  ├── StandardScaler
  ├── VotingClassifier (soft voting):
  │   ├── RandomForestClassifier
  │   │   n=100, depth=6, seed=42
  │   ├── XGBClassifier
  │   │   n=100, depth=6, lr=0.1
  │   └── LGBMClassifier
  │       n=100, depth=6, lr=0.1
  └── 5-Fold Stratified CV
  ↓ models/q_score_model.joblib
  ↓ Optuna (50 trials, XGB+LGB)
  ↓ models/optimized_scorer.joblib
```
            """)
    with col2:
        if lang == 'de':
            st.markdown("""
#### Metriken (Ø Q1/Q2/Q3)

| Metrik | Q1 | Q2 | Q3 | Ø |
|--------|-----|-----|-----|-----|
| Accuracy | 65,3% | 66,1% | 66,1% | **65,8%** |
| MAE | 0,595 | 0,570 | 0,603 | **0,589** |
| CV | 64,2% | 65,3% | 65,8% | **65,1%** |
| QWK | 0,624 | 0,634 | 0,597 | **0,618** |
| Kappa | 0,337 | 0,339 | 0,363 | **0,346** |
| Macro-F1 | 37,8% | 36,4% | 44,3% | **39,5%** |

#### Top Features (Q1)
| Feature | Importance |
|---------|-----------|
| spent_hours | 45,3% |
| comments_count | 25,3% |
| turn_no | 12,1% |
| steps | 11,0% |
| priority_numeric | 6,3% |
            """)
        else:
            st.markdown("""
#### Metrics (avg Q1/Q2/Q3)

| Metric | Q1 | Q2 | Q3 | Avg |
|--------|-----|-----|-----|-----|
| Accuracy | 65.3% | 66.1% | 66.1% | **65.8%** |
| MAE | 0.595 | 0.570 | 0.603 | **0.589** |
| CV | 64.2% | 65.3% | 65.8% | **65.1%** |
| QWK | 0.624 | 0.634 | 0.597 | **0.618** |
| Kappa | 0.337 | 0.339 | 0.363 | **0.346** |
| Macro-F1 | 37.8% | 36.4% | 44.3% | **39.5%** |

#### Top Features (Q1)
| Feature | Importance |
|---------|-----------|
| spent_hours | 45.3% |
| comments_count | 25.3% |
| turn_no | 12.1% |
| steps | 11.0% |
| priority_numeric | 6.3% |
            """)

# ── O-Score ──
with tab_o:
    col1, col2 = st.columns([1, 1])
    with col1:
        if lang == 'de':
            st.markdown("""
#### O-Score Pipeline (objektive Bewertung)
```
data/raw/issues_snapshot.csv (90.963 Zeilen)
  ↓ o_score.py
  ├── calculate_employee_metrics()
  │   ├── ticket_count
  │   ├── median_time_hours
  │   ├── avg_steps
  │   ├── avg_comments
  │   ├── reopen_rate (wfe_reopened > 0)
  │   ├── first_touch_rate (Kommentar < 1h)
  │   └── success_rate (status: closed/done)
  ├── Gewichtetes Composite Scoring:
  │   ├── quality_score (35%)
  │   │   0.6×(1−reopen) + 0.4×success
  │   ├── efficiency_score (25%)
  │   │   Perzentil(median_time, invertiert)
  │   ├── productivity_score (20%)
  │   │   0.6×Vol-Pz + 0.4×(1−steps-Pz)
  │   └── communication_score (20%)
  │       0.5×first_touch + 0.5×comm_opt
  ├── o_score_raw → o_score (1–5, skaliert)
  └── 231 Mitarbeiter (≥3 Tickets Filter)
  ↓ data/processed/o_score_results.csv
  ↓ ml_model_o.py
  ├── bins=[0, 1.8, 2.6, 3.4, 4.2, 5.1]
  ├── StandardScaler
  ├── VotingClassifier (RF+XGB+LGB)
  └── 5-Fold CV
  ↓ models/o_score_model.joblib
```
            """)
        else:
            st.markdown("""
#### O-Score Pipeline (objective rating)
```
data/raw/issues_snapshot.csv (90,963 rows)
  ↓ o_score.py
  ├── calculate_employee_metrics()
  │   ├── ticket_count
  │   ├── median_time_hours
  │   ├── avg_steps
  │   ├── avg_comments
  │   ├── reopen_rate (wfe_reopened > 0)
  │   ├── first_touch_rate (comment < 1h)
  │   └── success_rate (status: closed/done)
  ├── Weighted composite scoring:
  │   ├── quality_score (35%)
  │   │   0.6×(1−reopen) + 0.4×success
  │   ├── efficiency_score (25%)
  │   │   Percentile(median_time, inverted)
  │   ├── productivity_score (20%)
  │   │   0.6×vol-pct + 0.4×(1−steps-pct)
  │   └── communication_score (20%)
  │       0.5×first_touch + 0.5×comm_opt
  ├── o_score_raw → o_score (1–5, scaled)
  └── 231 employees (≥3 tickets filter)
  ↓ data/processed/o_score_results.csv
  ↓ ml_model_o.py
  ├── bins=[0, 1.8, 2.6, 3.4, 4.2, 5.1]
  ├── StandardScaler
  ├── VotingClassifier (RF+XGB+LGB)
  └── 5-Fold CV
  ↓ models/o_score_model.joblib
```
            """)
    with col2:
        if lang == 'de':
            st.markdown("""
#### Feature Importance (O-Score)
| Feature | Wichtigkeit |
|---------|------------|
| median_time_hours | 30,1% |
| avg_comments | 16,6% |
| ticket_count | 13,2% |
| first_touch_rate | 11,8% |
| reopen_rate | 11,2% |
| success_rate | 9,3% |
| avg_steps | 7,9% |

#### O-Score Gewichtung
| Komponente | Gewicht | Formel |
|-----------|---------|--------|
| Qualität | 35% | 0,6×(1−reopen) + 0,4×success |
| Effizienz | 25% | Perzentil(median_time)⁻¹ |
| Produktivität | 20% | 0,6×Vol + 0,4×(1−Steps) |
| Kommunikation | 20% | 0,5×first_touch + 0,5×opt |

**Coverage:** 231 Mitarbeiter (aus 90.963 Tickets)
            """)
        else:
            st.markdown("""
#### Feature Importance (O-Score)
| Feature | Importance |
|---------|-----------|
| median_time_hours | 30.1% |
| avg_comments | 16.6% |
| ticket_count | 13.2% |
| first_touch_rate | 11.8% |
| reopen_rate | 11.2% |
| success_rate | 9.3% |
| avg_steps | 7.9% |

#### O-Score Weights
| Component | Weight | Formula |
|-----------|--------|---------|
| Quality | 35% | 0.6×(1−reopen) + 0.4×success |
| Efficiency | 25% | Percentile(median_time)⁻¹ |
| Productivity | 20% | 0.6×vol + 0.4×(1−steps) |
| Communication | 20% | 0.5×first_touch + 0.5×opt |

**Coverage:** 231 employees (from 90,963 tickets)
            """)

# ── Clustering ──
with tab_c:
    col1, col2 = st.columns([1, 1])
    with col1:
        if lang == 'de':
            st.markdown("""
#### Clustering Pipeline (unüberwachtes Lernen)
```
issues_snapshot.csv + issues_change_history.csv
  ↓ unsuper_feature_engineering.py
  ├── Priority Encoding (Blocker=5..Lowest=0)
  ├── Global Median Resolution (Referenz)
  ├── Reassignment-Erkennung (change_history)
  ├── First Response Time (erste Statusänderung)
  ├── Active Months (year_month Perioden)
  └── Per-Assignee Features (≥5 Tickets):
      Effizienz:    median/avg/std resolution days,
                    pct_fast_resolved
      Volumen:      total_tickets, tickets_per_month,
                    active_months
      Komplexität:  avg_priority, pct_high_priority,
                    n_distinct_projects/_categories
      Qualität:     pct_reopened, resolution_rate,
                    avg_comments
      Workflow:     pct_sole_resolver,
                    avg_first_response_days,
                    avg_processing_steps
  ↓ employee_features.csv (302 × 18)
  ↓ unsuper_clustering.py
  ├── Winsorisierung (99. Perzentil)
  ├── RobustScaler (IQR-basiert)
  ├── PCA (2 Komp.) → 78,6% Varianz
  │   PC1: resolution_rate (54,9%)
  │   PC2: median_resolution_days (23,7%)
  ├── Silhouette-Suche k=2..8
  │   k=2: 0,765 | k=3: 0,755 | k=4: 0,581
  ├── KMeans(k=4, n_init=20, seed=42)
  ├── DBSCAN(eps=1.5, min_samples=5)
  ├── AgglomerativeClustering(k=4)
  ├── Semantisches Labeling nach Perf.-Score
  └── Outlier: Z-Score (>3,0) + Mahalanobis
  ↓ cluster_results.csv    (302 × 22)
  ↓ cluster_profiles.csv   (4 × 19)
  ↓ pca_results.csv        (302 × 5)
  ↓ elbow_silhouette.csv   (7 × 3)
  ↓ feature_importance.csv (17 × 4)
  ↓ outlier_analysis.csv   (302 × 24)
  ↓ models/kmeans_model.joblib
  ↓ models/scaler.joblib
```
            """)
        else:
            st.markdown("""
#### Clustering Pipeline (unsupervised learning)
```
issues_snapshot.csv + issues_change_history.csv
  ↓ unsuper_feature_engineering.py
  ├── Priority Encoding (Blocker=5..Lowest=0)
  ├── Global Median Resolution (reference)
  ├── Reassignment detection (change_history)
  ├── First Response Time (first status change)
  ├── Active Months (year_month periods)
  └── Per-Assignee Features (≥5 tickets):
      Efficiency:   median/avg/std resolution days,
                    pct_fast_resolved
      Volume:       total_tickets, tickets_per_month,
                    active_months
      Complexity:   avg_priority, pct_high_priority,
                    n_distinct_projects/_categories
      Quality:      pct_reopened, resolution_rate,
                    avg_comments
      Workflow:     pct_sole_resolver,
                    avg_first_response_days,
                    avg_processing_steps
  ↓ employee_features.csv (302 × 18)
  ↓ unsuper_clustering.py
  ├── Winsorizing (99th percentile)
  ├── RobustScaler (IQR-based)
  ├── PCA (2 components) → 78.6% variance
  │   PC1: resolution_rate (54.9%)
  │   PC2: median_resolution_days (23.7%)
  ├── Silhouette search k=2..8
  │   k=2: 0.765 | k=3: 0.755 | k=4: 0.581
  ├── KMeans(k=4, n_init=20, seed=42)
  ├── DBSCAN(eps=1.5, min_samples=5)
  ├── AgglomerativeClustering(k=4)
  ├── Semantic labeling by performance score
  └── Outliers: Z-Score (>3.0) + Mahalanobis
  ↓ cluster_results.csv    (302 × 22)
  ↓ cluster_profiles.csv   (4 × 19)
  ↓ pca_results.csv        (302 × 5)
  ↓ elbow_silhouette.csv   (7 × 3)
  ↓ feature_importance.csv (17 × 4)
  ↓ outlier_analysis.csv   (302 × 24)
  ↓ models/kmeans_model.joblib
  ↓ models/scaler.joblib
```
            """)
    with col2:
        if lang == 'de':
            st.markdown("""
#### Cluster-Ergebnisse (k=4)
| Cluster | Label | Anzahl | Anteil |
|---------|-------|--------|--------|
| 0 | High Performer 🟢 | 273 | 90,4% |
| 1 | Solid Performer 🟡 | 16 | 5,3% |
| 2 | Specialist ⚫ | 7 | 2,3% |
| 3 | Needs Improvement 🔴 | 6 | 2,0% |

#### KMeans-Parameter
| Parameter | Wert | Begründung |
|-----------|------|-----------|
| n_clusters | 4 | Silhouette + Business-Interpretierbarkeit |
| n_init | 20 | Stabile Centroids (Standard=10) |
| random_state | 42 | Reproduzierbarkeit |
| Inertia | 6747,69 | Elbow bei k=4 |

#### PCA-Loadings (Top 5)
| Feature | PC1 | PC2 |
|---------|-----|-----|
| resolution_rate | 55,75% | — |
| median_resolution_days | — | 20,97% |
| avg_resolution_days | 12,49% | — |
| std_resolution_days | — | 7,34% |
| avg_first_response_days | — | 5,79% |

#### Ausreißer
- **Z-Score** (>3,0): 37 Mitarbeiter
- **Mahalanobis** (p<0,05): 22 Mitarbeiter
- **Beide Methoden**: 14 Mitarbeiter
            """)
        else:
            st.markdown("""
#### Cluster Results (k=4)
| Cluster | Label | Count | Share |
|---------|-------|-------|-------|
| 0 | High Performer 🟢 | 273 | 90.4% |
| 1 | Solid Performer 🟡 | 16 | 5.3% |
| 2 | Specialist ⚫ | 7 | 2.3% |
| 3 | Needs Improvement 🔴 | 6 | 2.0% |

#### KMeans Parameters
| Parameter | Value | Justification |
|-----------|-------|--------------|
| n_clusters | 4 | Silhouette + business interpretability |
| n_init | 20 | Stable centroids (default=10) |
| random_state | 42 | Reproducibility |
| Inertia | 6747.69 | Elbow at k=4 |

#### PCA Loadings (Top 5)
| Feature | PC1 | PC2 |
|---------|-----|-----|
| resolution_rate | 55.75% | — |
| median_resolution_days | — | 20.97% |
| avg_resolution_days | 12.49% | — |
| std_resolution_days | — | 7.34% |
| avg_first_response_days | — | 5.79% |

#### Outliers
- **Z-Score** (>3.0): 37 employees
- **Mahalanobis** (p<0.05): 22 employees
- **Both methods**: 14 employees
            """)

render_footer()
