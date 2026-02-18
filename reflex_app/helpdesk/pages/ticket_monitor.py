"""Ticket Monitor Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def ticket_monitor_page() -> rx.Component:
    return page_layout(
        page_header(
            "🎫 Ticket Monitor",
            "Live-Überwachung aller Helpdesk-Tickets",
        ),

        # KPIs
        rx.hstack(
            metric_card("🎫 Gesamt", AppState.kpi_total_tickets.to_string(), ""),
            metric_card("📂 Offen", AppState.kpi_open_tickets.to_string(), "In Bearbeitung"),
            metric_card("✅ Heute gelöst", AppState.kpi_resolved_today.to_string(), ""),
            metric_card("🚨 Kritisch offen", AppState.kpi_critical.to_string(), "Priorität 1", "#ef4444"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Filter bar
        section_card(
            "🔍 Filter",
            rx.hstack(
                rx.vstack(
                    rx.text("Status", font_size="0.85em", font_weight="500"),
                    rx.select(
                        ["Alle", "Open", "In Progress", "Waiting", "Resolved", "Closed"],
                        value=AppState.ticket_filter_status,
                        on_change=AppState.set_ticket_filter_status,
                        width="180px",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Priorität", font_size="0.85em", font_weight="500"),
                    rx.select(
                        ["Alle", "Blocker", "High", "Medium", "Low", "Minimal"],
                        value=AppState.ticket_filter_priority,
                        on_change=AppState.set_ticket_filter_priority,
                        width="180px",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Suche", font_size="0.85em", font_weight="500"),
                    rx.input(
                        placeholder="Ticket-Nummer oder Titel...",
                        value=AppState.ticket_search,
                        on_change=AppState.set_ticket_search,
                        width="300px",
                    ),
                    spacing="1",
                ),
                rx.button(
                    "🔄 Aktualisieren",
                    on_click=AppState.refresh_data,
                    color_scheme="blue",
                    variant="soft",
                    align_self="flex-end",
                ),
                spacing="4",
                align_items="start",
                flex_wrap="wrap",
            ),
        ),

        rx.box(height="1.5em"),

        # Priority distribution chart
        section_card(
            "📊 Prioritäts-Verteilung",
            rx.recharts.bar_chart(
                rx.recharts.bar(data_key="count", fill="#8b5cf6", radius=[4, 4, 0, 0]),
                rx.recharts.x_axis(data_key="priority"),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=AppState.priority_distribution,
                height=250,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Status distribution pie
        section_card(
            "🍩 Status-Verteilung",
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=AppState.status_distribution,
                    data_key="count",
                    name_key="status",
                    cx="50%",
                    cy="50%",
                    outer_radius=120,
                    fill="#3b82f6",
                    label=True,
                ),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                height=300,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Tickets table
        section_card(
            "📋 Aktuelle Tickets",
            rx.cond(
                AppState.recent_tickets.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Ticket #"),
                            rx.table.column_header_cell("Titel"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Priorität"),
                            rx.table.column_header_cell("Bearbeiter"),
                            rx.table.column_header_cell("Erstellt"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            AppState.recent_tickets,
                            lambda row: rx.table.row(
                                rx.table.cell(
                                    rx.text(
                                        row["ticket_num"],
                                        font_family="monospace",
                                        font_size="0.85em",
                                        color="#3b82f6",
                                    )
                                ),
                                rx.table.cell(
                                    rx.text(
                                        row["title"],
                                        font_size="0.85em",
                                        max_width="300px",
                                        overflow="hidden",
                                        text_overflow="ellipsis",
                                        white_space="nowrap",
                                    )
                                ),
                                rx.table.cell(rx.badge(row["status"], color_scheme="blue")),
                                rx.table.cell(rx.text(row["priority"], font_size="0.85em")),
                                rx.table.cell(rx.text(row["assignee"], font_size="0.85em")),
                                rx.table.cell(rx.text(row["created_at"], font_size="0.85em")),
                            ),
                        ),
                    ),
                    width="100%",
                    variant="surface",
                ),
                rx.text("Keine Tickets verfügbar. Bitte Datenbank initialisieren.", color="#94a3b8"),
            ),
        ),
    )
