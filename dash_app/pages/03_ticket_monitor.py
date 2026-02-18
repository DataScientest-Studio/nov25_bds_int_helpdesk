"""
Seite 03: Ticket Monitor
Live-Monitoring aller Tickets mit Filtern.
"""
import dash
from dash import html, dcc, dash_table, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_issues

dash.register_page(__name__, path="/ticket-monitor", name="🎫 Ticket Monitor", order=3)


def layout():
    df = load_issues()
    if df.empty:
        return dbc.Container([
            html.H3("🎫 Ticket Monitor", className="text-warning"),
            dbc.Alert("Keine Ticket-Daten gefunden.", color="warning"),
        ], fluid=True, className="py-3")

    status_opts = [{"label": s, "value": s} for s in sorted(df['issue_status'].dropna().unique())] if 'issue_status' in df.columns else []
    prio_opts = [{"label": p, "value": p} for p in sorted(df['issue_priority'].dropna().unique())] if 'issue_priority' in df.columns else []

    disp_cols = ['id', 'issue_assignee', 'issue_reporter', 'issue_priority', 'issue_status',
                 'issue_type', 'issue_created', 'wf_total_time']
    disp_cols = [c for c in disp_cols if c in df.columns]

    return dbc.Container([
        html.H3("🎫 Ticket Monitor", className="mb-1 text-warning"),
        html.P("Echtzeit-Monitoring aller Helpdesk-Tickets mit Filterfunktion.", className="text-muted mb-4"),

        # Filter row
        dbc.Card([
            dbc.CardHeader([html.I(className="fa fa-filter me-2"), "Filter"]),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Label("Status", className="small text-muted"),
                        dcc.Dropdown(
                            id="tm-status-filter",
                            options=status_opts,
                            placeholder="Alle Status",
                            multi=True,
                            style={"backgroundColor": "#2d3436", "color": "#000"},
                        ),
                    ], md=4),
                    dbc.Col([
                        html.Label("Priorität", className="small text-muted"),
                        dcc.Dropdown(
                            id="tm-prio-filter",
                            options=prio_opts,
                            placeholder="Alle Prioritäten",
                            multi=True,
                            style={"backgroundColor": "#2d3436", "color": "#000"},
                        ),
                    ], md=4),
                    dbc.Col([
                        html.Label("Max. Zeilen", className="small text-muted"),
                        dcc.Slider(id="tm-limit", min=50, max=500, step=50, value=100,
                                   marks={50: "50", 250: "250", 500: "500"}),
                    ], md=4),
                ])
            )
        ], className="mb-4 border-secondary"),

        # KPIs
        dbc.Row(id="tm-kpi-row", className="mb-4"),

        # Charts
        dbc.Row([
            dbc.Col(dcc.Graph(id="tm-status-chart", config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(id="tm-prio-chart", config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        # Table
        html.H5("Ticket-Liste", className="text-info"),
        html.Div(id="tm-table"),

        # Store raw data (serialized)
        dcc.Store(id="tm-raw-cols", data=disp_cols),
    ], fluid=True, className="py-3")


@callback(
    Output("tm-kpi-row", "children"),
    Output("tm-status-chart", "figure"),
    Output("tm-prio-chart", "figure"),
    Output("tm-table", "children"),
    Input("tm-status-filter", "value"),
    Input("tm-prio-filter", "value"),
    Input("tm-limit", "value"),
)
def update_ticket_monitor(status_vals, prio_vals, limit):
    df = load_issues()
    if df.empty:
        empty = go_empty()
        return [], empty, empty, dbc.Alert("Keine Daten.", color="warning")

    filtered = df.copy()
    if status_vals:
        filtered = filtered[filtered['issue_status'].isin(status_vals)]
    if prio_vals:
        filtered = filtered[filtered['issue_priority'].isin(prio_vals)]
    filtered = filtered.head(limit or 100)

    # KPIs
    total = len(filtered)
    avg_t = round(filtered['wf_total_time'].mean() / 3600, 1) if 'wf_total_time' in filtered.columns and total > 0 else 0
    open_t = len(filtered[filtered['issue_status'] != 'done']) if 'issue_status' in filtered.columns else 0

    kpi_cards = dbc.Row([
        dbc.Col(kpi_mini("Gefilterte Tickets", total, "#f39c12"), md=4),
        dbc.Col(kpi_mini("Ø Bearbeitungszeit", f"{avg_t}h", "#3498db"), md=4),
        dbc.Col(kpi_mini("Offene Tickets", open_t, "#e74c3c"), md=4),
    ])

    # Status chart
    if 'issue_status' in filtered.columns:
        sc = filtered['issue_status'].value_counts().head(8)
        status_fig = px.bar(x=sc.values, y=sc.index, orientation='h',
                            title="Status-Verteilung", color_discrete_sequence=["#f39c12"])
    else:
        status_fig = go_empty()
    status_fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                             font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Priority chart
    if 'issue_priority' in filtered.columns:
        pc = filtered['issue_priority'].value_counts()
        prio_fig = px.pie(values=pc.values, names=pc.index, title="Prioritäts-Verteilung",
                          color_discrete_sequence=px.colors.sequential.Oranges_r)
    else:
        prio_fig = go_empty()
    prio_fig.update_layout(paper_bgcolor="#1a1a2e", font_color="#e0e0e0",
                           margin=dict(t=50, b=10, l=10, r=10))

    # Table
    disp_cols = ['id', 'issue_assignee', 'issue_reporter', 'issue_priority', 'issue_status',
                 'issue_type', 'issue_created', 'wf_total_time']
    disp_cols = [c for c in disp_cols if c in filtered.columns]
    table = dash_table.DataTable(
        data=filtered[disp_cols].head(200).to_dict("records"),
        columns=[{"name": c, "id": c} for c in disp_cols],
        page_size=15,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto", "fontSize": "0.8rem"},
        style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
        style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
        style_data_conditional=[
            {"if": {"filter_query": '{issue_priority} = "High"'}, "backgroundColor": "#3d1515"},
            {"if": {"filter_query": '{issue_status} = "done"'}, "backgroundColor": "#1a3d1a"},
        ],
    )

    return kpi_cards.children, status_fig, prio_fig, table


def kpi_mini(label, value, color):
    return dbc.Card(dbc.CardBody([
        html.H4(str(value), style={"color": color}, className="mb-0"),
        html.Small(label, className="text-muted"),
    ]), className="text-center kpi-card mb-3", style={"borderLeftColor": color})


def go_empty():
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                      font_color="#e0e0e0", title="Keine Daten")
    return fig
