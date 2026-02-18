"""
HelpDesk Performance Monitor - Main Reflex App
Single-page app with sidebar navigation and conditional page rendering.
"""
import reflex as rx
from helpdesk.state import AppState

# Import all page components
from helpdesk.pages.dashboard import dashboard_page
from helpdesk.pages.data_inventory import data_inventory_page
from helpdesk.pages.ticket_monitor import ticket_monitor_page
from helpdesk.pages.employee_performance import employee_performance_page
from helpdesk.pages.training import training_page
from helpdesk.pages.objectivity import objectivity_page
from helpdesk.pages.nlp import nlp_page
from helpdesk.pages.compliance import compliance_page
from helpdesk.pages.ml_model import ml_model_page
from helpdesk.pages.trends import trends_page
from helpdesk.pages.export import export_page
from helpdesk.pages.dialog import dialog_page
from helpdesk.pages.score_compare import score_compare_page
from helpdesk.pages.presentation import presentation_page
from helpdesk.pages.settings_page import settings_page
from helpdesk.components.sidebar import sidebar


NAV_ITEMS = [
    ("dashboard",            "🏠", "Dashboard"),
    ("data_inventory",       "📊", "Daten-Inventar"),
    ("ticket_monitor",       "🎫", "Ticket Monitor"),
    ("employee_performance", "👥", "Mitarbeiter Performance"),
    ("training",             "🏋️", "Training & Defizite"),
    ("objectivity",          "🔍", "Objektivitätsprüfung"),
    ("nlp",                  "💬", "Kommunikation NLP"),
    ("compliance",           "🔄", "Prozess Compliance"),
    ("ml_model",             "🎯", "ML Modell Details"),
    ("trends",               "📈", "Trend Analyse"),
    ("export",               "📥", "Export Center"),
    ("dialog",               "💬", "Dialog Analyse"),
    ("score_compare",        "🔬", "Score Vergleich"),
    ("presentation",         "🎬", "Präsentation"),
    ("settings",             "⚙️", "Einstellungen"),
]


def nav_item(page_id: str, icon: str, label: str) -> rx.Component:
    """Single nav item in sidebar."""
    is_active = AppState.current_page == page_id
    return rx.box(
        rx.hstack(
            rx.text(icon, font_size="1.1em"),
            rx.text(
                label,
                font_size="0.88em",
                font_weight=rx.cond(is_active, "700", "400"),
            ),
            spacing="2",
            align="center",
        ),
        padding_x="1em",
        padding_y="0.45em",
        border_radius="0.4em",
        cursor="pointer",
        background_color=rx.cond(is_active, "#3b82f6", "transparent"),
        color=rx.cond(is_active, "white", "#cbd5e1"),
        _hover={"background_color": rx.cond(is_active, "#2563eb", "#334155")},
        on_click=AppState.set_page(page_id),
        width="100%",
        transition="all 0.15s ease",
    )


def build_sidebar() -> rx.Component:
    """Build the navigation sidebar."""
    return rx.box(
        rx.vstack(
            # Logo + Title
            rx.hstack(
                rx.text("🎯", font_size="1.6em"),
                rx.vstack(
                    rx.text(
                        "HelpDesk Monitor",
                        font_weight="700",
                        color="white",
                        font_size="0.95em",
                    ),
                    rx.text(
                        "Performance Analytics",
                        color="#64748b",
                        font_size="0.72em",
                    ),
                    spacing="0",
                    align_items="start",
                ),
                spacing="2",
                align="center",
                padding_x="1em",
                padding_y="0.8em",
            ),
            rx.divider(border_color="#1e293b", margin_y="0.3em"),

            # Navigation
            *[nav_item(pid, icon, lbl) for pid, icon, lbl in NAV_ITEMS],

            rx.divider(border_color="#1e293b", margin_y="0.3em"),

            # Footer info
            rx.vstack(
                rx.text("Projekt: HelpDesk Analytics", color="#475569", font_size="0.72em"),
                rx.text("Version 4.0 · Reflex", color="#475569", font_size="0.72em"),
                rx.text("🟢 Production Ready", color="#10b981", font_size="0.72em"),
                spacing="0",
                padding_x="1em",
                align_items="start",
            ),
            spacing="0",
            align_items="stretch",
            width="100%",
            gap="0",
        ),
        background_color="#0f172a",
        min_height="100vh",
        width="255px",
        padding_y="0.5em",
        position="fixed",
        left="0",
        top="0",
        overflow_y="auto",
        z_index="100",
        border_right="1px solid #1e293b",
    )


def page_content() -> rx.Component:
    """Main content area that switches based on current_page."""
    return rx.match(
        AppState.current_page,
        ("dashboard",            dashboard_page()),
        ("data_inventory",       data_inventory_page()),
        ("ticket_monitor",       ticket_monitor_page()),
        ("employee_performance", employee_performance_page()),
        ("training",             training_page()),
        ("objectivity",          objectivity_page()),
        ("nlp",                  nlp_page()),
        ("compliance",           compliance_page()),
        ("ml_model",             ml_model_page()),
        ("trends",               trends_page()),
        ("export",               export_page()),
        ("dialog",               dialog_page()),
        ("score_compare",        score_compare_page()),
        ("presentation",         presentation_page()),
        ("settings",             settings_page()),
        dashboard_page(),  # default fallback
    )


def index() -> rx.Component:
    """Root page of the application."""
    return rx.box(
        build_sidebar(),
        rx.box(
            page_content(),
            margin_left="255px",
            min_height="100vh",
            background_color="#f1f5f9",
            padding="2em",
        ),
        font_family='"Inter", "Segoe UI", system-ui, sans-serif',
        width="100%",
        min_height="100vh",
    )


# ── App setup ──────────────────────────────────────────────────────────────
app = rx.App(
    style={
        "font_family": '"Inter", "Segoe UI", system-ui, sans-serif',
        "background_color": "#f1f5f9",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

app.add_page(
    index,
    route="/",
    on_load=AppState.on_load,
    title="HelpDesk Performance Monitor",
    description="KI-gestützte Mitarbeiter-Performance-Analyse",
)
