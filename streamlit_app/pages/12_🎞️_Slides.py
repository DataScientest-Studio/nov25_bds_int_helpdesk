"""
Slides — SVG-Präsentation aus docs/Slides/
"""

import base64
from pathlib import Path
import streamlit as st
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_settings_sidebar, page_header, render_footer,
    init_session_state, get_text
)

st.set_page_config(page_title="Slides", page_icon="🎞️", layout="wide")

init_session_state()
render_settings_sidebar()

lang = st.session_state.get('language', 'de')

# ── Slides laden ─────────────────────────────────────────────────────────────
SLIDES_DIR = Path(__file__).parent.parent.parent / "docs" / "Slides"

def load_slides():
    if not SLIDES_DIR.exists():
        return []
    files = sorted(
        list(SLIDES_DIR.glob("*.SVG")) + list(SLIDES_DIR.glob("*.svg")),
        key=lambda p: p.name.lower()
    )
    # Deduplizieren (falls sowohl .SVG als auch .svg)
    seen = set()
    unique = []
    for f in files:
        key = f.name.lower()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique

slides = load_slides()

# ── Session State ─────────────────────────────────────────────────────────────
if "slide_index" not in st.session_state:
    st.session_state.slide_index = 0

n = len(slides)

# ── Header ────────────────────────────────────────────────────────────────────
page_header(
    "🎞️ Slides",
    "Präsentation / Presentation" if lang == 'de' else "Presentation"
)

# ── Keine Slides ──────────────────────────────────────────────────────────────
if n == 0:
    st.warning(
        f"Keine SVG-Dateien in `{SLIDES_DIR}` gefunden."
        if lang == 'de' else
        f"No SVG files found in `{SLIDES_DIR}`."
    )
    render_footer()
    st.stop()

# ── Index sicherstellen ───────────────────────────────────────────────────────
idx = st.session_state.slide_index % n

# ── Navigation Bar ────────────────────────────────────────────────────────────
nav_left, nav_center, nav_right = st.columns([1, 4, 1])

with nav_left:
    if st.button("◀  Zurück" if lang == 'de' else "◀  Back",
                 key="slide_prev", width="stretch"):
        st.session_state.slide_index = (idx - 1) % n
        st.rerun()

with nav_center:
    # Progress bar + counter
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:14px;padding:6px 0;">
            <div style="flex:1;background:#e1e5ec;border-radius:6px;height:8px;">
                <div style="background:#2563eb;width:{(idx+1)/n*100:.1f}%;height:8px;
                     border-radius:6px;transition:width 0.3s;"></div>
            </div>
            <span style="font-size:14px;font-weight:700;color:#1e3a5f;white-space:nowrap;">
                {idx + 1} / {n}
            </span>
            <span style="font-size:12px;color:#64748b;white-space:nowrap;">
                {slides[idx].stem}
            </span>
        </div>""",
        unsafe_allow_html=True
    )

with nav_right:
    if st.button("Weiter  ▶" if lang == 'de' else "Next  ▶",
                 key="slide_next", width="stretch"):
        st.session_state.slide_index = (idx + 1) % n
        st.rerun()

st.markdown("---")

# ── Slide anzeigen ────────────────────────────────────────────────────────────
svg_bytes = slides[idx].read_bytes()

# Safari-Fix: Calibri (Microsoft-only) durch systemübergreifenden Font ersetzen
svg_text = svg_bytes.decode('utf-8', errors='replace')
svg_text = svg_text.replace(
    'Calibri,Calibri_MSFontService,sans-serif',
    '-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,Helvetica,sans-serif'
).replace(
    'Calibri,Calibri_MSFontService',
    '-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,Helvetica'
).replace(
    '"Calibri"',
    'Arial'
).replace(
    "'Calibri'",
    'Arial'
)
b64 = base64.b64encode(svg_text.encode('utf-8')).decode()

st.markdown(
    f"""<div style="
            background:transparent;
            border:1px solid rgba(255,255,255,0.15);
            border-radius:10px;
            padding:16px;
            box-shadow:0 2px 8px rgba(0,0,0,0.15);
            text-align:center;
        ">
        <img src="data:image/svg+xml;base64,{b64}"
             style="max-width:100%;height:auto;border-radius:6px;" />
    </div>""",
    unsafe_allow_html=True
)

# ── Thumbnail-Leiste ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗂️ Alle Slides" if lang == 'de' else "🗂️ All Slides", expanded=False):
    cols = st.columns(min(n, 4))
    for i, slide in enumerate(slides):
        with cols[i % 4]:
            raw = slide.read_bytes().decode('utf-8', errors='replace')
            raw = raw.replace(
                'Calibri,Calibri_MSFontService,sans-serif',
                '-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,Helvetica,sans-serif'
            ).replace('Calibri,Calibri_MSFontService', '-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,Helvetica')
            b64_thumb = base64.b64encode(raw.encode('utf-8')).decode()
            border = "2px solid #2563eb" if i == idx else "1px solid rgba(255,255,255,0.15)"
            bg = "rgba(37,99,235,0.15)" if i == idx else "transparent"
            st.markdown(
                f"""<div style="background:{bg};border:{border};border-radius:8px;
                         padding:8px;margin-bottom:8px;cursor:pointer;text-align:center;">
                    <img src="data:image/svg+xml;base64,{b64_thumb}"
                         style="width:100%;height:auto;border-radius:4px;" />
                    <div style="font-size:11px;font-weight:600;color:inherit;
                                margin-top:6px;">{slide.stem}</div>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button(f"▶ {slide.stem}", key=f"thumb_{i}", width="stretch"):
                st.session_state.slide_index = i
                st.rerun()

render_footer()
