"""
analysis.py
-----------
Core analytical functions for the Expense Tracker App.
Covers category analysis, monthly trends, spending patterns,
budget analysis, and insight generation.
"""

import pandas as pd
import numpy as np


# ── Category Analysis ─────────────────────────────────────────────────────────

def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Total spend, transaction count, average per category."""
    summary = (
        df.groupby("Category", observed=True)["Amount"]
        .agg(Total="sum", Count="count", Average="mean", Max="max")
        .round(2)
        .sort_values("Total", ascending=False)
        .reset_index()
    )
    summary["% of Total"] = (summary["Total"] / summary["Total"].sum() * 100).round(1)
    return summary


def top_subcategories(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N subcategories by total spend."""
    return (
        df.groupby(["Category", "Subcategory"], observed=True)["Amount"]
        .sum().round(2)
        .reset_index()
        .sort_values("Amount", ascending=False)
        .head(n)
    )


# ── Monthly Trends ────────────────────────────────────────────────────────────

def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly total and transaction count."""
    monthly = (
        df.groupby(["Month_Num", "Month"])["Amount"]
        .agg(Total="sum", Count="count")
        .round(2)
        .reset_index()
        .sort_values("Month_Num")
    )
    monthly["MoM_Change_%"] = monthly["Total"].pct_change().mul(100).round(1)
    return monthly


def quarterly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Quarterly aggregation."""
    return (
        df.groupby("Quarter")["Amount"]
        .agg(Total="sum", Count="count", Average="mean")
        .round(2)
        .reset_index()
        .sort_values("Quarter")
    )


def category_monthly_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot: rows = month, columns = category."""
    pivot = df.pivot_table(
        index="Month_Num",
        columns="Category",
        values="Amount",
        aggfunc="sum",
        observed=True
    ).fillna(0).round(2)
    pivot.index = df.sort_values("Month_Num")["Month"].unique()[:len(pivot)]
    return pivot


# ── Spending Pattern Analysis ─────────────────────────────────────────────────

def weekday_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Average spend per day of the week."""
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    agg = (
        df.groupby("Day_of_Week")["Amount"]
        .agg(Total="sum", Average="mean", Count="count")
        .round(2)
        .reindex(order)
        .reset_index()
    )
    return agg


def payment_method_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Spend distribution by payment method."""
    pm = (
        df.groupby("Payment_Method")["Amount"]
        .agg(Total="sum", Count="count", Average="mean")
        .round(2)
        .sort_values("Total", ascending=False)
        .reset_index()
    )
    pm["% of Total"] = (pm["Total"] / pm["Total"].sum() * 100).round(1)
    return pm


def weekend_vs_weekday(df: pd.DataFrame) -> pd.DataFrame:
    """Compare weekend vs weekday spending."""
    return (
        df.groupby("Is_Weekend")["Amount"]
        .agg(Total="sum", Average="mean", Count="count")
        .round(2)
        .rename(index={True: "Weekend", False: "Weekday"})
        .reset_index()
        .rename(columns={"Is_Weekend": "Type"})
    )


# ── Budget & Overspending ─────────────────────────────────────────────────────

MONTHLY_BUDGET = {
    "Food & Dining":    5000,
    "Rent":             12000,
    "Transportation":   2500,
    "Entertainment":    1500,
    "Shopping":         3000,
    "Healthcare":       1000,
    "Education":        2500,
    "Utilities":        2000,
    "Travel":           5000,
    "Miscellaneous":    1000,
}


def budget_vs_actual(df: pd.DataFrame) -> pd.DataFrame:
    """Compare actual monthly average to budget per category."""
    actual = df.groupby("Category", observed=True)["Amount"].sum() / 12  # avg monthly
    budget = pd.Series(MONTHLY_BUDGET)
    result = pd.DataFrame({
        "Budget":        budget,
        "Actual_Avg":    actual.round(2),
    }).dropna()
    result["Variance"]   = (result["Actual_Avg"] - result["Budget"]).round(2)
    result["Status"]     = result["Variance"].apply(
        lambda x: "⚠️ Over Budget" if x > 0 else "✅ Under Budget"
    )
    result["Variance_%"] = (result["Variance"] / result["Budget"] * 100).round(1)
    return result.reset_index().rename(columns={"index": "Category"})


def overspend_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Return all transactions flagged as overspending."""
    return df[df["Overspend_Flag"] == True][
        ["Date", "Category", "Subcategory", "Amount", "Payment_Method"]
    ].sort_values("Amount", ascending=False)


# ── Key Insights ──────────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[str]:
    """Auto-generate bullet-point insights from the data."""
    insights = []

    total        = df["Amount"].sum()
    avg_monthly  = total / 12
    top_cat      = df.groupby("Category", observed=True)["Amount"].sum().idxmax()
    top_cat_pct  = df.groupby("Category", observed=True)["Amount"].sum().max() / total * 100
    peak_month   = df.groupby("Month_Num")["Amount"].sum().idxmax()
    peak_month_name = df[df["Month_Num"] == peak_month]["Month"].values[0]
    top_pm       = df.groupby("Payment_Method")["Amount"].sum().idxmax()
    overspend_n  = df["Overspend_Flag"].sum()
    weekend_avg  = df[df["Is_Weekend"]]["Amount"].mean()
    weekday_avg  = df[~df["Is_Weekend"]]["Amount"].mean()

    insights.append(f"💰 Total annual spend: ₹{total:,.0f} | Monthly average: ₹{avg_monthly:,.0f}")
    insights.append(f"🏆 Highest spending category: {top_cat} ({top_cat_pct:.1f}% of total spend)")
    insights.append(f"📅 Peak spending month: {peak_month_name}")
    insights.append(f"💳 Most used payment method: {top_pm}")
    insights.append(f"⚠️  {overspend_n} transactions flagged as potential overspending")
    insights.append(
        f"🗓️  Weekend avg spend ₹{weekend_avg:.0f} vs Weekday avg ₹{weekday_avg:.0f} "
        f"({'higher' if weekend_avg > weekday_avg else 'lower'} on weekends)"
    )

    bva = budget_vs_actual(df)
    over = bva[bva["Variance"] > 0]["Category"].tolist()
    if over:
        insights.append(f"🚨 Categories over monthly budget: {', '.join(over)}")
    else:
        insights.append("✅ All categories are within monthly budget!")

    return insights


if __name__ == "__main__":
    df = pd.read_csv("data/expenses_clean.csv", parse_dates=["Date"])

    print("\n📊 CATEGORY SUMMARY")
    print(category_summary(df).to_string(index=False))

    print("\n📅 MONTHLY TREND")
    print(monthly_trend(df).to_string(index=False))

    print("\n💳 PAYMENT METHOD")
    print(payment_method_analysis(df).to_string(index=False))

    print("\n💡 KEY INSIGHTS")
    for i in generate_insights(df):
        print(" ", i)
