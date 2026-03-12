"""
Dataset loader module for the phishing detection ML system.
Loads, validates, and cleans the phishing CSV dataset for model training.

Expected CSV format:
    text,label
    "Your account has been compromised...", phishing
    "Meeting scheduled for Monday...", legitimate

Usage:
    from dataset_loader import load_dataset

    df = load_dataset()                       # default path
    df = load_dataset("path/to/custom.csv")   # custom path
"""

import os
import sys
import pandas as pd

# ── Constants ───────────────────────────────────────────────────────

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
REQUIRED_COLUMNS = {"text", "label"}

# Labels that should map to "phishing"
PHISHING_ALIASES = {"1", "phishing", "spam", "malicious"}


# ── Public API ──────────────────────────────────────────────────────

def load_dataset(path: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the phishing dataset from a CSV file, validate its structure,
    clean null/empty rows, and normalise labels.

    Args:
        path: Absolute or relative path to the CSV file.
              Defaults to ``backend/data/dataset.csv``.

    Returns:
        A cleaned ``pd.DataFrame`` with columns ``text`` (str) and
        ``label`` (str — 'phishing' or 'legitimate').

    Raises:
        SystemExit: If the file is missing, has wrong columns, or
                    contains no usable rows after cleaning.
    """
    # 1. Check file exists
    if not os.path.exists(path):
        _fatal(f"Dataset not found at {path}")

    # 2. Read CSV
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        _fatal(f"Failed to read CSV: {exc}")

    # 3. Validate required columns
    _validate_columns(df)

    # 4. Clean null / empty rows
    df = _clean_rows(df)

    # 5. Normalise labels
    df["label"] = df["label"].apply(_normalise_label)

    # 6. Summary
    _print_summary(df)
    return df


# ── Internal Helpers ────────────────────────────────────────────────

def _validate_columns(df: pd.DataFrame) -> None:
    """Ensure the dataframe contains 'text' and 'label' columns."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        _fatal(
            f"Dataset is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )


def _clean_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where 'text' or 'label' is null or empty."""
    before = len(df)

    # Drop nulls
    df = df.dropna(subset=["text", "label"])

    # Drop rows with empty / whitespace-only text
    df = df[df["text"].astype(str).str.strip().astype(bool)]
    df = df[df["label"].astype(str).str.strip().astype(bool)]

    removed = before - len(df)
    if removed:
        print(f"[CLEAN] Removed {removed} null/empty rows")

    if df.empty:
        _fatal("Dataset has no usable rows after cleaning")

    return df.reset_index(drop=True)


def _normalise_label(val) -> str:
    """Map various label representations to 'phishing' or 'legitimate'."""
    normalised = str(val).lower().strip()
    return "phishing" if normalised in PHISHING_ALIASES else "legitimate"


def _print_summary(df: pd.DataFrame) -> None:
    """Print a concise dataset summary."""
    total = len(df)
    legit = (df["label"] == "legitimate").sum()
    phish = (df["label"] == "phishing").sum()
    print(f"[OK] Loaded dataset: {total} samples")
    print(f"     Legitimate : {legit}")
    print(f"     Phishing   : {phish}")


def _fatal(message: str) -> None:
    """Print an error and exit."""
    print(f"[ERR] {message}")
    sys.exit(1)


# ── CLI usage ───────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_dataset()
    print(f"\nFirst 5 rows:\n{df.head()}")
