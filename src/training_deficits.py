"""
Training-Defizite - Identifiziert Schulungsbedarf und Disziplinarmaßnahmen
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Schwellenwerte für Klassifikation
THRESHOLDS = {
    # YELLOW (Training empfohlen)
    'low_score': 2.5,            # Ø Score unter 2.5
    'high_variance': 1.5,        # Std > 1.5 (inkonsistent)
    'below_team_avg': -0.5,      # 0.5 Punkte unter Team-Ø
    
    # RED (Disziplinarisch)
    'critical_low_score': 1.5,   # Ø Score unter 1.5
    'critical_min_score': 2.0,   # Mindest-Score unter 2
}


def calculate_employee_metrics(scored_df):
    """
    Berechnet Performance-Metriken pro Mitarbeiter.
    
    Returns:
        DataFrame mit aggregierten Metriken
    """
    print("📊 Berechne Mitarbeiter-Metriken...")
    
    # Nur gültige Scores
    valid_df = scored_df[scored_df['Q1'] > 0].copy()
    
    # Aggregation pro Assignee
    metrics = valid_df.groupby('assignee').agg({
        'Q1': ['mean', 'std', 'count', 'min'],
        'Q2': ['mean'],
        'Q3': ['mean']
    }).reset_index()
    
    # Spalten umbenennen
    metrics.columns = [
        'employee_id',
        'avg_q1', 'std_q1', 'ticket_count', 'min_q1',
        'avg_q2', 'avg_q3'
    ]
    
    # Q1 und Q2 messen beide "Quality of Work", Q3 misst "Client Relations"
    # Daher: Quality Score = (Q1 + Q2) / 2, dann 50% Quality + 50% Client
    metrics['quality_score'] = (metrics['avg_q1'] + metrics['avg_q2']) / 2
    metrics['client_score'] = metrics['avg_q3']
    
    # Gesamtscore: 50% Quality of Work + 50% Client Relations
    metrics['overall_score'] = (
        metrics['quality_score'] * 0.5 +
        metrics['client_score'] * 0.5
    )
    
    # Vergleich mit Team-Durchschnitt
    team_avg = metrics['overall_score'].mean()
    metrics['vs_team_avg'] = metrics['overall_score'] - team_avg
    
    print(f"   {len(metrics)} Mitarbeiter analysiert")
    print(f"   Team-Durchschnitt: {team_avg:.2f}")
    
    return metrics


def classify_employee(metrics_row):
    """
    Klassifiziert einen Mitarbeiter nach Risk Level.
    
    Returns:
        dict: Klassifikation und Empfehlungen
    """
    training_areas = []
    disciplinary_flags = []
    recommendations = []
    
    avg_score = metrics_row['overall_score']
    std_score = metrics_row['std_q1'] if pd.notna(metrics_row['std_q1']) else 0
    min_score = metrics_row['min_q1']
    vs_team = metrics_row['vs_team_avg']
    
    # === TRAINING (YELLOW) ===
    
    if avg_score < THRESHOLDS['low_score']:
        training_areas.append('Qualität der Lösungen')
        recommendations.append('Workshop: Systematische Problemanalyse')
    
    if std_score > THRESHOLDS['high_variance']:
        training_areas.append('Konsistenz')
        recommendations.append('Coaching: Checklisten für gleichbleibende Qualität')
    
    if vs_team < THRESHOLDS['below_team_avg']:
        training_areas.append('Allgemeine Performance')
        recommendations.append('Mentoring: Pair-Work mit erfahrenem Kollegen')
    
    # === DISZIPLINARISCH (RED) ===
    
    if avg_score < THRESHOLDS['critical_low_score']:
        disciplinary_flags.append('Kritisch niedrige Performance')
    
    if min_score < THRESHOLDS['critical_min_score']:
        disciplinary_flags.append('Sehr schlechte Einzelbewertungen')
    
    # === RISK LEVEL ===
    
    if disciplinary_flags:
        risk_level = 'RED'
    elif training_areas:
        risk_level = 'YELLOW'
    else:
        risk_level = 'GREEN'
        recommendations.append('Gute Arbeit! Weiter so.')
    
    return {
        'risk_level': risk_level,
        'training_areas': training_areas,
        'disciplinary_flags': disciplinary_flags,
        'recommendations': recommendations
    }


def analyze_all_employees(scored_df):
    """
    Analysiert alle Mitarbeiter.
    
    Returns:
        DataFrame mit Klassifikation
    """
    print("\n🔍 TRAININGSDEFIZIT-ANALYSE")
    print("="*50)
    
    # Metriken berechnen
    metrics_df = calculate_employee_metrics(scored_df)
    
    # Jeden Mitarbeiter klassifizieren
    results = []
    
    for _, row in metrics_df.iterrows():
        classification = classify_employee(row)
        
        results.append({
            'employee': row['employee_id'],
            'overall_score': round(row['overall_score'], 2),
            'ticket_count': int(row['ticket_count']),
            'risk_level': classification['risk_level'],
            'training_areas': ', '.join(classification['training_areas']) or '-',
            'flags': ', '.join(classification['disciplinary_flags']) or '-',
            'recommendations': '; '.join(classification['recommendations'])
        })
    
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(['risk_level', 'overall_score'], ascending=[False, True])
    
    # Zusammenfassung
    green = (results_df['risk_level'] == 'GREEN').sum()
    yellow = (results_df['risk_level'] == 'YELLOW').sum()
    red = (results_df['risk_level'] == 'RED').sum()
    
    print(f"\n📊 ERGEBNIS:")
    print(f"   🟢 GREEN (OK): {green}")
    print(f"   🟡 YELLOW (Training): {yellow}")
    print(f"   🔴 RED (Disziplinarisch): {red}")
    
    return results_df


def print_training_plan(results_df):
    """Druckt einen Trainingsplan."""
    print("\n" + "="*50)
    print("📋 TRAININGSPLAN")
    print("="*50)
    
    # RED Mitarbeiter
    red_employees = results_df[results_df['risk_level'] == 'RED']
    if len(red_employees) > 0:
        print("\n🔴 DRINGEND - Sofortmaßnahmen:")
        for _, emp in red_employees.iterrows():
            print(f"\n   {emp['employee']} (Score: {emp['overall_score']})")
            print(f"      Flags: {emp['flags']}")
    
    # YELLOW Mitarbeiter
    yellow_employees = results_df[results_df['risk_level'] == 'YELLOW']
    if len(yellow_employees) > 0:
        print("\n🟡 TRAINING EMPFOHLEN:")
        for _, emp in yellow_employees.head(10).iterrows():
            print(f"\n   {emp['employee']} (Score: {emp['overall_score']})")
            print(f"      Bereiche: {emp['training_areas']}")
    
    if len(red_employees) == 0 and len(yellow_employees) == 0:
        print("\n✅ Alle Mitarbeiter im grünen Bereich!")


if __name__ == "__main__":
    print("="*50)
    print("🔍 TRAINING-DEFIZITE")
    print("="*50)
    
    # Daten laden
    data_path = Path("data/raw/issues_snapshot_sample.xlsx")
    
    if data_path.exists():
        scored_df = pd.read_excel(data_path)
        print(f"📁 Geladen: {len(scored_df)} bewertete Samples")
        
        # Analyse
        results_df = analyze_all_employees(scored_df)
        
        # Trainingsplan
        print_training_plan(results_df)
        
        # Speichern
        output_path = Path("reports/training_report.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(output_path, index=False)
        print(f"\n💾 Gespeichert: {output_path}")
    else:
        print("❌ Bewertete Samples nicht gefunden!")
