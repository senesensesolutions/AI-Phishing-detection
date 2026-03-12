"""
Flask API server for phishing detection.
Provides POST /analyze endpoint that accepts text and returns
prediction, confidence, key indicator words, and security flags.
Includes basic rate limiting, security pattern detection, and
local authentication (signup/login) with JSON file storage.
"""

import os
import sys
import re
import json
import hashlib
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from preprocessing import preprocess_text
from feature_engineering import load_vectorizer
from predict import predict_message, load_resources
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Rate Limiter Configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "60 per minute"]
)

# ── Local Auth Helpers ──────────────────────────────────────────────

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _load_users() -> list:
    """Load user records from local JSON file."""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, Exception):
        return []


def _save_users(users: list):
    """Persist user records to local JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str, salt: str = None) -> tuple:
    """Hash a password with a random salt; returns (hash, salt)."""
    if salt is None:
        salt = uuid.uuid4().hex
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


# ── Auth Endpoints ──────────────────────────────────────────────────

@app.route('/signup', methods=['POST'])
@limiter.limit("20 per minute")
def signup():
    """
    POST /signup
    Input:  { "email": "...", "password": "..." }
    Output: { "token": "<user-id>", "email": "..." }
    """
    data = request.get_json(silent=True)
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    users = _load_users()

    # Check for existing user
    if any(u['email'] == email for u in users):
        return jsonify({'error': 'User already exists'}), 409

    hashed, salt = _hash_password(password)
    user_id = uuid.uuid4().hex

    users.append({
        'id': user_id,
        'email': email,
        'passwordHash': hashed,
        'salt': salt,
    })
    _save_users(users)

    print(f"[AUTH] New user registered: {email}")
    return jsonify({'token': user_id, 'email': email}), 201


@app.route('/login', methods=['POST'])
@limiter.limit("30 per minute")
def login():
    """
    POST /login
    Input:  { "email": "...", "password": "..." }
    Output: { "token": "<user-id>", "email": "..." }
    """
    data = request.get_json(silent=True)
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    users = _load_users()
    user = next((u for u in users if u['email'] == email), None)

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    hashed, _ = _hash_password(password, user['salt'])
    if hashed != user['passwordHash']:
        return jsonify({'error': 'Invalid email or password'}), 401

    print(f"[AUTH] User logged in: {email}")
    return jsonify({'token': user['id'], 'email': email})

# Security regex patterns
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)
URGENCY_PATTERN = re.compile(
    r'\b(urgent|immediately|act now|verify now|attention|alert|limited time|expire)\b',
    re.IGNORECASE
)


def get_key_indicators(text: str, max_indicators: int = 8) -> list:
    """
    Extract the most important TF-IDF features from the input text.
    Returns a list of the top contributing words/bigrams.
    """
    try:
        vectorizer = load_vectorizer() # Relies on joblib cache if we optimize, or loads fast
        cleaned = preprocess_text(text)
        if not cleaned:
            return []

        tfidf_vector = vectorizer.transform([cleaned])
        feature_names = vectorizer.get_feature_names_out()

        # Get non-zero TF-IDF scores
        non_zero = tfidf_vector.nonzero()
        scores = []
        for idx in non_zero[1]:
            scores.append((feature_names[idx], tfidf_vector[0, idx]))

        # Sort by TF-IDF score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return [word for word, score in scores[:max_indicators]]
    except Exception:
        return []


def check_security_flags(text: str) -> dict:
    """Analyze text for heuristic security flags."""
    return {
        "has_urls": bool(URL_PATTERN.search(text)),
        "has_urgency": bool(URGENCY_PATTERN.search(text))
    }


@app.route('/analyze', methods=['POST'])
@limiter.limit("60 per minute")
def analyze():
    """
    POST /analyze
    Input:  { "text": "message string" }
    Output: { 
              "prediction": "phishing" | "legitimate",
              "confidence": float (0-1),
              "indicators": ["word1", "word2", ...],
              "security_flags": {"has_urls": bool, "has_urgency": bool}
            }
    """
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({
            'error': 'Missing required field: text',
            'message': 'Please provide a JSON body with a "text" field.'
        }), 400

    text = data['text']
    if not isinstance(text, str) or not text.strip():
        return jsonify({
            'error': 'Invalid input',
            'message': 'The "text" field must be a non-empty string.'
        }), 400

    print(f"[INFO] Analyzed text from IP: {request.remote_addr} (length: {len(text)})")

    try:
        # Check security flags
        flags = check_security_flags(text)

        # Run ML Prediction
        result = predict_message(text)
        label = result['prediction']
        confidence = result['confidence']

        # Heuristic overrides
        if label == 'legitimate' and flags["has_urls"] and flags["has_urgency"]:
            label = 'phishing'
            # Boost confidence logically if overridden
            confidence = max(confidence, 0.80)
            print("[WARN] Heuristic override applied due to URL + Urgency patterns.")

        # Get key indicators
        indicators = get_key_indicators(text)

        return jsonify({
            'prediction': label,
            'confidence': confidence,
            'indicators': indicators,
            'security_flags': flags
        })

    except Exception as e:
        print(f"[ERR] Prediction failed: {str(e)}")
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'version': '2.0.0'
    })


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Returns the latest evaluation metrics from the saved model."""
    metrics_path = os.path.join(os.path.dirname(__file__), "models", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Metrics not found"}), 404


@app.route('/api/dataset', methods=['GET'])
def get_dataset_info():
    """Returns information about the current dataset."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        dataset_path = os.path.join(data_dir, "phishing_dataset.csv")
        
        if not os.path.exists(dataset_path):
            return jsonify({
                "exists": False,
                "total_rows": 0,
                "size_mb": 0
            })
            
        file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
        df = pd.read_csv(dataset_path)
        
        phishing_count = len(df[df['label'] == 'phishing']) if 'label' in df.columns else 0
        legitimate_count = len(df[df['label'] == 'legitimate']) if 'label' in df.columns else 0
        
        # Get a small sample
        sample = df.head(5).to_dict(orient='records')
        
        return jsonify({
            "exists": True,
            "total_rows": len(df),
            "phishing_count": phishing_count,
            "legitimate_count": legitimate_count,
            "size_mb": round(file_size_mb, 2),
            "columns": list(df.columns),
            "sample": sample
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dataset/upload', methods=['POST'])
def upload_dataset():
    """Uploads and replaces the phishing dataset."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Save exact name expected by the system
        filepath = os.path.join(data_dir, "phishing_dataset.csv")
        file.save(filepath)
        
        return jsonify({
            'message': 'Dataset uploaded successfully',
            'filename': filename
        })
        
    return jsonify({'error': 'Only CSV files are allowed'}), 400


if __name__ == '__main__':
    try:
        load_resources() # Pre-load model & vectorizer into memory
        print("[OK] Model and vectorizer loaded successfully")
    except Exception as e:
        print(f"[WARN] Starting server without pre-loaded model: {e}")
        
    print("\n[OK] Flask server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
