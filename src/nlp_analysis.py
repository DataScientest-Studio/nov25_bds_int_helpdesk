"""
NLP Analysis - Sentiment and communication quality
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

# VADER Sentiment (optional import)
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print(" VADER not installed. Install with: pip install vaderSentiment")


# Word lists for pattern recognition
POLITENESS_WORDS = [
    'please', 'thank', 'thanks', 'appreciate', 'grateful',
    'sorry', 'apolog', 'kindly', 'would you', 'could you'
]

URGENCY_WORDS = [
    'urgent', 'asap', 'immediately', 'critical', 'emergency',
    'deadline', 'priority', 'important', 'blocker', 'blocked'
]

TECHNICAL_WORDS = [
    'error', 'bug', 'fix', 'issue', 'problem', 'crash',
    'exception', 'failed', 'timeout', 'null', 'undefined'
]

SOLUTION_WORDS = [
    'fixed', 'resolved', 'solved', 'solution', 'working',
    'deployed', 'released', 'updated', 'patched', 'done'
]


def analyze_sentiment(text):
    """
    Analyze the sentiment of a text.

    Returns:
        dict: Sentiment scores (compound, pos, neg, neu)
    """
    if not VADER_AVAILABLE:
        return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1}

    if pd.isna(text) or not str(text).strip():
        return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1}

    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(str(text))


def extract_text_features(text):
    """Extract basic features from text."""
    if pd.isna(text) or not str(text).strip():
        return {
            'word_count': 0,
            'char_count': 0,
            'question_count': 0,
            'exclamation_count': 0
        }

    text = str(text)
    words = text.split()

    return {
        'word_count': len(words),
        'char_count': len(text),
        'question_count': text.count('?'),
        'exclamation_count': text.count('!')
    }


def extract_patterns(text):
    """Count communication patterns in text."""
    if pd.isna(text) or not str(text).strip():
        return {
            'politeness_score': 0,
            'urgency_score': 0,
            'technical_score': 0,
            'solution_score': 0
        }

    text_lower = str(text).lower()

    return {
        'politeness_score': sum(1 for w in POLITENESS_WORDS if w in text_lower),
        'urgency_score': sum(1 for w in URGENCY_WORDS if w in text_lower),
        'technical_score': sum(1 for w in TECHNICAL_WORDS if w in text_lower),
        'solution_score': sum(1 for w in SOLUTION_WORDS if w in text_lower)
    }


def process_utterances(utterances_df):
    """
    Process all utterances and extract NLP features.

    Args:
        utterances_df: DataFrame with comments

    Returns:
        DataFrame with NLP features
    """
    print(" Processing comments...")

    # Find text column
    text_col = 'actionbody' if 'actionbody' in utterances_df.columns else 'body'

    results = []
    total = len(utterances_df)

    for idx, row in utterances_df.iterrows():
        text = row[text_col] if text_col in row else ""

        # Sentiment
        sentiment = analyze_sentiment(text)

        # Text features
        text_feat = extract_text_features(text)

        # Patterns
        patterns = extract_patterns(text)

        results.append({
            'issueid': row.get('issueid', idx),
            'author_role': row.get('author_role', 'unknown'),
            'sentiment_compound': sentiment['compound'],
            'sentiment_pos': sentiment['pos'],
            'sentiment_neg': sentiment['neg'],
            **text_feat,
            **patterns
        })

        # Progress indicator
        if (idx + 1) % 5000 == 0:
            print(f"   {idx+1:,}/{total:,} processed...")

    print(f" {len(results):,} comments analyzed")
    return pd.DataFrame(results)


def aggregate_by_issue(features_df):
    """Aggregate NLP features per issue."""
    print(" Aggregating per issue...")

    aggregated = features_df.groupby('issueid').agg({
        'sentiment_compound': ['mean', 'std', 'min', 'max'],
        'sentiment_pos': 'mean',
        'sentiment_neg': 'mean',
        'word_count': ['mean', 'sum'],
        'question_count': 'sum',
        'politeness_score': 'sum',
        'urgency_score': 'sum',
        'technical_score': 'sum',
        'solution_score': 'sum'
    }).reset_index()

    # Rename columns
    aggregated.columns = ['_'.join(col).strip('_') for col in aggregated.columns]

    print(f" {len(aggregated):,} issues aggregated")
    return aggregated


if __name__ == "__main__":
    print("="*50)
    print(" NLP ANALYSIS")
    print("="*50)

    # Load utterances
    data_path = Path("data/raw/sample_utterances.csv")

    if data_path.exists():
        utterances = pd.read_csv(data_path)
        print(f" Loaded: {len(utterances):,} comments")

        # Process
        features = process_utterances(utterances)

        # Aggregate
        issue_features = aggregate_by_issue(features)

        # Save
        output_path = Path("data/processed/nlp_features.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        issue_features.to_csv(output_path, index=False)
        print(f"\n Saved: {output_path}")

        # Statistics
        if 'sentiment_compound_mean' in issue_features.columns:
            avg_sentiment = issue_features['sentiment_compound_mean'].mean()
            print(f"\n Average sentiment: {avg_sentiment:.3f}")
    else:
        print(" Utterances file not found!")
