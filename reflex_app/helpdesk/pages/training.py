"""Training Defizite Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header


def training_page() -> rx.Component:
    return page_layout(
        page_header(
            "🏋️ Training & Defizite",
            "Identifikation von Mitarbeitern mit Schulungsbedarf",
        ),

        # Info box
        rx.callout.root(
            rx.callout.icon(rx.icon("book_open")),
            rx.callout.text(
                "Mitarbeiter mit einem Durchschnittsscore unter 3.0 (von 5) "
                "in einem oder mehreren Bereichen werden als Schulungsbedarf identifiziert. "
                "Q1 = Lösungsqualität, Q2 = Kommunikation, Q3 = Zeitmanagement."
            ),
            color_scheme="blue",
            margin_bottom="1em",
        ),

        # Training needs by dimension chart
        section_card(
            "📊 Schulungsbedarf nach Dimension",
            rx.recharts.radar_chart(
                rx.recharts.radar(
                    name="Mitarbeiter",
                    data_key="value",
                    fill="#3b82f6",
                    fill_opacity=0.4,
                ),
                rx.recharts.polar_grid(),
                rx.recharts.polar_angle_axis(data_key="dimension"),
                rx.recharts.graphing_tooltip(),
                data=[
                    {"dimension": "Q1: Qualität", "value": 65},
                    {"dimension": "Q2: Kommunikation", "value": 45},
                    {"dimension": "Q3: Zeit", "value": 55},
                    {"dimension": "Compliance", "value": 40},
                    {"dimension": "Teamwork", "value": 70},
                ],
                height=300,
                cx="50%",
                cy="50%",
                outer_radius=100,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Schwächen-Mitarbeiter Tabelle
        section_card(
            "⚠️ Mitarbeiter mit Schulungsbedarf",
            rx.cond(
                AppState.training_gaps.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Mitarbeiter"),
                            rx.table.column_header_cell("Ø Q1 (Qualität)"),
                            rx.table.column_header_cell("Ø Q2 (Kommunikation)"),
                            rx.table.column_header_cell("Anzahl Tickets"),
                            rx.table.column_header_cell("Schulung nötig"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.training_gaps,
                            lambda row: rx.table.row(
                                rx.table.cell(rx.text(row["assignee"], font_size="0.85em")),
                                rx.table.cell(rx.text(row["q1_mean"], font_size="0.85em", font_weight="600")),
                                rx.table.cell(rx.text(row["q2_mean"], font_size="0.85em")),
                                rx.table.cell(rx.text(row["count"], font_size="0.85em")),
                                rx.table.cell(
                                    rx.cond(
                                        row["training_needed"],
                                        rx.badge("JA", color_scheme="red"),
                                        rx.badge("Nein", color_scheme="green"),
                                    )
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                    variant="surface",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text("Keine Schulungsdaten verfügbar. Bitte issues_snapshot_sample.xlsx prüfen."),
                    color_scheme="blue",
                ),
            ),
        ),

        rx.box(height="1.5em"),

        # Empfehlungen
        section_card(
            "💡 Training-Empfehlungen",
            rx.grid(
                rx.box(
                    rx.text("📚 Q1: Lösungsqualität", font_weight="600", color="#3b82f6"),
                    rx.text("• Root-Cause-Analysis Training", font_size="0.85em", margin_top="0.5em"),
                    rx.text("• Dokumentation & Knowledge-Base", font_size="0.85em"),
                    rx.text("• Peer-Review-Prozesse", font_size="0.85em"),
                    background_color="#eff6ff",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="3px solid #3b82f6",
                ),
                rx.box(
                    rx.text("💬 Q2: Kommunikation", font_weight="600", color="#8b5cf6"),
                    rx.text("• Kundenservice-Training", font_size="0.85em", margin_top="0.5em"),
                    rx.text("• Schriftliche Kommunikation", font_size="0.85em"),
                    rx.text("• Eskalations-Management", font_size="0.85em"),
                    background_color="#f5f3ff",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="3px solid #8b5cf6",
                ),
                rx.box(
                    rx.text("⏱️ Q3: Zeitmanagement", font_weight="600", color="#f59e0b"),
                    rx.text("• Priorisierungs-Workshops", font_size="0.85em", margin_top="0.5em"),
                    rx.text("• Agile Arbeitsweisen", font_size="0.85em"),
                    rx.text("• SLA-Bewusstsein stärken", font_size="0.85em"),
                    background_color="#fffbeb",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="3px solid #f59e0b",
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
        ),
    )
