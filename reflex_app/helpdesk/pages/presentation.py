"""Präsentation Page"""
import reflex as rx
from helpdesk.state import AppState
from helpdesk.pages.layout import page_layout, section_card, page_header, metric_card


def presentation_page() -> rx.Component:
    return page_layout(
        page_header(
            "🎬 Präsentation",
            "Executive Summary – HelpDesk Performance Monitor",
        ),

        # Hero section
        rx.box(
            rx.vstack(
                rx.text("🎯 HelpDesk Performance Monitor", font_size="2em", font_weight="700", color="white", text_align="center"),
                rx.text("KI-gestützte Mitarbeiter-Performance-Analyse", font_size="1.1em", color="#bfdbfe", text_align="center"),
                rx.text("Datengetrieben · Objektiv · Handlungsorientiert", color="#93c5fd", text_align="center"),
                spacing="2",
                align_items="center",
                padding="2em",
            ),
            background="linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 50%, #4c1d95 100%)",
            border_radius="1em",
            width="100%",
            margin_bottom="1.5em",
        ),

        # Problem statement
        section_card(
            "🔴 Problem",
            rx.grid(
                rx.box(
                    rx.text("Subjektive Bewertungen", font_weight="600", color="#ef4444"),
                    rx.text(
                        "Manager-Bewertungen zeigen starken Halo-Effekt (r=0.921) "
                        "und Leniency-Bias. Performance-Einschätzungen sind nicht verlässlich.",
                        font_size="0.9em",
                        margin_top="0.5em",
                    ),
                    background_color="#fef2f2",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="4px solid #ef4444",
                ),
                rx.box(
                    rx.text("Keine Objektiven Metriken", font_weight="600", color="#f59e0b"),
                    rx.text(
                        "Ohne datenbasierte Grundlage ist es unmöglich, Training-Defizite "
                        "zu identifizieren oder faire Leistungsbeurteilungen zu erstellen.",
                        font_size="0.9em",
                        margin_top="0.5em",
                    ),
                    background_color="#fffbeb",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="4px solid #f59e0b",
                ),
                rx.box(
                    rx.text("Reaktives Management", font_weight="600", color="#8b5cf6"),
                    rx.text(
                        "Probleme werden erst erkannt wenn Tickets eskalieren. "
                        "Frühindikatoren fehlen, präventive Maßnahmen sind nicht möglich.",
                        font_size="0.9em",
                        margin_top="0.5em",
                    ),
                    background_color="#f5f3ff",
                    padding="1em",
                    border_radius="0.5em",
                    border_left="4px solid #8b5cf6",
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Solution
        section_card(
            "✅ Lösung: KI-gestützte Performance-Analyse",
            rx.vstack(
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="improvement", fill="#10b981", name="Verbesserung %"),
                    rx.recharts.x_axis(data_key="metric"),
                    rx.recharts.y_axis(unit="%"),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    data=[
                        {"metric": "Objektivität", "improvement": 78},
                        {"metric": "Früherkennung", "improvement": 65},
                        {"metric": "Training-Effizienz", "improvement": 42},
                        {"metric": "SLA-Compliance", "improvement": 18},
                        {"metric": "Mitarbeiter-Zufriedenheit", "improvement": 31},
                    ],
                    height=250,
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Key results
        section_card(
            "🏆 Kernergebnisse",
            rx.grid(
                rx.box(
                    rx.text("77.8%", font_size="2.5em", font_weight="700", color="#3b82f6", text_align="center"),
                    rx.text("ML-Modell Accuracy", color="#64748b", font_size="0.9em", text_align="center"),
                    rx.text("Q1-Score Vorhersage", color="#94a3b8", font_size="0.8em", text_align="center"),
                    background_color="#eff6ff",
                    padding="1.5em",
                    border_radius="0.75em",
                    text_align="center",
                ),
                rx.box(
                    rx.text("66k+", font_size="2.5em", font_weight="700", color="#10b981", text_align="center"),
                    rx.text("Analysierte Tickets", color="#64748b", font_size="0.9em", text_align="center"),
                    rx.text("Mit NLP-Features", color="#94a3b8", font_size="0.8em", text_align="center"),
                    background_color="#f0fdf4",
                    padding="1.5em",
                    border_radius="0.75em",
                    text_align="center",
                ),
                rx.box(
                    rx.text("1348", font_size="2.5em", font_weight="700", color="#8b5cf6", text_align="center"),
                    rx.text("Ground-Truth Samples", color="#64748b", font_size="0.9em", text_align="center"),
                    rx.text("Manager-bewertet", color="#94a3b8", font_size="0.8em", text_align="center"),
                    background_color="#f5f3ff",
                    padding="1.5em",
                    border_radius="0.75em",
                    text_align="center",
                ),
                rx.box(
                    rx.text("15", font_size="2.5em", font_weight="700", color="#f59e0b", text_align="center"),
                    rx.text("Dashboard-Seiten", color="#64748b", font_size="0.9em", text_align="center"),
                    rx.text("Vollständige Analyse", color="#94a3b8", font_size="0.8em", text_align="center"),
                    background_color="#fffbeb",
                    padding="1.5em",
                    border_radius="0.75em",
                    text_align="center",
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
        ),

        rx.box(height="1.5em"),

        # Next steps
        section_card(
            "🚀 Nächste Schritte",
            rx.vstack(
                rx.hstack(
                    rx.badge("Q1 2024", color_scheme="blue"),
                    rx.text("Integration in HR-System und automatische Alert-Generierung", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("Q2 2024", color_scheme="purple"),
                    rx.text("Erweiterung auf alle Support-Teams (100+ Mitarbeiter)", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("Q3 2024", color_scheme="green"),
                    rx.text("Echtzeit-Scoring mit LLM-basierter Dialog-Analyse", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge("Q4 2024", color_scheme="orange"),
                    rx.text("Predictive Analytics: Burn-Out und Fluktuations-Prognose", font_size="0.9em"),
                    spacing="2",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
        ),
    )
