"""
Home - Redirect to Dashboard
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home", order=0)


def layout():
    return html.Div([
        dcc.Location(id="home-redirect", refresh=True),
        dbc.Container([
            html.Div([
                html.I(className="fa fa-bullseye fa-4x text-warning mb-4"),
                html.H2("HelpDesk Performance Monitor", className="text-warning"),
                html.P("KI-gestütztes System zur Mitarbeiter-Performance-Analyse", className="text-muted mb-4"),
                dbc.Spinner(color="warning", size="sm"),
                html.P("Weiterleitung zum Dashboard...", className="text-muted mt-2 small"),
            ], className="text-center py-5"),
        ]),
        dcc.Interval(id="home-interval", interval=500, n_intervals=0, max_intervals=1),
    ])


from dash import callback, Output, Input

@callback(
    Output("home-redirect", "href"),
    Input("home-interval", "n_intervals"),
    prevent_initial_call=True,
)
def redirect_home(n):
    return "/dashboard"
