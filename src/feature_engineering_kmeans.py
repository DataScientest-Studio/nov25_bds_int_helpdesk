"""
Feature Engineering for Employee Performance Clustering
Generates per-assignee features from issues_snapshot.csv and issues_change_history.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Feature Engineering Pipeline")
print("=" * 60)

# ─── Load Data ─────────────────────────────────────────────
print("\n[1/5] Loading issues_snapshot.csv...")
df = pd.read_csv(RAW_DIR / "issues_snapshot.csv")
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns")

print("[1/5] Loading issues_change_history.csv...")
ch = pd.read_csv(RAW_DIR / "issues_change_history.csv")
print(f"  Loaded: {len(ch):,} rows")

# ─── Parse Dates ───────────────────────────────────────────
print("\n[2/5] Parsing dates...")
df['issue_created'] = pd.to_datetime(df['issue_created'], utc=True, errors='coerce')
df['issue_resolution_date'] = pd.to_datetime(df['issue_resolution_date'], utc=True, errors='coerce')
ch['created'] = pd.to_datetime(ch['created'], utc=True, errors='coerce')

# ─── Priority Encoding ─────────────────────────────────────
print("[2/5] Encoding priorities...")
PRIORITY_MAP = {
    'Blocker': 5,
    'Highest': 4,
    'High': 3,
    'Medium': 2,
    'unknown': 2,
    'Low': 1,
    'Lowest': 0,
}
df['priority_numeric'] = df['issue_priority'].map(PRIORITY_MAP).fillna(2)

# ─── Global Median for Fast Resolution ────────────────────
global_median_sec = df['wf_total_time'].dropna().median()
print(f"  Global median resolution time: {global_median_sec/86400:.2f} days")

# ─── Reassignment Tickets ─────────────────────────────────
print("\n[3/5] Computing reassignment data from change history...")
# Tickets that were reassigned (field='assignee' appears in change history)
reassigned_issues = set(
    ch.loc[ch['field'] == 'assignee', 'issueid'].dropna().astype(int)
)
print(f"  Tickets with reassignments: {len(reassigned_issues):,}")

# ─── First Status Change (First Response) ────────────────
print("[3/5] Computing first status change times...")
status_changes = ch[ch['field'] == 'status'].copy()
status_changes = status_changes.sort_values('created')
# Use issueid as string for merge
first_status_change = (
    status_changes.groupby('issueid')['created']
    .first()
    .reset_index()
    .rename(columns={'created': 'first_status_change'})
)

# Merge first status change into main df
df['issueid_int'] = df['id'].astype('Int64')
first_status_change['issueid'] = first_status_change['issueid'].astype('Int64')
df = df.merge(first_status_change, left_on='issueid_int', right_on='issueid', how='left')

# First response time in seconds
df['first_response_sec'] = (
    df['first_status_change'] - df['issue_created']
).dt.total_seconds()
df['first_response_sec'] = df['first_response_sec'].clip(lower=0)

# ─── Active Months ────────────────────────────────────────
print("[3/5] Computing active months...")
df['year_month'] = df['issue_created'].dt.to_period('M')

# ─── Per-Assignee Feature Engineering ────────────────────
print("\n[4/5] Engineering per-assignee features...")

def compute_features(group):
    n = len(group)
    
    # Efficiency
    total_times = group['wf_total_time'].dropna()
    med_res_days = total_times.median() / 86400 if len(total_times) > 0 else np.nan
    avg_res_days = total_times.mean() / 86400 if len(total_times) > 0 else np.nan
    std_res_days = total_times.std() / 86400 if len(total_times) > 0 else np.nan
    pct_fast = (total_times < global_median_sec).sum() / len(total_times) if len(total_times) > 0 else np.nan
    
    # Volume
    months = group['year_month'].nunique()
    total = n
    tpm = total / months if months > 0 else 0
    
    # Complexity
    avg_prio = group['priority_numeric'].mean()
    pct_high_prio = (group['priority_numeric'] >= 3).sum() / n
    n_projects = group['issue_proj'].nunique()
    n_categories = group['issue_type'].nunique()
    
    # Quality
    pct_reopened = (group['wfe_reopened'] > 0).sum() / n
    resolution_rate = group['issue_status'].isin(['closed', 'done']).sum() / n
    avg_comments = group['issue_comments_count'].mean()
    
    # Workflow - Sole Resolver
    issue_ids = set(group['id'].dropna().astype(int))
    reassigned_in_group = len(issue_ids & reassigned_issues)
    pct_sole_resolver = 1 - (reassigned_in_group / n)
    
    # First response time
    fr = group['first_response_sec'].dropna()
    avg_first_response_days = fr.mean() / 86400 if len(fr) > 0 else np.nan
    
    # Processing steps
    avg_steps = group['processing_steps'].mean()
    
    return pd.Series({
        # Efficiency
        'median_resolution_days': med_res_days,
        'avg_resolution_days': avg_res_days,
        'std_resolution_days': std_res_days,
        'pct_fast_resolved': pct_fast,
        # Volume
        'total_tickets': total,
        'tickets_per_month': tpm,
        'active_months': months,
        # Complexity
        'avg_priority': avg_prio,
        'pct_high_priority': pct_high_prio,
        'n_distinct_projects': n_projects,
        'n_distinct_categories': n_categories,
        # Quality
        'pct_reopened': pct_reopened,
        'resolution_rate': resolution_rate,
        'avg_comments': avg_comments,
        # Workflow
        'pct_sole_resolver': pct_sole_resolver,
        'avg_first_response_days': avg_first_response_days,
        'avg_processing_steps': avg_steps,
    })

# Filter assignees with at least 5 tickets
assignee_counts = df['issue_assignee'].value_counts()
valid_assignees = assignee_counts[assignee_counts >= 5].index
df_filtered = df[df['issue_assignee'].isin(valid_assignees)].copy()
print(f"  Assignees with >= 5 tickets: {len(valid_assignees)}")
print(f"  Filtered rows: {len(df_filtered):,}")

features_df = df_filtered.groupby('issue_assignee').apply(compute_features)
features_df = features_df.reset_index()
print(f"  Feature matrix shape: {features_df.shape}")

# ─── Handle NaN Values ────────────────────────────────────
print("\n[5/5] Handling NaN values...")
# Efficiency features: impute with median
efficiency_cols = ['median_resolution_days', 'avg_resolution_days', 'std_resolution_days', 
                   'pct_fast_resolved', 'avg_first_response_days']
for col in efficiency_cols:
    med = features_df[col].median()
    n_nan = features_df[col].isna().sum()
    if n_nan > 0:
        print(f"  Imputing {col}: {n_nan} NaN → {med:.4f}")
    features_df[col] = features_df[col].fillna(med)

# Volume features: fill with 0
volume_cols = ['std_resolution_days']
features_df['std_resolution_days'] = features_df['std_resolution_days'].fillna(0)

print(f"\n  NaN remaining: {features_df.isna().sum().sum()}")
print(f"  Final feature matrix: {features_df.shape[0]} employees × {features_df.shape[1]-1} features")

# ─── Save ────────────────────────────────────────────────
out_path = PROCESSED_DIR / "employee_features.csv"
features_df.to_csv(out_path, index=False)
print(f"\n✅ Saved: {out_path}")

# Quick summary
print("\nFeature summary:")
numeric_cols = features_df.select_dtypes(include='number').columns
print(features_df[numeric_cols].describe().round(3).to_string())
