"""
Dialog Analysis - Classifies comments by communication type
"""

import pandas as pd
import re
from pathlib import Path


# Dialog Act Categories
DIALOG_ACTS = {
    'QUESTION': 'Question',
    'ANSWER': 'Answer',
    'GREETING': 'Greeting',
    'COMPLAINT': 'Complaint',
    'THANKS': 'Thanks',
    'APOLOGY': 'Apology',
    'REQUEST': 'Request',
    'INFORM': 'Information',
    'CONFIRM': 'Confirmation',
    'REJECT': 'Rejection',
    'PROMISE': 'Promise',
    'OTHER': 'Other'
}

# Regex patterns for classification
PATTERNS = {
    'QUESTION': [
        r'\?$',
        r'^(how|what|when|where|why|who|can|could|is|are|do|does)\b',
        r'^(wie|was|wann|wo|warum|wer|kann|ist|sind)\b'
    ],
    'GREETING': [
        r'^(hi|hello|hey|dear|good morning|good afternoon)\b',
        r'^(hallo|guten tag|liebe|sehr geehrte)\b',
        r'(regards|best|thanks|cheers)[\s,]*$'
    ],
    'COMPLAINT': [
        r'\b(not working|broken|issue|problem|error|bug|fail|wrong)\b',
        r'\b(funktioniert nicht|kaputt|fehler|problem|falsch)\b'
    ],
    'THANKS': [
        r'\b(thank|thanks|appreciate|grateful)\b',
        r'\b(danke|vielen dank)\b'
    ],
    'APOLOGY': [
        r'\b(sorry|apolog|regret|excuse)\b',
        r'\b(entschuldigung|tut mir leid)\b'
    ],
    'REQUEST': [
        r'\b(please|could you|would you|can you|need)\b',
        r'\b(bitte|könnten sie|würden sie|brauche)\b',
        r'\b(urgent|asap|priority)\b'
    ],
    'CONFIRM': [
        r'\b(yes|correct|confirmed|ok|okay|sure)\b',
        r'\b(ja|korrekt|bestätigt|einverstanden)\b'
    ],
    'REJECT': [
        r'\b(no|cannot|unable|impossible|denied)\b',
        r'\b(nein|kann nicht|unmöglich)\b'
    ],
    'PROMISE': [
        r'\b(will|going to|promise|commit)\b',
        r'\b(werde|werden|verspreche)\b'
    ],
    'INFORM': [
        r'\b(fyi|for your information|please note|update)\b',
        r'\b(zur information|hinweis|aktualisierung)\b'
    ]
}


def classify_text(text):
    """
    Classify a text as Dialog Act.

    Args:
        text: Text to classify

    Returns:
        dict: Dialog Act and confidence
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 3:
        return {'act': 'OTHER', 'name': 'Other', 'confidence': 0.0}

    text = text.strip()
    matches = {}

    # Check all patterns
    for act, patterns in PATTERNS.items():
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match_count += 1
        if match_count > 0:
            matches[act] = match_count

    # No matches -> OTHER
    if not matches:
        return {'act': 'OTHER', 'name': 'Other', 'confidence': 0.3}

    # Best match
    best_act = max(matches, key=matches.get)
    confidence = min(matches[best_act] / len(PATTERNS[best_act]), 1.0)

    return {
        'act': best_act,
        'name': DIALOG_ACTS[best_act],
        'confidence': round(confidence, 2)
    }


def process_comments(utterances_df):
    """
    Classify all comments.

    Args:
        utterances_df: DataFrame with comments

    Returns:
        DataFrame with Dialog Act classification
    """
    print(" Classifying comments...")

    # Find text column
    text_col = 'actionbody' if 'actionbody' in utterances_df.columns else 'body'

    results = []
    total = len(utterances_df)

    for idx, row in utterances_df.iterrows():
        text = row.get(text_col, "")

        # Classify
        result = classify_text(str(text) if pd.notna(text) else "")

        results.append({
            'issueid': row.get('issueid', idx),
            'author': row.get('author', 'unknown'),
            'author_role': row.get('author_role', 'unknown'),
            'dialog_act': result['act'],
            'dialog_act_name': result['name'],
            'confidence': result['confidence'],
            'text_preview': str(text)[:100] if pd.notna(text) else ""
        })

        if (idx + 1) % 5000 == 0:
            print(f"   {idx+1:,}/{total:,} classified...")

    print(f" {len(results):,} comments classified")
    return pd.DataFrame(results)


def get_distribution(dialog_df):
    """Calculate the distribution of Dialog Acts."""
    distribution = dialog_df['dialog_act'].value_counts()

    print("\n Dialog Act Distribution:")
    for act, count in distribution.items():
        pct = count / len(dialog_df) * 100
        name = DIALOG_ACTS.get(act, act)
        print(f"   {name:<15} {count:>6} ({pct:>5.1f}%)")

    return distribution


if __name__ == "__main__":
    print("="*50)
    print(" DIALOG ANALYSIS")
    print("="*50)

    # Load utterances
    data_path = Path("data/raw/sample_utterances.csv")

    if data_path.exists():
        utterances = pd.read_csv(data_path)
        print(f" Loaded: {len(utterances):,} comments")

        # Classify
        dialog_df = process_comments(utterances)

        # Show distribution
        get_distribution(dialog_df)

        # Save
        output_path = Path("data/processed/dialog_acts.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dialog_df.to_csv(output_path, index=False)
        print(f"\n Saved: {output_path}")
    else:
        print(" Utterances file not found!")
