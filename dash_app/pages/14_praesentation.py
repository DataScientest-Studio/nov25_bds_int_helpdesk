"""
Seite 14: Präsentation
Projekt-Zusammenfassung und Präsentations-Folien.
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_issues, load_scored, load_ml_dataset, MODELS_DIR, PROJECT_ROOT

dash.register_page(__name__, path="/praesentation", name="🎬 Präsentation", order=14)

SLIDES = [
    {
        "title": "Help Desk Performance Monitor",
        "subtitle": "KI-gestütztes System zur Mitarbeiter-Performance-Analyse",
        "content": [
            "🎯 Ziel: Objektive Bewertung der Helpdesk-Mitarbeiter",
            "📊 Datenbasis: Öffentlicher Mendeley-Datensatz (Performance Appraisal)",
            "🤖 ML-Modell: Random Forest für Q-Score & O-Score-Vorhersage",
            "💬 NLP: Sentiment-Analyse & Dialog-Akt-Erkennung",
            "🔍 Bias-Analyse: Halo-Effekt & Leniency-Erkennung",
        ],
        "icon": "🎯",
    },
    {
        "title": "Datenbasis & Methodik",
        "subtitle": "Ausgangsdaten und Verarbeitungs-Pipeline",
        "content": [
            "📁 Issues-Datensatz: Alle Helpdesk-Tickets mit Workflow-Informationen",
            "📋 Snapshot-Datensatz: Ticket-Zustände zu verschiedenen Zeitpunkten",
            "⭐ Bewertungs-Datensatz: Manager-Ratings (Q1, Q2, Q3) für 1.000+ Samples",
            "💬 Äußerungs-Datensatz: Rohtext für NLP-Analyse",
            "🔄 Pipeline: Raw → Feature Engineering → ML-Training → Scoring",
        ],
        "icon": "📊",
    },
    {
        "title": "ML-Modell Performance",
        "subtitle": "Zwei komplementäre Scoring-Systeme",
        "content": [
            "Q-Score: Manager-Rating Vorhersage (Random Forest Classifier)",
            "O-Score: Objektives Scoring auf Basis messbarer KPIs",
            "Feature Engineering: 30+ Features aus Ticket-Metadaten",
            "Kreuzvalidierung: 5-fach, Stratified K-Fold",
            "Wichtigste Features: Bearbeitungszeit, Kommentaranzahl, Priorität",
        ],
        "icon": "🤖",
    },
    {
        "title": "Erkenntnisse & Insights",
        "subtitle": "Key Findings aus der Analyse",
        "content": [
            "🚨 Halo-Effekt: Viele Manager bewerten konsistent hoch/niedrig",
            "⚖️ Moderate Korrelation (r≈0.5) zwischen Q-Score & O-Score",
            "📈 Tendenz: Technische KPIs erklären ~60% der Manager-Bewertung",
            "🏆 Top-Performer: Kombination aus Effizienz + Kommunikationsqualität",
            "⚠️ Verbesserungspotenzial: ~25% der MA zeigen Trainingsbedarfe",
        ],
        "icon": "💡",
    },
    {
        "title": "Architektur & Technologie",
        "subtitle": "System-Architektur und Tech-Stack",
        "content": [
            "🐍 Python-Stack: pandas, scikit-learn, VADER NLP, plotly",
            "🗄️ Datenhaltung: SQLite DB + CSV-Dateien",
            "🤖 ML: Random Forest, Gradient Boosting, Pipeline",
            "💻 Frontend: Dash (Port 8502) + Streamlit (Port 8501)",
            "🔄 Deployment: systemd User Service, Git-Versionierung",
        ],
        "icon": "🏗️",
    },
]


def layout():
    issues = load_issues()
    scored = load_scored()
    ml_df = load_ml_dataset()

    # Quick stats
    n_tickets = len(issues)
    n_scored = len(scored)
    n_features = ml_df.shape[1] if not ml_df.empty else 0
    models_count = len(list(MODELS_DIR.glob("*.joblib")))

    # Build slide cards
    slide_cards = []
    for i, slide in enumerate(SLIDES):
        items = [html.Li(item, className="mb-1") for item in slide["content"]]
        slide_cards.append(
            dbc.Card([
                dbc.CardHeader([
                    html.Span(slide["icon"] + " ", className="me-1"),
                    html.Strong(f"Folie {i+1}: {slide['title']}"),
                ], className="border-bottom border-warning"),
                dbc.CardBody([
                    html.H6(slide["subtitle"], className="text-muted mb-3"),
                    html.Ul(items, className="mb-0"),
                ]),
            ], className="mb-4 border-secondary")
        )

    # Summary chart
    summary_fig = go.Figure(go.Bar(
        x=["Tickets", "Bewertet", "Features", "Modelle"],
        y=[n_tickets, n_scored, n_features, models_count],
        marker_color=["#f39c12", "#3498db", "#2ecc71", "#e74c3c"],
        text=[f"{v:,}" for v in [n_tickets, n_scored, n_features, models_count]],
        textposition='outside',
    ))
    summary_fig.update_layout(
        title="Projekt-Kennzahlen auf einen Blick",
        paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
        font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20),
    )

    # Process flow
    flow_fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20,
            label=["Rohdaten", "Feature Eng.", "ML Training", "Q-Score", "O-Score", "Dashboard"],
            color=["#f39c12", "#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#1abc9c"],
        ),
        link=dict(
            source=[0, 0, 1, 1, 2, 2],
            target=[1, 1, 2, 2, 3, 4],
            value=[50, 30, 40, 20, 30, 30],
        ),
    ))
    flow_fig.update_layout(
        title="Daten-Verarbeitungs-Flow",
        paper_bgcolor="#1a1a2e", font_color="#e0e0e0",
        margin=dict(t=50, b=20, l=20, r=20),
    )

    # Slide reports
    slide_imgs = []
    slides_dir = PROJECT_ROOT / "reports" / "slides"
    if slides_dir.exists():
        for img_path in sorted(slides_dir.glob("*.png"))[:5]:
            slide_imgs.append(dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.Img(
                            src=f"/assets/slides/{img_path.name}",
                            style={"width": "100%", "border-radius": "6px"},
                        ),
                        html.P(img_path.stem, className="text-muted small mt-1 text-center"),
                    ])
                ], className="border-secondary"),
                md=4, className="mb-3"
            ))

    return dbc.Container([
        html.H3("🎬 Präsentation", className="mb-1 text-warning"),
        html.P("Projekt-Zusammenfassung, Methodik und Key Findings.", className="text-muted mb-4"),

        # KPI banner
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H3(f"{n_tickets:,}", className="text-warning mb-0"),
                html.Small("Tickets analysiert", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#f39c12"}), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H3(f"{n_scored:,}", className="text-info mb-0"),
                html.Small("Bewertete Samples", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#3498db"}), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H3(str(n_features), className="text-success mb-0"),
                html.Small("ML-Features", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#2ecc71"}), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H3(str(models_count), className="text-danger mb-0"),
                html.Small("Trainierte Modelle", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#e74c3c"}), md=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=summary_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=flow_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        html.Hr(className="border-secondary"),
        html.H5("Präsentations-Folien", className="text-info mb-3"),

        *slide_cards,

        html.Hr(className="border-secondary") if slide_imgs else html.Div(),
        html.H5("Report-Slides", className="text-info mb-3") if slide_imgs else html.Div(),
        dbc.Row(slide_imgs) if slide_imgs else html.Div(),

        dbc.Alert([
            html.I(className="fa fa-graduation-cap me-2 text-warning"),
            html.Strong("Datascientest Projekt: "),
            "Diese Analyse entstand im Rahmen des DataScientest Data Science Bootcamps. "
            "Ziel war die Entwicklung eines vollständigen ML-Pipelines zur KI-gestützten "
            "Performance-Bewertung von Helpdesk-Mitarbeitern.",
        ], color="dark", className="border border-warning mt-3"),
    ], fluid=True, className="py-3")
