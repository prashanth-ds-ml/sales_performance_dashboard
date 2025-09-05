import os, sqlite3, pandas as pd, numpy as np
import streamlit as st
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import date

# ────────────────────────── paths / config ──────────────────────────
st.set_page_config(page_title="Superstore — SQL Dashboard", layout="wide")
HERE     = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(HERE, "..", "data"))
DB_PATH  = os.path.join(DATA_DIR, "superstore.db")
CSV_PATH = os.path.join(DATA_DIR, "superstore_clean.csv")

# ─────────────────────── helpers: db + csv build ────────────────────
def _ensure_db():
    """If the DB is missing but CSV exists, build a minimal DB on the fly."""
    if os.path.exists(DB_PATH):
        return
    if not os.path.exists(CSV_PATH):
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    # normalize cols
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
    )
    # dtypes
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
            ("idx_sales_region", "region"),
            ("idx_sales_state", "state"),
            ("idx_sales_category", "category"),
        ]:
            if col in df.columns:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {name} ON sales({col});")

_ensure_db()

@st.cache_data(show_spinner=False)
def run_sql(query: str, params: dict | None = None) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        return pd.read_sql_query(query, conn, params=params or {})

@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    df = run_sql("SELECT * FROM sales")
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["ym"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    if "ship_date" in df.columns:
        df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    return df

# ─────────────────────────── health check ───────────────────────────
if not os.path.exists(DB_PATH):
    st.error("SQLite DB not found and CSV not available to build it.\n\n"
             "Make sure `data/superstore.db` exists (or `superstore_clean.csv` to auto-build).")
    st.stop()

df = load_df()
if df.empty:
    st.warning("Database loaded but returned 0 rows.")
else:
    st.success(f"DB OK — {len(df):,} rows")

# ───────────────────────────── sidebar ──────────────────────────────
st.sidebar.header("Filters")
if "order_date" in df.columns and not df["order_date"].isna().all():
    min_d = pd.to_datetime(df["order_date"].min())
    max_d = pd.to_datetime(df["order_date"].max())
    start_d, end_d = st.sidebar.date_input("Order date range", [min_d, max_d])
else:
    start_d = end_d = None

segment_sel = []
if "segment" in df.columns:
    opts = sorted(df["segment"].dropna().unique().tolist())
    segment_sel = st.sidebar.multiselect("Segment", opts, default=opts)

region_sel = []
if "region" in df.columns:
    opts = sorted(df["region"].dropna().unique().tolist())
    region_sel = st.sidebar.multiselect("Region", opts, default=opts)

# build WHERE clause for SQL
where = []
params = {}
if start_d and end_d and "order_date" in df.columns:
    where += ["date(order_date) BETWEEN date(:s) AND date(:e)"]
    params["s"] = pd.to_datetime(start_d).date().isoformat()
    params["e"] = pd.to_datetime(end_d).date().isoformat()

def _in_clause(col: str, values: list[str], key: str):
    if not values:
        return None, {}
    ph = ",".join([f":{key}{i}" for i in range(len(values))])
    clause = f"{col} IN ({ph})"
    prm = {f"{key}{i}": v for i, v in enumerate(values)}
    return clause, prm

if "segment" in df.columns and segment_sel:
    clause, prm = _in_clause("segment", segment_sel, "seg")
    where += [clause]; params |= prm

if "region" in df.columns and region_sel:
    clause, prm = _in_clause("region", region_sel, "reg")
    where += [clause]; params |= prm

WHERE = ("WHERE " + " AND ".join(where)) if where else ""

# ───────────────────────────── layout ───────────────────────────────
st.title("🛒 Superstore — SQL-backed Dashboard")

# KPIs (server-side aggregated)
kpis = run_sql(f"""
    SELECT
      SUM(sales)   AS total_sales,
      SUM(profit)  AS total_profit,
      COUNT(*)     AS total_orders,
      AVG(discount) AS avg_discount
    FROM sales
    {WHERE}
""", params)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"${kpis['total_sales'][0]:,.0f}" if not kpis.empty else "$0")
c2.metric("Total Profit", f"${kpis['total_profit'][0]:,.0f}" if not kpis.empty else "$0")
c3.metric("Total Orders", f"{int(kpis['total_orders'][0]) if not kpis.empty else 0:,}")
c4.metric("Avg. Discount", f"{kpis['avg_discount'][0]:.2%}" if not kpis.empty else "0.00%")

st.markdown("---")

# Monthly sales
ts = run_sql(f"""
    SELECT strftime('%Y-%m-01', order_date) AS ym,
           SUM(sales) AS sales, SUM(profit) AS profit
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

# Category bar
cat = run_sql(f"""
    SELECT category, SUM(sales) AS sales, SUM(profit) AS profit
    FROM sales
    {WHERE}
    GROUP BY category
    ORDER BY sales DESC
""", params)
if not cat.empty:
    st.subheader("Sales by Category")
    st.plotly_chart(px.bar(cat, x="category", y="sales", hover_data=["profit"]),
                    use_container_width=True)

# Top states (matplotlib)
states = run_sql(f"""
    SELECT state, SUM(sales) AS sales
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

# Discount vs Profit (Altair)
dvp = run_sql(f"""
    SELECT discount, profit
    FROM sales
    {WHERE}
""", params)
if not dvp.empty:
    st.subheader("Discount vs Profit")
    scatter = alt.Chart(dvp).mark_circle(opacity=0.5).encode(
        x="discount:Q", y="profit:Q"
    ).interactive().properties(height=300)
    st.altair_chart(scatter, use_container_width=True)

st.caption("SQLite + SQL aggregations; Viz: Altair / Plotly / Matplotlib.")
