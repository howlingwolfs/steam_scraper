#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Steam Games Dashboard – Streamlit version (updated for Streamlit 1.39+)

Author: howlingwolfs
"""

# ------------------------------------------------------------------ #
# Path helper – make sure the `src` package is importable
# ------------------------------------------------------------------ #
import sys
from pathlib import Path

# Two levels up: app → steam_scraper/
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# ------------------------------------------------------------------ #
# Imports
# ------------------------------------------------------------------ #
import re
import time
from typing import List, Dict

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Project modules
from src.scraper.steam_scraper import scrape_steam_store, write_csv
from src.data_cleaner.cleaner import (
    clean_steam_data,
    get_top_five_tags,
    extract_and_convert_price,
    extract_review_count,
    encode_sentiment,
)

# ------------------------------------------------------------------ #
# Paths (adapted to the new folder structure)
# ------------------------------------------------------------------ #
BASE_DIR = Path(__file__).resolve().parents[1]          # steam_scraper/
RAW_PATH = BASE_DIR / "data" / "raw" / "steam_games.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_PATH = PROCESSED_DIR / "steam_games_clean.csv"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ #
# Helper functions
# ------------------------------------------------------------------ #
@st.cache_data(show_spinner=False)
def load_processed_data(csv_path: Path = PROCESSED_PATH) -> pd.DataFrame:
    """Load the cleaned CSV that is ready for analysis."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Processed file not found: {csv_path}")
    df = pd.read_csv(csv_path, dtype=str)
    df["Numeric_Price"] = pd.to_numeric(df["Numeric_Price"], errors="coerce")
    df["Release_Year"] = pd.to_numeric(df["Release_Year"], errors="coerce")
    return df

def clean_and_save(raw_path: Path, processed_path: Path) -> pd.DataFrame:
    """Read the raw CSV, clean it, write the processed file and return the DataFrame."""
    df_raw = pd.read_csv(raw_path, dtype=str)
    df_clean = clean_steam_data(df_raw)
    df_clean.to_csv(processed_path, index=False)
    st.toast("Data cleaned and saved.", icon="✅")
    return df_clean

def run_scraping_and_cleaning(pages_to_scrape: int) -> pd.DataFrame:
    """Scrape the store, write raw CSV, clean it and return the cleaned DataFrame."""
    with st.spinner("Scraping Steam store…"):
        all_games = scrape_steam_store(pages_to_scrape)
    if not all_games:
        st.warning("No games were scraped – aborting.")
        return pd.DataFrame()

    write_csv(all_games, RAW_PATH)
    st.toast(f"Raw data written to {RAW_PATH.name}.", icon="🗂️")

    with st.spinner("Cleaning data…"):
        df_clean = clean_and_save(RAW_PATH, PROCESSED_PATH)

    return df_clean

# ------------------------------------------------------------------ #
# Streamlit UI
# ------------------------------------------------------------------ #
def main() -> None:
    """App entry point."""
    st.set_page_config(page_title="Steam Games Dashboard", layout="wide", page_icon="🎮")

    st.title("🎮 Steam Games Dashboard")
    st.markdown(
        """
        Explore pricing, sentiment, publishers, tags and more from the Steam games dataset.
        Use the **Scrape Fresh Data** button to pull the latest information from Steam.
        """
    )

    # ------------------------------------------------------------------
    # Sidebar – Data actions
    # ------------------------------------------------------------------
    st.sidebar.header("Data actions")
    with st.sidebar.expander("Scrape & Clean", expanded=False):
        pages_to_scrape = st.number_input(
            "Pages to scrape (≈ 200 = full catalogue)",
            min_value=1,
            value=200,
            step=50,
        )
        if st.button("Scrape Fresh Data", type="primary"):
            try:
                df = run_scraping_and_cleaning(int(pages_to_scrape))
                if df.empty:
                    st.sidebar.warning("No data after scraping.")
                else:
                    st.session_state["df"] = df
            except Exception as exc:
                st.sidebar.error(f"Error: {exc}")

    # Load data (either from session or from disk)
    if "df" in st.session_state:
        df = st.session_state["df"]
    else:
        try:
            df = load_processed_data()
        except FileNotFoundError:
            st.warning(
                "No processed data found. Use the *Scrape Fresh Data* button to start."
            )
            df = pd.DataFrame()

    if df.empty:
        st.stop()

    # ------------------------------------------------------------------
    # Sidebar – Filters
    # ------------------------------------------------------------------
    st.sidebar.header("Filters")

    # Price filter
    price_min = float(df["Numeric_Price"].replace(np.nan, 0).min())
    price_max = float(df["Numeric_Price"].replace(np.nan, 0).max())
    price_range = st.sidebar.slider(
        "Price range ($)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=0.5,
    )

    # Sentiment filter
    sentiment_options = sorted(df["Sentiment_Score"].unique())
    sentiment_selected = st.sidebar.multiselect(
        "Sentiment score", options=sentiment_options, default=sentiment_options
    )

    # Publisher filter
    top_publishers = df["Publisher"].value_counts().nlargest(20).index.tolist()
    publisher_selected = st.sidebar.multiselect(
        "Publishers", options=top_publishers, default=top_publishers
    )

    # Release year filter
    years = df["Release_Year"].dropna()
    year_min = int(years.min()) if not years.empty else 1900
    year_max = int(years.max()) if not years.empty else 2100
    year_range = st.sidebar.slider(
        "Release year",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
    )

    # Tag filter
    all_tags = (
        df["Tags"]
        .apply(lambda t: [tag.strip() for tag in t.split(",")])
        .explode()
        .unique()
        .tolist()
    )
    tag_selected = st.sidebar.multiselect("Tags", options=all_tags, default=[])

    # ------------------------------------------------------------------
    # Apply filters
    # ------------------------------------------------------------------
    base_filtered = df[
        (df["Numeric_Price"].astype(float) >= price_range[0])
        & (df["Numeric_Price"].astype(float) <= price_range[1])
        & (df["Sentiment_Score"].isin(sentiment_selected))
        & (df["Publisher"].isin(publisher_selected))
        & df["Release_Year"].notna()
        ]

    filtered = base_filtered[
        (base_filtered["Release_Year"].astype(int) >= year_range[0])
        & (base_filtered["Release_Year"].astype(int) <= year_range[1])
        ]

    if tag_selected:
        tag_regex = "|".join(map(re.escape, tag_selected))
        filtered = filtered[filtered["Top Five Tags"].str.contains(tag_regex, na=False)]
    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("Filtered Data Overview")
    st.write(f"**Total games**: {len(filtered)}")
    if not filtered.empty:
        st.dataframe(filtered.head(10))
    else:
        st.warning("No games match the current filter set.")

    # ------------------------------------------------------------------
    # Visualisations
    # ------------------------------------------------------------------
    st.markdown("## Visualisations")

    if filtered.empty:
        st.info("No data to visualise after applying the filters.")
    else:
        # 1️⃣ Distribution of Game Prices
        st.subheader("1️⃣ Distribution of Game Prices")
        price_fig = px.histogram(
            filtered,
            x="Numeric_Price",
            nbins=50,
            marginal="rug",
            title="Distribution of Game Prices",
            opacity=0.75,
        )
        mean_price = filtered["Numeric_Price"].astype(float).mean()
        price_fig.add_vline(
            x=mean_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: ${mean_price:.2f}",
        )
        st.plotly_chart(price_fig, use_container_width=True)

        # 2️⃣ Sentiment distribution
        st.subheader("2️⃣ Distribution of Sentiment Scores")
        sentiment_counts = filtered["Sentiment_Score"].value_counts().sort_index()
        sentiment_fig = px.bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            labels={"x": "Sentiment Score", "y": "Number of Games"},
            title="Sentiment Score Distribution",
            color=sentiment_counts.index,
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(sentiment_fig, use_container_width=True)

        # 3️⃣ Price vs. Sentiment
        st.subheader("3️⃣ Price Distribution by Sentiment")
        price_sentiment_fig = px.box(
            filtered,
            x="Sentiment_Score",
            y="Numeric_Price",
            points="all",
            title="Price Distribution by Sentiment",
            labels={"Sentiment_Score": "Sentiment Score", "Numeric_Price": "Price ($)"},
        )
        st.plotly_chart(price_sentiment_fig, use_container_width=True)

        # 4️⃣ Review Count vs. Sentiment
        st.subheader("4️⃣ Review Count vs. Sentiment Score")
        review_sentiment_fig = px.scatter(
            filtered,
            x="Review_Count",
            y="Sentiment_Score",
            color="Sentiment_Score",
            title="Review Count vs. Sentiment",
            labels={"Review_Count": "Review Count", "Sentiment_Score": "Sentiment Score"},
        )
        st.plotly_chart(review_sentiment_fig, use_container_width=True)

        # 5️⃣ Top publishers
        st.subheader("5️⃣ Top Publishers")
        publisher_counts = filtered["Publisher"].value_counts().head(15)
        publisher_fig = px.bar(
            x=publisher_counts.index,
            y=publisher_counts.values,
            title="Top 15 Publishers",
            labels={"x": "Publisher", "y": "Number of Games"},
        )
        publisher_fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(publisher_fig, use_container_width=True)

        # 6️⃣ Tag popularity
        st.subheader("6️⃣ Top 20 Most Common Tags")
        tags_list = (
            filtered["Tags"]
            .apply(lambda t: [tag.strip() for tag in t.split(",")])
            .explode()
            .dropna()
        )
        tag_counts = tags_list[tags_list != "No Tags"].value_counts().head(20)
        tag_fig = px.bar(
            x=tag_counts.index,
            y=tag_counts.values,
            title="Top 20 Tags",
            labels={"x": "Tag", "y": "Frequency"},
        )
        tag_fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(tag_fig, use_container_width=True)

    # ------------------------------------------------------------------
    # Download filtered data
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("Download Filtered Data")
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="filtered_steam_games.csv",
        mime="text/csv",
    )

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("Data source: [Steam](https://store.steampowered.com/)")
    st.sidebar.markdown("Built with Streamlit 🚀")


# ------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
