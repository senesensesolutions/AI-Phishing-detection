"""
Preprocessing module for phishing detection.
Handles text cleaning: lowercase, remove special chars,
remove stopwords (NLTK), and lemmatize (spaCy).
"""

import re
import nltk
import spacy

# Download required NLTK data (only on first run)
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Load spaCy English model for lemmatization
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not installed, download it
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# NLTK stopwords set
STOPWORDS = set(nltk.corpus.stopwords.words('english'))


def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline for a single text input.
    Steps:
      1. Lowercase
      2. Remove special characters and punctuation
      3. Remove stopwords
      4. Lemmatize using spaCy
    Returns cleaned text string. Handles empty/invalid input safely.
    """
    # Handle None or non-string input
    if not text or not isinstance(text, str):
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove special characters, punctuation, and digits
    text = re.sub(r'[^a-z\s]', '', text)

    # 3. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return ""

    # 4. Tokenize into words, remove stopwords
    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 1]

    # 5. Lemmatize using spaCy
    doc = nlp(' '.join(words))
    lemmatized = [token.lemma_ for token in doc if token.lemma_.strip()]

    return ' '.join(lemmatized)


def preprocess_batch(texts: list) -> list:
    """Preprocess a list of texts. Skips invalid entries."""
    return [preprocess_text(t) for t in texts]
