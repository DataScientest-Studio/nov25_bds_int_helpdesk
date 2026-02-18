"""Objektivitätsprüfung Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def objectivity_page() -> rx.Component:
    return page_layout(
        page_header(
            "🔍 Objektivitätsprüfung",
            "Bias-Analyse der Manager-Bewertungen: Halo-Effekt, Leniency, Central Tendency",
        ),

        # Warning
        rx.callout.root(
            rx.callout.icon(rx.icon("triangle_alert")),
            rx.callout.text(
                "⚠️ BIAS-WARNUNG: Die Datenanalyse zeigt starke Anzeichen von Halo-Effekt und "
                "Leniency-Bias in den Manager-Bewertungen. Diese verfälschen die Performance-Einschätzung "
                "und sollten durch das ML-Modell korrigiert werden."
            ),
            color_scheme="red",
            margin_bottom="1em",
        ),

        # Bias KPI cards
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.text("Halo-Effekt", color="#64748b", font_size="0.85em"),
                    rx.text("0.921", font_size="2em", font_weight="700", color="#ef4444"),
                    rx.badge("⚠️ HOCH (>0.8)", color_scheme="red"),
                    spacing="1",
                    align_items="start",
                ),
                background_color="white",
                border="2px solid #fca5a5",
                border_radius="0.75em",
                padding="1.2em",
                flex="1",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Leniency Bias (Q1)", color="#64748b", font_size="0.85em"),
                    rx.text("Ø 3.72", font_size="2em", font_weight="700", color="#f59e0b"),
                    rx.badge("⚠️ Zu milde (>3.5)", color_scheme="yellow"),
                    spacing="1",
                    align_items="start",
                ),
                background_color="white",
                border="2px solid #fcd34d",
                border_radius="0.75em",
                padding="1.2em",
                flex="1",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Central Tendency (Std)", color="#64748b", font_size="0.85em"),
                    rx.text("0.73", font_size="2em", font_weight="700", color="#f59e0b"),
                    rx.badge("⚠️ Zu eng (<0.8)", color_scheme="yellow"),
                    spacing="1",
                    align_items="start",
                ),
                background_color="white",
                border="2px solid #fcd34d",
                border_radius="0.75em",
                padding="1.2em",
                flex="1",
            ),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Q-Score Correlation heatmap (static visualization)
        section_card(
            "🔥 Korrelationsmatrix Q1/Q2/Q3",
            rx.box(
                rx.grid(
                    # Header row
                    rx.box(),
                    rx.text("Q1", font_weight="700", text_align="center"),
                    rx.text("Q2", font_weight="700", text_align="center"),
                    rx.text("Q3", font_weight="700", text_align="center"),
                    # Q1 row
                    rx.text("Q1", font_weight="700"),
                    rx.box(rx.text("1.000", color="white", text_align="center"), background_color="#1d4ed8", padding="0.5em", border_radius="0.25em"),
                    rx.box(rx.text("0.921", color="white", text_align="center"), background_color="#ef4444", padding="0.5em", border_radius="0.25em"),
                    rx.box(rx.text("0.887", color="white", text_align="center"), background_color="#f97316", padding="0.5em", border_radius="0.25em"),
                    # Q2 row
                    rx.text("Q2", font_weight="700"),
                    rx.box(rx.text("0.921", color="white", text_align="center"), background_color="#ef4444", padding="0.5em", border_radius="0.25em"),
                    rx.box(rx.text("1.000", color="white", text_align="center"), background_color="#1d4ed8", padding="0.5em", border_radius="0.25em"),
                    rx.box(rx.text("0.903", color="white", text_align="center"), background_color="#ef4444", padding="0.5em", border_radius="0.25em"),
                    # Q3 row
                    rx.text("Q3", font_weight="700"),
                    rx.box(rx.text("0.887", color="white", text_align="center"), background_color="#f97316", padding="0.5em", border_radius="0.25em"),
                    rx.box(rx.text("0.903", color="white", text_align="center"), background_color="#ef4444", padding="0.5em", border_radius="0.25em"),
                    rx.box(rx.text("1.000", color="white", text_align="center"), background_color="#1d4ed8", padding="0.5em", border_radius="0.25em"),
                    columns="4",
                    spacing="2",
                    max_width="400px",
                ),
                padding="1em",
            ),
            rx.text(
                "💡 Interpretation: Korrelationen > 0.8 zwischen Q1/Q2/Q3 deuten auf starken Halo-Effekt hin. "
                "Der Manager bewertet tendenziell alle Dimensionen ähnlich, statt unabhängig.",
                color="#64748b",
                font_size="0.85em",
                margin_top="1em",
            ),
        ),

        rx.box(height="1.5em"),

        # O-Score vs Q-Score comparison
        section_card(
            "⚖️ Objektiver Score (O-Score) vs. Manager-Score (Q-Score)",
            rx.cond(
                AppState.score_comparison.length() > 0,
                rx.recharts.scatter_chart(
                    rx.recharts.scatter(
                        data=AppState.score_comparison,
                        name="Q vs O Score",
                        fill="#3b82f6",
                    ),
                    rx.recharts.x_axis(data_key="q_score", name="Q-Score (Manager)"),
                    rx.recharts.y_axis(data_key="o_score", name="O-Score (Objektiv)"),
                    rx.recharts.graphing_tooltip(cursor={"strokeDasharray": "3 3"}),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    height=300,
                    width="100%",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text("Score-Vergleichsdaten nicht verfügbar (q_vs_o_score_comparison.csv)"),
                    color_scheme="blue",
                ),
            ),
        ),

        rx.box(height="1.5em"),

        # Recommendations
        section_card(
            "💡 Handlungsempfehlungen",
            rx.vstack(
                rx.hstack(
                    rx.badge("1", color_scheme="blue"),
                    rx.text("**Kalibrierungssitzungen** einführen: Regelmäßige Manager-Meetings zur Score-Normierung", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("2", color_scheme="blue"),
                    rx.text("**Blind-Scoring**: Bewertungen ohne Kenntnis früherer Scores durchführen", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("3", color_scheme="blue"),
                    rx.text("**ML-Modell als Benchmark**: O-Score als objektiven Anker verwenden", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("4", color_scheme="blue"),
                    rx.text("**360°-Feedback** integrieren: Kollegenbewertungen und Kundenzufriedenheit einbeziehen", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
        ),
    )
