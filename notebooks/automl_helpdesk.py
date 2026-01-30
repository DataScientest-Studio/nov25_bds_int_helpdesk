"""
AutoML Pipeline für Help Desk Ticket Prediction
================================================
Basierend auf der Data Inventory Analyse (01_Data-inventory-4.ipynb)

Mögliche Vorhersageziele:
1. Total Workflow Time (Regression) - Wie lange dauert ein Ticket?
2. Issue Resolution (Classification) - Wird es gelöst, abgelehnt, etc.?
3. Priority Classification - Prioritätsvorhersage basierend auf Features

Autor: AutoML Pipeline
Datum: Januar 2025
"""

# =============================================================================
# 1. IMPORT LIBRARIES
# =============================================================================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pathlib import Path
from datetime import datetime

# Preprocessing
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Feature Selection
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, mutual_info_classif

# Models
from sklearn.linear_model import LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    AdaBoostClassifier, AdaBoostRegressor,
    ExtraTreesClassifier, ExtraTreesRegressor
)
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

# Metrics
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)

# Hyperparameter Tuning
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# Optional: AutoML Libraries (installieren falls nicht vorhanden)
try:
    import autosklearn.classification
    import autosklearn.regression
    AUTOSKLEARN_AVAILABLE = True
except ImportError:
    AUTOSKLEARN_AVAILABLE = False
    print("⚠️ auto-sklearn nicht verfügbar - nutze manuelle AutoML Pipeline")

try:
    from flaml import AutoML as FLAMLAutoML
    FLAML_AVAILABLE = True
except ImportError:
    FLAML_AVAILABLE = False
    print("⚠️ FLAML nicht verfügbar")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️ LightGBM nicht verfügbar")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost nicht verfügbar")

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

print("✅ Libraries erfolgreich importiert")


# =============================================================================
# 2. CONFIGURATION
# =============================================================================
class Config:
    """Zentrale Konfiguration für AutoML Pipeline"""
    
    # Pfade (anpassen für lokale/Colab Umgebung)
    # Google Colab:
    # DATA_PATH = Path('/content/drive/MyDrive/Colab_Projekte/nov25_bds_int_helpdesk/data/raw')
    # Lokal:
    DATA_PATH = Path('../data/raw')
    
    # Dateien
    ISSUES_FILE = "issues.csv"
    SNAPSHOT_FILE = "issues_snapshot.csv"
    CHANGE_HISTORY_FILE = "issues_change_history.csv"
    UTTERANCES_FILE = "sample_utterances.csv"
    
    # Cutoff Datum (aus Data Inventory)
    CUTOFF_DATE = pd.Timestamp("2015-07-01", tz="UTC")
    
    # Modell-Konfiguration
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    CV_FOLDS = 5
    
    # AutoML Zeitlimit (Sekunden)
    AUTOML_TIME_LIMIT = 300  # 5 Minuten für schnellen Test
    
    # Target Variable Options
    TARGETS = {
        'regression': ['wf_total_time', 'processing_steps'],
        'classification': ['issue_resolution', 'issue_priority', 'issue_status']
    }


# =============================================================================
# 3. DATA LOADING & PREPROCESSING
# =============================================================================
class DataLoader:
    """Lädt und bereitet Daten vor basierend auf Data Inventory Analyse"""
    
    def __init__(self, config: Config):
        self.config = config
        self.dfi = None  # Issues DataFrame
        self.dfs = None  # Snapshot DataFrame
        
    def load_data(self):
        """Lädt die Hauptdatasets"""
        print("📂 Lade Daten...")
        
        try:
            self.dfi = pd.read_csv(
                self.config.DATA_PATH / self.config.ISSUES_FILE, 
                low_memory=False
            )
            print(f"  ✓ Issues: {self.dfi.shape[0]:,} Zeilen, {self.dfi.shape[1]} Spalten")
            
            self.dfs = pd.read_csv(
                self.config.DATA_PATH / self.config.SNAPSHOT_FILE, 
                low_memory=False
            )
            print(f"  ✓ Snapshot: {self.dfs.shape[0]:,} Zeilen, {self.dfs.shape[1]} Spalten")
            
        except FileNotFoundError as e:
            print(f"⚠️ Datei nicht gefunden: {e}")
            print("📝 Erstelle Beispieldaten für Demo...")
            self._create_demo_data()
            
        return self
    
    def _create_demo_data(self):
        """Erstellt synthetische Demo-Daten basierend auf Data Inventory Erkenntnissen"""
        np.random.seed(42)
        n_samples = 10000
        
        # Basierend auf den Erkenntnissen aus der Data Inventory
        issue_types = ['Ticket', 'Service', 'Story', 'HD Service', 'Subtask', 
                       'Task', 'Bug', 'Project', 'Epic', 'Vacation']
        priorities = ['Medium', 'High', 'Low', 'unknown', 'Blocker', 'Highest', 'Lowest']
        resolutions = ['Done', 'Won\'t Do', 'Duplicate', 'Cannot Reproduce']
        statuses = ['done', 'closed', 'validation', 'open', 'resolved', 'waiting',
                   'pending_deployment', 'in_progress', 'approved', 'to_do']
        
        # Gewichtungen basierend auf Data Inventory
        type_weights = [0.6, 0.1, 0.08, 0.05, 0.05, 0.03, 0.03, 0.02, 0.02, 0.02]
        priority_weights = [0.45, 0.25, 0.15, 0.08, 0.03, 0.02, 0.02]
        resolution_weights = [0.85, 0.08, 0.04, 0.03]
        
        self.dfi = pd.DataFrame({
            'id': range(n_samples),
            'issue_type': np.random.choice(issue_types, n_samples, p=type_weights),
            'issue_priority': np.random.choice(priorities, n_samples, p=priority_weights),
            'issue_resolution': np.random.choice(resolutions, n_samples, p=resolution_weights),
            'issue_status': np.random.choice(statuses, n_samples),
            'issue_contr_count': np.random.poisson(1.5, n_samples),
            'issue_comments_count': np.random.poisson(3, n_samples),
            'processing_steps': np.random.poisson(4, n_samples) + 1,
            
            # Workflow Zeiten (in Sekunden) - stark rechtsschief wie im Data Inventory
            'wf_open': np.random.exponential(5000000, n_samples),
            'wf_in_progress': np.random.exponential(1000000, n_samples),
            'wf_waiting': np.random.exponential(1700000, n_samples),
            'wf_resolved': np.random.exponential(340000, n_samples),
            'wf_done': np.random.exponential(9000000, n_samples) * np.random.binomial(1, 0.02, n_samples),
            'wf_validation': np.random.exponential(2000000, n_samples) * np.random.binomial(1, 0.06, n_samples),
            
            # Projekt-Typ
            'proj_type': np.random.choice(['internal', 'external'], n_samples, p=[0.3, 0.7]),
        })
        
        # Total time als Summe der Workflow-Zeiten
        wf_cols = [c for c in self.dfi.columns if c.startswith('wf_')]
        self.dfi['wf_total_time'] = self.dfi[wf_cols].sum(axis=1)
        
        # Timestamps
        base_date = pd.Timestamp('2016-01-01')
        self.dfi['issue_created'] = base_date + pd.to_timedelta(
            np.random.randint(0, 365*7, n_samples), unit='d'
        )
        
        print(f"  ✓ Demo-Daten erstellt: {n_samples:,} Samples")
        
    def preprocess(self):
        """Führt Preprocessing durch basierend auf Data Inventory Erkenntnissen"""
        print("\n🔧 Preprocessing...")
        
        # 1. Datumsfilter (wie im Data Inventory)
        if 'issue_created' in self.dfi.columns:
            self.dfi['issue_created'] = pd.to_datetime(
                self.dfi['issue_created'], 
                errors='coerce'
            )
            # Timezone handling
            if self.dfi['issue_created'].dt.tz is not None:
                initial_count = len(self.dfi)
                self.dfi = self.dfi[
                    self.dfi['issue_created'] >= self.config.CUTOFF_DATE
                ]
                print(f"  ✓ Datumsfilter: {initial_count - len(self.dfi):,} Zeilen entfernt")
        
        # 2. Issue Type Cleaning (Sub-task -> Subtask)
        if 'issue_type' in self.dfi.columns:
            self.dfi['issue_type'] = self.dfi['issue_type'].replace({'Sub-task': 'Subtask'})
            print("  ✓ Issue Types bereinigt")
        
        # 3. Projekt-Typ Extraktion (falls nicht vorhanden)
        if 'proj_type' not in self.dfi.columns and 'issue_proj' in self.dfi.columns:
            proj = self.dfi['issue_proj'].astype('string').str.strip()
            self.dfi['proj_type'] = 'internal'
            external_mask = proj.str.match(r'^C\d{2}.+', na=False)
            self.dfi.loc[external_mask, 'proj_type'] = 'external'
            print("  ✓ Projekt-Typ extrahiert")
        
        # 4. Missing Values Info
        missing_pct = (self.dfi.isna().sum() / len(self.dfi) * 100).round(2)
        high_missing = missing_pct[missing_pct > 40]
        if len(high_missing) > 0:
            print(f"  ⚠️ Hohe Missing Rate (>40%): {list(high_missing.index)}")
        
        return self
    
    def get_features_and_target(self, target_col: str, task_type: str = 'auto'):
        """Extrahiert Features und Target für ML"""
        
        if target_col not in self.dfi.columns:
            raise ValueError(f"Target '{target_col}' nicht in Daten gefunden")
        
        # Auto-detect task type
        if task_type == 'auto':
            if self.dfi[target_col].dtype in ['object', 'category']:
                task_type = 'classification'
            elif self.dfi[target_col].nunique() < 10:
                task_type = 'classification'
            else:
                task_type = 'regression'
        
        print(f"\n🎯 Target: {target_col} ({task_type})")
        
        # Feature Selection
        exclude_cols = [
            'id', 'idx', 'issueid', target_col,
            'issue_created', 'started', 'ended', 
            'issue_resolution_date', 'last_change_date',
            'issue_reporter', 'issue_assignee', 'issue_proj', 'issue_num'
        ]
        
        # Workflow-Zeiten nur bei Classification verwenden (nicht bei Time-Prediction)
        if target_col == 'wf_total_time':
            exclude_cols.extend([c for c in self.dfi.columns if c.startswith('wf_')])
        
        feature_cols = [c for c in self.dfi.columns 
                       if c not in exclude_cols 
                       and not c.startswith('wfe_')]
        
        X = self.dfi[feature_cols].copy()
        y = self.dfi[target_col].copy()
        
        # Drop rows with missing target
        valid_mask = y.notna()
        X = X[valid_mask]
        y = y[valid_mask]
        
        print(f"  Features: {len(feature_cols)}")
        print(f"  Samples: {len(y):,}")
        
        return X, y, task_type, feature_cols


# =============================================================================
# 4. FEATURE ENGINEERING
# =============================================================================
class FeatureEngineer:
    """Feature Engineering Pipeline"""
    
    def __init__(self):
        self.numeric_cols = []
        self.categorical_cols = []
        self.preprocessor = None
        
    def fit_transform(self, X: pd.DataFrame):
        """Identifiziert und transformiert Features"""
        
        # Identifiziere Spaltentypen
        self.numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        print(f"\n📊 Feature Engineering:")
        print(f"  Numerische Features: {len(self.numeric_cols)}")
        print(f"  Kategorische Features: {len(self.categorical_cols)}")
        
        # Preprocessing Pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_cols),
                ('cat', categorical_transformer, self.categorical_cols)
            ],
            remainder='drop'
        )
        
        X_transformed = self.preprocessor.fit_transform(X)
        
        # Feature Namen extrahieren
        feature_names = self.numeric_cols.copy()
        if self.categorical_cols:
            cat_features = self.preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(self.categorical_cols)
            feature_names.extend(cat_features.tolist())
        
        print(f"  Transformierte Features: {X_transformed.shape[1]}")
        
        return X_transformed, feature_names
    
    def transform(self, X: pd.DataFrame):
        """Transformiert neue Daten"""
        return self.preprocessor.transform(X)


# =============================================================================
# 5. AUTOML ENGINE
# =============================================================================
class AutoMLEngine:
    """Custom AutoML Engine mit mehreren Algorithmen"""
    
    def __init__(self, task_type: str, config: Config):
        self.task_type = task_type
        self.config = config
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_score = None
        
    def _get_models(self):
        """Definiert Modell-Pool basierend auf Task"""
        
        if self.task_type == 'classification':
            models = {
                'Logistic Regression': LogisticRegression(
                    random_state=self.config.RANDOM_STATE,
                    max_iter=1000,
                    n_jobs=-1
                ),
                'Random Forest': RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1
                ),
                'Gradient Boosting': GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE
                ),
                'Extra Trees': ExtraTreesClassifier(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1
                ),
                'KNN': KNeighborsClassifier(n_neighbors=5, n_jobs=-1),
                'Decision Tree': DecisionTreeClassifier(
                    random_state=self.config.RANDOM_STATE
                ),
            }
            
            if XGBOOST_AVAILABLE:
                models['XGBoost'] = xgb.XGBClassifier(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=0
                )
            
            if LIGHTGBM_AVAILABLE:
                models['LightGBM'] = lgb.LGBMClassifier(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1,
                    verbose=-1
                )
                
        else:  # regression
            models = {
                'Ridge': Ridge(random_state=self.config.RANDOM_STATE),
                'Lasso': Lasso(random_state=self.config.RANDOM_STATE),
                'ElasticNet': ElasticNet(random_state=self.config.RANDOM_STATE),
                'Random Forest': RandomForestRegressor(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1
                ),
                'Gradient Boosting': GradientBoostingRegressor(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE
                ),
                'Extra Trees': ExtraTreesRegressor(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1
                ),
                'KNN': KNeighborsRegressor(n_neighbors=5, n_jobs=-1),
                'Decision Tree': DecisionTreeRegressor(
                    random_state=self.config.RANDOM_STATE
                ),
            }
            
            if XGBOOST_AVAILABLE:
                models['XGBoost'] = xgb.XGBRegressor(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=0
                )
            
            if LIGHTGBM_AVAILABLE:
                models['LightGBM'] = lgb.LGBMRegressor(
                    n_estimators=100,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1,
                    verbose=-1
                )
        
        return models
    
    def train_and_evaluate(self, X_train, X_test, y_train, y_test):
        """Trainiert alle Modelle und evaluiert sie"""
        
        self.models = self._get_models()
        
        print(f"\n🤖 Training {len(self.models)} Modelle...")
        print("-" * 60)
        
        for name, model in self.models.items():
            try:
                # Training
                start_time = datetime.now()
                model.fit(X_train, y_train)
                train_time = (datetime.now() - start_time).total_seconds()
                
                # Prediction
                y_pred = model.predict(X_test)
                
                # Evaluation
                if self.task_type == 'classification':
                    # Multi-class handling
                    if len(np.unique(y_train)) > 2:
                        avg = 'weighted'
                    else:
                        avg = 'binary'
                    
                    metrics = {
                        'accuracy': accuracy_score(y_test, y_pred),
                        'precision': precision_score(y_test, y_pred, average=avg, zero_division=0),
                        'recall': recall_score(y_test, y_pred, average=avg, zero_division=0),
                        'f1': f1_score(y_test, y_pred, average=avg, zero_division=0),
                    }
                    main_metric = metrics['f1']
                    
                else:  # regression
                    metrics = {
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                        'mae': mean_absolute_error(y_test, y_pred),
                        'r2': r2_score(y_test, y_pred),
                    }
                    main_metric = metrics['r2']
                
                metrics['train_time'] = train_time
                self.results[name] = metrics
                
                # Output
                if self.task_type == 'classification':
                    print(f"  {name:25s} | F1: {metrics['f1']:.4f} | Acc: {metrics['accuracy']:.4f} | Time: {train_time:.2f}s")
                else:
                    print(f"  {name:25s} | R²: {metrics['r2']:.4f} | RMSE: {metrics['rmse']:.2f} | Time: {train_time:.2f}s")
                
                # Best model tracking
                if self.best_score is None or main_metric > self.best_score:
                    self.best_score = main_metric
                    self.best_model = (name, model)
                    
            except Exception as e:
                print(f"  {name:25s} | ❌ Fehler: {str(e)[:50]}")
        
        print("-" * 60)
        print(f"🏆 Bestes Modell: {self.best_model[0]} (Score: {self.best_score:.4f})")
        
        return self
    
    def get_results_df(self):
        """Gibt Ergebnisse als DataFrame zurück"""
        df = pd.DataFrame(self.results).T
        df = df.sort_values(df.columns[0], ascending=False)
        return df
    
    def hyperparameter_tuning(self, X_train, y_train, model_name: str = None):
        """Führt Hyperparameter-Tuning für das beste Modell durch"""
        
        if model_name is None:
            model_name = self.best_model[0]
        
        print(f"\n🔧 Hyperparameter Tuning für {model_name}...")
        
        # Parameter Grids
        param_grids = {
            'Random Forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'Gradient Boosting': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 1.0]
            },
            'XGBoost': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0]
            },
            'LightGBM': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'num_leaves': [31, 50, 100]
            }
        }
        
        if model_name not in param_grids:
            print(f"  ⚠️ Kein Parameter Grid für {model_name} definiert")
            return self.best_model[1]
        
        model = self.models[model_name]
        param_grid = param_grids[model_name]
        
        # Scoring
        scoring = 'f1_weighted' if self.task_type == 'classification' else 'r2'
        
        # RandomizedSearchCV (schneller als GridSearchCV)
        search = RandomizedSearchCV(
            model,
            param_distributions=param_grid,
            n_iter=20,
            cv=3,
            scoring=scoring,
            random_state=self.config.RANDOM_STATE,
            n_jobs=-1,
            verbose=1
        )
        
        search.fit(X_train, y_train)
        
        print(f"\n  Beste Parameter: {search.best_params_}")
        print(f"  Bester CV Score: {search.best_score_:.4f}")
        
        return search.best_estimator_


# =============================================================================
# 6. MODEL EVALUATION & VISUALIZATION
# =============================================================================
class ModelEvaluator:
    """Umfassende Modell-Evaluation und Visualisierung"""
    
    def __init__(self, task_type: str):
        self.task_type = task_type
        
    def plot_comparison(self, results_df: pd.DataFrame, save_path: str = None):
        """Visualisiert Modellvergleich"""
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        if self.task_type == 'classification':
            # Accuracy vs F1
            metrics = ['accuracy', 'f1']
            colors = ['skyblue', 'coral']
        else:
            # R² und RMSE
            metrics = ['r2', 'mae']
            colors = ['skyblue', 'coral']
        
        for ax, metric, color in zip(axes, metrics, colors):
            sorted_df = results_df.sort_values(metric, ascending=False)
            bars = ax.barh(sorted_df.index, sorted_df[metric], color=color)
            ax.set_xlabel(metric.upper())
            ax.set_title(f'Modellvergleich: {metric.upper()}')
            
            # Werte anzeigen
            for bar, val in zip(bars, sorted_df[metric]):
                ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{val:.3f}', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Plot gespeichert: {save_path}")
        
        plt.show()
        
    def plot_confusion_matrix(self, y_true, y_pred, labels=None, save_path: str = None):
        """Plottet Confusion Matrix"""
        
        if self.task_type != 'classification':
            print("Confusion Matrix nur für Classification verfügbar")
            return
        
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=labels, yticklabels=labels)
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.show()
        
    def plot_feature_importance(self, model, feature_names, top_n: int = 20, save_path: str = None):
        """Plottet Feature Importance"""
        
        if not hasattr(model, 'feature_importances_'):
            print("Modell unterstützt keine Feature Importance")
            return
        
        importance = model.feature_importances_
        indices = np.argsort(importance)[::-1][:top_n]
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(top_n), importance[indices][::-1], color='teal')
        plt.yticks(range(top_n), [feature_names[i] for i in indices][::-1])
        plt.xlabel('Importance')
        plt.title(f'Top {top_n} Feature Importances')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.show()
        
    def regression_diagnostics(self, y_true, y_pred, save_path: str = None):
        """Regression Diagnostik Plots"""
        
        if self.task_type != 'regression':
            print("Regression Diagnostics nur für Regression verfügbar")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Actual vs Predicted
        ax = axes[0, 0]
        ax.scatter(y_true, y_pred, alpha=0.5, s=10)
        ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        ax.set_xlabel('Actual')
        ax.set_ylabel('Predicted')
        ax.set_title('Actual vs Predicted')
        
        # 2. Residuals vs Predicted
        ax = axes[0, 1]
        residuals = y_true - y_pred
        ax.scatter(y_pred, residuals, alpha=0.5, s=10)
        ax.axhline(y=0, color='r', linestyle='--')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Residuals')
        ax.set_title('Residuals vs Predicted')
        
        # 3. Residuals Distribution
        ax = axes[1, 0]
        ax.hist(residuals, bins=50, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Residual')
        ax.set_ylabel('Frequency')
        ax.set_title('Residuals Distribution')
        
        # 4. QQ Plot
        ax = axes[1, 1]
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.show()


# =============================================================================
# 7. MAIN PIPELINE
# =============================================================================
def run_automl_pipeline(
    target_col: str = 'issue_resolution',
    task_type: str = 'auto',
    use_flaml: bool = False,
    tune_hyperparams: bool = True
):
    """
    Hauptfunktion für AutoML Pipeline
    
    Parameters:
    -----------
    target_col : str
        Zielvariable für Vorhersage
        - 'wf_total_time': Gesamte Bearbeitungszeit (Regression)
        - 'issue_resolution': Resolution Kategorie (Classification)
        - 'issue_priority': Priorität (Classification)
        - 'processing_steps': Anzahl Schritte (Regression)
        
    task_type : str
        'classification', 'regression' oder 'auto'
        
    use_flaml : bool
        Ob FLAML AutoML verwendet werden soll
        
    tune_hyperparams : bool
        Ob Hyperparameter-Tuning durchgeführt werden soll
    """
    
    print("=" * 70)
    print("🚀 AutoML Pipeline für Help Desk Ticket Prediction")
    print("=" * 70)
    
    # 1. Config
    config = Config()
    
    # 2. Data Loading
    loader = DataLoader(config)
    loader.load_data().preprocess()
    
    # 3. Feature & Target
    X, y, task_type, feature_cols = loader.get_features_and_target(target_col, task_type)
    
    # 4. Label Encoding für Classification
    label_encoder = None
    if task_type == 'classification' and y.dtype == 'object':
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)
        print(f"  Classes: {label_encoder.classes_}")
    
    # 5. Feature Engineering
    fe = FeatureEngineer()
    X_transformed, feature_names = fe.fit_transform(X)
    
    # 6. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_transformed, y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=y if task_type == 'classification' else None
    )
    
    print(f"\n📊 Data Split:")
    print(f"  Training: {X_train.shape[0]:,} samples")
    print(f"  Test: {X_test.shape[0]:,} samples")
    
    # 7. AutoML Training
    if use_flaml and FLAML_AVAILABLE:
        print("\n🔄 Verwende FLAML AutoML...")
        automl = FLAMLAutoML()
        automl.fit(
            X_train, y_train,
            task=task_type,
            time_budget=config.AUTOML_TIME_LIMIT,
            metric='f1' if task_type == 'classification' else 'r2',
            verbose=1
        )
        
        print(f"\n🏆 Bestes Modell: {automl.best_estimator}")
        y_pred = automl.predict(X_test)
        best_model = automl.model
        
    else:
        # Custom AutoML Engine
        engine = AutoMLEngine(task_type, config)
        engine.train_and_evaluate(X_train, X_test, y_train, y_test)
        
        # Hyperparameter Tuning
        if tune_hyperparams:
            best_model = engine.hyperparameter_tuning(X_train, y_train)
        else:
            best_model = engine.best_model[1]
        
        y_pred = best_model.predict(X_test)
    
    # 8. Final Evaluation
    print("\n" + "=" * 70)
    print("📈 FINALE EVALUATION")
    print("=" * 70)
    
    evaluator = ModelEvaluator(task_type)
    
    if task_type == 'classification':
        if label_encoder:
            print(classification_report(y_test, y_pred, 
                                       target_names=label_encoder.classes_))
        else:
            print(classification_report(y_test, y_pred))
        
        evaluator.plot_confusion_matrix(
            y_test, y_pred,
            labels=label_encoder.classes_ if label_encoder else None
        )
    else:
        print(f"  R² Score: {r2_score(y_test, y_pred):.4f}")
        print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
        print(f"  MAE: {mean_absolute_error(y_test, y_pred):.2f}")
        
        evaluator.regression_diagnostics(y_test, y_pred)
    
    # 9. Feature Importance
    if hasattr(best_model, 'feature_importances_'):
        evaluator.plot_feature_importance(best_model, feature_names)
    
    # 10. Results Summary
    if not use_flaml:
        results_df = engine.get_results_df()
        print("\n📊 Alle Modell-Ergebnisse:")
        print(results_df.round(4))
        evaluator.plot_comparison(results_df)
    
    return {
        'model': best_model,
        'feature_engineer': fe,
        'label_encoder': label_encoder,
        'feature_names': feature_names,
        'results': engine.get_results_df() if not use_flaml else None
    }


# =============================================================================
# 8. AUSFÜHRUNG
# =============================================================================
if __name__ == "__main__":
    
    # Beispiel 1: Classification - Issue Resolution vorhersagen
    print("\n" + "🔵" * 35)
    print("BEISPIEL 1: Issue Resolution Prediction (Classification)")
    print("🔵" * 35)
    
    results_classification = run_automl_pipeline(
        target_col='issue_resolution',
        task_type='classification',
        tune_hyperparams=True
    )
    
    # Beispiel 2: Regression - Total Workflow Time vorhersagen
    print("\n" + "🟢" * 35)
    print("BEISPIEL 2: Workflow Time Prediction (Regression)")
    print("🟢" * 35)
    
    results_regression = run_automl_pipeline(
        target_col='wf_total_time',
        task_type='regression',
        tune_hyperparams=True
    )
    
    print("\n" + "=" * 70)
    print("✅ AutoML Pipeline abgeschlossen!")
    print("=" * 70)
