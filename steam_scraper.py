import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_steam_store(pages_to_scrape=1):
    # Base search URL. We will loop through pagination.
    search_url = "https://store.steampowered.com/search/?page="

    # CRITICAL: Cookies to bypass the age gate for Mature/M-rated games
    # Without this, games like GTA V or Cyberpunk will return an age-verification page
    cookies = {
        'birthtime': '283993201',
        'lastagecheckage': '1-0-1990',
        'wants_mature_content': '1'
    }

    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    all_games_data = []

    for page in range(1, pages_to_scrape + 1):
        print(f"Fetching Search Page {page}...")
        response = requests.get(f"{search_url}{page}", headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Grab all the game rows on the search page
        game_rows = soup.find_all('a', class_='search_result_row')

        for row in game_rows:
            game_url = row.get('href')

            # Skip bundles or packages (they don't have standard app IDs)
            if '/app/' not in game_url:
                continue

            print(f"Scraping: {game_url.split('?')[0]}")

            # Request the individual game's store page
            game_res = requests.get(game_url, headers=headers, cookies=cookies)
            game_soup = BeautifulSoup(game_res.text, 'html.parser')

            # Initialize our data dictionary with default values
            game_data = {
                'Game Name': 'N/A',
                'Price': 'N/A',
                'Discount': '0%',
                'Reviews': 'N/A',
                'Tags': 'N/A',
                'Release Date': 'N/A',
                'Publisher': 'N/A'
            }

            # 1. Game Name
            name_tag = game_soup.find('div', class_='apphub_AppName')
            if name_tag:
                game_data['Game Name'] = name_tag.text.strip()

            # 2. Price & 3. Discount
            discount_block = game_soup.find('div', class_='discount_block')
            if discount_block:
                final_price = discount_block.find('div', class_='discount_final_price')
                if final_price:
                    game_data['Price'] = final_price.text.strip()

                discount_pct = discount_block.find('div', class_='discount_pct')
                if discount_pct:
                    game_data['Discount'] = discount_pct.text.strip()
            else:
                # If the game is not on sale
                regular_price = game_soup.find('div', class_='game_purchase_price')
                if regular_price and regular_price.text.strip():
                    game_data['Price'] = regular_price.text.strip()
                else:
                    game_data['Price'] = 'Free to Play / Not Available'

            # 4. Reviews
            review_tag = game_soup.find('span', class_='game_review_summary')
            if review_tag:
                game_data['Reviews'] = review_tag.text.strip()

            # 5. Tags
            tag_elements = game_soup.find_all('a', class_='app_tag')
            if tag_elements:
                # Exclude the trailing '+' symbol used in the UI
                tags = [t.text.strip() for t in tag_elements if t.text.strip() != '+']
                game_data['Tags'] = ", ".join(tags)

            # 6. Release Date
            release_div = game_soup.find('div', class_='release_date')
            if release_div:
                date_tag = release_div.find('div', class_='date')
                if date_tag:
                    game_data['Release Date'] = date_tag.text.strip()

            # 7. Publisher
            dev_rows = game_soup.find_all('div', class_='dev_row')
            for dev_row in dev_rows:
                subtitle = dev_row.find('div', class_='subtitle')
                if subtitle and 'Publisher:' in subtitle.text:
                    pubs = dev_row.find_all('a')
                    game_data['Publisher'] = ", ".join([p.text.strip() for p in pubs])

            all_games_data.append(game_data)

            # STEAM RATE LIMITING: You must sleep between requests to avoid being IP blocked.
            time.sleep(1.5)

    return all_games_data


if __name__ == "__main__":
    # Change this number to scrape more pages from the search results
    pages_to_scrape = 10
    data = scrape_steam_store(pages_to_scrape)

    # Export the collected data to a CSV file
    if data:
        keys = data[0].keys()
        with open('steam_games.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        print("\nScraping complete! Data saved to steam_games.csv")
    else:
        print("\nNo data was found.")