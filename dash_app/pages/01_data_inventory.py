"""
Seite 01: Daten-Inventar
Übersicht über alle Datensätze.
"""
import dash
from dash import html, dcc, dash_table, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import (
    load_issues, load_snapshots, load_scored, load_utterances,
    load_ml_dataset, load_nlp_features, load_employee_metrics,
    load_workflow_analysis, DATA_DIR, PROJECT_ROOT
)

dash.register_page(__name__, path="/data-inventory", name="📊 Daten-Inventar", order=1)

DATASETS = [
    {"key": "issues",    "file": "raw/issues.csv",             "label": "Issues (Hauptdatensatz)", "loader": load_issues},
    {"key": "snap",      "file": "raw/issues_snapshot.csv",    "label": "Issues Snapshots",         "loader": load_snapshots},
    {"key": "scored",    "file": "raw/issues_snapshot_sample.xlsx", "label": "Bewertete Samples",  "loader": load_scored},
    {"key": "utt",       "file": "raw/sample_utterances.csv",  "label": "Beispiel-Äußerungen",     "loader": load_utterances},
    {"key": "ml",        "file": "processed/ml_dataset.csv",   "label": "ML-Datensatz",             "loader": load_ml_dataset},
    {"key": "nlp",       "file": "processed/nlp_features.csv", "label": "NLP Features",             "loader": load_nlp_features},
    {"key": "emp",       "file": "processed/employee_metrics_raw.csv", "label": "Mitarbeiter Metriken", "loader": load_employee_metrics},
    {"key": "wf",        "file": "processed/workflow_analysis.csv", "label": "Workflow Analyse",    "loader": load_workflow_analysis},
]


def load_all_info():
    rows = []
    for ds in DATASETS:
        path = DATA_DIR / ds["file"]
        exists = path.exists()
        size_kb = round(path.stat().st_size / 1024, 1) if exists else 0
        try:
            df = ds["loader"]()
            n_rows, n_cols = df.shape if not df.empty else (0, 0)
        except Exception:
            n_rows, n_cols = 0, 0
        rows.append({
            "Datensatz": ds["label"],
            "Datei": ds["file"],
            "Existiert": "✅" if exists else "❌",
            "Zeilen": n_rows,
            "Spalten": n_cols,
            "Größe (KB)": size_kb,
        })
    return pd.DataFrame(rows)


def layout():
    info_df = load_all_info()

    summary_cards = []
    for _, row in info_df.iterrows():
        color = "success" if row["Existiert"] == "✅" else "danger"
        summary_cards.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6(row["Datensatz"], className="card-title text-truncate"),
                        html.P(f"{row['Zeilen']:,} Zeilen · {row['Spalten']} Spalten",
                               className="card-text small text-muted"),
                        html.P(f"{row['Größe (KB)']} KB", className="card-text small"),
                        dbc.Badge(row["Existiert"], color=color),
                    ]),
                    className="kpi-card h-100",
                    style={"borderLeftColor": "#27ae60" if color == "success" else "#e74c3c"},
                ),
                md=3, className="mb-3"
            )
        )

    columns = [{"name": c, "id": c} for c in info_df.columns]
    table_data = info_df.to_dict("records")

    # Detail section for each dataset
    detail_tabs = []
    for ds in DATASETS:
        try:
            df = ds["loader"]()
        except Exception:
            df = pd.DataFrame()
        if df.empty:
            content = dbc.Alert("Datei nicht gefunden oder leer.", color="warning")
        else:
            preview = df.head(5)
            col_info = pd.DataFrame({
                "Spalte": df.columns,
                "Datentyp": df.dtypes.astype(str).values,
                "Nicht-Null": df.notna().sum().values,
                "Eindeutig": df.nunique().values,
                "Beispiel": [str(df[c].dropna().iloc[0]) if not df[c].dropna().empty else "" for c in df.columns],
            })
            content = html.Div([
                html.H6(f"{df.shape[0]:,} Zeilen × {df.shape[1]} Spalten", className="text-info mb-2"),
                html.P("Spalten-Übersicht:", className="fw-bold mb-1"),
                dash_table.DataTable(
                    data=col_info.to_dict("records"),
                    columns=[{"name": c, "id": c} for c in col_info.columns],
                    style_table={"overflowX": "auto", "fontSize": "0.8rem"},
                    style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
                    style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
                    page_size=10,
                ),
                html.P("Vorschau (erste 5 Zeilen):", className="fw-bold mt-3 mb-1"),
                dash_table.DataTable(
                    data=preview.to_dict("records"),
                    columns=[{"name": c, "id": c} for c in preview.columns],
                    style_table={"overflowX": "auto", "fontSize": "0.75rem"},
                    style_cell={"backgroundColor": "#2d3436", "color": "#ccc", "border": "1px solid #495057", "maxWidth": "150px", "overflow": "hidden", "textOverflow": "ellipsis"},
                    style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
                ),
            ])
        detail_tabs.append(dbc.Tab(content, label=ds["label"], tab_id=ds["key"]))

    return dbc.Container([
        html.H3("📊 Daten-Inventar", className="mb-1 text-warning"),
        html.P("Übersicht über alle Datensätze des Help Desk Performance Systems.", className="text-muted mb-4"),
        dbc.Row(summary_cards),
        html.Hr(className="border-secondary"),
        html.H5("Datensatz-Übersicht", className="text-info mb-3"),
        dash_table.DataTable(
            data=table_data,
            columns=columns,
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
            style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
            style_data_conditional=[
                {"if": {"filter_query": '{Existiert} = "❌"'}, "backgroundColor": "#3d1515"},
            ],
        ),
        html.Hr(className="border-secondary mt-4"),
        html.H5("Datensatz-Details", className="text-info mb-3"),
        dbc.Tabs(detail_tabs, active_tab="issues"),
    ], fluid=True, className="py-3")
