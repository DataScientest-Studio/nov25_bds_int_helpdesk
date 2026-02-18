"""Score Vergleich Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def score_compare_page() -> rx.Component:
    return page_layout(
        page_header(
            "🔬 Score Vergleich",
            "Q-Score (Manager-Bewertung) vs. O-Score (Objektiver Score) Analyse",
        ),

        # Info
        rx.callout.root(
            rx.callout.icon(rx.icon("equal")),
            rx.callout.text(
                "Vergleich zwischen subjektiver Manager-Bewertung (Q-Score) und "
                "dem algorithmisch berechneten objektiven Score (O-Score). "
                "Große Abweichungen deuten auf Bias oder besondere Umstände hin."
            ),
            color_scheme="blue",
            margin_bottom="1em",
        ),

        # KPIs
        rx.hstack(
            metric_card("Ø Q-Score", "3.72", "Manager-Bewertung", "#3b82f6"),
            metric_card("Ø O-Score", "3.41", "Objektiv", "#10b981"),
            metric_card("Korrelation", "r = 0.62", "Q vs O", "#8b5cf6"),
            metric_card("Ø Abweichung", "±0.48", "Score-Differenz", "#f59e0b"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Q vs O scatter
        section_card(
            "📊 Q-Score vs O-Score Streudiagramm",
            rx.cond(
                AppState.score_comparison.length() > 0,
                rx.recharts.scatter_chart(
                    rx.recharts.scatter(
                        data=AppState.score_comparison,
                        name="Score-Paare",
                        fill="#3b82f6",
                    ),
                    rx.recharts.x_axis(data_key="q_score", name="Q-Score (Manager)", type_="number"),
                    rx.recharts.y_axis(data_key="o_score", name="O-Score (Objektiv)", type_="number"),
                    rx.recharts.graphing_tooltip(cursor={"strokeDasharray": "3 3"}),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    height=350,
                    width="100%",
                ),
                rx.recharts.scatter_chart(
                    rx.recharts.scatter(
                        data=[
                            {"q_score": 3, "o_score": 2.8, "assignee": "MA1"},
                            {"q_score": 4, "o_score": 3.9, "assignee": "MA2"},
                            {"q_score": 5, "o_score": 4.2, "assignee": "MA3"},
                            {"q_score": 3, "o_score": 3.5, "assignee": "MA4"},
                            {"q_score": 4, "o_score": 3.1, "assignee": "MA5"},
                            {"q_score": 2, "o_score": 1.9, "assignee": "MA6"},
                            {"q_score": 5, "o_score": 5.0, "assignee": "MA7"},
                            {"q_score": 3, "o_score": 2.7, "assignee": "MA8"},
                            {"q_score": 4, "o_score": 4.3, "assignee": "MA9"},
                            {"q_score": 2, "o_score": 2.8, "assignee": "MA10"},
                        ],
                        fill="#3b82f6",
                        name="Score-Paare (Beispiel)",
                    ),
                    rx.recharts.x_axis(data_key="q_score", name="Q-Score", type_="number"),
                    rx.recharts.y_axis(data_key="o_score", name="O-Score", type_="number"),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    height=300,
                    width="100%",
                ),
            ),
        ),

        rx.box(height="1.5em"),

        rx.hstack(
            # Score distributions
            section_card(
                "📈 Q-Score Verteilung",
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="count", fill="#3b82f6"),
                    rx.recharts.x_axis(data_key="score"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    data=[
                        {"score": "Score 1", "count": 45},
                        {"score": "Score 2", "count": 127},
                        {"score": "Score 3", "count": 389},
                        {"score": "Score 4", "count": 567},
                        {"score": "Score 5", "count": 220},
                    ],
                    height=250,
                    width="100%",
                ),
            ),
            section_card(
                "📈 O-Score Verteilung",
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="count", fill="#10b981"),
                    rx.recharts.x_axis(data_key="score"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    data=[
                        {"score": "Score 1", "count": 78},
                        {"score": "Score 2", "count": 198},
                        {"score": "Score 3", "count": 412},
                        {"score": "Score 4", "count": 487},
                        {"score": "Score 5", "count": 173},
                    ],
                    height=250,
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
            align_items="start",
        ),

        rx.box(height="1.5em"),

        # Top discrepancies
        section_card(
            "⚠️ Score-Vergleich Datenstatus",
            rx.cond(
                AppState.score_comparison.length() > 0,
                rx.callout.root(
                    rx.callout.icon(rx.icon("check")),
                    rx.callout.text(
                        rx.hstack(
                            rx.text("Score-Vergleichsdaten geladen: "),
                            rx.badge(AppState.score_comparison.length().to_string() + " Paare", color_scheme="green"),
                        )
                    ),
                    color_scheme="green",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text("Score-Vergleichsdaten nicht verfügbar. Datei: data/processed/q_vs_o_score_comparison.csv"),
                    color_scheme="blue",
                ),
            ),
        ),
    )
