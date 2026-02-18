"""
Seite 06: Objektivitätsprüfung
Bias-Analyse der Manager-Bewertungen.
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
from components.data_loader import load_scored

dash.register_page(__name__, path="/objektivitaet", name="🔍 Objektivitätsprüfung", order=6)

SCORE_COLS = ['Q1', 'Q2', 'Q3']


def compute_bias(df):
    """Berechne Bias-Metriken."""
    results = []
    for col in SCORE_COLS:
        if col not in df.columns:
            continue
        vals = df[col].dropna()
        if vals.empty:
            continue
        std = vals.std()
        mean = vals.mean()
        # Halo-Effekt: hohe Korrelation zwischen Scores
        # Leniency: Tendenz zu hohen Scores
        leniency = (vals >= 4).sum() / len(vals) * 100
        halo = "HOCH" if std < 0.5 else ("MITTEL" if std < 1.0 else "NIEDRIG")
        results.append({
            'Score': col,
            'Mittelwert': round(mean, 3),
            'Std-Abweichung': round(std, 3),
            'Leniency %': round(leniency, 1),
            'Halo-Effekt': halo,
        })
    return pd.DataFrame(results)


def layout():
    df = load_scored()

    if df.empty:
        return dbc.Container([
            html.H3("🔍 Objektivitätsprüfung", className="text-warning"),
            dbc.Alert("Keine Bewertungsdaten gefunden.", color="warning"),
        ], fluid=True, className="py-3")

    bias_df = compute_bias(df)

    # Bias type cards
    bias_cards = []
    colors = {"HOCH": "#e74c3c", "MITTEL": "#f39c12", "NIEDRIG": "#2ecc71"}
    for _, row in bias_df.iterrows():
        c = colors.get(row['Halo-Effekt'], "#adb5bd")
        bias_cards.append(dbc.Col(
            dbc.Card(dbc.CardBody([
                html.H5(row['Score'], className="card-title"),
                dbc.Badge(f"Halo: {row['Halo-Effekt']}", color="danger" if row['Halo-Effekt'] == "HOCH" else "warning" if row['Halo-Effekt'] == "MITTEL" else "success"),
                html.P(f"Mittelwert: {row['Mittelwert']}", className="mt-2 mb-0 small"),
                html.P(f"Std: {row['Std-Abweichung']}", className="mb-0 small"),
                html.P(f"Leniency: {row['Leniency %']}%", className="mb-0 small"),
            ]), className="kpi-card", style={"borderLeftColor": c}),
            md=4, className="mb-3"
        ))

    # Score distribution for each Q
    violin_fig = go.Figure()
    for col in SCORE_COLS:
        if col in df.columns:
            violin_fig.add_trace(go.Violin(y=df[col].dropna(), name=col, box_visible=True,
                                           meanline_visible=True))
    violin_fig.update_layout(title="Score-Verteilung (Violin)", paper_bgcolor="#1a1a2e",
                             plot_bgcolor="#2d3436", font_color="#e0e0e0",
                             margin=dict(t=50, b=30, l=30, r=20))

    # Correlation heatmap
    available_cols = [c for c in SCORE_COLS if c in df.columns]
    heat_fig = go.Figure()
    if len(available_cols) >= 2:
        corr = df[available_cols].corr()
        heat_fig = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
            colorscale="RdYlGn", zmin=-1, zmax=1,
            text=corr.round(2).values, texttemplate="%{text}",
        ))
        heat_fig.update_layout(title="Korrelations-Matrix der Scores",
                               paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                               font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Histogram of Q1
    hist_fig = px.histogram(df, x='Q1', nbins=10, title="Q1-Score Häufigkeitsverteilung",
                            color_discrete_sequence=["#f39c12"]) if 'Q1' in df.columns else go.Figure()
    hist_fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                           font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Bias table
    bias_table = dash_table.DataTable(
        data=bias_df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in bias_df.columns],
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
        style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
        style_data_conditional=[
            {"if": {"filter_query": '{Halo-Effekt} = "HOCH"'}, "backgroundColor": "#3d1515", "color": "#ff6b6b"},
        ],
    )

    return dbc.Container([
        html.H3("🔍 Objektivitätsprüfung", className="mb-1 text-warning"),
        html.P("Bias-Analyse: Erkennung von Halo-Effekt, Leniency und Bewertungsverzerrungen.", className="text-muted mb-4"),

        html.H5("Bias-Typen nach Score", className="text-info mb-3"),
        dbc.Row(bias_cards),

        html.Hr(className="border-secondary"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=violin_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=heat_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=hist_fig, config={"displayModeBar": False}), md=12),
        ], className="mb-4"),

        html.H5("Bias-Tabelle", className="text-info mb-2"),
        bias_table,

        html.Hr(className="border-secondary mt-4"),
        dbc.Alert([
            html.I(className="fa fa-info-circle me-2 text-info"),
            html.Strong("Interpretation: "),
            "Ein hoher Halo-Effekt (niedrige Std-Abweichung) deutet darauf hin, dass alle Scores eines Managers "
            "ähnlich ausfallen – unabhängig von der tatsächlichen Leistung. "
            "Leniency > 60% zeigt eine Tendenz zu positiven Bewertungen.",
        ], color="dark", className="border border-info"),
    ], fluid=True, className="py-3")
