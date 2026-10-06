# src/scraper/scraper.py
"""
Steam Games Scraper

Scrapes the Steam store search results, downloads every
public‑facing game page, and extracts key attributes:
name, price, discount, reviews, tags, release date, publisher.

The scraped data is written to `data/raw/steam_games.csv`
inside the repository.  No command‑line arguments are
needed – just run the file.

Author: howlingwolfs
"""

from __future__ import annotations

import csv
import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Request helpers
# --------------------------------------------------------------------------- #
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

COOKIES = {
    "birthtime": "283993201",  # 1 Jan 1989 – bypass age gate
    "lastagecheckage": "1-0-1990",
    "wants_mature_content": "1",
}

MAX_RETRIES = 3
MIN_DELAY = 1.0  # seconds
MAX_DELAY = 3.0  # seconds


def make_request(session: requests.Session, url: str) -> requests.Response:
    """
    Perform a GET request with retries and a random delay.

    Args:
        session: requests.Session instance.
        url: URL to fetch.

    Returns:
        requests.Response object.

    Raises:
        requests.HTTPError if the final attempt fails.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, headers=HEADERS, cookies=COOKIES, timeout=30)
            resp.raise_for_status()
            log.debug("Fetched %s", url)
            return resp
        except requests.RequestException as exc:
            log.warning(
                "Attempt %d/%d failed for %s: %s",
                attempt,
                MAX_RETRIES,
                url,
                exc,
            )
            if attempt == MAX_RETRIES:
                raise
            # Wait a bit before retrying
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    # Unreachable, but keeps mypy happy
    raise RuntimeError("Unreachable code reached in make_request")


# --------------------------------------------------------------------------- #
# Scraping logic
# --------------------------------------------------------------------------- #
BASE_SEARCH_URL = "https://store.steampowered.com/search/?page={}"
GAME_ROW_CLASS = "search_result_row"
SEARCH_TIMEOUT = 30


def scrape_page(session: requests.Session, page_num: int) -> List[Dict]:
    """
    Scrape a single search results page.

    Returns:
        A list of dicts, one per game found on that page.
    """
    url = BASE_SEARCH_URL.format(page_num)
    log.info("Fetching search results page %d", page_num)

    resp = make_request(session, url)
    soup = BeautifulSoup(resp.text, "html.parser")

    game_rows = soup.find_all("a", class_=GAME_ROW_CLASS)
    if not game_rows:
        log.warning("No game rows found on page %d", page_num)

    games_data: List[Dict] = []

    for row in game_rows:
        game_url = row.get("href")
        if not game_url or "/app/" not in game_url:
            continue  # skip bundles, DLCs, etc.

        games_data.append(scrape_game(session, game_url))

    return games_data


def scrape_game(session: requests.Session, game_url: str) -> Dict:
    """
    Scrape a single Steam game page.

    Returns:
        A dict with keys: Game Name, Price, Discount, Reviews, Tags,
        Release Date, Publisher.
    """
    # Strip query params for clarity
    game_name_part = game_url.split("?")[0]
    log.info("Scraping: %s", game_name_part)

    resp = make_request(session, game_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Default values
    data: Dict = {
        "Game Name": "N/A",
        "Price": "N/A",
        "Discount": "0%",
        "Reviews": "N/A",
        "Tags": "N/A",
        "Release Date": "N/A",
        "Publisher": "N/A",
    }

    # 1️⃣ Game name
    name_tag = soup.find("div", class_="apphub_AppName")
    if name_tag:
        data["Game Name"] = name_tag.text.strip()

    # 2️⃣ Price & discount
    discount_block = soup.find("div", class_="discount_block")
    if discount_block:
        final_price = discount_block.find("div", class_="discount_final_price")
        if final_price:
            data["Price"] = final_price.text.strip()

        discount_pct = discount_block.find("div", class_="discount_pct")
        if discount_pct:
            data["Discount"] = discount_pct.text.strip()
    else:
        # No discount – grab the normal price
        regular_price = soup.find("div", class_="game_purchase_price")
        if regular_price and regular_price.text.strip():
            data["Price"] = regular_price.text.strip()
        else:
            data["Price"] = "Free to Play / Not Available"

    # 3️⃣ Reviews
    review_tag = soup.find("span", class_="game_review_summary")
    if review_tag:
        data["Reviews"] = review_tag.text.strip()

    # 4️⃣ Tags
    tag_elements = soup.find_all("a", class_="app_tag")
    if tag_elements:
        tags = [t.text.strip() for t in tag_elements if t.text.strip() != "+"]
        data["Tags"] = ", ".join(tags)

    # 5️⃣ Release date
    release_div = soup.find("div", class_="release_date")
    if release_div:
        date_tag = release_div.find("div", class_="date")
        if date_tag:
            data["Release Date"] = date_tag.text.strip()

    # 6️⃣ Publisher
    dev_rows = soup.find_all("div", class_="dev_row")
    for dev_row in dev_rows:
        subtitle = dev_row.find("div", class_="subtitle")
        if subtitle and "Publisher:" in subtitle.text:
            pubs = dev_row.find_all("a")
            data["Publisher"] = ", ".join([p.text.strip() for p in pubs])
            break

    # Random sleep between 1–3 s to be polite to Steam
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    return data


def scrape_steam_store(pages_to_scrape: int = 1) -> List[Dict]:
    """
    Orchestrate the scraping of multiple search pages.

    Args:
        pages_to_scrape: Number of pagination pages to crawl.

    Returns:
        List of game data dicts.
    """
    session = requests.Session()
    all_games: List[Dict] = []

    for page_num in range(1, pages_to_scrape + 1):
        page_data = scrape_page(session, page_num)
        all_games.extend(page_data)

    return all_games


# --------------------------------------------------------------------------- #
# CSV export
# --------------------------------------------------------------------------- #
def write_csv(games: List[Dict], csv_path: Path) -> None:
    """
    Write the scraped data to a CSV file.

    Args:
        games: List of game data dictionaries.
        csv_path: Path where the CSV will be written.
    """
    if not games:
        log.warning("No data to write – CSV will not be created.")
        return

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    keys = games[0].keys()

    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=keys)
        writer.writeheader()
        writer.writerows(games)

    log.info("Wrote %d records to %s", len(games), csv_path)


# --------------------------------------------------------------------------- #
# Main script block
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # ---------------------------- #
    # USER‑CONFIGURATION
    # ---------------------------- #
    # 1️⃣ How many search‑results pages to scrape (default 200)
    PAGES_TO_SCRAPE = 200

    # 2️⃣ Where to put the raw CSV
    CSV_FILE_PATH = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "raw"
        / "steam_games.csv"
    )

    log.info("Starting Steam scraper …")
    try:
        scraped_games = scrape_steam_store(PAGES_TO_SCRAPE)
    except Exception as exc:
        log.exception("Scraping aborted: %s", exc)
        raise

    write_csv(scraped_games, CSV_FILE_PATH)
    log.info("Scraping finished successfully.")
