"""
BERT integration module for phishing detection.
Handles dataset tokenisation, HuggingFace model fine-tuning (distilbert),
saving the trained model, and providing a prediction endpoint.
"""

import os
import torch
import numpy as np
import pandas as pd
from typing import Tuple, Dict

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        Trainer,
        TrainingArguments,
    )
    from datasets import Dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("[WARN] transformers or datasets library not installed. BERT unavailable.")

# Configuration
PRETRAINED_MODEL_NAME = "distilbert-base-uncased"
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
BERT_SAVE_PATH = os.path.join(MODELS_DIR, "bert_model")

# Label mappings
LABEL2ID = {"legitimate": 0, "phishing": 1}
ID2LABEL = {0: "legitimate", 1: "phishing"}


def check_hf_available():
    if not HF_AVAILABLE:
        raise ImportError(
            "HuggingFace libraries not installed. Run: pip install torch transformers datasets accelerate"
        )


def _tokenize_function(examples, tokenizer):
    """Tokenize the text data."""
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )


def build_and_train_bert(df: pd.DataFrame, test_size: float = 0.2) -> Tuple[float, str]:
    """
    Fine-tune a distilbert sequence classification model on the dataset.
    
    Args:
        df: Pandas DataFrame containing 'cleaned' and 'label' columns.
        test_size: Proportion of the dataset to include in the test split.

    Returns:
        Tuple containing the evaluation accuracy and the path the model was saved to.
    """
    check_hf_available()
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    print("\n" + "=" * 60)
    print("  BERT Model Fine-Tuning")
    print("=" * 60)
    print(f"[*] Base model: {PRETRAINED_MODEL_NAME}")

    # Ensure device is available (GPU if possible)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Using device: {device}")

    # Format dataframe for HuggingFace
    hf_df = df.copy()
    hf_df['label_id'] = hf_df['label'].map(LABEL2ID)
    
    # Split
    train_df, eval_df = train_test_split(
        hf_df, test_size=test_size, random_state=42, stratify=hf_df['label_id']
    )
    
    # Convert to HF Datasets
    train_dataset = Dataset.from_pandas(train_df[['cleaned', 'label_id']].rename(columns={'cleaned': 'text', 'label_id': 'label'}))
    eval_dataset = Dataset.from_pandas(eval_df[['cleaned', 'label_id']].rename(columns={'cleaned': 'text', 'label_id': 'label'}))

    # Load Tokenizer
    print("[...] Loading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)

    # Tokenize datasets
    print("[...] Tokenizing datasets...")
    train_tokenized = train_dataset.map(lambda e: _tokenize_function(e, tokenizer), batched=True)
    eval_tokenized = eval_dataset.map(lambda e: _tokenize_function(e, tokenizer), batched=True)

    # Load Model
    print("[...] Loading pre-trained Classification Model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        PRETRAINED_MODEL_NAME, 
        num_labels=2,
        id2label=ID2LABEL,
        label2id=LABEL2ID
    ).to(device)

    # Define Metrics
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {"accuracy": accuracy_score(labels, predictions)}

    # Training Arguments
    training_args = TrainingArguments(
        output_dir=os.path.join(MODELS_DIR, "results"),
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir=os.path.join(MODELS_DIR, "logs"),
        logging_steps=10,
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=eval_tokenized,
        compute_metrics=compute_metrics,
    )

    # Train
    print("[...] Starting training loop (this may take a while)...")
    trainer.train()

    # Evaluate
    print("[...] Evaluating best model...")
    eval_results = trainer.evaluate()
    accuracy = eval_results.get("eval_accuracy", 0.0)
    print(f"\n  [OK] BERT Evaluation Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")

    # Save
    print(f"[...] Saving best model to {BERT_SAVE_PATH}...")
    model.save_pretrained(BERT_SAVE_PATH)
    tokenizer.save_pretrained(BERT_SAVE_PATH)
    print("[OK] BERT model and tokenizer saved.")

    return accuracy, BERT_SAVE_PATH


# ── Prediction API ──────────────────────────────────────────────────

_bert_model = None
_bert_tokenizer = None

def load_bert_resources():
    """Load the trained BERT model and tokenizer into memory."""
    global _bert_model, _bert_tokenizer
    check_hf_available()
    
    if _bert_model is None or _bert_tokenizer is None:
        if not os.path.exists(BERT_SAVE_PATH):
            raise FileNotFoundError(f"BERT model not found at {BERT_SAVE_PATH}. Train it first.")
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _bert_tokenizer = AutoTokenizer.from_pretrained(BERT_SAVE_PATH)
        _bert_model = AutoModelForSequenceClassification.from_pretrained(BERT_SAVE_PATH).to(device)
        _bert_model.eval()


def predict_bert(text: str) -> Dict:
    """
    Predict using the fine-tuned BERT model.
    Assumes `text` is already preprocessed.
    """
    load_bert_resources()
    device = _bert_model.device

    # Tokenize input
    inputs = _bert_tokenizer(
        text, 
        padding="max_length", 
        truncation=True, 
        max_length=128, 
        return_tensors="pt"
    ).to(device)

    # Predict
    with torch.no_grad():
        outputs = _bert_model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0]
        
    pred_idx = np.argmax(probabilities)
    confidence = float(probabilities[pred_idx])
    label = ID2LABEL[pred_idx]

    return {
        "prediction": label,
        "confidence": confidence
    }
