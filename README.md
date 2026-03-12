# AI-Powered Phishing Detection Using NLP

A complete web application that detects phishing messages using Natural Language Processing (NLP) and Machine Learning.

![AI Phishing Detection](https://img.shields.io/badge/AI-Phishing%20Detection-blue) ![Python](https://img.shields.io/badge/Python-Flask-green) ![React](https://img.shields.io/badge/React-TypeScript-61DAFB)

---

## Features

- **ML-powered detection** — Trained NLP model (TF-IDF + SVM) for accurate phishing classification
- **Real-time analysis** — Instant predictions with confidence scores
- **Key indicators** — Highlights the most important words driving the detection
- **Dark futuristic UI** — Glassmorphism design with smooth animations
- **REST API** — Clean `/predict` endpoint for integration

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python, Flask, scikit-learn, NLTK, spaCy |
| Frontend  | React, TypeScript, TailwindCSS, Vite |
| ML Models | Multinomial Naive Bayes, Linear SVC  |
| Features  | TF-IDF with unigram + bigram        |

---

## Project Structure

```
Ai Phishing/
├── backend/
│   ├── data/
│   │   └── dataset.csv          # Training dataset (120+ samples)
│   ├── models/
│   │   ├── best_model.joblib    # Trained ML model (auto-generated)
│   │   └── tfidf_vectorizer.joblib  # Fitted vectorizer (auto-generated)
│   ├── app.py                   # Flask API server
│   ├── preprocessing.py         # NLP text preprocessing
│   ├── feature_engineering.py   # TF-IDF vectorization
│   ├── train.py                 # Model training script
│   └── requirements.txt         # Python dependencies
├── project/
│   ├── src/
│   │   ├── components/          # React UI components
│   │   ├── services/            # API service layer
│   │   ├── types/               # TypeScript types
│   │   ├── App.tsx              # Main application
│   │   └── index.css            # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Setup & Run

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Train the ML model
python train.py

# Start the Flask API (runs on http://localhost:5000)
python app.py
```

### 2. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd project

# Install Node.js dependencies
npm install

# Start the dev server (runs on http://localhost:5173)
npm run dev
```

### 3. Use the App

1. Open **http://localhost:5173** in your browser
2. Paste any email, SMS, or message text
3. Click **Analyze Message** (or press Ctrl+Enter)
4. View the prediction, confidence score, and key indicator words

---

## API Reference

### `POST /predict`

**Request:**
```json
{
  "text": "URGENT: Your account has been compromised. Click here to verify."
}
```

**Response:**
```json
{
  "prediction": "phishing",
  "confidence": 0.97,
  "indicators": ["urgent", "account", "compromised", "verify", "click"]
}
```

### `GET /health`

Returns `{ "status": "ok", "model_loaded": true }`

---

## Model Performance

The training script automatically:
- Trains **Multinomial Naive Bayes** and **Calibrated Linear SVC**
- Compares accuracy, precision, recall, and F1 score
- Selects and saves the best-performing model
- Target accuracy: **≥ 90%**

---

## License

This project is for educational purposes.
