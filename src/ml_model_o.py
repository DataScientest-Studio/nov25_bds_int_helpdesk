"""
ML-Modell mit O-Score als Target (Objektive Bewertung)

Dieses Modell nutzt den berechneten O-Score als Zielvariable
anstelle der subjektiven Q-Scores vom Manager.

Target: O-Score (1-5, diskretisiert)
Features: Ticket-Metriken aus o_score_results.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_absolute_error, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False


# Modell-Konfiguration
MODEL_CONFIG = {
    'n_estimators': 100,
    'max_depth': 6,
    'random_state': 42
}


def load_o_score_data(data_path="data/processed/o_score_results.csv"):
    """Laedt die O-Score Daten."""
    df = pd.read_csv(data_path)
    return df


def prepare_features(o_score_df):
    """
    Bereitet Features fuer das ML-Modell vor.
    
    Features basieren auf den gleichen Metriken wie der O-Score,
    aber das Modell lernt die Gewichtung selbst.
    """
    feature_cols = [
        'ticket_count',
        'median_time_hours',
        'avg_steps',
        'avg_comments',
        'reopen_rate',
        'first_touch_rate',
        'success_rate'
    ]
    
    # Nur vorhandene Spalten nutzen
    available_cols = [c for c in feature_cols if c in o_score_df.columns]
    
    X = o_score_df[available_cols].copy()
    
    # Fehlende Werte fuellen
    X = X.fillna(X.median())
    
    return X, available_cols


def discretize_o_score(o_scores):
    """
    Diskretisiert den kontinuierlichen O-Score in Klassen 1-5.
    """
    bins = [0, 1.8, 2.6, 3.4, 4.2, 5.1]
    labels = [1, 2, 3, 4, 5]
    return pd.cut(o_scores, bins=bins, labels=labels).astype(int)


def create_ensemble_classifier():
    """Erstellt Ensemble-Klassifikator."""
    estimators = []
    
    # RandomForest
    rf = RandomForestClassifier(
        n_estimators=MODEL_CONFIG['n_estimators'],
        max_depth=MODEL_CONFIG['max_depth'],
        random_state=MODEL_CONFIG['random_state'],
        n_jobs=-1
    )
    estimators.append(('rf', rf))
    
    # XGBoost
    if XGBOOST_AVAILABLE:
        xgb_model = xgb.XGBClassifier(
            n_estimators=MODEL_CONFIG['n_estimators'],
            max_depth=MODEL_CONFIG['max_depth'],
            learning_rate=0.1,
            random_state=MODEL_CONFIG['random_state'],
            verbosity=0,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        estimators.append(('xgb', xgb_model))
    
    # LightGBM
    if LIGHTGBM_AVAILABLE:
        lgb_model = lgb.LGBMClassifier(
            n_estimators=MODEL_CONFIG['n_estimators'],
            max_depth=MODEL_CONFIG['max_depth'],
            learning_rate=0.1,
            random_state=MODEL_CONFIG['random_state'],
            verbose=-1
        )
        estimators.append(('lgb', lgb_model))
    
    return VotingClassifier(estimators=estimators, voting='soft')


def train_o_score_model(o_score_df, test_size=0.2):
    """
    Trainiert das O-Score Klassifikationsmodell.
    """
    print("\n" + "="*50)
    print("O-SCORE MODELL TRAINING")
    print("="*50)
    
    # Features vorbereiten
    X, feature_cols = prepare_features(o_score_df)
    
    # Target: diskrete Klassen 1-5
    y = discretize_o_score(o_score_df['o_score'])
    
    print(f"\nDaten: {len(X)} Samples, {len(feature_cols)} Features")
    print(f"Features: {feature_cols}")
    print(f"\nO-Score Klassen-Verteilung:")
    print(pd.Series(y).value_counts().sort_index())
    
    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")
    
    # Scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Training
    print("\n--- Klassifikator (Klassen 1-5) ---")
    classifier = create_ensemble_classifier()
    classifier.fit(X_train_scaled, y_train)
    
    # Evaluation
    y_pred = classifier.predict(X_test_scaled)
    
    accuracy = accuracy_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Cross-Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(classifier, scaler.fit_transform(X), y, cv=cv)
    
    print(f"Accuracy: {accuracy:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"CV: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")
    
    # Feature Importance
    if hasattr(classifier.named_estimators_['rf'], 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': classifier.named_estimators_['rf'].feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nFeature Importance:")
        for _, row in importance_df.iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
    else:
        importance_df = pd.DataFrame()
    
    # Metriken
    metrics = {
        'classifier': {
            'accuracy': round(accuracy, 3),
            'mae': round(mae, 3),
            'cv_mean': round(cv_scores.mean(), 3),
            'cv_std': round(cv_scores.std(), 3),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
    }
    
    return {
        'classifier': classifier,
        'scaler': scaler,
        'feature_cols': feature_cols,
        'metrics': metrics,
        'feature_importance': importance_df,
        'model_type': 'o_score'
    }


def save_model(model_data, output_path="models/o_score_model.joblib"):
    """Speichert das Modell."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_data, output_path)
    print(f"\nModell gespeichert: {output_path}")


def load_model(model_path="models/o_score_model.joblib"):
    """Laedt das Modell."""
    return joblib.load(model_path)


def predict_o_score(model_data, X_new):
    """
    Vorhersage fuer neue Daten.
    
    Returns:
        Array mit vorhergesagten Klassen (1-5)
    """
    X_scaled = model_data['scaler'].transform(X_new)
    return model_data['classifier'].predict(X_scaled)


def print_summary(model_data):
    """Druckt Zusammenfassung."""
    metrics = model_data['metrics']
    
    print("\n" + "="*50)
    print("O-SCORE MODELL ZUSAMMENFASSUNG")
    print("="*50)
    
    print("\nKlassifikator (Klassen 1-5):")
    print(f"   Accuracy: {metrics['classifier']['accuracy']}")
    print(f"   MAE: {metrics['classifier']['mae']}")
    print(f"   CV: {metrics['classifier']['cv_mean']} +/- {metrics['classifier']['cv_std']}")


if __name__ == "__main__":
    print("="*50)
    print("O-SCORE ML-MODELL")
    print("="*50)
    
    # Daten laden
    data_path = Path("data/processed/o_score_results.csv")
    
    if not data_path.exists():
        print("O-Score Daten nicht gefunden!")
        print("Bitte zuerst: python src/o_score.py")
        exit(1)
    
    o_score_df = load_o_score_data(data_path)
    print(f"Geladen: {len(o_score_df)} Mitarbeiter")
    
    # Training
    model_data = train_o_score_model(o_score_df)
    
    # Zusammenfassung
    print_summary(model_data)
    
    # Speichern
    save_model(model_data)
    
    print("\n" + "="*50)
    print("TRAINING ABGESCHLOSSEN")
    print("="*50)
