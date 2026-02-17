"""
Data Inventory - Übersicht über alle Datensätze
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Projekt-Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Settings importieren
try:
    from components.settings import (
    render_navigation,
        init_session_state, render_settings_sidebar, render_footer,
        get_text, section_header, e
    )
except ImportError:
    # Fallback
    def init_session_state(): pass
    def render_settings_sidebar(): pass
    def render_footer(): pass
    def get_text(key): return key
    def section_header(text, key=None): st.subheader(text)
    def e(text): return text

# Page Config
st.set_page_config(
    page_title="Data Inventory",
    page_icon="📊",
    layout="wide"
)

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

# Dataset-Definitionen
DATASETS = {
    'issues': {
        'file': 'issues.csv',
        'name': 'Issues',
        'description': 'Hauptdatensatz mit allen Helpdesk-Tickets',
        'key_columns': ['id', 'issue_assignee', 'issue_priority', 'issue_status', 'wf_total_time']
    },
    'snapshots': {
        'file': 'issues_snapshot.csv',
        'name': 'Issues Snapshots',
        'description': 'Snapshots der Issues zu verschiedenen Zeitpunkten',
        'key_columns': ['id', 'issue_assignee', 'turn', 'wf_total_time']
    },
    'history': {
        'file': 'issues_change_history.csv',
        'name': 'Change History',
        'description': 'Änderungshistorie (Statuswechsel) aller Issues',
        'key_columns': ['id', 'issueid', 'field', 'value', 'created']
    },
    'scored': {
        'file': 'issues_snapshot_sample.xlsx',
        'name': 'Scored Samples (Ground Truth)',
        'description': 'Manuell bewertete Samples mit Q1, Q2, Q3 Scores',
        'key_columns': ['id', 'assignee', 'Q1', 'Q2', 'Q3', 'spent hours']
    },
    'utterances': {
        'file': 'sample_utterances.csv',
        'name': 'Utterances (Kommentare)',
        'description': 'Ticket-Kommentare für NLP-Analyse',
        'key_columns': ['issueid', 'author', 'author_role', 'actionbody']
    }
}


@st.cache_data
def load_dataset(filename):
    """Lädt einen Datensatz."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return None
    
    if filename.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        return pd.read_csv(filepath)


def get_dtype_category(dtype):
    """Kategorisiert Datentypen."""
    dtype_str = str(dtype)
    if 'int' in dtype_str:
        return '🔢 Integer'
    elif 'float' in dtype_str:
        return '📊 Float'
    elif dtype_str == 'object':
        return '📝 Text/Object'
    elif 'bool' in dtype_str:
        return '✅ Boolean'
    elif 'datetime' in dtype_str:
        return '📅 Datetime'
    else:
        return f'❓ {dtype_str}'


def main():
    # Session State
    init_session_state()
    
    # Sidebar
    render_settings_sidebar()
    
    # Header
    st.title(e("📊 ") + "Data Inventory")
    st.markdown("**Übersicht über alle Datensätze des Help Desk Performance Systems**")
    
    st.markdown("---")
    
    # === ÜBERSICHT ===
    section_header(e("📋 ") + "Datensatz-Übersicht", 'overview')
    
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
            label="Datensätze",
            value=f"{len(loaded_datasets)}/5"
        )
    
    with col2:
        if 'issues' in loaded_datasets:
            st.metric(
                label="Issues",
                value=f"{len(loaded_datasets['issues']):,}"
            )
    
    with col3:
        if 'scored' in loaded_datasets:
            st.metric(
                label="Bewertete Samples",
                value=f"{len(loaded_datasets['scored']):,}"
            )
    
    with col4:
        if 'utterances' in loaded_datasets:
            st.metric(
                label="Kommentare",
                value=f"{len(loaded_datasets['utterances']):,}"
            )
    
    with col5:
        st.metric(
            label="Gesamt Zeilen",
            value=f"{total_rows:,}"
        )
    
    st.markdown("---")
    
    # === DETAILS PRO DATENSATZ ===
    section_header(e("🔍 ") + "Datensatz-Details", 'details')
    
    for key, info in DATASETS.items():
        with st.expander(f"📁 **{info['name']}** - {info['file']}", expanded=False):
            df = loaded_datasets.get(key)
            
            if df is None:
                st.error(f"❌ Datei nicht gefunden: {info['file']}")
                st.info(f"Erwartet in: {DATA_DIR / info['file']}")
                continue
            
            # Beschreibung
            st.markdown(f"*{info['description']}*")
            
            # Basis-Statistiken
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Zeilen", f"{len(df):,}")
            with col2:
                st.metric("Spalten", f"{len(df.columns)}")
            with col3:
                memory_mb = df.memory_usage(deep=True).sum() / 1024**2
                st.metric("Speicher", f"{memory_mb:.2f} MB")
            with col4:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Fehlend", f"{missing_pct:.1f}%")
            
            # Spalten-Tabelle
            st.markdown("**Spalten:**")
            
            columns_info = []
            for col in df.columns:
                columns_info.append({
                    'Spalte': col,
                    'Datentyp': get_dtype_category(df[col].dtype),
                    'Nicht-Null': f"{df[col].notna().sum():,}",
                    'Unique': f"{df[col].nunique():,}",
                    'Beispiel': str(df[col].dropna().iloc[0])[:50] if df[col].notna().any() else 'N/A'
                })
            
            columns_df = pd.DataFrame(columns_info)
            st.dataframe(columns_df, use_container_width=True, hide_index=True)
            
            # Vorschau
            st.markdown("**Vorschau (erste 5 Zeilen):**")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Key Columns hervorheben
            st.markdown(f"**Wichtige Spalten:** `{'`, `'.join(info['key_columns'])}`")
    
    st.markdown("---")
    
    # === DATENTYPEN-ZUSAMMENFASSUNG ===
    section_header(e("📊 ") + "Datentypen-Verteilung", 'dtypes')
    
    all_dtypes = {'Integer': 0, 'Float': 0, 'Text/Object': 0, 'Boolean': 0, 'Datetime': 0, 'Andere': 0}
    
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
                all_dtypes['Andere'] += 1
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        import plotly.express as px
        dtype_df = pd.DataFrame({
            'Typ': all_dtypes.keys(),
            'Anzahl': all_dtypes.values()
        })
        fig = px.bar(dtype_df, x='Typ', y='Anzahl', color='Typ',
                     title='Spalten nach Datentyp')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Zusammenfassung:**")
        for typ, count in all_dtypes.items():
            if count > 0:
                st.write(f"- {typ}: {count} Spalten")
    
    st.markdown("---")
    
    # === DATENQUELLEN ===
    section_header(e("📚 ") + "Datenquelle", 'source')
    
    st.info("""
    **Mendeley Dataset**
    
    Die Daten stammen aus dem öffentlichen Mendeley-Datensatz:
    - **Titel:** Toward Performance Appraisal Automation
    - **URL:** https://data.mendeley.com/datasets/btm76zndnt/2
    
    Der Datensatz enthält anonymisierte Helpdesk-Ticket-Daten einer IT-Serviceorganisation.
    """)
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()
