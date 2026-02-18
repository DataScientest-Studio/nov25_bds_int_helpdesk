"""Prozess Compliance Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def compliance_page() -> rx.Component:
    return page_layout(
        page_header(
            "🔄 Prozess Compliance",
            "Einhaltung von Workflows, SLAs und Eskalationspfaden",
        ),

        # KPI Cards
        rx.hstack(
            metric_card("✅ SLA Eingehalten", "78.3%", "Gesamt", "#10b981"),
            metric_card("⚠️ SLA Verletzt", "21.7%", "Handlungsbedarf", "#ef4444"),
            metric_card("🔄 Korrekte Eskalation", "89.1%", "Compliance", "#3b82f6"),
            metric_card("📋 Workflow-Konform", "91.5%", "Prozesse", "#10b981"),
            spacing="4",
            wrap="wrap",
            width="100%",
        ),

        rx.box(height="1.5em"),

        # SLA Compliance over time
        section_card(
            "📈 SLA-Compliance Zeitverlauf",
            rx.recharts.line_chart(
                rx.recharts.line(data_key="sla_rate", stroke="#10b981", name="SLA-Rate %", dot=False),
                rx.recharts.line(data_key="target", stroke="#ef4444", stroke_dasharray="5 5", name="Ziel 85%", dot=False),
                rx.recharts.x_axis(data_key="month"),
                rx.recharts.y_axis(domain=[60, 100]),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=[
                    {"month": "Jan", "sla_rate": 72, "target": 85},
                    {"month": "Feb", "sla_rate": 74, "target": 85},
                    {"month": "Mär", "sla_rate": 76, "target": 85},
                    {"month": "Apr", "sla_rate": 75, "target": 85},
                    {"month": "Mai", "sla_rate": 78, "target": 85},
                    {"month": "Jun", "sla_rate": 79, "target": 85},
                    {"month": "Jul", "sla_rate": 77, "target": 85},
                    {"month": "Aug", "sla_rate": 80, "target": 85},
                    {"month": "Sep", "sla_rate": 78, "target": 85},
                    {"month": "Okt", "sla_rate": 81, "target": 85},
                    {"month": "Nov", "sla_rate": 78, "target": 85},
                    {"month": "Dez", "sla_rate": 78.3, "target": 85},
                ],
                height=280,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Workflow compliance breakdown
        section_card(
            "🔍 Workflow-Analyse",
            rx.cond(
                AppState.workflow_analysis.length() > 0,
                rx.callout.root(
                    rx.callout.icon(rx.icon("check")),
                    rx.callout.text(
                        rx.hstack(
                            rx.text("Workflow-Daten geladen: "),
                            rx.badge(AppState.workflow_analysis.length().to_string() + " Einträge", color_scheme="green"),
                        )
                    ),
                    color_scheme="green",
                ),
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="compliant", fill="#10b981", name="Konform"),
                    rx.recharts.bar(data_key="violation", fill="#ef4444", name="Verletzung"),
                    rx.recharts.x_axis(data_key="step"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(),
                    data=[
                        {"step": "Triage", "compliant": 92, "violation": 8},
                        {"step": "Assignment", "compliant": 88, "violation": 12},
                        {"step": "1st Response", "compliant": 79, "violation": 21},
                        {"step": "Resolution", "compliant": 78, "violation": 22},
                        {"step": "Closure", "compliant": 95, "violation": 5},
                        {"step": "Post-Review", "compliant": 65, "violation": 35},
                    ],
                    height=280,
                    width="100%",
                ),
            ),
        ),

        rx.box(height="1.5em"),

        # Reopen analysis
        section_card(
            "🔁 Reopen-Rate Analyse",
            rx.hstack(
                rx.vstack(
                    rx.text("Gesamt Reopen-Rate", color="#64748b", font_size="0.85em"),
                    rx.text("8.7%", font_size="2.5em", font_weight="700", color="#f59e0b"),
                    rx.text("Ziel: < 5%", color="#ef4444", font_size="0.85em"),
                    spacing="1",
                    align_items="center",
                    background_color="#fffbeb",
                    padding="1.5em",
                    border_radius="0.75em",
                    min_width="180px",
                ),
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="reopen_rate", fill="#f59e0b"),
                    rx.recharts.x_axis(data_key="priority"),
                    rx.recharts.y_axis(unit="%"),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    data=[
                        {"priority": "Blocker", "reopen_rate": 14.2},
                        {"priority": "High", "reopen_rate": 10.8},
                        {"priority": "Medium", "reopen_rate": 7.9},
                        {"priority": "Low", "reopen_rate": 5.1},
                        {"priority": "Minimal", "reopen_rate": 2.3},
                    ],
                    height=250,
                    width="100%",
                ),
                spacing="4",
                align_items="center",
                width="100%",
            ),
        ),
    )
