"""
visualizations.py
-----------------
Generates and saves all charts for the Expense Tracker App.
Each function saves a PNG to the outputs/ directory.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

from src.analysis import (
    category_summary, monthly_trend, weekday_analysis,
    payment_method_analysis, budget_vs_actual,
    quarterly_trend, category_monthly_pivot, weekend_vs_weekday
)

# ── Global Style ──────────────────────────────────────────────────────────────
PALETTE     = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B",
               "#44BBA4", "#E94F37", "#393E41", "#F5A623", "#7B2D8B"]
BG_COLOR    = "#F8F9FA"
GRID_COLOR  = "#E0E0E0"
TEXT_COLOR  = "#2C3E50"

plt.rcParams.update({
    "figure.facecolor":   BG_COLOR,
    "axes.facecolor":     BG_COLOR,
    "axes.edgecolor":     GRID_COLOR,
    "axes.labelcolor":    TEXT_COLOR,
    "axes.titlesize":     14,
    "axes.titleweight":   "bold",
    "axes.labelsize":     11,
    "xtick.color":        TEXT_COLOR,
    "ytick.color":        TEXT_COLOR,
    "font.family":        "DejaVu Sans",
    "axes.grid":          True,
    "grid.color":         GRID_COLOR,
    "grid.linestyle":     "--",
    "grid.alpha":         0.7,
    "legend.framealpha":  0.9,
})

os.makedirs("outputs", exist_ok=True)


def _save(fig, filename: str):
    path = f"outputs/{filename}"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"  ✅  Saved → {path}")
    return path


# ── 1. Category Pie Chart ─────────────────────────────────────────────────────

def plot_category_pie(df: pd.DataFrame):
    cat = category_summary(df)
    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(
        cat["Total"],
        labels=cat["Category"],
        autopct="%1.1f%%",
        colors=PALETTE[:len(cat)],
        startangle=140,
        pctdistance=0.82,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Category-Wise Spending Distribution", pad=20, color=TEXT_COLOR)
    centre = plt.Circle((0, 0), 0.60, color=BG_COLOR)
    ax.add_patch(centre)
    ax.text(0, 0, f"₹{cat['Total'].sum():,.0f}\nTotal Spend",
            ha="center", va="center", fontsize=11, color=TEXT_COLOR, fontweight="bold")
    return _save(fig, "01_category_pie.png")


# ── 2. Category Bar Chart ─────────────────────────────────────────────────────

def plot_category_bar(df: pd.DataFrame):
    cat = category_summary(df).sort_values("Total")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(cat["Category"], cat["Total"], color=PALETTE[:len(cat)],
                   edgecolor="white", height=0.65)
    for bar, val in zip(bars, cat["Total"]):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                f"₹{val:,.0f}", va="center", fontsize=9, color=TEXT_COLOR)
    ax.set_xlabel("Total Amount Spent (₹)")
    ax.set_title("Total Spending by Category", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.set_xlim(0, cat["Total"].max() * 1.18)
    fig.tight_layout()
    return _save(fig, "02_category_bar.png")


# ── 3. Monthly Trend Line Chart ───────────────────────────────────────────────

def plot_monthly_trend(df: pd.DataFrame):
    monthly = monthly_trend(df)
    fig, ax1 = plt.subplots(figsize=(12, 5))

    ax1.fill_between(monthly["Month"], monthly["Total"],
                     alpha=0.15, color=PALETTE[0])
    ax1.plot(monthly["Month"], monthly["Total"],
             marker="o", color=PALETTE[0], linewidth=2.5, markersize=7, label="Total Spend")
    ax1.set_ylabel("Total Spend (₹)", color=PALETTE[0])
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.bar(monthly["Month"], monthly["Count"],
            alpha=0.3, color=PALETTE[2], label="Transactions")
    ax2.set_ylabel("No. of Transactions", color=PALETTE[2])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    ax1.set_title("Monthly Spending Trend (2024)", pad=15)
    fig.tight_layout()
    return _save(fig, "03_monthly_trend.png")


# ── 4. Quarterly Bar Chart ────────────────────────────────────────────────────

def plot_quarterly(df: pd.DataFrame):
    qt = quarterly_trend(df)
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(qt["Quarter"], qt["Total"], color=PALETTE[:4], edgecolor="white", width=0.5)
    for bar, val in zip(bars, qt["Total"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
                f"₹{val:,.0f}", ha="center", fontsize=10, fontweight="bold", color=TEXT_COLOR)
    ax.set_title("Quarterly Spending Overview", pad=15)
    ax.set_ylabel("Total Spend (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    fig.tight_layout()
    return _save(fig, "04_quarterly.png")


# ── 5. Payment Method Bar ─────────────────────────────────────────────────────

def plot_payment_methods(df: pd.DataFrame):
    pm = payment_method_analysis(df)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Bar
    ax = axes[0]
    ax.bar(pm["Payment_Method"], pm["Total"], color=PALETTE[:len(pm)], edgecolor="white")
    ax.set_title("Spend by Payment Method")
    ax.set_ylabel("Total Amount (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.tick_params(axis="x", rotation=20)

    # Pie
    ax2 = axes[1]
    ax2.pie(pm["Count"], labels=pm["Payment_Method"], autopct="%1.0f%%",
            colors=PALETTE[:len(pm)], startangle=90,
            wedgeprops={"linewidth": 1.5, "edgecolor": "white"})
    ax2.set_title("Transaction Count by Payment Method")

    fig.tight_layout()
    return _save(fig, "05_payment_methods.png")


# ── 6. Weekday Spending Heatmap ───────────────────────────────────────────────

def plot_weekday_bar(df: pd.DataFrame):
    wd = weekday_analysis(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE[3] if row["Day_of_Week"] in ["Saturday","Sunday"] else PALETTE[0]
              for _, row in wd.iterrows()]
    ax.bar(wd["Day_of_Week"], wd["Average"], color=colors, edgecolor="white", width=0.6)
    ax.set_title("Average Spending by Day of Week\n(Red = Weekend)", pad=15)
    ax.set_ylabel("Average Spend (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    fig.tight_layout()
    return _save(fig, "06_weekday_spending.png")


# ── 7. Budget vs Actual ───────────────────────────────────────────────────────

def plot_budget_vs_actual(df: pd.DataFrame):
    bva = budget_vs_actual(df).sort_values("Actual_Avg", ascending=True)
    fig, ax = plt.subplots(figsize=(11, 7))
    x     = range(len(bva))
    width = 0.38
    ax.barh([i + width/2 for i in x], bva["Budget"],    width, label="Budget",    color=PALETTE[0], alpha=0.85)
    ax.barh([i - width/2 for i in x], bva["Actual_Avg"], width, label="Actual",  color=PALETTE[2], alpha=0.85)
    ax.set_yticks(list(x))
    ax.set_yticklabels(bva["Category"])
    ax.set_xlabel("Amount (₹ per month)")
    ax.set_title("Monthly Budget vs Actual Spending", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.legend()
    fig.tight_layout()
    return _save(fig, "07_budget_vs_actual.png")


# ── 8. Category Heatmap (Month × Category) ───────────────────────────────────

def plot_heatmap(df: pd.DataFrame):
    pivot = df.pivot_table(
        index="Month_Num", columns="Category",
        values="Amount", aggfunc="sum", observed=True
    ).fillna(0)
    pivot.index = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot)]
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.5, linecolor="white",
                fmt=".0f", annot=True, annot_kws={"size": 7},
                cbar_kws={"label": "Amount (₹)"})
    ax.set_title("Spending Heatmap: Month × Category", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Month")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return _save(fig, "08_heatmap.png")


# ── 9. Top Subcategories ──────────────────────────────────────────────────────

def plot_top_subcategories(df: pd.DataFrame):
    top = (df.groupby(["Category","Subcategory"], observed=True)["Amount"]
           .sum().reset_index()
           .sort_values("Amount", ascending=False)
           .head(12))
    top["Label"] = top["Category"].astype(str) + " → " + top["Subcategory"]
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(top))]
    ax.barh(top["Label"][::-1], top["Amount"][::-1], color=colors[::-1], edgecolor="white")
    ax.set_title("Top 12 Subcategories by Spend", pad=15)
    ax.set_xlabel("Total Spend (₹)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    fig.tight_layout()
    return _save(fig, "09_top_subcategories.png")


# ── 10. Dashboard (Summary Grid) ─────────────────────────────────────────────

def plot_dashboard(df: pd.DataFrame):
    fig = plt.figure(figsize=(18, 12))
    fig.suptitle("💰  Personal Expense Tracker — 2024 Dashboard",
                 fontsize=18, fontweight="bold", color=TEXT_COLOR, y=0.98)

    # Category pie
    ax1 = fig.add_subplot(3, 3, 1)
    cat = category_summary(df)
    ax1.pie(cat["Total"], labels=cat["Category"], colors=PALETTE[:len(cat)],
            autopct="%1.0f%%", startangle=140,
            wedgeprops={"linewidth":1,"edgecolor":"white"},
            textprops={"fontsize": 7})
    ax1.set_title("Category Split")

    # Monthly trend
    ax2 = fig.add_subplot(3, 3, (2, 3))
    monthly = monthly_trend(df)
    ax2.fill_between(monthly["Month"], monthly["Total"], alpha=0.15, color=PALETTE[0])
    ax2.plot(monthly["Month"], monthly["Total"], marker="o", color=PALETTE[0], linewidth=2)
    ax2.set_title("Monthly Trend")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax2.tick_params(axis="x", rotation=45, labelsize=8)

    # Category bar
    ax3 = fig.add_subplot(3, 3, 4)
    cat_s = category_summary(df).sort_values("Total")
    ax3.barh(cat_s["Category"], cat_s["Total"], color=PALETTE[:len(cat_s)], edgecolor="white")
    ax3.set_title("Spend by Category")
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax3.tick_params(labelsize=8)

    # Payment method
    ax4 = fig.add_subplot(3, 3, 5)
    pm = payment_method_analysis(df)
    ax4.bar(pm["Payment_Method"], pm["Total"], color=PALETTE[:len(pm)], edgecolor="white")
    ax4.set_title("Payment Methods")
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax4.tick_params(axis="x", rotation=20, labelsize=8)

    # Quarterly
    ax5 = fig.add_subplot(3, 3, 6)
    qt = quarterly_trend(df)
    ax5.bar(qt["Quarter"], qt["Total"], color=PALETTE[:4], edgecolor="white")
    ax5.set_title("Quarterly Overview")
    ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))

    # Weekday
    ax6 = fig.add_subplot(3, 3, 7)
    wd = weekday_analysis(df)
    colors_wd = [PALETTE[3] if d in ["Saturday","Sunday"] else PALETTE[0]
                 for d in wd["Day_of_Week"]]
    ax6.bar(wd["Day_of_Week"], wd["Average"], color=colors_wd, edgecolor="white")
    ax6.set_title("Avg Spend by Day")
    ax6.tick_params(axis="x", rotation=30, labelsize=7)

    # Budget vs Actual
    ax7 = fig.add_subplot(3, 3, (8, 9))
    bva = budget_vs_actual(df)
    x   = range(len(bva))
    ax7.bar([i - 0.2 for i in x], bva["Budget"],     0.38, label="Budget", color=PALETTE[0], alpha=0.85)
    ax7.bar([i + 0.2 for i in x], bva["Actual_Avg"], 0.38, label="Actual", color=PALETTE[2], alpha=0.85)
    ax7.set_xticks(list(x))
    ax7.set_xticklabels(bva["Category"], rotation=30, ha="right", fontsize=7)
    ax7.set_title("Budget vs Actual (Monthly Avg)")
    ax7.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax7.legend(fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return _save(fig, "10_dashboard.png")


# ── Run All ───────────────────────────────────────────────────────────────────

def generate_all_charts(df: pd.DataFrame):
    """Generate and save all charts."""
    print("\n📊  Generating all charts...\n")
    plot_category_pie(df)
    plot_category_bar(df)
    plot_monthly_trend(df)
    plot_quarterly(df)
    plot_payment_methods(df)
    plot_weekday_bar(df)
    plot_budget_vs_actual(df)
    plot_heatmap(df)
    plot_top_subcategories(df)
    plot_dashboard(df)
    print("\n🎉  All charts saved to outputs/")


if __name__ == "__main__":
    df = pd.read_csv("data/expenses_clean.csv", parse_dates=["Date"])
    generate_all_charts(df)
