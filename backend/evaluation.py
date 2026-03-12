"""
Model evaluation module for phishing detection.
Provides functions to evaluate a trained model and print detailed
performance metrics: Accuracy, Precision, Recall, F1 Score,
and a Confusion Matrix.

Usage:
    from evaluation import evaluate_model
    metrics = evaluate_model(model, X_test, y_test, "Linear SVC")

CLI:
    python evaluation.py          # evaluates the saved best_model.joblib
"""

import os
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

def evaluate_model(model, X_test, y_test, model_name: str) -> dict:
    """
    Evaluate a binary model and print comprehensive metrics.

    Args:
        model:      A trained scikit-learn model with a `.predict()` method.
        X_test:     Sparse matrix or array of test features.
        y_test:     Iterable of true labels ('phishing' or 'legitimate').
        model_name: Display name for the model in the report.

    Returns:
        dict: A dictionary containing accuracy, precision, recall, and f1 scores.
    """
    y_pred = model.predict(X_test)

    # Use binary average for metrics if pos_label is found, else fallback to macro
    acc = accuracy_score(y_test, y_pred)
    try:
        prec = precision_score(y_test, y_pred, pos_label='phishing', zero_division=0)
        rec = recall_score(y_test, y_pred, pos_label='phishing', zero_division=0)
        f1 = f1_score(y_test, y_pred, pos_label='phishing', zero_division=0)
    except ValueError:
        prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)

    # Generate Confusion Matrix
    # We specify labels to ensure the matrix layout is consistent even if a class is missing in test set
    cm = confusion_matrix(y_test, y_pred, labels=['legitimate', 'phishing'])

    print(f"\n{'='*50}")
    print(f"  {model_name} — Evaluation Results")
    print(f"{'='*50}")
    print(f"  Accuracy  : {acc:.4f} ({acc*100:.1f}%)")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(f"  F1 Score  : {f1:.4f}")
    print(f"\n  Confusion Matrix (Rows: True, Cols: Pred):")
    print("                Legitimate  Phishing")
    print(f"  Legitimate | {cm[0][0]:9d} {cm[0][1]:9d}")
    print(f"  Phishing   | {cm[1][0]:9d} {cm[1][1]:9d}")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}


# ── CLI Demo ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import joblib
    from sklearn.model_selection import train_test_split
    from dataset_loader import load_dataset
    from preprocessing import preprocess_batch
    from feature_engineering import transform, load_vectorizer

    print("\n" + "="*60)
    print("  Model Evaluation Report — Standalone Demo")
    print("="*60)

    MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
    MODEL_PATH = os.path.join(MODELS_DIR, "best_model.joblib")

    if not os.path.exists(MODEL_PATH):
        print(f"[ERR] Model not found at {MODEL_PATH}. Run train.py first.")
        exit(1)

    print("\n[...] Loading existing dataset...")
    df = load_dataset()

    print("[...] Preprocessing dataset...")
    df["cleaned"] = preprocess_batch(df["text"].tolist())
    df = df[df["cleaned"].str.strip() != ""]

    print("[...] Loading Vectorizer and transforming test split...")
    vectorizer = load_vectorizer()
    
    # We use the same random_state as train.py to ensure we evaluate on the exact same test set
    _, X_test, _, y_test = train_test_split(
        df['cleaned'], df['label'],
        test_size=0.2, random_state=42, stratify=df['label']
    )
    
    X_test_tfidf = transform(vectorizer, X_test.tolist())

    print("[...] Loading Model...")
    model = joblib.load(MODEL_PATH)
    
    # Identify model name for display
    model_name = type(model).__name__
    if model_name == 'CalibratedClassifierCV':
        model_name = "Linear SVC (Calibrated)"

    evaluate_model(model, X_test_tfidf, y_test, model_name)
    
    print("\n" + "="*60)
    print("  Evaluation complete!")
    print("="*60 + "\n")
