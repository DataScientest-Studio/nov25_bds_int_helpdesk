"""
Trend Analysis - Performance development and forecasts
"""

import pandas as pd
import numpy as np
from pathlib import Path


def calculate_employee_trends(scored_df):
    """
    Calculate trends per employee.

    Returns:
        DataFrame with trend metrics
    """
    print(" Calculating employee trends...")

    # Only valid scores
    valid_df = scored_df[scored_df['Q1'] > 0].copy()

    # Aggregation
    trends = valid_df.groupby('assignee').agg({
        'Q1': ['mean', 'std', 'count'],
        'Q2': 'mean',
        'Q3': 'mean'
    }).reset_index()

    trends.columns = ['employee', 'avg_q1', 'std_q1', 'ticket_count', 'avg_q2', 'avg_q3']

    # Overall score
    trends['overall_score'] = (trends['avg_q1'] + trends['avg_q2'] + trends['avg_q3']) / 3

    # Variance (higher = more inconsistent)
    trends['variance'] = trends['std_q1'].fillna(0)

    # Risk level
    def get_risk(row):
        if row['overall_score'] < 2.0:
            return 'RED'
        elif row['overall_score'] < 3.0:
            return 'YELLOW'
        else:
            return 'GREEN'

    trends['risk_level'] = trends.apply(get_risk, axis=1)

    # Sort by score
    trends = trends.sort_values('overall_score', ascending=False)

    print(f"   {len(trends)} employees analyzed")

    return trends


def get_top_bottom(trends_df, n=10):
    """Return top and bottom performers."""
    top = trends_df.nlargest(n, 'overall_score')[['employee', 'overall_score', 'ticket_count']]
    bottom = trends_df.nsmallest(n, 'overall_score')[['employee', 'overall_score', 'ticket_count']]

    return {
        'top': top.to_dict('records'),
        'bottom': bottom.to_dict('records')
    }


def calculate_team_statistics(trends_df):
    """Calculate team statistics."""
    stats = {
        'total_employees': len(trends_df),
        'avg_score': round(trends_df['overall_score'].mean(), 2),
        'std_score': round(trends_df['overall_score'].std(), 2),
        'median_score': round(trends_df['overall_score'].median(), 2),
        'green_count': (trends_df['risk_level'] == 'GREEN').sum(),
        'yellow_count': (trends_df['risk_level'] == 'YELLOW').sum(),
        'red_count': (trends_df['risk_level'] == 'RED').sum(),
        'total_tickets': int(trends_df['ticket_count'].sum()),
        'avg_tickets_per_employee': round(trends_df['ticket_count'].mean(), 1)
    }
    return stats


def simulate_training_effect(trends_df, improvement=0.5, coverage=0.5):
    """
    Simulate the effect of training on YELLOW employees.

    Args:
        trends_df: Trends DataFrame
        improvement: Score improvement from training
        coverage: Proportion of YELLOW employees who receive training

    Returns:
        dict: Before/after statistics
    """
    yellow_employees = trends_df[trends_df['risk_level'] == 'YELLOW'].copy()

    # Number of employees to train
    n_to_train = int(len(yellow_employees) * coverage)

    # Simulate improvement
    current_avg = trends_df['overall_score'].mean()

    # After training
    improved_df = trends_df.copy()
    train_indices = yellow_employees.head(n_to_train).index
    improved_df.loc[train_indices, 'overall_score'] += improvement
    improved_df['overall_score'] = improved_df['overall_score'].clip(upper=5.0)

    new_avg = improved_df['overall_score'].mean()

    return {
        'current_avg': round(current_avg, 2),
        'projected_avg': round(new_avg, 2),
        'improvement': round(new_avg - current_avg, 2),
        'employees_trained': n_to_train,
        'coverage_pct': int(coverage * 100)
    }


def print_trend_report(trends_df):
    """Print a trend report."""
    stats = calculate_team_statistics(trends_df)
    top_bottom = get_top_bottom(trends_df, 5)

    print("\n" + "="*50)
    print(" TREND ANALYSIS REPORT")
    print("="*50)

    # Team statistics
    print(f"\n TEAM STATISTICS:")
    print(f"   Employees: {stats['total_employees']}")
    print(f"   Avg score: {stats['avg_score']}")
    print(f"   Total tickets: {stats['total_tickets']}")

    # Risk distribution
    print(f"\n RISK DISTRIBUTION:")
    print(f"    GREEN: {stats['green_count']}")
    print(f"    YELLOW: {stats['yellow_count']}")
    print(f"    RED: {stats['red_count']}")

    # Top performers
    print(f"\n TOP 5 PERFORMERS:")
    for emp in top_bottom['top']:
        print(f"   {emp['employee']}: {emp['overall_score']:.2f} ({emp['ticket_count']} tickets)")

    # Bottom performers
    print(f"\n BOTTOM 5 (Action required):")
    for emp in top_bottom['bottom']:
        print(f"   {emp['employee']}: {emp['overall_score']:.2f} ({emp['ticket_count']} tickets)")

    # Training simulation
    simulation = simulate_training_effect(trends_df)
    print(f"\n TRAINING SIMULATION (50% of YELLOW employees):")
    print(f"   Current avg: {simulation['current_avg']}")
    print(f"   After training: {simulation['projected_avg']}")
    print(f"   Improvement: +{simulation['improvement']}")


if __name__ == "__main__":
    print("="*50)
    print(" TREND ANALYSIS")
    print("="*50)

    # Load data
    data_path = Path("data/raw/issues_snapshot_sample.xlsx")

    if data_path.exists():
        scored_df = pd.read_excel(data_path)
        print(f" Loaded: {len(scored_df)} rated samples")

        # Calculate trends
        trends_df = calculate_employee_trends(scored_df)

        # Report
        print_trend_report(trends_df)

        # Save
        output_path = Path("reports/trend_analysis.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        trends_df.to_csv(output_path, index=False)
        print(f"\n Saved: {output_path}")
    else:
        print(" Rated samples not found!")
