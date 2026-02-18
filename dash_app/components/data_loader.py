"""
Data Loader - Shared data loading functions for all pages.
"""
import pandas as pd
import sqlite3
from pathlib import Path
import joblib

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DB_PATH = DATA_DIR / "helpdesk.db"

# ---- Raw data ----

def load_issues():
    path = DATA_DIR / "raw" / "issues.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_snapshots():
    path = DATA_DIR / "raw" / "issues_snapshot.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_scored():
    path = DATA_DIR / "raw" / "issues_snapshot_sample.xlsx"
    if path.exists():
        df = pd.read_excel(path)
        return df[df['Q1'] > 0] if 'Q1' in df.columns else df
    return pd.DataFrame()


def load_utterances():
    path = DATA_DIR / "raw" / "sample_utterances.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

# ---- Processed data ----

def load_ml_dataset():
    path = DATA_DIR / "processed" / "ml_dataset.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_nlp_features():
    path = DATA_DIR / "processed" / "nlp_features.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_employee_metrics():
    path = DATA_DIR / "processed" / "employee_metrics_raw.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_workflow_analysis():
    path = DATA_DIR / "processed" / "workflow_analysis.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_dialog_acts():
    path = DATA_DIR / "processed" / "dialog_acts.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_o_score_results():
    path = DATA_DIR / "processed" / "o_score_results.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_q_vs_o_comparison():
    path = DATA_DIR / "processed" / "q_vs_o_score_comparison.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_training_report():
    path = PROJECT_ROOT / "reports" / "training_report.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

# ---- Models ----

def load_model(name: str):
    path = MODELS_DIR / name
    if path.exists():
        try:
            return joblib.load(path)
        except Exception:
            return None
    return None

# ---- DB ----

def get_db_connection():
    if DB_PATH.exists():
        return sqlite3.connect(DB_PATH)
    return None


def load_db_tickets(limit=500):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM issues LIMIT ?", conn, params=(limit,))
        conn.close()
        return df
    except Exception:
        conn.close()
        return pd.DataFrame()


def list_db_tables():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return tables
    except Exception:
        return []
