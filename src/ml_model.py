"""
ML Model - Trains an ensemble model for score prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, cohen_kappa_score, mean_absolute_error, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

# Optional: XGBoost und LightGBM
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


def create_model():
    """
    Create ML ensemble.
    
    Consists of:
    - XGBoost (if available)
    - LightGBM (if available)
    - RandomForest (always available)
    """
    estimators = []
    
    # RandomForest (Basis)
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,  # Optimized for balance between bias and variance
        random_state=42,
        n_jobs=-1
    )
    estimators.append(('rf', rf))
    
    # XGBoost
    if XGBOOST_AVAILABLE:
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,  # Consistent with other models
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        estimators.append(('xgb', xgb_model))
    
    # LightGBM
    if LIGHTGBM_AVAILABLE:
        lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,  # Consistent with other models
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
        estimators.append(('lgb', lgb_model))
    
    # Voting Ensemble
    ensemble = VotingClassifier(
        estimators=estimators,
        voting='soft'
    )
    
    return ensemble


def train_model(X, y, test_size=0.2):
    """
    Train the model.
    
    Args:
        X: Features DataFrame
        y: Target DataFrame (Q1, Q2, Q3)
        test_size: Anteil Test-Daten
        
    Returns:
        dict: Trained models and metrics
    """
    print("\n🤖 MODELL-TRAINING")
    print("="*50)
    
    targets = ['Q1', 'Q2', 'Q3']
    models = {}
    metrics = {}
    feature_importance = {}
    
    # Scaler
    scaler = StandardScaler()
    
    for target in targets:
        print(f"\n📊 Training für {target}...")
        
        # Target vorbereiten (Scores 1-5 -> 0-4)
        y_target = y[target].values - 1
        
        # Train-Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X.values, y_target,
            test_size=test_size,
            random_state=42,
            stratify=y_target
        )
        
        # Skalierung
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print(f"   Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Modell erstellen und trainieren
        model = create_model()
        model.fit(X_train_scaled, y_train)
        
        # Vorhersage
        y_pred = model.predict(X_test_scaled)
        
        # Metriken
        accuracy = accuracy_score(y_test, y_pred)
        kappa = cohen_kappa_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross-Validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, scaler.fit_transform(X.values), y_target, cv=cv, scoring='accuracy')
        
        metrics[target] = {
            'accuracy': round(accuracy, 3),
            'kappa': round(kappa, 3),
            'mae': round(mae, 3),
            'cv_mean': round(cv_scores.mean(), 3),
            'cv_std': round(cv_scores.std(), 3),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   Kappa: {kappa:.3f}")
        print(f"   CV: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        
        models[target] = model
        
        # Feature Importance (von RandomForest)
        if hasattr(model.named_estimators_['rf'], 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': X.columns,
                'importance': model.named_estimators_['rf'].feature_importances_
            }).sort_values('importance', ascending=False)
            feature_importance[target] = importance_df
    
    return {
        'models': models,
        'scaler': scaler,
        'metrics': metrics,
        'feature_importance': feature_importance
    }


def save_model(model_data, output_path="models/performance_scorer.joblib"):
    """Save the trained model."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model_data, output_path)
    print(f"\n💾 Model saved: {output_path}")


def load_model(model_path="models/performance_scorer.joblib"):
    """Load a saved model."""
    model_path = Path(model_path)
    if model_path.exists():
        return joblib.load(model_path)
    return None


def print_summary(metrics):
    """Print summary."""
    print("\n" + "="*50)
    print("📊 MODEL SUMMARY")
    print("="*50)
    
    for target, m in metrics.items():
        print(f"\n{target}:")
        print(f"   Accuracy: {m['accuracy']}")
        print(f"   Kappa: {m['kappa']}")
        print(f"   CV: {m['cv_mean']} ± {m['cv_std']}")
    
    # Average
    avg_acc = np.mean([m['accuracy'] for m in metrics.values()])
    avg_kappa = np.mean([m['kappa'] for m in metrics.values()])
    
    print(f"\n🎯 TOTAL:")
    print(f"   Ø Accuracy: {avg_acc:.3f}")
    print(f"   Ø Kappa: {avg_kappa:.3f}")


if __name__ == "__main__":
    print("="*50)
    print("🤖 ML-MODELL TRAINING")
    print("="*50)
    
    # ML-Datensatz laden
    data_path = Path("data/processed/ml_dataset.csv")
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        print(f"📁 Loaded: {len(df)} Samples")
        
        # Features und Targets trennen
        target_cols = ['Q1', 'Q2', 'Q3']
        feature_cols = [col for col in df.columns if col not in target_cols]
        
        X = df[feature_cols]
        y = df[target_cols]
        
        print(f"   Features: {len(feature_cols)}")
        
        # Training
        model_data = train_model(X, y)
        
        # Zusammenfassung
        print_summary(model_data['metrics'])
        
        # Speichern
        save_model(model_data)
        
        # Top Features anzeigen
        print("\n📈 Top 5 Features (Q1):")
        if 'Q1' in model_data['feature_importance']:
            for _, row in model_data['feature_importance']['Q1'].head(5).iterrows():
                print(f"   {row['feature']}: {row['importance']:.4f}")
    else:
        print("❌ ML-Datensatz not found!")
        print("   Please run feature_engineering.py first.")
