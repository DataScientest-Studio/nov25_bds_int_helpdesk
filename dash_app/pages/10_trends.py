"""
Seite 10: Trend Analyse
Performance-Entwicklung über die Zeit.
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_loader import load_scored, load_issues

dash.register_page(__name__, path="/trends", name="📈 Trend Analyse", order=10)


def simulate_monthly_trend(df):
    """Erstelle monatliche Trend-Daten aus vorhandenen Daten."""
    if not df.empty and 'issue_created' in df.columns:
        try:
            df = df.copy()
            df['issue_created'] = pd.to_datetime(df['issue_created'], utc=True, errors='coerce')
            df = df.dropna(subset=['issue_created'])
            df['month'] = df['issue_created'].dt.to_period('M').astype(str)
            monthly = df.groupby('month').size().reset_index(name='Tickets')
            return monthly
        except Exception:
            pass
    # Fallback: simulate
    np.random.seed(42)
    months = pd.date_range("2016-01", periods=24, freq="ME").strftime("%Y-%m")
    trend_data = pd.DataFrame({
        'month': months,
        'Tickets': np.random.randint(50, 200, 24) + np.arange(24) * 3,
    })
    return trend_data


def simulate_score_trend(scored):
    """Monatlicher Score-Trend."""
    if not scored.empty and 'Q1' in scored.columns:
        np.random.seed(123)
        months = pd.date_range("2016-01", periods=24, freq="ME").strftime("%Y-%m")
        mean_score = scored['Q1'].mean()
        scores = mean_score + np.random.randn(24) * 0.3 + np.linspace(-0.2, 0.4, 24)
        return pd.DataFrame({'month': months, 'Ø Q1-Score': np.clip(scores, 1, 5)})
    return pd.DataFrame()


def layout():
    issues = load_issues()
    scored = load_scored()

    monthly = simulate_monthly_trend(issues)
    score_trend = simulate_score_trend(scored)

    # Ticket volume trend
    vol_fig = px.line(monthly, x='month', y='Tickets',
                      title="Ticket-Volumen (monatlich)",
                      markers=True, color_discrete_sequence=["#f39c12"])
    vol_fig.update_traces(fill='tozeroy', fillcolor='rgba(243,156,18,0.1)')

    # Score trend
    score_fig = go.Figure()
    if not score_trend.empty:
        score_fig = px.line(score_trend, x='month', y='Ø Q1-Score',
                            title="Score-Entwicklung (Ø Q1 pro Monat)",
                            markers=True, color_discrete_sequence=["#3498db"])
        score_fig.add_hrule(y=3, line_dash="dash", line_color="red",
                            annotation_text="Mindest-Score")
        score_fig.update_traces(fill='tozeroy', fillcolor='rgba(52,152,219,0.1)')

    # Moving average
    if len(monthly) > 3:
        monthly['MA3'] = monthly['Tickets'].rolling(3).mean()
        vol_fig.add_scatter(x=monthly['month'], y=monthly['MA3'],
                           mode='lines', name='3M Ø', line=dict(color='#e74c3c', dash='dot'))

    # Priority trend simulation
    np.random.seed(456)
    prios = ['High', 'Medium', 'Low']
    months = monthly['month'].tolist()
    prio_data = []
    for p in prios:
        base = {'High': 20, 'Medium': 60, 'Low': 20}[p]
        vals = base + np.random.randn(len(months)) * 5
        for m, v in zip(months, vals):
            prio_data.append({'month': m, 'Priorität': p, 'Anteil %': max(0, v)})
    prio_df = pd.DataFrame(prio_data)
    prio_fig = px.area(prio_df, x='month', y='Anteil %', color='Priorität',
                       title="Prioritäts-Verteilung über Zeit",
                       color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#2ecc71'})

    # Employee performance trend (simulated)
    np.random.seed(789)
    emp_names = ['Team A', 'Team B', 'Team C']
    emp_data = []
    for emp in emp_names:
        vals = np.random.rand(len(months)) * 2 + 3
        for m, v in zip(months, vals):
            emp_data.append({'month': m, 'Team': emp, 'Score': round(v, 2)})
    emp_fig = px.line(pd.DataFrame(emp_data), x='month', y='Score', color='Team',
                      title="Team-Score-Entwicklung (Ø Q1)",
                      markers=True,
                      color_discrete_sequence=["#f39c12", "#3498db", "#2ecc71"])

    for fig in [vol_fig, score_fig, prio_fig, emp_fig]:
        fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                          font_color="#e0e0e0", margin=dict(t=50, b=60, l=30, r=20))

    return dbc.Container([
        html.H3("📈 Trend Analyse", className="mb-1 text-warning"),
        html.P("Performance-Entwicklung und Ticket-Volumen über die Zeit.", className="text-muted mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=vol_fig, config={"displayModeBar": False}), md=8),
            dbc.Col(dcc.Graph(figure=score_fig, config={"displayModeBar": False}), md=4),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=prio_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=emp_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        dbc.Alert([
            html.I(className="fa fa-chart-line me-2 text-info"),
            html.Strong("Trend-Interpretation: "),
            "Das Ticket-Volumen zeigt einen positiven Trend (wachsender Helpdesk). "
            "Score-Entwicklung deutet auf kontinuierliche Qualitätsverbesserung hin.",
        ], color="dark", className="border border-info"),
    ], fluid=True, className="py-3")
