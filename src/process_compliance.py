"""
Process Compliance - Checks adherence to workflow process
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Expected process flow
EXPECTED_PROCESS = ["Open", "In Progress", "Resolved", "Closed"]

# Allowed status transitions
VALID_TRANSITIONS = {
    "Open": ["In Progress", "Closed"],
    "In Progress": ["Waiting", "Resolved", "Open"],
    "Waiting": ["In Progress", "Resolved"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": ["In Progress"]
}


def check_compliance(status_history):
    """
    Check whether a workflow correctly follows the defined process.
    
    Args:
        status_history: List of status values
        
    Returns:
        dict: Compliance result
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
        
        # Check for invalid transitions
        valid_next = VALID_TRANSITIONS.get(prev_status, [])
        if curr_status not in valid_next:
            violations += 1
        
        # Check for backward steps
        if prev_status in EXPECTED_PROCESS and curr_status in EXPECTED_PROCESS:
            prev_idx = EXPECTED_PROCESS.index(prev_status)
            curr_idx = EXPECTED_PROCESS.index(curr_status)
            if curr_idx < prev_idx:
                backward_steps += 1
    
    # Calculate compliance score
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
    Analyze workflows based on wfe_* columns.
    (wfe_ = number of passes per status)
    
    Args:
        issues_df: DataFrame with issues
        
    Returns:
        DataFrame with compliance analysis
    """
    print("🔄 Analyzing workflows...")
    
    # Find all wfe_ columns
    wfe_cols = [col for col in issues_df.columns if col.startswith('wfe_')]
    
    results = []
    
    for idx, row in issues_df.iterrows():
        issue_id = row.get('id', idx)
        
        # Calculate metrics
        total_steps = sum(row[col] for col in wfe_cols if pd.notna(row[col]))
        
        # Count reopens
        reopens = 0
        if 'wfe_reopened' in issues_df.columns:
            reopens = row['wfe_reopened'] if pd.notna(row['wfe_reopened']) else 0
        
        # Backward steps (multiple passes through same status)
        backward = 0
        for col in wfe_cols:
            if pd.notna(row[col]) and row[col] > 1:
                backward += row[col] - 1
        
        # Compliance score
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
        
        # Progress indicator
        if (idx + 1) % 10000 == 0:
            print(f"   {idx+1:,}/{len(issues_df):,} analyzed...")
    
    print(f"✅ {len(results):,} issues analyzed")
    return pd.DataFrame(results)


def get_compliance_summary(workflow_df):
    """Create a compliance summary."""
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
    print("🔄 PROCESS COMPLIANCE")
    print("="*50)
    
    # Load issues
    data_path = Path("data/raw/issues.csv")
    
    if data_path.exists():
        issues = pd.read_csv(data_path)
        print(f"📁 Loaded: {len(issues):,} issues")
        
        # Analysis
        workflow_df = analyze_workflow_from_wfe(issues)
        
        # Summary
        summary = get_compliance_summary(workflow_df)
        
        print("\n📊 SUMMARY:")
        print(f"   Total issues: {summary['total_issues']:,}")
        print(f"   Compliant: {summary['compliant_count']:,} ({summary['compliance_rate']}%)")
        print(f"   Avg compliance score: {summary['avg_compliance_score']}")
        print(f"   Reopen rate: {summary['reopen_rate']}%")
        
        # Save
        output_path = Path("data/processed/workflow_analysis.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved: {output_path}")
    else:
        print("❌ Issues file not found!")
