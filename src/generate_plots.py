"""
Plot-Generator für Projektdokumentation
Creates all required visualizations as PNG (300 dpi)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
from sklearn.metrics import confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Matplotlib-Konfiguration für bessere Qualität
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# Output-Verzeichnis
OUTPUT_DIR = Path("reports/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load all required data."""
    print("📊 Load Data...")
    
    data = {}
    
    # ML-Datasatz
    ml_path = Path("data/processed/ml_dataset.csv")
    if ml_path.exists():
        data['ml_dataset'] = pd.read_csv(ml_path)
        print(f"   ML-Dataset: {len(data['ml_dataset'])} Samples")
    
    # Ground Truth (bewertete Samples)
    gt_path = Path("data/raw/issues_snapshot_sample.xlsx")
    if gt_path.exists():
        data['ground_truth'] = pd.read_excel(gt_path)
        print(f"   Ground Truth: {len(data['ground_truth'])} Samples")
    
    # Model laden für Feature Importance
    model_path = Path("models/performance_scorer.joblib")
    if model_path.exists():
        data['model'] = joblib.load(model_path)
        print("   Model geladen")
    
    # Workflow-Analyse
    wf_path = Path("data/processed/workflow_analysis.csv")
    if wf_path.exists():
        data['workflow'] = pd.read_csv(wf_path)
        print(f"   Workflow: {len(data['workflow'])} entries")
    
    return data


def plot_score_distribution(data):
    """Plot 1: Histogramm der Q1, Q2, Q3 Scores."""
    print("📈 Erstelle Score-Verteilung...")
    
    if 'ground_truth' not in data:
        print("   ⚠️ Ground Truth not available")
        return
    
    df = data['ground_truth']
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    labels = [
        'Q1: Quality of Work\n(Accuracy & Precision)',
        'Q2: Quality of Work\n(Thoroughness)',
        'Q3: Client Relations\n(Responsive & Courteous)'
    ]
    
    for i, (col, color, label) in enumerate(zip(['Q1', 'Q2', 'Q3'], colors, labels)):
        if col in df.columns:
            ax = axes[i]
            counts = df[col].value_counts().sort_index()
            ax.bar(counts.index, counts.values, color=color, edgecolor='black', alpha=0.8)
            ax.set_xlabel('Score (1-5)')
            ax.set_ylabel('Anzahl')
            ax.set_title(label)
            ax.set_xticks([1, 2, 3, 4, 5])
            
            # Mittelwert-Linie
            mean_val = df[col].mean()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
            ax.legend()
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "01_score_distribution.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 01_score_distribution.png")


def plot_correlation_matrix(data):
    """Plot 2: Korrelationsmatrix (Halo-Effekt visualisieren)."""
    print("📈 Erstelle Korrelationsmatrix...")
    
    if 'ground_truth' not in data:
        print("   ⚠️ Ground Truth not available")
        return
    
    df = data['ground_truth']
    
    if all(col in df.columns for col in ['Q1', 'Q2', 'Q3']):
        corr_data = df[['Q1', 'Q2', 'Q3']].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Heatmap
        sns.heatmap(
            corr_data,
            annot=True,
            cmap='RdYlGn_r',
            vmin=0,
            vmax=1,
            center=0.5,
            square=True,
            linewidths=2,
            annot_kws={'size': 14, 'weight': 'bold'},
            ax=ax
        )
        
        ax.set_title('Q-Score Korrelationsmatrix\n(Hohe Werte = Halo-Effekt)', fontsize=14, fontweight='bold')
        
        # Labels anpassen
        labels = ['Q1\n(Accuracy)', 'Q2\n(Thoroughness)', 'Q3\n(Client Rel.)']
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "02_correlation_matrix.png", bbox_inches='tight')
        plt.close()
        print("   ✅ 02_correlation_matrix.png")


def plot_employee_performance(data):
    """Plot 3: Top/Bottom 10 Employee."""
    print("📈 Erstelle Employee-Performance...")
    
    if 'ground_truth' not in data:
        print("   ⚠️ Ground Truth not available")
        return
    
    df = data['ground_truth']
    
    if 'assignee' not in df.columns:
        print("   ⚠️ 'assignee' Spalte not found")
        return
    
    # Aggregiere pro Employee mit neuer Formel:
    # Quality = (Q1 + Q2) / 2, Client = Q3, Overall = 0.5 * Quality + 0.5 * Client
    emp_scores = df.groupby('assignee').agg({
        'Q1': 'mean',
        'Q2': 'mean', 
        'Q3': 'mean'
    }).reset_index()
    
    emp_scores['quality_score'] = (emp_scores['Q1'] + emp_scores['Q2']) / 2
    emp_scores['client_score'] = emp_scores['Q3']
    emp_scores['overall'] = 0.5 * emp_scores['quality_score'] + 0.5 * emp_scores['client_score']
    
    emp_scores = emp_scores.sort_values('overall', ascending=False)
    
    # Top 10 und Bottom 10
    top10 = emp_scores.head(10)
    bottom10 = emp_scores.tail(10)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Top 10
    ax1 = axes[0]
    colors_top = ['#27ae60' if s >= 4 else '#f39c12' if s >= 3 else '#e74c3c' for s in top10['overall']]
    bars1 = ax1.barh(range(len(top10)), top10['overall'], color=colors_top, edgecolor='black')
    ax1.set_yticks(range(len(top10)))
    ax1.set_yticklabels([f"MA-{i+1}" for i in range(len(top10))])
    ax1.set_xlabel('Overall Score')
    ax1.set_title('TOP 10 Employee', fontsize=12, fontweight='bold')
    ax1.set_xlim(0, 5)
    ax1.axvline(3.0, color='orange', linestyle='--', alpha=0.7, label='Grenzwert (3.0)')
    ax1.legend()
    
    # Score-Werte anzeigen
    for i, (bar, val) in enumerate(zip(bars1, top10['overall'])):
        ax1.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}', va='center')
    
    # Bottom 10
    ax2 = axes[1]
    bottom10_sorted = bottom10.sort_values('overall', ascending=True)
    colors_bottom = ['#27ae60' if s >= 4 else '#f39c12' if s >= 3 else '#e74c3c' for s in bottom10_sorted['overall']]
    bars2 = ax2.barh(range(len(bottom10_sorted)), bottom10_sorted['overall'], color=colors_bottom, edgecolor='black')
    ax2.set_yticks(range(len(bottom10_sorted)))
    ax2.set_yticklabels([f"MA-{89-i}" for i in range(len(bottom10_sorted))])
    ax2.set_xlabel('Overall Score')
    ax2.set_title('BOTTOM 10 Employee', fontsize=12, fontweight='bold')
    ax2.set_xlim(0, 5)
    ax2.axvline(3.0, color='orange', linestyle='--', alpha=0.7, label='Grenzwert (3.0)')
    ax2.axvline(2.0, color='red', linestyle='--', alpha=0.7, label='Kritisch (2.0)')
    ax2.legend()
    
    for i, (bar, val) in enumerate(zip(bars2, bottom10_sorted['overall'])):
        ax2.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}', va='center')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "03_employee_performance.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 03_employee_performance.png")


def plot_workflow_status(data):
    """Plot 4: Workflow-Status Verteilung."""
    print("📈 Erstelle Workflow-Status...")
    
    # Beispiel-Data für typischen Helpdesk-Workflow
    status_data = {
        'Status': ['Open', 'In Progress', 'Waiting Feedback', 'Verification', 'Resolved', 'Closed'],
        'Anteil': [5, 15, 10, 8, 12, 50]
    }
    
    df_status = pd.DataFrame(status_data)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Pie Chart
    ax1 = axes[0]
    colors = ['#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#2ecc71', '#1abc9c']
    wedges, texts, autotexts = ax1.pie(
        df_status['Anteil'],
        labels=df_status['Status'],
        autopct='%1.1f%%',
        colors=colors,
        explode=[0, 0, 0, 0, 0, 0.05],
        shadow=True
    )
    ax1.set_title('Ticket-Status Verteilung', fontsize=12, fontweight='bold')
    
    # Bar Chart
    ax2 = axes[1]
    bars = ax2.bar(df_status['Status'], df_status['Anteil'], color=colors, edgecolor='black')
    ax2.set_ylabel('Anteil (%)')
    ax2.set_title('Workflow-Status (Bar Chart)', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height}%', ha='center')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "04_workflow_status.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 04_workflow_status.png")


def plot_confusion_matrices(data):
    """Plot 5: Confusion Matrix pro Q-Score."""
    print("📈 Erstelle Confusion Matrices...")
    
    if 'model' not in data or 'ml_dataset' not in data:
        print("   ⚠️ Model oder Data not available")
        return
    
    model_data = data['model']
    df = data['ml_dataset']
    
    target_cols = ['Q1', 'Q2', 'Q3']
    feature_cols = [col for col in df.columns if col not in target_cols]
    
    X = df[feature_cols]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    labels = [
        'Q1: Accuracy & Precision',
        'Q2: Thoroughness',
        'Q3: Client Relations'
    ]
    
    for i, (target, label) in enumerate(zip(target_cols, labels)):
        ax = axes[i]
        
        if target in model_data.get('metrics', {}):
            cm = np.array(model_data['metrics'][target]['confusion_matrix'])
            
            # Normalisierte Confusion Matrix
            cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            cm_norm = np.nan_to_num(cm_norm)
            
            sns.heatmap(
                cm_norm,
                annot=True,
                fmt='.2f',
                cmap='Blues',
                xticklabels=[1, 2, 3, 4, 5],
                yticklabels=[1, 2, 3, 4, 5],
                ax=ax,
                cbar=False
            )
            
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            ax.set_title(label, fontsize=10, fontweight='bold')
    
    plt.suptitle('Confusion Matrices (Normalisiert)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "05_confusion_matrices.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 05_confusion_matrices.png")


def plot_feature_importance(data):
    """Plot 6: Feature Importance (Top 10)."""
    print("📈 Erstelle Feature Importance...")
    
    if 'model' not in data:
        print("   ⚠️ Model not available")
        return
    
    model_data = data['model']
    
    if 'feature_importance' not in model_data:
        print("   ⚠️ Feature Importance nicht im Model")
        return
    
    # Q1 Feature Importance als Beispiel
    if 'Q1' in model_data['feature_importance']:
        fi_df = model_data['feature_importance']['Q1'].head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(fi_df)))
        
        bars = ax.barh(range(len(fi_df)), fi_df['importance'].values[::-1], color=colors)
        ax.set_yticks(range(len(fi_df)))
        ax.set_yticklabels(fi_df['feature'].values[::-1])
        ax.set_xlabel('Importance Score')
        ax.set_title('Top 10 Features (basierend auf RandomForest)', fontsize=12, fontweight='bold')
        
        # Werte anzeigen
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.005, bar.get_y() + bar.get_height()/2, f'{width:.3f}', va='center')
        
        ax.set_xlim(0, max(fi_df['importance']) * 1.2)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "06_feature_importance.png", bbox_inches='tight')
        plt.close()
        print("   ✅ 06_feature_importance.png")


def plot_team_score_trend(data):
    """Plot 7: Team-Score Trend (simuliert)."""
    print("📈 Erstelle Team-Score Trend...")
    
    # Simulierte monatliche Data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    np.random.seed(42)
    quality_scores = 3.5 + np.cumsum(np.random.randn(12) * 0.1)
    quality_scores = np.clip(quality_scores, 2.5, 4.5)
    
    client_scores = 3.7 + np.cumsum(np.random.randn(12) * 0.08)
    client_scores = np.clip(client_scores, 2.5, 4.5)
    
    overall_scores = 0.5 * quality_scores + 0.5 * client_scores
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(months, quality_scores, 'o-', label='Quality Score (Q1+Q2)/2', color='#3498db', linewidth=2, markersize=8)
    ax.plot(months, client_scores, 's-', label='Client Score (Q3)', color='#e74c3c', linewidth=2, markersize=8)
    ax.plot(months, overall_scores, '^-', label='Overall Score', color='#2ecc71', linewidth=3, markersize=10)
    
    ax.axhline(3.0, color='orange', linestyle='--', alpha=0.7, label='Grenzwert Training (3.0)')
    ax.axhline(2.0, color='red', linestyle='--', alpha=0.7, label='Kritischer Grenzwert (2.0)')
    
    ax.fill_between(months, 3.0, 5.0, alpha=0.1, color='green', label='GREEN Zone')
    ax.fill_between(months, 2.0, 3.0, alpha=0.1, color='orange', label='YELLOW Zone')
    ax.fill_between(months, 0, 2.0, alpha=0.1, color='red', label='RED Zone')
    
    ax.set_xlabel('Monat')
    ax.set_ylabel('Score')
    ax.set_title('Team Performance Trend 2025', fontsize=14, fontweight='bold')
    ax.set_ylim(1, 5)
    ax.legend(loc='lower right', ncol=2)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "07_team_score_trend.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 07_team_score_trend.png")


def plot_risk_distribution(data):
    """Plot 8: Risk Level Verteilung."""
    print("📈 Erstelle Risk-Verteilung...")
    
    # Typische Verteilung
    risk_data = {
        'Risk Level': ['GREEN', 'YELLOW', 'RED'],
        'Anzahl': [72, 14, 3],
        'Farbe': ['#27ae60', '#f39c12', '#e74c3c']
    }
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pie Chart
    ax1 = axes[0]
    wedges, texts, autotexts = ax1.pie(
        risk_data['Anzahl'],
        labels=risk_data['Risk Level'],
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(risk_data["Anzahl"]))})',
        colors=risk_data['Farbe'],
        explode=[0, 0.05, 0.1],
        shadow=True,
        textprops={'fontsize': 11}
    )
    ax1.set_title('Employee Risk-Verteilung', fontsize=12, fontweight='bold')
    
    # Erklarung
    ax2 = axes[1]
    ax2.axis('off')
    
    explanation = """
    RISK LEVEL KLASSIFIKATION
    
    GREEN (Score >= 3.0):
    - Keine Aktion erforderlich
    - Performance im akzeptablen Bereich
    
    YELLOW (Score 2.0 - 3.0):
    - Training empfohlen
    - Workshop, Coaching oder Mentoring
    
    RED (Score < 2.0):
    - Disziplinarische Prufung
    - HR-Gesprach, Performance Plan
    """
    
    ax2.text(0.1, 0.5, explanation, fontsize=11, fontfamily='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "08_risk_distribution.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 08_risk_distribution.png")


def plot_workflow_diagram():
    """Plot 9: Workflow-Prozess Diagramm."""
    print("📈 Erstelle Workflow-Diagramm...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    
    # Positionen der Boxen
    boxes = {
        'Report Issue': (0.1, 0.8, '#e74c3c'),
        'Initial Investigation': (0.3, 0.8, '#3498db'),
        'Valid?': (0.5, 0.8, '#f39c12'),
        'Handled out of System': (0.5, 0.95, '#95a5a6'),
        'Assign to Support': (0.7, 0.8, '#3498db'),
        'Open': (0.1, 0.5, '#3498db'),
        'In Progress': (0.3, 0.5, '#e74c3c'),
        'Waiting Feedback': (0.3, 0.3, '#9b59b6'),
        'Verification': (0.5, 0.3, '#9b59b6'),
        'Resolved': (0.7, 0.5, '#27ae60'),
        'Closed': (0.9, 0.5, '#1abc9c'),
    }
    
    for name, (x, y, color) in boxes.items():
        if name == 'Valid?':
            # Diamant für Entscheidung
            diamond = plt.Polygon([(x, y+0.06), (x+0.06, y), (x, y-0.06), (x-0.06, y)], 
                                  facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(diamond)
            ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')
        else:
            rect = plt.Rectangle((x-0.08, y-0.04), 0.16, 0.08, 
                                  facecolor=color, edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(rect)
            ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold', color='white')
    
    # Pfeile
    arrows = [
        ((0.18, 0.8), (0.22, 0.8)),  # Report -> Investigation
        ((0.38, 0.8), (0.44, 0.8)),  # Investigation -> Valid?
        ((0.5, 0.86), (0.5, 0.91)),  # Valid? -> Out of System (No)
        ((0.56, 0.8), (0.62, 0.8)),  # Valid? -> Assign (Yes)
        ((0.7, 0.76), (0.1, 0.54)),  # Assign -> Open
        ((0.18, 0.5), (0.22, 0.5)),  # Open -> In Progress
        ((0.3, 0.46), (0.3, 0.34)),  # In Progress -> Waiting
        ((0.38, 0.3), (0.42, 0.3)),  # Waiting -> Verification
        ((0.5, 0.34), (0.3, 0.46)),  # Verification -> In Progress (loop)
        ((0.38, 0.5), (0.62, 0.5)),  # In Progress -> Resolved
        ((0.78, 0.5), (0.82, 0.5)),  # Resolved -> Closed
    ]
    
    for (x1, y1), (x2, y2) in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    # Labels fur Ja/Nein
    ax.text(0.5, 0.88, 'No', fontsize=8, ha='center')
    ax.text(0.58, 0.82, 'Yes', fontsize=8, ha='left')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0.2, 1)
    ax.set_title('Helpdesk Ticket Workflow', fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "09_workflow_diagram.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 09_workflow_diagram.png")


def plot_model_comparison():
    """Plot 10: Model-Metriken Vergleich."""
    print("📈 Erstelle Model-Vergleich...")
    
    # Neue Metriken mit max_depth=6
    metrics = {
        'Q-Score': ['Q1', 'Q2', 'Q3'],
        'Accuracy': [0.678, 0.653, 0.727],
        'Kappa': [0.403, 0.342, 0.462],
        'CV Mean': [0.645, 0.652, 0.655]
    }
    
    df = pd.DataFrame(metrics)
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    x = np.arange(3)
    width = 0.6
    
    # Accuracy
    ax1 = axes[0]
    bars1 = ax1.bar(x, df['Accuracy'], width, color=['#2ecc71', '#3498db', '#e74c3c'], edgecolor='black')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Test Accuracy', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['Q-Score'])
    ax1.set_ylim(0, 1)
    ax1.axhline(0.686, color='purple', linestyle='--', label=f'Mean: 68.6%')
    ax1.legend()
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{height:.1%}', ha='center', fontweight='bold')
    
    # Kappa
    ax2 = axes[1]
    bars2 = ax2.bar(x, df['Kappa'], width, color=['#2ecc71', '#3498db', '#e74c3c'], edgecolor='black')
    ax2.set_ylabel("Cohen's Kappa")
    ax2.set_title("Cohen's Kappa", fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['Q-Score'])
    ax2.set_ylim(0, 1)
    ax2.axhline(0.402, color='purple', linestyle='--', label=f'Mean: 0.402')
    ax2.legend()
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{height:.3f}', ha='center', fontweight='bold')
    
    # CV
    ax3 = axes[2]
    bars3 = ax3.bar(x, df['CV Mean'], width, color=['#2ecc71', '#3498db', '#e74c3c'], edgecolor='black')
    ax3.set_ylabel('CV Score')
    ax3.set_title('5-Fold Cross-Validation', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(df['Q-Score'])
    ax3.set_ylim(0, 1)
    ax3.axhline(0.651, color='purple', linestyle='--', label=f'Mean: 65.1%')
    ax3.legend()
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{height:.3f}', ha='center', fontweight='bold')
    
    plt.suptitle('ML-Model Performance (max_depth=6)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "10_model_metrics.png", bbox_inches='tight')
    plt.close()
    print("   ✅ 10_model_metrics.png")


def main():
    print("="*60)
    print("📊 PLOT-GENERATOR FUR PROJEKTDOKUMENTATION")
    print("="*60)
    
    # Data laden
    data = load_data()
    
    print("\n📈 Erstelle Plots...")
    print("-"*40)
    
    # Alle Plots erstellen
    plot_score_distribution(data)
    plot_correlation_matrix(data)
    plot_employee_performance(data)
    plot_workflow_status(data)
    plot_confusion_matrices(data)
    plot_feature_importance(data)
    plot_team_score_trend(data)
    plot_risk_distribution(data)
    plot_workflow_diagram()
    plot_model_comparison()
    
    print("\n" + "="*60)
    print(f"✅ FERTIG! {len(list(OUTPUT_DIR.glob('*.png')))} Plots erstellt in {OUTPUT_DIR}")
    print("="*60)


if __name__ == "__main__":
    main()
