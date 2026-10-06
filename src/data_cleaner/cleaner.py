# src/data_cleaner/cleaner.py
"""
Steam Games Data Cleaner

This script reads the raw CSV produced by the scraper,
performs all the cleaning / feature engineering that was
originally done in `visualization.py`, and writes a cleaned
CSV to the `data/processed` folder.

Usage
-----
    python .\src\data_cleaner\cleaner.py

No arguments are required. The file paths are hard‑coded
according to the repository layout.

Author: howlingwolfs
"""

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------------- #

def get_top_five_tags(tag_series: pd.Series) -> pd.Series:
    """Return the first 5 tags per game as a comma‑separated string."""
    return (
        tag_series
        .str.split(",")
        .str[:5]
        .apply(lambda tags: ", ".join([t.strip() for t in tags]))
    )


def extract_and_convert_price(price_str: str) -> float:
    """Convert a price string (e.g. '$19.99') to a float.
    Returns 0.0 for 'Free To Play' and NaN for malformed entries."""
    if not isinstance(price_str, str):
        return np.nan

    if "Free To Play" in price_str:
        return 0.0

    cleaned = price_str.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def extract_review_count(review_str: str) -> int:
    """Return the number of user reviews, or 0 if none is found."""
    if pd.isna(review_str):
        return 0

    match = re.search(r"(\d+)\s+user\s+reviews", str(review_str), re.IGNORECASE)
    return int(match.group(1)) if match else 0


# Sentiment mapping used by the original script
SENTIMENT_MAP = {
    "Overwhelmingly Positive": 3,
    "Very Positive": 2,
    "Positive": 1,
    "Mixed": 0,
    "Mostly Negative": -1,
    "Very Negative": -2,
    "Overwhelmingly Negative": -3,
}


def encode_sentiment(review_str: str) -> int:
    """Map the textual sentiment to a numeric score."""
    if pd.isna(review_str) or "No" in review_str:
        return 0  # Neutral

    for text, score in SENTIMENT_MAP.items():
        if text in review_str:
            return score
    return 0


# --------------------------------------------------------------------------- #
# Core cleaning routine
# --------------------------------------------------------------------------- #

def clean_steam_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning steps that were originally in `visualization.py`.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame loaded from the scraper output.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for analysis / visualization.
    """
    # 1. Drop duplicates
    df = df.drop_duplicates()

    # 2. Fill missing scalar columns
    df["Game Name"] = df["Game Name"].fillna("")
    df["Reviews"] = df["Reviews"].fillna("No Reviews")
    df["Tags"] = df["Tags"].fillna("No Tags")
    df["Release Date"] = df["Release Date"].fillna("Unknown")
    df["Publisher"] = df["Publisher"].fillna("Unknown Publisher")

    # 3. Derived columns
    df["Top Five Tags"] = get_top_five_tags(df["Tags"])

    # 4. Release date to datetime + year
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
    df["Release_Year"] = df["Release Date"].dt.year

    # 5. Numeric price
    df["Numeric_Price"] = df["Price"].apply(extract_and_convert_price)

    # 6. Review count
    df["Review_Count"] = df["Reviews"].apply(extract_review_count)

    # 7. Sentiment score
    df["Sentiment_Score"] = df["Reviews"].apply(encode_sentiment)

    return df


# --------------------------------------------------------------------------- #
# Main script block
# --------------------------------------------------------------------------- #

def main() -> None:
    """Read raw CSV → clean → write processed CSV."""
    # Define paths relative to this file
    base_dir = Path(__file__).resolve().parent.parent.parent
    raw_path = base_dir / "data" / "raw" / "steam_games.csv"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_path = processed_dir / "steam_games_clean.csv"

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw file not found: {raw_path}")

    print(f"Reading raw data from {raw_path}")
    df_raw = pd.read_csv(raw_path)

    print("Cleaning data…")
    df_clean = clean_steam_data(df_raw)

    print(f"Writing cleaned data to {out_path}")
    df_clean.to_csv(out_path, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
