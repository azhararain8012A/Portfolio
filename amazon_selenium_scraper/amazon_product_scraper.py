"""Amazon product scraping practice with Selenium.

Use only where you have permission to automate/access content. The default
example targets a user-supplied URL and extracts common product-card fields.
Selectors may need adjustment when the target site's HTML changes.
"""

import argparse
import csv
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def build_driver(headless: bool = True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    return webdriver.Chrome(options=options)


def first_text(element, selectors):
    for selector in selectors:
        try:
            value = element.find_element(By.CSS_SELECTOR, selector).text.strip()
            if value:
                return value
        except Exception:
            pass
    return ""


def scrape_products(url, pages=1, delay=2, output="amazon_products.csv", headless=True):
    driver = build_driver(headless)
    rows = []
    try:
        for page in range(1, pages + 1):
            page_url = url if page == 1 else f"{url}&page={page}"
            driver.get(page_url)
            WebDriverWait(driver, 15).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            )
            cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            for card in cards:
                name = first_text(card, ["h2 a span", "h2 span"])
                price = first_text(card, ["span.a-price span.a-offscreen", "span.a-price-whole"])
                rating = first_text(card, ["span.a-icon-alt"])
                reviews = first_text(card, ["span.a-size-base.s-underline-text", "span[aria-label*='ratings']"])
                link = ""
                try:
                    link = card.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href") or ""
                except Exception:
                    pass
                if name:
                    rows.append({"name": name, "price": price, "rating": rating, "reviews": reviews, "url": link})
            time.sleep(delay)
    finally:
        driver.quit()

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "rating", "reviews", "url"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} products to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selenium product-card extraction practice")
    parser.add_argument("url", help="Product listing/search URL you are authorized to access")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--delay", type=float, default=2)
    parser.add_argument("--output", default="amazon_products.csv")
    parser.add_argument("--show-browser", action="store_true")
    args = parser.parse_args()
    scrape_products(args.url, args.pages, args.delay, args.output, not args.show_browser)
