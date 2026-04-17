"""
data_cleaner.py
---------------
Cleans and preprocesses the raw expense dataset.
Handles missing values, outliers, type casting, and feature engineering.
"""

import pandas as pd
import numpy as np


def load_data(filepath: str = "data/expenses.csv") -> pd.DataFrame:
    """Load raw expense CSV into a DataFrame."""
    df = pd.read_csv(filepath, parse_dates=["Date"])
    print(f"📂  Loaded {len(df)} records from '{filepath}'")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
    1. Drop exact duplicates
    2. Handle missing values
    3. Fix data types
    4. Remove outliers (IQR method per category)
    5. Add derived columns
    """
    original_shape = df.shape

    # ── 1. Drop duplicates ────────────────────────────────────────────────────
    df = df.drop_duplicates()

    # ── 2. Handle missing values ──────────────────────────────────────────────
    df["Amount"]         = df["Amount"].fillna(df["Amount"].median())
    df["Category"]       = df["Category"].fillna("Miscellaneous")
    df["Payment_Method"] = df["Payment_Method"].fillna("Unknown")
    df["Notes"]          = df["Notes"].fillna("")

    # ── 3. Data types ─────────────────────────────────────────────────────────
    df["Amount"]     = pd.to_numeric(df["Amount"], errors="coerce").round(2)
    df["Date"]       = pd.to_datetime(df["Date"], errors="coerce")
    df["Category"]   = df["Category"].astype("category")
    df["Month_Num"]  = df["Date"].dt.month
    df["Month"]      = df["Date"].dt.strftime("%B")
    df["Day_of_Week"]= df["Date"].dt.strftime("%A")
    df["Quarter"]    = "Q" + df["Date"].dt.quarter.astype(str)

    # Drop rows where Amount or Date is null after coercion
    df = df.dropna(subset=["Amount", "Date"])

    # ── 4. Outlier removal (per category, IQR × 3) ───────────────────────────
    clean_frames = []
    for cat, group in df.groupby("Category", observed=True):
        Q1  = group["Amount"].quantile(0.25)
        Q3  = group["Amount"].quantile(0.75)
        IQR = Q3 - Q1
        filtered = group[group["Amount"] <= Q3 + 3 * IQR]
        clean_frames.append(filtered)
    df = pd.concat(clean_frames).sort_values("Date").reset_index(drop=True)

    # ── 5. Derived feature columns ────────────────────────────────────────────
    df["Week_Number"]  = df["Date"].dt.isocalendar().week.astype(int)
    df["Is_Weekend"]   = df["Day_of_Week"].isin(["Saturday", "Sunday"])
    df["Amount_INR"]   = df["Amount"].apply(lambda x: f"₹{x:,.2f}")

    print(f"🧹  Cleaning complete: {original_shape} → {df.shape}")
    print(f"    Nulls remaining : {df.isnull().sum().sum()}")
    return df


def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    return df[["Amount"]].describe().round(2)


if __name__ == "__main__":
    df_raw   = load_data()
    df_clean = clean_data(df_raw)
    df_clean.to_csv("data/expenses_clean.csv", index=False)
    print("\n📊  Summary Statistics:")
    print(get_summary_stats(df_clean))
    print(f"\n✅  Clean data saved → data/expenses_clean.csv")
