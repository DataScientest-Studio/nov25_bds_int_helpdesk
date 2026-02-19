"""
E – Operations
E1: Communication Analysis | E2: Dialog Acts | E3: Process Compliance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Import components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Operations", page_icon="💼", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ─── Cache functions ─────────────────────────────────────────────────────────

@st.cache_data
def load_nlp_data():
    """E1: NLP features."""
    nlp_path = PROJECT_ROOT / "data" / "processed" / "nlp_features.csv"
    if nlp_path.exists():
        return pd.read_csv(nlp_path)
    return None


@st.cache_data
def load_scored_data():
    """E1: Scored raw data (Excel)."""
    data_path = PROJECT_ROOT / "data" / "raw" / "issues_snapshot_sample.xlsx"
    if data_path.exists():
        return pd.read_excel(data_path)
    return None


@st.cache_data
def load_dialog_data():
    """E2: Dialog acts data."""
    path = PROJECT_ROOT / "data" / "processed" / "dialog_acts.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data
def load_workflow_data():
    """E3: Workflow analysis."""
    path = PROJECT_ROOT / "data" / "processed" / "workflow_analysis.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


# ─── Page Header ────────────────────────────────────────────────────────────
page_header(e("💼 ") + "Operations – Communication, Dialog & Compliance", help_key='nlp')


# ════════════════════════════════════════════════════════════════════════════
# E1 – Communication Analysis
# ════════════════════════════════════════════════════════════════════════════
st.header(get_text('communication_analysis'))

section_header(e("💬 ") + get_text('communication_subtitle'))

nlp_df = load_nlp_data()
scored_df = load_scored_data()

if nlp_df is None:
    st.warning(e("⚠️ ") + get_text('nlp_not_found'))
else:
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(e("📝 ") + get_text('analyzed_issues'), len(nlp_df))
    with col2:
        avg_sentiment = nlp_df['sentiment_compound_mean'].mean()
        sentiment_label = get_text('positive') if avg_sentiment > 0.1 else get_text('neutral') if avg_sentiment > -0.1 else get_text('negative')
        st.metric(e("😊 ") + get_text('avg_sentiment'), f"{avg_sentiment:.3f}", sentiment_label)
    with col3:
        if 'politeness_score_sum' in nlp_df.columns:
            avg_polite = nlp_df['politeness_score_sum'].mean()
            st.metric(e("🙏 ") + get_text('avg_politeness'), f"{avg_polite:.1f}")
        else:
            st.metric(e("🙏 ") + get_text('avg_politeness'), "N/A")
    with col4:
        if 'word_count_sum' in nlp_df.columns:
            avg_words = nlp_df['word_count_sum'].mean()
            st.metric(e("📖 ") + get_text('avg_words'), f"{avg_words:.0f}")
        else:
            st.metric(e("📖 ") + get_text('avg_words'), "N/A")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        section_header(e("📊 ") + get_text('sentiment_distribution'), 'sentiment')
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=nlp_df['sentiment_compound_mean'], nbinsx=30, marker_color='steelblue'))
        fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text=get_text('neutral'))
        fig.update_layout(xaxis_title=get_text('sentiment_score'),
                          yaxis_title=get_text('issues_count'), height=350)
        st.plotly_chart(fig, width="stretch")

        complaints_label = "Complaints" if st.session_state.get('language') == 'en' else "Beschwerden"
        factual_label = "Factual" if st.session_state.get('language') == 'en' else "Sachlich"
        friendly_label = "Friendly" if st.session_state.get('language') == 'en' else "Freundlich"

        st.markdown(f"""
- **< -0.1**: {get_text('negative')} ({complaints_label})
- **-0.1 to 0.1**: {get_text('neutral')} ({factual_label})
- **> 0.1**: {get_text('positive')} ({friendly_label}, {get_text('solution_oriented')})
""")

    with col2:
        section_header(e("📈 ") + get_text('communication_patterns'), 'patterns')
        patterns = {
            get_text('politeness'): nlp_df['politeness_score_sum'].mean() if 'politeness_score_sum' in nlp_df.columns else 0,
            get_text('urgency'): nlp_df['urgency_score_sum'].mean() if 'urgency_score_sum' in nlp_df.columns else 0,
            get_text('technical'): nlp_df['technical_score_sum'].mean() if 'technical_score_sum' in nlp_df.columns else 0,
            get_text('solution_oriented'): nlp_df['solution_score_sum'].mean() if 'solution_score_sum' in nlp_df.columns else 0,
        }
        fig = go.Figure(data=[go.Bar(
            x=list(patterns.keys()), y=list(patterns.values()),
            marker_color=['green', 'orange', 'blue', 'purple']
        )])
        fig.update_layout(xaxis_title=get_text('pattern'),
                          yaxis_title=get_text('avg_score_per_issue'), height=350)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    section_header(e("🔗 ") + get_text('sentiment_vs_performance'))

    if scored_df is not None and 'id' in scored_df.columns:
        merged_e1 = nlp_df.merge(
            scored_df[['id', 'Q1', 'Q2', 'Q3', 'assignee']].rename(columns={'id': 'issueid'}),
            on='issueid', how='inner'
        )

        if len(merged_e1) > 0:
            import numpy as np
            from scipy import stats

            valid_data_e1 = merged_e1[merged_e1['Q1'] > 0].copy()
            fig = go.Figure()
            colors_e1 = {1: '#d73027', 2: '#fc8d59', 3: '#fee08b', 4: '#91cf60', 5: '#1a9850'}
            x_range_e1 = np.linspace(-1, 1, 200)

            for score in sorted(valid_data_e1['Q1'].unique()):
                score_data = valid_data_e1[valid_data_e1['Q1'] == score]['sentiment_compound_mean'].dropna()
                if len(score_data) > 2:
                    kde = stats.gaussian_kde(score_data)
                    y_kde = kde(x_range_e1)
                    fig.add_trace(go.Scatter(
                        x=x_range_e1, y=y_kde, mode='lines',
                        name=f'Score {score}',
                        line=dict(color=colors_e1.get(score, '#888'), width=2.5)
                    ))

            fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text=get_text('neutral'))
            fig.update_layout(
                title=get_text('sentiment_density'),
                xaxis_title=get_text('sentiment') + " (-1 to +1)",
                yaxis_title=get_text('density'), height=450, legend_title="Q1 Score"
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(get_text('no_overlap'))
    else:
        st.info(get_text('scored_not_available'))

    st.markdown("---")

    section_header(e("📋 ") + get_text('extreme_cases'))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{e('🔝')} {get_text('most_positive')}:**")
        top_positive = nlp_df.nlargest(5, 'sentiment_compound_mean')[['issueid', 'sentiment_compound_mean']]
        top_positive.columns = ['Issue ID', get_text('sentiment')]
        st.dataframe(top_positive, width="stretch")
    with col2:
        st.markdown(f"**{e('🔻')} {get_text('most_negative')}:**")
        top_negative = nlp_df.nsmallest(5, 'sentiment_compound_mean')[['issueid', 'sentiment_compound_mean']]
        top_negative.columns = ['Issue ID', get_text('sentiment')]
        st.dataframe(top_negative, width="stretch")


# ════════════════════════════════════════════════════════════════════════════
# E2 – Dialog Acts
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(get_text('dialog_analysis'))

section_header(e("💭 ") + get_text('dialog_subtitle'))

df_e2 = load_dialog_data()

if df_e2.empty:
    st.warning(e("⚠️ ") + get_text('no_dialog_data'))
    st.code("python src/features/dialog_acts.py")
else:
    def get_dialog_acts():
        return {
            'QUESTION': (e('❓'), get_text('dialog_question'), get_text('dialog_question_desc')),
            'ANSWER': (e('💡'), get_text('dialog_answer'), get_text('dialog_answer_desc')),
            'GREETING': (e('👋'), get_text('dialog_greeting'), get_text('dialog_greeting_desc')),
            'COMPLAINT': (e('😤'), get_text('dialog_complaint'), get_text('dialog_complaint_desc')),
            'THANKS': (e('🙏'), get_text('dialog_thanks'), get_text('dialog_thanks_desc')),
            'APOLOGY': (e('🙇'), get_text('dialog_apology'), get_text('dialog_apology_desc')),
            'REQUEST': (e('📝'), get_text('dialog_request'), get_text('dialog_request_desc')),
            'INFORM': (e('ℹ️'), get_text('dialog_inform'), get_text('dialog_inform_desc')),
            'CONFIRM': (e('✅'), get_text('dialog_confirm'), get_text('dialog_confirm_desc')),
            'REJECT': (e('❌'), get_text('dialog_reject'), get_text('dialog_reject_desc')),
            'PROMISE': (e('🤝'), get_text('dialog_promise'), get_text('dialog_promise_desc')),
            'OTHER': (e('📄'), get_text('dialog_other'), get_text('dialog_other_desc'))
        }

    DIALOG_ACTS = get_dialog_acts()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(e("💬 ") + get_text('total_comments'), f"{len(df_e2):,}")
    with col2:
        classified_e2 = df_e2[df_e2['dialog_act'] != 'OTHER'].shape[0]
        pct_e2 = classified_e2 / len(df_e2) * 100
        st.metric(e("✅ ") + get_text('classified'), f"{classified_e2:,}", f"{pct_e2:.1f}%")
    with col3:
        avg_conf_e2 = df_e2['dialog_confidence'].mean()
        st.metric(e("🎯 ") + get_text('avg_confidence'), f"{avg_conf_e2:.2f}")
    with col4:
        unique_issues_e2 = df_e2['issueid'].nunique()
        st.metric(e("🎫 ") + get_text('tickets'), f"{unique_issues_e2:,}")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        e("📊 ") + get_text('distribution'),
        e("🔍 ") + get_text('details'),
        e("📈 ") + get_text('insights')
    ])

    with tab1:
        section_header(e("📊 ") + get_text('dialog_act_distribution'), 'dialog_dist')
        distribution_e2 = df_e2['dialog_act'].value_counts()
        fig = px.pie(
            values=distribution_e2.values,
            names=[DIALOG_ACTS.get(act, ('', act, ''))[1] for act in distribution_e2.index],
            title=get_text('communication_types_dist'), hole=0.4
        )
        fig.update_layout(height=450, showlegend=True,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        st.plotly_chart(fig, width="stretch")

    with tab2:
        section_header(e("🔍 ") + get_text('examples_per_dialog_act'), 'dialog_examples')
        selected_act_e2 = st.selectbox(
            get_text('select_dialog_act') + ":", options=df_e2['dialog_act'].unique(),
            format_func=lambda x: f"{DIALOG_ACTS.get(x, ('', x, ''))[0]} {DIALOG_ACTS.get(x, ('', x, ''))[1]}",
            key="e2_act_select"
        )
        filtered_e2 = df_e2[df_e2['dialog_act'] == selected_act_e2]
        col1, col2 = st.columns(2)
        with col1:
            st.metric(get_text('count'), f"{len(filtered_e2):,}")
        with col2:
            st.metric(get_text('avg_confidence'), f"{filtered_e2['dialog_confidence'].mean():.2f}")

        st.markdown(f"### {get_text('example_comments')}")
        examples_e2 = filtered_e2.nlargest(10, 'dialog_confidence')
        for i, row in examples_e2.iterrows():
            text = str(row.get('body', ''))[:200]
            conf = row['dialog_confidence']
            with st.expander(f"{get_text('confidence')}: {conf:.2f} | {text[:50]}..."):
                st.write(text)
                st.caption(f"{get_text('issue')}: {row.get('issueid', 'N/A')} | {get_text('author')}: {row.get('author', 'N/A')}")

    with tab3:
        section_header(e("📈 ") + get_text('communication_insights'), 'dialog_insights')

        positive_acts_e2 = ['GREETING', 'THANKS', 'APOLOGY', 'CONFIRM', 'PROMISE']
        negative_acts_e2 = ['COMPLAINT', 'REJECT']
        positive_count_e2 = df_e2[df_e2['dialog_act'].isin(positive_acts_e2)].shape[0]
        negative_count_e2 = df_e2[df_e2['dialog_act'].isin(negative_acts_e2)].shape[0]
        total_classified_e2 = positive_count_e2 + negative_count_e2
        positivity_ratio_e2 = positive_count_e2 / total_classified_e2 if total_classified_e2 > 0 else 0.5

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(e("✅ ") + get_text('positive_communication'), f"{positive_count_e2:,}")
            st.caption(f"{get_text('dialog_greeting')}, {get_text('dialog_thanks')}, {get_text('dialog_apology')}, {get_text('dialog_confirm')}, {get_text('dialog_promise')}")
        with col2:
            st.metric(e("⚠️ ") + get_text('negative_communication'), f"{negative_count_e2:,}")
            st.caption(f"{get_text('dialog_complaint')}, {get_text('dialog_reject')}")
        with col3:
            st.metric(e("📊 ") + get_text('positivity_ratio'), f"{positivity_ratio_e2*100:.1f}%")
            if positivity_ratio_e2 > 0.7:
                st.success(get_text('mostly_positive'))
            elif positivity_ratio_e2 > 0.5:
                st.info(get_text('balanced_communication'))
            else:
                st.warning(get_text('more_negative'))

        st.markdown("---")
        section_header(e("❓ ") + get_text('qa_analysis'))

        questions_e2 = df_e2[df_e2['dialog_act'] == 'QUESTION'].shape[0]
        answers_e2 = df_e2[df_e2['dialog_act'] == 'ANSWER'].shape[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(e("❓ ") + get_text('questions'), f"{questions_e2:,}")
        with col2:
            st.metric(e("💡 ") + get_text('answers'), f"{answers_e2:,}")
        with col3:
            if questions_e2 > 0:
                qa_ratio_e2 = answers_e2 / questions_e2
                st.metric(get_text('answer_question_ratio'), f"{qa_ratio_e2:.2f}")
                if qa_ratio_e2 >= 1:
                    st.success(get_text('all_questions_answered'))
                else:
                    st.warning(f"{qa_ratio_e2*100:.0f}% {get_text('questions_answered_pct')}")

        st.markdown("---")
        section_header(e("🎯 ") + get_text('service_quality'))

        complaints_e2 = df_e2[df_e2['dialog_act'] == 'COMPLAINT'].shape[0]
        apologies_e2 = df_e2[df_e2['dialog_act'] == 'APOLOGY'].shape[0]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### {e('😤')} {get_text('complaints')}")
            st.metric(get_text('count'), f"{complaints_e2:,}")
            pct_complaints = complaints_e2 / len(df_e2) * 100
            if pct_complaints > 15:
                st.error(e("⚠️ ") + f"{get_text('high_complaint_rate')}: {pct_complaints:.1f}%")
            elif pct_complaints > 10:
                st.warning(f"{get_text('moderate_complaint_rate')}: {pct_complaints:.1f}%")
            else:
                st.success(f"{get_text('low_complaint_rate')}: {pct_complaints:.1f}%")
        with col2:
            st.markdown(f"### {e('🙇')} {get_text('apologies')}")
            st.metric(get_text('count'), f"{apologies_e2:,}")
            if complaints_e2 > 0:
                apology_rate_e2 = apologies_e2 / complaints_e2 * 100
                st.metric(get_text('per_complaint'), f"{apology_rate_e2:.1f}%")
                if apology_rate_e2 > 50:
                    st.success(get_text('good_complaint_response'))
                else:
                    st.info(get_text('more_apologies_help'))


# ════════════════════════════════════════════════════════════════════════════
# E3 – Process Compliance
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header(get_text('process_compliance'))

section_header(e("🔄 ") + get_text('compliance_subtitle'))

workflow_df = load_workflow_data()

if workflow_df is None:
    st.warning(e("⚠️ ") + get_text('workflow_not_found'))
else:
    # KPIs
    total_e3 = len(workflow_df)
    compliant_e3 = workflow_df['is_compliant'].sum()
    compliance_rate_e3 = compliant_e3 / total_e3 * 100
    avg_score_e3 = workflow_df['compliance_score'].mean()
    reopen_rate_e3 = (workflow_df['reopens'] > 0).mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(e("📋 ") + get_text('total_issues'), f"{total_e3:,}")
    with col2:
        st.metric(e("✅ ") + get_text('compliance_rate'), f"{compliance_rate_e3:.1f}%",
                  delta=f"{compliance_rate_e3 - 80:.1f}% {get_text('vs_target')} (80%)")
    with col3:
        st.metric(e("📊 ") + get_text('avg_compliance_score'), f"{avg_score_e3:.3f}")
    with col4:
        st.metric(e("🔄 ") + get_text('reopen_rate'), f"{reopen_rate_e3:.1f}%",
                  delta=f"-{5 - reopen_rate_e3:.1f}% {get_text('vs_target')} (5%)" if reopen_rate_e3 < 5 else f"+{reopen_rate_e3 - 5:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        section_header(e("📊 ") + get_text('compliance_score_dist'), 'compliance_score')
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=workflow_df['compliance_score'], nbinsx=20, marker_color='steelblue'))
        fig.add_vline(x=0.8, line_dash="dash", line_color="orange",
                      annotation_text=get_text('threshold') + " (0.8)")
        fig.update_layout(xaxis_title="Compliance Score", yaxis_title=get_text('issues_count'), height=350)
        st.plotly_chart(fig, width="stretch")

    with col2:
        section_header(e("🔄 ") + get_text('reopens_per_issue'), 'reopens')
        reopen_dist_e3 = workflow_df['reopens'].value_counts().sort_index().head(10)
        fig = go.Figure(data=[go.Bar(
            x=reopen_dist_e3.index.astype(str),
            y=reopen_dist_e3.values,
            marker_color=['green' if i == 0 else 'orange' if i == 1 else 'red' for i in reopen_dist_e3.index]
        )])
        fig.update_layout(xaxis_title=get_text('reopens_count'), yaxis_title=get_text('issues_count'), height=350)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

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

    valid_process_e3 = get_text('valid_process')
    problematic_e3 = get_text('problematic')
    st.markdown(f"""
**{valid_process_e3}:**
1. Open → In Progress → Resolved → Closed {e('✅')}
2. Open → In Progress → Waiting → Resolved → Closed {e('✅')}

**{problematic_e3}:**
- {get_text('multiple_reopens')} {e('⚠️')}
- {get_text('direct_jump')} {e('⚠️')}
""")

    st.markdown("---")

    section_header(e("⚠️ ") + get_text('issues_with_problems'))

    col1, col2, col3 = st.columns(3)
    with col1:
        min_reopens_e3 = st.slider(get_text('min_reopens'), 0, 10, 0, key="e3_filter_reopens")
    with col2:
        max_compliance_e3 = st.slider(get_text('max_compliance'), 0.0, 1.0, 1.0, step=0.05, key="e3_filter_compliance")
    with col3:
        filter_mode_e3 = st.radio(get_text('connection'), [get_text('or'), get_text('and')],
                                   horizontal=True, key="e3_filter_mode")

    if filter_mode_e3 == get_text('and'):
        problem_issues_e3 = workflow_df[
            (workflow_df['reopens'] >= min_reopens_e3) &
            (workflow_df['compliance_score'] <= max_compliance_e3)
        ]
    else:
        problem_issues_e3 = workflow_df[
            (workflow_df['reopens'] >= min_reopens_e3) |
            (workflow_df['compliance_score'] <= max_compliance_e3)
        ]

    problem_issues_e3 = problem_issues_e3.sort_values('compliance_score')
    st.info(f"{e('🔍')} Reopens ≥ {min_reopens_e3} **{filter_mode_e3}** Compliance ≤ {max_compliance_e3:.2f} → **{len(problem_issues_e3):,}** Issues")

    if len(problem_issues_e3) > 0:
        display_e3 = problem_issues_e3.head(50)[['issue_id', 'total_steps', 'reopens',
                                                  'backward_indicators', 'compliance_score']].copy()
        display_e3['compliance_score'] = display_e3['compliance_score'].apply(lambda x: f"{x:.2f}")
        st.dataframe(
            display_e3, width="stretch",
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
