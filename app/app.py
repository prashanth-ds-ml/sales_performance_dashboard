import streamlit as st
import pandas as pd
import mysql.connector
from contextlib import closing

st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

# -----------------------
# DB connection (same lib as your loader)
# -----------------------
@st.cache_resource
def get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=True,
    )

@st.cache_data(ttl=300)
def read_df(sql: str, params: tuple | None = None) -> pd.DataFrame:
    with closing(get_conn().cursor(dictionary=True)) as cur:
        cur.execute(sql, params or ())
        rows = cur.fetchall()
    return pd.DataFrame(rows)

# -----------------------
# Sidebar filters (basic)
# -----------------------
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start date", value=None)
end_date   = st.sidebar.date_input("End date",   value=None)

# Build WHERE safely (optional filters)
where = "WHERE 1=1"
params: list = []
if start_date:
    where += " AND `Order Date` >= %s"
    params.append(start_date.isoformat())
if end_date:
    where += " AND `Order Date` <= %s"
    params.append(end_date.isoformat())

# NOTE: If your server is case-sensitive and the real table is `sales`,
# use `sales` below OR create a view: CREATE VIEW Sales AS SELECT * FROM sales;

# -----------------------
# KPIs
# -----------------------
kpi_sql = f"""
SELECT 
  ROUND(SUM(Sales),2)  AS total_sales,
  ROUND(SUM(Profit),2) AS total_profit,
  ROUND(100*SUM(Profit)/NULLIF(SUM(Sales),0),2) AS margin_pct,
  COUNT(DISTINCT `Order ID`) AS orders,
  MIN(`Order Date`) AS start_date,
  MAX(`Order Date`) AS end_date
FROM Sales
{where}
"""
kpi = read_df(kpi_sql, tuple(params))
ts   = kpi.iloc[0]

st.title("📈 Superstore Sales — Basic Dashboard")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total Sales", f"${ts.total_sales:,.2f}")
c2.metric("Total Profit", f"${ts.total_profit:,.2f}")
c3.metric("Margin %", f"{ts.margin_pct:.2f}%")
c4.metric("Orders", int(ts.orders))
c5.metric("Date Range", f"{ts.start_date} → {ts.end_date}")

st.divider()

# -----------------------
# Monthly Sales & Profit (B1)
# -----------------------
monthly_sql = f"""
SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS month,
       ROUND(SUM(Sales),2)  AS sales,
       ROUND(SUM(Profit),2) AS profit
FROM Sales
{where}
GROUP BY month
ORDER BY month
"""
monthly = read_df(monthly_sql, tuple(params))
st.subheader("Monthly Sales & Profit")
if not monthly.empty:
    st.line_chart(
        monthly.set_index("month")[["sales","profit"]],
        height=300
    )
else:
    st.info("No data for the selected date range.")

# -----------------------
# Segment performance (D1-lite)
# -----------------------
seg_sql = f"""
SELECT Segment,
       COUNT(*) AS orders,
       ROUND(SUM(Sales),2) AS sales,
       ROUND(SUM(Profit),2) AS profit,
       ROUND(100 * SUM(Profit)/NULLIF(SUM(Sales),0), 2) AS margin_pct
FROM Sales
{where}
GROUP BY Segment
ORDER BY sales DESC
"""
seg = read_df(seg_sql, tuple(params))
colA, colB = st.columns(2)
with colA:
    st.subheader("Sales by Segment")
    if not seg.empty:
        st.bar_chart(seg.set_index("Segment")["sales"], height=300)
    else:
        st.info("No data.")
with colB:
    st.subheader("Margin % by Segment")
    if not seg.empty:
        st.bar_chart(seg.set_index("Segment")["margin_pct"], height=300)
    else:
        st.info("No data.")

st.divider()

# -----------------------
# Top 5 States by Sales (E3)
# -----------------------
top_states_sql = f"""
SELECT State, ROUND(SUM(Sales),2) AS sales
FROM Sales
{where}
GROUP BY State
ORDER BY sales DESC
LIMIT 5
"""
top_states = read_df(top_states_sql, tuple(params))
st.subheader("Top 5 States by Sales")
if not top_states.empty:
    st.bar_chart(top_states.set_index("State")["sales"], height=300)
else:
    st.info("No data.")
