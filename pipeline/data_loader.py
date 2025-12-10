"""
Data loading and cleaning for DataCo Supply Chain dataset.

- Reads raw CSV from data/raw/DataCoSupplyChainDataset.csv
- Cleans and standardizes columns
- Writes cleaned parquet to data/processed/orders_clean.parquet
"""

import os
import sys
from pathlib import Path

# ----------------------------------------------------------
# 0. PATCH PYTHON PATH TO PROJECT ROOT
# ----------------------------------------------------------

# This file is in: <project_root>/pipeline/data_loader.py
CURRENT_DIR = Path(__file__).resolve().parent          # .../Final Project/pipeline
PROJECT_ROOT = CURRENT_DIR.parent                      # .../Final Project

# Ensure project root is on sys.path so `from config import ...` works
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from config import DATA_RAW_PATH, DATA_PROCESSED_PATH


def load_raw_data() -> pd.DataFrame:
    """Load the original DataCo CSV."""
    if not DATA_RAW_PATH.exists():
        raise FileNotFoundError(f"Raw data not found at {DATA_RAW_PATH}")
    df = pd.read_csv(DATA_RAW_PATH, encoding="latin-1")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map original column names to clean snake_case names
    based on the schema you pasted.
    """
    df = df.copy()
    rename_map = {
        "Type": "payment_type",
        "Days for shipping (real)": "days_for_shipping_real",
        "Days for shipment (scheduled)": "days_for_shipment_scheduled",
        "Benefit per order": "benefit_per_order",
        "Sales per customer": "sales_per_customer",
        "Delivery Status": "delivery_status",
        "Late_delivery_risk": "late_delivery_risk",
        "Category Id": "category_id",
        "Category Name": "category_name",
        "Customer City": "customer_city",
        "Customer Country": "customer_country",
        "Customer Email": "customer_email",
        "Customer Fname": "customer_fname",
        "Customer Id": "customer_id",
        "Customer Lname": "customer_lname",
        "Customer Password": "customer_password",
        "Customer Segment": "customer_segment",
        "Customer State": "customer_state",
        "Customer Street": "customer_street",
        "Customer Zipcode": "customer_zipcode",
        "Department Id": "department_id",
        "Department Name": "department_name",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Market": "market",
        "Order City": "order_city",
        "Order Country": "order_country",
        "Order Customer Id": "order_customer_id",
        "order date (DateOrders)": "order_date",
        "Order Id": "order_id",
        "Order Item Cardprod Id": "order_item_cardprod_id",
        "Order Item Discount": "order_item_discount",
        "Order Item Discount Rate": "order_item_discount_rate",
        "Order Item Id": "order_item_id",
        "Order Item Product Price": "order_item_product_price",
        "Order Item Profit Ratio": "order_item_profit_ratio",
        "Order Item Quantity": "order_item_quantity",
        "Sales": "sales",
        "Order Item Total": "order_item_total",
        "Order Profit Per Order": "order_profit_per_order",
        "Order Region": "order_region",
        "Order State": "order_state",
        "Order Status": "order_status",
        "Order Zipcode": "order_zipcode",
        "Product Card Id": "product_card_id",
        "Product Category Id": "product_category_id",
        "Product Description": "product_description",
        "Product Image": "product_image",
        "Product Name": "product_name",
        "Product Price": "product_price",
        "Product Status": "product_status",
        "shipping date (DateOrders)": "shipping_date",
        "Shipping Mode": "shipping_mode",
    }

    df = df.rename(columns=rename_map)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns, types, and derived features."""
    df = rename_columns(df)

    # Convert dates
    for col in ["order_date", "shipping_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Convert numeric columns
    numeric_cols = [
        "days_for_shipping_real",
        "days_for_shipment_scheduled",
        "benefit_per_order",
        "sales_per_customer",
        "late_delivery_risk",
        "order_item_discount",
        "order_item_discount_rate",
        "order_item_product_price",
        "order_item_profit_ratio",
        "order_item_quantity",
        "sales",
        "order_item_total",
        "order_profit_per_order",
        "latitude",
        "longitude",
        "product_price",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived columns: shipping_delay_days and on_time_delivery
    if "days_for_shipping_real" in df.columns and "days_for_shipment_scheduled" in df.columns:
        df["shipping_delay_days"] = (
            df["days_for_shipping_real"] - df["days_for_shipment_scheduled"]
        )

    if "shipping_delay_days" in df.columns:
        df["on_time_delivery"] = df["shipping_delay_days"] <= 0

    # Drop duplicates based on order_item_id (line-level)
    if "order_item_id" in df.columns:
        df = df.drop_duplicates(subset=["order_item_id"])

    # Drop rows missing key fields
    key_cols = [c for c in ["order_id", "order_date", "sales"] if c in df.columns]
    if key_cols:
        df = df.dropna(subset=key_cols)

    return df


def save_processed_data(df: pd.DataFrame):
    """Write cleaned data to parquet file."""
    DATA_PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DATA_PROCESSED_PATH, index=False)
    print(f"Saved cleaned data to {DATA_PROCESSED_PATH}")


if __name__ == "__main__":
    print("Project root detected as:", PROJECT_ROOT)
    print("Using raw data path:", DATA_RAW_PATH)

    df_raw = load_raw_data()
    print("Raw columns:", list(df_raw.columns))

    df_clean = clean_data(df_raw)
    print("Cleaned columns:", list(df_clean.columns))

    save_processed_data(df_clean)
