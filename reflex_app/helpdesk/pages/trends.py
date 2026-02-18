"""Trend Analyse Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def trends_page() -> rx.Component:
    return page_layout(
        page_header(
            "📈 Trend Analyse",
            "Zeitreihenanalyse von Performance-Indikatoren",
        ),

        # Period selector
        section_card(
            "📅 Zeitraum",
            rx.hstack(
                rx.foreach(
                    ["7d", "30d", "90d", "180d", "1y"],
                    lambda period: rx.button(
                        period,
                        on_click=AppState.set_trend_period(period),
                        color_scheme=rx.cond(AppState.trend_period == period, "blue", "gray"),
                        variant=rx.cond(AppState.trend_period == period, "solid", "soft"),
                        size="2",
                    ),
                ),
                spacing="2",
            ),
        ),

        rx.box(height="1.5em"),

        # Ticket volume trend
        section_card(
            "📊 Ticket-Volumen Trend",
            rx.recharts.composed_chart(
                rx.recharts.area(data_key="tickets", stroke="#3b82f6", fill="#bfdbfe", name="Tickets"),
                rx.recharts.line(data_key="resolved", stroke="#10b981", name="Gelöst", dot=False),
                rx.recharts.x_axis(data_key="week"),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=[
                    {"week": "KW01", "tickets": 892, "resolved": 845},
                    {"week": "KW02", "tickets": 934, "resolved": 901},
                    {"week": "KW03", "tickets": 867, "resolved": 834},
                    {"week": "KW04", "tickets": 1023, "resolved": 978},
                    {"week": "KW05", "tickets": 956, "resolved": 921},
                    {"week": "KW06", "tickets": 1087, "resolved": 1043},
                    {"week": "KW07", "tickets": 978, "resolved": 955},
                    {"week": "KW08", "tickets": 1034, "resolved": 998},
                    {"week": "KW09", "tickets": 891, "resolved": 867},
                    {"week": "KW10", "tickets": 1123, "resolved": 1089},
                    {"week": "KW11", "tickets": 1067, "resolved": 1034},
                    {"week": "KW12", "tickets": 987, "resolved": 965},
                ],
                height=300,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Performance score trend
        section_card(
            "⭐ Performance-Score Trend",
            rx.recharts.line_chart(
                rx.recharts.line(data_key="q1_avg", stroke="#3b82f6", name="Q1 Ø", dot=True),
                rx.recharts.line(data_key="q2_avg", stroke="#8b5cf6", name="Q2 Ø", dot=True),
                rx.recharts.line(data_key="q3_avg", stroke="#10b981", name="Q3 Ø", dot=True),
                rx.recharts.reference_line(y="3.5", stroke="#ef4444", stroke_dasharray="5 5"),
                rx.recharts.x_axis(data_key="month"),
                rx.recharts.y_axis(domain=[1, 5]),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=[
                    {"month": "Jan", "q1_avg": 3.45, "q2_avg": 3.61, "q3_avg": 3.38},
                    {"month": "Feb", "q1_avg": 3.52, "q2_avg": 3.67, "q3_avg": 3.41},
                    {"month": "Mär", "q1_avg": 3.48, "q2_avg": 3.59, "q3_avg": 3.44},
                    {"month": "Apr", "q1_avg": 3.61, "q2_avg": 3.73, "q3_avg": 3.52},
                    {"month": "Mai", "q1_avg": 3.57, "q2_avg": 3.68, "q3_avg": 3.49},
                    {"month": "Jun", "q1_avg": 3.64, "q2_avg": 3.76, "q3_avg": 3.55},
                    {"month": "Jul", "q1_avg": 3.71, "q2_avg": 3.82, "q3_avg": 3.63},
                    {"month": "Aug", "q1_avg": 3.68, "q2_avg": 3.79, "q3_avg": 3.60},
                    {"month": "Sep", "q1_avg": 3.73, "q2_avg": 3.85, "q3_avg": 3.67},
                    {"month": "Okt", "q1_avg": 3.76, "q2_avg": 3.88, "q3_avg": 3.71},
                    {"month": "Nov", "q1_avg": 3.72, "q2_avg": 3.84, "q3_avg": 3.68},
                    {"month": "Dez", "q1_avg": 3.78, "q2_avg": 3.91, "q3_avg": 3.74},
                ],
                height=300,
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Resolution time trend
        section_card(
            "⏱️ Bearbeitungszeit-Trend (Stunden)",
            rx.recharts.area_chart(
                rx.recharts.area(data_key="avg_hours", stroke="#f59e0b", fill="#fef3c7", name="Ø Stunden", dot=False),
                rx.recharts.x_axis(data_key="month"),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                data=[
                    {"month": "Jan", "avg_hours": 28.4},
                    {"month": "Feb", "avg_hours": 26.1},
                    {"month": "Mär", "avg_hours": 27.8},
                    {"month": "Apr", "avg_hours": 24.3},
                    {"month": "Mai", "avg_hours": 25.6},
                    {"month": "Jun", "avg_hours": 23.1},
                    {"month": "Jul", "avg_hours": 22.8},
                    {"month": "Aug", "avg_hours": 24.5},
                    {"month": "Sep", "avg_hours": 21.9},
                    {"month": "Okt", "avg_hours": 20.7},
                    {"month": "Nov", "avg_hours": 22.3},
                    {"month": "Dez", "avg_hours": 21.1},
                ],
                height=250,
                width="100%",
            ),
        ),
    )
