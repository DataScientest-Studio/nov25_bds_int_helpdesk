"""
ML Model Details
Feature Importance, SHAP analysis and model performance.
Q-Score (Manager) und O-Score (Objektiv) Tabs.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import joblib
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.settings import (
    render_navigation,
    render_settings_sidebar, section_header, page_header, render_footer,
    get_text, get_help, init_session_state, e
)

st.set_page_config(page_title="ML Model Details", page_icon="🎯", layout="wide")

# Initialize settings
init_session_state()

# Render settings sidebar
render_settings_sidebar()

# Page header
page_header(
    e("🎯 ") + get_text('ml_model_details'),
    get_text('model_subtitle'),
    help_key='model'
)

MODELS_DIR = Path(__file__).parent.parent.parent / "models"


@st.cache_resource
def load_q_score_model():
    """Load Q-Score (Manager) model."""
    q_path = MODELS_DIR / "q_score_model.joblib"
    if q_path.exists():
        return joblib.load(q_path), "q_score"
    
    opt_path = MODELS_DIR / "optimized_scorer.joblib"
    if opt_path.exists():
        return joblib.load(opt_path), "optimized"
    
    std_path = MODELS_DIR / "performance_scorer.joblib"
    if std_path.exists():
        return joblib.load(std_path), "standard"
    
    return None, None


@st.cache_resource
def load_o_score_model():
    """Load O-Score (Objektiv) model."""
    o_path = MODELS_DIR / "o_score_model.joblib"
    if o_path.exists():
        return joblib.load(o_path), "o_score"
    return None, None


def render_q_score_details(model_data, model_type):
    """Render Q-Score model details (Q1, Q2, Q3 structure)."""
    
    if model_data is None:
        st.warning(e("⚠️ ") + "Q-Score Modell nicht gefunden")
        return
    
    st.success(e("✅ ") + f"Modell geladen: **{model_type.upper()}**")
    
    targets = ['Q1', 'Q2', 'Q3']
    
    # Metrics display
    section_header(e("📊 ") + get_text('performance_metrics'), 'metrics_q_score')
    
    metrics = model_data.get('metrics', {})
    
    if metrics:
        cols = st.columns(len(targets))
        
        for idx, (target, col) in enumerate(zip(targets, cols)):
            if target in metrics:
                m = metrics[target]
                with col:
                    st.markdown(f"### {target}")
                    st.metric(get_text('accuracy'), f"{m.get('accuracy', 0)*100:.1f}%")
                    st.metric(get_text('cohens_kappa'), f"{m.get('kappa', 0):.3f}")
                    st.metric(get_text('mae'), f"{m.get('mae', 0):.3f}")
                    if 'f1' in m:
                        st.metric(get_text('f1_score'), f"{m.get('f1', 0):.3f}")
        
        # Average
        st.markdown("---")
        available_targets = [t for t in targets if t in metrics]
        if available_targets:
            avg_acc = np.mean([metrics[t].get('accuracy', 0) for t in available_targets])
            avg_kappa = np.mean([metrics[t].get('kappa', 0) for t in available_targets])
            cv_mean = np.mean([metrics[t].get('cv_mean', 0) for t in available_targets])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(e("📈 ") + get_text('avg_accuracy'), f"{avg_acc*100:.1f}%")
            with col2:
                st.metric(e("📊 ") + get_text('avg_kappa'), f"{avg_kappa:.3f}")
            with col3:
                st.metric(e("🔄 ") + get_text('avg_cv_score'), f"{cv_mean*100:.1f}%")
    
    st.markdown("---")
    
    # Feature Importance
    section_header(e("📈 ") + get_text('feature_importance'), 'feature_imp_q_score')
    
    feature_importance = model_data.get('feature_importance', {})
    
    if isinstance(feature_importance, dict) and feature_importance:
        available_fi = [t for t in targets if t in feature_importance]
        if available_fi:
            target_select = st.selectbox(
                get_text('select_target') + ":", 
                available_fi,
                key='fi_select_q_score'
            )
            
            if target_select in feature_importance:
                importance_df = feature_importance[target_select]
                render_feature_importance_chart(importance_df, target_select)
        else:
            st.info(get_text('feature_importance') + " " + get_text('not_available'))
    else:
        st.info(get_text('feature_importance') + " " + get_text('not_available'))
    
    st.markdown("---")
    
    # Confusion Matrix
    section_header(e("🔢 ") + get_text('confusion_matrix'), 'confusion_q_score')
    
    if metrics:
        available_cm = [t for t in targets if t in metrics and 'confusion_matrix' in metrics.get(t, {})]
        
        if available_cm:
            target_cm = st.selectbox(
                get_text('target_for_cm') + ":", 
                available_cm, 
                key='cm_select_q_score'
            )
            render_confusion_matrix(metrics[target_cm]['confusion_matrix'], target_cm)
        else:
            st.info(get_text('confusion_matrix') + " " + get_text('not_available'))


def render_o_score_details(model_data, model_type):
    """Render O-Score model details (classifier/regressor structure)."""
    
    if model_data is None:
        st.warning(e("⚠️ ") + "O-Score Modell nicht gefunden")
        return
    
    st.success(e("✅ ") + f"Modell geladen: **{model_type.upper()}**")
    
    # Metrics display
    section_header(e("📊 ") + get_text('performance_metrics'), 'metrics_o_score')
    
    metrics = model_data.get('metrics', {})
    
    if metrics:
        classifier_metrics = metrics.get('classifier', {})
        
        # Zeile 1: Accuracy, MAE, CV Score, CV Std
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            acc = classifier_metrics.get('accuracy', 0)
            st.metric(get_text('accuracy'), f"{acc*100:.1f}%")
        
        with col2:
            mae = classifier_metrics.get('mae', 0)
            st.metric(get_text('mae'), f"{mae:.3f}")
        
        with col3:
            cv_mean = classifier_metrics.get('cv_mean', 0)
            st.metric("CV Score", f"{cv_mean*100:.1f}%")
        
        with col4:
            cv_std = classifier_metrics.get('cv_std', 0)
            st.metric("CV Std", f"±{cv_std*100:.1f}%")
        
        # Zeile 2: F1-Scores und Kappa-Metriken
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            f1_macro = classifier_metrics.get('f1_macro', 0)
            st.metric("Macro-F1", f"{f1_macro:.3f}")
        
        with col2:
            f1_weighted = classifier_metrics.get('f1_weighted', 0)
            st.metric("Weighted-F1", f"{f1_weighted:.3f}")
        
        with col3:
            kappa = classifier_metrics.get('kappa', 0)
            st.metric("Cohen's Kappa", f"{kappa:.3f}")
        
        with col4:
            qwk = classifier_metrics.get('qwk', 0)
            st.metric("QWK", f"{qwk:.3f}")
    
    st.markdown("---")
    
    # Feature Importance
    section_header(e("📈 ") + get_text('feature_importance'), 'feature_imp_o_score')
    
    feature_importance = model_data.get('feature_importance')
    
    # O-Score has feature_importance as a single DataFrame
    if feature_importance is not None:
        if isinstance(feature_importance, pd.DataFrame) and not feature_importance.empty:
            render_feature_importance_chart(feature_importance, "O-Score")
        elif isinstance(feature_importance, dict) and feature_importance:
            # Falls es doch als Dict strukturiert ist
            st.info("Feature Importance als Dictionary vorhanden")
        else:
            st.info(get_text('feature_importance') + " " + get_text('not_available'))
    else:
        st.info(get_text('feature_importance') + " " + get_text('not_available'))
    
    st.markdown("---")
    
    # Confusion Matrix
    section_header(e("🔢 ") + get_text('confusion_matrix'), 'confusion_o_score')
    
    if metrics and 'classifier' in metrics:
        cm = metrics['classifier'].get('confusion_matrix')
        if cm:
            render_confusion_matrix(cm, "O-Score")
        else:
            st.info(get_text('confusion_matrix') + " " + get_text('not_available'))
    else:
        st.info(get_text('confusion_matrix') + " " + get_text('not_available'))


def render_feature_importance_chart(importance_df, title):
    """Render feature importance chart."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            importance_df.head(15),
            x='importance',
            y='feature',
            orientation='h',
            title=f"{get_text('top_features')} {title}",
            color='importance',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(f"**{get_text('top_10_features')}:**")
        for i, (_, row) in enumerate(importance_df.head(10).iterrows()):
            pct = row['importance'] * 100
            st.markdown(f"{i+1}. **{row['feature']}**: {pct:.1f}%")
        
        st.markdown("---")
        st.markdown(f"**{get_text('interpretation')}:**")
        top_feature = importance_df.iloc[0]['feature']
        st.info(f"{get_text('most_important_feature')} **{top_feature}**. "
               f"{get_text('feature_influence')}")


def render_confusion_matrix(cm, title):
    """Render confusion matrix."""
    cm = np.array(cm)
    
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=[f"Pred {i+1}" for i in range(cm.shape[1])],
        y=[f"True {i+1}" for i in range(cm.shape[0])],
        colorscale='Blues',
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 14}
    ))
    fig.update_layout(
        title=f"{get_text('confusion_matrix')} - {title}",
        xaxis_title=get_text('predicted'),
        yaxis_title=get_text('actual'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    **{get_text('reading_hint')}:**
    - {get_text('diagonal_correct')}
    - {get_text('adjacent_acceptable')}
    - {get_text('far_problematic')}
    """)


# Load both models
q_model_data, q_model_type = load_q_score_model()
o_model_data, o_model_type = load_o_score_model()

# Create Tabs
tab_q, tab_o = st.tabs([
    e("👔 ") + "Q-Score (Manager)", 
    e("🎯 ") + "O-Score (Objektiv)"
])

with tab_q:
    if st.session_state.get('language', 'de') == 'de':
        st.markdown("""
        **Q-Score** basiert auf subjektiven Manager-Bewertungen mit drei Dimensionen:
        - **Q1**: Genauigkeit, Präzision, Sorgfalt
        - **Q2**: Gründlichkeit, Vollständigkeit, Umfassendheit  
        - **Q3**: Reaktionsschnelligkeit, Verbindlichkeit, Höflichkeit
        """)
    else:
        st.markdown("""
        **Q-Score** is based on subjective manager ratings with three dimensions:
        - **Q1**: Accuracy, precision, attention to detail
        - **Q2**: Thoroughness, completeness, comprehensiveness  
        - **Q3**: Responsiveness, promptness, courtesy
        """)
    st.markdown("---")
    render_q_score_details(q_model_data, q_model_type)

with tab_o:
    if st.session_state.get('language', 'de') == 'de':
        st.markdown("""
        **O-Score** basiert auf objektiven, messbaren Kriterien:
        - **Qualität** (35%): Reopen-Rate, Success-Rate
        - **Effizienz** (25%): Mediane Bearbeitungszeit
        - **Produktivität** (20%): Ticket-Volumen
        - **Kommunikation** (20%): First-Touch-Rate
        """)
    else:
        st.markdown("""
        **O-Score** is based on objective, measurable criteria:
        - **Quality** (35%): Reopen rate, success rate
        - **Efficiency** (25%): Median processing time
        - **Productivity** (20%): Ticket volume
        - **Communication** (20%): First-touch rate
        """)
    st.markdown("---")
    render_o_score_details(o_model_data, o_model_type)

# Model Comparison Summary
st.markdown("---")
section_header(e("⚖️ ") + "Modell-Vergleich")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Q-Score (Manager)")
    if q_model_data and 'metrics' in q_model_data:
        q_metrics = q_model_data['metrics']
        q_targets = [t for t in ['Q1', 'Q2', 'Q3'] if t in q_metrics]
        if q_targets:
            avg_acc = np.mean([q_metrics[t].get('accuracy', 0) for t in q_targets])
            avg_cv = np.mean([q_metrics[t].get('cv_mean', 0) for t in q_targets])
            st.metric("Ø Accuracy", f"{avg_acc*100:.1f}%")
            st.metric("Ø CV Score", f"{avg_cv*100:.1f}%")
        else:
            st.info("Keine Q1/Q2/Q3 Metriken")
    else:
        st.info("Keine Metriken verfügbar")

with col2:
    st.markdown("### O-Score (Objektiv)")
    if o_model_data and 'metrics' in o_model_data:
        o_metrics = o_model_data['metrics']
        classifier = o_metrics.get('classifier', {})
        if classifier:
            st.metric("Accuracy", f"{classifier.get('accuracy', 0)*100:.1f}%")
            st.metric("CV Score", f"{classifier.get('cv_mean', 0)*100:.1f}%")
        else:
            st.info("Keine Classifier Metriken")
    else:
        st.info("Keine Metriken verfügbar")

st.info("""
**💡 Empfehlung:** Kombiniere beide Scores für ein vollständiges Bild!
- Q-Score erfasst subjektive Qualitätsaspekte
- O-Score liefert objektive, nachprüfbare Metriken
""")

# Footer
render_footer()
