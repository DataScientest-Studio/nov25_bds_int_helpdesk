"""
Sidebar Navigation Component
"""
import reflex as rx
from helpdesk.state import AppState


NAV_ITEMS = [
    ("dashboard",           "🏠", "Dashboard"),
    ("data_inventory",      "📊", "Daten-Inventar"),
    ("ticket_monitor",      "🎫", "Ticket Monitor"),
    ("employee_performance","👥", "Mitarbeiter Performance"),
    ("training",            "🏋️", "Training & Defizite"),
    ("objectivity",         "🔍", "Objektivitätsprüfung"),
    ("nlp",                 "💬", "Kommunikation NLP"),
    ("compliance",          "🔄", "Prozess Compliance"),
    ("ml_model",            "🎯", "ML Modell Details"),
    ("trends",              "📈", "Trend Analyse"),
    ("export",              "📥", "Export Center"),
    ("dialog",              "💬", "Dialog Analyse"),
    ("score_compare",       "🔬", "Score Vergleich"),
    ("presentation",        "🎬", "Präsentation"),
    ("settings",            "⚙️", "Einstellungen"),
]


def nav_item(page_id: str, icon: str, label: str) -> rx.Component:
    """Single navigation item."""
    is_active = AppState.current_page == page_id
    return rx.box(
        rx.hstack(
            rx.text(icon, font_size="1.1em"),
            rx.text(label, font_size="0.9em", font_weight=rx.cond(is_active, "700", "400")),
            spacing="2",
            align="center",
        ),
        padding_x="1em",
        padding_y="0.5em",
        border_radius="0.4em",
        cursor="pointer",
        background_color=rx.cond(is_active, "#3b82f6", "transparent"),
        color=rx.cond(is_active, "white", "#e2e8f0"),
        _hover={"background_color": rx.cond(is_active, "#2563eb", "#374151")},
        on_click=AppState.set_page(page_id),
        width="100%",
    )


def sidebar() -> rx.Component:
    """Full sidebar with navigation."""
    return rx.box(
        # Header
        rx.vstack(
            rx.hstack(
                rx.text("🎯", font_size="1.5em"),
                rx.vstack(
                    rx.text("HelpDesk Monitor", font_weight="700", color="white", font_size="1em"),
                    rx.text("Performance Analytics", color="#94a3b8", font_size="0.75em"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="2",
                align="center",
            ),
            rx.divider(border_color="#374151"),
            # Navigation items
            *[nav_item(page_id, icon, label) for page_id, icon, label in NAV_ITEMS],
            rx.divider(border_color="#374151"),
            # Status info
            rx.box(
                rx.text("Projekt: HelpDesk Monitor", color="#94a3b8", font_size="0.75em"),
                rx.text("Status: Production Ready ✅", color="#10b981", font_size="0.75em"),
                padding_x="1em",
            ),
            spacing="1",
            align_items="stretch",
            width="100%",
        ),
        background_color="#1e293b",
        min_height="100vh",
        width="260px",
        padding_y="1em",
        position="fixed",
        left="0",
        top="0",
        overflow_y="auto",
        z_index="100",
    )
