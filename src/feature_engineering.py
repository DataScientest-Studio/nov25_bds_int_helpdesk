"""
Feature Engineering - Erstellt Features für das ML-Modell
"""

import pandas as pd
import numpy as np
from pathlib import Path


def create_time_features(df):
    """Erstellt zeitbasierte Features."""
    result = df.copy()
    
    # Workflow-Zeit-Ratios
    if 'wf_total_time' in df.columns:
        total_time = df['wf_total_time'].replace(0, np.nan)
        result['total_hours'] = df['wf_total_time'] / 3600
        result['total_days'] = df['wf_total_time'] / 86400
    
    # Spent hours (falls vorhanden)
    if 'spent hours' in df.columns:
        result['spent_hours'] = df['spent hours']
    
    return result


def create_process_features(df):
    """Erstellt Prozess-bezogene Features."""
    result = df.copy()
    
    # Statuswechsel zählen (wfe_ Spalten)
    wfe_cols = [col for col in df.columns if col.startswith('wfe_')]
    if wfe_cols:
        result['total_status_changes'] = df[wfe_cols].sum(axis=1)
    
    # Processing Steps
    if 'processing_steps' in df.columns:
        median_steps = df['processing_steps'].median()
        result['is_complex'] = (df['processing_steps'] > median_steps).astype(int)
    
    return result


def create_communication_features(df):
    """Erstellt Kommunikations-Features."""
    result = df.copy()
    
    # Kommentare zählen
    if 'issue_comments_count' in df.columns:
        result['comments_count'] = df['issue_comments_count']
    elif 'comments count' in df.columns:
        result['comments_count'] = df['comments count']
    
    return result


def create_priority_features(df):
    """Erstellt Priority-Features."""
    result = df.copy()
    
    # Finde Priority-Spalte
    priority_col = 'issue_priority' if 'issue_priority' in df.columns else 'priority'
    
    if priority_col in df.columns:
        # Priority als Zahl (höher = dringender)
        priority_map = {
            'Critical': 4, 'Kritisch': 4,
            'High': 3, 'Hoch': 3,
            'Medium': 2, 'Mittel': 2,
            'Low': 1, 'Niedrig': 1
        }
        result['priority_numeric'] = df[priority_col].map(priority_map).fillna(2)
    
    return result


def prepare_ml_dataset(scored_df):
    """
    Bereitet den ML-Datensatz vor.
    
    Args:
        scored_df: DataFrame mit bewerteten Samples
    
    Returns:
        X: Features
        y: Targets (Q1, Q2, Q3)
        feature_names: Liste der Feature-Namen
    """
    print("🔧 Erstelle ML-Datensatz...")
    
    # Kopie erstellen
    df = scored_df.copy()
    
    # Features anwenden
    df = create_time_features(df)
    df = create_process_features(df)
    df = create_communication_features(df)
    df = create_priority_features(df)
    
    # Target-Variablen
    target_cols = ['Q1', 'Q2', 'Q3']
    
    # Spalten die wir NICHT als Features nutzen
    exclude_cols = [
        'id', 'no', 'project', 'reporter', 'assignee',
        'started', 'ended', 'Notes', 'valid',
        'issue_proj', 'issue_reporter', 'issue_assignee',
        'issue_created', 'issue_resolution_date', 'last_change_date',
        'type', 'issue_type', 'issue_priority', 'priority'
    ] + target_cols
    
    # Nur numerische Spalten als Features
    feature_cols = []
    for col in df.columns:
        if col not in exclude_cols:
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32', 'bool']:
                feature_cols.append(col)
    
    # Filtere gültige Samples (Score > 0)
    valid_mask = (df['Q1'] > 0) & (df['Q2'] > 0) & (df['Q3'] > 0)
    df_valid = df[valid_mask].copy()
    
    print(f"   Gültige Samples: {len(df_valid)}")
    print(f"   Features: {len(feature_cols)}")
    
    X = df_valid[feature_cols].copy()
    y = df_valid[target_cols].copy()
    
    # Fehlende Werte mit Median ersetzen
    X = X.fillna(X.median())
    
    return X, y, feature_cols


def save_ml_dataset(X, y, feature_cols, output_dir="data/processed"):
    """Speichert den ML-Datensatz."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Kombiniere X und y
    combined = pd.concat([X.reset_index(drop=True), y.reset_index(drop=True)], axis=1)
    combined.to_csv(output_path / "ml_dataset.csv", index=False)
    
    # Feature-Liste speichern
    with open(output_path / "feature_columns.txt", 'w') as f:
        for col in feature_cols:
            f.write(f"{col}\n")
    
    print(f"💾 Gespeichert: {output_path}")


if __name__ == "__main__":
    print("="*50)
    print("🔧 FEATURE ENGINEERING")
    print("="*50)
    
    # Daten laden
    data_path = Path("data/raw/issues_snapshot_sample.xlsx")
    if data_path.exists():
        scored_df = pd.read_excel(data_path)
        print(f"📁 Geladen: {len(scored_df)} bewertete Samples")
        
        # Features erstellen
        X, y, features = prepare_ml_dataset(scored_df)
        
        # Speichern
        save_ml_dataset(X, y, features)
        
        print("\n✅ Feature Engineering abgeschlossen!")
    else:
        print("❌ Datei nicht gefunden!")
