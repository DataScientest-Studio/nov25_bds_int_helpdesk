"""
Data Inventory - Overview of all datasets
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import settings
try:
    from components.settings import (
        render_navigation,
        init_session_state, render_settings_sidebar, render_footer,
        get_text, section_header, page_header, e
    )
except ImportError:
    # Fallback
    def init_session_state(): pass
    def render_settings_sidebar(): pass
    def render_footer(): pass
    def get_text(key): return key
    def section_header(text, key=None): st.subheader(text)
    def page_header(text, subtitle=None, help_key=None): st.title(text)
    def e(text): return text

# Page Config
st.set_page_config(
    page_title="Data Inventory",
    page_icon="📊",
    layout="wide"
)

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"


def get_dataset_definitions():
    """Get dataset definitions with translations."""
    return {
        'issues': {
            'file': 'issues.csv',
            'name': 'Issues',
            'description': get_text('issues') + ' - ' + (
                'Main dataset with all helpdesk tickets' if st.session_state.get('language') == 'en' 
                else 'Hauptdatensatz mit allen Helpdesk-Tickets'
            ),
            'key_columns': ['id', 'issue_assignee', 'issue_priority', 'issue_status', 'wf_total_time']
        },
        'snapshots': {
            'file': 'issues_snapshot.csv',
            'name': 'Issues Snapshots',
            'description': 'Snapshots ' + (
                'of issues at different points in time' if st.session_state.get('language') == 'en'
                else 'der Issues zu verschiedenen Zeitpunkten'
            ),
            'key_columns': ['id', 'issue_assignee', 'turn', 'wf_total_time']
        },
        'history': {
            'file': 'issues_change_history.csv',
            'name': 'Change History',
            'description': (
                'Change history (status changes) of all issues' if st.session_state.get('language') == 'en'
                else 'Änderungshistorie (Statuswechsel) aller Issues'
            ),
            'key_columns': ['id', 'issueid', 'field', 'value', 'created']
        },
        'scored': {
            'file': 'issues_snapshot_sample.xlsx',
            'name': get_text('scored_samples') + ' (Ground Truth)',
            'description': (
                'Manually scored samples with Q1, Q2, Q3 scores' if st.session_state.get('language') == 'en'
                else 'Manuell bewertete Samples mit Q1, Q2, Q3 Scores'
            ),
            'key_columns': ['id', 'assignee', 'Q1', 'Q2', 'Q3', 'spent hours']
        },
        'utterances': {
            'file': 'sample_utterances.csv',
            'name': 'Utterances (' + get_text('comments') + ')',
            'description': (
                'Ticket comments for NLP analysis' if st.session_state.get('language') == 'en'
                else 'Ticket-Kommentare für NLP-Analyse'
            ),
            'key_columns': ['issueid', 'author', 'author_role', 'actionbody']
        }
    }


@st.cache_data
def load_dataset(filename):
    """Load a dataset."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return None
    
    if filename.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        return pd.read_csv(filepath)


def get_dtype_category(dtype):
    """Categorize data types."""
    dtype_str = str(dtype)
    if 'int' in dtype_str:
        return e('🔢 ') + 'Integer'
    elif 'float' in dtype_str:
        return e('📊 ') + 'Float'
    elif dtype_str == 'object':
        return e('📝 ') + 'Text/Object'
    elif 'bool' in dtype_str:
        return e('✅ ') + 'Boolean'
    elif 'datetime' in dtype_str:
        return e('📅 ') + 'Datetime'
    else:
        return f'{e("❓ ")}{dtype_str}'


def main():
    # Session State
    init_session_state()
    
    # Sidebar
    render_settings_sidebar()
    
    # Header
    page_header(
        e("📊 ") + get_text('data_inventory'),
        get_text('data_inventory_subtitle'),
        help_key='overview'
    )
    
    # Get dataset definitions
    DATASETS = get_dataset_definitions()
    
    # === OVERVIEW ===
    section_header(e("📋 ") + get_text('dataset_overview'), 'overview')
    
    # Summary Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_rows = 0
    loaded_datasets = {}
    
    for key, info in DATASETS.items():
        df = load_dataset(info['file'])
        if df is not None:
            loaded_datasets[key] = df
            total_rows += len(df)
    
    with col1:
        st.metric(
            label=get_text('datasets'),
            value=f"{len(loaded_datasets)}/5"
        )
    
    with col2:
        if 'issues' in loaded_datasets:
            st.metric(
                label=get_text('issues'),
                value=f"{len(loaded_datasets['issues']):,}"
            )
    
    with col3:
        if 'scored' in loaded_datasets:
            st.metric(
                label=get_text('scored_samples'),
                value=f"{len(loaded_datasets['scored']):,}"
            )
    
    with col4:
        if 'utterances' in loaded_datasets:
            st.metric(
                label=get_text('comments'),
                value=f"{len(loaded_datasets['utterances']):,}"
            )
    
    with col5:
        st.metric(
            label=get_text('total_rows'),
            value=f"{total_rows:,}"
        )
    
    st.markdown("---")
    
    # === DETAILS PER DATASET ===
    section_header(e("🔍 ") + get_text('dataset_details'), 'details')
    
    for key, info in DATASETS.items():
        with st.expander(f"📁 **{info['name']}** - {info['file']}", expanded=False):
            df = loaded_datasets.get(key)
            
            if df is None:
                st.error(f"❌ {get_text('file_not_found')}: {info['file']}")
                st.info(f"{get_text('expected_at')}: {DATA_DIR / info['file']}")
                continue
            
            # Description
            st.markdown(f"*{info['description']}*")
            
            # Basic statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(get_text('rows'), f"{len(df):,}")
            with col2:
                st.metric(get_text('columns'), f"{len(df.columns)}")
            with col3:
                memory_mb = df.memory_usage(deep=True).sum() / 1024**2
                st.metric(get_text('memory'), f"{memory_mb:.2f} MB")
            with col4:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric(get_text('missing'), f"{missing_pct:.1f}%")
            
            # Columns table
            st.markdown(f"**{get_text('columns')}:**")
            
            columns_info = []
            for col in df.columns:
                columns_info.append({
                    get_text('column'): col,
                    get_text('datatype'): get_dtype_category(df[col].dtype),
                    get_text('non_null'): f"{df[col].notna().sum():,}",
                    get_text('unique'): f"{df[col].nunique():,}",
                    get_text('example'): str(df[col].dropna().iloc[0])[:50] if df[col].notna().any() else 'N/A'
                })
            
            columns_df = pd.DataFrame(columns_info)
            st.dataframe(columns_df, use_container_width=True, hide_index=True)
            
            # Preview
            st.markdown(f"**{get_text('preview')}:**")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Key Columns
            st.markdown(f"**{get_text('important_columns')}:** `{'`, `'.join(info['key_columns'])}`")
    
    st.markdown("---")
    
    # === DATATYPE DISTRIBUTION ===
    section_header(e("📊 ") + get_text('datatype_distribution'), 'dtypes')
    
    all_dtypes = {'Integer': 0, 'Float': 0, 'Text/Object': 0, 'Boolean': 0, 'Datetime': 0, 'Other': 0}
    
    for key, df in loaded_datasets.items():
        for col in df.columns:
            dtype_str = str(df[col].dtype)
            if 'int' in dtype_str:
                all_dtypes['Integer'] += 1
            elif 'float' in dtype_str:
                all_dtypes['Float'] += 1
            elif dtype_str == 'object':
                all_dtypes['Text/Object'] += 1
            elif 'bool' in dtype_str:
                all_dtypes['Boolean'] += 1
            elif 'datetime' in dtype_str:
                all_dtypes['Datetime'] += 1
            else:
                all_dtypes['Other'] += 1
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        import plotly.express as px
        dtype_df = pd.DataFrame({
            get_text('type'): all_dtypes.keys(),
            get_text('count'): all_dtypes.values()
        })
        fig = px.bar(dtype_df, x=get_text('type'), y=get_text('count'), color=get_text('type'),
                     title=get_text('columns_by_type'))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(f"**{get_text('summary')}:**")
        for typ, count in all_dtypes.items():
            if count > 0:
                st.write(f"- {typ}: {count} {get_text('columns')}")
    
    st.markdown("---")
    
    # === DATA SOURCE ===
    section_header(e("📚 ") + get_text('data_source'), 'source')
    
    source_title = "Mendeley Dataset" if st.session_state.get('language') == 'en' else "Mendeley-Datensatz"
    source_desc = get_text('data_source_info')
    
    st.info(f"""
    **{source_title}**
    
    {source_desc}
    
    - **URL:** https://data.mendeley.com/datasets/btm76zndnt/2
    """)
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()
