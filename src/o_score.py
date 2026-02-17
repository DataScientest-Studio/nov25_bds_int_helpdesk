"""
O-Score - Objektives Bewertungssystem (Parallel zum Q-Score)

Berechnet einen datenbasierten Performance-Score (1-5) basierend auf:
- Qualität (35%): Reopen-Rate, Success-Rate
- Effizienz (25%): Bearbeitungszeit
- Produktivität (20%): Volumen, Processing Steps
- Kommunikation (20%): First-Touch, Kommentare

Autor: Frank (AI Assistant)
Datum: 2026-02-16
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Gewichtung der Komponenten
WEIGHTS = {
    'quality': 0.35,
    'efficiency': 0.25,
    'productivity': 0.20,
    'communication': 0.20
}

# Mindestanzahl Tickets fuer valide Bewertung
MIN_TICKETS = 10


def load_snapshot_data(data_path="data/raw/issues_snapshot.csv"):
    """Laedt die Snapshot-Daten."""
    return pd.read_csv(data_path, low_memory=False)


def calculate_employee_metrics(snapshot_df, min_tickets=MIN_TICKETS):
    """
    Aggregiert Metriken pro Mitarbeiter.
    
    Args:
        snapshot_df: DataFrame mit issues_snapshot Daten
        min_tickets: Mindestanzahl Tickets fuer Bewertung
        
    Returns:
        DataFrame mit Metriken pro Mitarbeiter
    """
    # Nur Mitarbeiter mit genug Tickets
    assignee_counts = snapshot_df.groupby('issue_assignee').size()
    valid_assignees = assignee_counts[assignee_counts >= min_tickets].index
    df = snapshot_df[snapshot_df['issue_assignee'].isin(valid_assignees)].copy()
    
    # Aggregation
    metrics = df.groupby('issue_assignee').agg({
        'id': 'count',
        'wf_total_time': 'median',
        'processing_steps': 'mean',
        'issue_comments_count': 'mean',
        'wfe_reopened': lambda x: (x > 0).mean(),
        'turn': lambda x: (x == 1).mean(),
        'issue_resolution': lambda x: (x == 'Done').mean()
    }).reset_index()
    
    metrics.columns = [
        'employee', 'ticket_count', 'median_time', 'avg_steps',
        'avg_comments', 'reopen_rate', 'first_touch_rate', 'success_rate'
    ]
    
    # Zeit in Stunden
    metrics['median_time_hours'] = metrics['median_time'] / 3600
    
    return metrics


def calculate_quality_score(metrics_df):
    """
    Berechnet Quality-Score (0-1).
    
    - Reopen-Rate: niedriger = besser (60%)
    - Success-Rate: hoeher = besser (40%)
    """
    # Reopen invertieren (Cap bei 50%)
    quality_reopen = 1 - metrics_df['reopen_rate'].clip(upper=0.5) / 0.5
    quality_success = metrics_df['success_rate']
    
    return 0.6 * quality_reopen + 0.4 * quality_success


def calculate_efficiency_score(metrics_df):
    """
    Berechnet Efficiency-Score (0-1).
    
    - Bearbeitungszeit: Percentile-basiert, schneller = besser
    """
    time_percentile = metrics_df['median_time_hours'].rank(pct=True)
    return 1 - time_percentile


def calculate_productivity_score(metrics_df):
    """
    Berechnet Productivity-Score (0-1).
    
    - Ticket-Volumen: hoeher = besser (60%)
    - Processing Steps: weniger = besser (40%)
    """
    volume_percentile = metrics_df['ticket_count'].rank(pct=True)
    steps_percentile = metrics_df['avg_steps'].rank(pct=True)
    
    return 0.6 * volume_percentile + 0.4 * (1 - steps_percentile)


def calculate_communication_score(metrics_df):
    """
    Berechnet Communication-Score (0-1).
    
    - First-Touch-Rate: hoeher = besser (50%)
    - Kommentare: optimal ist Median (50%)
    """
    # Kommentare: optimal ist Median
    comment_median = metrics_df['avg_comments'].median()
    comment_deviation = abs(metrics_df['avg_comments'] - comment_median) / max(comment_median, 1)
    comm_optimal = 1 - comment_deviation.clip(upper=1)
    
    return 0.5 * metrics_df['first_touch_rate'] + 0.5 * comm_optimal


def calculate_o_score(snapshot_df, min_tickets=MIN_TICKETS):
    """
    Berechnet den vollstaendigen O-Score.
    
    Args:
        snapshot_df: DataFrame mit issues_snapshot Daten
        min_tickets: Mindestanzahl Tickets
        
    Returns:
        DataFrame mit O-Score und allen Komponenten
    """
    # Metriken berechnen
    metrics = calculate_employee_metrics(snapshot_df, min_tickets)
    
    # Komponenten-Scores
    metrics['quality_score'] = calculate_quality_score(metrics)
    metrics['efficiency_score'] = calculate_efficiency_score(metrics)
    metrics['productivity_score'] = calculate_productivity_score(metrics)
    metrics['communication_score'] = calculate_communication_score(metrics)
    
    # Gewichteter Gesamt-Score (0-1)
    metrics['o_score_raw'] = (
        WEIGHTS['quality'] * metrics['quality_score'] +
        WEIGHTS['efficiency'] * metrics['efficiency_score'] +
        WEIGHTS['productivity'] * metrics['productivity_score'] +
        WEIGHTS['communication'] * metrics['communication_score']
    )
    
    # Skalierung auf 1-5
    metrics['o_score'] = np.clip(metrics['o_score_raw'] * 5, 1, 5).round(2)
    metrics['o_score_int'] = np.clip(np.ceil(metrics['o_score_raw'] * 5), 1, 5).astype(int)
    
    return metrics


def compare_with_q_score(o_score_df, q_score_path="data/raw/issues_snapshot_sample.xlsx"):
    """
    Vergleicht O-Score mit Q-Score (Manager-Bewertung).
    
    Returns:
        DataFrame mit beiden Scores und Differenz
    """
    # Q-Scores laden
    scored = pd.read_excel(q_score_path)
    
    # Q-Scores aggregieren
    q_scores = scored[scored['Q1'] > 0].groupby('assignee').agg({
        'Q1': 'mean',
        'Q2': 'mean',
        'Q3': 'mean'
    }).reset_index()
    
    q_scores['q_score'] = (q_scores['Q1'] + q_scores['Q2'] + q_scores['Q3']) / 3
    q_scores.columns = ['employee', 'q1', 'q2', 'q3', 'q_score']
    
    # Merge
    comparison = o_score_df.merge(q_scores, on='employee', how='inner')
    
    # Differenz
    comparison['score_diff'] = comparison['o_score'] - comparison['q_score']
    comparison['bias_type'] = comparison['score_diff'].apply(
        lambda x: 'OVERRATED' if x < -1 else ('UNDERRATED' if x > 1 else 'OK')
    )
    
    return comparison


def get_risk_classification(o_score_df):
    """
    Klassifiziert Mitarbeiter nach O-Score.
    
    Returns:
        DataFrame mit Risk-Level
    """
    df = o_score_df.copy()
    
    def classify(score):
        if score >= 4.0:
            return 'EXCELLENT'
        elif score >= 3.0:
            return 'GOOD'
        elif score >= 2.0:
            return 'NEEDS_IMPROVEMENT'
        else:
            return 'CRITICAL'
    
    df['risk_level'] = df['o_score'].apply(classify)
    
    return df


def print_summary(o_score_df):
    """Gibt eine Zusammenfassung aus."""
    print("\n" + "="*50)
    print("O-SCORE ZUSAMMENFASSUNG")
    print("="*50)
    
    print(f"\nMitarbeiter bewertet: {len(o_score_df)}")
    
    print(f"\nO-Score Verteilung:")
    print(o_score_df['o_score_int'].value_counts().sort_index().to_string())
    
    print(f"\nStatistiken:")
    print(f"   Mean: {o_score_df['o_score'].mean():.2f}")
    print(f"   Median: {o_score_df['o_score'].median():.2f}")
    print(f"   Std: {o_score_df['o_score'].std():.2f}")
    
    # Komponenten-Durchschnitte
    print(f"\nKomponenten-Durchschnitte:")
    print(f"   Quality: {o_score_df['quality_score'].mean():.2f}")
    print(f"   Efficiency: {o_score_df['efficiency_score'].mean():.2f}")
    print(f"   Productivity: {o_score_df['productivity_score'].mean():.2f}")
    print(f"   Communication: {o_score_df['communication_score'].mean():.2f}")


if __name__ == "__main__":
    print("="*50)
    print("O-SCORE BERECHNUNG")
    print("="*50)
    
    # Daten laden
    snapshot = load_snapshot_data()
    print(f"Daten geladen: {len(snapshot):,} Zeilen")
    
    # O-Score berechnen
    o_scores = calculate_o_score(snapshot)
    
    # Zusammenfassung
    print_summary(o_scores)
    
    # Mit Q-Score vergleichen
    print("\n" + "="*50)
    print("VERGLEICH MIT Q-SCORE")
    print("="*50)
    
    comparison = compare_with_q_score(o_scores)
    
    corr = comparison['o_score'].corr(comparison['q_score'])
    print(f"\nKorrelation O vs Q: {corr:.3f}")
    print(f"Mean Differenz: {comparison['score_diff'].mean():.2f}")
    
    bias_counts = comparison['bias_type'].value_counts()
    print(f"\nBias-Analyse:")
    for bias_type, count in bias_counts.items():
        print(f"   {bias_type}: {count}")
    
    # Speichern
    output_dir = Path("data/processed")
    o_scores.to_csv(output_dir / "o_score_results.csv", index=False)
    comparison.to_csv(output_dir / "q_vs_o_score_comparison.csv", index=False)
    
    # Risk Classification
    risk_df = get_risk_classification(o_scores)
    risk_df.to_csv(output_dir / "o_score_risk_classification.csv", index=False)
    
    print(f"\nDateien gespeichert in {output_dir}/")
