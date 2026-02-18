"""
Seite 12: Dialog Analyse
Analyse von Dialog-Akten und Kommunikationsmustern.
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
from components.data_loader import load_dialog_acts, load_utterances, load_nlp_features

dash.register_page(__name__, path="/dialog", name="💬 Dialog Analyse", order=12)

DIALOG_ACT_LABELS = {
    'request': '❓ Anfrage',
    'inform': 'ℹ️ Information',
    'confirm': '✅ Bestätigung',
    'deny': '❌ Ablehnung',
    'greet': '👋 Begrüßung',
    'bye': '👋 Verabschiedung',
    'thanks': '🙏 Dankeschön',
    'clarify': '🔎 Klärung',
}


def layout():
    dialog_df = load_dialog_acts()
    utt_df = load_utterances()
    nlp_df = load_nlp_features()

    has_data = not dialog_df.empty or not utt_df.empty

    # Dialog acts distribution
    act_fig = go.Figure()
    if not dialog_df.empty:
        act_col = [c for c in dialog_df.columns if 'act' in c.lower() or 'dialog' in c.lower()]
        if act_col:
            counts = dialog_df[act_col[0]].value_counts().head(10)
            act_fig = px.bar(x=counts.values, y=counts.index, orientation='h',
                             title="Dialog-Akt Verteilung",
                             color_discrete_sequence=["#9b59b6"])

    # Utterance length distribution
    len_fig = go.Figure()
    if not utt_df.empty:
        text_cols = [c for c in utt_df.columns if 'text' in c.lower() or 'comment' in c.lower() or 'utterance' in c.lower()]
        if text_cols:
            utt_df = utt_df.copy()
            utt_df['length'] = utt_df[text_cols[0]].fillna('').str.len()
            len_fig = px.histogram(utt_df, x='length', nbins=30,
                                   title="Äußerungs-Längenverteilung (Zeichen)",
                                   color_discrete_sequence=["#3498db"])

    # NLP: sentiment by turn/sequence
    turn_fig = go.Figure()
    if not nlp_df.empty and 'sentiment_compound_mean' in nlp_df.columns:
        sample = nlp_df.head(50).reset_index()
        turn_fig = px.scatter(sample, x=sample.index, y='sentiment_compound_mean',
                              title="Sentiment-Verlauf (erste 50 Tickets)",
                              color='sentiment_compound_mean',
                              color_continuous_scale='RdYlGn',
                              labels={"x": "Ticket-Index", "sentiment_compound_mean": "Sentiment"})
        turn_fig.add_hrule(y=0, line_dash="dash", line_color="white")

    # Word cloud simulation (top words via bar chart)
    word_fig = go.Figure()
    if not nlp_df.empty and 'word_count_mean' in nlp_df.columns:
        # Simulated top words
        words = ['problem', 'lösung', 'ticket', 'fehler', 'update', 'system',
                 'installation', 'netzwerk', 'passwort', 'drucker']
        counts_w = [45, 38, 120, 67, 29, 54, 23, 31, 44, 18]
        word_fig = px.bar(x=words, y=counts_w, title="Häufigste Begriffe (Simulation)",
                          color_discrete_sequence=["#e67e22"])

    for fig in [act_fig, len_fig, turn_fig, word_fig]:
        fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                          font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Dialog acts table
    act_table = html.Div()
    if not dialog_df.empty:
        act_table = html.Div([
            html.H5("Dialog-Akt Datensatz", className="text-info mb-2"),
            dash_table.DataTable(
                data=dialog_df.head(20).to_dict("records"),
                columns=[{"name": c, "id": c} for c in dialog_df.columns],
                page_size=10,
                style_table={"overflowX": "auto", "fontSize": "0.8rem"},
                style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0",
                            "border": "1px solid #495057"},
                style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
            )
        ])

    # Summary stats
    kpi_row = dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4(f"{len(dialog_df):,}" if not dialog_df.empty else "–",
                    className="text-warning mb-0"),
            html.Small("Dialog-Akte analysiert", className="text-muted"),
        ]), className="text-center kpi-card", style={"borderLeftColor": "#f39c12"}), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4(f"{len(utt_df):,}" if not utt_df.empty else "–",
                    className="text-info mb-0"),
            html.Small("Äußerungen", className="text-muted"),
        ]), className="text-center kpi-card", style={"borderLeftColor": "#3498db"}), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4(len(DIALOG_ACT_LABELS), className="text-success mb-0"),
            html.Small("Dialog-Akt-Typen", className="text-muted"),
        ]), className="text-center kpi-card", style={"borderLeftColor": "#2ecc71"}), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4(f"{len(nlp_df):,}" if not nlp_df.empty else "–",
                    className="text-danger mb-0"),
            html.Small("NLP Features", className="text-muted"),
        ]), className="text-center kpi-card", style={"borderLeftColor": "#e74c3c"}), md=3),
    ], className="mb-4")

    return dbc.Container([
        html.H3("💬 Dialog Analyse", className="mb-1 text-warning"),
        html.P("Analyse von Dialog-Akten, Kommunikationsmustern und Äußerungsstrukturen.", className="text-muted mb-4"),

        kpi_row,

        dbc.Row([
            dbc.Col(dcc.Graph(figure=act_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=len_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=turn_fig, config={"displayModeBar": False}), md=8),
            dbc.Col(dcc.Graph(figure=word_fig, config={"displayModeBar": False}), md=4),
        ], className="mb-4"),

        act_table,
    ], fluid=True, className="py-3")
