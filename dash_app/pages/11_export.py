"""
Seite 11: Export Center
Daten-Export in verschiedenen Formaten.
"""
import dash
from dash import html, dcc, dash_table, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import io
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import (
    load_issues, load_scored, load_ml_dataset, load_nlp_features,
    load_workflow_analysis, load_employee_metrics
)

dash.register_page(__name__, path="/export", name="📥 Export Center", order=11)

EXPORT_DATASETS = {
    "issues": ("Issues (Hauptdatensatz)", load_issues),
    "scored": ("Bewertete Samples", load_scored),
    "ml_dataset": ("ML-Datensatz", load_ml_dataset),
    "nlp_features": ("NLP Features", load_nlp_features),
    "workflow": ("Workflow-Analyse", load_workflow_analysis),
    "employees": ("Mitarbeiter-Metriken", load_employee_metrics),
}


def layout():
    dataset_cards = []
    for key, (label, loader) in EXPORT_DATASETS.items():
        try:
            df = loader()
            rows, cols = df.shape if not df.empty else (0, 0)
            status = "✅ Verfügbar" if not df.empty else "❌ Leer"
            color = "success" if not df.empty else "danger"
        except Exception:
            rows, cols = 0, 0
            status = "❌ Fehler"
            color = "danger"
        dataset_cards.append(dbc.Col(
            dbc.Card(dbc.CardBody([
                html.H6(label, className="card-title"),
                dbc.Badge(status, color=color, className="mb-2"),
                html.P(f"{rows:,} Zeilen · {cols} Spalten", className="small text-muted mb-2"),
                dbc.Button(f"⬇️ {label}", id=f"export-btn-{key}",
                           color="warning", size="sm", outline=True, className="me-1"),
                dcc.Download(id=f"export-dl-{key}"),
            ]), className="kpi-card h-100"),
            md=4, className="mb-3"
        ))

    return dbc.Container([
        html.H3("📥 Export Center", className="mb-1 text-warning"),
        html.P("Exportiere alle Datensätze als CSV-Dateien.", className="text-muted mb-4"),
        html.H5("Verfügbare Datensätze", className="text-info mb-3"),
        dbc.Row(dataset_cards),
        html.Hr(className="border-secondary mt-2"),
        html.H5("Datensatz-Vorschau", className="text-info mb-3"),
        dbc.Row([
            dbc.Col([
                html.Label("Datensatz auswählen", className="small text-muted"),
                dcc.Dropdown(
                    id="export-preview-select",
                    options=[{"label": v[0], "value": k} for k, v in EXPORT_DATASETS.items()],
                    value="issues",
                    style={"backgroundColor": "#2d3436", "color": "#000"},
                    clearable=False,
                ),
            ], md=4),
        ], className="mb-3"),
        html.Div(id="export-preview-table"),
    ], fluid=True, className="py-3")


# Preview callback
@callback(
    Output("export-preview-table", "children"),
    Input("export-preview-select", "value"),
)
def update_preview(key):
    if key not in EXPORT_DATASETS:
        return dbc.Alert("Unbekannter Datensatz.", color="warning")
    _, loader = EXPORT_DATASETS[key]
    df = loader()
    if df.empty:
        return dbc.Alert("Datensatz leer oder nicht verfügbar.", color="warning")
    preview = df.head(20)
    return html.Div([
        html.P(f"Vorschau: {df.shape[0]:,} Zeilen × {df.shape[1]} Spalten", className="text-muted small"),
        dash_table.DataTable(
            data=preview.to_dict("records"),
            columns=[{"name": c, "id": c} for c in preview.columns],
            page_size=10,
            style_table={"overflowX": "auto", "fontSize": "0.8rem"},
            style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0",
                        "border": "1px solid #495057", "maxWidth": "150px",
                        "overflow": "hidden", "textOverflow": "ellipsis"},
            style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
        )
    ])


# Download callbacks (one per dataset)
@callback(Output("export-dl-issues", "data"), Input("export-btn-issues", "n_clicks"), prevent_initial_call=True)
def dl_issues(n):
    df = load_issues()
    if df.empty: return None
    buf = io.StringIO(); df.to_csv(buf, index=False)
    return {"content": buf.getvalue(), "filename": "issues_export.csv"}

@callback(Output("export-dl-scored", "data"), Input("export-btn-scored", "n_clicks"), prevent_initial_call=True)
def dl_scored(n):
    df = load_scored()
    if df.empty: return None
    buf = io.StringIO(); df.to_csv(buf, index=False)
    return {"content": buf.getvalue(), "filename": "scored_export.csv"}

@callback(Output("export-dl-ml_dataset", "data"), Input("export-btn-ml_dataset", "n_clicks"), prevent_initial_call=True)
def dl_ml(n):
    df = load_ml_dataset()
    if df.empty: return None
    buf = io.StringIO(); df.to_csv(buf, index=False)
    return {"content": buf.getvalue(), "filename": "ml_dataset_export.csv"}

@callback(Output("export-dl-nlp_features", "data"), Input("export-btn-nlp_features", "n_clicks"), prevent_initial_call=True)
def dl_nlp(n):
    df = load_nlp_features()
    if df.empty: return None
    buf = io.StringIO(); df.to_csv(buf, index=False)
    return {"content": buf.getvalue(), "filename": "nlp_features_export.csv"}

@callback(Output("export-dl-workflow", "data"), Input("export-btn-workflow", "n_clicks"), prevent_initial_call=True)
def dl_workflow(n):
    df = load_workflow_analysis()
    if df.empty: return None
    buf = io.StringIO(); df.to_csv(buf, index=False)
    return {"content": buf.getvalue(), "filename": "workflow_export.csv"}

@callback(Output("export-dl-employees", "data"), Input("export-btn-employees", "n_clicks"), prevent_initial_call=True)
def dl_employees(n):
    df = load_employee_metrics()
    if df.empty: return None
    buf = io.StringIO(); df.to_csv(buf, index=False)
    return {"content": buf.getvalue(), "filename": "employees_export.csv"}
