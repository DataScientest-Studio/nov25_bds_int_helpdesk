"""
Präsentation - Project Defense Slides
"""
import streamlit as st

st.set_page_config(
    page_title="Präsentation",
    page_icon="🎬",
    layout="wide"
)

from pathlib import Path
import base64
import os
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import init_session_state, get_text, e, render_settings_sidebar

init_session_state()
render_settings_sidebar()

# Paths
REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"
PPTX_FILE = REPORTS_DIR / "Datascientest_project_defense.pptx"
PDF_FILE = REPORTS_DIR / "Datascientest_project_defense.pdf"
SLIDES_DIR = REPORTS_DIR / "slides"

def convert_pdf_to_images():
    """Convert PDF to PNG images using pdf2image"""
    try:
        from pdf2image import convert_from_path
        
        if not PDF_FILE.exists():
            return None, "PDF-Datei nicht gefunden"
        
        # Create slides directory
        SLIDES_DIR.mkdir(exist_ok=True)
        
        # Check if already converted
        existing_slides = sorted(SLIDES_DIR.glob("slide_*.png"))
        if existing_slides:
            return existing_slides, None
        
        # Convert PDF to images
        with st.spinner("Konvertiere PDF zu Slides..."):
            images = convert_from_path(str(PDF_FILE), dpi=150)
            
            slide_paths = []
            for i, image in enumerate(images, 1):
                slide_path = SLIDES_DIR / f"slide_{i:03d}.png"
                image.save(str(slide_path), "PNG")
                slide_paths.append(slide_path)
            
            return slide_paths, None
            
    except ImportError:
        return None, "pdf2image nicht installiert"
    except Exception as ex:
        return None, str(ex)

def get_slide_images():
    """Get list of slide images, convert if necessary"""
    # Check for existing slides (support both formats: slide_001.png and slide-1.png)
    if SLIDES_DIR.exists():
        slides = sorted(SLIDES_DIR.glob("slide*.png"))
        if slides:
            return slides, None
    
    # Try to convert PDF
    if PDF_FILE.exists():
        return convert_pdf_to_images()
    
    return None, "no_pdf"

def main():
    st.title(e("🎬 ") + "Project Defense Präsentation")
    st.markdown("**Datascientest - Helpdesk Performance Analytics**")
    st.divider()
    
    # Get slides
    slides, error = get_slide_images()
    
    if error == "no_pdf":
        st.warning(e("⚠️ ") + "PDF-Version der Präsentation fehlt!")
        st.markdown("""
        **Um die Präsentation anzuzeigen, bitte die PPTX als PDF exportieren:**
        
        1. Öffne die PowerPoint-Datei
        2. **Datei → Speichern unter → PDF**
        3. Speichere als: `Datascientest_project_defense.pdf`
        4. Im Ordner: `reports/`
        
        Oder installiere LibreOffice für automatische Konvertierung:
        ```bash
        sudo apt install libreoffice-impress -y
        ```
        """)
        
        # Show PPTX download option
        if PPTX_FILE.exists():
            with open(PPTX_FILE, "rb") as f:
                st.download_button(
                    label=e("📥 ") + "PPTX herunterladen",
                    data=f,
                    file_name="Datascientest_project_defense.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
        return
    
    if error:
        st.error(f"Fehler: {error}")
        return
    
    if not slides:
        st.error("Keine Slides gefunden")
        return
    
    # Slide navigation
    total_slides = len(slides)
    
    # Initialize slide index in session state (and validate range)
    if 'current_slide' not in st.session_state or st.session_state.current_slide < 1 or st.session_state.current_slide > total_slides:
        st.session_state.current_slide = 1
    
    # Navigation controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
    
    with col1:
        if st.button(e("⏮️ ") + "Start", width="stretch", disabled=st.session_state.current_slide == 1):
            st.session_state.current_slide = 1
            st.rerun()
    
    with col2:
        if st.button(e("◀️ ") + "Zurück", width="stretch", disabled=st.session_state.current_slide == 1):
            st.session_state.current_slide -= 1
            st.rerun()
    
    with col3:
        # Slide selector
        new_slide = st.select_slider(
            "Slide",
            options=list(range(1, total_slides + 1)),
            value=st.session_state.current_slide,
            format_func=lambda x: f"Slide {x} / {total_slides}",
            label_visibility="collapsed"
        )
        if new_slide != st.session_state.current_slide:
            st.session_state.current_slide = new_slide
            st.rerun()
    
    with col4:
        if st.button("Weiter " + e("▶️"), width="stretch", disabled=st.session_state.current_slide == total_slides):
            st.session_state.current_slide += 1
            st.rerun()
    
    with col5:
        if st.button("Ende " + e("⏭️"), width="stretch", disabled=st.session_state.current_slide == total_slides):
            st.session_state.current_slide = total_slides
            st.rerun()
    
    st.divider()
    
    # Display current slide
    current_slide_path = slides[st.session_state.current_slide - 1]
    
    # Center the slide with max width
    col_left, col_center, col_right = st.columns([1, 10, 1])
    with col_center:
        st.image(
            str(current_slide_path),
            width="stretch",
            caption=f"Slide {st.session_state.current_slide} von {total_slides}"
        )
    
    # Keyboard navigation hint
    st.markdown("""
    <style>
    .slide-hint {
        text-align: center;
        color: #666;
        font-size: 0.85em;
        margin-top: 1rem;
    }
    </style>
    <p class="slide-hint">💡 Nutze die Buttons oder den Slider zur Navigation</p>
    """, unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**{e('📊')} Präsentation**")
        st.markdown(f"Slide {st.session_state.current_slide} / {total_slides}")
        
        # Progress bar
        progress = st.session_state.current_slide / total_slides
        st.progress(progress)
        
        # Quick navigation
        st.markdown("**Schnellnavigation:**")
        quick_nav = st.selectbox(
            "Gehe zu Slide",
            options=list(range(1, total_slides + 1)),
            index=st.session_state.current_slide - 1,
            label_visibility="collapsed"
        )
        if quick_nav != st.session_state.current_slide:
            st.session_state.current_slide = quick_nav
            st.rerun()

if __name__ == "__main__":
    main()
