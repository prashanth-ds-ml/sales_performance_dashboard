# app/dashboard.py
# Streamlit + SQLite Superstore Dashboard
# Uses ONLY the saved queries from app/sql_queries.py
# Filters are injected by wrapping queries with a filtered CTE.

import os
import sqlite3
from datetime import date
from typing import Dict, List, Tuple

import pandas as pd
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

# import your saved queries
import sql_queries as Q  # make sure this file exists

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

# ───────────────── filter → WHERE + CTE injection ────────────────
def _in_clause(col: str, values: List[str], key: str) -> Tuple[str | None, Dict]:
    if not values:
        return None, {}
    placeholders = ",".join([f":{key}{i}" for i in range(len(values))])
    clause = f"{col} IN ({placeholders})"
    prm = {f"{key}{i}": v for i, v in enumerate(values)}
    return clause, prm

def make_filtered_query(saved_sql: str, where_sql: str) -> str:
    """
    If the saved query references 'FROM sales', inject a CTE:
      WITH filtered_sales AS (SELECT * FROM sales {WHERE})
      <saved_sql with 'FROM sales' replaced by 'FROM filtered_sales'>
    Otherwise, return the saved query unchanged (e.g., PRAGMA).
    """
    if " from sales" in saved_sql.lower():
        # be conservative: replace case-insensitively
        def replace_from_sales(s: str) -> str:
            # replace all common casings
            s = s.replace("FROM sales", "FROM filtered_sales")
            s = s.replace("from sales", "from filtered_sales")
            return s
        prefix = f"WITH filtered_sales AS (SELECT * FROM sales {where_sql})\n"
        return prefix + replace_from_sales(saved_sql)
    else:
        return saved_sql  # e.g., PRAGMA, or queries that don't touch 'sales'

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

# persist selections
st.session_state["date_range"] = date_range
st.session_state["seg_sel"] = seg_sel
st.session_state["reg_sel"] = reg_sel
st.session_state["cat_sel"] = cat_sel

# Build WHERE clause + params (used in the filtered CTE)
where_parts = []
params: Dict = {}

if isinstance(date_range, list) and len(date_range) == 2 and "order_date" in df_all.columns:
    s = pd.to_datetime(date_range[0]).date().isoformat()
    e = pd.to_datetime(date_range[1]).date().isoformat()
    where_parts.append("date(order_date) BETWEEN date(:s) AND date(:e)")
    params |= {"s": s, "e": e}

if "segment" in df_all.columns and seg_sel:
    c, p = _in_clause("segment", seg_sel, "seg"); where_parts += [c]; params |= p
if "region" in df_all.columns and reg_sel:
    c, p = _in_clause("region", reg_sel, "reg"); where_parts += [c]; params |= p
if "category" in df_all.columns and cat_sel:
    c, p = _in_clause("category", cat_sel, "cat"); where_parts += [c]; params |= p

WHERE = "WHERE " + " AND ".join([w for w in where_parts if w]) if where_parts else ""

# ─────────────────────────── Title / KPIs ─────────────────────────
st.title("🛒 Superstore — SQL-backed Dashboard (Saved Queries)")

# KPIs use your saved query pattern: we’ll derive from a simple SUM/AVG query
kpi_sql = f"""
SELECT
  SUM(sales)    AS total_sales,
  SUM(profit)   AS total_profit,
  COUNT(*)      AS total_orders,
  AVG(discount) AS avg_discount
FROM sales
"""
kpis = run_sql(make_filtered_query(kpi_sql, WHERE), params)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"${(kpis['total_sales'][0] or 0):,.0f}" if not kpis.empty else "$0")
c2.metric("Total Profit", f"${(kpis['total_profit'][0] or 0):,.0f}" if not kpis.empty else "$0")
c3.metric("Total Orders", f"{int(kpis['total_orders'][0] or 0):,}" if not kpis.empty else "0")
c4.metric("Avg. Discount", f"{(kpis['avg_discount'][0] or 0):.2%}" if not kpis.empty else "0.00%")

st.markdown("---")

# ────────────────────────── Charts / Tables ───────────────────────
# 1) Monthly Sales & Profit (Q.MONTHLY_SALES_PROFIT)
if hasattr(Q, "MONTHLY_SALES_PROFIT"):
    q1 = make_filtered_query(Q.MONTHLY_SALES_PROFIT, WHERE)
    ts = run_sql(q1, params)
    if not ts.empty:
        # expects columns: month, sales, profit
        if "ym" in ts.columns:
            ts["ym"] = pd.to_datetime(ts["ym"])
            x_col = "ym"
        else:
            # Q.MONTHLY_SALES_PROFIT returns 'month' like 'YYYY-MM'; cast to period-start
            if "month" in ts.columns:
                ts["ym"] = pd.to_datetime(ts["month"] + "-01", errors="coerce")
                x_col = "ym"
            else:
                x_col = ts.columns[0]
        st.subheader("Monthly Sales")
        st.altair_chart(
            alt.Chart(ts).mark_line(point=True).encode(
                x=f"{x_col}:T", y="sales:Q",
                tooltip=[f"{x_col}:T","sales:Q","profit:Q"] if "profit" in ts else [f"{x_col}:T","sales:Q"]
            ).properties(height=300),
            use_container_width=True
        )
        st.download_button("Download monthly (CSV)", ts.to_csv(index=False),
                           "monthly_sales.csv", "text/csv")

# 2) Category distribution (Q.CATEGORY_DIST)
if hasattr(Q, "CATEGORY_DIST"):
    q2 = make_filtered_query(Q.CATEGORY_DIST, WHERE)
    cat = run_sql(q2, params)
    if not cat.empty and "category" in cat.columns:
        st.subheader("Sales by Category")
        st.plotly_chart(px.bar(cat, x="category", y="sales", hover_data=[c for c in ["profit","margin_pct","pct_sales","pct_profit","avg_discount"] if c in cat]),
                        use_container_width=True)
        st.download_button("Download categories (CSV)", cat.to_csv(index=False),
                           "category_sales.csv", "text/csv")

# 3) Top States (Q.STATE_SALES)
if hasattr(Q, "STATE_SALES"):
    q3 = make_filtered_query(Q.STATE_SALES, WHERE)
    states = run_sql(q3, params)
    if not states.empty and "state" in states.columns and "sales" in states.columns:
        st.subheader("Top 10 States by Sales")
        top_states = states.sort_values("sales", ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8,4))
        ax.bar(top_states["state"], top_states["sales"])
        ax.set_xlabel("State"); ax.set_ylabel("Sales")
        ax.set_xticks(range(len(top_states)))
        ax.set_xticklabels(top_states["state"], rotation=45, ha="right")
        st.pyplot(fig)
        st.download_button("Download top states (CSV)", top_states.to_csv(index=False),
                           "top_states.csv", "text/csv")

# 4) Discount vs Profit (raw two-column pull via Q or fallback)
if hasattr(Q, "AVG_DISCOUNT_BY_CATEGORY"):
    # use a lightweight select for scatter
    scatter_sql = "SELECT discount, profit FROM sales"
    dvp = run_sql(make_filtered_query(scatter_sql, WHERE), params)
else:
    dvp = run_sql(make_filtered_query("SELECT discount, profit FROM sales", WHERE), params)

if not dvp.empty and set(["discount","profit"]).issubset(dvp.columns):
    st.subheader("Discount vs Profit")
    scatter = alt.Chart(dvp).mark_circle(opacity=0.5).encode(
        x="discount:Q", y="profit:Q"
    ).interactive().properties(height=300)
    st.altair_chart(scatter, use_container_width=True)
    st.download_button("Download scatter data (CSV)", dvp.to_csv(index=False),
                       "discount_vs_profit.csv", "text/csv")

# ─────────────────────── Sidebar: SQL Runner ──────────────────────
with st.sidebar.expander("Run a saved SQL"):
    saved = {
        "Schema (PRAGMA)": Q.PRAGMA_SCHEMA if hasattr(Q, "PRAGMA_SCHEMA") else "PRAGMA table_info(sales);",
        "Head 10": Q.HEAD_10 if hasattr(Q, "HEAD_10") else "SELECT * FROM sales LIMIT 10;",
        "Distinct categoricals": getattr(Q, "DISTINCT_CATS", None),
        "Monthly Sales & Profit": getattr(Q, "MONTHLY_SALES_PROFIT", None),
        "MoM Revenue": getattr(Q, "MOM_REVENUE", None),
        "Segment RPM": getattr(Q, "SEGMENT_RPM", None),
        "Top Products by Revenue": getattr(Q, "TOP_PRODUCTS_BY_REVENUE", None),
        "Loss-Making States": getattr(Q, "STATE_LOSS", None),
        "Ship Days by Region": getattr(Q, "SHIP_DAYS_BY_REGION", None),
    }
    # drop Nones
    saved = {k:v for k,v in saved.items() if v}

    pick = st.selectbox("Pick a query", list(saved.keys()))
    apply_filters = st.checkbox("Apply current filters", value=True, help="Wrap query with filtered_sales CTE")
    if st.button("Run"):
        chosen_sql = saved[pick]
        sql_to_run = make_filtered_query(chosen_sql, WHERE) if apply_filters else chosen_sql
        res = run_sql(sql_to_run, params if apply_filters else None)
        st.dataframe(res, use_container_width=True)
        st.download_button("Download result (CSV)", res.to_csv(index=False),
                           "query_result.csv", "text/csv")

# ───────────────────────── Footer / Notes ─────────────────────────
st.caption("All analytics powered by saved SQL in app/sql_queries.py • Filters are injected via a CTE for reusability.")
