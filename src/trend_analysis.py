"""
Trend-Analyse - Performance-Entwicklung und Prognosen
"""

import pandas as pd
import numpy as np
from pathlib import Path


def calculate_employee_trends(scored_df):
    """
    Calculatet Trends pro Employee.
    
    Returns:
        DataFrame mit Trend-Metriken
    """
    print("📈 Calculate Employee-Trends...")
    
    # Nur gültige Scores
    valid_df = scored_df[scored_df['Q1'] > 0].copy()
    
    # Aggregation
    trends = valid_df.groupby('assignee').agg({
        'Q1': ['mean', 'std', 'count'],
        'Q2': 'mean',
        'Q3': 'mean'
    }).reset_index()
    
    trends.columns = ['employee', 'avg_q1', 'std_q1', 'ticket_count', 'avg_q2', 'avg_q3']
    
    # Gesamtscore
    trends['overall_score'] = (trends['avg_q1'] + trends['avg_q2'] + trends['avg_q3']) / 3
    
    # Varianz (höher = inkonsistent)
    trends['variance'] = trends['std_q1'].fillna(0)
    
    # Risk Level
    def get_risk(row):
        if row['overall_score'] < 2.0:
            return 'RED'
        elif row['overall_score'] < 3.0:
            return 'YELLOW'
        else:
            return 'GREEN'
    
    trends['risk_level'] = trends.apply(get_risk, axis=1)
    
    # Sortieren nach Score
    trends = trends.sort_values('overall_score', ascending=False)
    
    print(f"   {len(trends)} Employee analysiert")
    
    return trends


def get_top_bottom(trends_df, n=10):
    """Gibt Top und Bottom Performer zurück."""
    top = trends_df.nlargest(n, 'overall_score')[['employee', 'overall_score', 'ticket_count']]
    bottom = trends_df.nsmallest(n, 'overall_score')[['employee', 'overall_score', 'ticket_count']]
    
    return {
        'top': top.to_dict('records'),
        'bottom': bottom.to_dict('records')
    }


def calculate_team_statistics(trends_df):
    """Calculatet Team-Statistiken."""
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
    Simuliert den Effekt von Training auf YELLOW-Employee.
    
    Args:
        trends_df: Trends DataFrame
        improvement: Score-Verbesserung durch Training
        coverage: Anteil der YELLOW-Employee die trainiert werden
        
    Returns:
        dict: Vorher/Nachher Statistiken
    """
    yellow_employees = trends_df[trends_df['risk_level'] == 'YELLOW'].copy()
    
    # Anzahl zu trainierender Employee
    n_to_train = int(len(yellow_employees) * coverage)
    
    # Simuliere Verbesserung
    current_avg = trends_df['overall_score'].mean()
    
    # Nach Training
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
    """Druckt einen Trend-Report."""
    stats = calculate_team_statistics(trends_df)
    top_bottom = get_top_bottom(trends_df, 5)
    
    print("\n" + "="*50)
    print("📈 TREND-ANALYSE REPORT")
    print("="*50)
    
    # Team-Statistiken
    print(f"\n📊 TEAM-STATISTIKEN:")
    print(f"   Employee: {stats['total_employees']}")
    print(f"   Ø Score: {stats['avg_score']}")
    print(f"   Tickets gesamt: {stats['total_tickets']}")
    
    # Risk-Verteilung
    print(f"\n🚦 RISK-VERTEILUNG:")
    print(f"   🟢 GREEN: {stats['green_count']}")
    print(f"   🟡 YELLOW: {stats['yellow_count']}")
    print(f"   🔴 RED: {stats['red_count']}")
    
    # Top Performer
    print(f"\n🏆 TOP 5 PERFORMER:")
    for emp in top_bottom['top']:
        print(f"   {emp['employee']}: {emp['overall_score']:.2f} ({emp['ticket_count']} Tickets)")
    
    # Bottom Performer
    print(f"\n⚠️ BOTTOM 5 (Handlungsbedarf):")
    for emp in top_bottom['bottom']:
        print(f"   {emp['employee']}: {emp['overall_score']:.2f} ({emp['ticket_count']} Tickets)")
    
    # Training-Simulation
    simulation = simulate_training_effect(trends_df)
    print(f"\n📊 TRAINING-SIMULATION (50% der YELLOW-Employee):")
    print(f"   Aktueller Ø: {simulation['current_avg']}")
    print(f"   Nach Training: {simulation['projected_avg']}")
    print(f"   Verbesserung: +{simulation['improvement']}")


if __name__ == "__main__":
    print("="*50)
    print("📈 TREND-ANALYSE")
    print("="*50)
    
    # Data laden
    data_path = Path("data/raw/issues_snapshot_sample.xlsx")
    
    if data_path.exists():
        scored_df = pd.read_excel(data_path)
        print(f"📁 Loaded: {len(scored_df)} bewertete Samples")
        
        # Trends berechnen
        trends_df = calculate_employee_trends(scored_df)
        
        # Report
        print_trend_report(trends_df)
        
        # Saven
        output_path = Path("reports/trend_analysis.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        trends_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved: {output_path}")
    else:
        print("❌ Bewertete Samples not found!")
