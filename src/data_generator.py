"""
data_generator.py
-----------------
Generates synthetic expense data for the Expense Tracker App.
Simulates 1 year of realistic personal finance data across multiple categories.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ── Configuration ────────────────────────────────────────────────────────────
CATEGORIES = {
    "Food & Dining":    {"base": 4500,  "std": 800,  "freq": 30},
    "Rent":             {"base": 12000, "std": 0,    "freq": 1},
    "Transportation":   {"base": 2000,  "std": 500,  "freq": 15},
    "Entertainment":    {"base": 1500,  "std": 600,  "freq": 8},
    "Shopping":         {"base": 3000,  "std": 1200, "freq": 10},
    "Healthcare":       {"base": 800,   "std": 400,  "freq": 2},
    "Education":        {"base": 2500,  "std": 300,  "freq": 2},
    "Utilities":        {"base": 1800,  "std": 200,  "freq": 3},
    "Travel":           {"base": 5000,  "std": 2000, "freq": 1},
    "Miscellaneous":    {"base": 1000,  "std": 500,  "freq": 5},
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]

SUBCATEGORIES = {
    "Food & Dining":    ["Groceries", "Restaurant", "Swiggy/Zomato", "Cafe", "Snacks"],
    "Rent":             ["Monthly Rent"],
    "Transportation":   ["Uber/Ola", "Fuel", "Auto", "Bus/Metro", "Train Ticket"],
    "Entertainment":    ["OTT Subscription", "Movies", "Gaming", "Events", "Books"],
    "Shopping":         ["Clothing", "Electronics", "Home Decor", "Footwear", "Accessories"],
    "Healthcare":       ["Medicine", "Doctor Visit", "Lab Tests", "Gym", "Supplements"],
    "Education":        ["Course Fee", "Books", "Certification", "Stationery", "Coaching"],
    "Utilities":        ["Electricity", "Internet", "Mobile Recharge", "Water", "Gas"],
    "Travel":           ["Flight", "Hotel", "Tour Package", "Local Travel", "Sightseeing"],
    "Miscellaneous":    ["Gift", "Charity", "Repairs", "Personal Care", "Other"],
}

# Monthly seasonal multipliers (higher spend in festive months)
SEASONAL_MULTIPLIERS = {
    1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95, 5: 1.00,
    6: 0.95, 7: 0.90, 8: 0.95, 9: 1.00, 10: 1.15,
    11: 1.20, 12: 1.30
}


def generate_expenses(year: int = 2024, num_records: int = 500) -> pd.DataFrame:
    """Generate a realistic synthetic expense dataset."""
    records = []
    start_date = datetime(year, 1, 1)
    end_date   = datetime(year, 12, 31)
    date_range = (end_date - start_date).days

    for _ in range(num_records):
        # Random date within the year
        offset   = random.randint(0, date_range)
        exp_date = start_date + timedelta(days=offset)
        month    = exp_date.month

        # Pick category
        category = random.choice(list(CATEGORIES.keys()))
        cfg      = CATEGORIES[category]

        # Generate amount with seasonal effect
        seasonal  = SEASONAL_MULTIPLIERS[month]
        base_amt  = cfg["base"] / cfg["freq"]
        amount    = max(10, np.random.normal(base_amt * seasonal, cfg["std"] / cfg["freq"]))
        amount    = round(amount, 2)

        subcategory    = random.choice(SUBCATEGORIES[category])
        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=[35, 30, 20, 10, 5]
        )[0]

        # Flag potential overspending (top 10% of category spend)
        overspend_flag = amount > (base_amt * seasonal * 1.8)

        records.append({
            "Date":            exp_date.strftime("%Y-%m-%d"),
            "Category":        category,
            "Subcategory":     subcategory,
            "Amount":          amount,
            "Payment_Method":  payment_method,
            "Month":           exp_date.strftime("%B"),
            "Month_Num":       month,
            "Day_of_Week":     exp_date.strftime("%A"),
            "Quarter":         f"Q{(month - 1) // 3 + 1}",
            "Overspend_Flag":  overspend_flag,
            "Notes":           f"{subcategory} expense"
        })

    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_expenses()
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/expenses.csv", index=False)
    print(f"✅  Dataset saved → data/expenses.csv")
    print(f"    Shape   : {df.shape}")
    print(f"    Date range: {df['Date'].min().date()} → {df['Date'].max().date()}")
    print(f"    Total spend: ₹{df['Amount'].sum():,.2f}")
    print(df.head())
