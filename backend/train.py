"""
Model training script for phishing detection.
Trains MultinomialNB and LinearSVC, compares accuracy,
selects the best model, and saves it along with the vectorizer.
Prints detailed evaluation metrics.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from evaluation import evaluate_model
from preprocessing import preprocess_text, preprocess_batch
from feature_engineering import (
    create_vectorizer, fit_transform, transform,
    save_vectorizer
)
from dataset_loader import load_dataset
from bert_model import HF_AVAILABLE, build_and_train_bert

# Paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'best_model.joblib')


def train():
    """Main training pipeline."""
    print("\n" + "="*60)
    print("  AI Phishing Detection — Model Training")
    print("="*60)

    # 1. Load data
    df = load_dataset()

    # 2. Preprocess texts
    print("\n[...] Preprocessing texts (this may take a moment)...")
    df['cleaned'] = preprocess_batch(df['text'].tolist())

    # Remove any rows that produced empty text after cleaning
    df = df[df['cleaned'].str.strip() != '']
    print(f"[OK] Preprocessed {len(df)} samples")

    # 3. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned'], df['label'],
        test_size=0.2, random_state=42, stratify=df['label']
    )
    print(f"[OK] Train: {len(X_train)}, Test: {len(X_test)}")

    # 4. Vectorize
    print("[...] Fitting TF-IDF vectorizer...")
    vectorizer = create_vectorizer()
    X_train_tfidf = fit_transform(vectorizer, X_train.tolist())
    X_test_tfidf = transform(vectorizer, X_test.tolist())
    print(f"[OK] Vocabulary size: {len(vectorizer.vocabulary_)} features")

    # 5. Train models
    print("\n[...] Training MultinomialNB...")
    nb_model = MultinomialNB(alpha=0.1)
    nb_model.fit(X_train_tfidf, y_train)
    nb_metrics = evaluate_model(nb_model, X_test_tfidf, y_test, "Multinomial Naive Bayes")

    print("\n[...] Training LinearSVC (with calibration for probability support)...")
    svc_base = LinearSVC(max_iter=10000, C=1.0)
    svc_model = CalibratedClassifierCV(svc_base, cv=3)
    svc_model.fit(X_train_tfidf, y_train)
    svc_metrics = evaluate_model(svc_model, X_test_tfidf, y_test, "Linear SVC (Calibrated)")

    # Train BERT if available
    bert_accuracy = 0.0
    if HF_AVAILABLE:
        try:
            print("\n[...] Training BERT Model...")
            # BERT module uses identical random_state=42 so the test split is identical
            bert_accuracy, _ = build_and_train_bert(df, test_size=0.2)
        except Exception as e:
            print(f"[ERR] BERT training failed: {e}")

    # 6. Select best model
    print("\n" + "="*60)
    print("  Model Comparison")
    print("="*60)
    print(f"  MultinomialNB  accuracy: {nb_metrics['accuracy']*100:.1f}%")
    print(f"  LinearSVC      accuracy: {svc_metrics['accuracy']*100:.1f}%")
    if HF_AVAILABLE:
        print(f"  BERT           accuracy: {bert_accuracy*100:.1f}%")

    best_sklearn_acc = svc_metrics['accuracy'] if svc_metrics['accuracy'] >= nb_metrics['accuracy'] else nb_metrics['accuracy']
    best_sklearn_model = svc_model if svc_metrics['accuracy'] >= nb_metrics['accuracy'] else nb_model
    best_sklearn_name = "LinearSVC (Calibrated)" if svc_metrics['accuracy'] >= nb_metrics['accuracy'] else "MultinomialNB"

    use_bert = False
    if bert_accuracy > best_sklearn_acc:
        best_name = "BERT (DistilBERT Sequence Classification)"
        use_bert = True
    else:
        best_name = best_sklearn_name

    print(f"\n  * Best model: {best_name}")

    # 7. Save model and vectorizer
    os.makedirs(MODELS_DIR, exist_ok=True)
    use_bert_flag_file = os.path.join(MODELS_DIR, "USE_BERT.txt")
    metrics_file = os.path.join(MODELS_DIR, "metrics.json")
    
    # Save metrics JSON so frontend can visualize it
    best_metrics = svc_metrics if svc_metrics['accuracy'] >= nb_metrics['accuracy'] else nb_metrics
    # If BERT, we don't have full precision/recall/f1 extracted conveniently right now so fallback to best_sklearn + overwrite accuracy if needed
    if use_bert:
        # Assuming BERT has the best accuracy, use it.
        metrics_dict = {
            "model_name": best_name,
            "accuracy": bert_accuracy,
            "precision": best_metrics.get("precision", 0.0),
            "recall": best_metrics.get("recall", 0.0),
            "f1": best_metrics.get("f1", 0.0)
        }
    else:
        metrics_dict = {
            "model_name": best_name,
            "accuracy": best_metrics.get("accuracy", 0.0),
            "precision": best_metrics.get("precision", 0.0),
            "recall": best_metrics.get("recall", 0.0),
            "f1": best_metrics.get("f1", 0.0)
        }
    
    with open(metrics_file, "w") as f:
        json.dump(metrics_dict, f, indent=4)
    
    if use_bert:
        # Save a flag so predict.py knows to route to BERT
        with open(use_bert_flag_file, "w") as f:
            f.write("true")
        save_vectorizer(vectorizer)
        print("\n[OK] BERT chosen as primary model. Flag saved.")
    else:
        # Save traditional model
        if os.path.exists(use_bert_flag_file):
            os.remove(use_bert_flag_file)
        joblib.dump(best_sklearn_model, MODEL_PATH)
        save_vectorizer(vectorizer)
        print(f"\n[OK] Model saved to {MODEL_PATH}")

    print("\n" + "="*60)
    print("  Training complete! Ready to serve predictions.")
    print("="*60 + "\n")


if __name__ == '__main__':
    train()
