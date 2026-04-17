"""
main.py
-------
Entry point for the Expense Tracker App.
Run this file to execute the complete pipeline:
  1. Generate synthetic dataset
  2. Clean & preprocess data
  3. Analyse spending patterns
  4. Generate all visualizations
  5. Produce summary reports

Usage:
    python main.py
"""

import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_generator  import generate_expenses
from src.data_cleaner    import clean_data
from src.analysis        import generate_insights
from src.visualizations  import generate_all_charts
from src.report_generator import generate_report


def main():
    print("\n" + "=" * 60)
    print("   💰  EXPENSE TRACKER APP  |  Data Science Project")
    print("=" * 60)

    # ── Step 1: Generate Data ────────────────────────────────────────────────
    print("\n[1/5] 🔧  Generating synthetic expense dataset...")
    os.makedirs("data", exist_ok=True)
    df_raw = generate_expenses(year=2024, num_records=500)
    df_raw.to_csv("data/expenses.csv", index=False)
    print(f"      Dataset shape : {df_raw.shape}")
    print(f"      Date range    : {df_raw['Date'].min().date()} → {df_raw['Date'].max().date()}")
    print(f"      Total spend   : ₹{df_raw['Amount'].sum():,.2f}")

    # ── Step 2: Clean Data ───────────────────────────────────────────────────
    print("\n[2/5] 🧹  Cleaning and preprocessing data...")
    df_clean = clean_data(df_raw)
    df_clean.to_csv("data/expenses_clean.csv", index=False)

    # ── Step 3: Insights ─────────────────────────────────────────────────────
    print("\n[3/5] 💡  Generating insights...")
    insights = generate_insights(df_clean)
    for insight in insights:
        print(f"      {insight}")

    # ── Step 4: Visualizations ───────────────────────────────────────────────
    print("\n[4/5] 📊  Generating visualizations...")
    generate_all_charts(df_clean)

    # ── Step 5: Report ───────────────────────────────────────────────────────
    print("\n[5/5] 📝  Generating reports...")
    generate_report(df_clean)

    # ── Done ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("   ✅  PIPELINE COMPLETE!")
    print("=" * 60)
    print("\n📁 Output files:")
    print("   data/expenses.csv          → Raw synthetic dataset")
    print("   data/expenses_clean.csv    → Cleaned dataset")
    print("   outputs/01_category_pie.png")
    print("   outputs/02_category_bar.png")
    print("   outputs/03_monthly_trend.png")
    print("   outputs/04_quarterly.png")
    print("   outputs/05_payment_methods.png")
    print("   outputs/06_weekday_spending.png")
    print("   outputs/07_budget_vs_actual.png")
    print("   outputs/08_heatmap.png")
    print("   outputs/09_top_subcategories.png")
    print("   outputs/10_dashboard.png")
    print("   outputs/expense_report.txt")
    print("   outputs/category_summary.csv")
    print("   outputs/monthly_summary.csv")
    print("   outputs/budget_analysis.csv")
    print("\n🚀  Open the outputs/ folder to view all charts and reports.")
    print("    Push to GitHub to showcase your project!\n")


if __name__ == "__main__":
    main()
