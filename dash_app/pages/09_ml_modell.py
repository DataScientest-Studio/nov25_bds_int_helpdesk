"""
Seite 09: ML Modell Details
Feature Importance, Modell-Performance, Q-Score & O-Score.
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
from components.data_loader import load_model, load_ml_dataset, MODELS_DIR

dash.register_page(__name__, path="/ml-modell", name="🎯 ML Modell Details", order=9)

MODEL_FILES = {
    "Q-Score Modell (Manager)": "q_score_model.joblib",
    "O-Score Modell (Objektiv)": "o_score_model.joblib",
    "Performance Scorer": "performance_scorer.joblib",
    "Optimized Scorer": "optimized_scorer.joblib",
}


def get_feature_importance(model, feature_names=None):
    """Extrahiere Feature Importance aus Modell."""
    try:
        if hasattr(model, 'feature_importances_'):
            imp = model.feature_importances_
        elif hasattr(model, 'coef_'):
            imp = np.abs(model.coef_).flatten()
        else:
            return None
        if feature_names is None or len(feature_names) != len(imp):
            feature_names = [f"Feature {i}" for i in range(len(imp))]
        df = pd.DataFrame({'Feature': feature_names, 'Importance': imp})
        return df.sort_values('Importance', ascending=False).head(20)
    except Exception:
        return None


def layout():
    ml_df = load_ml_dataset()

    # Model status cards
    model_cards = []
    for name, fname in MODEL_FILES.items():
        m = load_model(fname)
        exists = m is not None
        model_cards.append(dbc.Col(
            dbc.Card(dbc.CardBody([
                html.I(className=f"fa fa-{'check-circle text-success' if exists else 'times-circle text-danger'} fa-2x mb-2"),
                html.H6(name, className="card-title"),
                dbc.Badge("✅ Geladen" if exists else "❌ Nicht gefunden",
                          color="success" if exists else "danger"),
                html.P(fname, className="small text-muted mt-1 mb-0"),
                html.P(f"Typ: {type(m).__name__}" if m else "", className="small text-secondary mb-0"),
            ]), className="text-center kpi-card h-100",
                style={"borderLeftColor": "#2ecc71" if exists else "#e74c3c"}),
            md=3, className="mb-3"
        ))

    # Feature importance for q_score model
    fi_fig = go.Figure()
    q_model = load_model("q_score_model.joblib")
    if q_model is not None:
        feature_names = None
        if not ml_df.empty:
            target_cols = ['Q1', 'Q2', 'Q3', 'q_score', 'o_score']
            exclude = [c for c in ml_df.columns if c in target_cols or 'id' in c.lower() or 'date' in c.lower()]
            feature_names = [c for c in ml_df.columns if c not in exclude][:30]
        fi_df = get_feature_importance(q_model, feature_names)
        if fi_df is not None:
            fi_fig = px.bar(fi_df, x='Importance', y='Feature', orientation='h',
                            title="Feature Importance – Q-Score Modell",
                            color_discrete_sequence=["#f39c12"])
    fi_fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                         font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # Feature importance for o_score model
    fi_fig2 = go.Figure()
    o_model = load_model("o_score_model.joblib")
    if o_model is not None:
        fi_df2 = get_feature_importance(o_model)
        if fi_df2 is not None:
            fi_fig2 = px.bar(fi_df2, x='Importance', y='Feature', orientation='h',
                             title="Feature Importance – O-Score Modell",
                             color_discrete_sequence=["#3498db"])
    fi_fig2.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#2d3436",
                          font_color="#e0e0e0", margin=dict(t=50, b=30, l=30, r=20))

    # ML dataset overview
    ml_info = []
    if not ml_df.empty:
        ml_info = [
            html.H5("ML-Datensatz Übersicht", className="text-info mt-4 mb-2"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(f"{len(ml_df):,}", className="text-warning mb-0"),
                    html.Small("Trainings-Samples", className="text-muted"),
                ]), className="text-center kpi-card", style={"borderLeftColor": "#f39c12"}), md=3),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(str(ml_df.shape[1]), className="text-info mb-0"),
                    html.Small("Features", className="text-muted"),
                ]), className="text-center kpi-card", style={"borderLeftColor": "#3498db"}), md=3),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(f"{ml_df.isnull().sum().sum():,}", className="text-warning mb-0"),
                    html.Small("Fehlende Werte", className="text-muted"),
                ]), className="text-center kpi-card", style={"borderLeftColor": "#f39c12"}), md=3),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4(f"{ml_df.dtypes.value_counts().to_dict()}", className="text-muted mb-0 small"),
                    html.Small("Datentypen", className="text-muted"),
                ]), className="text-center kpi-card", style={"borderLeftColor": "#2ecc71"}), md=3),
            ], className="mb-3"),
        ]

    # Model details tabs
    tabs_content = []
    for name, fname in MODEL_FILES.items():
        m = load_model(fname)
        if m is None:
            content = dbc.Alert(f"Modell '{fname}' nicht geladen.", color="warning")
        else:
            attrs = []
            for attr in ['n_estimators', 'max_depth', 'learning_rate', 'C', 'kernel', 'alpha']:
                if hasattr(m, attr):
                    attrs.append(html.Li(f"{attr}: {getattr(m, attr)}"))
            inner_attrs = []
            if hasattr(m, 'named_steps'):
                for step_name, step in m.named_steps.items():
                    inner_attrs.append(html.Li(f"Pipeline-Schritt: {step_name} ({type(step).__name__})"))
                    for attr in ['n_estimators', 'max_depth', 'C']:
                        if hasattr(step, attr):
                            inner_attrs.append(html.Li(f"  {attr}: {getattr(step, attr)}", className="ms-3"))
            content = html.Div([
                html.H6(f"Modell-Typ: {type(m).__name__}", className="text-info"),
                html.Ul(attrs + inner_attrs) if attrs or inner_attrs else html.P("(Keine Parameter extrahierbar)", className="text-muted"),
            ])
        tabs_content.append(dbc.Tab(content, label=name))

    return dbc.Container([
        html.H3("🎯 ML Modell Details", className="mb-1 text-warning"),
        html.P("Feature Importance, Modell-Typen und Parameter-Übersicht.", className="text-muted mb-4"),

        html.H5("Modell-Status", className="text-info mb-3"),
        dbc.Row(model_cards),

        *ml_info,

        html.Hr(className="border-secondary mt-3"),
        html.H5("Feature Importance", className="text-info mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fi_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=fi_fig2, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),

        html.Hr(className="border-secondary"),
        html.H5("Modell-Details", className="text-info mb-3"),
        dbc.Tabs(tabs_content),
    ], fluid=True, className="py-3")
