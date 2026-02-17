"""
ML Model with O-Score as Target (Objective Rating)

This model uses the calculated O-Score as target variable
instead of subjective Q-Scores from managers.

Target: O-Score (1-5, discretized)
Features: Ticket metrics from o_score_results.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, mean_absolute_error, confusion_matrix,
    f1_score, cohen_kappa_score
)
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


# Model configuration
MODEL_CONFIG = {
    'n_estimators': 100,
    'max_depth': 6,
    'random_state': 42
}


def quadratic_weighted_kappa(y_true, y_pred, num_classes=5):
    """
    Calculate Quadratic Weighted Kappa (QWK).
    Penalizes larger deviations more than smaller ones.
    """
    cm = confusion_matrix(y_true, y_pred, labels=list(range(1, num_classes + 1)))
    
    weights = np.zeros((num_classes, num_classes))
    for i in range(num_classes):
        for j in range(num_classes):
            weights[i, j] = ((i - j) ** 2) / ((num_classes - 1) ** 2)
    
    hist_true = np.bincount(y_true, minlength=num_classes + 1)[1:]
    hist_pred = np.bincount(y_pred, minlength=num_classes + 1)[1:]
    
    n = len(y_true)
    expected = np.outer(hist_true, hist_pred).astype(float) / n
    
    num = np.sum(weights * cm)
    den = np.sum(weights * expected)
    
    if den == 0:
        return 1.0
    
    return 1.0 - (num / den)


def load_o_score_data(data_path="data/processed/o_score_results.csv"):
    """Load O-Score data."""
    df = pd.read_csv(data_path)
    return df


def prepare_features(o_score_df):
    """
    Prepare features for ML model.
    
    Features are based on the same metrics as the O-Score,
    but the model learns the weighting itself.
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
    
    # Use only available columns
    available_cols = [c for c in feature_cols if c in o_score_df.columns]
    
    X = o_score_df[available_cols].copy()
    
    # Fill missing values
    X = X.fillna(X.median())
    
    return X, available_cols


def discretize_o_score(o_scores):
    """
    Discretize continuous O-Score into classes 1-5.
    """
    bins = [0, 1.8, 2.6, 3.4, 4.2, 5.1]
    labels = [1, 2, 3, 4, 5]
    return pd.cut(o_scores, bins=bins, labels=labels).astype(int)


def create_ensemble_classifier():
    """Create ensemble classifier."""
    estimators = []
    
    rf = RandomForestClassifier(
        n_estimators=MODEL_CONFIG['n_estimators'],
        max_depth=MODEL_CONFIG['max_depth'],
        random_state=MODEL_CONFIG['random_state'],
        n_jobs=-1
    )
    estimators.append(('rf', rf))
    
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
    Train O-Score classification model.
    """
    print("\n" + "="*50)
    print("O-SCORE MODEL TRAINING")
    print("="*50)
    
    # Prepare features
    X, feature_cols = prepare_features(o_score_df)
    
    # Target: discrete classes 1-5
    y = discretize_o_score(o_score_df['o_score'])
    
    print(f"\nData: {len(X)} samples, {len(feature_cols)} features")
    print(f"Features: {feature_cols}")
    print(f"\nO-Score class distribution:")
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
    print("\n--- Classifier (Classes 1-5) ---")
    classifier = create_ensemble_classifier()
    classifier.fit(X_train_scaled, y_train)
    
    # Evaluation
    y_pred = classifier.predict(X_test_scaled)
    
    # Base metrics
    accuracy = accuracy_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    # F1-Scores
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    # Kappa metrics
    kappa = cohen_kappa_score(y_test, y_pred)
    qwk = quadratic_weighted_kappa(np.array(y_test), np.array(y_pred))
    
    # Cross-Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(classifier, scaler.fit_transform(X), y, cv=cv)
    
    print(f"Accuracy: {accuracy:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"Macro-F1: {f1_macro:.3f}")
    print(f"Weighted-F1: {f1_weighted:.3f}")
    print(f"Cohen's Kappa: {kappa:.3f}")
    print(f"QWK: {qwk:.3f}")
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
    
    # Metrics
    metrics = {
        'classifier': {
            'accuracy': round(accuracy, 3),
            'mae': round(mae, 3),
            'f1_macro': round(f1_macro, 3),
            'f1_weighted': round(f1_weighted, 3),
            'kappa': round(kappa, 3),
            'qwk': round(qwk, 3),
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
    """Save the model."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_data, output_path)
    print(f"\nModel saved: {output_path}")


def load_model(model_path="models/o_score_model.joblib"):
    """Load the model."""
    return joblib.load(model_path)


def predict_o_score(model_data, X_new):
    """
    Prediction for new data.
    
    Returns:
        Array with predicted classes (1-5)
    """
    X_scaled = model_data['scaler'].transform(X_new)
    return model_data['classifier'].predict(X_scaled)


def print_summary(model_data):
    """Print summary."""
    metrics = model_data['metrics']
    
    print("\n" + "="*50)
    print("O-SCORE MODEL SUMMARY")
    print("="*50)
    
    print("\nClassifier (Classes 1-5):")
    print(f"   Accuracy: {metrics['classifier']['accuracy']}")
    print(f"   MAE: {metrics['classifier']['mae']}")
    print(f"   CV: {metrics['classifier']['cv_mean']} +/- {metrics['classifier']['cv_std']}")


if __name__ == "__main__":
    print("="*50)
    print("O-SCORE ML MODEL")
    print("="*50)
    
    # Load data
    data_path = Path("data/processed/o_score_results.csv")
    
    if not data_path.exists():
        print("O-Score data not found!")
        print("Please run first: python src/o_score.py")
        exit(1)
    
    o_score_df = load_o_score_data(data_path)
    print(f"Loaded: {len(o_score_df)} employees")
    
    # Training
    model_data = train_o_score_model(o_score_df)
    
    # Summary
    print_summary(model_data)
    
    # Save
    save_model(model_data)
    
    print("\n" + "="*50)
    print("TRAINING COMPLETED")
    print("="*50)
