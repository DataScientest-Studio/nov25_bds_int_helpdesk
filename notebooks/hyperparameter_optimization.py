"""
Hyperparameter-Optimierung für Help Desk Ticket Workflow Time Prediction
=========================================================================

Dieses Skript führt eine systematische Hyperparameter-Optimierung durch,
basierend auf den Erkenntnissen der explorativen Datenanalyse.

Zielvariable: wf_total_time (Gesamtbearbeitungszeit in Sekunden)

Autor: Data Science Pipeline
Datum: Januar 2025
"""

# =============================================================================
# 1. IMPORTS
# =============================================================================
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import json
import pickle

# Preprocessing
from sklearn.model_selection import (
    train_test_split, 
    TimeSeriesSplit, 
    cross_val_score,
    RandomizedSearchCV
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Modelle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# Metriken
from sklearn.metrics import (
    mean_absolute_error, 
    mean_squared_error, 
    r2_score,
    mean_absolute_percentage_error
)

# Hyperparameter-Optimierung
try:
    import optuna
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("Optuna nicht installiert. Verwende RandomizedSearchCV stattdessen.")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost nicht installiert.")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("LightGBM nicht installiert.")

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("CatBoost nicht installiert.")

warnings.filterwarnings('ignore')

# =============================================================================
# 2. KONFIGURATION
# =============================================================================
class Config:
    """Zentrale Konfigurationsklasse"""
    
    # Pfade (anpassen an Ihre Umgebung)
    DATA_DIR = Path('/content/drive/MyDrive/Colab Notebooks/nov25_bds_int_helpdesk/data/raw')
    OUTPUT_DIR = Path('./output')
    
    # Alternativ für lokale Ausführung:
    # DATA_DIR = Path('../data/raw')
    
    # Zufallsseed für Reproduzierbarkeit
    RANDOM_STATE = 42
    
    # Zielvariable
    TARGET = 'wf_total_time'
    
    # Zeitlicher Cutoff (basierend auf EDA: Drift vor 2017)
    CUTOFF_DATE = '2017-01-01'
    
    # Trainings-/Test-Split
    TEST_SIZE = 0.2
    
    # Cross-Validation
    CV_FOLDS = 5
    
    # Optuna Einstellungen
    N_TRIALS = 100  # Anzahl der Optimierungsversuche
    TIMEOUT = 3600  # Maximale Zeit in Sekunden (1 Stunde)
    
    # Feature-Gruppen
    NUMERIC_FEATURES = [
        'issue_contr_count',
        'issue_comments_count',
        'processing_steps',
        # Workflow-Zeiten (außer Zielvariable)
        'wf_in_review', 'wf_deployment', 'wf_resolved', 'wf_open',
        'wf_monitoring', 'wf_done', 'wf_pending_customer_approval',
        'wf_rejected', 'wf_testing_monitoring', 'wf_in_progress',
        'wf_reopened', 'wf_to_do', 'wf_validation',
        'wf_resolved_under_monitoring', 'wf_closed', 'wf_waiting',
        'wf_cancelled', 'wf_under_review', 'wf_approved',
        'wf_pending_deployment'
    ]
    
    CATEGORICAL_FEATURES = [
        'issue_type',
        'issue_priority', 
        'issue_status',
        'proj_type'  # internal/external
    ]


# =============================================================================
# 3. DATEN LADEN UND VORBEREITEN
# =============================================================================
def load_and_prepare_data(config: Config) -> pd.DataFrame:
    """
    Lädt die Daten und führt grundlegende Vorbereitungen durch.
    
    Returns:
        pd.DataFrame: Vorbereiteter Datensatz
    """
    print("=" * 60)
    print("DATEN LADEN")
    print("=" * 60)
    
    # Daten laden
    try:
        df = pd.read_csv(config.DATA_DIR / "issues.csv", low_memory=False)
        print(f"✓ Datensatz geladen: {df.shape[0]:,} Zeilen, {df.shape[1]} Spalten")
    except FileNotFoundError:
        print("FEHLER: issues.csv nicht gefunden!")
        print(f"Gesuchter Pfad: {config.DATA_DIR / 'issues.csv'}")
        print("\nBitte passen Sie Config.DATA_DIR an Ihren Pfad an.")
        return None
    
    # Timestamps konvertieren
    date_cols = ['started', 'ended', 'issue_created', 'issue_resolution_date', 'last_change_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='ISO8601', errors='coerce')
    
    # Zeitlichen Cutoff anwenden (basierend auf EDA: Drift vor 2017)
    cutoff = pd.Timestamp(config.CUTOFF_DATE, tz='UTC')
    if df['issue_created'].dt.tz is None:
        df['issue_created'] = df['issue_created'].dt.tz_localize('UTC')
    
    df_filtered = df[df['issue_created'] >= cutoff].copy()
    print(f"✓ Nach zeitlichem Filter (ab {config.CUTOFF_DATE}): {df_filtered.shape[0]:,} Zeilen")
    
    # Projekt-Typ extrahieren (internal vs external)
    proj = df_filtered['issue_proj'].astype('string').str.strip()
    df_filtered['proj_type'] = 'internal'
    df_filtered.loc[proj.str.match(r'^C\d{2}.+', na=False), 'proj_type'] = 'external'
    
    # Issue-Type bereinigen
    df_filtered['issue_type'] = df_filtered['issue_type'].replace({'Sub-task': 'Subtask'})
    
    # Zielvariable prüfen
    df_filtered = df_filtered[df_filtered[config.TARGET].notna()].copy()
    df_filtered = df_filtered[df_filtered[config.TARGET] > 0].copy()  # Nur positive Werte
    print(f"✓ Nach Entfernung fehlender/ungültiger Zielvariablen: {df_filtered.shape[0]:,} Zeilen")
    
    return df_filtered


def create_features(df: pd.DataFrame, config: Config) -> tuple:
    """
    Erstellt Feature-Matrix und Zielvariable.
    
    Returns:
        tuple: (X, y, feature_names)
    """
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    
    # Verfügbare Features filtern
    available_numeric = [f for f in config.NUMERIC_FEATURES if f in df.columns]
    available_categorical = [f for f in config.CATEGORICAL_FEATURES if f in df.columns]
    
    print(f"Numerische Features: {len(available_numeric)}")
    print(f"Kategorische Features: {len(available_categorical)}")
    
    # Feature-Matrix erstellen
    X = df[available_numeric + available_categorical].copy()
    
    # Zielvariable (Log-Transformation wegen Rechtsschiefe)
    y = np.log1p(df[config.TARGET].values)
    print(f"✓ Zielvariable log-transformiert (log1p)")
    
    # Numerische Features: Fehlende Werte mit Median füllen
    for col in available_numeric:
        if X[col].isna().any():
            median_val = X[col].median()
            X[col] = X[col].fillna(median_val)
    
    # Kategorische Features: Fehlende Werte als eigene Kategorie
    for col in available_categorical:
        X[col] = X[col].fillna('missing')
        X[col] = X[col].astype('category')
    
    # Zusätzliche Features erstellen
    # Ratio-Features (basierend auf Korrelationsanalyse)
    if 'wf_waiting' in X.columns and 'wf_open' in X.columns:
        X['waiting_to_open_ratio'] = X['wf_waiting'] / (X['wf_open'] + 1)
        available_numeric.append('waiting_to_open_ratio')
    
    if 'wf_in_progress' in X.columns and 'wf_open' in X.columns:
        X['progress_to_open_ratio'] = X['wf_in_progress'] / (X['wf_open'] + 1)
        available_numeric.append('progress_to_open_ratio')
    
    # Zeitliche Features
    if 'issue_created' in df.columns:
        X['created_month'] = df['issue_created'].dt.month
        X['created_dayofweek'] = df['issue_created'].dt.dayofweek
        X['created_hour'] = df['issue_created'].dt.hour
        available_numeric.extend(['created_month', 'created_dayofweek', 'created_hour'])
    
    print(f"✓ Zusätzliche Features erstellt")
    print(f"  Finale Feature-Anzahl: {X.shape[1]}")
    
    # Feature-Namen speichern
    feature_names = {
        'numeric': available_numeric,
        'categorical': available_categorical,
        'all': list(X.columns)
    }
    
    return X, y, feature_names


def encode_categorical_features(X: pd.DataFrame, feature_names: dict) -> pd.DataFrame:
    """
    Kodiert kategorische Features für Sklearn-kompatible Modelle.
    """
    X_encoded = X.copy()
    label_encoders = {}
    
    for col in feature_names['categorical']:
        if col in X_encoded.columns:
            le = LabelEncoder()
            X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
            label_encoders[col] = le
    
    return X_encoded, label_encoders


# =============================================================================
# 4. MODELL-DEFINITIONEN
# =============================================================================
def get_xgboost_params(trial) -> dict:
    """Definiert den Suchraum für XGBoost."""
    return {
        'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 200),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 50.0, log=True),
        'gamma': trial.suggest_float('gamma', 1e-8, 1.0, log=True),
        'random_state': Config.RANDOM_STATE,
        'n_jobs': -1,
        'objective': 'reg:squarederror',
        # Huber-Loss für Robustheit gegen Ausreißer:
        # 'objective': 'reg:pseudohubererror',
    }


def get_lightgbm_params(trial) -> dict:
    """Definiert den Suchraum für LightGBM."""
    return {
        'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'num_leaves': trial.suggest_int('num_leaves', 20, 150),
        'min_child_samples': trial.suggest_int('min_child_samples', 10, 200),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 50.0, log=True),
        'random_state': Config.RANDOM_STATE,
        'n_jobs': -1,
        'verbose': -1,
        'force_col_wise': True,
    }


def get_catboost_params(trial) -> dict:
    """Definiert den Suchraum für CatBoost."""
    return {
        'iterations': trial.suggest_int('iterations', 100, 2000),
        'depth': trial.suggest_int('depth', 4, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1e-8, 50.0, log=True),
        'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 200),
        'bagging_temperature': trial.suggest_float('bagging_temperature', 0.0, 1.0),
        'random_strength': trial.suggest_float('random_strength', 1e-8, 10.0, log=True),
        'random_state': Config.RANDOM_STATE,
        'verbose': False,
        'allow_writing_files': False,
    }


def get_random_forest_params(trial) -> dict:
    """Definiert den Suchraum für Random Forest."""
    return {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 5, 30),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 50),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 50),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.5, 0.8]),
        'random_state': Config.RANDOM_STATE,
        'n_jobs': -1,
    }


# =============================================================================
# 5. OPTUNA OPTIMIERUNG
# =============================================================================
class OptunaObjective:
    """Optuna Objective-Klasse für die Hyperparameter-Optimierung."""
    
    def __init__(self, X_train, y_train, model_type, cv_folds=5):
        self.X_train = X_train
        self.y_train = y_train
        self.model_type = model_type
        self.cv_folds = cv_folds
        self.best_model = None
        
    def __call__(self, trial):
        # Parameter basierend auf Modelltyp
        if self.model_type == 'xgboost' and XGBOOST_AVAILABLE:
            params = get_xgboost_params(trial)
            model = xgb.XGBRegressor(**params)
        elif self.model_type == 'lightgbm' and LIGHTGBM_AVAILABLE:
            params = get_lightgbm_params(trial)
            model = lgb.LGBMRegressor(**params)
        elif self.model_type == 'catboost' and CATBOOST_AVAILABLE:
            params = get_catboost_params(trial)
            model = cb.CatBoostRegressor(**params)
        elif self.model_type == 'random_forest':
            params = get_random_forest_params(trial)
            model = RandomForestRegressor(**params)
        else:
            raise ValueError(f"Unbekannter Modelltyp: {self.model_type}")
        
        # Cross-Validation mit TimeSeriesSplit
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)
        
        scores = []
        for train_idx, val_idx in tscv.split(self.X_train):
            X_tr, X_val = self.X_train.iloc[train_idx], self.X_train.iloc[val_idx]
            y_tr, y_val = self.y_train[train_idx], self.y_train[val_idx]
            
            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_val)
            
            # MAE als Metrik (robuster gegen Ausreißer)
            mae = mean_absolute_error(y_val, y_pred)
            scores.append(mae)
        
        return np.mean(scores)


def run_optuna_optimization(X_train, y_train, model_type, n_trials=100, timeout=3600):
    """
    Führt die Optuna-Optimierung durch.
    
    Args:
        X_train: Trainings-Features
        y_train: Trainings-Zielvariable
        model_type: 'xgboost', 'lightgbm', 'catboost', 'random_forest'
        n_trials: Anzahl der Versuche
        timeout: Maximale Zeit in Sekunden
    
    Returns:
        tuple: (beste_parameter, studie)
    """
    print(f"\n{'=' * 60}")
    print(f"OPTUNA OPTIMIERUNG: {model_type.upper()}")
    print(f"{'=' * 60}")
    
    # Optuna Study erstellen
    sampler = TPESampler(seed=Config.RANDOM_STATE)
    study = optuna.create_study(
        direction='minimize',  # MAE minimieren
        sampler=sampler,
        study_name=f'{model_type}_optimization'
    )
    
    # Objective erstellen
    objective = OptunaObjective(X_train, y_train, model_type)
    
    # Optimierung starten
    study.optimize(
        objective,
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=True,
        callbacks=[lambda study, trial: print(f"Trial {trial.number}: MAE = {trial.value:.4f}") 
                   if trial.number % 10 == 0 else None]
    )
    
    print(f"\n✓ Optimierung abgeschlossen!")
    print(f"  Beste MAE: {study.best_value:.4f}")
    print(f"  Beste Parameter:")
    for key, value in study.best_params.items():
        print(f"    {key}: {value}")
    
    return study.best_params, study


# =============================================================================
# 6. RANDOMIZED SEARCH (FALLBACK)
# =============================================================================
def run_randomized_search(X_train, y_train, model_type, n_iter=50):
    """
    Führt RandomizedSearchCV als Fallback durch (wenn Optuna nicht verfügbar).
    """
    print(f"\n{'=' * 60}")
    print(f"RANDOMIZED SEARCH: {model_type.upper()}")
    print(f"{'=' * 60}")
    
    # Parameter-Distributionen
    if model_type == 'xgboost' and XGBOOST_AVAILABLE:
        from scipy.stats import uniform, randint
        param_dist = {
            'n_estimators': randint(100, 2000),
            'max_depth': randint(3, 12),
            'learning_rate': uniform(0.01, 0.29),
            'min_child_weight': randint(1, 200),
            'subsample': uniform(0.6, 0.4),
            'colsample_bytree': uniform(0.6, 0.4),
            'reg_alpha': uniform(0, 10),
            'reg_lambda': uniform(1, 49),
        }
        model = xgb.XGBRegressor(random_state=Config.RANDOM_STATE, n_jobs=-1)
    
    elif model_type == 'lightgbm' and LIGHTGBM_AVAILABLE:
        from scipy.stats import uniform, randint
        param_dist = {
            'n_estimators': randint(100, 2000),
            'max_depth': randint(3, 12),
            'learning_rate': uniform(0.01, 0.29),
            'num_leaves': randint(20, 150),
            'min_child_samples': randint(10, 200),
            'subsample': uniform(0.6, 0.4),
            'colsample_bytree': uniform(0.6, 0.4),
            'reg_alpha': uniform(0, 10),
            'reg_lambda': uniform(1, 49),
        }
        model = lgb.LGBMRegressor(random_state=Config.RANDOM_STATE, n_jobs=-1, verbose=-1)
    
    elif model_type == 'random_forest':
        from scipy.stats import uniform, randint
        param_dist = {
            'n_estimators': randint(100, 1000),
            'max_depth': randint(5, 30),
            'min_samples_split': randint(2, 50),
            'min_samples_leaf': randint(1, 50),
            'max_features': ['sqrt', 'log2', 0.5, 0.8],
        }
        model = RandomForestRegressor(random_state=Config.RANDOM_STATE, n_jobs=-1)
    
    else:
        raise ValueError(f"Modell nicht verfügbar: {model_type}")
    
    # TimeSeriesSplit für Cross-Validation
    tscv = TimeSeriesSplit(n_splits=Config.CV_FOLDS)
    
    # RandomizedSearchCV
    search = RandomizedSearchCV(
        model,
        param_distributions=param_dist,
        n_iter=n_iter,
        cv=tscv,
        scoring='neg_mean_absolute_error',
        random_state=Config.RANDOM_STATE,
        n_jobs=-1,
        verbose=2
    )
    
    search.fit(X_train, y_train)
    
    print(f"\n✓ Suche abgeschlossen!")
    print(f"  Beste MAE: {-search.best_score_:.4f}")
    print(f"  Beste Parameter:")
    for key, value in search.best_params_.items():
        print(f"    {key}: {value}")
    
    return search.best_params_, search


# =============================================================================
# 7. MODELL TRAINING UND EVALUATION
# =============================================================================
def train_final_model(X_train, y_train, best_params, model_type):
    """Trainiert das finale Modell mit den besten Parametern."""
    
    print(f"\n{'=' * 60}")
    print(f"FINALES MODELL TRAINING: {model_type.upper()}")
    print(f"{'=' * 60}")
    
    if model_type == 'xgboost' and XGBOOST_AVAILABLE:
        model = xgb.XGBRegressor(**best_params, random_state=Config.RANDOM_STATE, n_jobs=-1)
    elif model_type == 'lightgbm' and LIGHTGBM_AVAILABLE:
        model = lgb.LGBMRegressor(**best_params, random_state=Config.RANDOM_STATE, n_jobs=-1, verbose=-1)
    elif model_type == 'catboost' and CATBOOST_AVAILABLE:
        model = cb.CatBoostRegressor(**best_params, random_state=Config.RANDOM_STATE, verbose=False)
    elif model_type == 'random_forest':
        model = RandomForestRegressor(**best_params, random_state=Config.RANDOM_STATE, n_jobs=-1)
    else:
        raise ValueError(f"Modell nicht verfügbar: {model_type}")
    
    model.fit(X_train, y_train)
    print("✓ Modell trainiert!")
    
    return model


def evaluate_model(model, X_test, y_test, model_name="Model"):
    """Evaluiert das Modell und gibt Metriken zurück."""
    
    print(f"\n{'=' * 60}")
    print(f"EVALUATION: {model_name}")
    print(f"{'=' * 60}")
    
    # Vorhersagen
    y_pred_log = model.predict(X_test)
    
    # Rücktransformation (expm1 für log1p)
    y_test_original = np.expm1(y_test)
    y_pred_original = np.expm1(y_pred_log)
    
    # Metriken auf Log-Skala
    mae_log = mean_absolute_error(y_test, y_pred_log)
    rmse_log = np.sqrt(mean_squared_error(y_test, y_pred_log))
    r2_log = r2_score(y_test, y_pred_log)
    
    # Metriken auf Original-Skala (Sekunden → Tage)
    y_test_days = y_test_original / 86400
    y_pred_days = y_pred_original / 86400
    
    mae_days = mean_absolute_error(y_test_days, y_pred_days)
    rmse_days = np.sqrt(mean_squared_error(y_test_days, y_pred_days))
    r2_original = r2_score(y_test_original, y_pred_original)
    
    # Median Absolute Error (robuster)
    medae_days = np.median(np.abs(y_test_days - y_pred_days))
    
    print(f"\nMetriken auf Log-Skala:")
    print(f"  MAE:  {mae_log:.4f}")
    print(f"  RMSE: {rmse_log:.4f}")
    print(f"  R²:   {r2_log:.4f}")
    
    print(f"\nMetriken auf Original-Skala (Tage):")
    print(f"  MAE:    {mae_days:.2f} Tage")
    print(f"  MedAE:  {medae_days:.2f} Tage")
    print(f"  RMSE:   {rmse_days:.2f} Tage")
    print(f"  R²:     {r2_original:.4f}")
    
    metrics = {
        'mae_log': mae_log,
        'rmse_log': rmse_log,
        'r2_log': r2_log,
        'mae_days': mae_days,
        'medae_days': medae_days,
        'rmse_days': rmse_days,
        'r2_original': r2_original
    }
    
    return metrics, y_pred_original


def plot_feature_importance(model, feature_names, model_name, top_n=20):
    """Visualisiert die Feature Importance."""
    
    # Feature Importance extrahieren
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        print("Feature Importance nicht verfügbar für dieses Modell.")
        return
    
    # DataFrame erstellen
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    # Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=importance_df.head(top_n),
        x='Importance',
        y='Feature',
        palette='viridis'
    )
    plt.title(f'Top {top_n} Feature Importances - {model_name}', fontsize=14)
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig(f'feature_importance_{model_name.lower().replace(" ", "_")}.png', dpi=150)
    plt.show()
    
    return importance_df


def plot_predictions(y_test, y_pred, model_name):
    """Visualisiert Vorhersagen vs. tatsächliche Werte."""
    
    # In Tage konvertieren
    y_test_days = y_test / 86400
    y_pred_days = y_pred / 86400
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Scatter Plot
    ax1 = axes[0]
    ax1.scatter(y_test_days, y_pred_days, alpha=0.3, s=10)
    max_val = max(y_test_days.max(), y_pred_days.max())
    ax1.plot([0, max_val], [0, max_val], 'r--', label='Perfekte Vorhersage')
    ax1.set_xlabel('Tatsächliche Werte (Tage)')
    ax1.set_ylabel('Vorhergesagte Werte (Tage)')
    ax1.set_title(f'{model_name}: Vorhersage vs. Tatsächlich')
    ax1.legend()
    
    # Residuen-Plot
    ax2 = axes[1]
    residuals = y_test_days - y_pred_days
    ax2.scatter(y_pred_days, residuals, alpha=0.3, s=10)
    ax2.axhline(y=0, color='r', linestyle='--')
    ax2.set_xlabel('Vorhergesagte Werte (Tage)')
    ax2.set_ylabel('Residuen (Tage)')
    ax2.set_title(f'{model_name}: Residuen-Plot')
    
    plt.tight_layout()
    plt.savefig(f'predictions_{model_name.lower().replace(" ", "_")}.png', dpi=150)
    plt.show()


# =============================================================================
# 8. HAUPTPROGRAMM
# =============================================================================
def main():
    """Hauptfunktion für die Hyperparameter-Optimierung."""
    
    print("\n" + "=" * 70)
    print("   HYPERPARAMETER-OPTIMIERUNG FÜR HELP DESK TICKET PREDICTION")
    print("=" * 70)
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    config = Config()
    
    # 1. Daten laden
    df = load_and_prepare_data(config)
    if df is None:
        return
    
    # 2. Features erstellen
    X, y, feature_names = create_features(df, config)
    
    # 3. Kategorische Features kodieren (für Sklearn-kompatible Modelle)
    X_encoded, label_encoders = encode_categorical_features(X, feature_names)
    
    # 4. Train/Test Split (zeitbasiert)
    # Sortieren nach Erstellungsdatum
    df_sorted = df.sort_values('issue_created').reset_index(drop=True)
    X_sorted = X_encoded.loc[df_sorted.index].reset_index(drop=True)
    y_sorted = y[df_sorted.index.values]
    
    # Letzten Teil als Test-Set
    split_idx = int(len(X_sorted) * (1 - config.TEST_SIZE))
    X_train, X_test = X_sorted.iloc[:split_idx], X_sorted.iloc[split_idx:]
    y_train, y_test = y_sorted[:split_idx], y_sorted[split_idx:]
    
    print(f"\n✓ Train/Test Split (zeitbasiert):")
    print(f"  Training: {len(X_train):,} Samples")
    print(f"  Test:     {len(X_test):,} Samples")
    
    # 5. Modelle optimieren
    results = {}
    
    # Verfügbare Modelle ermitteln
    available_models = ['random_forest']  # Immer verfügbar
    if XGBOOST_AVAILABLE:
        available_models.append('xgboost')
    if LIGHTGBM_AVAILABLE:
        available_models.append('lightgbm')
    if CATBOOST_AVAILABLE:
        available_models.append('catboost')
    
    print(f"\nVerfügbare Modelle: {', '.join(available_models)}")
    
    for model_type in available_models:
        try:
            # Hyperparameter-Optimierung
            if OPTUNA_AVAILABLE:
                best_params, study = run_optuna_optimization(
                    X_train, y_train, model_type,
                    n_trials=config.N_TRIALS,
                    timeout=config.TIMEOUT
                )
            else:
                best_params, search = run_randomized_search(
                    X_train, y_train, model_type,
                    n_iter=50
                )
            
            # Finales Modell trainieren
            model = train_final_model(X_train, y_train, best_params, model_type)
            
            # Evaluation
            metrics, y_pred = evaluate_model(model, X_test, y_test, model_type.upper())
            
            # Feature Importance
            importance_df = plot_feature_importance(
                model, feature_names['all'], model_type.upper()
            )
            
            # Vorhersage-Plots
            plot_predictions(np.expm1(y_test), y_pred, model_type.upper())
            
            # Ergebnisse speichern
            results[model_type] = {
                'best_params': best_params,
                'metrics': metrics,
                'model': model,
                'feature_importance': importance_df
            }
            
        except Exception as e:
            print(f"\nFEHLER bei {model_type}: {str(e)}")
            continue
    
    # 6. Ergebnisse vergleichen
    print("\n" + "=" * 70)
    print("   ERGEBNISVERGLEICH")
    print("=" * 70)
    
    comparison = []
    for model_name, result in results.items():
        comparison.append({
            'Modell': model_name.upper(),
            'MAE (Tage)': result['metrics']['mae_days'],
            'MedAE (Tage)': result['metrics']['medae_days'],
            'RMSE (Tage)': result['metrics']['rmse_days'],
            'R²': result['metrics']['r2_original']
        })
    
    comparison_df = pd.DataFrame(comparison).sort_values('MAE (Tage)')
    print("\n")
    print(comparison_df.to_string(index=False))
    
    # Bestes Modell
    best_model_name = comparison_df.iloc[0]['Modell'].lower()
    print(f"\n✓ Bestes Modell: {best_model_name.upper()}")
    
    # 7. Beste Parameter exportieren
    print("\n" + "=" * 70)
    print("   BESTE PARAMETER EXPORTIEREN")
    print("=" * 70)
    
    # Parameter als JSON speichern
    export_params = {
        model: {
            'best_params': result['best_params'],
            'metrics': result['metrics']
        }
        for model, result in results.items()
    }
    
    with open('best_hyperparameters.json', 'w') as f:
        json.dump(export_params, f, indent=2, default=str)
    print("✓ Parameter gespeichert in: best_hyperparameters.json")
    
    # Bestes Modell als Pickle speichern
    best_model = results[best_model_name]['model']
    with open(f'best_model_{best_model_name}.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    print(f"✓ Modell gespeichert in: best_model_{best_model_name}.pkl")
    
    print("\n" + "=" * 70)
    print(f"   FERTIG: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return results, comparison_df


# =============================================================================
# 9. SCHNELLSTART-FUNKTIONEN
# =============================================================================
def quick_baseline(X_train, y_train, X_test, y_test):
    """
    Trainiert schnelle Baseline-Modelle ohne Hyperparameter-Optimierung.
    Nützlich für einen ersten Überblick.
    """
    print("\n" + "=" * 60)
    print("SCHNELLE BASELINE-MODELLE")
    print("=" * 60)
    
    baselines = {}
    
    # 1. Random Forest Baseline
    print("\n1. Random Forest (Default)...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    mae_rf = mean_absolute_error(np.expm1(y_test), np.expm1(y_pred_rf)) / 86400
    print(f"   MAE: {mae_rf:.2f} Tage")
    baselines['random_forest'] = mae_rf
    
    # 2. XGBoost Baseline
    if XGBOOST_AVAILABLE:
        print("\n2. XGBoost (Default)...")
        xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        xgb_model.fit(X_train, y_train)
        y_pred_xgb = xgb_model.predict(X_test)
        mae_xgb = mean_absolute_error(np.expm1(y_test), np.expm1(y_pred_xgb)) / 86400
        print(f"   MAE: {mae_xgb:.2f} Tage")
        baselines['xgboost'] = mae_xgb
    
    # 3. LightGBM Baseline
    if LIGHTGBM_AVAILABLE:
        print("\n3. LightGBM (Default)...")
        lgb_model = lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
        lgb_model.fit(X_train, y_train)
        y_pred_lgb = lgb_model.predict(X_test)
        mae_lgb = mean_absolute_error(np.expm1(y_test), np.expm1(y_pred_lgb)) / 86400
        print(f"   MAE: {mae_lgb:.2f} Tage")
        baselines['lightgbm'] = mae_lgb
    
    print("\n" + "-" * 40)
    print("Baseline-Vergleich (MAE in Tagen):")
    for name, mae in sorted(baselines.items(), key=lambda x: x[1]):
        print(f"  {name}: {mae:.2f}")
    
    return baselines


# =============================================================================
# AUSFÜHRUNG
# =============================================================================
if __name__ == "__main__":
    # Hauptprogramm ausführen
    results, comparison = main()
    
    # Optional: Nur Baseline testen
    # quick_baseline(X_train, y_train, X_test, y_test)
