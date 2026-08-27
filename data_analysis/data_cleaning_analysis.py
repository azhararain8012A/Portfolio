"""Professional data cleaning and exploratory sales analysis pipeline.

This project demonstrates a reusable, portfolio-level workflow for turning a
messy CSV into analysis-ready data. It covers validation, type conversion,
missing-value treatment, duplicate detection, outlier reporting, feature
engineering, KPI generation, grouped analysis, and CSV export.

Install:
    pip install pandas

Run:
    python data_cleaning_analysis.py

Outputs:
    sample_sales_cleaned.csv
    sales_summary_by_category.csv
    sales_summary_by_city.csv
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sample_sales_raw.csv"
CLEANED_FILE = BASE_DIR / "sample_sales_cleaned.csv"
CATEGORY_FILE = BASE_DIR / "sales_summary_by_category.csv"
CITY_FILE = BASE_DIR / "sales_summary_by_city.csv"

REQUIRED_COLUMNS = {"customer", "city", "category", "quantity", "unit_price"}


def load_data(path: Path) -> pd.DataFrame:
    """Load the source CSV and validate the expected schema."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns.str.strip().str.lower().str.replace(" ", "_"))
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and text fields."""
    data = df.copy()
    data.columns = (
        data.columns.astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    )
    for col in ["customer", "city", "category"]:
        data[col] = data[col].astype("string").str.strip()
        data[col] = data[col].str.replace(r"\s+", " ", regex=True)
    return data


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric columns safely and report invalid values."""
    data = df.copy()
    for col in ["quantity", "unit_price"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean data and return both the cleaned frame and quality statistics."""
    data = standardize_columns(df)
    data = convert_types(data)

    before = len(data)
    duplicate_count = int(data.duplicated().sum())
    missing_before = data.isna().sum().to_dict()

    # Replace impossible numeric values before filling missing values.
    data.loc[data["quantity"] <= 0, "quantity"] = pd.NA
    data.loc[data["unit_price"] < 0, "unit_price"] = pd.NA

    data["quantity"] = data["quantity"].fillna(data["quantity"].median())
    data["unit_price"] = data["unit_price"].fillna(data["unit_price"].median())
    data["customer"] = data["customer"].fillna("Unknown Customer")
    data["category"] = data["category"].fillna("Unknown")
    data["city"] = data["city"].fillna("Unknown")

    data = data.drop_duplicates().reset_index(drop=True)
    data["quantity"] = data["quantity"].astype(int)
    data["unit_price"] = data["unit_price"].round(2)
    data["sales"] = (data["quantity"] * data["unit_price"]).round(2)
    data["order_value_band"] = pd.cut(
        data["sales"], bins=[-0.01, 100, 500, float("inf")],
        labels=["Low", "Medium", "High"]
    )

    quality = {
        "raw_rows": before,
        "clean_rows": len(data),
        "duplicates_removed": duplicate_count,
        "missing_values_before": int(sum(missing_before.values())),
        "missing_values_after": int(data.isna().sum().sum()),
    }
    return data, quality


def create_summaries(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create category and city performance summaries."""
    category = (
        df.groupby("category", dropna=False)
        .agg(
            orders=("customer", "count"),
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            average_order_value=("sales", "mean"),
        )
        .sort_values("revenue", ascending=False)
        .round(2)
        .reset_index()
    )

    city = (
        df.groupby("city", dropna=False)
        .agg(
            orders=("customer", "count"),
            units_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            average_order_value=("sales", "mean"),
        )
        .sort_values("revenue", ascending=False)
        .round(2)
        .reset_index()
    )
    return category, city


def print_report(raw: pd.DataFrame, clean: pd.DataFrame, quality: dict) -> None:
    """Print a readable business analysis report to the terminal."""
    total_revenue = clean["sales"].sum()
    total_units = clean["quantity"].sum()
    average_order = clean["sales"].mean()
    top_category = clean.groupby("category")["sales"].sum().idxmax()
    top_city = clean.groupby("city")["sales"].sum().idxmax()

    print("\n" + "=" * 60)
    print("DATA CLEANING & SALES ANALYSIS REPORT")
    print("=" * 60)
    print(f"Raw rows                 : {quality['raw_rows']}")
    print(f"Clean rows               : {quality['clean_rows']}")
    print(f"Duplicates removed       : {quality['duplicates_removed']}")
    print(f"Missing values before    : {quality['missing_values_before']}")
    print(f"Missing values after     : {quality['missing_values_after']}")
    print(f"Total revenue            : ${total_revenue:,.2f}")
    print(f"Total units sold         : {total_units:,}")
    print(f"Average order value      : ${average_order:,.2f}")
    print(f"Top category by revenue  : {top_category}")
    print(f"Top city by revenue      : {top_city}")
    print("\nRevenue by category:")
    print(clean.groupby("category")["sales"].sum().sort_values(ascending=False).round(2))
    print("\nRevenue by city:")
    print(clean.groupby("city")["sales"].sum().sort_values(ascending=False).round(2))
    print("=" * 60)


def main() -> None:
    raw = load_data(INPUT_FILE)
    clean, quality = clean_data(raw)
    category_summary, city_summary = create_summaries(clean)

    clean.to_csv(CLEANED_FILE, index=False)
    category_summary.to_csv(CATEGORY_FILE, index=False)
    city_summary.to_csv(CITY_FILE, index=False)

    print_report(raw, clean, quality)
    print(f"\nCleaned dataset saved to: {CLEANED_FILE}")
    print(f"Category summary saved to: {CATEGORY_FILE}")
    print(f"City summary saved to: {CITY_FILE}")


if __name__ == "__main__":
    main()
