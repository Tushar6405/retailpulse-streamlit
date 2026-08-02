"""
RetailPulse — Interactive Sales Intelligence Dashboard (Streamlit)
--------------------------------------------------------------------
A live, filterable version of the Power BI dashboard, built directly on
top of the same SQL star-schema warehouse (retailpulse.db). Solves the
"no live link" limitation of Power BI's free tier by running entirely
in the browser via Streamlit Cloud.

Run locally:  streamlit run app.py
"""

import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="RetailPulse | Sales Intelligence Dashboard", page_icon="📊", layout="wide")

DB_PATH = Path(__file__).parent / "retailpulse.db"

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .kpi-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
    }
    .kpi-label { font-size: 13px; color: #64748B; font-weight: 600; }
    .kpi-value { font-size: 24px; color: #1E3A8A; font-weight: 700; margin-top: 4px; }
    .insight-box {
        background: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 14px;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

# ---------------------------------------------------------------------------
# Data loading (joins the full star schema into one flat frame, cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            f.order_id, f.quantity, f.unit_price, f.discount_pct,
            f.revenue, f.cost, f.profit, f.sales_channel,
            d.full_date, d.year, d.month_name, d.month_num, d.quarter, d.is_weekend,
            p.product_name, p.category,
            c.customer_segment, c.customer_code,
            r.region_name
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_region r ON f.region_key = r.region_key
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df["full_date"] = pd.to_datetime(df["full_date"])
    return df

df_all = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters (mirrors the synced slicers in the Power BI version)
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

years = sorted(df_all["year"].unique())
regions = sorted(df_all["region_name"].unique())
categories = sorted(df_all["category"].unique())
segments = sorted(df_all["customer_segment"].unique())

sel_years = st.sidebar.multiselect("Year", years, default=years)
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)
sel_categories = st.sidebar.multiselect("Category", categories, default=categories)
sel_segments = st.sidebar.multiselect("Customer Segment", segments, default=segments)

st.sidebar.markdown("---")
st.sidebar.caption("Built with SQLite (star schema) · Pandas · Plotly · Streamlit")
st.sidebar.caption("Same underlying data warehouse as the Power BI version of this project.")

df = df_all[
    df_all["year"].isin(sel_years)
    & df_all["region_name"].isin(sel_regions)
    & df_all["category"].isin(sel_categories)
    & df_all["customer_segment"].isin(sel_segments)
]

if df.empty:
    st.warning("No data matches the current filter selection. Adjust filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
st.title("📊 RetailPulse — Sales Intelligence Dashboard")
st.caption("Live, filterable version of the Power BI report — built on the same SQL star-schema warehouse.")

total_revenue = df["revenue"].sum()
total_profit = df["profit"].sum()
total_orders = df["order_id"].nunique()
total_units = df["quantity"].sum()
aov = total_revenue / total_orders if total_orders else 0
margin_pct = (total_profit / total_revenue * 100) if total_revenue else 0

k1, k2, k3, k4, k5 = st.columns(5)
for col, label, value in zip(
    [k1, k2, k3, k4, k5],
    ["Total Revenue", "Total Profit", "Total Orders", "Avg Order Value", "Profit Margin"],
    [f"₹{total_revenue:,.0f}", f"₹{total_profit:,.0f}", f"{total_orders:,}",
     f"₹{aov:,.0f}", f"{margin_pct:.1f}%"],
):
    col.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                 f'<div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown("")

# ---------------------------------------------------------------------------
# Tabs (mirrors the 4 Power BI report pages)
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Overview", "📦 Product Performance",
    "👥 Customer & Region Insights", "📊 Trends",
])

# ---- TAB 1: Executive Overview ----
with tab1:
    c1, c2 = st.columns([1.3, 1])

    with c1:
        st.subheader("Revenue Trend")
        daily = df.groupby("full_date", as_index=False)["revenue"].sum()
        fig = px.line(daily, x="full_date", y="revenue", labels={"revenue": "Revenue", "full_date": ""})
        fig.update_traces(line_color="#2563EB")
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Revenue by Region")
        region_rev = df.groupby("region_name", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        fig = px.pie(region_rev, names="region_name", values="revenue", hole=0.45,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Revenue by Category")
    cat_rev = df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    fig = px.bar(cat_rev, x="revenue", y="category", orientation="h", color="category",
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(height=320, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

    top_region = region_rev.iloc[0]
    top_cat = cat_rev.iloc[0]
    st.markdown(
        f'<div class="insight-box">💡 <b>{top_region["region_name"]}</b> is the top-performing region '
        f'(₹{top_region["revenue"]:,.0f}), and <b>{top_cat["category"]}</b> is the leading category '
        f'(₹{top_cat["revenue"]:,.0f}).</div>',
        unsafe_allow_html=True,
    )

# ---- TAB 2: Product Performance ----
with tab2:
    prod = df.groupby(["product_name", "category"], as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"),
    )
    prod["margin_pct"] = (prod["profit"] / prod["revenue"] * 100).round(1)
    prod = prod.sort_values("revenue", ascending=False)
    prod.insert(0, "rank", range(1, len(prod) + 1))

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.subheader("Product Rankings")
        st.dataframe(
            prod[["rank", "product_name", "category", "revenue", "margin_pct", "units"]]
            .rename(columns={"product_name": "Product", "category": "Category",
                              "revenue": "Revenue", "margin_pct": "Margin %", "units": "Units Sold"}),
            hide_index=True, use_container_width=True, height=380,
        )

    with c2:
        st.subheader("Revenue vs Margin (bubble size = units sold)")
        fig = px.scatter(
            prod, x="revenue", y="margin_pct", size="units", color="product_name",
            hover_name="product_name", labels={"revenue": "Revenue", "margin_pct": "Profit Margin %"},
            size_max=45,
        )
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Products by Revenue")
    top10 = prod.head(10)
    fig = px.bar(top10, x="revenue", y="product_name", orientation="h", color="margin_pct",
                 color_continuous_scale="Blues", labels={"revenue": "Revenue", "product_name": ""})
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

    lowest_margin = prod.sort_values("margin_pct").iloc[0]
    st.markdown(
        f'<div class="insight-box">💡 <b>{lowest_margin["product_name"]}</b> has the lowest profit margin '
        f'({lowest_margin["margin_pct"]:.1f}%) among top products — worth a pricing review, '
        f'especially if it also carries meaningful revenue share.</div>',
        unsafe_allow_html=True,
    )

# ---- TAB 3: Customer & Region Insights ----
with tab3:
    st.subheader("Revenue: Customer Segment × Region")
    matrix = df.pivot_table(index="customer_segment", columns="region_name", values="revenue", aggfunc="sum", fill_value=0)
    matrix["Total"] = matrix.sum(axis=1)
    matrix.loc["Total"] = matrix.sum()
    st.dataframe(matrix.style.format("₹{:,.0f}"), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Customer Segment")
        seg_rev = df.groupby("customer_segment", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        fig = px.bar(seg_rev, x="revenue", y="customer_segment", orientation="h",
                     color="customer_segment", color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(height=300, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Heatmap: Segment × Region")
        heat_df = df.pivot_table(index="customer_segment", columns="region_name", values="revenue", aggfunc="sum", fill_value=0)
        fig = go.Figure(data=go.Heatmap(
            z=heat_df.values, x=heat_df.columns, y=heat_df.index,
            colorscale="Blues", text=heat_df.values.round(0), texttemplate="%{text:,.0f}",
        ))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

# ---- TAB 4: Trends ----
with tab4:
    st.subheader("Running Total Revenue")
    daily = df.groupby("full_date", as_index=False)["revenue"].sum().sort_values("full_date")
    daily["running_total"] = daily["revenue"].cumsum()
    fig = px.area(daily, x="full_date", y="running_total", labels={"running_total": "Cumulative Revenue", "full_date": ""})
    fig.update_traces(line_color="#2563EB", fillcolor="rgba(37,99,235,0.15)")
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Sales Channel")
        channel_rev = df.groupby("sales_channel", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        fig = px.bar(channel_rev, x="sales_channel", y="revenue", color="sales_channel",
                     color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(height=320, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Weekday vs Weekend")
        wk = df.copy()
        wk["day_type"] = wk["is_weekend"].map({1: "Weekend", 0: "Weekday"})
        wk_rev = wk.groupby("day_type", as_index=False)["revenue"].sum()
        fig = px.pie(wk_rev, names="day_type", values="revenue", hole=0.5,
                     color_discrete_sequence=["#2563EB", "#93C5FD"])
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Month-over-Month Revenue (current filter selection)")
    monthly = df.groupby(["year", "month_num", "month_name"], as_index=False)["revenue"].sum().sort_values(["year", "month_num"])
    monthly["mom_growth_pct"] = monthly["revenue"].pct_change() * 100
    fig = px.bar(monthly, x="month_name", y="revenue", color="year",
                 category_orders={"month_name": MONTH_ORDER}, barmode="group")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("RetailPulse · Built by Tushar Bhadane · SQL star-schema warehouse + Streamlit/Plotly live layer")
