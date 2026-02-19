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
        'sec_components': '🧩 Komponentenübersicht',
        'sec_datasources': '📂 Datenquellen',
        'sec_pipeline': '🤖 Modell-Pipeline',
        'sec_dashboard': '📊 Dashboard-Architektur',
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
        'components_title': 'Alle Module und ihre Rolle',
        'datasources_title': 'Rohdateien und verarbeitete Daten',
        'pipeline_title': 'ML-Trainings-Pipeline im Detail',
        'dashboard_title': 'Streamlit-Seiten und ihre Funktion',
        'file': 'Datei',
        'rows': 'Zeilen',
        'cols': 'Spalten',
        'description': 'Beschreibung',
        'module': 'Modul',
        'role': 'Rolle',
        'inputs': 'Eingaben',
        'outputs': 'Ausgaben',
        'page': 'Seite',
        'content': 'Inhalt',
    },
    'en': {
        'title': '🏗️ Project Architecture',
        'subtitle': 'System overview, data flow and component structure of the Helpdesk ML Dashboard',
        'sec_overview': '📋 Project Overview',
        'sec_dataflow': '🔄 Data Flow Diagram',
        'sec_components': '🧩 Component Overview',
        'sec_datasources': '📂 Data Sources',
        'sec_pipeline': '🤖 Model Pipeline',
        'sec_dashboard': '📊 Dashboard Architecture',
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
        'components_title': 'All Modules and Their Role',
        'datasources_title': 'Raw Files and Processed Data',
        'pipeline_title': 'ML Training Pipeline in Detail',
        'dashboard_title': 'Streamlit Pages and Their Function',
        'file': 'File',
        'rows': 'Rows',
        'cols': 'Columns',
        'description': 'Description',
        'module': 'Module',
        'role': 'Role',
        'inputs': 'Inputs',
        'outputs': 'Outputs',
        'page': 'Page',
        'content': 'Content',
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

# Graphviz-Diagramm des Datenflusses
st.graphviz_chart("""
digraph dataflow {
    rankdir=LR;
    node [shape=box, style=filled, fontname="Arial", fontsize=11];

    subgraph cluster_raw {
        label="Raw Data";
        style=filled;
        color=lightgrey;
        issues [label="issues.csv\\n(66.691 Zeilen)", fillcolor="#AED6F1"];
        snapshot [label="issues_snapshot.csv\\n(90.963 Zeilen)", fillcolor="#AED6F1"];
        sample [label="issues_snapshot_sample.xlsx\\n(747 Zeilen, Ground Truth)", fillcolor="#A9DFBF"];
        utterances [label="sample_utterances.csv\\n(30.104 Zeilen)", fillcolor="#AED6F1"];
        history [label="issues_change_history.csv\\n(257.508 Zeilen)", fillcolor="#AED6F1"];
    }

    subgraph cluster_processing {
        label="Processing";
        style=filled;
        color="#FEF9E7";
        data_loader [label="data_loader.py\\nLädt alle Datensätze", fillcolor="#FAD7A0"];
        feat_eng [label="feature_engineering.py\\nErstellt ML-Features", fillcolor="#FAD7A0"];
        o_score [label="o_score.py\\nBerechnet O-Score", fillcolor="#FAD7A0"];
        nlp [label="nlp_analysis.py\\nSentiment & Patterns", fillcolor="#F9E79F"];
        dialog [label="dialog_analysis.py\\nDialog-Act Klassifikation", fillcolor="#F9E79F"];
        compliance [label="process_compliance.py\\nWorkflow-Analyse", fillcolor="#F9E79F"];
        bias [label="bias_analysis.py\\nBias-Erkennung", fillcolor="#F9E79F"];
        trends [label="trend_analysis.py\\nPerformance-Trends", fillcolor="#F9E79F"];
        deficits [label="training_deficits.py\\nSchulungsbedarf", fillcolor="#F9E79F"];
    }

    subgraph cluster_ml {
        label="ML Training";
        style=filled;
        color="#FDEDEC";
        ml_model [label="ml_model.py\\n(Basis-Ensemble)", fillcolor="#F1948A"];
        ml_model_q [label="ml_model_q.py\\n(Q-Score mit QWK)", fillcolor="#F1948A"];
        ml_model_o [label="ml_model_o.py\\n(O-Score Classifier)", fillcolor="#F1948A"];
    }

    subgraph cluster_models {
        label="Saved Models";
        style=filled;
        color="#EBF5FB";
        perf_scorer [label="performance_scorer.joblib\\n(RF+XGB+LGB Ensemble)", fillcolor="#85C1E9"];
        q_score_model [label="q_score_model.joblib\\n(RF+XGB+LGB, QWK)", fillcolor="#85C1E9"];
        o_score_model [label="o_score_model.joblib\\n(RF+XGB+LGB Classifier)", fillcolor="#85C1E9"];
        optimized [label="optimized_scorer.joblib\\n(XGB+LGB, Optuna-optimiert)", fillcolor="#5DADE2"];
    }

    subgraph cluster_dashboard {
        label="Streamlit Dashboard (Port 8501)";
        style=filled;
        color="#E9F7EF";
        dashboard [label="app.py\\nHauptanwendung", fillcolor="#82E0AA"];
        pages [label="pages/ (7 Seiten)\\nOverview, Tickets, People...\\nArchitecture, IO-Docs, Export, Settings", fillcolor="#82E0AA"];
        settings_comp [label="components/settings.py\\nÜbersetzungen, Navigation, UI", fillcolor="#A9DFBF"];
    }

    // Fluss
    issues -> data_loader;
    snapshot -> data_loader;
    sample -> data_loader;
    utterances -> data_loader;
    history -> data_loader;

    data_loader -> feat_eng;
    data_loader -> o_score;
    data_loader -> nlp;
    data_loader -> dialog;
    data_loader -> compliance;
    data_loader -> bias;
    data_loader -> trends;
    data_loader -> deficits;

    feat_eng -> ml_model;
    feat_eng -> ml_model_q;
    o_score -> ml_model_o;

    ml_model -> perf_scorer;
    ml_model_q -> q_score_model;
    ml_model_o -> o_score_model;
    ml_model_q -> optimized;

    perf_scorer -> dashboard;
    q_score_model -> dashboard;
    o_score_model -> dashboard;
    optimized -> dashboard;

    data_loader -> dashboard;
    o_score -> dashboard;
    nlp -> dashboard;
    dialog -> dashboard;
    compliance -> dashboard;
    bias -> dashboard;
    trends -> dashboard;
    deficits -> dashboard;

    dashboard -> pages;
    settings_comp -> pages;
}
""", use_container_width=True)

# ── 3. Komponentenübersicht ────────────────────────────────────────────────
section_header(T['sec_components'])

components_data = {
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
        'streamlit_app/app.py',
        'streamlit_app/components/settings.py',
        'streamlit_app/pages/01_🏠_Overview.py',
        'streamlit_app/pages/02_🎫_Tickets.py',
        'streamlit_app/pages/03_👥_People.py',
        'streamlit_app/pages/04_📊_Performance_Scores.py',
        'streamlit_app/pages/05_💼_Operations.py',
        'streamlit_app/pages/10_🏗️_Architecture.py',
        'streamlit_app/pages/11_📋_IO_Documentation.py',
        'streamlit_app/pages/22_📥_Export.py',
        'streamlit_app/pages/23_⚙️_Settings.py',
    ],
    T['role']: [
        'Lädt alle 5 Rohdatensätze (CSV/Excel)',
        'Feature Engineering für ML-Modelle (Zeit, Prozess, Kommunikation, Priorität)',
        'Basismodell: VotingClassifier (RF+XGB+LGB) für Q1/Q2/Q3',
        'Verbessertes Q-Score-Modell mit Quadratic Weighted Kappa (QWK)',
        'O-Score Klassifikator (klassen 1-5, Ensemble-Modell)',
        'Berechnet objektiven Performance-Score (Qualität 35%, Effizienz 25%, Produktivität 20%, Kommunikation 20%)',
        'Erkennt Rating-Biases: Halo-Effekt, Leniency, Central Tendency',
        'Sentiment-Analyse (VADER) und Kommunikationsmuster aus Kommentaren',
        'Identifiziert Schulungsbedarf (GREEN/YELLOW/RED Klassifizierung)',
        'Prüft Workflow-Compliance auf Basis von wfe_*-Spalten',
        'Berechnet Performance-Trends und Top/Bottom-Performer',
        'Klassifiziert Dialog-Akte in Kommentaren (Frage, Beschwerde, Dank, etc.)',
        'Erzeugt 10 Visualisierungen als PNG (300 dpi) für Berichte',
        'Konvertiert Markdown-Berichte zu PDF (via WeasyPrint)',
        'Streamlit-Hauptanwendung, Einstiegspunkt',
        'UI-Komponenten: Übersetzungen (DE/EN), Navigation, Header, Footer',
        'A) Tickets & Menschen Snapshot — Live-Übersicht, KPIs',
        'B) Ticket-Analyse — Status, Priorität, Typen, Zeitverteilung',
        'C) Mitarbeiter-Analyse — Leistungsübersicht, Vergleiche',
        'D) Performance Scores — Q-Score, O-Score, ML-Vorhersagen',
        'E) Operations — Workflow, Compliance, Trend-Analyse',
        'Projektarchitektur (diese Seite)',
        'I/O-Dokumentation und Hyperparameter',
        'F) Export — PDF/CSV Berichte',
        'G) Einstellungen — Seiten-Sichtbarkeit, System-Info',
    ],
    T['inputs']: [
        'data/raw/*.csv, data/raw/*.xlsx',
        'issues_snapshot_sample.xlsx (Ground Truth)',
        'data/processed/ml_dataset.csv',
        'data/processed/ml_dataset.csv',
        'data/processed/o_score_results.csv',
        'data/raw/issues_snapshot.csv',
        'issues_snapshot_sample.xlsx',
        'data/raw/sample_utterances.csv',
        'issues_snapshot_sample.xlsx',
        'data/raw/issues.csv (wfe_*-Spalten)',
        'issues_snapshot_sample.xlsx',
        'data/raw/sample_utterances.csv',
        'data/processed/ml_dataset.csv, models/*.joblib',
        'reports/*.md, reports/plots/*.png',
        '— (Startpunkt)',
        '— (Konfiguration)',
        'data/helpdesk.db, models/*.joblib',
        'data/helpdesk.db, models/*.joblib',
        'models/*.joblib, data/raw/issues_snapshot_sample.xlsx',
        'models/*.joblib, data/processed/o_score_results.csv',
        'data/raw/issues.csv, data/processed/workflow_analysis.csv',
        '—',
        'models/*.joblib (Hyperparameter)',
        'data/processed/*.csv, models/*.joblib',
        '—',
    ],
    T['outputs']: [
        'dict mit DataFrames (issues, snapshots, history, scored, utterances)',
        'X (Features), y (Q1/Q2/Q3), data/processed/ml_dataset.csv',
        'models/performance_scorer.joblib',
        'models/q_score_model.joblib',
        'models/o_score_model.joblib',
        'data/processed/o_score_results.csv, q_vs_o_comparison.csv',
        'dict: distribution, halo_effect, leniency, central_tendency',
        'data/processed/nlp_features.csv',
        'reports/training_report.csv',
        'data/processed/workflow_analysis.csv',
        'reports/trend_analysis.csv',
        'data/processed/dialog_acts.csv',
        'reports/plots/01_*.png … 10_*.png',
        'reports/*.html, reports/*.pdf',
        'Streamlit-App auf Port 8501',
        'Übersetzungen, get_text(), render_*(), e(), maybe_emoji()',
        'Live-Dashboard mit KPIs und Ticket-Tabelle',
        'Ticket-Visualisierungen und Filteransichten',
        'Mitarbeiter-Ranking und Detailansichten',
        'Score-Vergleich, ML-Vorhersage-Interface',
        'Workflow-Charts, Compliance-Analyse, Trends',
        'Architektur-Diagramme und Tabellen',
        'I/O-Dokumentation, Hyperparameter-Tabellen',
        'CSV/PDF-Download der Berichte',
        'Seiten-Sichtbarkeit-Konfiguration, System-Info',
    ],
}

df_components = pd.DataFrame(components_data)
st.dataframe(df_components, use_container_width=True, hide_index=True,
             column_config={
                 T['module']: st.column_config.TextColumn(width="medium"),
                 T['role']: st.column_config.TextColumn(width="large"),
                 T['inputs']: st.column_config.TextColumn(width="medium"),
                 T['outputs']: st.column_config.TextColumn(width="medium"),
             })

# ── 4. Datenquellen ────────────────────────────────────────────────────────
section_header(T['sec_datasources'])

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
    T['rows']: [
        '66.691', '90.963', '747', '257.508', '30.104',
        '603', '~variabel', '~variabel', '~variabel', '~variabel'
    ],
    T['cols']: [
        '58', '60', '19', '6', '9',
        '9', '~15', '6', '~15', '7'
    ],
    T['description']: [
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
    ],
}

df_sources = pd.DataFrame(datasources)
st.dataframe(df_sources, use_container_width=True, hide_index=True)

# Spaltenübersicht der wichtigsten Datei
st.markdown("---")
if lang == 'de':
    st.markdown("**Spalten `issues.csv` (58 Spalten):**")
else:
    st.markdown("**Columns `issues.csv` (58 columns):**")

issues_cols = [
    'id', 'started', 'ended', 'issue_num', 'issue_proj', 'issue_reporter', 'issue_assignee',
    'issue_contr_count', 'issue_type', 'issue_priority', 'issue_created', 'issue_resolution_date',
    'issue_resolution', 'issue_status', 'issue_comments_count', 'last_change_date',
    'wf_in_review', 'wfe_in_review', 'wf_deployment', 'wfe_deployment', 'wf_resolved', 'wfe_resolved',
    'wf_open', 'wfe_open', 'wf_monitoring', 'wfe_monitoring', 'wf_done', 'wfe_done',
    'wf_pending_customer_approval', 'wfe_pending_customer_approval', 'wf_rejected', 'wfe_rejected',
    'wf_testing_monitoring', 'wfe_testing_monitoring', 'wf_in_progress', 'wfe_in_progress',
    'wf_reopened', 'wfe_reopened', 'wf_to_do', 'wfe_to_do', 'wf_validation', 'wfe_validation',
    'wf_resolved_under_monitoring', 'wfe_resolved_under_monitoring', 'wf_closed', 'wfe_closed',
    'wf_waiting', 'wfe_waiting', 'wf_cancelled', 'wfe_cancelled', 'wf_under_review', 'wfe_under_review',
    'wf_approved', 'wfe_approved', 'wf_pending_deployment', 'wfe_pending_deployment',
    'wf_total_time', 'processing_steps'
]
st.code(', '.join(issues_cols), language=None)

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
    ↓ models/performance_scorer.joblib (identisch)
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
    ↓ models/performance_scorer.joblib (identical)
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

# Feature Importance Tabelle
st.markdown("---")
if lang == 'de':
    st.markdown("#### Feature-Importance (aus RF-Komponente der Modelle)")
    st.markdown("**Q-Score-Modell (performance_scorer / q_score_model) — 6 Features:**")
else:
    st.markdown("#### Feature Importance (from RF component of models)")
    st.markdown("**Q-Score Model (performance_scorer / q_score_model) — 6 Features:**")

feat_imp_q = pd.DataFrame({
    'Feature': ['spent_hours', 'comments_count', 'turn_no', 'steps', 'contributors', 'priority_numeric'],
    'Importance (Q1)': [0.4534, 0.2529, 0.1205, 0.1105, 0.0440, 0.0188],
    'Rang': [1, 2, 3, 4, 5, 6],
})
st.dataframe(feat_imp_q, use_container_width=True, hide_index=True)

if lang == 'de':
    st.markdown("**O-Score-Modell — 7 Features:**")
else:
    st.markdown("**O-Score Model — 7 Features:**")

feat_imp_o = pd.DataFrame({
    'Feature': ['median_time_hours', 'avg_comments', 'ticket_count', 'first_touch_rate',
                'reopen_rate', 'success_rate', 'avg_steps'],
    'Importance': [0.3007, 0.1655, 0.1323, 0.1176, 0.1119, 0.0925, 0.0795],
    'Rang': [1, 2, 3, 4, 5, 6, 7],
})
st.dataframe(feat_imp_o, use_container_width=True, hide_index=True)

# ── 6. Dashboard-Architektur ───────────────────────────────────────────────
section_header(T['sec_dashboard'])

dashboard_pages = {
    T['page']: [
        '01_🏠_Overview.py',
        '02_🎫_Tickets.py',
        '03_👥_People.py',
        '04_📊_Performance_Scores.py',
        '05_💼_Operations.py',
        '10_🏗️_Architecture.py',
        '11_📋_IO_Documentation.py',
        '22_📥_Export.py',
        '23_⚙️_Settings.py',
    ],
    T['content']: [
        'A) Tickets & Menschen Snapshot — Live-KPIs, Auto-Refresh, Ticket-Tabelle, Mitarbeiter-Übersicht',
        'B) Ticket-Analyse — Status-Verteilung, Priorität, Ticket-Typen, Zeitverteilung, SLA-Analyse',
        'C) Mitarbeiter-Analyse — Leistungsranking, Top-/Bottom-Performer, Mitarbeiter-Detailansicht',
        'D) Performance Scores — Q-Score/O-Score-Vergleich, ML-Vorhersage, Bias-Analyse, Halo-Effekt',
        'E) Operations — Workflow-Compliance, Prozess-Analyse, Dialog-Akte, Trend-Analyse',
        'Projektarchitektur — System-Überblick, Datenfluß, Komponenten, Modell-Pipeline (diese Seite)',
        'I/O-Dokumentation — Inputs/Outputs aller Module, ML-Hyperparameter, Feature Importance',
        'F) Export — CSV-Downloads, PDF-Berichte, Report-Generierung',
        'G) Einstellungen — Seiten-Sichtbarkeit, System-Info, Service-Status, Sprache/Emoji-Toggles',
    ],
    'Status': [
        '✅ Aktiv', '✅ Aktiv', '✅ Aktiv', '✅ Aktiv', '✅ Aktiv',
        '✅ Neu', '✅ Neu', '✅ Aktiv', '✅ Aktiv'
    ],
}

df_dashboard = pd.DataFrame(dashboard_pages)
st.dataframe(df_dashboard, use_container_width=True, hide_index=True)

st.markdown("---")
if lang == 'de':
    st.info("""
    **Komponentenstruktur im Überblick:**
    - `streamlit_app/app.py` — Einstiegspunkt, wird von systemd als Service gestartet
    - `streamlit_app/components/settings.py` — Zentrale Konfiguration: Übersetzungen, Navigation, UI-Helfer
    - `streamlit_app/pages/` — Alle Unterseiten, sortiert nach Nummerierung im Dateinamen
    - Sidebar: Navigation, Sprach-Toggle (DE/EN), Emoji-Toggle via `render_settings_sidebar()`
    """)
else:
    st.info("""
    **Component structure at a glance:**
    - `streamlit_app/app.py` — Entry point, started by systemd as a service
    - `streamlit_app/components/settings.py` — Central config: translations, navigation, UI helpers
    - `streamlit_app/pages/` — All subpages, sorted by number prefix in filename
    - Sidebar: navigation, language toggle (DE/EN), emoji toggle via `render_settings_sidebar()`
    """)

render_footer()
