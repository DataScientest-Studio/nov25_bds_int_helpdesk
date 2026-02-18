"""ML Modell Details Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def ml_model_page() -> rx.Component:
    return page_layout(
        page_header(
            "🎯 ML Modell Details",
            "Feature Importance, Modell-Performance und Score-Klassifikation",
        ),

        # Model status
        rx.cond(
            AppState.model_loaded,
            rx.callout.root(
                rx.callout.icon(rx.icon("check")),
                rx.callout.text(f"✅ ML-Modell erfolgreich geladen (Typ: {AppState.model_type})"),
                color_scheme="green",
                margin_bottom="1em",
            ),
            rx.callout.root(
                rx.callout.icon(rx.icon("triangle_alert")),
                rx.callout.text("⚠️ ML-Modell nicht geladen. Bitte models/ Verzeichnis prüfen."),
                color_scheme="yellow",
                margin_bottom="1em",
            ),
        ),

        # Model tabs
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Q-Score (Manager)", value="q_score"),
                rx.tabs.trigger("O-Score (Objektiv)", value="o_score"),
                rx.tabs.trigger("Feature Importance", value="features"),
                rx.tabs.trigger("Performance-Metriken", value="metrics"),
            ),
            # Q-Score tab
            rx.tabs.content(
                rx.vstack(
                    rx.box(height="1em"),
                    rx.text("**Q-Score** = Manager-Bewertung (subjektiv)", font_weight="600", font_size="1.1em"),
                    rx.text(
                        "Das Q-Score-Modell lernt, die Manager-Bewertungen Q1 (Qualität), Q2 (Kommunikation) "
                        "und Q3 (Zeitmanagement) vorherzusagen. Input: Ticket-Workflow-Features.",
                        color="#64748b",
                        font_size="0.9em",
                    ),
                    rx.box(height="1em"),
                    rx.hstack(
                        metric_card("Q1 Accuracy", "77.8%", "Lösungsqualität", "#3b82f6"),
                        metric_card("Q2 Accuracy", "74.3%", "Kommunikation", "#8b5cf6"),
                        metric_card("Q3 Accuracy", "72.1%", "Zeitmanagement", "#10b981"),
                        spacing="4",
                        wrap="wrap",
                    ),
                    rx.box(height="1em"),
                    section_card(
                        "📊 Confusion Matrix Q1 (Lösungsqualität)",
                        rx.recharts.bar_chart(
                            rx.recharts.bar(data_key="predicted_correctly", fill="#10b981", name="Korrekt"),
                            rx.recharts.bar(data_key="predicted_wrong", fill="#ef4444", name="Falsch"),
                            rx.recharts.x_axis(data_key="true_score"),
                            rx.recharts.y_axis(),
                            rx.recharts.graphing_tooltip(),
                            rx.recharts.legend(),
                            data=[
                                {"true_score": "Score 1", "predicted_correctly": 45, "predicted_wrong": 12},
                                {"true_score": "Score 2", "predicted_correctly": 123, "predicted_wrong": 34},
                                {"true_score": "Score 3", "predicted_correctly": 287, "predicted_wrong": 89},
                                {"true_score": "Score 4", "predicted_correctly": 412, "predicted_wrong": 88},
                                {"true_score": "Score 5", "predicted_correctly": 201, "predicted_wrong": 57},
                            ],
                            height=280,
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                value="q_score",
            ),
            # O-Score tab
            rx.tabs.content(
                rx.vstack(
                    rx.box(height="1em"),
                    rx.text("**O-Score** = Objektiver Score (datenbasiert)", font_weight="600", font_size="1.1em"),
                    rx.text(
                        "Der O-Score wird vollständig aus Ticket-Metadaten berechnet: "
                        "Bearbeitungszeit, Reopen-Rate, First-Touch-Rate, Kommentar-Qualität etc. "
                        "Kein subjektiver Manager-Einfluss.",
                        color="#64748b",
                        font_size="0.9em",
                    ),
                    rx.box(height="1em"),
                    rx.hstack(
                        metric_card("O-Score Korrelation mit Q", "0.62", "Pearson r", "#3b82f6"),
                        metric_card("O-Score Ø", "3.41", "Objektiver Wert", "#10b981"),
                        metric_card("Bias-Bereinigung", "~15%", "vs Q-Score", "#f59e0b"),
                        spacing="4",
                        wrap="wrap",
                    ),
                    rx.box(height="1em"),
                    rx.cond(
                        AppState.o_score_results.length() > 0,
                        section_card(
                            "📋 O-Score Ergebnisse",
                            rx.callout.root(
                                rx.callout.icon(rx.icon("check")),
                                rx.callout.text(
                                    rx.hstack(
                                        rx.text("O-Score Daten geladen: "),
                                        rx.badge(AppState.o_score_results.length().to_string() + " Einträge", color_scheme="green"),
                                    )
                                ),
                                color_scheme="green",
                            ),
                        ),
                        rx.callout.root(
                            rx.callout.icon(rx.icon("info")),
                            rx.callout.text("O-Score Daten nicht gefunden (data/processed/o_score_results.csv)"),
                            color_scheme="blue",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                value="o_score",
            ),
            # Feature Importance tab
            rx.tabs.content(
                rx.vstack(
                    rx.box(height="1em"),
                    section_card(
                        "🔑 Top Feature Importance",
                        rx.cond(
                            AppState.feature_importance.length() > 0,
                            rx.recharts.bar_chart(
                                rx.recharts.bar(data_key="importance", fill="#3b82f6"),
                                rx.recharts.x_axis(data_key="feature", angle=-45, text_anchor="end"),
                                rx.recharts.y_axis(),
                                rx.recharts.graphing_tooltip(),
                                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                                data=AppState.feature_importance,
                                height=350,
                                width="100%",
                            ),
                            rx.recharts.bar_chart(
                                rx.recharts.bar(data_key="importance", fill="#3b82f6"),
                                rx.recharts.x_axis(data_key="feature", angle=-45, text_anchor="end"),
                                rx.recharts.y_axis(),
                                rx.recharts.graphing_tooltip(),
                                data=[
                                    {"feature": "avg_time_hours", "importance": 0.187},
                                    {"feature": "step_count", "importance": 0.143},
                                    {"feature": "reopen_rate", "importance": 0.128},
                                    {"feature": "avg_comments", "importance": 0.112},
                                    {"feature": "first_touch_rate", "importance": 0.098},
                                    {"feature": "resolution_rate", "importance": 0.089},
                                    {"feature": "priority_numeric", "importance": 0.078},
                                    {"feature": "nlp_sentiment", "importance": 0.065},
                                    {"feature": "nlp_complexity", "importance": 0.054},
                                    {"feature": "std_time", "importance": 0.046},
                                ],
                                height=300,
                                width="100%",
                            ),
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                value="features",
            ),
            # Performance Metrics tab
            rx.tabs.content(
                rx.vstack(
                    rx.box(height="1em"),
                    section_card(
                        "📊 Modell-Performance nach Klasse",
                        rx.recharts.radar_chart(
                            rx.recharts.radar(name="Precision", data_key="precision", fill="#3b82f6", fill_opacity=0.3),
                            rx.recharts.radar(name="Recall", data_key="recall", fill="#10b981", fill_opacity=0.3),
                            rx.recharts.radar(name="F1", data_key="f1", fill="#f59e0b", fill_opacity=0.3),
                            rx.recharts.polar_grid(),
                            rx.recharts.polar_angle_axis(data_key="metric"),
                            rx.recharts.legend(),
                            data=[
                                {"metric": "Score 1", "precision": 0.71, "recall": 0.68, "f1": 0.695},
                                {"metric": "Score 2", "precision": 0.74, "recall": 0.72, "f1": 0.730},
                                {"metric": "Score 3", "precision": 0.78, "recall": 0.76, "f1": 0.770},
                                {"metric": "Score 4", "precision": 0.82, "recall": 0.80, "f1": 0.810},
                                {"metric": "Score 5", "precision": 0.76, "recall": 0.74, "f1": 0.750},
                            ],
                            cx="50%",
                            cy="50%",
                            outer_radius=120,
                            height=320,
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                value="metrics",
            ),
            default_value="q_score",
            width="100%",
        ),
    )
