"""Export Center Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header


def export_page() -> rx.Component:
    return page_layout(
        page_header(
            "📥 Export Center",
            "Datensätze und Berichte exportieren",
        ),

        # Export configuration
        section_card(
            "⚙️ Export-Konfiguration",
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Datensatz auswählen", font_weight="500", font_size="0.9em"),
                        rx.select(
                            ["Tickets", "Mitarbeiter", "ML-Datensatz", "NLP Features",
                             "Dialog Acts", "Score Vergleich", "O-Score Ergebnisse",
                             "Workflow Analyse", "Training Defizite"],
                            value=AppState.export_dataset,
                            on_change=AppState.set_export_dataset,
                            width="250px",
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Export-Format", font_weight="500", font_size="0.9em"),
                        rx.select(
                            ["CSV", "Excel (XLSX)", "JSON", "Parquet"],
                            value=AppState.export_format,
                            on_change=AppState.set_export_format,
                            width="200px",
                        ),
                        spacing="1",
                    ),
                    rx.button(
                        "📥 Export starten",
                        on_click=AppState.do_export,
                        color_scheme="blue",
                        size="3",
                        align_self="flex-end",
                    ),
                    spacing="4",
                    flex_wrap="wrap",
                    align_items="flex-end",
                ),
                rx.cond(
                    AppState.export_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("download")),
                        rx.callout.text(AppState.export_message),
                        color_scheme="blue",
                        margin_top="1em",
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Available datasets overview
        section_card(
            "📊 Verfügbare Datensätze zum Export",
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Datensatz"),
                        rx.table.column_header_cell("Größe"),
                        rx.table.column_header_cell("Format"),
                        rx.table.column_header_cell("Beschreibung"),
                        rx.table.column_header_cell("Export"),
                    ),
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.cell("Tickets (vollständig)"),
                        rx.table.cell(rx.badge("66k+ Zeilen", color_scheme="blue")),
                        rx.table.cell("CSV / XLSX"),
                        rx.table.cell("Alle Helpdesk-Tickets mit Metadaten"),
                        rx.table.cell(rx.button("Export", size="1", color_scheme="blue", variant="soft")),
                    ),
                    rx.table.row(
                        rx.table.cell("Mitarbeiter Performance"),
                        rx.table.cell(rx.badge("500+ Zeilen", color_scheme="blue")),
                        rx.table.cell("CSV"),
                        rx.table.cell("Performance-Metriken pro Mitarbeiter"),
                        rx.table.cell(rx.button("Export", size="1", color_scheme="blue", variant="soft")),
                    ),
                    rx.table.row(
                        rx.table.cell("ML Datensatz"),
                        rx.table.cell(rx.badge("1348 Zeilen", color_scheme="purple")),
                        rx.table.cell("CSV"),
                        rx.table.cell("Features + Q-Score Labels für ML"),
                        rx.table.cell(rx.button("Export", size="1", color_scheme="purple", variant="soft")),
                    ),
                    rx.table.row(
                        rx.table.cell("NLP Features"),
                        rx.table.cell(rx.badge("66k+ Zeilen", color_scheme="purple")),
                        rx.table.cell("CSV"),
                        rx.table.cell("Sentiment, Komplexität, Empathie"),
                        rx.table.cell(rx.button("Export", size="1", color_scheme="purple", variant="soft")),
                    ),
                    rx.table.row(
                        rx.table.cell("Score Vergleich (Q vs O)"),
                        rx.table.cell(rx.badge("1348 Zeilen", color_scheme="orange")),
                        rx.table.cell("CSV"),
                        rx.table.cell("Manager-Score vs Objektiver Score"),
                        rx.table.cell(rx.button("Export", size="1", color_scheme="orange", variant="soft")),
                    ),
                    rx.table.row(
                        rx.table.cell("Performance Report"),
                        rx.table.cell(rx.badge("Vollständig", color_scheme="green")),
                        rx.table.cell("PDF"),
                        rx.table.cell("Kompletter Analyse-Bericht"),
                        rx.table.cell(rx.button("Export", size="1", color_scheme="green", variant="soft")),
                    ),
                ),
                width="100%",
                variant="surface",
            ),
        ),

        rx.box(height="1.5em"),

        # Scheduled reports
        section_card(
            "⏰ Geplante Berichte",
            rx.callout.root(
                rx.callout.icon(rx.icon("clock")),
                rx.callout.text(
                    "Automatische Berichte können über Cron-Jobs oder den Scheduler eingerichtet werden. "
                    "Berichte werden in reports/ gespeichert."
                ),
                color_scheme="blue",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("📅 Wöchentlicher Report", font_weight="600"),
                    rx.text("Jeden Montag 08:00 Uhr", color="#64748b", font_size="0.85em"),
                    rx.badge("Aktiv", color_scheme="green"),
                    spacing="1",
                    background_color="#f0fdf4",
                    padding="1em",
                    border_radius="0.5em",
                    flex="1",
                ),
                rx.vstack(
                    rx.text("📅 Monatlicher Report", font_weight="600"),
                    rx.text("1. des Monats, 07:00 Uhr", color="#64748b", font_size="0.85em"),
                    rx.badge("Aktiv", color_scheme="green"),
                    spacing="1",
                    background_color="#f0fdf4",
                    padding="1em",
                    border_radius="0.5em",
                    flex="1",
                ),
                rx.vstack(
                    rx.text("📅 Quartals-Report", font_weight="600"),
                    rx.text("Q1/Q2/Q3/Q4 Start", color="#64748b", font_size="0.85em"),
                    rx.badge("Inaktiv", color_scheme="gray"),
                    spacing="1",
                    background_color="#f8fafc",
                    padding="1em",
                    border_radius="0.5em",
                    flex="1",
                ),
                spacing="4",
                width="100%",
            ),
        ),
    )
