"""
Data Loader - Loads the helpdesk datasets
"""

import pandas as pd
from pathlib import Path


def load_all_data(data_dir="data/raw"):
    """
    Load all 5 datasets.

    Returns:
        dict: Dictionary with all DataFrames
    """
    data_path = Path(data_dir)

    datasets = {}

    # 1. Issues (main dataset)
    if (data_path / "issues.csv").exists():
        datasets['issues'] = pd.read_csv(data_path / "issues.csv")
        print(f" Issues: {len(datasets['issues']):,} rows")

    # 2. Issues Snapshots
    if (data_path / "issues_snapshot.csv").exists():
        datasets['snapshots'] = pd.read_csv(data_path / "issues_snapshot.csv")
        print(f" Snapshots: {len(datasets['snapshots']):,} rows")

    # 3. Change History
    if (data_path / "issues_change_history.csv").exists():
        datasets['history'] = pd.read_csv(data_path / "issues_change_history.csv")
        print(f" History: {len(datasets['history']):,} rows")

    # 4. Rated Samples (Ground Truth)
    if (data_path / "issues_snapshot_sample.xlsx").exists():
        datasets['scored'] = pd.read_excel(data_path / "issues_snapshot_sample.xlsx")
        print(f" Scored: {len(datasets['scored']):,} rows")

    # 5. Utterances (Comments)
    if (data_path / "sample_utterances.csv").exists():
        datasets['utterances'] = pd.read_csv(data_path / "sample_utterances.csv")
        print(f" Utterances: {len(datasets['utterances']):,} rows")

    return datasets


def get_data_summary(datasets):
    """Return an overview of the loaded data."""
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
    print(" LOADING DATA")
    print("="*50)

    data = load_all_data()

    print("\n Summary:")
    for name, info in get_data_summary(data).items():
        print(f"  {name}: {info['rows']:,} rows, {info['columns']} columns")
