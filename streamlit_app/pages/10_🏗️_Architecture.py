"""
Projektarchitektur – Übersicht über das System, Datenfluss und Komponenten
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Import components (relative, wie alle anderen Seiten)
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
        'sec_overview': '📋 Projektübersicht',
        'sec_dataflow': '🔄 Datenfluß-Diagramm',
        'sec_datasources': '📂 Datenquellen',
        'sec_pipeline': '🤖 Modell-Pipeline',
        'overview_text': """
**Help Desk Performance Monitor** ist ein KI-gestütztes Analyse-Dashboard für Helpdesk-Mitarbeiterdaten.

**Ziel:** Automatische Bewertung der Mitarbeiter-Performance auf Basis von Ticket-Daten — als Ergänzung 
zur subjektiven Manager-Bewertung (Q-Score) durch ein datenbasiertes Bewertungssystem (O-Score + ML-Modelle).

**Technologie-Stack:**
- Python 3.x — Datenverarbeitung, ML-Training
- Streamlit — Web-Dashboard (Port 8501)
- Scikit-learn, XGBoost, LightGBM — ML-Modelle
- CSV / Excel → pandas DataFrames — Datenhaltung
- Joblib — Modell-Serialisierung
- SQLite — Simulations-Datenbank (helpdesk.db)

**Architekturprinzip:** Klassische ML-Pipeline → Offline-Training → Online-Inferenz im Dashboard.
        """,
        'dataflow_title': 'Datenfluß: Von Rohdaten zum Dashboard',
        'datasources_title': 'Rohdateien und verarbeitete Daten',
        'pipeline_title': 'ML-Trainings-Pipeline im Detail',
        'file': 'Datei',
        'rows': 'Zeilen',
        'cols': 'Spalten',
        'description': 'Beschreibung',
    },
    'en': {
        'title': '🏗️ Project Architecture',
        'subtitle': 'System overview, data flow and component structure of the Helpdesk ML Dashboard',
        'sec_overview': '📋 Project Overview',
        'sec_dataflow': '🔄 Data Flow Diagram',
        'sec_datasources': '📂 Data Sources',
        'sec_pipeline': '🤖 Model Pipeline',
        'overview_text': """
**Help Desk Performance Monitor** is an AI-powered analytics dashboard for helpdesk employee data.

**Goal:** Automatic employee performance evaluation based on ticket data — complementing 
the subjective manager rating (Q-Score) with a data-driven rating system (O-Score + ML models).

**Technology Stack:**
- Python 3.x — Data processing, ML training
- Streamlit — Web dashboard (port 8501)
- Scikit-learn, XGBoost, LightGBM — ML models
- CSV / Excel → pandas DataFrames — Data storage
- Joblib — Model serialization
- SQLite — Simulation database (helpdesk.db)

**Architecture Principle:** Classic ML pipeline → Offline training → Online inference in the dashboard.
        """,
        'dataflow_title': 'Data Flow: From Raw Data to Dashboard',
        'datasources_title': 'Raw Files and Processed Data',
        'pipeline_title': 'ML Training Pipeline in Detail',
        'file': 'File',
        'rows': 'Rows',
        'cols': 'Columns',
        'description': 'Description',
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

# Graphviz-Diagramm — kreuzungsfreies TB-Layout
if lang == 'de':
    _gv_issues    = "issues.csv\\n(66.691 Zeilen)"
    _gv_snapshot  = "issues_snapshot.csv\\n(90.963 Zeilen)"
    _gv_sample    = "issues_snapshot_sample.xlsx\\n(747 Zeilen, Ground Truth)"
    _gv_history   = "issues_change_history.csv\\n(257.508 Zeilen)"
    _gv_utterance = "sample_utterances.csv\\n(30.104 Zeilen)"
    _gv_loader    = "data_loader.py\\nLädt alle Datensätze"
    _gv_oscore    = "o_score.py\\nBerechnet O-Score"
    _gv_oresult   = "o_score_results.csv\\n(pro Mitarbeiter)"
    _gv_app       = "app.py\\nHauptanwendung"
    _gv_feateng   = "feature_engineering.py\\nErstellt ML-Features"
else:
    _gv_issues    = "issues.csv\\n(66,691 rows)"
    _gv_snapshot  = "issues_snapshot.csv\\n(90,963 rows)"
    _gv_sample    = "issues_snapshot_sample.xlsx\\n(747 rows, Ground Truth)"
    _gv_history   = "issues_change_history.csv\\n(257,508 rows)"
    _gv_utterance = "sample_utterances.csv\\n(30,104 rows)"
    _gv_loader    = "data_loader.py\\nLoads all datasets"
    _gv_oscore    = "o_score.py\\nCalculates O-Score"
    _gv_oresult   = "o_score_results.csv\\n(per employee)"
    _gv_app       = "app.py\\nMain Application"
    _gv_feateng   = "feature_engineering.py\\nCreates ML features"

st.graphviz_chart(f"""
digraph dataflow {{
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", fontsize=11];
    splines=ortho;

    subgraph cluster_raw {{
        label="Raw Data";
        style=filled;
        color=lightgrey;
        rank=same;
        issues [label="{_gv_issues}", fillcolor="#AED6F1"];
        snapshot [label="{_gv_snapshot}", fillcolor="#AED6F1"];
        sample [label="{_gv_sample}", fillcolor="#A9DFBF"];
        history [label="{_gv_history}", fillcolor="#AED6F1"];
        utterances [label="{_gv_utterance}", fillcolor="#AED6F1"];
    }}

    data_loader [label="{_gv_loader}", fillcolor="#FAD7A0"];

    subgraph cluster_qpipeline {{
        label="Q-Score Pipeline";
        style=filled;
        color="#FDEDEC";
        feat_eng [label="{_gv_feateng}", fillcolor="#FAD7A0"];
        ml_model_q [label="ml_model_q.py\\n(Q-Score mit QWK)", fillcolor="#F1948A"];
        q_score_model [label="q_score_model.joblib\\n(RF+XGB+LGB Ensemble)", fillcolor="#85C1E9"];
        optimized [label="optimized_scorer.joblib\\n(XGB+LGB, Optuna)", fillcolor="#5DADE2"];
    }}

    subgraph cluster_opipeline {{
        label="O-Score Pipeline";
        style=filled;
        color="#EBF5FB";
        o_score [label="{_gv_oscore}", fillcolor="#FAD7A0"];
        o_score_results [label="{_gv_oresult}", fillcolor="#AED6F1"];
        ml_model_o [label="ml_model_o.py\\n(O-Score Classifier)", fillcolor="#F1948A"];
        o_score_model [label="o_score_model.joblib\\n(RF+XGB+LGB Classifier)", fillcolor="#85C1E9"];
    }}

    analytics [label="nlp_analysis\\ndialog_analysis\\nprocess_compliance\\nbias_analysis\\ntrend_analysis\\ntraining_deficits", fillcolor="#F9E79F", shape=box];

    subgraph cluster_dashboard {{
        label="Streamlit Dashboard (Port 8501)";
        style=filled;
        color="#E9F7EF";
        dashboard [label="{_gv_app}", fillcolor="#82E0AA"];
        subgraph cluster_pages {{
            label="pages/";
            style=filled;
            color="#D5F5E3";
            rank=same;
            p1 [label="01_Overview", fillcolor="#A9DFBF"];
            p2 [label="02_Tickets", fillcolor="#A9DFBF"];
            p3 [label="03_People", fillcolor="#A9DFBF"];
            p4 [label="04_Performance", fillcolor="#A9DFBF"];
            p5 [label="05_Operations", fillcolor="#A9DFBF"];
            p6 [label="10_Architecture", fillcolor="#A9DFBF"];
            p7 [label="11_IO_Docs", fillcolor="#A9DFBF"];
        }}
    }}

    issues -> data_loader;
    snapshot -> data_loader;
    sample -> data_loader;
    history -> data_loader;
    utterances -> data_loader;

    data_loader -> feat_eng;
    feat_eng -> ml_model_q;
    ml_model_q -> q_score_model;
    ml_model_q -> optimized [label="Optuna"];

    data_loader -> o_score;
    o_score -> o_score_results;
    o_score_results -> ml_model_o;
    ml_model_o -> o_score_model;

    data_loader -> analytics;

    q_score_model -> dashboard;
    optimized -> dashboard;
    o_score_model -> dashboard;
    analytics -> dashboard;

    dashboard -> p1;
    dashboard -> p2;
    dashboard -> p3;
    dashboard -> p4;
    dashboard -> p5;
    dashboard -> p6;
    dashboard -> p7;
}}
""", use_container_width=True)

# ── 4. Datenquellen ────────────────────────────────────────────────────────
section_header(T['sec_datasources'])

_desc_de = [
    'Haupt-Issue-Datensatz: Ticket-Metadaten, Workflow-Zeiten (wf_*), Workflow-Ereignisse (wfe_*), Bearbeitungsschritte',
    'Snapshot pro Mitarbeiter/Ticket-Kombination mit turn-Nummer; Basis für O-Score-Berechnung',
    'Ground Truth: 747 manuell bewertete Tickets mit Q1, Q2, Q3 (Manager-Bewertungen, Skala 1–5)',
    'Audit-Trail: Alle Feldänderungen pro Ticket mit Zeitstempel und Änderungsgruppe',
    'Kommentar-Utterances: 30.104 einzelne Textbeiträge mit Autor-Rolle und Sequenzposition',
    'Prozessierter ML-Datensatz: 6 Features + Q1/Q2/Q3 Targets (nur valide Samples)',
    'O-Score pro Mitarbeiter: Qualität, Effizienz, Produktivität, Kommunikation (0–1) → O-Score (1–5)',
    'Workflow-Analyse: Compliance-Score, Reopens, Backward-Steps pro Ticket',
    'NLP-Features pro Issue: Sentiment (compound/pos/neg), Politeness, Urgency, Technikalität',
    'Dialog-Akt-Klassifikation: 12 Kategorien (QUESTION, COMPLAINT, THANKS, etc.)',
]
_desc_en = [
    'Main issue dataset: Ticket metadata, workflow times (wf_*), workflow events (wfe_*), processing steps',
    'Snapshot per employee/ticket combination with turn number; basis for O-Score calculation',
    'Ground truth: 747 manually rated tickets with Q1, Q2, Q3 (manager ratings, scale 1–5)',
    'Audit trail: All field changes per ticket with timestamp and change group',
    'Comment utterances: 30,104 individual text contributions with author role and sequence position',
    'Processed ML dataset: 6 features + Q1/Q2/Q3 targets (valid samples only)',
    'O-Score per employee: Quality, Efficiency, Productivity, Communication (0–1) → O-Score (1–5)',
    'Workflow analysis: Compliance score, reopens, backward steps per ticket',
    'NLP features per issue: Sentiment (compound/pos/neg), Politeness, Urgency, Technicality',
    'Dialog-act classification: 12 categories (QUESTION, COMPLAINT, THANKS, etc.)',
]
_rows_de = ['66.691', '90.963', '747', '257.508', '30.104', '603', '~variabel', '~variabel', '~variabel', '~variabel']
_rows_en = ['66,691', '90,963', '747', '257,508', '30,104', '603', '~variable', '~variable', '~variable', '~variable']

datasources = {
    T['file']: [
        'data/raw/issues.csv',
        'data/raw/issues_snapshot.csv',
        'data/raw/issues_snapshot_sample.xlsx',
        'data/raw/issues_change_history.csv',
        'data/raw/sample_utterances.csv',
        'data/processed/ml_dataset.csv',
        'data/processed/o_score_results.csv',
        'data/processed/workflow_analysis.csv',
        'data/processed/nlp_features.csv',
        'data/processed/dialog_acts.csv',
    ],
    T['rows']:        _rows_en if lang == 'en' else _rows_de,
    T['cols']:        ['58', '60', '19', '6', '9', '9', '~15', '6', '~15', '7'],
    T['description']: _desc_en if lang == 'en' else _desc_de,
}

df_sources = pd.DataFrame(datasources)
st.dataframe(df_sources, use_container_width=True, hide_index=True)

# ── 5. Modell-Pipeline ─────────────────────────────────────────────────────
section_header(T['sec_pipeline'])

col1, col2 = st.columns([1, 1])

with col1:
    if lang == 'de':
        st.markdown("""
#### Q-Score Pipeline (subjektive Bewertung)
```
issues_snapshot_sample.xlsx (747 Samples)
    ↓ feature_engineering.py
    ├── create_time_features()      → total_hours, total_days
    ├── create_process_features()   → total_status_changes, is_complex
    ├── create_communication_features() → comments_count
    └── create_priority_features()  → priority_numeric
    ↓ ml_dataset.csv (603 valide Samples, 6 Features)
    ↓ ml_model_q.py
    ├── Train-Test Split (80/20, stratified)
    ├── StandardScaler (Standardisierung)
    ├── VotingClassifier (soft voting):
    │   ├── RandomForestClassifier (n=100, depth=6)
    │   ├── XGBClassifier (n=100, depth=6, lr=0.1)
    │   └── LGBMClassifier (n=100, depth=6, lr=0.1)
    └── 5-Fold Stratified Cross-Validation
    ↓ models/q_score_model.joblib
    ↓ (Optuna-Hyperparameter-Optimierung)
    ↓ models/optimized_scorer.joblib
```
        """)
    else:
        st.markdown("""
#### Q-Score Pipeline (subjective rating)
```
issues_snapshot_sample.xlsx (747 samples)
    ↓ feature_engineering.py
    ├── create_time_features()      → total_hours, total_days
    ├── create_process_features()   → total_status_changes, is_complex
    ├── create_communication_features() → comments_count
    └── create_priority_features()  → priority_numeric
    ↓ ml_dataset.csv (603 valid samples, 6 features)
    ↓ ml_model_q.py
    ├── Train-Test Split (80/20, stratified)
    ├── StandardScaler (standardization)
    ├── VotingClassifier (soft voting):
    │   ├── RandomForestClassifier (n=100, depth=6)
    │   ├── XGBClassifier (n=100, depth=6, lr=0.1)
    │   └── LGBMClassifier (n=100, depth=6, lr=0.1)
    └── 5-Fold Stratified Cross-Validation
    ↓ models/q_score_model.joblib
    ↓ (Optuna hyperparameter optimization)
    ↓ models/optimized_scorer.joblib
```
        """)

with col2:
    if lang == 'de':
        st.markdown("""
#### O-Score Pipeline (objektive Bewertung)
```
data/raw/issues_snapshot.csv (90.963 Zeilen)
    ↓ o_score.py
    ├── calculate_employee_metrics()
    │   ├── ticket_count (pro Mitarbeiter)
    │   ├── median_time_hours
    │   ├── avg_steps
    │   ├── avg_comments
    │   ├── reopen_rate
    │   ├── first_touch_rate
    │   └── success_rate
    ├── Gewichtetes Scoring:
    │   ├── quality_score (35%): Reopen + Success
    │   ├── efficiency_score (25%): Bearbeitungszeit
    │   ├── productivity_score (20%): Volumen + Schritte
    │   └── communication_score (20%): First-touch + Kommentare
    ├── o_score_raw → o_score (1–5, skaliert)
    ↓ data/processed/o_score_results.csv
    ↓ ml_model_o.py
    ├── discretize_o_score() (bins: [0,1.8,2.6,3.4,4.2,5.1])
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
    │   ├── ticket_count (per employee)
    │   ├── median_time_hours
    │   ├── avg_steps
    │   ├── avg_comments
    │   ├── reopen_rate
    │   ├── first_touch_rate
    │   └── success_rate
    ├── Weighted scoring:
    │   ├── quality_score (35%): Reopen + Success
    │   ├── efficiency_score (25%): Processing time
    │   ├── productivity_score (20%): Volume + Steps
    │   └── communication_score (20%): First-touch + Comments
    ├── o_score_raw → o_score (1–5, scaled)
    ↓ data/processed/o_score_results.csv
    ↓ ml_model_o.py
    ├── discretize_o_score() (bins: [0,1.8,2.6,3.4,4.2,5.1])
    ├── StandardScaler
    ├── VotingClassifier (RF+XGB+LGB)
    └── 5-Fold CV
    ↓ models/o_score_model.joblib
```
        """)

render_footer()
