"""
Export Center
All reports and data for download.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="Export Center", page_icon="📥", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Page header
page_header(
    e("📥 ") + get_text('export_center'),
    get_text('export_subtitle'),
    help_key='export'
)

# Load data
@st.cache_data
def load_all_data():
    data = {}
    
    paths = {
        'training': project_root / "reports" / "training_report.csv",
        'ml': project_root / "data" / "processed" / "ml_dataset.csv",
        'nlp': project_root / "data" / "processed" / "nlp_features.csv",
        'workflow': project_root / "data" / "processed" / "workflow_analysis.csv",
    }
    
    for name, path in paths.items():
        if path.exists():
            data[name] = pd.read_csv(path)
    
    return data

data = load_all_data()

# Tabs
tab1, tab2 = st.tabs([
    e("📊 ") + get_text('excel_csv'), 
    e("📄 ") + get_text('pdf_reports')
])

with tab1:
    section_header(e("📊 ") + "Excel & CSV Downloads", 'export_data')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {e('📋')} {get_text('training_report')}")
        if 'training' in data:
            df = data['training']
            st.write(f"**{len(df)} {get_text('employees')}** | {get_text('last_update')}: today")
            
            # CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                e("📥 ") + get_text('download_csv'),
                csv,
                file_name=f"training_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Excel Export (deaktiviert - Modul entfernt)
            st.info("Excel-Export wurde in der vereinfachten Version entfernt.")
        else:
            st.info(get_text('training_report') + " " + get_text('not_available'))
    
    with col2:
        st.markdown(f"### {e('📈')} {get_text('ml_dataset')}")
        if 'ml' in data:
            df = data['ml']
            st.write(f"**{len(df)} {get_text('samples')}** | {len(df.columns)} {get_text('features')}")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                e("📥 ") + f"{get_text('ml_dataset')} (CSV)",
                csv,
                file_name=f"ml_dataset_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(get_text('ml_dataset') + " " + get_text('not_available'))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {e('💬')} {get_text('nlp_features')}")
        if 'nlp' in data:
            df = data['nlp']
            st.write(f"**{len(df)} {get_text('entries')}** | {get_text('sentiment_analysis')}")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                e("📥 ") + f"{get_text('nlp_features')} (CSV)",
                csv,
                file_name=f"nlp_features_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(get_text('nlp_features') + " " + get_text('not_available'))
    
    with col2:
        st.markdown(f"### {e('🔄')} {get_text('workflow_analysis')}")
        if 'workflow' in data:
            df = data['workflow']
            st.write(f"**{len(df)} Issues** | {get_text('compliance_data')}")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                e("📥 ") + f"{get_text('workflow_analysis')} (CSV)",
                csv,
                file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(get_text('workflow_analysis') + " " + get_text('not_available'))

with tab2:
    section_header(e("📄 ") + get_text('pdf_reports'))
    
    # List existing PDFs
    export_dir = project_root / "reports" / "exports"
    
    if export_dir.exists():
        pdf_files = list(export_dir.glob("*.pdf"))
        
        if pdf_files:
            st.markdown(f"### {get_text('existing_reports')}")
            
            for pdf_path in sorted(pdf_files, reverse=True)[:10]:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"{e('📄')} {pdf_path.name}")
                
                with col2:
                    size_kb = pdf_path.stat().st_size / 1024
                    st.write(f"{size_kb:.1f} KB")
                
                with col3:
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            e("📥"),
                            f.read(),
                            file_name=pdf_path.name,
                            mime="application/pdf",
                            key=f"pdf_{pdf_path.name}"
                        )
        else:
            st.info(get_text('no_pdf_reports'))
        
        st.markdown("---")
        
        # PDF Reports - bereits generiert
        st.markdown(f"### {e('🆕')} PDF Reports")
        st.info("Die PDF-Dokumentation wurde bereits erstellt und liegt im reports/ Ordner.")
    else:
        st.info("Export directory not found.")

# Bulk Export
st.markdown("---")
section_header(e("📦 ") + get_text('bulk_export'))

if st.button(e("📦 ") + get_text('download_all_zip')):
    import zipfile
    
    # Create ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, df in data.items():
            csv_content = df.to_csv(index=False)
            zf.writestr(f"{name}.csv", csv_content)
    
    zip_buffer.seek(0)
    
    st.download_button(
        e("📥 ") + get_text('download_zip'),
        zip_buffer.getvalue(),
        file_name=f"all_data_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip"
    )

# Footer
render_footer()
