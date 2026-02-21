"""
Bias Analysis - Detects biases in manager ratings
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path


def analyze_score_distribution(scored_df, score_cols=['Q1', 'Q2', 'Q3']):
    """
    Analyze the distribution of scores.

    Returns:
        dict: Statistics per score
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
    Check for Halo Effect (too high correlation between scores).

    The Halo Effect occurs when managers rate all dimensions
    based on an overall impression, instead of
    rating each dimension individually.

    Returns:
        dict: Halo Effect analysis
    """
    valid_df = scored_df[scored_df[score_cols[0]] > 0].copy()

    # Correlation matrix
    corr_matrix = valid_df[score_cols].corr()

    # Average inter-correlation (without diagonal)
    n = len(score_cols)
    corr_values = []
    for i in range(n):
        for j in range(i+1, n):
            corr_values.append(corr_matrix.iloc[i, j])

    avg_correlation = np.mean(corr_values)

    # Halo Effect warning if > 0.8
    is_halo = avg_correlation > 0.8

    if avg_correlation > 0.9:
        severity = 'HIGH'
    elif avg_correlation > 0.8:
        severity = 'MEDIUM'
    else:
        severity = 'LOW'

    return {
        'avg_inter_correlation': round(avg_correlation, 3),
        'is_halo_effect': is_halo,
        'severity': severity,
        'correlation_matrix': corr_matrix.round(3).to_dict()
    }


def check_leniency_bias(scored_df, score_cols=['Q1', 'Q2', 'Q3'], expected_mean=3.0):
    """
    Check for Leniency Bias (too mild rating) or Severity Bias (too strict).

    Returns:
        dict: Leniency/Severity analysis per score
    """
    results = {}

    for col in score_cols:
        valid_scores = scored_df[scored_df[col] > 0][col]
        mean = valid_scores.mean()

        # Determine bias type
        if mean > 3.5:
            bias_type = 'LENIENCY'  # Too mild
        elif mean < 2.5:
            bias_type = 'SEVERITY'  # Too strict
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
    Check for Central Tendency Bias (avoidance of extreme ratings).

    Returns:
        dict: Central Tendency analysis
    """
    results = {}

    for col in score_cols:
        valid_scores = scored_df[scored_df[col] > 0][col]
        std = valid_scores.std()

        # Proportion of extreme ratings (1 or 5)
        extreme_ratio = ((valid_scores == 1) | (valid_scores == 5)).mean()

        # Central Tendency if Std < 0.8
        is_central = std < 0.8

        results[col] = {
            'std': round(std, 2),
            'extreme_ratio': round(extreme_ratio * 100, 1),
            'is_central_tendency': is_central
        }

    return results


def run_full_analysis(scored_df):
    """
    Run the complete bias analysis.

    Returns:
        dict: All analysis results
    """
    print(" Running bias analysis...")

    score_cols = ['Q1', 'Q2', 'Q3']

    results = {
        'distribution': analyze_score_distribution(scored_df, score_cols),
        'halo_effect': check_halo_effect(scored_df, score_cols),
        'leniency': check_leniency_bias(scored_df, score_cols),
        'central_tendency': check_central_tendency(scored_df, score_cols)
    }

    # Summary of found bias types
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

    print(f" Analysis complete. Found bias types: {len(bias_flags)}")

    return results


def print_report(results):
    """Print a readable report."""
    print("\n" + "="*60)
    print(" BIAS ANALYSIS REPORT")
    print("="*60)

    # Halo Effect
    halo = results['halo_effect']
    print(f"\n HALO EFFECT:")
    print(f"   Inter-correlation: {halo['avg_inter_correlation']}")
    print(f"   Severity: {halo['severity']}")
    if halo['is_halo_effect']:
        print("    WARNING: Strong Halo Effect detected!")

    # Leniency/Severity
    print(f"\n LENIENCY/SEVERITY:")
    for col, data in results['leniency'].items():
        status = data['bias_type'] if data['bias_type'] else "OK"
        print(f"   {col}: Avg {data['mean']} ({status})")

    # Central Tendency
    print(f"\n CENTRAL TENDENCY:")
    for col, data in results['central_tendency'].items():
        status = "CENTRAL" if data['is_central_tendency'] else "OK"
        print(f"   {col}: Std={data['std']} ({status})")

    # Summary
    print(f"\n FOUND BIAS TYPES: {len(results['bias_flags'])}")
    for flag in results['bias_flags']:
        print(f"    {flag}")

    if not results['bias_flags']:
        print("    No significant bias types detected")

    print("\n" + "="*60)


if __name__ == "__main__":
    print("="*50)
    print(" BIAS ANALYSIS")
    print("="*50)

    # Load rated samples
    data_path = Path("data/raw/issues_snapshot_sample.xlsx")

    if data_path.exists():
        scored_df = pd.read_excel(data_path)
        print(f" Loaded: {len(scored_df)} rated samples")

        # Analysis
        results = run_full_analysis(scored_df)

        # Report
        print_report(results)
    else:
        print(" Rated samples not found!")
