import reflex as rx

config = rx.Config(
    app_name="helpdesk",
    frontend_port=3000,
    backend_port=8000,
    env=rx.Env.PROD,
    telemetry_enabled=False,
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
