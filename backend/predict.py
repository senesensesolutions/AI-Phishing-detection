"""
Prediction module for phishing detection.
Provides a reusable function to predict if a message is phishing or legitimate.
"""

import os
import joblib
import numpy as np
from preprocessing import preprocess_text
from preprocessing import preprocess_text
from feature_engineering import load_vectorizer

try:
    from bert_model import HF_AVAILABLE, load_bert_resources, predict_bert
except ImportError:
    HF_AVAILABLE = False

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'best_model.joblib')
USE_BERT_FLAG = os.path.join(MODELS_DIR, 'USE_BERT.txt')

# Global references for caching
_model = None
_vectorizer = None
_use_bert = False

def load_resources():
    """Load model and vectorizer into memory if not already loaded."""
    global _model, _vectorizer, _use_bert
    
    if os.path.exists(USE_BERT_FLAG) and HF_AVAILABLE:
        _use_bert = True
        load_bert_resources()
        return

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train the model first.")
        _model = joblib.load(MODEL_PATH)
    
    if _vectorizer is None:
        _vectorizer = load_vectorizer()

def predict_message(text: str) -> dict:
    """
    Accepts a new message or email, preprocesses it, extracts features,
    and returns the prediction ('phishing' or 'legitimate') and confidence score.
    """
    load_resources()

    cleaned = preprocess_text(text)
    if not cleaned:
        # Default to legitimate for empty or completely stripped text
        return {
            "prediction": "legitimate",
            "confidence": 1.0
        }

    if _use_bert:
        return predict_bert(cleaned)

    # Extract features
    features = _vectorizer.transform([cleaned])

    # Predict
    prediction = _model.predict(features)[0]
    
    # Calculate confidence score
    confidence = 0.85 # default fallback
    if hasattr(_model, 'predict_proba'):
        probabilities = _model.predict_proba(features)[0]
        confidence = float(max(probabilities))

    # The model should output 'phishing' or 'legitimate'
    # Ensure it's returned as string if the model returns ints
    if isinstance(prediction, (int, np.integer)):
        prediction = 'phishing' if prediction == 1 else 'legitimate'
    elif str(prediction) not in ['phishing', 'legitimate']:
        # Fallback mapping if it's something else
        prediction = str(prediction)

    return {
        "prediction": prediction,
        "confidence": confidence
    }
