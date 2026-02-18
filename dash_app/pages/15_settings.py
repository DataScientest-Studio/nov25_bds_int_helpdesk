"""
Seite 15: Einstellungen
App-Konfiguration und System-Informationen.
"""
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import platform
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import (
    load_issues, load_scored, load_ml_dataset, list_db_tables,
    DATA_DIR, MODELS_DIR, PROJECT_ROOT, DB_PATH
)

dash.register_page(__name__, path="/settings", name="⚙️ Einstellungen", order=15)


def get_system_info():
    return {
        "Python Version": platform.python_version(),
        "OS": platform.system() + " " + platform.release(),
        "Dashboard Port": "8502",
        "App Framework": "Dash 4.x + dash-bootstrap-components",
        "Theme": "DARKLY",
        "Zeitzone": "Europe/Berlin",
        "Stand": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def get_data_info():
    info = {}
    issues = load_issues()
    scored = load_scored()
    ml = load_ml_dataset()

    info["Issues (Tickets)"] = f"{len(issues):,} Zeilen" if not issues.empty else "❌ Nicht geladen"
    info["Bewertete Samples"] = f"{len(scored):,} Zeilen" if not scored.empty else "❌ Nicht geladen"
    info["ML-Datensatz"] = f"{len(ml):,} Zeilen" if not ml.empty else "❌ Nicht geladen"
    info["SQLite-DB"] = "✅ Vorhanden" if DB_PATH.exists() else "❌ Nicht gefunden"
    tables = list_db_tables()
    info["DB-Tabellen"] = ", ".join(tables) if tables else "Keine"

    model_files = list(MODELS_DIR.glob("*.joblib"))
    info["Modelle gefunden"] = str(len(model_files))
    for mf in model_files:
        size_kb = round(mf.stat().st_size / 1024, 1)
        info[f"  {mf.name}"] = f"{size_kb} KB"

    return info


def layout():
    sys_info = get_system_info()
    data_info = get_data_info()

    sys_rows = [html.Tr([html.Td(k, className="text-muted"), html.Td(v, className="text-light")])
                for k, v in sys_info.items()]
    data_rows = [html.Tr([html.Td(k, className="text-muted small"), html.Td(v, className="text-light small")])
                 for k, v in data_info.items()]

    return dbc.Container([
        html.H3("⚙️ Einstellungen", className="mb-1 text-warning"),
        html.P("System-Informationen, Konfiguration und Diagnose.", className="text-muted mb-4"),

        dbc.Row([
            # System info
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fa fa-server me-2"), "System-Informationen"]),
                    dbc.CardBody(
                        dbc.Table(html.Tbody(sys_rows), bordered=False, size="sm",
                                  style={"backgroundColor": "transparent"})
                    ),
                ], className="mb-4 border-secondary"),
            ], md=6),

            # Data info
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fa fa-database me-2"), "Daten-Status"]),
                    dbc.CardBody(
                        dbc.Table(html.Tbody(data_rows), bordered=False, size="sm",
                                  style={"backgroundColor": "transparent"})
                    ),
                ], className="mb-4 border-secondary"),
            ], md=6),
        ]),

        # Navigation overview
        dbc.Card([
            dbc.CardHeader([html.I(className="fa fa-map me-2"), "Seiten-Übersicht"]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ListGroup([
                            dbc.ListGroupItem([html.I(className="fa fa-database me-2 text-warning"), "Daten-Inventar"], href="/data-inventory", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-home me-2 text-warning"), "Dashboard"], href="/dashboard", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-ticket-alt me-2 text-warning"), "Ticket Monitor"], href="/ticket-monitor", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-users me-2 text-warning"), "Mitarbeiter Performance"], href="/mitarbeiter", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-dumbbell me-2 text-warning"), "Training & Defizite"], href="/training", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-search me-2 text-warning"), "Objektivitätsprüfung"], href="/objektivitaet", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-comments me-2 text-warning"), "Kommunikation & NLP"], href="/nlp", color="dark", className="border-secondary"),
                        ], flush=True),
                    ], md=6),
                    dbc.Col([
                        dbc.ListGroup([
                            dbc.ListGroupItem([html.I(className="fa fa-sync-alt me-2 text-info"), "Prozess Compliance"], href="/compliance", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-brain me-2 text-info"), "ML Modell Details"], href="/ml-modell", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-chart-line me-2 text-info"), "Trend Analyse"], href="/trends", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-file-export me-2 text-info"), "Export Center"], href="/export", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-comment-dots me-2 text-info"), "Dialog Analyse"], href="/dialog", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-balance-scale me-2 text-info"), "Score Vergleich"], href="/score-vergleich", color="dark", className="border-secondary"),
                            dbc.ListGroupItem([html.I(className="fa fa-film me-2 text-info"), "Präsentation"], href="/praesentation", color="dark", className="border-secondary"),
                        ], flush=True),
                    ], md=6),
                ]),
            ]),
        ], className="mb-4 border-secondary"),

        # About
        dbc.Card([
            dbc.CardHeader([html.I(className="fa fa-info-circle me-2"), "Über dieses Dashboard"]),
            dbc.CardBody([
                html.P([
                    "Das ", html.Strong("Help Desk Performance Monitor"), " Dashboard wurde als ",
                    html.Strong("Dash-App"), " auf Basis des DataScientest-Projekts entwickelt. ",
                    "Es ist das Schwester-Dashboard zum Streamlit-Original (Port 8501).",
                ]),
                html.P([
                    "📌 ", html.Strong("Port:"), " 8502  |  ",
                    "🔗 ", html.Strong("Framework:"), " Dash 4.x + Bootstrap (DARKLY)  |  ",
                    "📊 ", html.Strong("Daten:"), " Mendeley Dataset (Performance Appraisal)",
                ], className="text-muted small"),
                dbc.Row([
                    dbc.Col(dbc.Button([html.I(className="fa fa-home me-1"), " Dashboard"], href="/dashboard",
                                       color="warning", size="sm"), md=2),
                    dbc.Col(dbc.Button([html.I(className="fa fa-database me-1"), " Daten"], href="/data-inventory",
                                       color="info", size="sm", outline=True), md=2),
                    dbc.Col(dbc.Button([html.I(className="fa fa-brain me-1"), " ML-Modell"], href="/ml-modell",
                                       color="secondary", size="sm", outline=True), md=2),
                ], className="mt-3"),
            ]),
        ], className="border-secondary"),
    ], fluid=True, className="py-3")
