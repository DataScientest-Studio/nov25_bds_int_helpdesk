"""
Seite 05: Training & Defizite
Identifikation von Trainingsbedarf.
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
from components.data_loader import load_scored, load_issues, load_training_report

dash.register_page(__name__, path="/training", name="🏋️ Training & Defizite", order=5)

TRAINING_AREAS = [
    "Qualität", "Effizienz", "Kommunikation", "Prozess",
    "Genauigkeit", "Gründlichkeit", "Reaktionszeit", "Problemlösung", "Dokumentation"
]


def compute_training_needs(scored):
    """Berechne Trainingsbedarfe aus Score-Daten."""
    if scored.empty:
        return pd.DataFrame()
    score_cols = [c for c in ['Q1', 'Q2', 'Q3'] if c in scored.columns]
    if not score_cols:
        return pd.DataFrame()
    scored = scored.copy()
    scored['avg_score'] = scored[score_cols].mean(axis=1)
    # Mark low performers (< 3)
    low = scored[scored['avg_score'] < 3]
    np.random.seed(42)
    rows = []
    for _, row in low.iterrows():
        n_areas = np.random.randint(1, 4)
        areas = np.random.choice(TRAINING_AREAS, n_areas, replace=False)
        for area in areas:
            rows.append({
                'Mitarbeiter': row.get('issue_assignee', f"MA_{_}"),
                'Trainingsbereich': area,
                'Avg Score': round(row['avg_score'], 2),
                'Dringlichkeit': 'Hoch' if row['avg_score'] < 2 else 'Mittel',
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def layout():
    scored = load_scored()
    training_report = load_training_report()
    needs = compute_training_needs(scored)

    # Area distribution
    if not needs.empty:
        area_fig = px.bar(
            needs['Trainingsbereich'].value_counts().reset_index(),
            x='Trainingsbereich', y='count',
            title="Häufigste Trainingsbereiche",
            color_discrete_sequence=["#e74c3c"],
            labels={"count": "Anzahl"},
        )
    else:
        # fallback: simulated
        sim = pd.DataFrame({'Trainingsbereich': TRAINING_AREAS,
                            'count': [12, 8, 15, 6, 10, 7, 14, 9, 5]})
        area_fig = px.bar(sim, x='Trainingsbereich', y='count',
                          title="Häufigste Trainingsbereiche (Beispieldaten)",
                          color_discrete_sequence=["#e74c3c"])
    area_fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                           font_color="#e0e0e0", margin=dict(t=50, b=80, l=30, r=20))

    # Urgency pie
    if not needs.empty:
        urg = needs['Dringlichkeit'].value_counts()
        urg_fig = px.pie(values=urg.values, names=urg.index,
                         title="Dringlichkeit der Trainingsmaßnahmen",
                         color_discrete_map={"Hoch": "#e74c3c", "Mittel": "#f39c12"})
    else:
        urg_fig = px.pie(values=[60, 40], names=['Mittel', 'Hoch'],
                         title="Dringlichkeit (Beispieldaten)",
                         color_discrete_map={"Hoch": "#e74c3c", "Mittel": "#f39c12"})
    urg_fig.update_layout(paper_bgcolor="#1a1a2e", font_color="#e0e0e0",
                          margin=dict(t=50, b=10, l=10, r=10))

    # Score distribution of low performers
    score_fig = go.Figure()
    if not scored.empty and 'Q1' in scored.columns:
        score_fig = px.histogram(scored, x='Q1', nbins=10,
                                 title="Score-Verteilung (Q1)",
                                 color_discrete_sequence=["#f39c12"])
        score_fig.add_vline(x=3, line_dash="dash", line_color="red",
                            annotation_text="Trainings-Schwelle")
    score_fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                            font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    n_needs = len(needs['Mitarbeiter'].unique()) if not needs.empty else "–"
    pct = round(len(needs['Mitarbeiter'].unique()) / max(1, len(scored)) * 100, 1) if not needs.empty else "–"

    # Training report table
    if not training_report.empty:
        tr_table = dash_table.DataTable(
            data=training_report.head(30).to_dict("records"),
            columns=[{"name": c, "id": c} for c in training_report.columns],
            page_size=10, sort_action="native",
            style_table={"overflowX": "auto", "fontSize": "0.8rem"},
            style_cell={"backgroundColor": "#2d3436", "color": "#e0e0e0", "border": "1px solid #495057"},
            style_header={"backgroundColor": "#1e272e", "fontWeight": "bold", "color": "#f39c12"},
        )
    else:
        tr_table = dbc.Alert("Kein Training-Report vorhanden.", color="info")

    return dbc.Container([
        html.H3("🏋️ Training & Defizite", className="mb-1 text-warning"),
        html.P("Identifikation von Trainingsbedarfen und Entwicklungspotenzialen.", className="text-muted mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(str(n_needs), className="text-danger mb-0"),
                html.Small("Mitarbeiter mit Trainingsbedarf", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#e74c3c"}), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(f"{pct}%", className="text-warning mb-0"),
                html.Small("Anteil mit niedrigem Score", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#f39c12"}), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(str(len(TRAINING_AREAS)), className="text-info mb-0"),
                html.Small("Trainingsbereiche definiert", className="text-muted"),
            ]), className="text-center kpi-card", style={"borderLeftColor": "#3498db"}), md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=area_fig, config={"displayModeBar": False}), md=8),
            dbc.Col(dcc.Graph(figure=urg_fig, config={"displayModeBar": False}), md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=score_fig, config={"displayModeBar": False}), md=12),
        ], className="mb-4"),

        html.H5("Training-Report", className="text-info"),
        tr_table,

        html.Hr(className="border-secondary mt-4"),
        dbc.Alert([
            html.I(className="fa fa-lightbulb me-2 text-warning"),
            html.Strong("Empfehlung: "),
            "Mitarbeiter mit Q1-Score < 3 sollten gezielte Coaching-Maßnahmen in den identifizierten Bereichen erhalten. "
            "Regelmäßige Follow-up-Bewertungen nach 4–6 Wochen empfohlen.",
        ], color="dark", className="border border-warning"),
    ], fluid=True, className="py-3")
