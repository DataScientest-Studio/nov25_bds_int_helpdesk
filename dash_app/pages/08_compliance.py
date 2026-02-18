"""
Seite 08: Prozess Compliance
Workflow-Analyse und Prozessverletzungen.
"""
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_workflow_analysis, load_issues

dash.register_page(__name__, path="/compliance", name="🔄 Prozess Compliance", order=8)


def layout():
    wf_df = load_workflow_analysis()
    issues = load_issues()

    if wf_df.empty and issues.empty:
        return dbc.Container([
            html.H3("🔄 Prozess Compliance", className="text-warning"),
            dbc.Alert("Keine Workflow-Daten gefunden.", color="warning"),
        ], fluid=True, className="py-3")

    # Use issues as fallback for workflow data
    df = wf_df if not wf_df.empty else issues

    # Status distribution
    status_fig = go.Figure()
    if 'issue_status' in df.columns:
        sc = df['issue_status'].value_counts()
        status_fig = px.bar(sc, title="Status-Verteilung", color_discrete_sequence=["#2ecc71"])
    elif 'status' in df.columns:
        sc = df['status'].value_counts()
        status_fig = px.bar(sc, title="Status-Verteilung", color_discrete_sequence=["#2ecc71"])

    # Processing steps distribution
    steps_fig = go.Figure()
    if 'processing_steps' in df.columns:
        steps_fig = px.histogram(df, x='processing_steps', nbins=15,
                                 title="Workflow-Schritte pro Ticket",
                                 color_discrete_sequence=["#3498db"])

    # Total time distribution
    time_fig = go.Figure()
    if 'wf_total_time' in df.columns:
        time_hours = df['wf_total_time'].dropna() / 3600
        time_df = pd.DataFrame({'Stunden': time_hours[time_hours < time_hours.quantile(0.95)]})
        time_fig = px.histogram(time_df, x='Stunden', nbins=30,
                                title="Bearbeitungszeit-Verteilung (Stunden, ohne Ausreißer)",
                                color_discrete_sequence=["#e74c3c"])

    # Compliance metrics
    sla_violations = 0
    compliance_rate = 100.0
    if 'wf_total_time' in df.columns:
        SLA_HOURS = 48  # 48h SLA
        violations = (df['wf_total_time'].dropna() / 3600 > SLA_HOURS).sum()
        total = df['wf_total_time'].dropna().count()
        sla_violations = int(violations)
        compliance_rate = round((1 - violations / total) * 100, 1) if total > 0 else 100.0

    for fig in [status_fig, steps_fig, time_fig]:
        fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                          font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Workflow steps overview
    wf_cols = [c for c in df.columns if c.startswith('wf_') and c != 'wf_total_time'][:8]
    radar_fig = go.Figure()
    if wf_cols:
        means = [df[c].mean() for c in wf_cols]
        labels = [c.replace('wf_', '').replace('_', ' ').title() for c in wf_cols]
        radar_fig.add_trace(go.Scatterpolar(r=means, theta=labels, fill='toself',
                                             line_color="#f39c12"))
        radar_fig.update_layout(title="Workflow-Phasen (Ø Aktivierung)",
                                paper_bgcolor="#1a1a2e",
                                polar=dict(bgcolor="#2d3436",
                                           radialaxis=dict(color="#e0e0e0"),
                                           angularaxis=dict(color="#e0e0e0")),
                                font_color="#e0e0e0", margin=dict(t=80, b=30, l=30, r=30))

    return dbc.Container([
        html.H3("🔄 Prozess Compliance", className="mb-1 text-warning"),
        html.P("Workflow-Analyse, SLA-Monitoring und Prozesseinhaltung.", className="text-muted mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(f"{compliance_rate}%", className="text-success mb-0"),
                html.Small("Compliance-Rate (SLA 48h)", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#2ecc71"}), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(str(sla_violations), className="text-danger mb-0"),
                html.Small("SLA-Verletzungen", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#e74c3c"}), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(f"{len(df):,}", className="text-info mb-0"),
                html.Small("Analysierte Tickets", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#3498db"}), md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=status_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=steps_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=time_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=radar_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        dbc.Alert([
            html.I(className="fa fa-exclamation-triangle me-2 text-warning"),
            f"SLA (48 Stunden): {sla_violations} Tickets haben die SLA überschritten "
            f"({100 - compliance_rate:.1f}% der Tickets). "
            "Empfehlung: Prioritäts-Eskalation für Tickets > 24h einführen.",
        ], color="dark", className="border border-warning"),
    ], fluid=True, className="py-3")
