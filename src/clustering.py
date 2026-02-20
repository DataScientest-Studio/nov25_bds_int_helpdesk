"""
Employee Clustering — Leakage-Free Unsupervised Analysis
=========================================================

DATA SCIENCE NOTE: Dieses Clustering ist leakage-frei weil:
1. Unsupervised Learning — kein Target-Variable, kein Zirkelschluss
2. Features sind direkte Aggregationen aus Rohdaten (kein O-Score)
3. Keine Rang-Funktionen die Train/Test kontaminieren könnten
4. Kein Train/Test-Split notwendig (Clustering = beschreibend, nicht prädiktiv)

Hinweis: Ein früherer ML-Klassifikator (ml_model_o.py) wurde entfernt, da er zwei
Data-Science-Regeln verletzt hat:
- Tautologisches Modell: Zielwert = deterministische Funktion der Features
- Data Leakage: Rang-basierte Features über Gesamtdatensatz vor Train/Test-Split
Der O-Score wird nun direkt als regelbasierter Composite-Score (o_score.py) bereitgestellt.
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "issues_snapshot.csv"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SCHRITT 1: Feature Engineering (leakage-frei)
# =============================================================================

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregiere pro Mitarbeiter — nur direkte Aggregationen, kein O-Score, keine Rang-Funktionen.
    Returns DataFrame mit einem Mitarbeiter pro Zeile.
    """
    print("Building features...")

    # Nur Zeilen mit Assignee
    df = df[df['issue_assignee'].notna()].copy()

    # --- Basis-Aggregationen ---
    agg = df.groupby('issue_assignee').agg(
        ticket_count=('id', 'count'),
        median_time_sec=('wf_total_time', 'median'),
        std_time_sec=('wf_total_time', 'std'),
        avg_steps=('processing_steps', 'mean'),
        avg_comments=('issue_comments_count', 'mean'),
        reopen_rate=('wfe_reopened', lambda x: (x > 0).mean()),
        success_rate=('issue_resolution', lambda x: (x == 'Done').mean()),
        first_touch_rate=('turn', lambda x: (x == 1).mean()),
    ).reset_index()

    # Zeit in Stunden (Sekunden → Stunden)
    agg['median_time_hours'] = agg['median_time_sec'] / 3600.0
    agg['std_time_hours'] = agg['std_time_sec'] / 3600.0
    agg.drop(columns=['median_time_sec', 'std_time_sec'], inplace=True)

    # --- Priority-Mix ---
    priority_agg = df.groupby('issue_assignee').apply(
        lambda g: pd.Series({
            'pct_high': (g['issue_priority'].isin(['High', 'Highest', 'Critical', 'Blocker'])).mean(),
            'pct_low': (g['issue_priority'].isin(['Low', 'Lowest', 'Minor'])).mean(),
        })
    ).reset_index()

    # --- Type-Mix ---
    type_agg = df.groupby('issue_assignee').apply(
        lambda g: pd.Series({
            'pct_hd_service': (g['issue_type'] == 'HD Service').mean(),
        })
    ).reset_index()

    # Zusammenführen
    result = agg.merge(priority_agg, on='issue_assignee', how='left')
    result = result.merge(type_agg, on='issue_assignee', how='left')

    # Filter: nur Mitarbeiter mit >= 10 Tickets
    result = result[result['ticket_count'] >= 10].reset_index(drop=True)

    print(f"  Mitarbeiter nach Filter (ticket_count >= 10): {len(result)}")
    return result


# =============================================================================
# SCHRITT 2: Preprocessing
# =============================================================================

def preprocess(feature_df: pd.DataFrame, feature_cols: list) -> tuple:
    """
    Scale features, fill NaN with median, remove zero-variance columns.
    Log-transformiert stark schiefe Features (Zeit, Ticket-Anzahl).
    """
    X = feature_df[feature_cols].copy()

    # NaN auffüllen mit Median
    for col in X.columns:
        if X[col].isna().any():
            X[col].fillna(X[col].median(), inplace=True)

    # Log-Transformation für stark schiefe Features (Rechtsschiefe durch Ausreißer)
    skewed_cols = ['ticket_count', 'median_time_hours', 'std_time_hours',
                   'avg_steps', 'avg_comments']
    for col in skewed_cols:
        if col in X.columns:
            X[col] = np.log1p(X[col])

    # Spalten mit Varianz = 0 entfernen
    zero_var_cols = X.columns[X.std() == 0].tolist()
    if zero_var_cols:
        print(f"  Entferne Zero-Variance Spalten: {zero_var_cols}")
        X.drop(columns=zero_var_cols, inplace=True)

    active_cols = X.columns.tolist()

    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"  Features nach Preprocessing: {len(active_cols)} Spalten, {len(X_scaled)} Mitarbeiter")
    print(f"  Log-transformiert: {[c for c in skewed_cols if c in active_cols]}")
    return X_scaled, scaler, active_cols


# =============================================================================
# SCHRITT 3: Dimensionsreduktion
# =============================================================================

def reduce_dimensions(X_scaled: np.ndarray) -> dict:
    """PCA + UMAP (wenn verfügbar) für 2D-Visualisierung."""
    result = {}

    # PCA
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    result['pca'] = X_pca
    result['pca_model'] = pca
    explained = pca.explained_variance_ratio_.sum() * 100
    print(f"  PCA: {explained:.1f}% Varianz erklärt durch 2 Komponenten")

    # UMAP (besser für nicht-lineare Strukturen)
    try:
        import umap
        reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
        X_umap = reducer.fit_transform(X_scaled)
        result['umap'] = X_umap
        result['umap_model'] = reducer
        result['use_umap'] = True
        print("  UMAP: erfolgreich berechnet")
    except (ImportError, Exception) as ex:
        print(f"  UMAP nicht verfügbar ({ex}), verwende PCA als Fallback")
        result['umap'] = X_pca
        result['use_umap'] = False

    return result


# =============================================================================
# SCHRITT 4: Clustering-Algorithmen vergleichen
# =============================================================================

def run_clustering_comparison(X_scaled: np.ndarray) -> pd.DataFrame:
    """
    Teste KMeans, GaussianMixture, Agglomerative für k=2..6
    und HDBSCAN. Berechne Silhouette, Davies-Bouldin, Calinski-Harabasz.
    """
    results = []
    k_values = [2, 3, 4, 5, 6]

    print("\n  Algorithmen-Vergleich:")
    print(f"  {'Algo':<20} {'k':>3} {'Silhouette':>12} {'DB-Score':>10} {'CH-Score':>10}")
    print("  " + "-" * 58)

    for k in k_values:
        algorithms = {
            'KMeans': KMeans(n_clusters=k, random_state=42, n_init=10),
            'GaussianMixture': GaussianMixture(n_components=k, random_state=42),
            'Agglomerative': AgglomerativeClustering(n_clusters=k, linkage='ward'),
        }
        for algo_name, model in algorithms.items():
            try:
                labels = model.fit_predict(X_scaled)
                n_clusters_found = len(set(labels))
                if n_clusters_found < 2:
                    continue

                sil = silhouette_score(X_scaled, labels)
                db = davies_bouldin_score(X_scaled, labels)
                ch = calinski_harabasz_score(X_scaled, labels)

                results.append({
                    'algorithm': algo_name,
                    'k': k,
                    'silhouette': round(sil, 4),
                    'davies_bouldin': round(db, 4),
                    'calinski_harabasz': round(ch, 2),
                    'labels': labels,
                    'model': model,
                })
                print(f"  {algo_name:<20} {k:>3} {sil:>12.4f} {db:>10.4f} {ch:>10.2f}")
            except Exception as ex:
                print(f"  {algo_name:<20} {k:>3} FEHLER: {ex}")

    # HDBSCAN (ohne feste Cluster-Anzahl)
    try:
        import hdbscan
        hdb = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=3)
        labels_hdb = hdb.fit_predict(X_scaled)
        n_noise = (labels_hdb == -1).sum()
        n_clusters_hdb = len(set(labels_hdb)) - (1 if -1 in labels_hdb else 0)

        # Silhouette nur auf nicht-Rauschen
        mask = labels_hdb != -1
        if mask.sum() > n_clusters_hdb and n_clusters_hdb >= 2:
            sil_hdb = silhouette_score(X_scaled[mask], labels_hdb[mask])
            db_hdb = davies_bouldin_score(X_scaled[mask], labels_hdb[mask])
            ch_hdb = calinski_harabasz_score(X_scaled[mask], labels_hdb[mask])
            results.append({
                'algorithm': 'HDBSCAN',
                'k': n_clusters_hdb,
                'silhouette': round(sil_hdb, 4),
                'davies_bouldin': round(db_hdb, 4),
                'calinski_harabasz': round(ch_hdb, 2),
                'labels': labels_hdb,
                'model': hdb,
                'noise_count': n_noise,
            })
            print(f"  {'HDBSCAN':<20} {n_clusters_hdb:>3} {sil_hdb:>12.4f} {db_hdb:>10.4f} {ch_hdb:>10.2f}  (Rauschen: {n_noise})")
        else:
            print(f"  HDBSCAN: zu wenige Cluster ({n_clusters_hdb}), nicht auswertbar")
    except (ImportError, Exception) as ex:
        print(f"  HDBSCAN nicht verfügbar: {ex}")

    df_results = pd.DataFrame([{k: v for k, v in r.items() if k not in ('labels', 'model')} for r in results])
    return df_results, results


# =============================================================================
# SCHRITT 5: Beste Konfiguration auswählen
# =============================================================================

def select_best(comparison_results: list) -> dict:
    """
    Wähle beste Konfiguration anhand Silhouette Score.
    Filtere degenerierte Lösungen aus (Cluster mit < 3% der Mitarbeiter).
    """
    n_total = len(comparison_results[0]['labels']) if comparison_results else 0
    min_cluster_size = max(3, int(n_total * 0.02))  # mind. 2% pro Cluster

    valid = []
    for r in comparison_results:
        labels = r['labels']
        cluster_counts = pd.Series(labels[labels != -1]).value_counts()
        min_size = cluster_counts.min() if len(cluster_counts) > 0 else 0
        if min_size >= min_cluster_size:
            valid.append(r)
        else:
            print(f"    Überspringe {r['algorithm']} k={r['k']}: "
                  f"kleinstes Cluster hat nur {min_size} Mitarbeiter (min={min_cluster_size})")

    if not valid:
        print("  Warnung: Keine gültige Konfiguration gefunden, verwende beste ohne Filter")
        valid = comparison_results

    best = max(valid, key=lambda r: r['silhouette'])
    print(f"\n  ✅ Beste gültige Konfiguration: {best['algorithm']} k={best['k']} "
          f"(Silhouette={best['silhouette']:.4f})")
    return best


# =============================================================================
# SCHRITT 6: Cluster-Charakterisierung & Benennung
# =============================================================================

def characterize_clusters(feature_df: pd.DataFrame, labels: np.ndarray, feature_cols: list) -> tuple:
    """
    Berechne Cluster-Profile und vergib sprechende Namen basierend auf Daten.
    """
    temp_df = feature_df[feature_cols].copy()
    temp_df['_cluster'] = labels

    # Ignoriere Rauschen (-1) bei HDBSCAN
    valid = temp_df[temp_df['_cluster'] != -1]

    profile = valid.groupby('_cluster')[feature_cols].mean()

    # Normalisiere für Vergleich (0-1)
    profile_norm = (profile - profile.min()) / (profile.max() - profile.min() + 1e-9)

    cluster_names = {}

    for cluster_id, row in profile_norm.iterrows():
        raw = profile.loc[cluster_id]

        # Sprechende Namen basierend auf Profil-Kombinationen
        ticket_vol = row.get('ticket_count', 0)
        time_eff = 1 - row.get('median_time_hours', 0)  # hoher Wert = schneller
        quality = row.get('success_rate', 0)
        reopen = row.get('reopen_rate', 0)
        first_touch = row.get('first_touch_rate', 0)
        hd_service = row.get('pct_hd_service', 0)
        high_prio = row.get('pct_high', 0)
        steps = row.get('avg_steps', 0)
        comments = row.get('avg_comments', 0)

        # Benennung nach dominanten Charakteristika
        if ticket_vol >= 0.7 and time_eff >= 0.6:
            name = "Volumen-Performer"
        elif high_prio >= 0.6 and steps >= 0.6:
            name = "Eskalations-Spezialist"
        elif hd_service >= 0.6:
            name = "HD-Service-Spezialist"
        elif reopen >= 0.6 and quality < 0.4:
            name = "Problemlöser"
        elif quality >= 0.7 and ticket_vol < 0.4:
            name = "Qualitäts-Fokus"
        elif first_touch >= 0.7 and time_eff >= 0.5:
            name = "Erstlöser"
        elif comments >= 0.7:
            name = "Kommunikations-Intensiv"
        elif ticket_vol < 0.3:
            name = "Spezialisten"
        else:
            name = "Allrounder"

        cluster_names[cluster_id] = name

    # Duplikate auflösen (falls zwei Cluster denselben Namen bekämen)
    seen_names = {}
    for cid, name in cluster_names.items():
        if name in seen_names:
            seen_names[name] += 1
            cluster_names[cid] = f"{name} {seen_names[name]}"
        else:
            seen_names[name] = 1

    print("\n  Cluster-Namen:")
    for cid, name in cluster_names.items():
        mask = (labels == cid)
        count = mask.sum()
        raw = profile.loc[cid]
        print(f"    Cluster {cid} → '{name}' ({count} Mitarbeiter)")
        print(f"      tickets={raw.get('ticket_count',0):.0f}, "
              f"median_time_h={raw.get('median_time_hours',0):.1f}, "
              f"success={raw.get('success_rate',0):.2%}, "
              f"reopen={raw.get('reopen_rate',0):.2%}")

    return cluster_names, profile


# =============================================================================
# SCHRITT 7: Alles zusammenführen & speichern
# =============================================================================

def run():
    print("=" * 65)
    print("EMPLOYEE CLUSTERING — LEAKAGE-FREE UNSUPERVISED ANALYSIS")
    print("=" * 65)

    # --- Daten laden ---
    print(f"\n[1/7] Lade Daten: {DATA_RAW}")
    df = pd.read_csv(DATA_RAW, low_memory=False)
    print(f"      Rohdaten: {df.shape[0]:,} Zeilen, {df.shape[1]} Spalten")

    # --- Feature Engineering ---
    print("\n[2/7] Feature Engineering...")
    feature_df = build_features(df)

    feature_cols = [
        'ticket_count', 'median_time_hours', 'std_time_hours',
        'avg_steps', 'avg_comments', 'reopen_rate', 'success_rate',
        'first_touch_rate', 'pct_high', 'pct_low', 'pct_hd_service',
    ]

    # --- Preprocessing ---
    print("\n[3/7] Preprocessing (RobustScaler, NaN-Fill, Zero-Variance-Drop)...")
    X_scaled, scaler, active_cols = preprocess(feature_df, feature_cols)

    # --- Dimensionsreduktion ---
    print("\n[4/7] Dimensionsreduktion...")
    dim = reduce_dimensions(X_scaled)

    # --- Clustering-Vergleich ---
    print("\n[5/7] Clustering-Vergleich...")
    df_comparison, all_results = run_clustering_comparison(X_scaled)

    # --- Beste Konfiguration ---
    print("\n[6/7] Auswahl beste Konfiguration...")
    best = select_best(all_results)

    best_labels = best['labels']
    best_algo = best['algorithm']
    best_k = best['k']
    best_silhouette = best['silhouette']
    best_model = best['model']

    # --- Cluster-Charakterisierung ---
    cluster_names_map, profile_df = characterize_clusters(feature_df, best_labels, active_cols)

    # --- Output vorbereiten ---
    print("\n[7/7] Ergebnisse speichern...")

    # UMAP oder PCA Koordinaten wählen
    coords = dim['umap']
    coord_prefix = 'umap' if dim.get('use_umap') else 'pca'

    # Cluster-DataFrame
    cluster_df = feature_df.copy()
    cluster_df['cluster'] = best_labels
    cluster_df['cluster_name'] = cluster_df['cluster'].map(
        lambda x: cluster_names_map.get(x, 'Rauschen') if x != -1 else 'Rauschen (Outlier)'
    )
    cluster_df[f'{coord_prefix}_1'] = coords[:, 0]
    cluster_df[f'{coord_prefix}_2'] = coords[:, 1]
    cluster_df.rename(columns={'issue_assignee': 'employee'}, inplace=True)

    # Einheitliche Koordinatennamen für Streamlit (immer umap_1/umap_2)
    if coord_prefix == 'pca':
        cluster_df['umap_1'] = cluster_df['pca_1']
        cluster_df['umap_2'] = cluster_df['pca_2']
    elif coord_prefix == 'umap':
        # Schon vorhanden
        pass

    # Speichern
    cluster_csv = DATA_PROCESSED / "employee_clusters.csv"
    cluster_df.to_csv(cluster_csv, index=False)
    print(f"  ✅ Cluster-CSV: {cluster_csv} ({len(cluster_df)} Mitarbeiter)")

    # Cluster-Profile
    profile_valid = profile_df.reset_index()
    profile_valid['cluster_name'] = profile_valid['_cluster'].map(cluster_names_map)
    profile_valid.drop(columns=['_cluster'], inplace=True)
    profile_csv = DATA_PROCESSED / "cluster_profiles.csv"
    profile_valid.to_csv(profile_csv, index=False)
    print(f"  ✅ Profile-CSV: {profile_csv}")

    # Algorithmus-Vergleich speichern
    comparison_csv = DATA_PROCESSED / "clustering_comparison.csv"
    df_comparison.to_csv(comparison_csv, index=False)
    print(f"  ✅ Vergleichs-CSV: {comparison_csv}")

    # Modell-Bundle speichern
    model_path = MODELS_DIR / "employee_clustering.joblib"
    joblib.dump({
        'scaler': scaler,
        'model': best_model,
        'feature_cols': active_cols,
        'cluster_names': cluster_names_map,
        'algorithm': best_algo,
        'n_clusters': best_k,
        'silhouette': best_silhouette,
        'davies_bouldin': best['davies_bouldin'],
        'calinski_harabasz': best['calinski_harabasz'],
        'coord_prefix': coord_prefix,
        'dim_reduction': dim,
        'comparison_df': df_comparison,
    }, model_path)
    print(f"  ✅ Modell: {model_path}")

    # --- Zusammenfassung ---
    print("\n" + "=" * 65)
    print("ERGEBNIS-ZUSAMMENFASSUNG")
    print("=" * 65)
    print(f"  Mitarbeiter analysiert : {len(cluster_df)}")
    print(f"  Bester Algorithmus     : {best_algo}")
    print(f"  Beste Cluster-Anzahl   : {best_k}")
    print(f"  Silhouette Score       : {best_silhouette:.4f}")
    print(f"  Davies-Bouldin Score   : {best['davies_bouldin']:.4f}")
    print(f"  Calinski-Harabasz      : {best['calinski_harabasz']:.2f}")
    print(f"  Dimensionsreduktion    : {'UMAP' if dim.get('use_umap') else 'PCA'}")
    print()
    print("  Cluster-Verteilung:")
    vc = cluster_df['cluster_name'].value_counts()
    for name, count in vc.items():
        pct = count / len(cluster_df) * 100
        print(f"    {name:<30} {count:>4} Mitarbeiter ({pct:.1f}%)")
    print("=" * 65)

    return cluster_df, df_comparison


if __name__ == '__main__':
    run()
