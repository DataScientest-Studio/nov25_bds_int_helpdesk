"""
Seite 07: Kommunikation & NLP
Sentiment-Analyse und Kommunikationsmuster.
"""
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_nlp_features, load_utterances

dash.register_page(__name__, path="/nlp", name="💬 Kommunikation & NLP", order=7)


def layout():
    nlp_df = load_nlp_features()
    utt_df = load_utterances()

    # Sentiment histogram
    sent_fig = go.Figure()
    if not nlp_df.empty and 'sentiment_compound_mean' in nlp_df.columns:
        sent_fig = px.histogram(
            nlp_df, x='sentiment_compound_mean', nbins=30,
            title="Sentiment-Verteilung (Compound Score)",
            color_discrete_sequence=["#3498db"],
            labels={"sentiment_compound_mean": "Sentiment Score"},
        )
        sent_fig.add_vline(x=0.05, line_dash="dash", line_color="green",
                           annotation_text="Positiv-Schwelle")
        sent_fig.add_vline(x=-0.05, line_dash="dash", line_color="red",
                           annotation_text="Negativ-Schwelle")

    # Pos vs Neg sentiment scatter
    scatter_fig = go.Figure()
    if not nlp_df.empty and 'sentiment_pos_mean' in nlp_df.columns and 'sentiment_neg_mean' in nlp_df.columns:
        scatter_fig = px.scatter(
            nlp_df.head(500),
            x='sentiment_pos_mean', y='sentiment_neg_mean',
            title="Positiver vs. Negativer Sentiment",
            color='sentiment_compound_mean',
            color_continuous_scale='RdYlGn',
            labels={"sentiment_pos_mean": "Positiv", "sentiment_neg_mean": "Negativ"},
        )

    # Word count distribution
    word_fig = go.Figure()
    if not nlp_df.empty and 'word_count_mean' in nlp_df.columns:
        word_fig = px.histogram(nlp_df, x='word_count_mean', nbins=30,
                                title="Wortanzahl pro Ticket (Mittelwert)",
                                color_discrete_sequence=["#2ecc71"],
                                labels={"word_count_mean": "Ø Wortanzahl"})

    # Politeness vs urgency
    poli_fig = go.Figure()
    if not nlp_df.empty and 'politeness_score_sum' in nlp_df.columns:
        poli_fig = px.scatter(
            nlp_df.head(300),
            x='politeness_score_sum', y='urgency_score_sum',
            title="Höflichkeit vs. Dringlichkeit",
            color='word_count_mean' if 'word_count_mean' in nlp_df.columns else None,
            color_continuous_scale='Blues',
            labels={"politeness_score_sum": "Höflichkeit", "urgency_score_sum": "Dringlichkeit"},
        )

    # NLP summary stats
    kpis = []
    if not nlp_df.empty:
        kpis = [
            ("Tickets analysiert", f"{len(nlp_df):,}", "#f39c12"),
            ("Ø Sentiment", round(nlp_df['sentiment_compound_mean'].mean(), 3) if 'sentiment_compound_mean' in nlp_df.columns else "–", "#3498db"),
            ("Ø Wortanzahl", round(nlp_df['word_count_mean'].mean(), 1) if 'word_count_mean' in nlp_df.columns else "–", "#2ecc71"),
            ("Fragen gesamt", f"{int(nlp_df['question_count_sum'].sum()):,}" if 'question_count_sum' in nlp_df.columns else "–", "#e74c3c"),
        ]

    kpi_cards = [
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4(str(v), style={"color": c}, className="mb-0"),
            html.Small(t, className="text-muted"),
        ]), className="text-center kpi-card", style={"borderLeftColor": c}), md=3, className="mb-3")
        for t, v, c in kpis
    ] if kpis else []

    # Apply dark theme
    for fig in [sent_fig, scatter_fig, word_fig, poli_fig]:
        fig.update_layout(
            paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
            font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20)
        )

    # Sample utterances table
    utt_table = html.Div()
    if not utt_df.empty:
        utt_table = html.Div([
            html.H5("Beispiel-Äußerungen", className="text-info mb-2"),
            dash_table.DataTable(
                data=utt_df.head(20).to_dict("records"),
                columns=[{"name": c, "id": c} for c in utt_df.columns],
                page_size=10, filter_action="native",
                style_table={"overflowX": "auto", "fontSize": "0.8rem"},
                style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0",
                            "border": "1px solid #495057", "maxWidth": "300px",
                            "overflow": "hidden", "textOverflow": "ellipsis"},
                style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
            )
        ])

    return dbc.Container([
        html.H3("💬 Kommunikation & NLP", className="mb-1 text-warning"),
        html.P("Sentiment-Analyse, Sprachmuster und Kommunikationsqualität.", className="text-muted mb-4"),

        dbc.Row(kpi_cards) if kpi_cards else dbc.Alert("Keine NLP-Daten.", color="info"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=sent_fig, config={"displayModeBar": False}), md=8),
            dbc.Col(dcc.Graph(figure=word_fig, config={"displayModeBar": False}), md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=scatter_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=poli_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        utt_table,
    ], fluid=True, className="py-3")
