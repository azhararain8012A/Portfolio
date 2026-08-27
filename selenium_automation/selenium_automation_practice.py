"""Selenium automation practice using the public Quotes demo site.

Install:
    pip install selenium

Run:
    python selenium_automation_practice.py

The script uses headless Chrome, visits pages 1–3, extracts structured quote
metadata, and saves the result to quotes_output.csv.
"""
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

URL = "https://quotes.toscrape.com/"
OUTPUT = "quotes_output.csv"


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")

    driver = webdriver.Chrome(options=options)
    rows = []
    try:
        for page in range(1, 4):
            driver.get(URL if page == 1 else f"{URL}page/{page}/")
            for quote in driver.find_elements(By.CSS_SELECTOR, "div.quote"):
                rows.append({
                    "quote": quote.find_element(By.CSS_SELECTOR, "span.text").text,
                    "author": quote.find_element(By.CSS_SELECTOR, "small.author").text,
                    "tags": ", ".join(
                        tag.text for tag in quote.find_elements(By.CSS_SELECTOR, "a.tag")
                    ),
                })
    finally:
        driver.quit()

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["quote", "author", "tags"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Extracted {len(rows)} quotes")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
