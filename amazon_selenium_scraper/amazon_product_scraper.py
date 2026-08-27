"""Professional Amazon-style product listing scraper using Selenium.

This is a portfolio/learning project for authorized listing or search pages.
It demonstrates configurable browser automation, explicit waits, pagination,
robust selectors, normalization, duplicate removal, extraction metrics, and
CSV export. E-commerce HTML changes frequently, so selectors are intentionally
kept in small helper functions for easier maintenance.

Install:
    pip install selenium

Run against a page you are authorized to automate:
    python amazon_product_scraper.py "YOUR_AUTHORIZED_LISTING_URL" --pages 3

Show the browser:
    python amazon_product_scraper.py "YOUR_AUTHORIZED_LISTING_URL" --show-browser
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WAIT_SECONDS = 20
DEFAULT_DELAY = 2.0
PRODUCT_CARD = "div[data-component-type='s-search-result']"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Normalized product record produced by the scraper."""
    name: str
    price: str
    rating: str
    reviews: str
    url: str
    page: int


def build_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a reusable Chrome WebDriver configuration."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def clean_text(value: str) -> str:
    """Collapse whitespace and remove surrounding spaces."""
    return re.sub(r"\s+", " ", value or "").strip()


def first_text(element: WebElement, selectors: Iterable[str]) -> str:
    """Return the first non-empty text found using a list of selectors."""
    for selector in selectors:
        try:
            value = clean_text(element.find_element(By.CSS_SELECTOR, selector).text)
            if value:
                return value
        except Exception:
            continue
    return ""


def first_attribute(element: WebElement, selectors: Iterable[str], attribute: str) -> str:
    """Return the first non-empty element attribute."""
    for selector in selectors:
        try:
            value = element.find_element(By.CSS_SELECTOR, selector).get_attribute(attribute)
            if value:
                return clean_text(value)
        except Exception:
            continue
    return ""


def wait_for_product_cards(driver: webdriver.Chrome) -> List[WebElement]:
    """Wait for search-result cards and return them."""
    try:
        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, PRODUCT_CARD))
        )
    except TimeoutException as exc:
        raise TimeoutException("Product cards did not load before the timeout") from exc
    return driver.find_elements(By.CSS_SELECTOR, PRODUCT_CARD)


def extract_product(card: WebElement, page_number: int) -> Product | None:
    """Extract one product card while tolerating missing optional fields."""
    name = first_text(card, ["h2 a span", "h2 span", "h2"])
    if not name:
        return None

    price = first_text(card, [
        "span.a-price span.a-offscreen",
        "span.a-price-whole",
        ".a-price",
    ])
    rating = first_text(card, ["span.a-icon-alt", "i.a-icon-star-small span.a-icon-alt"])
    reviews = first_text(card, [
        "span.a-size-base.s-underline-text",
        "span[aria-label*='ratings']",
        "a[aria-label*='ratings']",
    ])
    url = first_attribute(card, ["h2 a", "a.a-link-normal"], "href")

    return Product(
        name=name,
        price=price,
        rating=rating,
        reviews=reviews,
        url=url,
        page=page_number,
    )


def build_page_url(base_url: str, page_number: int) -> str:
    """Add a page parameter while preserving an existing query string."""
    if page_number == 1:
        return base_url
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}page={page_number}"


def scrape_products(
    url: str,
    pages: int = 1,
    delay: float = DEFAULT_DELAY,
    headless: bool = True,
) -> List[Product]:
    """Scrape product cards from multiple listing pages."""
    if pages < 1:
        raise ValueError("pages must be at least 1")
    if delay < 0:
        raise ValueError("delay cannot be negative")

    driver = build_driver(headless)
    products: List[Product] = []
    try:
        for page in range(1, pages + 1):
            page_url = build_page_url(url, page)
            logger.info("Opening page %s/%s", page, pages)
            driver.get(page_url)
            try:
                cards = wait_for_product_cards(driver)
            except TimeoutException:
                logger.warning("No product cards found on page %s", page)
                break

            page_count = 0
            for card in cards:
                product = extract_product(card, page)
                if product:
                    products.append(product)
                    page_count += 1
            logger.info("Extracted %s products from page %s", page_count, page)
            time.sleep(delay)
    finally:
        driver.quit()
        logger.info("Browser closed")

    # Deduplicate by URL when available, otherwise by product name.
    unique = {}
    for product in products:
        key = product.url or product.name.lower()
        unique[key] = product
    return list(unique.values())


def save_csv(products: List[Product], output: Path) -> None:
    """Save normalized product records as UTF-8 CSV."""
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "price", "rating", "reviews", "url", "page"]
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for product in products:
            writer.writerow(asdict(product))


def print_report(products: List[Product], output: Path) -> None:
    """Print extraction quality and coverage metrics."""
    with_price = sum(bool(p.price) for p in products)
    with_rating = sum(bool(p.rating) for p in products)
    with_reviews = sum(bool(p.reviews) for p in products)
    with_url = sum(bool(p.url) for p in products)
    pages = sorted({p.page for p in products})

    print("\n" + "=" * 60)
    print("AMAZON PRODUCT SCRAPER — SELENIUM REPORT")
    print("=" * 60)
    print(f"Products extracted : {len(products)}")
    print(f"Pages represented  : {pages or 'None'}")
    print(f"Products with price : {with_price}")
    print(f"Products with rating: {with_rating}")
    print(f"Products with reviews: {with_reviews}")
    print(f"Products with URL   : {with_url}")
    print(f"CSV output          : {output}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Professional Selenium product-card extraction practice"
    )
    parser.add_argument("url", help="Listing/search URL you are authorized to access")
    parser.add_argument("--pages", type=int, default=1, help="Number of listing pages")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay between pages")
    parser.add_argument("--output", default="amazon_products.csv", help="CSV output path")
    parser.add_argument("--show-browser", action="store_true", help="Run Chrome visibly")
    args = parser.parse_args()

    output = Path(args.output)
    products = scrape_products(
        args.url,
        pages=args.pages,
        delay=args.delay,
        headless=not args.show_browser,
    )
    save_csv(products, output)
    print_report(products, output)
    logger.info("Scraping workflow completed successfully")


if __name__ == "__main__":
    main()
