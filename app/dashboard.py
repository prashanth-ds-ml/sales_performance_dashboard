# app/dashboard.py
# Streamlit + SQLite Superstore Dashboard
# - Reads ../data/superstore.db (auto-builds from ../data/superstore_clean.csv if DB is missing)
# - Uses SQL-first aggregations for speed
# - Optional: imports app/sql_queries.py for saved queries

import os
import sqlite3
from datetime import date
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt

# ────────────────────────── Page / Paths ──────────────────────────
st.set_page_config(page_title="Superstore — SQL Dashboard", layout="wide")
HERE     = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(HERE, "..", "data"))
DB_PATH  = os.path.join(DATA_DIR, "superstore.db")
CSV_PATH = os.path.join(DATA_DIR, "superstore_clean.csv")

# Optional import of your saved queries (app/sql_queries.py)
# The app will still work if this file isn't present.
try:
    from app import sql_queries as Q
except Exception:
    Q = None

# ───────────────────────── Helper: build DB ───────────────────────
def _ensure_db():
    """If DB is missing but CSV exists, build a minimal DB on the fly."""
    if os.path.exists(DB_PATH):
        return
    if not os.path.exists(CSV_PATH):
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    # normalize columns to snake_case
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
    )

    # coerce dtypes
    for c in ("order_date", "ship_date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ("sales", "quantity", "discount", "profit"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)
        # basic indexes for performance
        for name, col in [
            ("idx_sales_order_date", "order_date"),
            ("idx_sales_segment", "segment"),
            ("idx_sales_region",  "region"),
            ("idx_sales_state",   "state"),
            ("idx_sales_category","category"),
        ]:
            if col in df.columns:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {name} ON sales({col});")

_ensure_db()

# ─────────────────────── DB access helpers ────────────────────────
def _conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(show_spinner=False)
def run_sql(query: str, params: Dict | None = None) -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql_query(query, conn, params=params or {})

@st.cache_data(show_spinner=False)
def load_base_df() -> pd.DataFrame:
    df = run_sql("SELECT * FROM sales")
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["ym"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    if "ship_date" in df.columns:
        df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    return df

# ────────────────────────── Health check ──────────────────────────
if not os.path.exists(DB_PATH):
    st.error(
        "SQLite DB not found and CSV not available to build it.\n\n"
        "Add `data/superstore.db` (recommended) or `data/superstore_clean.csv` to auto-build."
    )
    st.stop()

df_all = load_base_df()
if df_all.empty:
    st.warning("Database loaded but returned 0 rows.")
else:
    st.success(f"DB OK — {len(df_all):,} rows")

# ───────────────────────── Sidebar Filters ────────────────────────
st.sidebar.header("Filters")

# keep initial defaults cached so Reset works
@st.cache_data
def _defaults(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp, List[str], List[str], List[str]]:
    if "order_date" in df and not df["order_date"].isna().all():
        min_d = pd.to_datetime(df["order_date"].min())
        max_d = pd.to_datetime(df["order_date"].max())
    else:
        min_d = max_d = pd.Timestamp(date.today())
    segs = sorted(df["segment"].dropna().unique().tolist()) if "segment" in df else []
    regs = sorted(df["region"].dropna().unique().tolist()) if "region" in df else []
    cats = sorted(df["category"].dropna().unique().tolist()) if "category" in df else []
    return min_d, max_d, segs, regs, cats

d_min, d_max, seg_all, reg_all, cat_all = _defaults(df_all)

reset = st.sidebar.button("Reset filters", type="primary")

if reset:
    st.session_state.pop("date_range", None)
    st.session_state.pop("seg_sel", None)
    st.session_state.pop("reg_sel", None)
    st.session_state.pop("cat_sel", None)

date_range = st.sidebar.date_input(
    "Order date range", 
    value=st.session_state.get("date_range", [d_min, d_max])
)

seg_sel = st.sidebar.multiselect("Segment", options=seg_all,
                                 default=st.session_state.get("seg_sel", seg_all))
reg_sel = st.sidebar.multiselect("Region", options=reg_all,
                                 default=st.session_state.get("reg_sel", reg_all))
cat_sel = st.sidebar.multiselect("Category", options=cat_all,
                                 default=st.session_state.get("cat_sel", cat_all))

# persist current selections
st.session_state["date_range"] = date_range
st.session_state["seg_sel"] = seg_sel
st.session_state["reg_sel"] = reg_sel
st.session_state["cat_sel"] = cat_sel

# Build SQL WHERE clause and params from filters
def _in_clause(col: str, values: List[str], key: str) -> Tuple[str | None, Dict]:
    if not values:
        return None, {}
    placeholders = ",".join([f":{key}{i}" for i in range(len(values))])
    clause = f"{col} IN ({placeholders})"
    prm = {f"{key}{i}": v for i, v in enumerate(values)}
    return clause, prm

where = []
params: Dict = {}

if isinstance(date_range, list) and len(date_range) == 2 and "order_date" in df_all.columns:
    s = pd.to_datetime(date_range[0]).date().isoformat()
    e = pd.to_datetime(date_range[1]).date().isoformat()
    where.append("date(order_date) BETWEEN date(:s) AND date(:e)")
    params |= {"s": s, "e": e}

if "segment" in df_all.columns and seg_sel:
    c, p = _in_clause("segment", seg_sel, "seg"); where += [c]; params |= p
if "region" in df_all.columns and reg_sel:
    c, p = _in_clause("region", reg_sel, "reg"); where += [c]; params |= p
if "category" in df_all.columns and cat_sel:
    c, p = _in_clause("category", cat_sel, "cat"); where += [c]; params |= p

WHERE = ("WHERE " + " AND ".join([w for w in where if w])) if where else ""

# ─────────────────────────── Title / KPIs ─────────────────────────
st.title("🛒 Superstore — SQL-backed Dashboard")

kpis = run_sql(f"""
    SELECT
      SUM(sales)     AS total_sales,
      SUM(profit)    AS total_profit,
      COUNT(*)       AS total_orders,
      AVG(discount)  AS avg_discount
    FROM sales
    {WHERE}
""", params)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"${(kpis['total_sales'][0] or 0):,.0f}" if not kpis.empty else "$0")
c2.metric("Total Profit", f"${(kpis['total_profit'][0] or 0):,.0f}" if not kpis.empty else "$0")
c3.metric("Total Orders", f"{int(kpis['total_orders'][0] or 0):,}" if not kpis.empty else "0")
c4.metric("Avg. Discount", f"{(kpis['avg_discount'][0] or 0):.2%}" if not kpis.empty else "0.00%")

st.markdown("---")

# ────────────────────────── Charts / Tables ───────────────────────
# Monthly Sales (Altair)
ts = run_sql(f"""
    SELECT strftime('%Y-%m-01', order_date) AS ym,
           SUM(sales)  AS sales,
           SUM(profit) AS profit
    FROM sales
    {WHERE}
    GROUP BY ym
    ORDER BY ym
""", params)
if not ts.empty:
    ts["ym"] = pd.to_datetime(ts["ym"])
    st.subheader("Monthly Sales")
    st.altair_chart(
        alt.Chart(ts).mark_line(point=True).encode(
            x="ym:T", y="sales:Q", tooltip=["ym:T","sales:Q","profit:Q"]
        ).properties(height=300),
        use_container_width=True
    )
    st.download_button("Download monthly (CSV)", ts.to_csv(index=False),
                       "monthly_sales.csv", "text/csv")

# Category Performance (Plotly)
cat = run_sql(f"""
    SELECT category, ROUND(SUM(sales),2) AS sales, ROUND(SUM(profit),2) AS profit
    FROM sales
    {WHERE}
    GROUP BY category
    ORDER BY sales DESC
""", params)
if not cat.empty:
    st.subheader("Sales by Category")
    st.plotly_chart(px.bar(cat, x="category", y="sales", hover_data=["profit"]),
                    use_container_width=True)
    st.download_button("Download categories (CSV)", cat.to_csv(index=False),
                       "category_sales.csv", "text/csv")

# Top 10 States (Matplotlib)
states = run_sql(f"""
    SELECT state, ROUND(SUM(sales),2) AS sales
    FROM sales
    {WHERE}
    GROUP BY state
    ORDER BY sales DESC
    LIMIT 10
""", params)
if not states.empty:
    st.subheader("Top 10 States by Sales")
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(states["state"], states["sales"])
    ax.set_xlabel("State"); ax.set_ylabel("Sales")
    ax.set_xticks(range(len(states))); ax.set_xticklabels(states["state"], rotation=45, ha="right")
    st.pyplot(fig)
    st.download_button("Download top states (CSV)", states.to_csv(index=False),
                       "top_states.csv", "text/csv")

# Discount vs Profit (Altair)
dvp = run_sql(f"SELECT discount, profit FROM sales {WHERE}", params)
if not dvp.empty:
    st.subheader("Discount vs Profit")
    scatter = alt.Chart(dvp).mark_circle(opacity=0.5).encode(
        x="discount:Q", y="profit:Q"
    ).interactive().properties(height=300)
    st.altair_chart(scatter, use_container_width=True)
    st.download_button("Download scatter data (CSV)", dvp.to_csv(index=False),
                       "discount_vs_profit.csv", "text/csv")

# ─────────────────────── Sidebar: SQL Runner ──────────────────────
with st.sidebar.expander("Run a saved SQL"):
    if Q is None:
        st.info("Add `app/sql_queries.py` for a library of saved queries.")
    else:
        options = {
            "Schema (PRAGMA)": Q.PRAGMA_SCHEMA,
            "Head 10": Q.HEAD_10,
            "Distinct categoricals": Q.DISTINCT_CATS,
            "Monthly Sales & Profit": Q.MONTHLY_SALES_PROFIT,
            "MoM Revenue": Q.MOM_REVENUE,
            "Segment RPM": Q.SEGMENT_RPM,
            "Top Products by Revenue": Q.TOP_PRODUCTS_BY_REVENUE,
            "Loss-Making States": Q.STATE_LOSS,
            "Ship Days by Region": Q.SHIP_DAYS_BY_REGION,
        }
        pick = st.selectbox("Pick a query", list(options.keys()))
        if st.button("Run"):
            out = run_sql(options[pick])
            st.dataframe(out, use_container_width=True)
            st.download_button("Download result (CSV)", out.to_csv(index=False),
                               "query_result.csv", "text/csv")

# ───────────────────────── Footer / Notes ─────────────────────────
st.caption("SQLite + SQL aggregations | Viz: Altair / Plotly / Matplotlib | Streamlit cache enabled.")
