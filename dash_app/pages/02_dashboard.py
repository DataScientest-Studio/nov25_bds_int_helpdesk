"""
Seite 02: Live Dashboard
Echtzeit-Übersicht über KPIs.
"""
import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import (
    load_issues, load_scored, load_ml_dataset, load_employee_metrics, MODELS_DIR
)

dash.register_page(__name__, path="/dashboard", name="🏠 Dashboard", order=2)


def get_kpis(issues, scored, ml):
    total = len(issues) if not issues.empty else 0
    avg_time = round(issues['wf_total_time'].mean() / 3600, 1) if not issues.empty and 'wf_total_time' in issues.columns else 0
    n_scored = len(scored) if not scored.empty else 0
    avg_score = round(scored['Q1'].mean(), 2) if not scored.empty and 'Q1' in scored.columns else 0
    return total, avg_time, n_scored, avg_score


def make_kpi_card(title, value, icon, color="#f39c12", sub=None):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"fa {icon} fa-2x mb-2", style={"color": color}),
                html.H2(str(value), className="kpi-value mb-0", style={"color": color}),
                html.P(title, className="text-muted mb-0 small"),
                html.Small(sub or "", className="text-secondary"),
            ], className="text-center")
        ]),
        className="kpi-card shadow-sm h-100",
        style={"borderLeftColor": color},
    )


def layout():
    issues = load_issues()
    scored = load_scored()
    ml = load_ml_dataset()
    emp = load_employee_metrics()

    total, avg_time, n_scored, avg_score = get_kpis(issues, scored, ml)

    # Model status
    model_exists = (MODELS_DIR / "q_score_model.joblib").exists()
    model_badge = dbc.Badge("✅ Modell trainiert", color="success") if model_exists else dbc.Badge("❌ Kein Modell", color="danger")

    # Score distribution chart
    score_fig = go.Figure()
    if not scored.empty and 'Q1' in scored.columns:
        score_fig = px.histogram(
            scored, x='Q1', nbins=10,
            title="Score-Verteilung (Q1 - Manager-Bewertung)",
            color_discrete_sequence=["#f39c12"],
            labels={"Q1": "Score", "count": "Anzahl"},
        )
        score_fig.update_layout(
            paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
            font_color="#e0e0e0", title_font_color="#f8f9fa",
            margin=dict(t=50, b=30, l=30, r=20),
        )

    # Priority chart
    prio_fig = go.Figure()
    if not issues.empty and 'issue_priority' in issues.columns:
        prio_counts = issues['issue_priority'].value_counts()
        prio_fig = px.pie(
            values=prio_counts.values,
            names=prio_counts.index,
            title="Ticket-Prioritäten",
            color_discrete_sequence=px.colors.sequential.Oranges_r,
        )
        prio_fig.update_layout(
            paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
            font_color="#e0e0e0", title_font_color="#f8f9fa",
            margin=dict(t=50, b=10, l=10, r=10),
        )

    # Status chart
    status_fig = go.Figure()
    if not issues.empty and 'issue_status' in issues.columns:
        sc = issues['issue_status'].value_counts().head(8)
        status_fig = px.bar(
            x=sc.values, y=sc.index, orientation='h',
            title="Ticket-Status Übersicht",
            color_discrete_sequence=["#2ecc71"],
            labels={"x": "Anzahl", "y": "Status"},
        )
        status_fig.update_layout(
            paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
            font_color="#e0e0e0", title_font_color="#f8f9fa",
            margin=dict(t=50, b=30, l=30, r=20),
        )

    # Employee performance chart
    emp_fig = go.Figure()
    if not emp.empty:
        # look for relevant columns
        for col in ['issue_assignee', 'assignee']:
            if col in emp.columns:
                grp = emp.groupby(col).size().nlargest(10)
                emp_fig = px.bar(
                    x=grp.values, y=grp.index, orientation='h',
                    title="Top Mitarbeiter (Ticket-Anzahl)",
                    color_discrete_sequence=["#3498db"],
                )
                emp_fig.update_layout(
                    paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                    font_color="#e0e0e0", title_font_color="#f8f9fa",
                    margin=dict(t=50, b=30, l=30, r=20),
                )
                break
    elif not issues.empty and 'issue_assignee' in issues.columns:
        grp = issues['issue_assignee'].value_counts().head(10)
        emp_fig = px.bar(
            x=grp.values, y=grp.index, orientation='h',
            title="Top Mitarbeiter (Ticket-Anzahl)",
            color_discrete_sequence=["#3498db"],
        )
        emp_fig.update_layout(
            paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
            font_color="#e0e0e0", title_font_color="#f8f9fa",
            margin=dict(t=50, b=30, l=30, r=20),
        )

    return dbc.Container([
        html.H3("🏠 Live Dashboard", className="mb-1 text-warning"),
        html.P("KI-gestützte Echtzeit-Übersicht der Helpdesk-Performance.", className="text-muted mb-4"),

        # KPI row
        dbc.Row([
            dbc.Col(make_kpi_card("Total Tickets", f"{total:,}", "fa-ticket-alt", "#f39c12"), md=3, className="mb-3"),
            dbc.Col(make_kpi_card("Ø Bearbeitungszeit", f"{avg_time}h", "fa-clock", "#3498db"), md=3, className="mb-3"),
            dbc.Col(make_kpi_card("Bewertete Samples", f"{n_scored:,}", "fa-check-circle", "#2ecc71"), md=3, className="mb-3"),
            dbc.Col(make_kpi_card("Ø Score (Q1)", f"{avg_score}", "fa-star", "#e74c3c"), md=3, className="mb-3"),
        ]),

        # ML Model status bar
        dbc.Row([
            dbc.Col(
                dbc.Alert([
                    html.I(className="fa fa-brain me-2"),
                    "ML-Modell Status: ", model_badge,
                    html.Span(f"  |  Datenbasis: {total:,} Tickets · {n_scored:,} Bewertungen", className="ms-3 text-muted small"),
                ], color="dark", className="border border-secondary"),
                md=12, className="mb-3"
            )
        ]),

        html.Hr(className="border-secondary"),

        # Charts row 1
        dbc.Row([
            dbc.Col(dcc.Graph(figure=score_fig, config={"displayModeBar": False}), md=8, className="mb-4"),
            dbc.Col(dcc.Graph(figure=prio_fig, config={"displayModeBar": False}), md=4, className="mb-4"),
        ]),

        # Charts row 2
        dbc.Row([
            dbc.Col(dcc.Graph(figure=status_fig, config={"displayModeBar": False}), md=6, className="mb-4"),
            dbc.Col(dcc.Graph(figure=emp_fig, config={"displayModeBar": False}), md=6, className="mb-4"),
        ]),
    ], fluid=True, className="py-3")
