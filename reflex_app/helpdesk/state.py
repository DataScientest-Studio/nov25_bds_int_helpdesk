"""
Global State for HelpDesk Performance Monitor
Manages data loading, navigation, and settings.
"""
import reflex as rx
import pandas as pd
import sqlite3
import joblib
import json
from pathlib import Path
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DB_PATH = DATA_DIR / "helpdesk.db"


# ── Helper functions (run at module level / in event handlers) ─────────────
def _load_csv_safe(path: Path) -> pd.DataFrame:
    """Load CSV safely, returning empty DF on error."""
    try:
        if path.exists():
            return pd.read_csv(path)
    except Exception:
        pass
    return pd.DataFrame()


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of dicts (JSON-serialisable)."""
    if df.empty:
        return []
    # Replace NaN with None for JSON compatibility
    return json.loads(df.where(pd.notnull(df), None).to_json(orient="records"))


def _load_db_table(query: str) -> pd.DataFrame:
    """Load data from SQLite DB."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ── Main App State ─────────────────────────────────────────────────────────
class AppState(rx.State):
    """Application-wide state."""

    # Navigation
    current_page: str = "dashboard"

    # Settings
    language: str = "de"
    show_help: bool = True
    show_emojis: bool = True
    dark_mode: bool = False
    sidebar_open: bool = True

    # Loading indicators
    is_loading: bool = False
    load_error: str = ""

    # ── KPI Data (serialisable) ────────────────────────────────────────────
    kpi_total_tickets: int = 0
    kpi_open_tickets: int = 0
    kpi_resolved_today: int = 0
    kpi_critical: int = 0
    kpi_employees: int = 0
    kpi_risk_red: int = 0
    kpi_avg_score: float = 0.0
    kpi_scored_samples: int = 0

    # ── Table Data (as JSON-serialisable list of dicts) ────────────────────
    recent_tickets: list[dict] = []
    status_distribution: list[dict] = []
    priority_distribution: list[dict] = []
    employee_list: list[dict] = []
    ml_dataset_preview: list[dict] = []
    nlp_features: list[dict] = []
    dialog_acts: list[dict] = []
    workflow_analysis: list[dict] = []
    score_comparison: list[dict] = []
    o_score_results: list[dict] = []
    training_gaps: list[dict] = []
    alerts: list[dict] = []
    trend_data: list[dict] = []

    # ── Model Data ────────────────────────────────────────────────────────
    model_loaded: bool = False
    model_type: str = ""
    model_metrics: dict = {}
    feature_importance: list[dict] = []

    # ── Filter State ─────────────────────────────────────────────────────
    ticket_filter_status: str = "Alle"
    ticket_filter_priority: str = "Alle"
    ticket_search: str = ""
    employee_filter: str = ""
    trend_period: str = "30d"

    # ── Export State ─────────────────────────────────────────────────────
    export_format: str = "CSV"
    export_dataset: str = "Tickets"
    export_message: str = ""

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def set_page(self, page: str):
        self.current_page = page

    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    def set_language(self, lang: str):
        self.language = lang

    def toggle_help(self):
        self.show_help = not self.show_help

    def toggle_emojis(self):
        self.show_emojis = not self.show_emojis

    def set_ticket_filter_status(self, val: str):
        self.ticket_filter_status = val

    def set_ticket_filter_priority(self, val: str):
        self.ticket_filter_priority = val

    def set_ticket_search(self, val: str):
        self.ticket_search = val

    def set_employee_filter(self, val: str):
        self.employee_filter = val

    def set_trend_period(self, val: str):
        self.trend_period = val

    def set_export_format(self, val: str):
        self.export_format = val

    def set_export_dataset(self, val: str):
        self.export_dataset = val

    def on_load(self):
        """Load all data when app starts."""
        self._load_kpis()
        self._load_tickets()
        self._load_employees()
        self._load_ml_model()
        self._load_processed_data()

    def refresh_data(self):
        """Refresh all data."""
        self.on_load()

    # ── Private data loaders ─────────────────────────────────────────────

    def _load_kpis(self):
        """Load KPI data."""
        # From DB (if exists)
        total = _load_db_table("SELECT COUNT(*) as c FROM tickets")
        self.kpi_total_tickets = int(total.iloc[0]["c"]) if not total.empty else 0

        if self.kpi_total_tickets == 0:
            # Fall back to CSV
            issues = _load_csv_safe(DATA_DIR / "raw" / "issues.csv")
            self.kpi_total_tickets = len(issues)

        open_t = _load_db_table(
            "SELECT COUNT(*) as c FROM tickets WHERE status IN ('Open','In Progress','Waiting','In Review')"
        )
        self.kpi_open_tickets = int(open_t.iloc[0]["c"]) if not open_t.empty else 0

        resolved = _load_db_table(
            "SELECT COUNT(*) as c FROM tickets WHERE DATE(resolved_at)=DATE('now')"
        )
        self.kpi_resolved_today = int(resolved.iloc[0]["c"]) if not resolved.empty else 0

        critical = _load_db_table(
            "SELECT COUNT(*) as c FROM tickets WHERE priority=1 AND status NOT IN ('Closed','Resolved')"
        )
        self.kpi_critical = int(critical.iloc[0]["c"]) if not critical.empty else 0

        emp = _load_db_table("SELECT COUNT(*) as c FROM employees")
        self.kpi_employees = int(emp.iloc[0]["c"]) if not emp.empty else 0

        red = _load_db_table("SELECT COUNT(*) as c FROM employees WHERE risk_level='RED'")
        self.kpi_risk_red = int(red.iloc[0]["c"]) if not red.empty else 0

        # Scores from processed data
        scored = _load_csv_safe(DATA_DIR / "raw" / "issues_snapshot_sample.xlsx")
        if scored.empty:
            # try XLSX via different method
            try:
                xlsx_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
                if xlsx_path.exists():
                    scored = pd.read_excel(xlsx_path)
            except Exception:
                pass
        if "Q1" in scored.columns:
            valid = scored[scored["Q1"] > 0]["Q1"]
            self.kpi_avg_score = round(float(valid.mean()), 2) if len(valid) > 0 else 0.0
            self.kpi_scored_samples = len(scored)

    def _load_tickets(self):
        """Load ticket tables - ensure consistent column names."""
        recent = _load_db_table(
            "SELECT ticket_num, title, status, priority, assignee, created_at FROM tickets ORDER BY created_at DESC LIMIT 20"
        )
        if recent.empty:
            snap = _load_csv_safe(DATA_DIR / "raw" / "issues_snapshot.csv")
            if not snap.empty:
                # Normalize column names to match expected structure
                rename_map = {"key": "ticket_num", "summary": "title", "created": "created_at"}
                snap = snap.rename(columns=rename_map)
                cols = [c for c in ["ticket_num", "title", "status", "priority", "assignee", "created_at"]
                        if c in snap.columns]
                recent = snap[cols].head(20)
        # Ensure all required columns exist
        for col in ["ticket_num", "title", "status", "priority", "assignee", "created_at"]:
            if col not in recent.columns:
                recent[col] = "–"
        # Normalize priority and status to strings
        recent["priority"] = recent["priority"].astype(str)
        recent["status"] = recent["status"].astype(str)
        recent["ticket_num"] = recent["ticket_num"].astype(str)
        recent["title"] = recent["title"].astype(str)
        recent["assignee"] = recent["assignee"].astype(str)
        recent["created_at"] = recent["created_at"].astype(str)
        self.recent_tickets = _df_to_records(recent)

        status_dist = _load_db_table("SELECT status, COUNT(*) as count FROM tickets GROUP BY status")
        if status_dist.empty:
            snap = _load_csv_safe(DATA_DIR / "raw" / "issues_snapshot.csv")
            if "status" in snap.columns:
                status_dist = snap["status"].value_counts().reset_index()
                status_dist.columns = ["status", "count"]
        self.status_distribution = _df_to_records(status_dist)

        prio_dist = _load_db_table("SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority")
        if prio_dist.empty:
            snap = _load_csv_safe(DATA_DIR / "raw" / "issues_snapshot.csv")
            if "priority" in snap.columns:
                prio_dist = snap["priority"].value_counts().reset_index()
                prio_dist.columns = ["priority", "count"]
        self.priority_distribution = _df_to_records(prio_dist)

    def _load_employees(self):
        """Load employee data with consistent column names."""
        emp = _load_db_table("SELECT * FROM employees ORDER BY avg_score DESC LIMIT 50")
        if emp.empty:
            emp = _load_csv_safe(DATA_DIR / "processed" / "employee_metrics_raw.csv")
            if not emp.empty:
                emp = emp.head(50)
        if not emp.empty:
            # Ensure required columns exist with consistent names
            for col in ["employee", "ticket_count", "avg_time_hours", "reopen_rate",
                        "first_touch_rate", "resolution_success_rate", "risk_level", "avg_score"]:
                if col not in emp.columns:
                    emp[col] = "–"
            # Convert numeric columns to string for display
            for col in ["ticket_count", "avg_time_hours", "reopen_rate",
                        "first_touch_rate", "resolution_success_rate"]:
                if col in emp.columns:
                    try:
                        emp[col] = emp[col].apply(
                            lambda x: f"{float(x):.2f}" if x is not None and str(x) != "–" and str(x) != "nan" else "–"
                        )
                    except Exception:
                        emp[col] = emp[col].astype(str)
            emp["employee"] = emp["employee"].astype(str)
            emp["risk_level"] = emp.get("risk_level", "–").fillna("–").astype(str) if "risk_level" in emp.columns else "–"
        self.employee_list = _df_to_records(emp)

        # Training gaps
        try:
            xlsx_path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
            if xlsx_path.exists():
                scored = pd.read_excel(xlsx_path)
                if "assignee" in scored.columns and "Q1" in scored.columns:
                    valid = scored[scored["Q1"] > 0]
                    gaps = valid.groupby("assignee").agg(
                        q1_mean=("Q1", "mean"),
                        q2_mean=("Q2", "mean") if "Q2" in valid.columns else ("Q1", "mean"),
                        count=("Q1", "count")
                    ).reset_index()
                    gaps["training_needed"] = gaps["q1_mean"] < 3.0
                    self.training_gaps = _df_to_records(gaps.sort_values("q1_mean").head(20))
        except Exception:
            pass

    def _load_ml_model(self):
        """Load ML model metadata."""
        for model_file, mtype in [
            ("optimized_scorer.joblib", "optimized"),
            ("q_score_model.joblib", "q_score"),
            ("performance_scorer.joblib", "standard"),
        ]:
            path = MODELS_DIR / model_file
            if path.exists():
                try:
                    data = joblib.load(path)
                    self.model_loaded = True
                    self.model_type = mtype
                    metrics = data.get("metrics", {})
                    # Ensure serializable
                    self.model_metrics = {
                        k: {mk: float(mv) for mk, mv in v.items()} if isinstance(v, dict) else float(v)
                        for k, v in metrics.items()
                    }
                    # Feature importance
                    feat_imp = data.get("feature_importance", [])
                    if isinstance(feat_imp, list):
                        self.feature_importance = feat_imp[:20]
                    elif hasattr(feat_imp, "to_dict"):
                        self.feature_importance = _df_to_records(feat_imp.head(20))
                    break
                except Exception:
                    pass

    def _load_processed_data(self):
        """Load processed data files."""
        nlp = _load_csv_safe(DATA_DIR / "processed" / "nlp_features.csv")
        self.nlp_features = _df_to_records(nlp.head(200))

        dialog = _load_csv_safe(DATA_DIR / "processed" / "dialog_acts.csv")
        self.dialog_acts = _df_to_records(dialog.head(200))

        workflow = _load_csv_safe(DATA_DIR / "processed" / "workflow_analysis.csv")
        self.workflow_analysis = _df_to_records(workflow.head(200))

        score_comp = _load_csv_safe(DATA_DIR / "processed" / "q_vs_o_score_comparison.csv")
        self.score_comparison = _df_to_records(score_comp.head(200))

        o_score = _load_csv_safe(DATA_DIR / "processed" / "o_score_results.csv")
        self.o_score_results = _df_to_records(o_score.head(200))

        ml_ds = _load_csv_safe(DATA_DIR / "processed" / "ml_dataset.csv")
        self.ml_dataset_preview = _df_to_records(ml_ds.head(50))

        # Alerts from DB
        alerts = _load_db_table(
            "SELECT * FROM alerts WHERE acknowledged=0 ORDER BY created_at DESC LIMIT 10"
        )
        self.alerts = _df_to_records(alerts)

    def do_export(self):
        """Simulate data export."""
        self.export_message = f"Export von '{self.export_dataset}' als {self.export_format} wird vorbereitet..."
