"""
Bias-Analyse - Erkennt Verzerrungen in Manager-Bewertungen
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path


def analyze_score_distribution(scored_df, score_cols=['Q1', 'Q2', 'Q3']):
    """
    Analysiert die Verteilung der Scores.
    
    Returns:
        dict: Statistiken pro Score
    """
    results = {}
    
    for col in score_cols:
        valid_scores = scored_df[scored_df[col] > 0][col]
        
        results[col] = {
            'mean': round(valid_scores.mean(), 2),
            'std': round(valid_scores.std(), 2),
            'median': round(valid_scores.median(), 2),
            'min': int(valid_scores.min()),
            'max': int(valid_scores.max()),
            'count': len(valid_scores)
        }
    
    return results


def check_halo_effect(scored_df, score_cols=['Q1', 'Q2', 'Q3']):
    """
    Prüft auf Halo-Effekt (zu hohe Korrelation zwischen Scores).
    
    Der Halo-Effekt tritt auf, wenn Manager alle Dimensionen
    basierend auf einem Gesamteindruck bewerten, anstatt
    jede Dimension einzeln zu bewerten.
    
    Returns:
        dict: Halo-Effekt Analyse
    """
    valid_df = scored_df[scored_df[score_cols[0]] > 0].copy()
    
    # Korrelationsmatrix
    corr_matrix = valid_df[score_cols].corr()
    
    # Durchschnittliche Inter-Korrelation (ohne Diagonale)
    n = len(score_cols)
    corr_values = []
    for i in range(n):
        for j in range(i+1, n):
            corr_values.append(corr_matrix.iloc[i, j])
    
    avg_correlation = np.mean(corr_values)
    
    # Halo-Effekt Warnung wenn > 0.8
    is_halo = avg_correlation > 0.8
    
    if avg_correlation > 0.9:
        severity = 'HOCH'
    elif avg_correlation > 0.8:
        severity = 'MITTEL'
    else:
        severity = 'NIEDRIG'
    
    return {
        'avg_inter_correlation': round(avg_correlation, 3),
        'is_halo_effect': is_halo,
        'severity': severity,
        'correlation_matrix': corr_matrix.round(3).to_dict()
    }


def check_leniency_bias(scored_df, score_cols=['Q1', 'Q2', 'Q3'], expected_mean=3.0):
    """
    Prüft auf Leniency-Bias (zu milde Bewertung) oder Severity-Bias (zu streng).
    
    Returns:
        dict: Leniency/Severity Analyse pro Score
    """
    results = {}
    
    for col in score_cols:
        valid_scores = scored_df[scored_df[col] > 0][col]
        mean = valid_scores.mean()
        
        # Bias-Typ bestimmen
        if mean > 3.5:
            bias_type = 'LENIENCY'  # Zu mild
        elif mean < 2.5:
            bias_type = 'SEVERITY'  # Zu streng
        else:
            bias_type = None  # OK
        
        results[col] = {
            'mean': round(mean, 2),
            'expected': expected_mean,
            'deviation': round(mean - expected_mean, 2),
            'bias_type': bias_type,
            'is_biased': bias_type is not None
        }
    
    return results


def check_central_tendency(scored_df, score_cols=['Q1', 'Q2', 'Q3']):
    """
    Prüft auf Central Tendency Bias (Vermeidung extremer Bewertungen).
    
    Returns:
        dict: Central Tendency Analyse
    """
    results = {}
    
    for col in score_cols:
        valid_scores = scored_df[scored_df[col] > 0][col]
        std = valid_scores.std()
        
        # Anteil extremer Bewertungen (1 oder 5)
        extreme_ratio = ((valid_scores == 1) | (valid_scores == 5)).mean()
        
        # Central Tendency wenn Std < 0.8
        is_central = std < 0.8
        
        results[col] = {
            'std': round(std, 2),
            'extreme_ratio': round(extreme_ratio * 100, 1),
            'is_central_tendency': is_central
        }
    
    return results


def run_full_analysis(scored_df):
    """
    Führt die vollständige Bias-Analyse durch.
    
    Returns:
        dict: Alle Analyse-Ergebnisse
    """
    print("🔬 Führe Bias-Analyse durch...")
    
    score_cols = ['Q1', 'Q2', 'Q3']
    
    results = {
        'distribution': analyze_score_distribution(scored_df, score_cols),
        'halo_effect': check_halo_effect(scored_df, score_cols),
        'leniency': check_leniency_bias(scored_df, score_cols),
        'central_tendency': check_central_tendency(scored_df, score_cols)
    }
    
    # Zusammenfassung der gefundenen Bias-Typen
    bias_flags = []
    
    if results['halo_effect']['is_halo_effect']:
        bias_flags.append('HALO_EFFECT')
    
    for col, data in results['leniency'].items():
        if data['is_biased']:
            bias_flags.append(f"{data['bias_type']}_{col}")
    
    for col, data in results['central_tendency'].items():
        if data['is_central_tendency']:
            bias_flags.append(f"CENTRAL_TENDENCY_{col}")
    
    results['bias_flags'] = bias_flags
    
    print(f"✅ Analyse abgeschlossen. Gefundene Bias-Typen: {len(bias_flags)}")
    
    return results


def print_report(results):
    """Druckt einen lesbaren Report."""
    print("\n" + "="*60)
    print("📋 BIAS-ANALYSE REPORT")
    print("="*60)
    
    # Halo-Effekt
    halo = results['halo_effect']
    print(f"\n🔍 HALO-EFFEKT:")
    print(f"   Inter-Korrelation: {halo['avg_inter_correlation']}")
    print(f"   Severity: {halo['severity']}")
    if halo['is_halo_effect']:
        print("   ⚠️ WARNUNG: Starker Halo-Effekt erkannt!")
    
    # Leniency/Severity
    print(f"\n📊 LENIENCY/SEVERITY:")
    for col, data in results['leniency'].items():
        status = data['bias_type'] if data['bias_type'] else "OK"
        print(f"   {col}: Ø {data['mean']} ({status})")
    
    # Central Tendency
    print(f"\n🎯 CENTRAL TENDENCY:")
    for col, data in results['central_tendency'].items():
        status = "CENTRAL" if data['is_central_tendency'] else "OK"
        print(f"   {col}: Std={data['std']} ({status})")
    
    # Zusammenfassung
    print(f"\n🚨 GEFUNDENE BIAS-TYPEN: {len(results['bias_flags'])}")
    for flag in results['bias_flags']:
        print(f"   ⚠️ {flag}")
    
    if not results['bias_flags']:
        print("   ✅ Keine signifikanten Bias-Typen erkannt")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("="*50)
    print("🔬 BIAS-ANALYSE")
    print("="*50)
    
    # Bewertete Samples laden
    data_path = Path("data/raw/issues_snapshot_sample.xlsx")
    
    if data_path.exists():
        scored_df = pd.read_excel(data_path)
        print(f"📁 Geladen: {len(scored_df)} bewertete Samples")
        
        # Analyse
        results = run_full_analysis(scored_df)
        
        # Report
        print_report(results)
    else:
        print("❌ Bewertete Samples nicht gefunden!")
