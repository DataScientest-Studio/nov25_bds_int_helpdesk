"""
Base layout for all pages - wraps content with sidebar.
"""
import reflex as rx
from helpdesk.components.sidebar import sidebar
from helpdesk.state import AppState


def page_layout(*children) -> rx.Component:
    """Main layout with sidebar and content area."""
    return rx.hstack(
        sidebar(),
        rx.box(
            *children,
            padding="2em",
            margin_left="260px",
            width="calc(100vw - 260px)",
            min_height="100vh",
            background_color=rx.cond(AppState.dark_mode, "#0f172a", "#f8fafc"),
            color=rx.cond(AppState.dark_mode, "#e2e8f0", "#1e293b"),
        ),
        spacing="0",
        align_items="start",
        width="100%",
    )


def metric_card(label: str, value: str, delta: str = "", color: str = "#3b82f6") -> rx.Component:
    """KPI metric card."""
    return rx.box(
        rx.vstack(
            rx.text(label, color="#64748b", font_size="0.85em", font_weight="500"),
            rx.text(value, font_size="1.8em", font_weight="700", color=color),
            rx.cond(
                delta != "",
                rx.text(delta, color="#10b981", font_size="0.8em"),
                rx.fragment(),
            ),
            spacing="1",
            align_items="start",
        ),
        background_color="white",
        border="1px solid #e2e8f0",
        border_radius="0.75em",
        padding="1.2em",
        box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        flex="1",
        min_width="160px",
    )


def section_card(title: str, *children) -> rx.Component:
    """Section container card."""
    return rx.box(
        rx.vstack(
            rx.text(title, font_size="1.1em", font_weight="600", color="#1e293b"),
            rx.divider(border_color="#e2e8f0"),
            *children,
            spacing="3",
            align_items="stretch",
            width="100%",
        ),
        background_color="white",
        border="1px solid #e2e8f0",
        border_radius="0.75em",
        padding="1.5em",
        box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        width="100%",
    )


def page_header(title: str, subtitle: str = "") -> rx.Component:
    """Page header with title."""
    return rx.vstack(
        rx.text(title, font_size="1.8em", font_weight="700", color="#1e293b"),
        rx.cond(
            subtitle != "",
            rx.text(subtitle, color="#64748b", font_size="0.95em"),
            rx.fragment(),
        ),
        rx.divider(border_color="#e2e8f0"),
        spacing="2",
        align_items="start",
        width="100%",
        margin_bottom="1em",
    )
