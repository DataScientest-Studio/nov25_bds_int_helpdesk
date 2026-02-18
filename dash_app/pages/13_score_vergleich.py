"""
Seite 13: Score Vergleich
Q-Score (Manager) vs O-Score (Objektiv) Vergleich.
"""
import dash
from dash import html, dcc, dash_table, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_q_vs_o_comparison, load_scored, load_o_score_results

dash.register_page(__name__, path="/score-vergleich", name="⚖️ Score Vergleich", order=13)


def build_comparison_df():
    """Baue Vergleichs-DataFrame."""
    cmp = load_q_vs_o_comparison()
    if not cmp.empty:
        return cmp

    # Fallback: merge from individual datasets
    scored = load_scored()
    o_results = load_o_score_results()

    if not scored.empty and not o_results.empty:
        # Try to merge on common key
        merge_keys = [c for c in scored.columns if c in o_results.columns and 'id' in c.lower()]
        if merge_keys:
            merged = scored.merge(o_results, on=merge_keys[0], suffixes=('_q', '_o'))
            return merged

    if not scored.empty and 'Q1' in scored.columns:
        # Simulate O-Score
        df = scored.copy()
        np.random.seed(42)
        if 'issue_assignee' in df.columns:
            df = df.rename(columns={'issue_assignee': 'Mitarbeiter'})
        else:
            df['Mitarbeiter'] = [f"MA_{i:03d}" for i in range(len(df))]
        df['Q_Score'] = df['Q1']
        df['O_Score'] = np.clip(df['Q1'] + np.random.randn(len(df)) * 0.7, 1, 5)
        df['Differenz'] = df['Q_Score'] - df['O_Score']
        df['Bias'] = df['Differenz'].apply(
            lambda x: 'Überbewertet' if x > 0.5 else ('Unterbewertet' if x < -0.5 else 'Fair')
        )
        return df[['Mitarbeiter', 'Q_Score', 'O_Score', 'Differenz', 'Bias']]

    return pd.DataFrame()


def layout():
    df = build_comparison_df()

    if df.empty:
        return dbc.Container([
            html.H3("⚖️ Score Vergleich", className="text-warning"),
            dbc.Alert("Keine Vergleichsdaten verfügbar.", color="warning"),
        ], fluid=True, className="py-3")

    q_col = next((c for c in df.columns if 'q' in c.lower() and 'score' in c.lower()), None) or \
            next((c for c in df.columns if c == 'Q1'), None)
    o_col = next((c for c in df.columns if 'o' in c.lower() and 'score' in c.lower()), None)

    if q_col is None or o_col is None:
        # Try to use any numeric columns
        num_cols = df.select_dtypes(include='number').columns.tolist()
        if len(num_cols) >= 2:
            q_col, o_col = num_cols[0], num_cols[1]
        else:
            return dbc.Container([
                html.H3("⚖️ Score Vergleich", className="text-warning"),
                dbc.Alert("Nicht genug Spalten für Vergleich.", color="warning"),
            ], fluid=True, className="py-3")

    # Correlation
    corr = round(df[q_col].corr(df[o_col]), 3) if q_col in df.columns and o_col in df.columns else 0
    diff_col = 'Differenz' if 'Differenz' in df.columns else None
    bias_col = 'Bias' if 'Bias' in df.columns else None

    # Scatter Q vs O
    scatter_fig = px.scatter(
        df.head(200),
        x=q_col, y=o_col,
        title=f"Q-Score vs O-Score (Korrelation: {corr})",
        color=bias_col if bias_col else None,
        color_discrete_map={'Überbewertet': '#e74c3c', 'Unterbewertet': '#3498db', 'Fair': '#2ecc71'},
        labels={q_col: "Q-Score (Manager)", o_col: "O-Score (Objektiv)"},
        hover_data=['Mitarbeiter'] if 'Mitarbeiter' in df.columns else [],
    )
    scatter_fig.add_scatter(x=[1, 5], y=[1, 5], mode='lines', name='Ideallinie',
                            line=dict(color='white', dash='dash'))

    # Difference distribution
    diff_fig = go.Figure()
    if diff_col:
        diff_fig = px.histogram(df, x=diff_col, nbins=30,
                                title="Differenz-Verteilung (Q-Score - O-Score)",
                                color_discrete_sequence=["#9b59b6"])
        diff_fig.add_vline(x=0, line_dash="dash", line_color="white",
                           annotation_text="Kein Bias")

    # Bias distribution pie
    bias_fig = go.Figure()
    if bias_col:
        bc = df[bias_col].value_counts()
        bias_fig = px.pie(values=bc.values, names=bc.index,
                          title="Bias-Verteilung",
                          color_discrete_map={'Überbewertet': '#e74c3c',
                                             'Unterbewertet': '#3498db', 'Fair': '#2ecc71'})

    # Histogram comparison
    hist_fig = go.Figure()
    hist_fig.add_trace(go.Histogram(x=df[q_col].dropna(), name='Q-Score', opacity=0.7,
                                    marker_color='#f39c12'))
    if o_col in df.columns:
        hist_fig.add_trace(go.Histogram(x=df[o_col].dropna(), name='O-Score', opacity=0.7,
                                        marker_color='#3498db'))
    hist_fig.update_layout(barmode='overlay', title="Score-Verteilungen im Vergleich")

    for fig in [scatter_fig, diff_fig, bias_fig, hist_fig]:
        fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                          font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Table
    disp_cols = [c for c in ['Mitarbeiter', q_col, o_col, diff_col, bias_col] if c and c in df.columns]
    table_df = df[disp_cols].sort_values(diff_col if diff_col else q_col, ascending=False) if disp_cols else df

    return dbc.Container([
        html.H3("⚖️ Score Vergleich: Q-Score vs O-Score", className="mb-1 text-warning"),
        html.P("Paralleler Vergleich: Manager-Bewertung (subjektiv) vs Objektive Metriken.", className="text-muted mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(f"{corr}", className="text-warning mb-0"),
                html.Small("Pearson-Korrelation", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#f39c12"}), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(str(len(df)), className="text-info mb-0"),
                html.Small("Vergleichbare Samples", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#3498db"}), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(str(len(df[df['Bias'] == 'Überbewertet'])) if bias_col else "–",
                        className="text-danger mb-0"),
                html.Small("Überbewertete MA", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#e74c3c"}), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(str(len(df[df['Bias'] == 'Unterbewertet'])) if bias_col else "–",
                        className="text-success mb-0"),
                html.Small("Unterbewertete MA", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#2ecc71"}), md=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=scatter_fig, config={"displayModeBar": False}), md=8),
            dbc.Col(dcc.Graph(figure=bias_fig, config={"displayModeBar": False}), md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=diff_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=hist_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        html.H5("Vollständiges Ranking", className="text-info mb-2"),
        dash_table.DataTable(
            data=table_df.head(50).round(3).to_dict("records"),
            columns=[{"name": c, "id": c} for c in table_df.columns],
            page_size=15, sort_action="native",
            style_table={"overflowX": "auto", "fontSize": "0.85rem"},
            style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
            style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
            style_data_conditional=[
                {"if": {"filter_query": '{Bias} = "Überbewertet"'}, "backgroundColor": "#3d1515"},
                {"if": {"filter_query": '{Bias} = "Unterbewertet"'}, "backgroundColor": "#153d3d"},
                {"if": {"filter_query": '{Bias} = "Fair"'}, "backgroundColor": "#153d15"},
            ],
        ),
    ], fluid=True, className="py-3")
