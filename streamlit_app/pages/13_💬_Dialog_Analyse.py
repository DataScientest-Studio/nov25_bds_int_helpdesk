"""
Dialog Analysis (Advanced NLP)
Classifies communication types in ticket comments.
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

st.set_page_config(page_title="Dialog Analysis", page_icon="💬", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Page header
page_header(
    e("💬 ") + get_text('dialog_analysis'),
    get_text('dialog_subtitle'),
    help_key='dialog'
)

# Load data
@st.cache_data
def load_dialog_data():
    path = Path(__file__).parent.parent.parent / "data" / "processed" / "dialog_acts.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_dialog_data()

if df.empty:
    st.warning(e("⚠️ ") + get_text('no_dialog_data'))
    st.code("python src/features/dialog_acts.py")
    st.stop()

# Dialog Act Descriptions (with translations)
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
    st.metric(e("💬 ") + get_text('total_comments'), f"{len(df):,}")

with col2:
    classified = df[df['dialog_act'] != 'OTHER'].shape[0]
    pct = classified / len(df) * 100
    st.metric(e("✅ ") + get_text('classified'), f"{classified:,}", f"{pct:.1f}%")

with col3:
    avg_conf = df['dialog_confidence'].mean()
    st.metric(e("🎯 ") + get_text('avg_confidence'), f"{avg_conf:.2f}")

with col4:
    unique_issues = df['issueid'].nunique()
    st.metric(e("🎫 ") + get_text('tickets'), f"{unique_issues:,}")

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs([
    e("📊 ") + get_text('distribution'), 
    e("🔍 ") + get_text('details'), 
    e("📈 ") + get_text('insights')
])

with tab1:
    section_header(e("📊 ") + get_text('dialog_act_distribution'), 'dialog_dist')
    
    # Calculate distribution
    distribution = df['dialog_act'].value_counts()
    
    # Pie Chart (full width, no separate legend)
    fig = px.pie(
        values=distribution.values,
        names=[DIALOG_ACTS.get(act, ('', act, ''))[1] for act in distribution.index],
        title=get_text('communication_types_dist'),
        hole=0.4
    )
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Bar Chart
    section_header(e("📊 ") + get_text('detailed_distribution'))
    
    dist_df = pd.DataFrame({
        'Dialog Act': [DIALOG_ACTS.get(act, ('', act, ''))[1] for act in distribution.index],
        get_text('count'): distribution.values,
        'Percent': (distribution.values / len(df) * 100).round(1)
    })
    
    fig = px.bar(
        dist_df,
        x='Dialog Act',
        y=get_text('count'),
        text='Percent',
        title=get_text('count_per_dialog_act'),
        color=get_text('count'),
        color_continuous_scale='Blues'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    section_header(e("🔍 ") + get_text('examples_per_dialog_act'), 'dialog_examples')
    
    # Select Dialog Act
    selected_act = st.selectbox(
        get_text('select_dialog_act') + ":",
        options=df['dialog_act'].unique(),
        format_func=lambda x: f"{DIALOG_ACTS.get(x, ('', x, ''))[0]} {DIALOG_ACTS.get(x, ('', x, ''))[1]}"
    )
    
    # Filter
    filtered = df[df['dialog_act'] == selected_act]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(get_text('count'), f"{len(filtered):,}")
    with col2:
        st.metric(get_text('avg_confidence'), f"{filtered['dialog_confidence'].mean():.2f}")
    
    # Show examples
    st.markdown(f"### {get_text('example_comments')}")
    
    # Sort by confidence
    examples = filtered.nlargest(10, 'dialog_confidence')
    
    for i, row in examples.iterrows():
        text = str(row.get('body', ''))[:200]
        conf = row['dialog_confidence']
        
        with st.expander(f"{get_text('confidence')}: {conf:.2f} | {text[:50]}..."):
            st.write(text)
            st.caption(f"{get_text('issue')}: {row.get('issueid', 'N/A')} | {get_text('author')}: {row.get('author', 'N/A')}")

with tab3:
    section_header(e("📈 ") + get_text('communication_insights'), 'dialog_insights')
    
    # Calculate professionalism
    positive_acts = ['GREETING', 'THANKS', 'APOLOGY', 'CONFIRM', 'PROMISE']
    negative_acts = ['COMPLAINT', 'REJECT']
    
    positive_count = df[df['dialog_act'].isin(positive_acts)].shape[0]
    negative_count = df[df['dialog_act'].isin(negative_acts)].shape[0]
    
    total_classified = positive_count + negative_count
    if total_classified > 0:
        positivity_ratio = positive_count / total_classified
    else:
        positivity_ratio = 0.5
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(e("✅ ") + get_text('positive_communication'), f"{positive_count:,}")
        st.caption(f"{get_text('dialog_greeting')}, {get_text('dialog_thanks')}, {get_text('dialog_apology')}, {get_text('dialog_confirm')}, {get_text('dialog_promise')}")
    
    with col2:
        st.metric(e("⚠️ ") + get_text('negative_communication'), f"{negative_count:,}")
        st.caption(f"{get_text('dialog_complaint')}, {get_text('dialog_reject')}")
    
    with col3:
        st.metric(e("📊 ") + get_text('positivity_ratio'), f"{positivity_ratio*100:.1f}%")
        if positivity_ratio > 0.7:
            st.success(get_text('mostly_positive'))
        elif positivity_ratio > 0.5:
            st.info(get_text('balanced_communication'))
        else:
            st.warning(get_text('more_negative'))
    
    st.markdown("---")
    
    # Question-Answer Analysis
    section_header(e("❓ ") + get_text('qa_analysis'))
    
    questions = df[df['dialog_act'] == 'QUESTION'].shape[0]
    answers = df[df['dialog_act'] == 'ANSWER'].shape[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(e("❓ ") + get_text('questions'), f"{questions:,}")
    
    with col2:
        st.metric(e("💡 ") + get_text('answers'), f"{answers:,}")
    
    with col3:
        if questions > 0:
            qa_ratio = answers / questions
            st.metric(get_text('answer_question_ratio'), f"{qa_ratio:.2f}")
            if qa_ratio >= 1:
                st.success(get_text('all_questions_answered'))
            else:
                st.warning(f"{qa_ratio*100:.0f}% {get_text('questions_answered_pct')}")
    
    st.markdown("---")
    
    # Service Quality
    section_header(e("🎯 ") + get_text('service_quality'))
    
    # Complaints vs Apologies
    complaints = df[df['dialog_act'] == 'COMPLAINT'].shape[0]
    apologies = df[df['dialog_act'] == 'APOLOGY'].shape[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {e('😤')} {get_text('complaints')}")
        st.metric(get_text('count'), f"{complaints:,}")
        pct = complaints / len(df) * 100
        if pct > 15:
            st.error(e("⚠️ ") + f"{get_text('high_complaint_rate')}: {pct:.1f}%")
        elif pct > 10:
            st.warning(f"{get_text('moderate_complaint_rate')}: {pct:.1f}%")
        else:
            st.success(f"{get_text('low_complaint_rate')}: {pct:.1f}%")
    
    with col2:
        st.markdown(f"### {e('🙇')} {get_text('apologies')}")
        st.metric(get_text('count'), f"{apologies:,}")
        if complaints > 0:
            apology_rate = apologies / complaints * 100
            st.metric(get_text('per_complaint'), f"{apology_rate:.1f}%")
            if apology_rate > 50:
                st.success(get_text('good_complaint_response'))
            else:
                st.info(get_text('more_apologies_help'))

# Footer
render_footer()
