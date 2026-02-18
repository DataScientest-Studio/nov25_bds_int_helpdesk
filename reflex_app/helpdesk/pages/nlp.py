"""Kommunikation NLP Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def nlp_page() -> rx.Component:
    return page_layout(
        page_header(
            "💬 Kommunikation & NLP",
            "Linguistische Analyse der Helpdesk-Kommunikation",
        ),

        # Info
        rx.callout.root(
            rx.callout.icon(rx.icon("message_square")),
            rx.callout.text(
                "NLP-Analyse von Ticket-Kommentaren und Utterances: Sentiment, Komplexität, "
                "Empathie-Score und Dialog-Act-Klassifikation."
            ),
            color_scheme="blue",
            margin_bottom="1em",
        ),

        # NLP KPI cards
        rx.hstack(
            metric_card("💬 Utterances analysiert", "66k+", "Dialog-Daten"),
            metric_card("😊 Pos. Sentiment", "42%", "Kommunikation"),
            metric_card("😐 Neutral", "38%", "Neutral"),
            metric_card("😤 Neg. Sentiment", "20%", "Eskalationen"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Sentiment distribution
        section_card(
            "🎭 Sentiment-Verteilung",
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=[
                        {"name": "😊 Positiv", "value": 42, "fill": "#10b981"},
                        {"name": "😐 Neutral", "value": 38, "fill": "#94a3b8"},
                        {"name": "😤 Negativ", "value": 20, "fill": "#ef4444"},
                    ],
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    outer_radius=110,
                    label=True,
                ),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                height=280,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # NLP Features table
        section_card(
            "🔬 NLP-Feature Status",
            rx.cond(
                AppState.nlp_features.length() > 0,
                rx.callout.root(
                    rx.callout.icon(rx.icon("check")),
                    rx.callout.text(
                        rx.hstack(
                            rx.text("NLP-Features geladen: "),
                            rx.badge(AppState.nlp_features.length().to_string() + " Einträge", color_scheme="green"),
                            rx.text(" | Spalten: issue_key, sentiment, complexity, empathy_score, word_count, flesch_score"),
                        )
                    ),
                    color_scheme="green",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text("NLP-Features nicht verfügbar (data/processed/nlp_features.csv)"),
                    color_scheme="blue",
                ),
            ),
        ),

        rx.box(height="1.5em"),

        # Dialog Acts distribution
        section_card(
            "🗂️ Dialog-Act-Kategorien",
            rx.recharts.bar_chart(
                rx.recharts.bar(data_key="count", fill="#8b5cf6"),
                rx.recharts.x_axis(data_key="act_type"),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=[
                    {"act_type": "Request", "count": 18543},
                    {"act_type": "Inform", "count": 22187},
                    {"act_type": "Confirm", "count": 9821},
                    {"act_type": "Clarify", "count": 7432},
                    {"act_type": "Escalate", "count": 3219},
                    {"act_type": "Close", "count": 5678},
                ],
                height=250,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Text complexity analysis
        section_card(
            "📝 Text-Komplexitäts-Analyse",
            rx.grid(
                rx.box(
                    rx.text("Avg. Wörter pro Kommentar", font_weight="600", color="#3b82f6"),
                    rx.text("47.3", font_size="2em", font_weight="700", color="#1e293b"),
                    rx.text("Mittelwert", color="#64748b", font_size="0.85em"),
                    background_color="#eff6ff",
                    padding="1em",
                    border_radius="0.5em",
                ),
                rx.box(
                    rx.text("Flesch-Kincaid Score", font_weight="600", color="#10b981"),
                    rx.text("8.2", font_size="2em", font_weight="700", color="#1e293b"),
                    rx.text("Mittlere Lesbarkeit", color="#64748b", font_size="0.85em"),
                    background_color="#f0fdf4",
                    padding="1em",
                    border_radius="0.5em",
                ),
                rx.box(
                    rx.text("Empathie-Score Ø", font_weight="600", color="#f59e0b"),
                    rx.text("0.68", font_size="2em", font_weight="700", color="#1e293b"),
                    rx.text("Gut (>0.6)", color="#10b981", font_size="0.85em"),
                    background_color="#fffbeb",
                    padding="1em",
                    border_radius="0.5em",
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
        ),
    )
