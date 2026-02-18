"""
Seite 04: Mitarbeiter Performance
Live-Monitoring der Mitarbeiter-Performance.
"""
import dash
from dash import html, dcc, dash_table, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_issues, load_scored, load_employee_metrics

dash.register_page(__name__, path="/mitarbeiter", name="👥 Mitarbeiter Performance", order=4)


def layout():
    return dbc.Container([
        html.H3("👥 Mitarbeiter Performance", className="mb-1 text-warning"),
        html.P("Detaillierte Analyse der Mitarbeiter-Leistung.", className="text-muted mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="mp-tickets-bar", config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(id="mp-score-box", config={"displayModeBar": False}), md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="mp-time-bar", config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(id="mp-radar", config={"displayModeBar": False}), md=6),
        ], className="mb-4"),
        html.H5("Mitarbeiter-Ranking", className="text-info"),
        html.Div(id="mp-table"),
    ], fluid=True, className="py-3")


@callback(
    Output("mp-tickets-bar", "figure"),
    Output("mp-score-box", "figure"),
    Output("mp-time-bar", "figure"),
    Output("mp-radar", "figure"),
    Output("mp-table", "children"),
    Input("mp-tickets-bar", "id"),  # trigger on load
)
def update_mp(_):
    issues = load_issues()
    scored = load_scored()

    # Chart 1: Tickets per employee
    fig1 = go.Figure()
    if not issues.empty and 'issue_assignee' in issues.columns:
        grp = issues.groupby('issue_assignee').size().nlargest(15).reset_index()
        grp.columns = ['Mitarbeiter', 'Anzahl']
        fig1 = px.bar(grp, x='Anzahl', y='Mitarbeiter', orientation='h',
                      title="Top 15 – Bearbeitete Tickets",
                      color_discrete_sequence=["#f39c12"])
    apply_dark(fig1, "Top 15 – Bearbeitete Tickets")

    # Chart 2: Score box per employee
    fig2 = go.Figure()
    if not scored.empty and 'Q1' in scored.columns:
        # Try to get assignee from scored or merge
        if 'issue_assignee' in scored.columns:
            sc_col = 'issue_assignee'
        elif 'contributors' in scored.columns:
            sc_col = 'contributors'
        else:
            sc_col = None
        if sc_col:
            fig2 = px.box(scored, x=sc_col, y='Q1', title="Score-Verteilung pro Mitarbeiter",
                          color_discrete_sequence=["#3498db"])
        else:
            fig2 = px.histogram(scored, x='Q1', title="Score-Verteilung (Q1)",
                                color_discrete_sequence=["#3498db"])
    apply_dark(fig2, "Score-Verteilung")

    # Chart 3: Avg resolution time per employee
    fig3 = go.Figure()
    if not issues.empty and 'wf_total_time' in issues.columns and 'issue_assignee' in issues.columns:
        grp2 = issues.groupby('issue_assignee')['wf_total_time'].mean().nlargest(15) / 3600
        grp2 = grp2.reset_index()
        grp2.columns = ['Mitarbeiter', 'Ø Stunden']
        fig3 = px.bar(grp2, x='Ø Stunden', y='Mitarbeiter', orientation='h',
                      title="Ø Bearbeitungszeit (Top 15, Stunden)",
                      color_discrete_sequence=["#2ecc71"])
    apply_dark(fig3, "Ø Bearbeitungszeit")

    # Chart 4: Radar / priority distribution
    fig4 = go.Figure()
    if not issues.empty and 'issue_priority' in issues.columns:
        prio_counts = issues['issue_priority'].value_counts()
        fig4 = go.Figure(go.Scatterpolar(
            r=prio_counts.values.tolist(),
            theta=prio_counts.index.tolist(),
            fill='toself',
            line_color="#f39c12",
        ))
        fig4.update_layout(title="Prioritäts-Radar")
    apply_dark(fig4, "Prioritäts-Radar")

    # Table
    if not issues.empty and 'issue_assignee' in issues.columns:
        grp3 = issues.groupby('issue_assignee').agg(
            Tickets=('id', 'count'),
            Ø_Zeit_h=('wf_total_time', lambda x: round(x.mean() / 3600, 1) if 'wf_total_time' in issues.columns else 0),
        ).reset_index().rename(columns={'issue_assignee': 'Mitarbeiter'})
        if not scored.empty and 'Q1' in scored.columns and 'issue_assignee' in scored.columns:
            score_grp = scored.groupby('issue_assignee')['Q1'].mean().reset_index()
            score_grp.columns = ['Mitarbeiter', 'Ø Q1-Score']
            grp3 = grp3.merge(score_grp, on='Mitarbeiter', how='left')
        grp3 = grp3.sort_values('Tickets', ascending=False)
        table = dash_table.DataTable(
            data=grp3.to_dict("records"),
            columns=[{"name": c, "id": c} for c in grp3.columns],
            page_size=15, sort_action="native",
            style_table={"overflowX": "auto", "fontSize": "0.85rem"},
            style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
            style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
        )
    else:
        table = dbc.Alert("Keine Mitarbeiter-Daten.", color="info")

    return fig1, fig2, fig3, fig4, table


def apply_dark(fig, title=""):
    fig.update_layout(
        paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
        font_color="#e0e0e0", title_font_color="#f8f9fa",
        title=title, margin=dict(t=50, b=30, l=30, r=20),
    )
    fig.update_layout(polar=dict(bgcolor="#2d3436")) if hasattr(fig, 'data') and fig.data and fig.data[0].type == 'scatterpolar' else None
