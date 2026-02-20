"""
Settings Component for all pages
Provides translations, emoji handling, and help system.
"""

import streamlit as st
import re

# ============================================================================
# TRANSLATIONS - Comprehensive dictionary for all pages
# ============================================================================
TRANSLATIONS = {
    'de': {
        # General / Common
        'app_title': 'HelpDesk Monitor',
        'settings': 'Einstellungen',
        'navigation': 'Navigation',
        'language': 'Sprache',
        'show_help': 'Hilfe-Icons',
        'show_emojis': 'Emojis anzeigen',
        'german': 'Deutsch',
        'english': 'English',
        'overview': 'Übersicht',
        'details': 'Details',
        'filter': 'Filter',
        'search': 'Suche',
        'all': 'Alle',
        'count': 'Anzahl',
        'total': 'Gesamt',
        'average': 'Durchschnitt',
        'status': 'Status',
        'date': 'Datum',
        'time': 'Zeit',
        'hours': 'Stunden',
        'minutes': 'Minuten',
        'seconds': 'Sekunden',
        'days': 'Tage',
        'yes': 'Ja',
        'no': 'Nein',
        'ok': 'OK',
        'cancel': 'Abbrechen',
        'save': 'Speichern',
        'download': 'Herunterladen',
        'export': 'Exportieren',
        'refresh': 'Aktualisieren',
        'auto_refresh': 'Auto-Refresh',
        'last_update': 'Letzte Aktualisierung',
        'loading': 'Lädt...',
        'no_data': 'Keine Daten verfügbar',
        'error': 'Fehler',
        'warning': 'Warnung',
        'success': 'Erfolg',
        'info': 'Information',
        'recommendations': 'Empfehlungen',
        'interpretation': 'Interpretation',
        'legend': 'Legende',
        
        # Navigation & Pages
        'nav_data_inventory': 'Daten-Inventar',
        'nav_dashboard': 'Dashboard',
        # Merged navigation keys (A-G structure)
        'nav_a_overview': 'Overview',
        'nav_b_tickets': 'Tickets',
        'nav_c_people': 'People',
        'nav_d_performance': 'Performance Scores',
        'nav_e_operations': 'Operations',
        'nav_clustering': 'Mitarbeiter-Clustering',
        'nav_architecture': 'Projektarchitektur',
        'nav_io_docs': 'I/O-Dokumentation',
        'nav_model': 'ML-Modell Details',
        'nav_alerts': 'Alerts & Benachrichtigungen',
        'nav_export': 'Export',
        'nav_presentation': 'Präsentation',
        'nav_settings': 'Einstellungen',
        
        # Dashboard / Main App
        'title': 'Help Desk Performance Monitor',
        'subtitle': 'KI-gestütztes System zur Mitarbeiter-Performance-Analyse',
        'total_tickets': 'Total Tickets',
        'avg_time': 'Ø Bearbeitungszeit',
        'scored_samples': 'Bewertete Samples',
        'avg_score': 'Ø Score (Q1)',
        'score_dist': 'Score-Verteilung',
        'bias_analysis': 'Bias-Analyse',
        'employee_overview': 'Mitarbeiter-Übersicht',
        'model_status': 'ML-Modell Status',
        'model_trained': 'Modell trainiert und gespeichert',
        'model_missing': 'Modell noch nicht trainiert',
        'analyzed': 'analysiert',
        'ground_truth': 'Ground Truth',
        'manager_rating': 'Manager-Bewertung',
        'project': 'Projekt',
        'production_ready': 'Production Ready',
        
        # Bias Analysis
        'bias_halo': 'Halo-Effekt',
        'bias_leniency': 'Leniency',
        'bias_std': 'Std',
        'bias_high': 'HOCH',
        'bias_medium': 'MITTEL',
        'bias_low': 'NIEDRIG',
        
        # Data Inventory Page
        'data_inventory': 'Daten-Inventar',
        'data_inventory_subtitle': 'Übersicht über alle Datensätze des Help Desk Performance Systems',
        'dataset_overview': 'Datensatz-Übersicht',
        'datasets': 'Datensätze',
        'issues': 'Issues',
        'total_rows': 'Gesamt Zeilen',
        'dataset_details': 'Datensatz-Details',
        'file_not_found': 'Datei nicht gefunden',
        'expected_at': 'Erwartet in',
        'rows': 'Zeilen',
        'columns': 'Spalten',
        'memory': 'Speicher',
        'missing': 'Fehlend',
        'column': 'Spalte',
        'datatype': 'Datentyp',
        'non_null': 'Nicht-Null',
        'unique': 'Eindeutig',
        'example': 'Beispiel',
        'preview': 'Vorschau (erste 5 Zeilen)',
        'important_columns': 'Wichtige Spalten',
        'datatype_distribution': 'Datentypen-Verteilung',
        'summary': 'Zusammenfassung',
        'data_source_info': 'Die Daten stammen aus dem öffentlichen Mendeley-Datensatz für Performance Appraisal Automation.',
        'columns_by_type': 'Spalten nach Datentyp',
        
        # Score Comparison Page
        'score_comparison': 'Score-Vergleich: Q-Score vs O-Score',
        'score_comparison_subtitle': 'Paralleler Vergleich: Manager-Bewertung (subjektiv) vs Objektive Metriken',
        'q_score_manager': 'Q-Score (Manager)',
        'o_score_objective': 'O-Score (Objektiv)',
        'correlation': 'Korrelation',
        'moderate': 'Moderat',
        'weak': 'Schwach',
        'overrated': 'Überbewertet',
        'underrated': 'Unterbewertet',
        'employee_search': 'Mitarbeiter-Suche',
        'search_employee': 'Mitarbeiter-ID suchen',
        'no_employee_found': 'Kein Mitarbeiter gefunden',
        'complete_ranking': 'Vollständiges Ranking',
        'sort_by': 'Sortieren nach',
        'o_score_high': 'O-Score (hoch)',
        'o_score_low': 'O-Score (niedrig)',
        'q_score_high': 'Q-Score (hoch)',
        'difference_large': 'Differenz (groß)',
        'difference': 'Differenz',
        'bias': 'Bias',
        'bias_distribution': 'Bias-Verteilung',
        'top_10_overrated': 'Top 10 Überbewertete',
        'score_diff_histogram': 'Score-Differenz Histogramm',
        'no_difference': 'Keine Differenz',
        'o_score_components': 'O-Score Komponenten',
        'o_score_composition': 'O-Score Zusammensetzung',
        'quality': 'Qualität',
        'efficiency': 'Effizienz',
        'productivity': 'Produktivität',
        'communication': 'Kommunikation',
        'weight': 'Gewicht',
        'description': 'Beschreibung',
        'reopen_rate_success': 'Reopen-Rate (niedrig = gut), Success-Rate',
        'processing_time': 'Bearbeitungszeit (schnell = gut)',
        'ticket_volume_steps': 'Ticket-Volumen, Processing Steps',
        'first_touch_comments': 'First-Touch-Rate, Kommentar-Aktivität',
        'component_averages': 'Komponenten-Durchschnitte',
        'component_correlation': 'Komponenten-Korrelation',
        'o_score_distribution': 'O-Score Verteilung (alle Mitarbeiter)',
        'employees_with_oscore': 'Mitarbeiter mit O-Score bewertet (min. 10 Tickets)',
        'score_legend': 'Q-Score: Subjektive Bewertung durch den Manager (Q1, Q2, Q3 gemittelt). O-Score: Objektive Bewertung basierend auf messbaren Metriken. Bias: Differenz > 1 Punkt gilt als signifikante Über-/Unterbewertung.',
        'comparison_data_not_found': 'Vergleichsdaten nicht gefunden. Bitte zuerst O-Score berechnen.',
        'run_o_score': 'python src/o_score.py',
        'subjective': 'Subjektiv',
        'score_distributions': 'Score-Verteilungen',
        
        # ML Model Details additions
        'model_loaded_type': 'Modell geladen',
        'avg_all_targets': 'Ø Durchschnitt (Q1, Q2, Q3)',
        'metrics_interpretation': 'Metriken-Interpretation',
        'overall_assessment': 'Gesamtbewertung',
        'very_good': 'Sehr gut',
        'good': 'Gut',
        'acceptable': 'Akzeptabel',
        'improvement_needed': 'Verbesserungspotential',
        'metrics_in_green': 'Metriken im grünen Bereich',
        'q_score_dimensions': 'Q-Score Dimensionen (Manager-Bewertung 1-5)',
        'q1_accuracy': 'Q1: Genauigkeit, Präzision, Sorgfalt',
        'q2_thoroughness': 'Q2: Gründlichkeit, Vollständigkeit, Umfassendheit',
        'q3_responsiveness': 'Q3: Reaktionsschnelligkeit, Verbindlichkeit, Höflichkeit',
        'o_score_criteria': 'O-Score basiert auf objektiven, messbaren Kriterien',
        'model_comparison': 'Modell-Vergleich',
        'combine_scores_tip': 'Kombiniere beide Scores für ein vollständiges Bild! Q-Score erfasst subjektive Qualitätsaspekte, O-Score liefert objektive, nachprüfbare Metriken.',
        
        # Trend Analysis additions
        'q_score_details': 'Q-Score Details',
        'q_score_dimensions_title': 'Q-Score Dimensionen',
        'q_score_correlations': 'Q-Score Korrelationen',
        'q_vs_o_score': 'Q-Score vs O-Score',
        'manager_vs_objective': 'Manager-Bewertung (Q) vs Objektive Metriken (O)',
        'ideal_q_equals_o': 'Ideal (Q=O)',
        'leniency_bias_detected': 'Leniency Bias erkannt: Manager bewerten im Schnitt höher als objektive Metriken',
        'severity_bias_detected': 'Severity Bias erkannt: Manager bewerten im Schnitt niedriger als objektive Metriken',
        'low_deviation': 'Geringe Abweichung zwischen Q-Score und O-Score',
        'target_group': 'Zielgruppe',
        'simulation_results': 'Simulationsergebnisse',
        'before_after_comparison': 'Vorher-Nachher-Vergleich',
        'with_training_effect': 'Mit Training-Effekt',
        'on_employees': 'auf Mitarbeiter der Kategorien',
        'categories': '',
        'employees_would_improve': 'Mitarbeiter würden sich verbessern',
        'more_in_green': 'mehr Mitarbeiter im grünen Bereich',
        'adjust_parameters': 'Parameter anpassen für andere Ergebnisse',
        
        # Training & Deficits additions
        'training_report_not_found': 'Training Report nicht gefunden. Bitte zuerst `training_deficits.py` ausführen.',
        'ok_green': 'OK (GREEN)',
        'training_yellow': 'Training (YELLOW)',
        'personal_conversation': 'Persönliches Gespräch mit dem Mitarbeiter',
        'root_cause_analysis': 'Ursachenanalyse der niedrigen Scores',
        'individual_development_plan': 'Individuellen Entwicklungsplan erstellen',
        
        # Objectivity Check additions
        'detected_bias_types': 'Erkannte Bias-Typen',
        'objectivity_subtitle': 'Analyse der Fairness und Objektivität der Manager-Bewertungen',
        'manager_rates_identical': 'Der Manager bewertet alle drei Dimensionen (Q1, Q2, Q3) fast identisch. Dies deutet darauf hin, dass der Gesamteindruck die Einzelbewertungen dominiert.',
        'manager_rates_mild': 'Der Manager bewertet systematisch zu mild.',
        'manager_rates_strict': 'Der Manager bewertet systematisch zu streng.',
        'rating_balanced': 'Die Bewertung ist ausgeglichen.',
        'severity': 'Severity',
        'against_halo': 'Gegen Halo-Effekt',
        'against_leniency': 'Gegen Leniency Bias',
        'separate_rating_rounds': 'Separate Bewertungsrunden für jede Dimension',
        'time_gap': 'Zeitlicher Abstand zwischen Bewertungen',
        'structured_forms': 'Strukturierte Bewertungsformulare mit konkreten Kriterien',
        'anonymization': 'Anonymisierung der Mitarbeiternamen während der Bewertung',
        'calibration_sessions': 'Kalibrierungssitzungen mit mehreren Managern',
        'concrete_benchmarks': 'Konkrete Benchmarks für jede Score-Stufe (1-5)',
        'forced_distribution': 'Forced Distribution in Betracht ziehen',
        'peer_reviews': 'Peer Reviews als Zweitmeinung einführen',
        
        # Communication NLP additions
        'nlp_not_found': 'NLP Features nicht gefunden. Bitte zuerst `nlp_features.py` ausführen.',
        'density': 'Dichte',
        'curve_interpretation': 'Je weiter rechts die Kurve, desto positiver die Kommunikation.',
        'no_overlap': 'Keine überlappenden Issues zwischen NLP-Daten und bewerteten Samples.',
        'scored_not_available': 'Bewertete Daten für Korrelationsanalyse nicht verfügbar.',
        
        # Process Compliance additions
        'workflow_not_found': 'Workflow-Analyse nicht gefunden. Bitte zuerst `workflow_analysis.py` ausführen.',
        'multiple_reopens': 'Mehrfaches Wiedereröffnen (> 2)',
        'direct_jump': 'Direkter Sprung von Open zu Closed (ohne In Progress)',
        'root_cause_patterns': 'Ursachenanalyse - Muster identifizieren',
        'quality_checks': 'Qualitätsprüfungen vor dem Schließen',
        'customer_feedback': 'Kundenfeedback - aktiv sammeln',
        'definition_of_done': 'Definition of Done - klar definieren',
        'process_training': 'Prozess-Training für betroffene Mitarbeiter',
        'automatic_validation': 'Automatische Validierung von Statusübergängen',
        'regular_audits': 'Regelmäßige Audits der Ticket-Workflows',
        'gamification': 'Gamification für korrekten Prozessfluss',
        
        # Settings Page additions
        'app_info': 'App Info',
        'environment': 'Umgebung',
        'cloud': 'Cloud',
        'local': 'Lokal',
        'cloud_info': 'Läuft auf Streamlit Cloud - Einige lokale Funktionen sind deaktiviert',
        'version': 'Version',
        'last_updated': 'Letztes Update',
        
        # Export additions
        'excel_removed': 'Excel-Export wurde in der vereinfachten Version entfernt.',
        'export_dir_not_found': 'Export-Verzeichnis nicht gefunden.',
        'today': 'heute',
        'type': 'Typ',
        'negative': 'Negativ',
        'not_available': 'nicht verfügbar',
        'data_source': 'Datenquelle',
        'bias_ok': 'OK',
        'bias_too_mild': 'Zu mild',
        'bias_central': 'Central Tendency',
        'bias_problems': 'Erkannte Probleme:',
        'bias_problem1': 'Starker Halo-Effekt (Scores zu ähnlich)',
        'bias_problem2': 'Leniency Bias (Manager bewertet zu mild)',
        'bias_type': 'Bias-Typ',
        'bias_value': 'Wert',
        'bias_severity': 'Severity',
        'inter_correlation': 'Inter-Korrelation',
        'neutral': 'Neutral',
        'correlation_matrix': 'Score-Korrelationsmatrix',
        'score_relationships': 'Score-Beziehungen',
        'perfect_correlation': 'Perfekte Korrelation',
        'statistical_summary': 'Statistische Zusammenfassung',
        'metric': 'Metrik',
        'sample_count': 'Anzahl Samples',
        'mean': 'Mittelwert',
        'std_dev': 'Standardabweichung',
        'median': 'Median',
        'min': 'Min',
        'max': 'Max',
        
        # Ticket Monitor
        'live_tickets': 'Live Tickets',
        'ticket_monitor': 'Ticket Monitor',
        'ticket_list': 'Ticket-Liste',
        'statistics': 'Statistiken',
        'priority': 'Priorität',
        'assignee': 'Bearbeiter',
        'created': 'Erstellt',
        'resolved': 'Gelöst',
        'open': 'Offen',
        'closed': 'Geschlossen',
        'in_progress': 'In Bearbeitung',
        'waiting': 'Wartet',
        'critical': 'Kritisch',
        'high': 'Hoch',
        'medium': 'Mittel',
        'low': 'Niedrig',
        'minimal': 'Minimal',
        'unknown': 'Unbekannt',
        'comments': 'Kommentare',
        'steps': 'Schritte',
        'ticket_details': 'Ticket-Details',
        'select_ticket': 'Ticket auswählen',
        'title_col': 'Titel',
        'type': 'Typ',
        'status_history': 'Status-Historie',
        'top_assignees': 'Top Bearbeiter (nach Tickets)',
        'status_distribution': 'Status-Verteilung',
        'priority_distribution': 'Prioritäts-Verteilung',
        
        # Employee Performance
        'employee_performance': 'Mitarbeiter Performance',
        'team_overview': 'Team-Übersicht',
        'employee_list': 'Mitarbeiter-Liste',
        'top_bottom': 'Top/Bottom',
        'analyses': 'Analysen',
        'risk_level': 'Risk Level',
        'risk_level_def': 'Risk Level Definition',
        'risk_green': 'GREEN',
        'risk_yellow': 'YELLOW',
        'risk_red': 'RED',
        'top_performers': 'Top 5 Performer',
        'bottom_performers': 'Bottom 5 (Handlungsbedarf)',
        'risk_distribution': 'Risk Level Verteilung',
        'score_distribution': 'Score-Verteilung',
        'tickets_vs_score': 'Ticket-Anzahl vs. Score',
        'select_employee': 'Mitarbeiter auswählen',
        'immediate_action': 'Sofortmaßnahmen erforderlich',
        'training_recommended': 'Training empfohlen',
        'all_ok': 'Alles OK',
        'classification_logic': 'Klassifikations-Logik',
        
        # Training & Deficits
        'training_deficits': 'Training & Defizite',
        'training_subtitle': 'Identifikation von Schulungsbedarf und disziplinarischen Maßnahmen',
        'total_employees': 'Total Mitarbeiter',
        'disciplinary': 'Disziplinarisch',
        'risk_overview': 'Risikoverteilung',
        'score_by_risk': 'Score-Verteilung nach Risk Level',
        'urgent': 'Dringend',
        'all_employees': 'Alle Mitarbeiter',
        'no_critical': 'Keine Mitarbeiter mit kritischen Problemen!',
        'critical_attention': 'Mitarbeiter benötigen sofortige Aufmerksamkeit!',
        'flags': 'Flags',
        'training_areas': 'Training-Bereiche',
        'no_training_needed': 'Keine Mitarbeiter mit Trainingsdefiziten!',
        'should_receive_training': 'Mitarbeiter sollten Training erhalten',
        'common_training_needs': 'Häufigste Trainingsbedarfe',
        'min_tickets': 'Min. Tickets',
        'all_thresholds': 'Alle Schwellenwerte im Überblick',
        'category': 'Kategorie',
        'criterion': 'Kriterium',
        'threshold': 'Schwellenwert',
        'meaning': 'Bedeutung',
        'management_recommendations': 'Empfehlungen für das Management',
        
        # NLP Communication
        'communication_analysis': 'Kommunikationsanalyse (NLP)',
        'communication_subtitle': 'Sentiment, Höflichkeit und Kommunikationsmuster aus Helpdesk-Kommentaren',
        'analyzed_issues': 'Analysierte Issues',
        'avg_sentiment': 'Ø Sentiment',
        'positive': 'Positiv',
        'negative': 'Negativ',
        'avg_politeness': 'Ø Höflichkeit',
        'avg_words': 'Ø Wörter/Issue',
        'sentiment_distribution': 'Sentiment-Verteilung',
        'sentiment_score': 'Sentiment Score (-1 bis +1)',
        'issues_count': 'Anzahl Issues',
        'communication_patterns': 'Kommunikationsmuster',
        'politeness': 'Höflichkeit',
        'urgency': 'Dringlichkeit',
        'technical': 'Technisch',
        'solution_oriented': 'Lösungsorientiert',
        'avg_score_per_issue': 'Ø Score pro Issue',
        'pattern': 'Muster',
        'sentiment_vs_performance': 'Sentiment vs. Performance',
        'sentiment_density': 'Sentiment-Dichteverteilung pro Q1 Score',
        'extreme_cases': 'Extremfälle',
        'most_positive': 'Positivste Kommunikation',
        'most_negative': 'Negativste Kommunikation',
        'sentiment': 'Sentiment',
        
        # Process Compliance
        'process_compliance': 'Prozess-Compliance',
        'compliance_subtitle': 'Workflow-Analyse basierend auf dem Helpdesk-Prozessfluss',
        'total_issues': 'Total Issues',
        'compliance_rate': 'Compliance Rate',
        'avg_compliance_score': 'Ø Compliance Score',
        'reopen_rate': 'Reopen Rate',
        'vs_target': 'vs. Ziel',
        'compliance_score_dist': 'Compliance Score Verteilung',
        'reopens_per_issue': 'Reopens pro Issue',
        'reopens_count': 'Anzahl Reopens',
        'expected_process': 'Erwarteter Prozessfluss',
        'valid_process': 'Gültiger Prozess',
        'problematic': 'Problematisch',
        'issues_with_problems': 'Issues mit Prozess-Problemen',
        'min_reopens': 'Min. Reopens',
        'max_compliance': 'Max. Compliance Score',
        'connection': 'Verknüpfung',
        'or': 'ODER',
        'and': 'UND',
        'backward_indicators': 'Rückschritte',
        'no_issues_found': 'Keine Issues mit den gewählten Kriterien gefunden!',
        'process_improvement': 'Empfehlungen zur Prozess-Verbesserung',
        'high_reopen_rate': 'Bei hoher Reopen-Rate',
        'low_compliance': 'Bei niedriger Compliance',
        
        # ML Model Details
        'ml_model_details': 'ML-Modell Details',
        'model_subtitle': 'Feature Importance, Performance-Metriken und Explainability',
        'model_loaded': 'Modell geladen',
        'no_model_found': 'Kein trainiertes Modell gefunden!',
        'performance_metrics': 'Performance-Metriken',
        'accuracy': 'Accuracy',
        'cohens_kappa': "Cohen's Kappa",
        'mae': 'MAE',
        'f1_score': 'F1-Score',
        'avg_accuracy': 'Ø Accuracy',
        'avg_kappa': 'Ø Kappa',
        'avg_cv_score': 'Ø CV-Score',
        'feature_importance': 'Feature Importance',
        'select_target': 'Target auswählen',
        'top_features': 'Top Features für',
        'top_10_features': 'Top 10 Features',
        'most_important_feature': 'Das wichtigste Feature ist',
        'feature_influence': 'Dies hat den größten Einfluss auf die Score-Vorhersage.',
        'not_available': 'nicht verfügbar',
        'confusion_matrix': 'Confusion Matrix',
        'target_for_cm': 'Target für Confusion Matrix',
        'predicted': 'Vorhergesagt',
        'actual': 'Tatsächlich',
        'reading_hint': 'Lesehinweis',
        'diagonal_correct': 'Diagonale = korrekte Vorhersagen',
        'adjacent_acceptable': 'Nebendiagonale = Fehler um 1 Score-Punkt (akzeptabel)',
        'far_problematic': 'Weit von Diagonale = grobe Fehler (problematisch)',
        'optimized_hyperparams': 'Optimierte Hyperparameter',
        'parameters_for': 'Parameter für',
        'model_confidence': 'Modell-Konfidenz',
        'overall_confidence': 'Gesamt-Konfidenz',
        'confidence_level': 'Konfidenz-Level',
        'model_type': 'Modell-Typ',
        'confidence_per_target': 'Konfidenz pro Target',
        'assessment': 'Bewertung',
        'high_reliability': 'Das Modell zeigt hohe Zuverlässigkeit. Vorhersagen können vertrauensvoll genutzt werden.',
        'medium_reliability': 'Mittlere Konfidenz. Vorhersagen sollten mit Vorsicht interpretiert werden.',
        'low_reliability': 'Niedrige Konfidenz. Modell sollte verbessert werden bevor es produktiv eingesetzt wird.',
        'ensemble': 'Ensemble',
        
        # Alerts & Notifications
        'alerts_notifications': 'Alerts & Benachrichtigungen',
        'alerts_subtitle': 'Automatische Benachrichtigungen für kritische Performance-Fälle',
        'critical_disciplinary': 'Kritisch (Disziplinarisch)',
        'attention_training': 'Achtung (Training)',
        'total_action_needed': 'Gesamt Handlungsbedarf',
        'current_alerts': 'Aktuelle Alerts',
        'email_preview': 'Email-Vorschau',
        'configuration': 'Konfiguration',
        'critical_employees': 'Kritische Mitarbeiter - Sofortmaßnahmen erforderlich',
        'no_critical_cases': 'Keine kritischen Fälle vorhanden!',
        'recommended_actions': 'Empfohlene Maßnahmen für',
        'employees': 'Mitarbeiter',
        'training_required': 'Training erforderlich',
        'no_training_cases': 'Keine Mitarbeiter mit Trainingsbedarf!',
        'email_would_look': 'So würde die Alert-Email aussehen:',
        'download_html': 'HTML-Report herunterladen',
        'download_text': 'Text-Version herunterladen',
        'email_config': 'Email-Konfiguration',
        'to_activate_alerts': 'Um automatische Email-Alerts zu aktivieren, erstelle eine Konfigurationsdatei:',
        'path': 'Pfad',
        'download_example_config': 'Beispiel-Konfiguration herunterladen',
        'manual_trigger': 'Manuelle Alert-Auslösung',
        'recipients': 'Empfänger (kommagetrennt)',
        'subject': 'Betreff',
        'attach_csv': 'CSV-Report anhängen',
        'send_test_email': 'Test-Email senden',
        'please_enter_recipients': 'Bitte Empfänger angeben!',
        'email_requires_config': 'Email-Versand erfordert SMTP-Konfiguration',
        
        # Trend Analysis
        'trend_analysis': 'Trend-Analyse',
        'trend_subtitle': 'Performance-Entwicklung und Prognosen',
        'employee_trends': 'Mitarbeiter-Trends',
        'forecast': 'Prognose',
        'performance_per_employee': 'Performance pro Mitarbeiter',
        'scores_by_risk': 'Scores nach Risiko-Level',
        'top_10_highest': 'Top 10 (höchste Scores)',
        'bottom_10_lowest': 'Bottom 10 (niedrigste Scores)',
        'ticket_volume_vs_performance': 'Ticket-Volumen vs. Performance',
        'relationship_tickets_performance': 'Zusammenhang: Ticket-Anzahl und Performance-Score',
        'positive_correlation': 'Positive Korrelation',
        'negative_correlation': 'Negative Korrelation',
        'weak_correlation': 'Schwache Korrelation',
        'more_tickets_higher': 'Mehr Tickets → höhere Scores',
        'more_tickets_lower': 'Mehr Tickets → niedrigere Scores (Überlastung?)',
        'little_influence': 'Ticket-Anzahl hat wenig Einfluss auf Score',
        'forecast_recommendations': 'Prognose & Empfehlungen',
        'what_if_scenario': 'Was-Wäre-Wenn Szenario',
        'simulate_interventions': 'Simuliere die Auswirkungen von Interventionen:',
        'training_effect': 'Training-Effekt (Score-Verbesserung)',
        'training_coverage': '% der YELLOW-Mitarbeiter trainiert',
        'forecast_at': 'Prognose bei',
        'after_training': 'Nach Training',
        'current': 'Aktuell',
        'expected_improvement': 'Erwartete Score-Verbesserung',
        'roi_estimate': 'ROI-Schätzung',
        'trained_employees': 'Trainierte Mitarbeiter',
        'expected_improvements': 'Erwartete Verbesserungen',
        'success_rate': 'Erfolgsrate',
        'potential_productivity': 'Potenzielle Produktivitätssteigerung',
        'team_performance': 'Teamleistung',
        'simulated_6month_trend': 'Simulierter 6-Monats-Trend',
        'without_intervention': 'Ohne Intervention',
        'with_training': 'Mit Training',
        'forecast_score_development': 'Prognostizierte Score-Entwicklung',
        'month': 'Monat',
        
        # Export Center
        'export_center': 'Export Center',
        'export_subtitle': 'Reports und Daten herunterladen',
        'excel_csv': 'Excel/CSV',
        'pdf_reports': 'PDF Reports',
        'training_report': 'Training Report',
        'ml_dataset': 'ML Dataset',
        'nlp_features': 'NLP Features',
        'workflow_analysis': 'Workflow Analysis',
        'features': 'Features',
        'entries': 'Einträge',
        'samples': 'Samples',
        'compliance_data': 'Compliance-Daten',
        'sentiment_analysis': 'Sentiment-Analyse',
        'download_csv': 'CSV herunterladen',
        'generate_excel': 'Excel-Report generieren',
        'generating_excel': 'Generiere Excel...',
        'download_excel': 'Excel herunterladen',
        'excel_created': 'Excel-Report erstellt!',
        'excel_export_unavailable': 'Excel-Export nicht verfügbar',
        'existing_reports': 'Vorhandene Reports',
        'no_pdf_reports': 'Noch keine PDF-Reports vorhanden.',
        'generate_new_report': 'Neuen Report generieren',
        'create_pdf_report': 'PDF-Report erstellen',
        'generating_pdf': 'Generiere PDF...',
        'download_pdf': 'PDF herunterladen',
        'pdf_created': 'PDF erstellt',
        'pdf_export_error': 'Fehler beim PDF-Export',
        'bulk_export': 'Bulk-Export',
        'download_all_zip': 'Alle Daten als ZIP herunterladen',
        'download_zip': 'ZIP herunterladen',
        
        # Dialog Analysis
        'dialog_analysis': 'Dialog-Analyse',
        'dialog_subtitle': 'Klassifikation von Kommunikationstypen (Dialog Acts)',
        'no_dialog_data': 'Keine Dialog-Daten verfügbar. Bitte Dialog Act Classification ausführen.',
        'total_comments': 'Kommentare gesamt',
        'classified': 'Klassifiziert',
        'avg_confidence': 'Ø Konfidenz',
        'tickets': 'Tickets',
        'distribution': 'Verteilung',
        'insights': 'Insights',
        'dialog_act_distribution': 'Dialog Act Verteilung',
        'communication_types_dist': 'Verteilung der Kommunikationstypen',
        'detailed_distribution': 'Detaillierte Verteilung',
        'count_per_dialog_act': 'Anzahl pro Dialog Act',
        'examples_per_dialog_act': 'Beispiele pro Dialog Act',
        'select_dialog_act': 'Dialog Act auswählen',
        'example_comments': 'Beispiel-Kommentare',
        'confidence': 'Konfidenz',
        'issue': 'Issue',
        'author': 'Autor',
        'communication_insights': 'Kommunikations-Insights',
        'positive_communication': 'Positive Kommunikation',
        'negative_communication': 'Negative Kommunikation',
        'positivity_ratio': 'Positivitäts-Ratio',
        'mostly_positive': 'Überwiegend positive Kommunikation!',
        'balanced_communication': 'Ausgewogene Kommunikation',
        'more_negative': 'Mehr negative als positive Kommunikation',
        'qa_analysis': 'Frage-Antwort-Analyse',
        'questions': 'Fragen',
        'answers': 'Antworten',
        'answer_question_ratio': 'Antwort/Frage Ratio',
        'all_questions_answered': 'Alle Fragen werden beantwortet!',
        'questions_answered_pct': 'der Fragen werden direkt beantwortet',
        'service_quality': 'Service-Qualität Indikatoren',
        'complaints': 'Beschwerden',
        'apologies': 'Entschuldigungen',
        'high_complaint_rate': 'Hohe Beschwerderate',
        'moderate_complaint_rate': 'Moderate Beschwerderate',
        'low_complaint_rate': 'Niedrige Beschwerderate',
        'per_complaint': 'Pro Beschwerde',
        'good_complaint_response': 'Gute Reaktion auf Beschwerden!',
        'more_apologies_help': 'Mehr Entschuldigungen könnten helfen',
        
        # Dialog Acts
        'dialog_question': 'Frage',
        'dialog_question_desc': 'Anfragen nach Information',
        'dialog_answer': 'Antwort',
        'dialog_answer_desc': 'Antworten auf Fragen',
        'dialog_greeting': 'Begrüßung',
        'dialog_greeting_desc': 'Begrüßungen und Verabschiedungen',
        'dialog_complaint': 'Beschwerde',
        'dialog_complaint_desc': 'Unzufriedenheit ausdrücken',
        'dialog_thanks': 'Dank',
        'dialog_thanks_desc': 'Dankbarkeit zeigen',
        'dialog_apology': 'Entschuldigung',
        'dialog_apology_desc': 'Sich entschuldigen',
        'dialog_request': 'Anfrage',
        'dialog_request_desc': 'Bitten um Handlung',
        'dialog_inform': 'Information',
        'dialog_inform_desc': 'Informationen mitteilen',
        'dialog_confirm': 'Bestätigung',
        'dialog_confirm_desc': 'Zustimmung/Bestätigung',
        'dialog_reject': 'Ablehnung',
        'dialog_reject_desc': 'Ablehnung/Verneinung',
        'dialog_promise': 'Zusage',
        'dialog_promise_desc': 'Versprechen/Zusagen',
        'dialog_other': 'Sonstiges',
        'dialog_other_desc': 'Nicht klassifiziert',
        
        # Settings Page
        'settings_admin': 'Settings & Admin',
        'simulation': 'Simulation',
        'database_simulator': 'Datenbank & Simulator',
        'simulation_reset': 'Simulation Reset',
        'resetting_database': 'Datenbank wird zurückgesetzt...',
        'simulation_restarted': 'Simulation neu gestartet!',
        'simulator_service': 'Simulator Service',
        'start': 'Start',
        'stop': 'Stop',
        'started': 'Gestartet!',
        'stopped': 'Gestoppt!',
        'simulator_running': 'Simulator läuft',
        'simulator_stopped': 'Simulator gestoppt',
        'database': 'Datenbank',
        'database_not_found': 'Datenbank nicht gefunden!',
        'page_visibility': 'Seiten-Sichtbarkeit',
        'page_visibility_hint': 'Ausgeblendete Seiten werden in der Navigation nicht angezeigt.',
        'status_changes': 'Status-Änderungen',
        'file_size': 'Dateigröße',
        'services': 'Services',
        'restart': 'Neustarten',
        'system_info': 'System Info',
        'project_path': 'Projekt-Pfad',
        'python': 'Python',
        'timestamp': 'Zeitstempel',
        
        # Live Dashboard
        'live_dashboard': 'Live Dashboard',
        'live_kpis': 'Live KPIs',
        'tickets_total': 'Tickets Gesamt',
        'resolved_today': 'Heute gelöst',
        'attention': 'Achtung!',
        'action_needed': 'Handlung nötig!',
        'active_alerts': 'Aktive Alerts',
        'live_activity': 'Live-Aktivität',
        'no_current_activity': 'Keine aktuelle Aktivität',
        'newest_tickets': 'Neueste Tickets',
        
        # Footer
        'footer_system': 'Help Desk Performance System',
        'data_source': 'Daten: Mendeley Dataset',
    },
    'en': {
        # General / Common
        'app_title': 'HelpDesk Monitor',
        'settings': 'Settings',
        'navigation': 'Navigation',
        'language': 'Language',
        'show_help': 'Help Icons',
        'show_emojis': 'Show Emojis',
        'german': 'German',
        'english': 'English',
        'overview': 'Overview',
        'details': 'Details',
        'filter': 'Filter',
        'search': 'Search',
        'all': 'All',
        'count': 'Count',
        'total': 'Total',
        'average': 'Average',
        'status': 'Status',
        'date': 'Date',
        'time': 'Time',
        'hours': 'hours',
        'minutes': 'minutes',
        'seconds': 'seconds',
        'days': 'days',
        'yes': 'Yes',
        'no': 'No',
        'ok': 'OK',
        'cancel': 'Cancel',
        'save': 'Save',
        'download': 'Download',
        'export': 'Export',
        'refresh': 'Refresh',
        'auto_refresh': 'Auto-Refresh',
        'last_update': 'Last Update',
        'loading': 'Loading...',
        'no_data': 'No data available',
        'error': 'Error',
        'warning': 'Warning',
        'success': 'Success',
        'info': 'Information',
        'recommendations': 'Recommendations',
        'interpretation': 'Interpretation',
        'legend': 'Legend',
        
        # Navigation & Pages
        'nav_data_inventory': 'Data Inventory',
        'nav_dashboard': 'Dashboard',
        # Merged navigation keys
        'nav_a_overview': 'Overview',
        'nav_b_tickets': 'Tickets',
        'nav_c_people': 'People',
        'nav_d_performance': 'Performance Scores',
        'nav_e_operations': 'Operations',
        'nav_clustering': 'Employee Clustering',
        'nav_architecture': 'Project Architecture',
        'nav_io_docs': 'I/O Documentation',
        'nav_slides': 'Slides',
        'nav_model': 'ML Model Details',
        'nav_alerts': 'Alerts & Notifications',
        'nav_export': 'Export',
        'nav_presentation': 'Presentation',
        'nav_settings': 'Settings',
        
        # Dashboard / Main App
        'title': 'Help Desk Performance Monitor',
        'subtitle': 'AI-powered Employee Performance Analysis System',
        'total_tickets': 'Total Tickets',
        'avg_time': 'Avg Processing Time',
        'scored_samples': 'Scored Samples',
        'avg_score': 'Avg Score (Q1)',
        'score_dist': 'Score Distribution',
        'bias_analysis': 'Bias Analysis',
        'employee_overview': 'Employee Overview',
        'model_status': 'ML Model Status',
        'model_trained': 'Model trained and saved',
        'model_missing': 'Model not yet trained',
        'analyzed': 'analyzed',
        'ground_truth': 'Ground Truth',
        'manager_rating': 'Manager Rating',
        'project': 'Project',
        'production_ready': 'Production Ready',
        
        # Bias Analysis
        'bias_halo': 'Halo Effect',
        'bias_leniency': 'Leniency',
        'bias_std': 'Std',
        'bias_high': 'HIGH',
        'bias_medium': 'MEDIUM',
        'bias_low': 'LOW',
        
        # Data Inventory Page
        'data_inventory': 'Data Inventory',
        'data_inventory_subtitle': 'Overview of all datasets in the Help Desk Performance System',
        'dataset_overview': 'Dataset Overview',
        'datasets': 'Datasets',
        'issues': 'Issues',
        'total_rows': 'Total Rows',
        'dataset_details': 'Dataset Details',
        'file_not_found': 'File not found',
        'expected_at': 'Expected at',
        'rows': 'Rows',
        'columns': 'Columns',
        'memory': 'Memory',
        'missing': 'Missing',
        'column': 'Column',
        'datatype': 'Data Type',
        'non_null': 'Non-Null',
        'unique': 'Unique',
        'example': 'Example',
        'preview': 'Preview (first 5 rows)',
        'important_columns': 'Important Columns',
        'datatype_distribution': 'Data Type Distribution',
        'summary': 'Summary',
        'data_source_info': 'The data originates from the public Mendeley dataset for Performance Appraisal Automation.',
        'columns_by_type': 'Columns by Data Type',
        
        # Score Comparison Page
        'score_comparison': 'Score Comparison: Q-Score vs O-Score',
        'score_comparison_subtitle': 'Parallel Comparison: Manager Rating (subjective) vs Objective Metrics',
        'q_score_manager': 'Q-Score (Manager)',
        'o_score_objective': 'O-Score (Objective)',
        'correlation': 'Correlation',
        'moderate': 'Moderate',
        'weak': 'Weak',
        'overrated': 'Overrated',
        'underrated': 'Underrated',
        'employee_search': 'Employee Search',
        'search_employee': 'Search Employee ID',
        'no_employee_found': 'No employee found',
        'complete_ranking': 'Complete Ranking',
        'sort_by': 'Sort by',
        'o_score_high': 'O-Score (high)',
        'o_score_low': 'O-Score (low)',
        'q_score_high': 'Q-Score (high)',
        'difference_large': 'Difference (large)',
        'difference': 'Difference',
        'bias': 'Bias',
        'bias_distribution': 'Bias Distribution',
        'top_10_overrated': 'Top 10 Overrated',
        'score_diff_histogram': 'Score Difference Histogram',
        'no_difference': 'No Difference',
        'o_score_components': 'O-Score Components',
        'o_score_composition': 'O-Score Composition',
        'quality': 'Quality',
        'efficiency': 'Efficiency',
        'productivity': 'Productivity',
        'communication': 'Communication',
        'weight': 'Weight',
        'description': 'Description',
        'reopen_rate_success': 'Reopen rate (low = good), success rate',
        'processing_time': 'Processing time (fast = good)',
        'ticket_volume_steps': 'Ticket volume, processing steps',
        'first_touch_comments': 'First-touch rate, comment activity',
        'component_averages': 'Component Averages',
        'component_correlation': 'Component Correlation',
        'o_score_distribution': 'O-Score Distribution (all employees)',
        'employees_with_oscore': 'employees with O-Score (min. 10 tickets)',
        'score_legend': 'Q-Score: Subjective manager rating (Q1, Q2, Q3 averaged). O-Score: Objective rating based on measurable metrics. Bias: Difference > 1 point is considered significant over-/underrating.',
        'comparison_data_not_found': 'Comparison data not found. Please calculate O-Score first.',
        'run_o_score': 'python src/o_score.py',
        'subjective': 'Subjective',
        'score_distributions': 'Score Distributions',
        
        # ML Model Details additions
        'model_loaded_type': 'Model loaded',
        'avg_all_targets': 'Avg All Targets (Q1, Q2, Q3)',
        'metrics_interpretation': 'Metrics Interpretation',
        'overall_assessment': 'Overall Assessment',
        'very_good': 'Very Good',
        'good': 'Good',
        'acceptable': 'Acceptable',
        'improvement_needed': 'Improvement Potential',
        'metrics_in_green': 'metrics in green zone',
        'q_score_dimensions': 'Q-Score Dimensions (Manager Rating 1-5)',
        'q1_accuracy': 'Q1: Accuracy, precision, attention to detail',
        'q2_thoroughness': 'Q2: Thoroughness, completeness, comprehensiveness',
        'q3_responsiveness': 'Q3: Responsiveness, promptness, courtesy',
        'o_score_criteria': 'O-Score is based on objective, measurable criteria',
        'model_comparison': 'Model Comparison',
        'combine_scores_tip': 'Combine both scores for a complete picture! Q-Score captures subjective quality aspects, O-Score provides objective, verifiable metrics.',
        
        # Trend Analysis additions
        'q_score_details': 'Q-Score Details',
        'q_score_dimensions_title': 'Q-Score Dimensions',
        'q_score_correlations': 'Q-Score Correlations',
        'q_vs_o_score': 'Q-Score vs O-Score',
        'manager_vs_objective': 'Manager Rating (Q) vs Objective Metrics (O)',
        'ideal_q_equals_o': 'Ideal (Q=O)',
        'leniency_bias_detected': 'Leniency Bias detected: Managers rate higher on average than objective metrics',
        'severity_bias_detected': 'Severity Bias detected: Managers rate lower on average than objective metrics',
        'low_deviation': 'Low deviation between Q-Score and O-Score',
        'target_group': 'Target Group',
        'simulation_results': 'Simulation Results',
        'before_after_comparison': 'Before-After Comparison',
        'with_training_effect': 'With training effect',
        'on_employees': 'on employees in categories',
        'categories': '',
        'employees_would_improve': 'employees would improve',
        'more_in_green': 'more employees in green zone',
        'adjust_parameters': 'Adjust parameters for different results',
        
        # Training & Deficits additions
        'training_report_not_found': 'Training Report not found. Please run `training_deficits.py` first.',
        'ok_green': 'OK (GREEN)',
        'training_yellow': 'Training (YELLOW)',
        'personal_conversation': 'Personal conversation with the employee',
        'root_cause_analysis': 'Root cause analysis of low scores',
        'individual_development_plan': 'Create individual development plan',
        
        # Objectivity Check additions
        'detected_bias_types': 'Detected Bias Types',
        'objectivity_subtitle': 'Analysis of fairness and objectivity of manager ratings',
        'manager_rates_identical': 'The manager rates all three dimensions (Q1, Q2, Q3) almost identically. This indicates that the overall impression dominates the individual ratings.',
        'manager_rates_mild': 'The manager rates systematically too mild.',
        'manager_rates_strict': 'The manager rates systematically too strict.',
        'rating_balanced': 'The rating is balanced.',
        'severity': 'Severity',
        'against_halo': 'Against Halo Effect',
        'against_leniency': 'Against Leniency Bias',
        'separate_rating_rounds': 'Separate rating rounds for each dimension',
        'time_gap': 'Time gap between ratings',
        'structured_forms': 'Structured rating forms with concrete criteria',
        'anonymization': 'Anonymization of employee names during rating',
        'calibration_sessions': 'Calibration sessions with multiple managers',
        'concrete_benchmarks': 'Concrete benchmarks for each score level (1-5)',
        'forced_distribution': 'Consider forced distribution',
        'peer_reviews': 'Introduce peer reviews as second opinion',
        
        # Communication NLP additions
        'nlp_not_found': 'NLP Features not found. Please run `nlp_features.py` first.',
        'density': 'Density',
        'curve_interpretation': 'The further right the curve, the more positive the communication.',
        'no_overlap': 'No overlapping issues between NLP data and scored samples.',
        'scored_not_available': 'Scored data not available for correlation analysis.',
        
        # Process Compliance additions
        'workflow_not_found': 'Workflow analysis not found. Please run `workflow_analysis.py` first.',
        'multiple_reopens': 'Multiple reopens (> 2)',
        'direct_jump': 'Direct jump from Open to Closed (without In Progress)',
        'root_cause_patterns': 'Root cause analysis - identify patterns',
        'quality_checks': 'Quality checks before closing',
        'customer_feedback': 'Customer feedback - actively collect',
        'definition_of_done': 'Definition of Done - define clearly',
        'process_training': 'Process training for affected employees',
        'automatic_validation': 'Automatic validation of status transitions',
        'regular_audits': 'Regular audits of ticket workflows',
        'gamification': 'Gamification for correct process flow',
        
        # Settings Page additions
        'app_info': 'App Info',
        'environment': 'Environment',
        'cloud': 'Cloud',
        'local': 'Local',
        'cloud_info': 'Running on Streamlit Cloud - Some local features are disabled',
        'version': 'Version',
        'last_updated': 'Last Update',
        
        # Export additions
        'excel_removed': 'Excel export has been removed in the simplified version.',
        'export_dir_not_found': 'Export directory not found.',
        'today': 'today',
        'type': 'Type',
        'negative': 'Negative',
        'not_available': 'not available',
        'data_source': 'Data Source',
        
        'bias_ok': 'OK',
        'bias_too_mild': 'Too mild',
        'bias_central': 'Central Tendency',
        'bias_problems': 'Detected Problems:',
        'bias_problem1': 'Strong Halo Effect (scores too similar)',
        'bias_problem2': 'Leniency Bias (manager rates too mild)',
        'bias_type': 'Bias Type',
        'bias_value': 'Value',
        'bias_severity': 'Severity',
        'inter_correlation': 'Inter-Correlation',
        'neutral': 'Neutral',
        'correlation_matrix': 'Score Correlation Matrix',
        'score_relationships': 'Score Relationships',
        'perfect_correlation': 'Perfect Correlation',
        'statistical_summary': 'Statistical Summary',
        'metric': 'Metric',
        'sample_count': 'Sample Count',
        'mean': 'Mean',
        'std_dev': 'Standard Deviation',
        'median': 'Median',
        'min': 'Min',
        'max': 'Max',
        
        # Ticket Monitor
        'live_tickets': 'Live Tickets',
        'ticket_monitor': 'Ticket Monitor',
        'ticket_list': 'Ticket List',
        'statistics': 'Statistics',
        'priority': 'Priority',
        'assignee': 'Assignee',
        'created': 'Created',
        'resolved': 'Resolved',
        'open': 'Open',
        'closed': 'Closed',
        'in_progress': 'In Progress',
        'waiting': 'Waiting',
        'critical': 'Critical',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low',
        'minimal': 'Minimal',
        'unknown': 'Unknown',
        'comments': 'Comments',
        'steps': 'Steps',
        'ticket_details': 'Ticket Details',
        'select_ticket': 'Select Ticket',
        'title_col': 'Title',
        'type': 'Type',
        'status_history': 'Status History',
        'top_assignees': 'Top Assignees (by Tickets)',
        'status_distribution': 'Status Distribution',
        'priority_distribution': 'Priority Distribution',
        
        # Employee Performance
        'employee_performance': 'Employee Performance',
        'team_overview': 'Team Overview',
        'employee_list': 'Employee List',
        'top_bottom': 'Top/Bottom',
        'analyses': 'Analyses',
        'risk_level': 'Risk Level',
        'risk_level_def': 'Risk Level Definition',
        'risk_green': 'GREEN',
        'risk_yellow': 'YELLOW',
        'risk_red': 'RED',
        'top_performers': 'Top 5 Performers',
        'bottom_performers': 'Bottom 5 (Action Needed)',
        'risk_distribution': 'Risk Level Distribution',
        'score_distribution': 'Score Distribution',
        'tickets_vs_score': 'Ticket Count vs. Score',
        'select_employee': 'Select Employee',
        'immediate_action': 'Immediate Action Required',
        'training_recommended': 'Training Recommended',
        'all_ok': 'All OK',
        'classification_logic': 'Classification Logic',
        
        # Training & Deficits
        'training_deficits': 'Training & Deficits',
        'training_subtitle': 'Identification of Training Needs and Disciplinary Actions',
        'total_employees': 'Total Employees',
        'disciplinary': 'Disciplinary',
        'risk_overview': 'Risk Distribution',
        'score_by_risk': 'Score Distribution by Risk Level',
        'urgent': 'Urgent',
        'all_employees': 'All Employees',
        'no_critical': 'No employees with critical problems!',
        'critical_attention': 'employees need immediate attention!',
        'flags': 'Flags',
        'training_areas': 'Training Areas',
        'no_training_needed': 'No employees with training deficits!',
        'should_receive_training': 'employees should receive training',
        'common_training_needs': 'Most Common Training Needs',
        'min_tickets': 'Min. Tickets',
        'all_thresholds': 'All Thresholds Overview',
        'category': 'Category',
        'criterion': 'Criterion',
        'threshold': 'Threshold',
        'meaning': 'Meaning',
        'management_recommendations': 'Management Recommendations',
        
        # NLP Communication
        'communication_analysis': 'Communication Analysis (NLP)',
        'communication_subtitle': 'Sentiment, politeness and communication patterns from helpdesk comments',
        'analyzed_issues': 'Analyzed Issues',
        'avg_sentiment': 'Avg Sentiment',
        'positive': 'Positive',
        'negative': 'Negative',
        'avg_politeness': 'Avg Politeness',
        'avg_words': 'Avg Words/Issue',
        'sentiment_distribution': 'Sentiment Distribution',
        'sentiment_score': 'Sentiment Score (-1 to +1)',
        'issues_count': 'Issue Count',
        'communication_patterns': 'Communication Patterns',
        'politeness': 'Politeness',
        'urgency': 'Urgency',
        'technical': 'Technical',
        'solution_oriented': 'Solution Oriented',
        'avg_score_per_issue': 'Avg Score per Issue',
        'pattern': 'Pattern',
        'sentiment_vs_performance': 'Sentiment vs. Performance',
        'sentiment_density': 'Sentiment Density Distribution per Q1 Score',
        'extreme_cases': 'Extreme Cases',
        'most_positive': 'Most Positive Communication',
        'most_negative': 'Most Negative Communication',
        'sentiment': 'Sentiment',
        
        # Process Compliance
        'process_compliance': 'Process Compliance',
        'compliance_subtitle': 'Workflow analysis based on helpdesk process flow',
        'total_issues': 'Total Issues',
        'compliance_rate': 'Compliance Rate',
        'avg_compliance_score': 'Avg Compliance Score',
        'reopen_rate': 'Reopen Rate',
        'vs_target': 'vs. Target',
        'compliance_score_dist': 'Compliance Score Distribution',
        'reopens_per_issue': 'Reopens per Issue',
        'reopens_count': 'Reopen Count',
        'expected_process': 'Expected Process Flow',
        'valid_process': 'Valid Process',
        'problematic': 'Problematic',
        'issues_with_problems': 'Issues with Process Problems',
        'min_reopens': 'Min. Reopens',
        'max_compliance': 'Max. Compliance Score',
        'connection': 'Connection',
        'or': 'OR',
        'and': 'AND',
        'backward_indicators': 'Backward Steps',
        'no_issues_found': 'No issues found with selected criteria!',
        'process_improvement': 'Process Improvement Recommendations',
        'high_reopen_rate': 'For High Reopen Rate',
        'low_compliance': 'For Low Compliance',
        
        # ML Model Details
        'ml_model_details': 'ML Model Details',
        'model_subtitle': 'Feature Importance, Performance Metrics and Explainability',
        'model_loaded': 'Model loaded',
        'no_model_found': 'No trained model found!',
        'performance_metrics': 'Performance Metrics',
        'accuracy': 'Accuracy',
        'cohens_kappa': "Cohen's Kappa",
        'mae': 'MAE',
        'f1_score': 'F1 Score',
        'avg_accuracy': 'Avg Accuracy',
        'avg_kappa': 'Avg Kappa',
        'avg_cv_score': 'Avg CV Score',
        'feature_importance': 'Feature Importance',
        'select_target': 'Select Target',
        'top_features': 'Top Features for',
        'top_10_features': 'Top 10 Features',
        'most_important_feature': 'The most important feature is',
        'feature_influence': 'This has the greatest influence on score prediction.',
        'not_available': 'not available',
        'confusion_matrix': 'Confusion Matrix',
        'target_for_cm': 'Target for Confusion Matrix',
        'predicted': 'Predicted',
        'actual': 'Actual',
        'reading_hint': 'Reading Hint',
        'diagonal_correct': 'Diagonal = correct predictions',
        'adjacent_acceptable': 'Adjacent diagonal = 1 score point error (acceptable)',
        'far_problematic': 'Far from diagonal = major errors (problematic)',
        'optimized_hyperparams': 'Optimized Hyperparameters',
        'parameters_for': 'Parameters for',
        'model_confidence': 'Model Confidence',
        'overall_confidence': 'Overall Confidence',
        'confidence_level': 'Confidence Level',
        'model_type': 'Model Type',
        'confidence_per_target': 'Confidence per Target',
        'assessment': 'Assessment',
        'high_reliability': 'The model shows high reliability. Predictions can be used confidently.',
        'medium_reliability': 'Medium confidence. Predictions should be interpreted with caution.',
        'low_reliability': 'Low confidence. Model should be improved before production use.',
        'ensemble': 'Ensemble',
        
        # Alerts & Notifications
        'alerts_notifications': 'Alerts & Notifications',
        'alerts_subtitle': 'Automatic notifications for critical performance cases',
        'critical_disciplinary': 'Critical (Disciplinary)',
        'attention_training': 'Attention (Training)',
        'total_action_needed': 'Total Action Needed',
        'current_alerts': 'Current Alerts',
        'email_preview': 'Email Preview',
        'configuration': 'Configuration',
        'critical_employees': 'Critical Employees - Immediate Action Required',
        'no_critical_cases': 'No critical cases present!',
        'recommended_actions': 'Recommended Actions for',
        'employees': 'employees',
        'training_required': 'Training Required',
        'no_training_cases': 'No employees with training needs!',
        'email_would_look': 'This is how the alert email would look:',
        'download_html': 'Download HTML Report',
        'download_text': 'Download Text Version',
        'email_config': 'Email Configuration',
        'to_activate_alerts': 'To activate automatic email alerts, create a configuration file:',
        'path': 'Path',
        'download_example_config': 'Download Example Configuration',
        'manual_trigger': 'Manual Alert Trigger',
        'recipients': 'Recipients (comma-separated)',
        'subject': 'Subject',
        'attach_csv': 'Attach CSV Report',
        'send_test_email': 'Send Test Email',
        'please_enter_recipients': 'Please enter recipients!',
        'email_requires_config': 'Email sending requires SMTP configuration',
        
        # Trend Analysis
        'trend_analysis': 'Trend Analysis',
        'trend_subtitle': 'Performance Development and Forecasts',
        'employee_trends': 'Employee Trends',
        'forecast': 'Forecast',
        'performance_per_employee': 'Performance per Employee',
        'scores_by_risk': 'Scores by Risk Level',
        'top_10_highest': 'Top 10 (Highest Scores)',
        'bottom_10_lowest': 'Bottom 10 (Lowest Scores)',
        'ticket_volume_vs_performance': 'Ticket Volume vs. Performance',
        'relationship_tickets_performance': 'Relationship: Ticket Count and Performance Score',
        'positive_correlation': 'Positive Correlation',
        'negative_correlation': 'Negative Correlation',
        'weak_correlation': 'Weak Correlation',
        'more_tickets_higher': 'More Tickets → Higher Scores',
        'more_tickets_lower': 'More Tickets → Lower Scores (Overload?)',
        'little_influence': 'Ticket count has little influence on score',
        'forecast_recommendations': 'Forecast & Recommendations',
        'what_if_scenario': 'What-If Scenario',
        'simulate_interventions': 'Simulate the effects of interventions:',
        'training_effect': 'Training Effect (Score Improvement)',
        'training_coverage': '% of YELLOW employees trained',
        'forecast_at': 'Forecast at',
        'after_training': 'After Training',
        'current': 'Current',
        'expected_improvement': 'Expected Score Improvement',
        'roi_estimate': 'ROI Estimate',
        'trained_employees': 'Trained Employees',
        'expected_improvements': 'Expected Improvements',
        'success_rate': 'Success Rate',
        'potential_productivity': 'Potential Productivity Increase',
        'team_performance': 'Team Performance',
        'simulated_6month_trend': 'Simulated 6-Month Trend',
        'without_intervention': 'Without Intervention',
        'with_training': 'With Training',
        'forecast_score_development': 'Forecasted Score Development',
        'month': 'Month',
        
        # Export Center
        'export_center': 'Export Center',
        'export_subtitle': 'Download Reports and Data',
        'excel_csv': 'Excel/CSV',
        'pdf_reports': 'PDF Reports',
        'training_report': 'Training Report',
        'ml_dataset': 'ML Dataset',
        'nlp_features': 'NLP Features',
        'workflow_analysis': 'Workflow Analysis',
        'features': 'Features',
        'entries': 'Entries',
        'samples': 'Samples',
        'compliance_data': 'Compliance Data',
        'sentiment_analysis': 'Sentiment Analysis',
        'download_csv': 'Download CSV',
        'generate_excel': 'Generate Excel Report',
        'generating_excel': 'Generating Excel...',
        'download_excel': 'Download Excel',
        'excel_created': 'Excel Report created!',
        'excel_export_unavailable': 'Excel export unavailable',
        'existing_reports': 'Existing Reports',
        'no_pdf_reports': 'No PDF reports yet.',
        'generate_new_report': 'Generate New Report',
        'create_pdf_report': 'Create PDF Report',
        'generating_pdf': 'Generating PDF...',
        'download_pdf': 'Download PDF',
        'pdf_created': 'PDF created',
        'pdf_export_error': 'PDF export error',
        'bulk_export': 'Bulk Export',
        'download_all_zip': 'Download All Data as ZIP',
        'download_zip': 'Download ZIP',
        
        # Dialog Analysis
        'dialog_analysis': 'Dialog Analysis',
        'dialog_subtitle': 'Classification of Communication Types (Dialog Acts)',
        'no_dialog_data': 'No dialog data available. Please run Dialog Act Classification.',
        'total_comments': 'Total Comments',
        'classified': 'Classified',
        'avg_confidence': 'Avg Confidence',
        'tickets': 'Tickets',
        'distribution': 'Distribution',
        'insights': 'Insights',
        'dialog_act_distribution': 'Dialog Act Distribution',
        'communication_types_dist': 'Distribution of Communication Types',
        'detailed_distribution': 'Detailed Distribution',
        'count_per_dialog_act': 'Count per Dialog Act',
        'examples_per_dialog_act': 'Examples per Dialog Act',
        'select_dialog_act': 'Select Dialog Act',
        'example_comments': 'Example Comments',
        'confidence': 'Confidence',
        'issue': 'Issue',
        'author': 'Author',
        'communication_insights': 'Communication Insights',
        'positive_communication': 'Positive Communication',
        'negative_communication': 'Negative Communication',
        'positivity_ratio': 'Positivity Ratio',
        'mostly_positive': 'Mostly positive communication!',
        'balanced_communication': 'Balanced communication',
        'more_negative': 'More negative than positive communication',
        'qa_analysis': 'Question-Answer Analysis',
        'questions': 'Questions',
        'answers': 'Answers',
        'answer_question_ratio': 'Answer/Question Ratio',
        'all_questions_answered': 'All questions are answered!',
        'questions_answered_pct': 'of questions are directly answered',
        'service_quality': 'Service Quality Indicators',
        'complaints': 'Complaints',
        'apologies': 'Apologies',
        'high_complaint_rate': 'High Complaint Rate',
        'moderate_complaint_rate': 'Moderate Complaint Rate',
        'low_complaint_rate': 'Low Complaint Rate',
        'per_complaint': 'Per Complaint',
        'good_complaint_response': 'Good response to complaints!',
        'more_apologies_help': 'More apologies could help',
        
        # Dialog Acts
        'dialog_question': 'Question',
        'dialog_question_desc': 'Requests for information',
        'dialog_answer': 'Answer',
        'dialog_answer_desc': 'Responses to questions',
        'dialog_greeting': 'Greeting',
        'dialog_greeting_desc': 'Greetings and farewells',
        'dialog_complaint': 'Complaint',
        'dialog_complaint_desc': 'Expressing dissatisfaction',
        'dialog_thanks': 'Thanks',
        'dialog_thanks_desc': 'Showing gratitude',
        'dialog_apology': 'Apology',
        'dialog_apology_desc': 'Apologizing',
        'dialog_request': 'Request',
        'dialog_request_desc': 'Asking for action',
        'dialog_inform': 'Information',
        'dialog_inform_desc': 'Sharing information',
        'dialog_confirm': 'Confirmation',
        'dialog_confirm_desc': 'Agreement/Confirmation',
        'dialog_reject': 'Rejection',
        'dialog_reject_desc': 'Rejection/Denial',
        'dialog_promise': 'Promise',
        'dialog_promise_desc': 'Promises/Commitments',
        'dialog_other': 'Other',
        'dialog_other_desc': 'Not classified',
        
        # Settings Page
        'settings_admin': 'Settings & Admin',
        'simulation': 'Simulation',
        'database_simulator': 'Database & Simulator',
        'simulation_reset': 'Simulation Reset',
        'resetting_database': 'Resetting database...',
        'simulation_restarted': 'Simulation restarted!',
        'simulator_service': 'Simulator Service',
        'start': 'Start',
        'stop': 'Stop',
        'started': 'Started!',
        'stopped': 'Stopped!',
        'simulator_running': 'Simulator running',
        'simulator_stopped': 'Simulator stopped',
        'database': 'Database',
        'database_not_found': 'Database not found!',
        'page_visibility': 'Page Visibility',
        'page_visibility_hint': 'Hidden pages will not appear in the navigation.',
        'status_changes': 'Status Changes',
        'file_size': 'File Size',
        'services': 'Services',
        'restart': 'Restart',
        'system_info': 'System Info',
        'project_path': 'Project Path',
        'python': 'Python',
        'timestamp': 'Timestamp',
        
        # Live Dashboard
        'live_dashboard': 'Live Dashboard',
        'live_kpis': 'Live KPIs',
        'tickets_total': 'Total Tickets',
        'resolved_today': 'Resolved Today',
        'attention': 'Attention!',
        'action_needed': 'Action needed!',
        'active_alerts': 'Active Alerts',
        'live_activity': 'Live Activity',
        'no_current_activity': 'No current activity',
        'newest_tickets': 'Newest Tickets',
        
        # Footer
        'footer_system': 'Help Desk Performance System',
        'data_source': 'Data: Mendeley Dataset',
    }
}

# ============================================================================
# HELP TEXTS for all sections
# ============================================================================
HELP_TEXTS = {
    'de': {
        'dashboard': 'Zeigt die wichtigsten KPIs des Help Desk Systems auf einen Blick.',
        'tickets': 'Live-Übersicht aller Tickets mit Filtern und Status-Tracking.',
        'employees': 'Performance-Übersicht aller Mitarbeiter mit Risk-Level-Klassifikation.',
        'training': 'Identifiziert Mitarbeiter mit Schulungsbedarf (RED/YELLOW/GREEN).',
        'bias': 'Analysiert Verzerrungen in Manager-Bewertungen (Halo, Leniency).',
        'nlp': 'Sentiment-Analyse und Kommunikationsqualität der Ticket-Kommentare.',
        'compliance': 'Überwacht die Einhaltung von Workflow-Prozessen.',
        'model': 'Details zum ML-Modell: Accuracy, Feature Importance, Hyperparameter.',
        'alerts': 'Konfiguration von Email-Benachrichtigungen bei kritischen Events.',
        'trends': 'Zeitliche Entwicklung von KPIs und Performance-Metriken.',
        'export': 'Export von Reports als Excel und PDF für HR.',
        'calibration': 'Tool zur Korrektur von Manager-Bias in Bewertungen.',
        'dialog': 'Klassifikation von Kommentaren nach Dialog-Akten.',
        'settings_page': 'Admin-Funktionen: Simulation Reset, Service-Status.',
        'overview': 'Zeigt die wichtigsten KPIs (Key Performance Indicators) des Help Desk Systems auf einen Blick.',
        'score_dist': 'Histogramm der Manager-Bewertungen für Q1, Q2 und Q3. Ideal ist eine Normalverteilung um den Mittelwert 3.',
        'bias_section': 'Analysiert systematische Verzerrungen in den Manager-Bewertungen wie Halo-Effekt und Leniency-Bias.',
        'employees_section': 'Ranking der Mitarbeiter nach Anzahl bewerteter Tickets und durchschnittlichen Scores.',
        'model_section': 'Status und Accuracy des trainierten ML-Modells für die automatische Score-Vorhersage.',
        'live_kpis': 'Echtzeit-Kennzahlen des Help Desk Systems mit automatischer Aktualisierung.',
        'status_dist': 'Verteilung der Ticket-Status zeigt den aktuellen Workload.',
        'priority_dist': 'Verteilung der Prioritäten hilft bei der Ressourcenplanung.',
        'ticket_list': 'Filterbare Liste aller Tickets mit Status und Priorität.',
        'ticket_stats': 'Statistische Auswertung der gefilterten Tickets.',
        'team_stats': 'Übersicht der Team-Performance nach Risk Level.',
        'employee_details': 'Detaillierte Performance-Analyse einzelner Mitarbeiter.',
        'risk_definition': 'Erklärung der Klassifikationskriterien für Risk Levels.',
        'training_urgency': 'Mitarbeiter die sofortige Aufmerksamkeit benötigen.',
        'training_overview': 'Übersicht aller Mitarbeiter mit Trainingsbedarf.',
        'correlation': 'Korrelationsanalyse zwischen Score-Dimensionen.',
        'sentiment': 'Sentiment-Analyse der Kommunikation in Tickets.',
        'patterns': 'Erkannte Kommunikationsmuster und deren Häufigkeit.',
        'compliance_score': 'Bewertung der Prozess-Einhaltung pro Issue.',
        'reopens': 'Anzahl der Wiederöffnungen zeigt Qualitätsprobleme.',
        'feature_imp': 'Wichtigkeit der Features für die Score-Vorhersage.',
        'metrics': 'Performance-Metriken des trainierten ML-Modells.',
        'confusion': 'Visualisierung der Vorhersage-Genauigkeit.',
        'alerts_overview': 'Übersicht kritischer Fälle die Aufmerksamkeit benötigen.',
        'email_config': 'Konfiguration für automatische Email-Benachrichtigungen.',
        'trend_employees': 'Zeitliche Entwicklung der Mitarbeiter-Performance.',
        'forecast': 'Prognose basierend auf aktuellen Trends und Interventionen.',
        'export_data': 'Export von Daten und Reports in verschiedenen Formaten.',
        'dialog_dist': 'Verteilung der klassifizierten Dialog-Akte.',
        'dialog_examples': 'Beispiele für jeden Dialog-Akt Typ.',
        'dialog_insights': 'Erkenntnisse aus der Kommunikationsanalyse.',
        'simulation': 'Steuerung der Live-Simulation für Demo-Zwecke.',
        'services': 'Status und Steuerung der System-Services.',
    },
    'en': {
        'dashboard': 'Shows key KPIs of the Help Desk system at a glance.',
        'tickets': 'Live overview of all tickets with filters and status tracking.',
        'employees': 'Performance overview of all employees with risk level classification.',
        'training': 'Identifies employees needing training (RED/YELLOW/GREEN).',
        'bias': 'Analyzes biases in manager ratings (Halo, Leniency).',
        'nlp': 'Sentiment analysis and communication quality of ticket comments.',
        'compliance': 'Monitors adherence to workflow processes.',
        'model': 'ML model details: Accuracy, Feature Importance, Hyperparameters.',
        'alerts': 'Configuration of email notifications for critical events.',
        'trends': 'Temporal development of KPIs and performance metrics.',
        'export': 'Export reports as Excel and PDF for HR.',
        'calibration': 'Tool for correcting manager bias in ratings.',
        'dialog': 'Classification of comments by dialog acts.',
        'settings_page': 'Admin functions: Simulation reset, service status.',
        'overview': 'Shows the key KPIs (Key Performance Indicators) of the Help Desk system at a glance.',
        'score_dist': 'Histogram of manager ratings for Q1, Q2 and Q3. Ideally a normal distribution around mean 3.',
        'bias_section': 'Analyzes systematic biases in manager ratings like Halo Effect and Leniency Bias.',
        'employees_section': 'Ranking of employees by number of rated tickets and average scores.',
        'model_section': 'Status and accuracy of the trained ML model for automatic score prediction.',
        'live_kpis': 'Real-time metrics of the Help Desk system with automatic updates.',
        'status_dist': 'Distribution of ticket status shows current workload.',
        'priority_dist': 'Distribution of priorities helps with resource planning.',
        'ticket_list': 'Filterable list of all tickets with status and priority.',
        'ticket_stats': 'Statistical analysis of filtered tickets.',
        'team_stats': 'Overview of team performance by risk level.',
        'employee_details': 'Detailed performance analysis of individual employees.',
        'risk_definition': 'Explanation of classification criteria for risk levels.',
        'training_urgency': 'Employees that need immediate attention.',
        'training_overview': 'Overview of all employees with training needs.',
        'correlation': 'Correlation analysis between score dimensions.',
        'sentiment': 'Sentiment analysis of communication in tickets.',
        'patterns': 'Detected communication patterns and their frequency.',
        'compliance_score': 'Assessment of process compliance per issue.',
        'reopens': 'Number of reopens indicates quality issues.',
        'feature_imp': 'Importance of features for score prediction.',
        'metrics': 'Performance metrics of the trained ML model.',
        'confusion': 'Visualization of prediction accuracy.',
        'alerts_overview': 'Overview of critical cases needing attention.',
        'email_config': 'Configuration for automatic email notifications.',
        'trend_employees': 'Temporal development of employee performance.',
        'forecast': 'Forecast based on current trends and interventions.',
        'export_data': 'Export data and reports in various formats.',
        'dialog_dist': 'Distribution of classified dialog acts.',
        'dialog_examples': 'Examples for each dialog act type.',
        'dialog_insights': 'Insights from communication analysis.',
        'simulation': 'Control of live simulation for demo purposes.',
        'services': 'Status and control of system services.',
    }
}


# ============================================================================
# EMOJI HANDLING
# ============================================================================
# Regex pattern to match emojis
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "]+",
    flags=re.UNICODE
)


def strip_emoji(text: str) -> str:
    """Remove all emojis from text."""
    if text is None:
        return ""
    return EMOJI_PATTERN.sub('', str(text)).strip()


def maybe_emoji(emoji: str, text: str = "") -> str:
    """
    Return emoji + text if emojis are enabled, otherwise just text.
    
    Args:
        emoji: The emoji to potentially include
        text: The text to follow the emoji
    
    Returns:
        Combined string based on emoji setting
    """
    if st.session_state.get('show_emojis', True):
        if text:
            return f"{emoji} {text}"
        return emoji
    return text.strip()


def e(text_with_emoji: str) -> str:
    """
    Smart emoji handler - strips emojis if disabled.
    
    Args:
        text_with_emoji: Text that may contain emojis
    
    Returns:
        Text with or without emojis based on setting
    """
    if st.session_state.get('show_emojis', True):
        return text_with_emoji
    return strip_emoji(text_with_emoji)


# ============================================================================
# SESSION STATE & SETTINGS
# ============================================================================
def init_session_state():
    """Initialize session state for settings."""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Default: English
    if 'show_help' not in st.session_state:
        st.session_state.show_help = True
    if 'show_emojis' not in st.session_state:
        st.session_state.show_emojis = False  # Default: Emojis off
    if 'active_model' not in st.session_state:
        st.session_state.active_model = 'q_score'  # Default: Q-Score (Manager)
    # All pages visible by default (except Settings which is always visible)
    default_visible = {
        # A) Overview
        'nav_a1_tickets': True,
        'nav_a2_people': True,
        # B) Tickets
        'nav_tickets': True,
        'nav_b2_analytics': True,
        'nav_b3_detail': True,
        # C) People
        'nav_c1_people': True,
        'nav_employees': True,
        'nav_training': True,
        'nav_trends': True,
        'nav_c5_detail': True,
        'nav_c6_risk': True,
        # D) Performance Scores
        'nav_d1_score': True,
        'nav_score_compare': True,
        'nav_bias': True,
        'nav_d4_model_q': True,
        'nav_d5_model_o': True,
        'nav_d6_components': True,
        'nav_d7_forecast': True,
        # E) Operations
        'nav_nlp': True,
        'nav_dialog': True,
        'nav_compliance': True,
        # F) Export
        'nav_export': True,
    }
    if 'visible_pages' not in st.session_state:
        st.session_state.visible_pages = default_visible
    else:
        # Ensure new pages are added to existing session state
        for key, value in default_visible.items():
            if key not in st.session_state.visible_pages:
                st.session_state.visible_pages[key] = value


def get_text(key: str) -> str:
    """
    Get translated text for a key.
    
    Args:
        key: Translation key
    
    Returns:
        Translated string, or key if not found
    """
    lang = st.session_state.get('language', 'de')
    translations_dict = TRANSLATIONS.get(lang, TRANSLATIONS['de'])
    text = translations_dict.get(key, key)
    
    # Debug: Show warning if key not found
    if text == key and key not in translations_dict:
        import logging
        logging.warning(f"Translation key not found: '{key}' for language '{lang}'")
    
    # Apply emoji stripping if emojis are disabled
    if not st.session_state.get('show_emojis', True):
        text = strip_emoji(text)
    return text


def get_help(key: str) -> str:
    """
    Get help text for a key.
    
    Args:
        key: Help text key
    
    Returns:
        Help text string
    """
    lang = st.session_state.get('language', 'de')
    return HELP_TEXTS.get(lang, HELP_TEXTS['de']).get(key, '')


# ============================================================================
# UI COMPONENTS
# ============================================================================

def get_nav_items():
    """Get list of navigation items."""
    return [
        # Overview
        ("pages/01_🏠_Overview.py", "nav_a_overview", "🏠"),
        # Tickets
        ("pages/02_🎫_Tickets.py", "nav_b_tickets", "🎫"),
        # People
        ("pages/03_👥_People.py", "nav_c_people", "👥"),
        # Performance Scores
        ("pages/04_📊_Performance_Scores.py", "nav_d_performance", "📊"),
        # Operations
        ("pages/05_💼_Operations.py", "nav_e_operations", "💼"),
        # Clustering
        ("pages/06_🔬_Clustering.py", "nav_clustering", "🔬"),
        # Architecture & IO Documentation
        ("pages/10_🏗️_Architecture.py", "nav_architecture", "🏗️"),
        ("pages/11_📋_IO_Documentation.py", "nav_io_docs", "📋"),
        # Slides
        ("pages/12_🎞️_Slides.py", "nav_slides", "🎞️"),
        # Export & Settings
        ("pages/22_📥_Export.py", "nav_export", "📥"),
        ("pages/23_⚙️_Settings.py", "nav_settings", "⚙️"),
    ]


def render_navigation():
    """Render custom navigation with translations."""
    init_session_state()
    
    nav_items = get_nav_items()
    visible_pages = st.session_state.get('visible_pages', {})
    
    st.sidebar.markdown("### " + get_text('navigation'))
    
    for page_file, trans_key, emoji in nav_items:
        # Settings page is always visible
        if trans_key != 'nav_settings' and not visible_pages.get(trans_key, True):
            continue
            
        label = get_text(trans_key)
        if st.session_state.get('show_emojis', False):
            label = f"{emoji} {label}"
        st.sidebar.page_link(page_file, label=label)


def render_settings_sidebar():
    """Render settings in the sidebar with custom navigation."""
    init_session_state()
    
    # Render custom navigation first
    render_navigation()
    
    # Language & Emoji toggles directly in sidebar (always visible)
    st.sidebar.markdown("---")
    
    col1, col2, col3 = st.sidebar.columns([1, 1, 1])
    
    with col1:
        if st.button("DE", width="stretch", 
                    type="primary" if st.session_state.language == 'de' else "secondary",
                    key='lang_de_btn'):
            st.session_state.language = 'de'
            st.rerun()
    
    with col2:
        if st.button("EN", width="stretch",
                    type="primary" if st.session_state.language == 'en' else "secondary",
                    key='lang_en_btn'):
            st.session_state.language = 'en'
            st.rerun()
    
    with col3:
        # Emoji toggle as button
        emoji_label = "😀" if st.session_state.show_emojis else "Aa"
        emoji_type = "primary" if st.session_state.show_emojis else "secondary"
        if st.button(emoji_label, width="stretch", type=emoji_type, key='emoji_btn'):
            st.session_state.show_emojis = not st.session_state.show_emojis
            st.rerun()



def help_icon(help_key: str) -> str:
    """
    Return HTML for help icon with tooltip.
    
    Args:
        help_key: Key for help text lookup
    
    Returns:
        HTML string for help icon, or empty string if disabled
    """
    if not st.session_state.get('show_help', True):
        return ""
    
    help_text = get_help(help_key)
    if not help_text:
        return ""
    
    return f' <span title="{help_text}" style="cursor:help;color:#3498db;font-size:0.8em;">ⓘ</span>'


def section_header(title: str, help_key: str = None, level: int = 3):
    """
    Render section header with optional help icon.
    
    Args:
        title: Section title (will have emojis stripped if disabled)
        help_key: Optional key for help text
        level: Header level (2 or 3)
    """
    # Apply emoji handling to title
    display_title = e(title)
    
    if help_key and st.session_state.get('show_help', True):
        help_text = get_help(help_key)
        hashes = "#" * level
        st.markdown(
            f"{hashes} {display_title} <span title=\"{help_text}\" style=\"cursor:help;color:#3498db;font-size:0.7em;\">ⓘ</span>",
            unsafe_allow_html=True
        )
    else:
        if level == 2:
            st.header(display_title)
        else:
            st.subheader(display_title)


def page_header(title: str, subtitle: str = None, help_key: str = None):
    """
    Render consistent page header with optional subtitle and help.
    
    Args:
        title: Page title
        subtitle: Optional subtitle
        help_key: Optional help text key
    """
    display_title = e(title)
    
    if help_key and st.session_state.get('show_help', True):
        help_text = get_help(help_key)
        st.markdown(
            f"# {display_title} <span title=\"{help_text}\" style=\"cursor:help;color:#3498db;font-size:0.5em;\">ⓘ</span>",
            unsafe_allow_html=True
        )
    else:
        st.title(display_title)
    
    if subtitle:
        st.markdown(f"**{e(subtitle)}**")
    
    st.markdown("---")


def render_footer():
    """Render consistent footer without author references."""
    st.markdown("---")
    system_name = get_text('footer_system')
    st.markdown(f"""
    <div style='text-align: center; color: #888;'>
        {system_name} v1.0 | {get_text('data_source')}
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MODEL TOGGLE HELPERS
# ============================================================================
def get_active_model():
    """Returns the currently active model type ('q_score' or 'o_score')."""
    return st.session_state.get('active_model', 'q_score')


def is_o_score_active():
    """Returns True if O-Score model is active."""
    return get_active_model() == 'o_score'


def get_model_label():
    """Returns the display label for the active model."""
    if is_o_score_active():
        return "O-Score (Objektiv)"
    return "Q-Score (Manager)"
