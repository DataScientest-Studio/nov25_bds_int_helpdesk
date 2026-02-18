"""Live Dashboard Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, metric_card, section_card, page_header


def status_pie_chart() -> rx.Component:
    """Status distribution as pie."""
    return rx.cond(
        AppState.status_distribution.length() > 0,
        rx.plotly(
            data=rx.foreach(
                AppState.status_distribution,
                lambda item: {
                    "type": "pie",
                    "labels": [item["status"]],
                    "values": [item["count"]],
                    "hole": 0.4,
                },
            ),
            layout={
                "height": 280,
                "margin": {"t": 10, "b": 10, "l": 10, "r": 10},
                "showlegend": True,
            },
            width="100%",
        ),
        rx.text("Keine Daten verfügbar", color="#94a3b8"),
    )


def priority_bar_chart() -> rx.Component:
    """Priority distribution bar chart."""
    return rx.cond(
        AppState.priority_distribution.length() > 0,
        rx.recharts.bar_chart(
            rx.recharts.bar(data_key="count", fill="#3b82f6"),
            rx.recharts.x_axis(data_key="priority"),
            rx.recharts.y_axis(),
            rx.recharts.graphing_tooltip(),
            data=AppState.priority_distribution,
            height=280,
            width="100%",
        ),
        rx.text("Keine Daten verfügbar", color="#94a3b8"),
    )


def recent_tickets_table() -> rx.Component:
    """Recent tickets table."""
    return rx.cond(
        AppState.recent_tickets.length() > 0,
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Ticket"),
                    rx.table.column_header_cell("Titel / Summary"),
                    rx.table.column_header_cell("Status"),
                    rx.table.column_header_cell("Priorität"),
                    rx.table.column_header_cell("Bearbeiter"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    AppState.recent_tickets,
                    lambda row: rx.table.row(
                        rx.table.cell(rx.text(row["ticket_num"], font_size="0.85em")),
                        rx.table.cell(rx.text(row["title"], font_size="0.85em", max_width="300px")),
                        rx.table.cell(rx.badge(row["status"], color_scheme="blue")),
                        rx.table.cell(rx.text(row["priority"], font_size="0.85em")),
                        rx.table.cell(rx.text(row["assignee"], font_size="0.85em")),
                    ),
                ),
            ),
            width="100%",
        ),
        rx.text("Keine aktuellen Tickets verfügbar", color="#94a3b8"),
    )


def dashboard_page() -> rx.Component:
    """Live Dashboard page content."""
    return page_layout(
        page_header(
            "🏠 Live Dashboard",
            "Echtzeit-Übersicht aller Helpdesk-Aktivitäten"
        ),

        # KPI Row
        rx.hstack(
            metric_card("🎫 Tickets gesamt", AppState.kpi_total_tickets.to_string(), ""),
            metric_card("📂 Offen", AppState.kpi_open_tickets.to_string(), "In Bearbeitung"),
            metric_card("✅ Heute gelöst", AppState.kpi_resolved_today.to_string(), ""),
            metric_card("🚨 Kritisch", AppState.kpi_critical.to_string(), "Priorität 1", "#ef4444"),
            metric_card("👥 Mitarbeiter", AppState.kpi_employees.to_string(), ""),
            metric_card("🔴 Risiko ROT", AppState.kpi_risk_red.to_string(), "Handlungsbedarf", "#ef4444"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # Charts row
        rx.hstack(
            section_card(
                "📊 Status-Verteilung",
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        data=AppState.status_distribution,
                        data_key="count",
                        name_key="status",
                        cx="50%",
                        cy="50%",
                        outer_radius=100,
                        fill="#3b82f6",
                        label=True,
                    ),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    height=280,
                    width="100%",
                ),
            ),
            section_card(
                "📈 Prioritäts-Verteilung",
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="count", fill="#8b5cf6"),
                    rx.recharts.x_axis(data_key="priority"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    data=AppState.priority_distribution,
                    height=280,
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
            align_items="start",
        ),

        rx.box(height="1.5em"),

        # Alerts
        rx.cond(
            AppState.alerts.length() > 0,
            section_card(
                "🔔 Aktuelle Alerts",
                rx.foreach(
                    AppState.alerts,
                    lambda alert: rx.box(
                        rx.hstack(
                            rx.badge("⚠️ ALERT", color_scheme="red"),
                            rx.text(str(alert.get("message", "Kein Text")), font_size="0.9em"),
                            spacing="2",
                        ),
                        padding="0.5em",
                        border_left="3px solid #ef4444",
                        margin_bottom="0.5em",
                    ),
                ),
            ),
            rx.fragment(),
        ),

        rx.box(height="1.5em"),

        # Recent tickets
        section_card(
            "🎫 Neueste Tickets",
            recent_tickets_table(),
        ),

        rx.box(height="1.5em"),

        # Refresh button
        rx.button(
            "🔄 Daten aktualisieren",
            on_click=AppState.refresh_data,
            color_scheme="blue",
            variant="soft",
        ),
    )
