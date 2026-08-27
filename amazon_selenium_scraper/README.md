# Amazon Product Scraper — Selenium

A portfolio-ready Selenium automation project for practicing structured product-card extraction from an authorized Amazon listing/search page.

## Features

- Selenium + Chrome WebDriver
- Headless browser support
- Product name extraction
- Price extraction
- Rating and review extraction
- Product URL extraction
- Multi-page support
- CSV export
- Explicit waits instead of relying only on fixed sleeps
- Defensive selectors so one missing field does not stop the whole run

## Setup

```bash
pip install selenium
```

## Run

```bash
python amazon_product_scraper.py "YOUR_AUTHORIZED_AMAZON_LISTING_URL" --pages 2 --output data/amazon_products.csv
```

To watch the browser:

```bash
python amazon_product_scraper.py "YOUR_AUTHORIZED_AMAZON_LISTING_URL" --show-browser
```

## Output

The scraper creates a CSV containing:

`name, price, rating, reviews, url`

## Notes

Amazon's HTML and anti-automation controls can change. Selectors may therefore need maintenance. Use automation only in accordance with the target site's terms, robots rules, applicable law, and any permission you have to access the content. This repository is intended as a Selenium learning/portfolio project, not a high-volume scraping service.
