"""
ML Model Details
Feature Importance, SHAP analysis and model performance.
Q-Score (Manager) and O-Score (Objective) Tabs.
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


def t(de_text, en_text):
    """Simple translation helper."""
    return en_text if st.session_state.get('language') == 'en' else de_text


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
    """Load O-Score (Objective) model."""
    o_path = MODELS_DIR / "o_score_model.joblib"
    if o_path.exists():
        return joblib.load(o_path), "o_score"
    return None, None


def render_metrics_interpretation(avg_acc, avg_mae, avg_cv, avg_f1_macro, avg_f1_weighted, avg_kappa, avg_qwk):
    """Render metrics interpretation section with full translation."""
    
    # Labels based on language
    is_en = st.session_state.get('language') == 'en'
    
    col1, col2 = st.columns(2)
    
    with col1:
        acc_rating = t("🟢 Gut", "🟢 Good") if avg_acc >= 0.7 else t("🟡 Akzeptabel", "🟡 Acceptable") if avg_acc >= 0.5 else t("🔴 Verbesserungsbedarf", "🔴 Needs Improvement")
        acc_desc = t(
            "Anteil korrekt klassifizierter Samples. Bei 5 Klassen wäre Zufall 20%.",
            "Proportion of correctly classified samples. With 5 classes, random would be 20%."
        )
        st.markdown(f"""
        **Accuracy ({avg_acc*100:.1f}%)** {acc_rating}
        > {acc_desc}
        """)
        
        mae_rating = t("🟢 Sehr gut", "🟢 Very Good") if avg_mae < 0.5 else t("🟡 Akzeptabel", "🟡 Acceptable") if avg_mae < 0.8 else t("🔴 Hoch", "🔴 High")
        mae_desc = t(
            "Mittlerer Fehler in Klassen. <0.5 = Fehler meist nur ±1 Klasse.",
            "Mean error in classes. <0.5 = errors usually only ±1 class."
        )
        st.markdown(f"""
        **MAE ({avg_mae:.3f})** {mae_rating}
        > {mae_desc}
        """)
        
        cv_rating = t("🟢 Stabil", "🟢 Stable") if avg_cv >= 0.6 else t("🟡 Moderat", "🟡 Moderate") if avg_cv >= 0.5 else t("🔴 Instabil", "🔴 Unstable")
        cv_desc = t(
            "Cross-Validation zeigt Generalisierungsfähigkeit.",
            "Cross-validation shows generalization capability."
        )
        st.markdown(f"""
        **CV Score ({avg_cv*100:.1f}%)** {cv_rating}
        > {cv_desc}
        """)
        
        f1m_rating = t("🟢 Gut", "🟢 Good") if avg_f1_macro >= 0.5 else t("🟡 Moderat", "🟡 Moderate") if avg_f1_macro >= 0.3 else t("🔴 Schwach", "🔴 Weak")
        f1m_desc = t(
            "Ungewichteter Durchschnitt über alle Klassen.",
            "Unweighted average across all classes."
        )
        st.markdown(f"""
        **Macro-F1 ({avg_f1_macro:.3f})** {f1m_rating}
        > {f1m_desc}
        """)
    
    with col2:
        f1w_rating = t("🟢 Gut", "🟢 Good") if avg_f1_weighted >= 0.6 else t("🟡 Moderat", "🟡 Moderate") if avg_f1_weighted >= 0.5 else t("🔴 Schwach", "🔴 Weak")
        f1w_desc = t(
            "Nach Klassengröße gewichtet.",
            "Weighted by class size."
        )
        st.markdown(f"""
        **Weighted-F1 ({avg_f1_weighted:.3f})** {f1w_rating}
        > {f1w_desc}
        """)
        
        kappa_rating = t("🟢 Substanziell", "🟢 Substantial") if avg_kappa >= 0.5 else t("🟡 Moderat", "🟡 Moderate") if avg_kappa >= 0.3 else t("🔴 Schwach", "🔴 Weak")
        kappa_desc = t(
            "Übereinstimmung über Zufall hinaus.",
            "Agreement beyond chance."
        )
        st.markdown(f"""
        **Cohen's Kappa ({avg_kappa:.3f})** {kappa_rating}
        > {kappa_desc}
        """)
        
        qwk_rating = t("🟢 Sehr gut", "🟢 Very Good") if avg_qwk >= 0.6 else t("🟡 Gut", "🟡 Good") if avg_qwk >= 0.4 else t("🔴 Moderat", "🔴 Moderate")
        qwk_desc = t(
            "Quadratic Weighted Kappa - bestraft große Fehler stärker.",
            "Quadratic Weighted Kappa - penalizes larger errors more."
        )
        st.markdown(f"""
        **QWK ({avg_qwk:.3f})** {qwk_rating}
        > {qwk_desc}
        """)


def render_overall_assessment(good_metrics):
    """Render overall assessment with translation."""
    very_good = t("Sehr gut", "Very Good")
    good_label = t("Gut", "Good")
    improvement = t("Verbesserungspotential", "Improvement Potential")
    metrics_label = t("Metriken im grünen Bereich", "metrics in green zone")
    overall = t("Gesamtbewertung", "Overall Assessment")
    
    if good_metrics >= 5:
        st.success(e("✅ ") + f"**{overall}: {very_good}** ({good_metrics}/6 {metrics_label})")
    elif good_metrics >= 3:
        st.info(e("👍 ") + f"**{overall}: {good_label}** ({good_metrics}/6 {metrics_label})")
    else:
        st.warning(e("⚠️ ") + f"**{overall}: {improvement}** ({good_metrics}/6 {metrics_label})")


def render_q_score_details(model_data, model_type):
    """Render Q-Score model details (Q1, Q2, Q3 structure)."""
    
    if model_data is None:
        not_found = t("Q-Score Modell nicht gefunden", "Q-Score Model not found")
        st.warning(e("⚠️ ") + not_found)
        return
    
    loaded_label = t("Modell geladen", "Model loaded")
    st.success(e("✅ ") + f"{loaded_label}: **{model_type.upper()}**")
    
    targets = ['Q1', 'Q2', 'Q3']
    
    # Metrics display
    section_header(e("📊 ") + get_text('performance_metrics'), 'metrics_q_score')
    
    metrics = model_data.get('metrics', {})
    
    if metrics:
        # Metriken pro Target (Q1, Q2, Q3)
        cols = st.columns(len(targets))
        
        for idx, (target, col) in enumerate(zip(targets, cols)):
            if target in metrics:
                m = metrics[target]
                with col:
                    st.markdown(f"### {target}")
                    st.metric(get_text('accuracy'), f"{m.get('accuracy', 0)*100:.1f}%")
                    st.metric(get_text('mae'), f"{m.get('mae', 0):.3f}")
                    st.metric("CV Score", f"{m.get('cv_mean', 0)*100:.1f}%")
                    st.metric("Macro-F1", f"{m.get('f1_macro', 0):.3f}")
                    st.metric("Weighted-F1", f"{m.get('f1_weighted', 0):.3f}")
                    st.metric("Cohen's Kappa", f"{m.get('kappa', 0):.3f}")
                    st.metric("QWK", f"{m.get('qwk', 0):.3f}")
        
        # Averages
        st.markdown("---")
        available_targets = [t_name for t_name in targets if t_name in metrics]
        if available_targets:
            avg_acc = np.mean([metrics[t_name].get('accuracy', 0) for t_name in available_targets])
            avg_mae = np.mean([metrics[t_name].get('mae', 0) for t_name in available_targets])
            avg_cv = np.mean([metrics[t_name].get('cv_mean', 0) for t_name in available_targets])
            avg_f1_macro = np.mean([metrics[t_name].get('f1_macro', 0) for t_name in available_targets])
            avg_f1_weighted = np.mean([metrics[t_name].get('f1_weighted', 0) for t_name in available_targets])
            avg_kappa = np.mean([metrics[t_name].get('kappa', 0) for t_name in available_targets])
            avg_qwk = np.mean([metrics[t_name].get('qwk', 0) for t_name in available_targets])
            
            avg_title = t("Ø Durchschnitt (Q1, Q2, Q3)", "Avg (Q1, Q2, Q3)")
            st.markdown(f"### {avg_title}")
            
            # Row 1
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(e("📈 ") + t("Ø Accuracy", "Avg Accuracy"), f"{avg_acc*100:.1f}%")
            with col2:
                st.metric(e("📉 ") + t("Ø MAE", "Avg MAE"), f"{avg_mae:.3f}")
            with col3:
                st.metric(e("🔄 ") + t("Ø CV Score", "Avg CV Score"), f"{avg_cv*100:.1f}%")
            with col4:
                st.metric(e("📊 ") + t("Ø Macro-F1", "Avg Macro-F1"), f"{avg_f1_macro:.3f}")
            
            # Row 2
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t("Ø Weighted-F1", "Avg Weighted-F1"), f"{avg_f1_weighted:.3f}")
            with col2:
                st.metric(t("Ø Cohen's Kappa", "Avg Cohen's Kappa"), f"{avg_kappa:.3f}")
            with col3:
                st.metric(t("Ø QWK", "Avg QWK"), f"{avg_qwk:.3f}")
            with col4:
                pass
            
            # Interpretation
            st.markdown("---")
            interpretation_title = t("Metriken-Interpretation (Durchschnitt)", "Metrics Interpretation (Average)")
            st.markdown("### " + e("📋 ") + interpretation_title)
            
            render_metrics_interpretation(avg_acc, avg_mae, avg_cv, avg_f1_macro, avg_f1_weighted, avg_kappa, avg_qwk)
            
            # Overall assessment
            st.markdown("---")
            good_metrics = sum([avg_acc >= 0.65, avg_mae < 0.6, avg_cv >= 0.6, 
                               avg_f1_weighted >= 0.6, avg_kappa >= 0.4, avg_qwk >= 0.6])
            render_overall_assessment(good_metrics)
    
    st.markdown("---")
    
    # Feature Importance
    section_header(e("📈 ") + get_text('feature_importance'), 'feature_imp_q_score')
    
    feature_importance = model_data.get('feature_importance', {})
    
    if isinstance(feature_importance, dict) and feature_importance:
        available_fi = [t_name for t_name in targets if t_name in feature_importance]
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
        available_cm = [t_name for t_name in targets if t_name in metrics and 'confusion_matrix' in metrics.get(t_name, {})]
        
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
        not_found = t("O-Score Modell nicht gefunden", "O-Score Model not found")
        st.warning(e("⚠️ ") + not_found)
        return
    
    loaded_label = t("Modell geladen", "Model loaded")
    st.success(e("✅ ") + f"{loaded_label}: **{model_type.upper()}**")
    
    # Metrics display
    section_header(e("📊 ") + get_text('performance_metrics'), 'metrics_o_score')
    
    metrics = model_data.get('metrics', {})
    
    if metrics:
        classifier_metrics = metrics.get('classifier', {})
        
        # Row 1
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
        
        # Row 2
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
        
        # Interpretation
        st.markdown("---")
        interpretation_title = t("Metriken-Interpretation", "Metrics Interpretation")
        st.markdown("### " + e("📋 ") + interpretation_title)
        
        acc = classifier_metrics.get('accuracy', 0)
        mae = classifier_metrics.get('mae', 0)
        cv_mean = classifier_metrics.get('cv_mean', 0)
        f1_macro = classifier_metrics.get('f1_macro', 0)
        f1_weighted = classifier_metrics.get('f1_weighted', 0)
        kappa = classifier_metrics.get('kappa', 0)
        qwk = classifier_metrics.get('qwk', 0)
        
        render_metrics_interpretation(acc, mae, cv_mean, f1_macro, f1_weighted, kappa, qwk)
        
        # Overall assessment
        st.markdown("---")
        good_metrics = sum([acc >= 0.7, mae < 0.4, cv_mean >= 0.7, f1_weighted >= 0.7, kappa >= 0.5, qwk >= 0.7])
        render_overall_assessment(good_metrics)
    
    st.markdown("---")
    
    # Feature Importance
    section_header(e("📈 ") + get_text('feature_importance'), 'feature_imp_o_score')
    
    feature_importance = model_data.get('feature_importance')
    
    if feature_importance is not None:
        if isinstance(feature_importance, pd.DataFrame) and not feature_importance.empty:
            render_feature_importance_chart(feature_importance, "O-Score")
        elif isinstance(feature_importance, dict) and feature_importance:
            dict_info = t("Feature Importance als Dictionary vorhanden", "Feature Importance available as dictionary")
            st.info(dict_info)
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
q_tab_label = t("Q-Score (Manager)", "Q-Score (Manager)")
o_tab_label = t("O-Score (Objektiv)", "O-Score (Objective)")

tab_q, tab_o = st.tabs([
    e("👔 ") + q_tab_label, 
    e("🎯 ") + o_tab_label
])

with tab_q:
    q_desc = t(
        """
        **Q-Score** basiert auf subjektiven Manager-Bewertungen mit drei Dimensionen:
        - **Q1**: Genauigkeit, Präzision, Sorgfalt
        - **Q2**: Gründlichkeit, Vollständigkeit, Umfassendheit  
        - **Q3**: Reaktionsschnelligkeit, Verbindlichkeit, Höflichkeit
        """,
        """
        **Q-Score** is based on subjective manager ratings with three dimensions:
        - **Q1**: Accuracy, precision, attention to detail
        - **Q2**: Thoroughness, completeness, comprehensiveness  
        - **Q3**: Responsiveness, promptness, courtesy
        """
    )
    st.markdown(q_desc)
    st.markdown("---")
    render_q_score_details(q_model_data, q_model_type)

with tab_o:
    o_desc = t(
        """
        **O-Score** basiert auf objektiven, messbaren Kriterien:
        - **Qualität** (35%): Reopen-Rate, Success-Rate
        - **Effizienz** (25%): Mediane Bearbeitungszeit
        - **Produktivität** (20%): Ticket-Volumen
        - **Kommunikation** (20%): First-Touch-Rate
        """,
        """
        **O-Score** is based on objective, measurable criteria:
        - **Quality** (35%): Reopen rate, success rate
        - **Efficiency** (25%): Median processing time
        - **Productivity** (20%): Ticket volume
        - **Communication** (20%): First-touch rate
        """
    )
    st.markdown(o_desc)
    st.markdown("---")
    render_o_score_details(o_model_data, o_model_type)

# Model Comparison Summary
st.markdown("---")
comparison_title = t("Modell-Vergleich", "Model Comparison")
section_header(e("⚖️ ") + comparison_title)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Q-Score (Manager)")
    if q_model_data and 'metrics' in q_model_data:
        q_metrics = q_model_data['metrics']
        q_targets = [t_name for t_name in ['Q1', 'Q2', 'Q3'] if t_name in q_metrics]
        if q_targets:
            avg_acc = np.mean([q_metrics[t_name].get('accuracy', 0) for t_name in q_targets])
            avg_cv = np.mean([q_metrics[t_name].get('cv_mean', 0) for t_name in q_targets])
            st.metric(t("Ø Accuracy", "Avg Accuracy"), f"{avg_acc*100:.1f}%")
            st.metric(t("Ø CV Score", "Avg CV Score"), f"{avg_cv*100:.1f}%")
        else:
            no_metrics = t("Keine Q1/Q2/Q3 Metriken", "No Q1/Q2/Q3 metrics")
            st.info(no_metrics)
    else:
        no_metrics = t("Keine Metriken verfügbar", "No metrics available")
        st.info(no_metrics)

with col2:
    o_label = t("O-Score (Objektiv)", "O-Score (Objective)")
    st.markdown(f"### {o_label}")
    if o_model_data and 'metrics' in o_model_data:
        o_metrics = o_model_data['metrics']
        classifier = o_metrics.get('classifier', {})
        if classifier:
            st.metric("Accuracy", f"{classifier.get('accuracy', 0)*100:.1f}%")
            st.metric("CV Score", f"{classifier.get('cv_mean', 0)*100:.1f}%")
        else:
            no_classifier = t("Keine Classifier Metriken", "No classifier metrics")
            st.info(no_classifier)
    else:
        no_metrics = t("Keine Metriken verfügbar", "No metrics available")
        st.info(no_metrics)

recommendation = t(
    """
**💡 Empfehlung:** Kombiniere beide Scores für ein vollständiges Bild!
- Q-Score erfasst subjektive Qualitätsaspekte
- O-Score liefert objektive, nachprüfbare Metriken
""",
    """
**💡 Recommendation:** Combine both scores for a complete picture!
- Q-Score captures subjective quality aspects
- O-Score provides objective, verifiable metrics
"""
)
st.info(recommendation)

# Footer
render_footer()
