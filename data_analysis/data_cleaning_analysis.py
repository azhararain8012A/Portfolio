"""Portfolio-ready data cleaning and analysis example.

Run:
    pip install pandas
    python data_cleaning_analysis.py

The script loads the included intentionally messy CSV, cleans common data-quality
issues, prints an analysis summary, and exports a cleaned CSV.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sample_sales_raw.csv"
OUTPUT_FILE = BASE_DIR / "sample_sales_cleaned.csv"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)

    for col in ["customer", "city", "category"]:
        data[col] = data[col].astype("string").str.strip()

    for col in ["quantity", "unit_price"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["quantity"] = data["quantity"].fillna(data["quantity"].median())
    data["unit_price"] = data["unit_price"].fillna(data["unit_price"].median())
    data["category"] = data["category"].fillna("Unknown")
    data["city"] = data["city"].fillna("Unknown")

    data = data[(data["quantity"] > 0) & (data["unit_price"] >= 0)]
    data = data.drop_duplicates().reset_index(drop=True)
    data["sales"] = (data["quantity"] * data["unit_price"]).round(2)
    return data


def main() -> None:
    raw = pd.read_csv(INPUT_FILE)
    clean = clean_data(raw)
    clean.to_csv(OUTPUT_FILE, index=False)

    print("=== Data Cleaning & Analysis Report ===")
    print(f"Raw rows: {len(raw)}")
    print(f"Clean rows: {len(clean)}")
    print(f"Total sales: ${clean['sales'].sum():,.2f}")
    print("\nSales by category:")
    print(clean.groupby("category")["sales"].sum().sort_values(ascending=False).round(2))
    print(f"\nCleaned file saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
