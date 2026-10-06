# src/visualizations/visualizations.py
"""
Steam Games Visualisation Suite

This module reads the cleaned Steam‑Games CSV
(`data/processed/steam_games_clean.csv`) and generates a collection of
interactive visualisations (Plotly + Seaborn).  The figures are
written to `data/visualizations/` as individual HTML files that can be
opened in any browser.

Author: howlingwolfs
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns

# --------------------------------------------------------------------------- #
# Configuration (edit these if you want different input/output paths)
# --------------------------------------------------------------------------- #
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]  # repo root
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "visualizations"
DATA_FILE = DATA_DIR / "steam_games_clean.csv"

# --------------------------------------------------------------------------- #
# Helper utilities
# --------------------------------------------------------------------------- #
def _ensure_output_dir() -> None:
    """Create the output folder if it does not yet exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_data() -> pd.DataFrame:
    """Load the cleaned Steam data into a DataFrame."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE, parse_dates=["Release Date"])
    # Convert numeric price to float (the cleaning step may have left NaNs)
    df["Numeric_Price"] = pd.to_numeric(df["Numeric_Price"], errors="coerce")
    return df


# --------------------------------------------------------------------------- #
# Individual visualisations
# --------------------------------------------------------------------------- #
def price_distribution(df: pd.DataFrame) -> None:
    """Histogram of game prices (Plotly)."""
    fig = px.histogram(
        df,
        x="Numeric_Price",
        nbins=80,
        title="Distribution of Steam Game Prices",
        marginal="rug",
        color_discrete_sequence=["#636efa"],
        opacity=0.75,
    )
    fig.update_layout(bargap=0.1)
    fig.add_vline(
        x=df["Numeric_Price"].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${df['Numeric_Price'].mean():.2f}",
    )
    fig.write_html(OUTPUT_DIR / "price_distribution.html")
    print("[✓] price_distribution.html")


def sentiment_distribution(df: pd.DataFrame) -> None:
    """Bar plot of sentiment scores (Plotly)."""
    counts = df["Sentiment_Score"].value_counts().sort_index()
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x": "Sentiment Score", "y": "Number of Games"},
        title="Sentiment Score Distribution",
        color=counts.index,
        color_continuous_scale="RdYlGn",
    )
    fig.write_html(OUTPUT_DIR / "sentiment_distribution.html")
    print("[✓] sentiment_distribution.html")


def price_vs_sentiment(df: pd.DataFrame) -> None:
    """Box plot of price by sentiment score (Plotly)."""
    fig = px.box(
        df,
        x="Sentiment_Score",
        y="Numeric_Price",
        points="all",
        title="Price Distribution by Sentiment",
        labels={"Sentiment_Score": "Sentiment Score", "Numeric_Price": "Price ($)"},
    )
    fig.write_html(OUTPUT_DIR / "price_vs_sentiment.html")
    print("[✓] price_vs_sentiment.html")


def review_vs_sentiment(df: pd.DataFrame) -> None:
    """Scatter plot of review count vs. sentiment (Plotly)."""
    fig = px.scatter(
        df,
        x="Review_Count",
        y="Sentiment_Score",
        color="Sentiment_Score",
        title="Review Count vs. Sentiment Score",
        labels={
            "Review_Count": "Number of Reviews",
            "Sentiment_Score": "Sentiment Score",
        },
    )
    fig.write_html(OUTPUT_DIR / "review_vs_sentiment.html")
    print("[✓] review_vs_sentiment.html")


def top_publishers(df: pd.DataFrame, n: int = 15) -> None:
    """Bar chart of the most frequent publishers (Plotly)."""
    counts = df["Publisher"].value_counts().nlargest(n)
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        title=f"Top {n} Publishers",
        labels={"x": "Publisher", "y": "Number of Games"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.write_html(OUTPUT_DIR / "top_publishers.html")
    print("[✓] top_publishers.html")


def tag_popularity(df: pd.DataFrame, n: int = 20) -> None:
    """Bar chart of the most common tags (Seaborn + Matplotlib)."""
    # explode tags into a single series
    tags = (
        df["Tags"]
        .apply(lambda t: [tag.strip() for tag in t.split(",")])
        .explode()
        .dropna()
    )
    tags = tags[tags != "No Tags"]
    counts = tags.value_counts().head(n)

    plt.figure(figsize=(12, 6))
    sns.barplot(x=counts.index, y=counts.values, palette="viridis")
    plt.title(f"Top {n} Game Tags")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "tag_popularity.png")
    plt.close()
    print("[✓] tag_popularity.png")


# --------------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------------- #
def main() -> None:
    """Generate all visualisations from the cleaned data."""
    _ensure_output_dir()
    df = _load_data()

    print(f"Loaded {len(df)} records from {DATA_FILE}")

    # ----- Plotly charts -----
    price_distribution(df)
    sentiment_distribution(df)
    price_vs_sentiment(df)
    review_vs_sentiment(df)
    top_publishers(df)

    # ----- Seaborn/Matplotlib chart -----
    tag_popularity(df)

    # ---- Optional: write a summary JSON for quick stats ----
    stats: Dict[str, Tuple[float, int]] = {
        "total_games": (len(df), 0),
        "mean_price": (df["Numeric_Price"].mean(), 0),
        "median_price": (df["Numeric_Price"].median(), 0),
        "max_price": (df["Numeric_Price"].max(), 0),
        "min_price": (df["Numeric_Price"].min(), 0),
        "most_common_sentiment": (
            df["Sentiment_Score"].value_counts().idxmax(),
            0,
        ),
    }
    stats_path = OUTPUT_DIR / "summary_stats.json"
    with stats_path.open("w", encoding="utf-8") as fp:
        json.dump(stats, fp, indent=4, default=str)
    print(f"[✓] summary_stats.json")


if __name__ == "__main__":
    main()
