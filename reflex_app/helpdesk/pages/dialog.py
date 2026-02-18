"""Dialog Analyse Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def dialog_page() -> rx.Component:
    return page_layout(
        page_header(
            "💬 Dialog Analyse",
            "Analyse von Helpdesk-Gesprächen nach Dialog-Akten und Mustern",
        ),

        # KPIs
        rx.hstack(
            metric_card("💬 Utterances gesamt", "66k+", "Analysiert"),
            metric_card("🗂️ Dialog-Akte", "8", "Kategorien"),
            metric_card("📊 Avg. Turns/Ticket", "4.7", "Gesprächsrunden"),
            metric_card("✅ Erfolgreiche Dialoge", "91.5%", "Abschluss"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Dialog acts distribution
        section_card(
            "📊 Dialog-Akt Verteilung",
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=[
                        {"name": "Inform", "value": 33.5, "fill": "#3b82f6"},
                        {"name": "Request", "value": 28.0, "fill": "#8b5cf6"},
                        {"name": "Confirm", "value": 14.8, "fill": "#10b981"},
                        {"name": "Clarify", "value": 11.2, "fill": "#f59e0b"},
                        {"name": "Escalate", "value": 4.9, "fill": "#ef4444"},
                        {"name": "Close", "value": 8.6, "fill": "#06b6d4"},
                    ],
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    outer_radius=130,
                    label=True,
                ),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                height=320,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Dialog flow analysis
        section_card(
            "🔄 Typischer Dialog-Fluss",
            rx.recharts.funnel_chart(
                rx.recharts.funnel(
                    rx.recharts.label_list(data_key="name", position="right", fill="#1e293b"),
                    data=[
                        {"value": 100, "name": "Ticket erstellt"},
                        {"value": 97, "name": "Erste Antwort"},
                        {"value": 89, "name": "Diagnose"},
                        {"value": 82, "name": "Lösungsversuch"},
                        {"value": 78, "name": "Kundenbestätigung"},
                        {"value": 75, "name": "Ticket geschlossen"},
                    ],
                    data_key="value",
                    fill="#3b82f6",
                ),
                height=320,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Dialog acts raw data
        section_card(
            "📋 Dialog-Akte Datensatz",
            rx.cond(
                AppState.dialog_acts.length() > 0,
                rx.callout.root(
                    rx.callout.icon(rx.icon("check")),
                    rx.callout.text(
                        rx.hstack(
                            rx.text("Dialog-Daten geladen: "),
                            rx.badge(AppState.dialog_acts.length().to_string() + " Einträge", color_scheme="green"),
                        )
                    ),
                    color_scheme="green",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text(
                        "Dialog-Daten nicht verfügbar (data/processed/dialog_acts.csv). "
                        "Bitte NLP-Pipeline ausführen."
                    ),
                    color_scheme="blue",
                ),
            ),
        ),

        rx.box(height="1.5em"),

        # Best practice examples
        section_card(
            "💡 Best-Practice Dialog-Muster",
            rx.vstack(
                rx.box(
                    rx.text("✅ Schnelle Lösung (< 2h)", font_weight="600", color="#10b981"),
                    rx.text("Request → Inform → Confirm → Close", font_size="0.9em", color="#64748b", margin_top="0.3em"),
                    rx.text("Direkte Diagnose, klare Kommunikation, schnelle Eskalation bei Bedarf", font_size="0.85em"),
                    background_color="#f0fdf4",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="3px solid #10b981",
                    width="100%",
                ),
                rx.box(
                    rx.text("⚠️ Problematischer Dialog", font_weight="600", color="#f59e0b"),
                    rx.text("Request → Clarify → Clarify → Clarify → Escalate", font_size="0.9em", color="#64748b", margin_top="0.3em"),
                    rx.text("Viele Rückfragen, keine klare Lösungsrichtung, späte Eskalation", font_size="0.85em"),
                    background_color="#fffbeb",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="3px solid #f59e0b",
                    width="100%",
                ),
                rx.box(
                    rx.text("🔴 Eskalations-Muster", font_weight="600", color="#ef4444"),
                    rx.text("Request → Inform → Escalate → Reassign → Resolve", font_size="0.9em", color="#64748b", margin_top="0.3em"),
                    rx.text("Ticket überschreitet Kompetenz, korrekte Eskalation aber hoher Zeitverlust", font_size="0.85em"),
                    background_color="#fef2f2",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="3px solid #ef4444",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
        ),
    )
