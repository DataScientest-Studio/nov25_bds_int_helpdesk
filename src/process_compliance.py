"""
Prozess-Compliance - Prüft die Einhaltung des Workflow-Prozesses
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Erwarteter Prozessfluss
EXPECTED_PROCESS = ["Open", "In Progress", "Resolved", "Closed"]

# Erlaubte Statusübergänge
VALID_TRANSITIONS = {
    "Open": ["In Progress", "Closed"],
    "In Progress": ["Waiting", "Resolved", "Open"],
    "Waiting": ["In Progress", "Resolved"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": ["In Progress"]
}


def check_compliance(status_history):
    """
    Prüft ob ein Workflow den Prozess korrekt einhält.
    
    Args:
        status_history: Liste der Status-Werte
        
    Returns:
        dict: Compliance-Ergebnis
    """
    if not status_history or len(status_history) < 2:
        return {
            'is_compliant': True,
            'violations': 0,
            'backward_steps': 0,
            'compliance_score': 1.0
        }
    
    violations = 0
    backward_steps = 0
    
    for i in range(1, len(status_history)):
        prev_status = status_history[i-1]
        curr_status = status_history[i]
        
        # Prüfe auf ungültige Übergänge
        valid_next = VALID_TRANSITIONS.get(prev_status, [])
        if curr_status not in valid_next:
            violations += 1
        
        # Prüfe auf Rückwärtsschritte
        if prev_status in EXPECTED_PROCESS and curr_status in EXPECTED_PROCESS:
            prev_idx = EXPECTED_PROCESS.index(prev_status)
            curr_idx = EXPECTED_PROCESS.index(curr_status)
            if curr_idx < prev_idx:
                backward_steps += 1
    
    # Compliance-Score berechnen
    total_transitions = len(status_history) - 1
    compliance_score = 1.0 - (violations / total_transitions)
    
    return {
        'is_compliant': violations == 0,
        'violations': violations,
        'backward_steps': backward_steps,
        'compliance_score': max(0.0, compliance_score)
    }


def analyze_workflow_from_wfe(issues_df):
    """
    Analysiert Workflows basierend auf wfe_* Spalten.
    (wfe_ = Anzahl der Durchläufe pro Status)
    
    Args:
        issues_df: DataFrame mit Issues
        
    Returns:
        DataFrame mit Compliance-Analyse
    """
    print("🔄 Analysiere Workflows...")
    
    # Finde alle wfe_ Spalten
    wfe_cols = [col for col in issues_df.columns if col.startswith('wfe_')]
    
    results = []
    
    for idx, row in issues_df.iterrows():
        issue_id = row.get('id', idx)
        
        # Berechne Metriken
        total_steps = sum(row[col] for col in wfe_cols if pd.notna(row[col]))
        
        # Reopens zählen
        reopens = 0
        if 'wfe_reopened' in issues_df.columns:
            reopens = row['wfe_reopened'] if pd.notna(row['wfe_reopened']) else 0
        
        # Rückwärtsschritte (mehrfache Durchläufe)
        backward = 0
        for col in wfe_cols:
            if pd.notna(row[col]) and row[col] > 1:
                backward += row[col] - 1
        
        # Compliance Score
        penalty = (reopens * 0.1) + (backward * 0.05)
        compliance_score = max(0, 1.0 - penalty)
        
        results.append({
            'issue_id': issue_id,
            'total_steps': total_steps,
            'reopens': reopens,
            'backward_steps': backward,
            'compliance_score': round(compliance_score, 3),
            'is_compliant': compliance_score > 0.8
        })
        
        # Fortschritt
        if (idx + 1) % 10000 == 0:
            print(f"   {idx+1:,}/{len(issues_df):,} analysiert...")
    
    print(f"✅ {len(results):,} Issues analysiert")
    return pd.DataFrame(results)


def get_compliance_summary(workflow_df):
    """Erstellt eine Zusammenfassung der Compliance."""
    return {
        'total_issues': len(workflow_df),
        'compliant_count': int(workflow_df['is_compliant'].sum()),
        'compliance_rate': round(workflow_df['is_compliant'].mean() * 100, 1),
        'avg_compliance_score': round(workflow_df['compliance_score'].mean(), 3),
        'avg_steps': round(workflow_df['total_steps'].mean(), 1),
        'total_reopens': int(workflow_df['reopens'].sum()),
        'reopen_rate': round((workflow_df['reopens'] > 0).mean() * 100, 1)
    }


if __name__ == "__main__":
    print("="*50)
    print("🔄 PROZESS-COMPLIANCE")
    print("="*50)
    
    # Issues laden
    data_path = Path("data/raw/issues.csv")
    
    if data_path.exists():
        issues = pd.read_csv(data_path)
        print(f"📁 Geladen: {len(issues):,} Issues")
        
        # Analyse
        workflow_df = analyze_workflow_from_wfe(issues)
        
        # Zusammenfassung
        summary = get_compliance_summary(workflow_df)
        
        print("\n📊 ZUSAMMENFASSUNG:")
        print(f"   Total Issues: {summary['total_issues']:,}")
        print(f"   Compliant: {summary['compliant_count']:,} ({summary['compliance_rate']}%)")
        print(f"   Ø Compliance Score: {summary['avg_compliance_score']}")
        print(f"   Reopen Rate: {summary['reopen_rate']}%")
        
        # Speichern
        output_path = Path("data/processed/workflow_analysis.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_df.to_csv(output_path, index=False)
        print(f"\n💾 Gespeichert: {output_path}")
    else:
        print("❌ Issues-Datei nicht gefunden!")
