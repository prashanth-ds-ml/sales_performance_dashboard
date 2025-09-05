# app/dashboard.py
# Streamlit + SQLite Superstore Dashboard (Saved-Queries Driven, WITH-safe wrapper)

import os, sqlite3
from datetime import date
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt

import sql_queries as Q   # <- lives beside this file

st.set_page_config(page_title="Superstore — SQL Dashboard", layout="wide")
HERE     = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(HERE, "..", "data"))
DB_PATH  = os.path.join(DATA_DIR, "superstore.db")
CSV_PATH = os.path.join(DATA_DIR, "superstore_clean.csv")

# ─────────────────────────── Build DB if needed ───────────────────────────
def _ensure_db():
    if os.path.exists(DB_PATH) or not os.path.exists(CSV_PATH):
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"[^\w]+", "_", regex=True)
    for c in ("order_date", "ship_date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ("sales", "quantity", "discount", "profit"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)
        for name, col in [
            ("idx_sales_order_date","order_date"),
            ("idx_sales_segment","segment"),
            ("idx_sales_region","region"),
            ("idx_sales_state","state"),
            ("idx_sales_category","category"),
        ]:
            if col in df.columns:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {name} ON sales({col});")
_ensure_db()

def _conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(show_spinner=False)
def run_sql(q: str, params: Dict | None = None) -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql_query(q, conn, params=params or {})

@st.cache_data(show_spinner=False)
def base_df() -> pd.DataFrame:
    df = run_sql("SELECT * FROM sales")
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["ym"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    if "ship_date" in df.columns:
        df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    return df

# ───────────────────── Filter builder + WITH-safe injector ─────────────────────
def _in_clause(col: str, values: List[str], key: str):
    if not values:
        return None, {}
    ph = ",".join([f":{key}{i}" for i in range(len(values))])
    clause = f"{col} IN ({ph})"
    prm = {f"{key}{i}": v for i, v in enumerate(values)}
    return clause, prm

def make_filtered_query(saved_sql: str, where_sql: str) -> str:
    """
    Inject a filtered CTE that works for:
      • plain SELECT ... FROM sales ...
      • WITH ... queries that reference sales inside (we chain our CTE first)
    Only injects when the query actually references 'FROM sales'.
    """
    if not saved_sql:
        return saved_sql
    sql = saved_sql.strip()
    # Only if it references the base table
    if " from sales" not in sql.lower():
        return sql

    # Replace all 'FROM sales' with 'FROM filtered_sales' (simple case-insensitive handling)
    replaced = (
        sql.replace("FROM sales", "FROM filtered_sales")
           .replace("from sales", "from filtered_sales")
    )

    cte = f"filtered_sales AS (SELECT * FROM sales {where_sql})"

    # If the query already starts with WITH, chain ours
    if replaced.lower().startswith("with "):
        after_with = replaced[4:].lstrip()  # drop 'WITH' + spaces
        return f"WITH {cte},\n{after_with}"

    # Otherwise, prepend our CTE alone
    return f"WITH {cte}\n{replaced}"

# ───────────────────────────── Health & filters ─────────────────────────────
if not os.path.exists(DB_PATH):
    st.error("No DB found and no CSV to build it. Add `data/superstore.db` or `data/superstore_clean.csv`.")
    st.stop()

df = base_df()
if df.empty:
    st.warning("Database loaded but returned 0 rows."); st.stop()
else:
    st.success(f"DB OK — {len(df):,} rows")

st.sidebar.header("Filters")

@st.cache_data
def _defaults(_df: pd.DataFrame):
    if "order_date" in _df and not _df["order_date"].isna().all():
        mn, mx = pd.to_datetime(_df["order_date"].min()), pd.to_datetime(_df["order_date"].max())
    else:
        mn = mx = pd.Timestamp(date.today())
    segs = sorted(_df["segment"].dropna().unique().tolist()) if "segment" in _df else []
    regs = sorted(_df["region"].dropna().unique().tolist()) if "region" in _df else []
    cats = sorted(_df["category"].dropna().unique().tolist()) if "category" in _df else []
    return mn, mx, segs, regs, cats

d_min, d_max, seg_all, reg_all, cat_all = _defaults(df)

if st.sidebar.button("Reset filters", type="primary"):
    for k in ("date_range","seg_sel","reg_sel","cat_sel"):
        st.session_state.pop(k, None)

date_range = st.sidebar.date_input("Order date range", value=st.session_state.get("date_range", [d_min, d_max]))
seg_sel = st.sidebar.multiselect("Segment", seg_all, default=st.session_state.get("seg_sel", seg_all))
reg_sel = st.sidebar.multiselect("Region", reg_all, default=st.session_state.get("reg_sel", reg_all))
cat_sel = st.sidebar.multiselect("Category", cat_all, default=st.session_state.get("cat_sel", cat_all))

st.session_state["date_range"] = date_range
st.session_state["seg_sel"] = seg_sel
st.session_state["reg_sel"] = reg_sel
st.session_state["cat_sel"] = cat_sel

where_parts, params = [], {}
if isinstance(date_range, list) and len(date_range) == 2 and "order_date" in df.columns:
    s = pd.to_datetime(date_range[0]).date().isoformat()
    e = pd.to_datetime(date_range[1]).date().isoformat()
    where_parts.append("date(order_date) BETWEEN date(:s) AND date(:e)")
    params |= {"s": s, "e": e}
if seg_sel:
    c, p = _in_clause("segment", seg_sel, "seg"); where_parts += [c]; params |= p
if reg_sel:
    c, p = _in_clause("region", reg_sel, "reg"); where_parts += [c]; params |= p
if cat_sel:
    c, p = _in_clause("category", cat_sel, "cat"); where_parts += [c]; params |= p

WHERE = "WHERE " + " AND ".join([w for w in where_parts if w]) if where_parts else ""

# ───────────────────────────── KPIs ─────────────────────────────
st.title("🛒 Superstore — SQL Dashboard (Saved Queries)")

kpi_sql = """
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

# ───────────────────────────── Tabs (Visuals) ─────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Time Series", "Segments & Categories", "Geography", "Products", "Shipping & Discounts"
])

with tab1:
    # Monthly Sales & Profit
    if hasattr(Q, "MONTHLY_SALES_PROFIT"):
        ts = run_sql(make_filtered_query(Q.MONTHLY_SALES_PROFIT, WHERE), params)
        if not ts.empty:
            if "month" in ts.columns:
                ts["ym"] = pd.to_datetime(ts["month"] + "-01", errors="coerce")
                xcol = "ym"
            elif "ym" in ts.columns:
                ts["ym"] = pd.to_datetime(ts["ym"]); xcol = "ym"
            else:
                xcol = ts.columns[0]
            st.subheader("Monthly Sales")
            st.altair_chart(
                alt.Chart(ts).mark_line(point=True).encode(
                    x=f"{xcol}:T", y="sales:Q",
                    tooltip=[f"{xcol}:T","sales:Q","profit:Q"] if "profit" in ts else [f"{xcol}:T","sales:Q"]
                ).properties(height=300),
                use_container_width=True
            )
            st.download_button("Download (CSV)", ts.to_csv(index=False), "monthly_sales.csv", "text/csv")

    # MoM Revenue (%)
    if hasattr(Q, "MOM_REVENUE"):
        try:
            mom = run_sql(make_filtered_query(Q.MOM_REVENUE, WHERE), params)
            if not mom.empty and "month" in mom.columns and "mom_pct" in mom.columns:
                mom["ym"] = pd.to_datetime(mom["month"] + "-01", errors="coerce")
                st.subheader("Month-over-Month % (Revenue)")
                st.altair_chart(
                    alt.Chart(mom).mark_line(point=True).encode(
                        x="ym:T", y="mom_pct:Q", tooltip=["month","sales","mom_pct"]
                    ).properties(height=260),
                    use_container_width=True
                )
        except Exception:
            st.info("MoM chart unavailable right now (query error handled).")

with tab2:
    colsA = st.columns(2)

    if hasattr(Q, "SEGMENT_RPM"):
        seg = run_sql(make_filtered_query(Q.SEGMENT_RPM, WHERE), params)
        if not seg.empty and "segment" in seg.columns:
            with colsA[0]:
                st.subheader("Segment Performance")
                st.plotly_chart(
                    px.bar(seg, x="segment", y="sales",
                           hover_data=[c for c in ["profit","margin_pct","pct_sales","pct_profit","avg_discount"] if c in seg]),
                    use_container_width=True
                )
                st.dataframe(seg, use_container_width=True)

    if hasattr(Q, "CATEGORY_DIST"):
        cat = run_sql(make_filtered_query(Q.CATEGORY_DIST, WHERE), params)
        if not cat.empty and "category" in cat.columns:
            with colsA[1]:
                st.subheader("Category Performance")
                st.plotly_chart(
                    px.bar(cat, x="category", y="sales",
                           hover_data=[c for c in ["profit","margin_pct","pct_sales","pct_profit","avg_discount"] if c in cat]),
                    use_container_width=True
                )
                st.dataframe(cat, use_container_width=True)

with tab3:
    colsB = st.columns(2)

    if hasattr(Q, "REGION_PERF"):
        reg = run_sql(make_filtered_query(Q.REGION_PERF, WHERE), params)
        if not reg.empty and "region" in reg.columns:
            with colsB[0]:
                st.subheader("Region Performance")
                st.plotly_chart(
                    px.bar(reg, x="region", y="sales",
                           hover_data=[c for c in ["profit","margin_pct","pct_sales","pct_profit","avg_discount"] if c in reg]),
                    use_container_width=True
                )
                st.dataframe(reg, use_container_width=True)

    if hasattr(Q, "STATE_SALES"):
        states = run_sql(make_filtered_query(Q.STATE_SALES, WHERE), params)
        if not states.empty and {"state","sales"}.issubset(states.columns):
            with colsB[1]:
                st.subheader("Top 10 States by Sales")
                top_states = states.sort_values("sales", ascending=False).head(10)
                fig, ax = plt.subplots(figsize=(8,4))
                ax.bar(top_states["state"], top_states["sales"])
                ax.set_xlabel("State"); ax.set_ylabel("Sales")
                ax.set_xticks(range(len(top_states)))
                ax.set_xticklabels(top_states["state"], rotation=45, ha="right")
                st.pyplot(fig)
                st.dataframe(top_states, use_container_width=True)

    if hasattr(Q, "STATE_LOSS"):
        loss = run_sql(make_filtered_query(Q.STATE_LOSS, WHERE), params)
        if not loss.empty:
            st.subheader("Loss-Making States")
            st.dataframe(loss, use_container_width=True)

with tab4:
    colsC = st.columns(2)

    if hasattr(Q, "TOP_PRODUCTS_BY_REVENUE"):
        tpr = run_sql(make_filtered_query(Q.TOP_PRODUCTS_BY_REVENUE, WHERE), params)
        if not tpr.empty and "product_name" in tpr.columns:
            with colsC[0]:
                st.subheader("Top Products by Revenue")
                st.plotly_chart(
                    px.bar(tpr, x="product_name", y="sales",
                           hover_data=[c for c in ["profit","margin_pct","avg_discount","order_lines"] if c in tpr])
                    .update_layout(xaxis_tickangle=-45),
                    use_container_width=True
                )
                st.dataframe(tpr, use_container_width=True)

    if hasattr(Q, "TOP_PRODUCTS_BY_QTY"):
        tpq = run_sql(make_filtered_query(Q.TOP_PRODUCTS_BY_QTY, WHERE), params)
        if not tpq.empty and "product_name" in tpq.columns:
            with colsC[1]:
                st.subheader("Top Products by Quantity")
                st.plotly_chart(
                    px.bar(tpq, x="product_name", y="qty",
                           hover_data=[c for c in ["sales","profit","margin_pct","avg_discount"] if c in tpq])
                    .update_layout(xaxis_tickangle=-45),
                    use_container_width=True
                )
                st.dataframe(tpq, use_container_width=True)

    if hasattr(Q, "HIGH_SALES_LOW_PROFIT"):
        hslp = run_sql(make_filtered_query(Q.HIGH_SALES_LOW_PROFIT, WHERE), params)
        if not hslp.empty:
            st.subheader("High Sales but ≤ 0 Profit")
            st.dataframe(hslp, use_container_width=True)

with tab5:
    colsD = st.columns(2)

    if hasattr(Q, "SHIP_DAYS_BY_REGION"):
        ship = run_sql(make_filtered_query(Q.SHIP_DAYS_BY_REGION, WHERE), params)
        if not ship.empty and "avg_ship_days" in ship.columns:
            with colsD[0]:
                st.subheader("Avg Ship Days by Region")
                st.plotly_chart(
                    px.bar(ship, x="region", y="avg_ship_days",
                           hover_data=[c for c in ["orders","sales","profit","margin_pct"] if c in ship]),
                    use_container_width=True
                )
                st.dataframe(ship, use_container_width=True)

    if hasattr(Q, "MONTHLY_AVG_DISCOUNT"):
        mad = run_sql(make_filtered_query(Q.MONTHLY_AVG_DISCOUNT, WHERE), params)
        if not mad.empty and "month" in mad.columns:
            with colsD[1]:
                mad["ym"] = pd.to_datetime(mad["month"] + "-01", errors="coerce")
                st.subheader("Monthly Avg. Discount")
                st.altair_chart(
                    alt.Chart(mad).mark_line(point=True).encode(
                        x="ym:T", y="avg_discount:Q", tooltip=["month","avg_discount"]
                    ).properties(height=260),
                    use_container_width=True
                )
                st.dataframe(mad, use_container_width=True)

    dvp = run_sql(make_filtered_query("SELECT discount, profit FROM sales", WHERE), params)
    if not dvp.empty and {"discount","profit"}.issubset(dvp.columns):
        st.subheader("Discount vs Profit")
        scatter = alt.Chart(dvp).mark_circle(opacity=0.5).encode(x="discount:Q", y="profit:Q").interactive().properties(height=300)
        st.altair_chart(scatter, use_container_width=True)

# ───────────────────────────── Sidebar: SQL Runner ─────────────────────────────
with st.sidebar.expander("Run a saved SQL"):
    saved = {
        "Schema (PRAGMA)": getattr(Q, "PRAGMA_SCHEMA", "PRAGMA table_info(sales);"),
        "Head 10": getattr(Q, "HEAD_10", "SELECT * FROM sales LIMIT 10;"),
        "Distinct categoricals": getattr(Q, "DISTINCT_CATS", None),
        "Monthly Sales & Profit": getattr(Q, "MONTHLY_SALES_PROFIT", None),
        "MoM Revenue": getattr(Q, "MOM_REVENUE", None),
        "Segment RPM": getattr(Q, "SEGMENT_RPM", None),
        "Top Products by Revenue": getattr(Q, "TOP_PRODUCTS_BY_REVENUE", None),
        "Top Products by Qty": getattr(Q, "TOP_PRODUCTS_BY_QTY", None),
        "Loss-Making States": getattr(Q, "STATE_LOSS", None),
        "Ship Days by Region": getattr(Q, "SHIP_DAYS_BY_REGION", None),
        "Monthly Avg Discount": getattr(Q, "MONTHLY_AVG_DISCOUNT", None),
    }
    saved = {k:v for k,v in saved.items() if v}
    pick = st.selectbox("Pick a query", list(saved.keys()))
    if st.button("Run"):
        out = run_sql(make_filtered_query(saved[pick], WHERE), params)
        st.dataframe(out, use_container_width=True)
        st.download_button("Download result (CSV)", out.to_csv(index=False), "query_result.csv", "text/csv")

st.caption("All visuals powered by saved SQL in app/sql_queries.py. Filters are applied via a CTE (WITH-safe).")
