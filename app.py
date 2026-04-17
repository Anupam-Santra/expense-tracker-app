"""
app.py  —  Streamlit Dashboard
-------------------------------
Interactive expense tracker dashboard.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_generator  import generate_expenses
from src.data_cleaner    import clean_data
from src.analysis        import (
    category_summary, monthly_trend, payment_method_analysis,
    budget_vs_actual, generate_insights, quarterly_trend,
    weekday_analysis, top_subcategories
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Expense Tracker App",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; }
    .metric-label { font-size: 0.85rem; opacity: 0.85; }
    .insight-box {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 0.6rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#667eea","#f093fb","#4facfe","#43e97b","#fa709a",
           "#fee140","#30cfd0","#a18cd1","#fda085","#f5576c"]


# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if os.path.exists("data/expenses_clean.csv"):
        return pd.read_csv("data/expenses_clean.csv", parse_dates=["Date"])
    df = generate_expenses()
    df = clean_data(df)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/expenses_clean.csv", index=False)
    return df


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💰 Expense Tracker")
    st.markdown("---")

    df_all = load_data()

    selected_cats = st.multiselect(
        "Filter by Category",
        options=sorted(df_all["Category"].unique()),
        default=list(df_all["Category"].unique())
    )

    selected_months = st.multiselect(
        "Filter by Month",
        options=list(range(1, 13)),
        format_func=lambda m: df_all[df_all["Month_Num"]==m]["Month"].iloc[0],
        default=list(range(1, 13))
    )

    selected_pm = st.multiselect(
        "Payment Method",
        options=sorted(df_all["Payment_Method"].unique()),
        default=list(df_all["Payment_Method"].unique())
    )

    st.markdown("---")
    st.caption("📊 Data Science Project\nSynthetic Data | 2024")

# ── Filter ────────────────────────────────────────────────────────────────────
df = df_all[
    (df_all["Category"].isin(selected_cats)) &
    (df_all["Month_Num"].isin(selected_months)) &
    (df_all["Payment_Method"].isin(selected_pm))
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("💰 Personal Expense Tracker Dashboard")
st.markdown("**2024 Annual Spending Analysis** · Synthetic Data · Data Science Project")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
total        = df["Amount"].sum()
avg_monthly  = total / max(len(selected_months), 1)
avg_txn      = df["Amount"].mean()
num_txn      = len(df)
overspend    = df["Overspend_Flag"].sum()

for col, label, val in zip(
    [c1, c2, c3, c4, c5],
    ["Total Spend", "Avg Monthly", "Avg Transaction", "Transactions", "Overspend Alerts"],
    [f"₹{total:,.0f}", f"₹{avg_monthly:,.0f}", f"₹{avg_txn:,.0f}", str(num_txn), str(overspend)]
):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val}</div>
        <div class="metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 1: Pie + Monthly Trend ────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Category Split")
    cat = category_summary(df)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(cat["Total"], labels=cat["Category"], autopct="%1.0f%%",
           colors=PALETTE[:len(cat)], startangle=140,
           wedgeprops={"linewidth":1.5,"edgecolor":"white"},
           textprops={"fontsize":8})
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F8F9FA")
    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("📅 Monthly Spending Trend")
    monthly = monthly_trend(df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.fill_between(monthly["Month"], monthly["Total"], alpha=0.15, color=PALETTE[0])
    ax.plot(monthly["Month"], monthly["Total"], marker="o", color=PALETTE[0], linewidth=2.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.tick_params(axis="x", rotation=40)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F8F9FA")
    st.pyplot(fig)
    plt.close(fig)

# ── Row 2: Category Bar + Budget ──────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏷️ Spending by Category")
    cat_s = category_summary(df).sort_values("Total")
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(cat_s["Category"], cat_s["Total"], color=PALETTE[:len(cat_s)], edgecolor="white")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F8F9FA")
    st.pyplot(fig)
    plt.close(fig)

with col4:
    st.subheader("💰 Budget vs Actual")
    bva = budget_vs_actual(df)
    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(bva))
    ax.bar([i-0.2 for i in x], bva["Budget"],     0.38, label="Budget", color=PALETTE[0])
    ax.bar([i+0.2 for i in x], bva["Actual_Avg"], 0.38, label="Actual", color=PALETTE[4])
    ax.set_xticks(list(x))
    ax.set_xticklabels(bva["Category"], rotation=30, ha="right", fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.legend()
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F8F9FA")
    st.pyplot(fig)
    plt.close(fig)

# ── Row 3: Payment Method + Heatmap ──────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("💳 Payment Methods")
    pm = payment_method_analysis(df)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(pm["Payment_Method"], pm["Total"], color=PALETTE[:len(pm)], edgecolor="white")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.tick_params(axis="x", rotation=20)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F8F9FA")
    st.pyplot(fig)
    plt.close(fig)

with col6:
    st.subheader("📅 Weekday Spending Pattern")
    wd = weekday_analysis(df)
    colors_wd = [PALETTE[4] if d in ["Saturday","Sunday"] else PALETTE[0]
                 for d in wd["Day_of_Week"]]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(wd["Day_of_Week"], wd["Average"], color=colors_wd, edgecolor="white")
    ax.tick_params(axis="x", rotation=30)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#F8F9FA")
    st.pyplot(fig)
    plt.close(fig)

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.subheader("🔥 Spending Heatmap: Month × Category")
pivot = df.pivot_table(
    index="Month_Num", columns="Category",
    values="Amount", aggfunc="sum", observed=True
).fillna(0)
pivot.index = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot)]
fig, ax = plt.subplots(figsize=(14, 4))
sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.5,
            fmt=".0f", annot=True, annot_kws={"size":7})
ax.set_facecolor("#F8F9FA")
fig.patch.set_facecolor("#F8F9FA")
st.pyplot(fig)
plt.close(fig)

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💡 Auto-Generated Insights")
for insight in generate_insights(df):
    st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Transaction Data")
show_cols = ["Date","Category","Subcategory","Amount","Payment_Method","Quarter","Overspend_Flag"]
st.dataframe(
    df[show_cols].sort_values("Date", ascending=False).head(100),
    use_container_width=True
)

st.markdown("""
---
<center>
💰 Expense Tracker App · Built with Python, Pandas, Matplotlib & Streamlit ·
Data Science Project for Placements
</center>
""", unsafe_allow_html=True)
