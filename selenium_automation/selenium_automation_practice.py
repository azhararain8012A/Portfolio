"""Professional Selenium automation practice project.

The script automates the public Quotes to Scrape demo site and demonstrates a
production-style Selenium workflow: configurable browser options, explicit
waits, pagination, structured extraction, validation, duplicate protection,
logging, retry handling, and CSV export.

Install:
    pip install selenium

Run:
    python selenium_automation_practice.py

Output:
    quotes_output.csv
"""
from __future__ import annotations

import csv
import logging
import time
from pathlib import Path
from typing import Dict, List

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://quotes.toscrape.com/"
OUTPUT_FILE = Path(__file__).resolve().parent / "quotes_output.csv"
MAX_PAGES = 5
WAIT_SECONDS = 15

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def build_driver() -> webdriver.Chrome:
    """Create a configured Chrome driver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def wait_for_quotes(driver: webdriver.Chrome) -> None:
    """Wait until quote cards are available on the current page."""
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.quote"))
    )


def extract_quote(card) -> Dict[str, str]:
    """Extract and normalize one quote card."""
    quote_text = card.find_element(By.CSS_SELECTOR, "span.text").text.strip()
    author = card.find_element(By.CSS_SELECTOR, "small.author").text.strip()
    tags = ", ".join(
        tag.text.strip()
        for tag in card.find_elements(By.CSS_SELECTOR, "a.tag")
        if tag.text.strip()
    )
    author_url = ""
    try:
        author_url = card.find_element(By.CSS_SELECTOR, "small.author + a").get_attribute("href") or ""
    except Exception:
        pass

    return {
        "quote": quote_text,
        "author": author,
        "tags": tags,
        "author_url": author_url,
    }


def scrape_page(driver: webdriver.Chrome, page_number: int) -> List[Dict[str, str]]:
    """Open a page and safely extract all quote records."""
    url = BASE_URL if page_number == 1 else f"{BASE_URL}page/{page_number}/"
    logger.info("Opening page %s: %s", page_number, url)
    driver.get(url)

    try:
        wait_for_quotes(driver)
    except TimeoutException:
        logger.warning("No quote cards found on page %s", page_number)
        return []

    records: List[Dict[str, str]] = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.quote")

    for index, card in enumerate(cards, start=1):
        for attempt in range(2):
            try:
                record = extract_quote(card)
                if record["quote"] and record["author"]:
                    record["page"] = str(page_number)
                    record["position"] = str(index)
                    records.append(record)
                break
            except StaleElementReferenceException:
                if attempt == 0:
                    cards = driver.find_elements(By.CSS_SELECTOR, "div.quote")
                    card = cards[index - 1]
                else:
                    logger.warning("Skipped stale quote card %s on page %s", index, page_number)

    logger.info("Extracted %s records from page %s", len(records), page_number)
    return records


def scrape_quotes(max_pages: int = MAX_PAGES) -> List[Dict[str, str]]:
    """Scrape several pages and remove duplicate quote records."""
    driver = build_driver()
    all_records: List[Dict[str, str]] = []
    try:
        for page in range(1, max_pages + 1):
            records = scrape_page(driver, page)
            if not records:
                break
            all_records.extend(records)
            time.sleep(1)  # polite pacing for this practice site
    finally:
        driver.quit()
        logger.info("Browser closed")

    unique: Dict[str, Dict[str, str]] = {}
    for record in all_records:
        unique[record["quote"]] = record
    return list(unique.values())


def save_csv(records: List[Dict[str, str]], output: Path) -> None:
    """Write structured results to a UTF-8 CSV file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["quote", "author", "tags", "author_url", "page", "position"]
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def print_summary(records: List[Dict[str, str]]) -> None:
    """Display useful extraction statistics."""
    authors = sorted({row["author"] for row in records})
    tag_count = sum(len(row["tags"].split(", ")) for row in records if row["tags"])

    print("\n" + "=" * 55)
    print("SELENIUM AUTOMATION REPORT")
    print("=" * 55)
    print(f"Quotes extracted : {len(records)}")
    print(f"Unique authors   : {len(authors)}")
    print(f"Tags collected   : {tag_count}")
    print(f"Output file      : {OUTPUT_FILE}")
    print("=" * 55)


def main() -> None:
    records = scrape_quotes()
    save_csv(records, OUTPUT_FILE)
    print_summary(records)
    logger.info("Automation completed successfully")


if __name__ == "__main__":
    main()
