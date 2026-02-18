"""
Help Desk Performance Monitor - Dash Dashboard
Multi-Page App with Sidebar Navigation (Port 8502)
"""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import os

# ---- App init ----
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "HelpDesk Performance Monitor"
server = app.server  # expose Flask server

# ---- Sidebar Navigation items ----
NAV_ITEMS = [
    {"icon": "fa-database",       "label": "Daten-Inventar",        "href": "/data-inventory"},
    {"icon": "fa-home",           "label": "Dashboard",              "href": "/dashboard"},
    {"icon": "fa-ticket-alt",     "label": "Ticket Monitor",         "href": "/ticket-monitor"},
    {"icon": "fa-users",          "label": "Mitarbeiter Performance", "href": "/mitarbeiter"},
    {"icon": "fa-dumbbell",       "label": "Training & Defizite",    "href": "/training"},
    {"icon": "fa-search",         "label": "Objektivitätsprüfung",   "href": "/objektivitaet"},
    {"icon": "fa-comments",       "label": "Kommunikation & NLP",    "href": "/nlp"},
    {"icon": "fa-sync-alt",       "label": "Prozess Compliance",     "href": "/compliance"},
    {"icon": "fa-brain",          "label": "ML Modell Details",      "href": "/ml-modell"},
    {"icon": "fa-chart-line",     "label": "Trend Analyse",          "href": "/trends"},
    {"icon": "fa-file-export",    "label": "Export Center",          "href": "/export"},
    {"icon": "fa-comment-dots",   "label": "Dialog Analyse",         "href": "/dialog"},
    {"icon": "fa-balance-scale",  "label": "Score Vergleich",        "href": "/score-vergleich"},
    {"icon": "fa-presentation",   "label": "Präsentation",           "href": "/praesentation"},
    {"icon": "fa-cog",            "label": "Einstellungen",          "href": "/settings"},
]


def build_sidebar():
    nav_links = [
        dbc.NavLink(
            [html.I(className=f"fa {item['icon']} me-2"), item["label"]],
            href=item["href"],
            active="exact",
            className="sidebar-link",
        )
        for item in NAV_ITEMS
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.I(className="fa fa-bullseye me-2 text-warning"),
                    html.Span("HelpDesk Monitor", className="fw-bold fs-5"),
                ],
                className="sidebar-brand px-3 py-3 border-bottom border-secondary",
            ),
            html.Div(
                dbc.Nav(nav_links, vertical=True, pills=True, className="flex-column px-2 py-2"),
            ),
            html.Hr(className="border-secondary mx-2"),
            html.Div(
                [
                    html.Small("🤖 KI-gestütztes System", className="text-muted px-3"),
                    html.Br(),
                    html.Small("⚡ Port 8502", className="text-muted px-3"),
                ],
                className="pb-3",
            ),
        ],
        className="sidebar bg-dark border-end border-secondary",
        id="sidebar",
    )


# ---- Layout ----
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        # Sidebar toggle button (mobile)
        dbc.Button(
            html.I(className="fa fa-bars"),
            id="sidebar-toggle",
            color="dark",
            className="d-md-none m-2",
            size="sm",
        ),
        html.Div(
            [
                build_sidebar(),
                html.Main(
                    dash.page_container,
                    className="main-content flex-grow-1 p-4",
                    id="page-content",
                ),
            ],
            className="d-flex",
            style={"minHeight": "100vh"},
        ),
    ]
)


# ---- Custom CSS (inline) ----
app.index_string = """
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<style>
  body { background-color: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
  .sidebar {
    width: 240px;
    min-height: 100vh;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    flex-shrink: 0;
  }
  .sidebar-link { color: #adb5bd !important; border-radius: 6px; font-size: 0.87rem; }
  .sidebar-link:hover { background-color: rgba(255,255,255,0.08) !important; color: #fff !important; }
  .sidebar-link.active { background-color: #f39c12 !important; color: #fff !important; font-weight: 600; }
  .sidebar-brand { color: #f39c12; }
  .main-content { background-color: #1a1a2e; min-height: 100vh; }
  .kpi-card { border-radius: 10px; border-left: 4px solid #f39c12; }
  .kpi-value { font-size: 2rem; font-weight: 700; color: #f39c12; }
  .card { border-color: #343a40 !important; }
  .card-header { background-color: #2d3436 !important; border-bottom: 1px solid #495057; }
  h4, h5 { color: #f8f9fa; }
  @media (max-width: 768px) {
    .sidebar { width: 100%; position: relative; height: auto; min-height: unset; }
    .d-flex { flex-direction: column; }
  }
</style>
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8502))
    app.run(host="0.0.0.0", port=port, debug=False)
