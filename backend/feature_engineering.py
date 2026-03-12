"""
Feature engineering module for phishing detection.
TF-IDF vectorization with unigrams + bigrams (1,2).
Provides functions to fit, transform, save, load, and inspect the vectorizer.

Usage:
    from feature_engineering import (
        create_vectorizer, fit_transform, transform,
        save_vectorizer, load_vectorizer, extract_features,
        get_feature_names
    )

CLI:
    python feature_engineering.py          # runs standalone demo
"""

import os
import sys
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Configuration ───────────────────────────────────────────────────

NGRAM_RANGE = (1, 2)          # unigrams + bigrams
MAX_FEATURES = 10_000         # cap vocabulary for performance
MIN_DF = 2                    # ignore terms that appear in < 2 docs
MAX_DF = 0.95                 # ignore terms that appear in > 95% of docs
SUBLINEAR_TF = True           # apply sublinear TF scaling (1 + log(tf))
STRIP_ACCENTS = "unicode"     # normalise accented characters

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")


# ── Public API ──────────────────────────────────────────────────────

def create_vectorizer(
    ngram_range: tuple = NGRAM_RANGE,
    max_features: int = MAX_FEATURES,
    min_df=MIN_DF,
    max_df=MAX_DF,
) -> TfidfVectorizer:
    """
    Create a TF-IDF vectorizer with sensible defaults for phishing detection.

    Args:
        ngram_range:  Tuple (min_n, max_n) for n-gram extraction.
        max_features: Maximum vocabulary size.
        min_df:       Minimum document frequency (int or float).
        max_df:       Maximum document frequency (int or float).

    Returns:
        A configured (unfitted) TfidfVectorizer.
    """
    vectorizer = TfidfVectorizer(
        ngram_range=ngram_range,
        max_features=max_features,
        min_df=min_df,
        max_df=max_df,
        sublinear_tf=SUBLINEAR_TF,
        strip_accents=STRIP_ACCENTS,
    )
    print(
        f"[OK] Vectorizer created  "
        f"n-grams={ngram_range}  max_features={max_features}  "
        f"min_df={min_df}  max_df={max_df}"
    )
    return vectorizer


def fit_transform(vectorizer: TfidfVectorizer, texts: list):
    """
    Fit the vectorizer on training texts and return the TF-IDF matrix.

    Args:
        vectorizer: An unfitted TfidfVectorizer.
        texts:      List of preprocessed text strings.

    Returns:
        Sparse TF-IDF feature matrix (n_samples × n_features).

    Raises:
        ValueError: If texts is empty or contains no valid strings.
    """
    _validate_texts(texts)

    matrix = vectorizer.fit_transform(texts)

    # Log useful stats
    n_samples, n_features = matrix.shape
    sparsity = 1.0 - (matrix.nnz / (n_samples * n_features)) if n_features else 0
    print(f"[OK] fit_transform complete  shape={matrix.shape}  sparsity={sparsity:.2%}")

    return matrix


def transform(vectorizer: TfidfVectorizer, texts: list):
    """
    Transform texts using an already-fitted vectorizer.

    Args:
        vectorizer: A fitted TfidfVectorizer.
        texts:      List of preprocessed text strings.

    Returns:
        Sparse TF-IDF feature matrix.

    Raises:
        ValueError: If texts is empty or contains no valid strings.
    """
    _validate_texts(texts)

    matrix = vectorizer.transform(texts)
    print(f"[OK] transform complete  shape={matrix.shape}")
    return matrix


def extract_features(texts: list, **kwargs):
    """
    Convenience function: create a vectorizer, fit it, and return both.

    Args:
        texts:    List of preprocessed text strings.
        **kwargs: Forwarded to create_vectorizer() (ngram_range, max_features, etc.).

    Returns:
        Tuple of (tfidf_matrix, fitted_vectorizer).
    """
    vectorizer = create_vectorizer(**kwargs)
    matrix = fit_transform(vectorizer, texts)
    return matrix, vectorizer


def get_feature_names(vectorizer: TfidfVectorizer) -> list:
    """
    Return the learned vocabulary terms from a fitted vectorizer.

    Args:
        vectorizer: A fitted TfidfVectorizer.

    Returns:
        List of feature name strings, ordered by column index.
    """
    return vectorizer.get_feature_names_out().tolist()


# ── Persistence ─────────────────────────────────────────────────────

def save_vectorizer(vectorizer: TfidfVectorizer, path: str = VECTORIZER_PATH):
    """
    Save the fitted vectorizer to disk using joblib.

    Args:
        vectorizer: A fitted TfidfVectorizer.
        path:       Destination file path.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(vectorizer, path)
        print(f"[OK] Vectorizer saved to {path}")
    except Exception as exc:
        print(f"[ERR] Failed to save vectorizer: {exc}")
        raise


def load_vectorizer(path: str = VECTORIZER_PATH) -> TfidfVectorizer:
    """
    Load a previously saved vectorizer from disk.

    Args:
        path: Path to the .joblib file.

    Returns:
        The fitted TfidfVectorizer.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Vectorizer not found at {path}. Train the model first."
        )
    try:
        vectorizer = joblib.load(path)
        print(f"[OK] Vectorizer loaded from {path}")
        return vectorizer
    except Exception as exc:
        print(f"[ERR] Failed to load vectorizer: {exc}")
        raise


# ── Internal Helpers ────────────────────────────────────────────────

def _validate_texts(texts: list) -> None:
    """Ensure texts is a non-empty list of strings."""
    if not texts:
        raise ValueError("texts list is empty — nothing to vectorize.")

    # Filter out None / non-string entries for a clear error message
    invalid = [i for i, t in enumerate(texts) if not isinstance(t, str)]
    if invalid:
        sample = invalid[:5]
        raise ValueError(
            f"texts contains {len(invalid)} non-string entries at indices {sample}. "
            "Ensure all items are strings (run preprocessing first)."
        )


# ── CLI Demo ────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dataset_loader import load_dataset
    from preprocessing import preprocess_batch

    print("\n" + "=" * 60)
    print("  Feature Engineering — Standalone Demo")
    print("=" * 60)

    # 1. Load & preprocess
    df = load_dataset()
    print("\n[...] Preprocessing texts...")
    df["cleaned"] = preprocess_batch(df["text"].tolist())
    df = df[df["cleaned"].str.strip() != ""]
    print(f"[OK] {len(df)} samples after preprocessing")

    # 2. Extract features
    print("\n[...] Extracting TF-IDF features...")
    matrix, vec = extract_features(df["cleaned"].tolist())

    # 3. Summary
    feature_names = get_feature_names(vec)
    print(f"\n  Vocabulary size : {len(feature_names)}")
    print(f"  Feature matrix  : {matrix.shape[0]} samples × {matrix.shape[1]} features")
    print(f"  Top 20 features : {feature_names[:20]}")

    # 4. Save
    save_vectorizer(vec)

    print("\n" + "=" * 60)
    print("  Done! Vectorizer is ready for model training.")
    print("=" * 60 + "\n")
