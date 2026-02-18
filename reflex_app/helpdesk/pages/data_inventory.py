"""Data Inventory Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def data_inventory_page() -> rx.Component:
    return page_layout(
        page_header(
            "📊 Daten-Inventar",
            "Übersicht aller verfügbaren Datensätze und Qualitätsmetriken",
        ),

        # Overview cards
        rx.hstack(
            metric_card("📋 Issues (CSV)", AppState.kpi_total_tickets.to_string(), "Rohdaten"),
            metric_card("⭐ Bewertete Samples", AppState.kpi_scored_samples.to_string(), "Ground Truth"),
            metric_card("👥 Mitarbeiter", AppState.kpi_employees.to_string(), "Unique"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Dataset overview table
        section_card(
            "📁 Verfügbare Datensätze",
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Datei"),
                        rx.table.column_header_cell("Typ"),
                        rx.table.column_header_cell("Beschreibung"),
                        rx.table.column_header_cell("Status"),
                    ),
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.cell("data/raw/issues.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="blue")),
                        rx.table.cell("66k+ Helpdesk-Tickets mit Workflow-Metadaten"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/raw/issues_snapshot.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="blue")),
                        rx.table.cell("Ticket-Snapshots mit Statuswechseln"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/raw/issues_snapshot_sample.xlsx"),
                        rx.table.cell(rx.badge("XLSX", color_scheme="orange")),
                        rx.table.cell("Manager-Bewertungen (Q1/Q2/Q3 Scores)"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/raw/sample_utterances.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="blue")),
                        rx.table.cell("Dialog-Utterances für NLP-Analyse"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/processed/ml_dataset.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="purple")),
                        rx.table.cell("Aufbereiteter ML-Datensatz (Features + Labels)"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/processed/nlp_features.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="purple")),
                        rx.table.cell("NLP-Features aus Dialog-Analyse"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/processed/dialog_acts.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="purple")),
                        rx.table.cell("Klassifizierte Dialog-Akte"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/processed/employee_metrics_raw.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="purple")),
                        rx.table.cell("Mitarbeiter-Performance-Metriken"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/processed/o_score_results.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="purple")),
                        rx.table.cell("Objektive Score-Berechnungen"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/processed/q_vs_o_score_comparison.csv"),
                        rx.table.cell(rx.badge("CSV", color_scheme="purple")),
                        rx.table.cell("Q-Score vs O-Score Vergleich"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("data/helpdesk.db"),
                        rx.table.cell(rx.badge("SQLite", color_scheme="red")),
                        rx.table.cell("Live-Datenbank mit Tickets, Mitarbeitern, Alerts"),
                        rx.table.cell(rx.badge("✅ Verfügbar", color_scheme="green")),
                    ),
                    rx.table.row(
                        rx.table.cell("models/optimized_scorer.joblib"),
                        rx.table.cell(rx.badge("Model", color_scheme="cyan")),
                        rx.table.cell("Optimiertes ML-Modell (Random Forest)"),
                        rx.table.cell(rx.cond(
                            AppState.model_loaded,
                            rx.badge("✅ Geladen", color_scheme="green"),
                            rx.badge("⚠️ Nicht gefunden", color_scheme="yellow"),
                        )),
                    ),
                ),
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # ML Dataset Preview
        section_card(
            "🔍 ML-Datensatz Vorschau (erste 50 Zeilen)",
            rx.cond(
                AppState.ml_dataset_preview.length() > 0,
                rx.box(
                    rx.text(
                        "Datensatz geladen. ",
                        rx.badge(AppState.ml_dataset_preview.length().to_string() + " Zeilen", color_scheme="green"),
                        font_size="0.9em",
                    ),
                    rx.text(
                        "Features: employee, ticket_count, avg_time_hours, median_time_hours, "
                        "reopen_rate, first_touch_rate, resolution_success_rate, avg_comments, "
                        "avg_steps, Q1, Q2, Q3",
                        color="#64748b",
                        font_size="0.85em",
                        margin_top="0.5em",
                        font_family="monospace",
                    ),
                    background_color="#f8fafc",
                    padding="1em",
                    border_radius="0.5em",
                    border="1px solid #e2e8f0",
                ),
                rx.text("ML-Datensatz nicht geladen", color="#94a3b8"),
            ),
        ),

        rx.box(height="1.5em"),

        # Feature columns
        section_card(
            "🧩 Feature-Kategorien",
            rx.grid(
                rx.box(
                    rx.text("⏱️ Zeitmetriken", font_weight="600", margin_bottom="0.5em"),
                    rx.text("• wf_total_time", font_size="0.85em", color="#64748b"),
                    rx.text("• avg_time_hours", font_size="0.85em", color="#64748b"),
                    rx.text("• median_time", font_size="0.85em", color="#64748b"),
                    background_color="#f0f9ff",
                    padding="1em",
                    border_radius="0.5em",
                ),
                rx.box(
                    rx.text("🔄 Workflow-Metriken", font_weight="600", margin_bottom="0.5em"),
                    rx.text("• step_count", font_size="0.85em", color="#64748b"),
                    rx.text("• reopen_rate", font_size="0.85em", color="#64748b"),
                    rx.text("• first_touch_rate", font_size="0.85em", color="#64748b"),
                    background_color="#f0fdf4",
                    padding="1em",
                    border_radius="0.5em",
                ),
                rx.box(
                    rx.text("💬 Kommunikations-Metriken", font_weight="600", margin_bottom="0.5em"),
                    rx.text("• avg_comments", font_size="0.85em", color="#64748b"),
                    rx.text("• nlp_features", font_size="0.85em", color="#64748b"),
                    rx.text("• dialog_acts", font_size="0.85em", color="#64748b"),
                    background_color="#fdf4ff",
                    padding="1em",
                    border_radius="0.5em",
                ),
                rx.box(
                    rx.text("🎯 Score Labels", font_weight="600", margin_bottom="0.5em"),
                    rx.text("• Q1: Lösungsqualität", font_size="0.85em", color="#64748b"),
                    rx.text("• Q2: Kommunikation", font_size="0.85em", color="#64748b"),
                    rx.text("• Q3: Zeitmanagement", font_size="0.85em", color="#64748b"),
                    background_color="#fff7ed",
                    padding="1em",
                    border_radius="0.5em",
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
        ),
    )
