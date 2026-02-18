"""Settings Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header


def settings_page() -> rx.Component:
    return page_layout(
        page_header(
            "⚙️ Einstellungen",
            "Dashboard-Konfiguration und Benutzereinstellungen",
        ),

        # UI Settings
        section_card(
            "🎨 Darstellung",
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Sprache / Language", font_weight="500"),
                        rx.radio_group.root(
                            rx.hstack(
                                rx.radio_group.item(value="de"),
                                rx.text("🇩🇪 Deutsch"),
                                rx.radio_group.item(value="en"),
                                rx.text("🇬🇧 English"),
                                spacing="3",
                            ),
                            value=AppState.language,
                            on_change=AppState.set_language,
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Dark Mode", font_weight="500"),
                        rx.switch(
                            checked=AppState.dark_mode,
                            on_change=AppState.toggle_dark_mode,
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Hilfe-Texte anzeigen", font_weight="500"),
                        rx.switch(
                            checked=AppState.show_help,
                            on_change=AppState.toggle_help,
                        ),
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Emojis anzeigen", font_weight="500"),
                        rx.switch(
                            checked=AppState.show_emojis,
                            on_change=AppState.toggle_emojis,
                        ),
                        spacing="2",
                    ),
                    spacing="6",
                    flex_wrap="wrap",
                ),
                spacing="3",
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Data Settings
        section_card(
            "💾 Datenquellen",
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Quelle"),
                        rx.table.column_header_cell("Pfad"),
                        rx.table.column_header_cell("Status"),
                    ),
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.cell("SQLite DB"),
                        rx.table.cell(rx.code("data/helpdesk.db")),
                        rx.table.cell(rx.badge("✅ Verbunden", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("Issues CSV"),
                        rx.table.cell(rx.code("data/raw/issues.csv")),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("Scored Samples"),
                        rx.table.cell(rx.code("data/raw/issues_snapshot_sample.xlsx")),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("ML Modell"),
                        rx.table.cell(rx.code("models/optimized_scorer.joblib")),
                        rx.table.cell(rx.cond(
                            AppState.model_loaded,
                            rx.badge("✅ Geladen", color_scheme="green"),
                            rx.badge("⚠️ Nicht gefunden", color_scheme="yellow"),
                        )),
                    ),
                ),
                width="100%",
                variant="surface",
            ),
        ),

        rx.box(height="1.5em"),

        # System info
        section_card(
            "ℹ️ System-Informationen",
            rx.table.root(
                rx.table.body(
                    rx.table.row(
                        rx.table.cell(rx.text("Framework", font_weight="500")),
                        rx.table.cell(rx.badge("Reflex 0.8.x", color_scheme="purple")),
                    ),
                    rx.table.row(
                        rx.table.cell(rx.text("Frontend Port", font_weight="500")),
                        rx.table.cell(rx.code("3000")),
                    ),
                    rx.table.row(
                        rx.table.cell(rx.text("Backend Port", font_weight="500")),
                        rx.table.cell(rx.code("8000")),
                    ),
                    rx.table.row(
                        rx.table.cell(rx.text("Version", font_weight="500")),
                        rx.table.cell(rx.text("4.0.0 (Reflex Edition)")),
                    ),
                    rx.table.row(
                        rx.table.cell(rx.text("Python", font_weight="500")),
                        rx.table.cell(rx.text("3.12")),
                    ),
                ),
                width="100%",
                variant="surface",
            ),
        ),

        rx.box(height="1.5em"),

        # Actions
        section_card(
            "🔧 Aktionen",
            rx.hstack(
                rx.button(
                    "🔄 Alle Daten neu laden",
                    on_click=AppState.refresh_data,
                    color_scheme="blue",
                    variant="soft",
                ),
                rx.button(
                    "🗑️ Cache leeren",
                    color_scheme="red",
                    variant="soft",
                ),
                spacing="3",
            ),
        ),
    )
