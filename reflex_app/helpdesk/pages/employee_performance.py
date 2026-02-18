"""Employee Performance Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def employee_performance_page() -> rx.Component:
    return page_layout(
        page_header(
            "👥 Mitarbeiter Performance",
            "Individuelle Leistungsanalyse und Risikobewertung",
        ),

        # KPIs
        rx.hstack(
            metric_card("👥 Mitarbeiter gesamt", AppState.kpi_employees.to_string(), ""),
            metric_card("🔴 Risiko ROT", AppState.kpi_risk_red.to_string(), "Sofort handeln", "#ef4444"),
            metric_card("⭐ Ø Score", AppState.kpi_avg_score.to_string(), "Manager-Bewertung"),
            metric_card("📋 Bewertete Samples", AppState.kpi_scored_samples.to_string(), "Ground Truth"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Filter
        section_card(
            "🔍 Mitarbeiter-Filter",
            rx.hstack(
                rx.input(
                    placeholder="Mitarbeiter-ID oder Name suchen...",
                    value=AppState.employee_filter,
                    on_change=AppState.set_employee_filter,
                    width="350px",
                ),
                rx.button("🔄 Aktualisieren", on_click=AppState.refresh_data, color_scheme="blue", variant="soft"),
                spacing="3",
            ),
        ),

        rx.box(height="1.5em"),

        # Employee performance chart
        section_card(
            "📊 Top Mitarbeiter nach Performance-Score",
            rx.cond(
                AppState.employee_list.length() > 0,
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="avg_score", fill="#10b981", name="Ø Score"),
                    rx.recharts.bar(data_key="ticket_count", fill="#3b82f6", name="Tickets"),
                    rx.recharts.x_axis(data_key="employee", angle=-45, text_anchor="end"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    data=AppState.employee_list,
                    height=350,
                    width="100%",
                ),
                rx.text("Mitarbeiterdaten werden geladen...", color="#94a3b8"),
            ),
        ),

        rx.box(height="1.5em"),

        # Employee table
        section_card(
            "📋 Mitarbeiter-Übersicht",
            rx.cond(
                AppState.employee_list.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Mitarbeiter"),
                            rx.table.column_header_cell("Tickets"),
                            rx.table.column_header_cell("Ø Zeit (h)"),
                            rx.table.column_header_cell("Reopen-Rate"),
                            rx.table.column_header_cell("First-Touch"),
                            rx.table.column_header_cell("Success-Rate"),
                            rx.table.column_header_cell("Risiko"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.employee_list,
                            lambda emp: rx.table.row(
                                rx.table.cell(rx.text(emp["employee"], font_size="0.85em", font_family="monospace")),
                                rx.table.cell(rx.text(emp["ticket_count"], font_size="0.85em")),
                                rx.table.cell(rx.text(emp["avg_time_hours"], font_size="0.85em")),
                                rx.table.cell(rx.text(emp["reopen_rate"], font_size="0.85em")),
                                rx.table.cell(rx.text(emp["first_touch_rate"], font_size="0.85em")),
                                rx.table.cell(rx.text(emp["resolution_success_rate"], font_size="0.85em")),
                                rx.table.cell(rx.badge(emp.get("risk_level", "–"), color_scheme="gray")),
                            ),
                        ),
                    ),
                    width="100%",
                    variant="surface",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text("Keine Mitarbeiterdaten verfügbar. Bitte Datenbank mit `python src/database/db_setup.py` initialisieren oder CSV-Daten prüfen."),
                    color_scheme="blue",
                ),
            ),
        ),
    )
