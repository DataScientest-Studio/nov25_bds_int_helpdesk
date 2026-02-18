"""
Process Compliance
Workflow analysis and process violations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Process Compliance", page_icon="🔄", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Page header
page_header(
    e("🔄 ") + get_text('process_compliance'),
    get_text('compliance_subtitle'),
    help_key='compliance'
)

# Load data
@st.cache_data
def load_workflow_data():
    path = Path(__file__).parent.parent.parent / "data" / "processed" / "workflow_analysis.csv"
    if path.exists():
        return pd.read_csv(path)
    return None

workflow_df = load_workflow_data()

if workflow_df is None:
    st.warning(e("⚠️ ") + get_text('workflow_not_found'))
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)

total = len(workflow_df)
compliant = workflow_df['is_compliant'].sum()
compliance_rate = compliant / total * 100
avg_score = workflow_df['compliance_score'].mean()
reopen_rate = (workflow_df['reopens'] > 0).mean() * 100

with col1:
    st.metric(e("📋 ") + get_text('total_issues'), f"{total:,}")

with col2:
    st.metric(e("✅ ") + get_text('compliance_rate'), f"{compliance_rate:.1f}%", 
              delta=f"{compliance_rate - 80:.1f}% {get_text('vs_target')} (80%)")

with col3:
    st.metric(e("📊 ") + get_text('avg_compliance_score'), f"{avg_score:.3f}")

with col4:
    st.metric(e("🔄 ") + get_text('reopen_rate'), f"{reopen_rate:.1f}%",
              delta=f"-{5 - reopen_rate:.1f}% {get_text('vs_target')} (5%)" if reopen_rate < 5 else f"+{reopen_rate - 5:.1f}%")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    section_header(e("📊 ") + get_text('compliance_score_dist'), 'compliance_score')
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=workflow_df['compliance_score'],
        nbinsx=20,
        marker_color='steelblue'
    ))
    threshold_text = get_text('threshold') + " (0.8)"
    fig.add_vline(x=0.8, line_dash="dash", line_color="orange", 
                  annotation_text=threshold_text)
    fig.update_layout(
        xaxis_title="Compliance Score",
        yaxis_title=get_text('issues_count'),
        height=350
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    section_header(e("🔄 ") + get_text('reopens_per_issue'), 'reopens')
    
    reopen_dist = workflow_df['reopens'].value_counts().sort_index().head(10)
    
    fig = go.Figure(data=[go.Bar(
        x=reopen_dist.index.astype(str),
        y=reopen_dist.values,
        marker_color=['green' if i == 0 else 'orange' if i == 1 else 'red' 
                      for i in reopen_dist.index]
    )])
    fig.update_layout(
        xaxis_title=get_text('reopens_count'),
        yaxis_title=get_text('issues_count'),
        height=350
    )
    st.plotly_chart(fig, width="stretch")

st.markdown("---")

# Process Flow Visualization
section_header(e("📈 ") + get_text('expected_process'))

st.markdown("""
```
┌───────┐     ┌─────────────┐     ┌─────────┐     ┌────────┐     ┌────────┐
│ Open  │ ──▶ │ In Progress │ ──▶ │ Waiting │ ──▶ │Resolved│ ──▶ │ Closed │
└───────┘     └─────────────┘     └─────────┘     └────────┘     └────────┘
                    │                   │              │
                    │                   └──────────────┤
                    │                                  │
                    ◀──────────────────────────────────┘
                          (Reopen/Rework)
```
""")

valid_process = get_text('valid_process')
problematic = get_text('problematic')

st.markdown(f"""
**{valid_process}:**
1. Open → In Progress → Resolved → Closed {e('✅')}
2. Open → In Progress → Waiting → Resolved → Closed {e('✅')}

**{problematic}:**
- {get_text('multiple_reopens')} {e('⚠️')}
- {get_text('direct_jump')} {e('⚠️')}
""")

st.markdown("---")

# Problem Issues
section_header(e("⚠️ ") + get_text('issues_with_problems'))

# Filter
col1, col2, col3 = st.columns(3)
with col1:
    min_reopens = st.slider(get_text('min_reopens'), 0, 10, 0, key="filter_reopens")
with col2:
    max_compliance = st.slider(get_text('max_compliance'), 0.0, 1.0, 1.0, step=0.05, key="filter_compliance")
with col3:
    filter_mode = st.radio(get_text('connection'), [get_text('or'), get_text('and')], horizontal=True)

# Apply filter
if filter_mode == get_text('and'):
    problem_issues = workflow_df[
        (workflow_df['reopens'] >= min_reopens) & 
        (workflow_df['compliance_score'] <= max_compliance)
    ]
else:  # OR
    problem_issues = workflow_df[
        (workflow_df['reopens'] >= min_reopens) | 
        (workflow_df['compliance_score'] <= max_compliance)
    ]

problem_issues = problem_issues.sort_values('compliance_score')

st.info(f"{e('🔍')} Reopens ≥ {min_reopens} **{filter_mode}** Compliance ≤ {max_compliance:.2f} → **{len(problem_issues):,}** Issues")

if len(problem_issues) > 0:
    display_df = problem_issues.head(50)[['issue_id', 'total_steps', 'reopens', 
                                          'backward_indicators', 'compliance_score']].copy()
    display_df['compliance_score'] = display_df['compliance_score'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        display_df,
        width="stretch",
        column_config={
            'issue_id': st.column_config.TextColumn("Issue ID"),
            'total_steps': st.column_config.NumberColumn(get_text('steps')),
            'reopens': st.column_config.NumberColumn("Reopens"),
            'backward_indicators': st.column_config.NumberColumn(get_text('backward_indicators')),
            'compliance_score': st.column_config.TextColumn("Compliance Score"),
        }
    )
else:
    st.success(e("✅ ") + get_text('no_issues_found'))

st.markdown("---")

# Recommendations
section_header(e("💡 ") + get_text('process_improvement'))

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    ### {get_text('high_reopen_rate')}:
    1. **{get_text('root_cause_patterns')}**
    2. **{get_text('quality_checks')}**
    3. **{get_text('customer_feedback')}**
    4. **{get_text('definition_of_done')}**
    """)

with col2:
    st.markdown(f"""
    ### {get_text('low_compliance')}:
    1. **{get_text('process_training')}**
    2. **{get_text('automatic_validation')}**
    3. **{get_text('regular_audits')}**
    4. **{get_text('gamification')}**
    """)

# Footer
render_footer()
