"""
Data Loader - Lädt die Helpdesk-Datensätze
"""

import pandas as pd
from pathlib import Path


def load_all_data(data_dir="data/raw"):
    """
    Lädt alle 5 Datensätze.
    
    Returns:
        dict: Dictionary mit allen DataFrames
    """
    data_path = Path(data_dir)
    
    datasets = {}
    
    # 1. Issues (Hauptdatensatz)
    if (data_path / "issues.csv").exists():
        datasets['issues'] = pd.read_csv(data_path / "issues.csv")
        print(f"✅ Issues: {len(datasets['issues']):,} Zeilen")
    
    # 2. Issues Snapshots
    if (data_path / "issues_snapshot.csv").exists():
        datasets['snapshots'] = pd.read_csv(data_path / "issues_snapshot.csv")
        print(f"✅ Snapshots: {len(datasets['snapshots']):,} Zeilen")
    
    # 3. Change History
    if (data_path / "issues_change_history.csv").exists():
        datasets['history'] = pd.read_csv(data_path / "issues_change_history.csv")
        print(f"✅ History: {len(datasets['history']):,} Zeilen")
    
    # 4. Bewertete Samples (Ground Truth)
    if (data_path / "issues_snapshot_sample.xlsx").exists():
        datasets['scored'] = pd.read_excel(data_path / "issues_snapshot_sample.xlsx")
        print(f"✅ Scored: {len(datasets['scored']):,} Zeilen")
    
    # 5. Utterances (Kommentare)
    if (data_path / "sample_utterances.csv").exists():
        datasets['utterances'] = pd.read_csv(data_path / "sample_utterances.csv")
        print(f"✅ Utterances: {len(datasets['utterances']):,} Zeilen")
    
    return datasets


def get_data_summary(datasets):
    """Gibt eine Übersicht der geladenen Daten."""
    summary = {}
    for name, df in datasets.items():
        summary[name] = {
            'rows': len(df),
            'columns': len(df.columns),
            'columns_list': df.columns.tolist()
        }
    return summary


if __name__ == "__main__":
    print("="*50)
    print("📁 DATEN LADEN")
    print("="*50)
    
    data = load_all_data()
    
    print("\n📊 Zusammenfassung:")
    for name, info in get_data_summary(data).items():
        print(f"  {name}: {info['rows']:,} Zeilen, {info['columns']} Spalten")
