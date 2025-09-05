# Superstore Sales Performance Dashboard (SQL + Streamlit + SQLite)

Interactive sales analytics on the classic **Superstore** dataset.  
Backend is **pure SQL on SQLite**, frontend is **Streamlit** with Altair/Plotly/Matplotlib.

- **Dataset**: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

---

##  What’s inside

- **SQLite-first pipeline** — build `superstore.db` from the cleaned CSV.
- **Saved SQL library** (`app/sql_queries.py`) — one place for all analysis queries.
- **Filter-aware dashboard** — sidebar filters (date, segment, region, category) are injected into saved queries via a **CTE wrapper** (no query duplication).
- **Zero-secrets deploy** — works on Streamlit Cloud without env vars.

---

##  Project Structure

````
sales\_performance\_dashboard/
│
├── app/
│   ├── dashboard.py          # Streamlit app (uses saved queries only)
│   └── sql\_queries.py        # All SQL used by the app (SQLite syntax)
│
├── scripts/
│   └── create\_sqlite\_db.py   # One-off script: CSV → SQLite database
│
├── data/
│   ├── Sample - Superstore.csv   # Raw dataset (optional)
│   ├── superstore\_clean.csv      # Cleaned dataset (used to build DB)
│   └── superstore.db             # SQLite DB (recommended to commit)
│
├── queries/
│   └── sql\_eda.sql           # Original EDA/profiling (MySQL-style; kept for reference)
│
├── .streamlit/
│   └── config.toml           # (optional) theme/server config
│
├── requirements.txt
├── runtime.txt               # (optional) pin Python for Cloud
└── README.md

````

---

##  Quickstart

### 1) Build the SQLite DB (from cleaned CSV)

```bash
python scripts/create_sqlite_db.py
# creates data/superstore.db
```

> The script normalizes column names, coerces types, and builds helpful indexes.

### 2) Run the dashboard locally

```bash
streamlit run app/dashboard.py
```

Open the URL printed in the terminal.

---

##  Deploy to Streamlit Cloud (public)

1. Push this repo (including `data/superstore.db` **or** `data/superstore_clean.csv`).
2. In Streamlit Cloud: **New app** → select repo/branch → main file: `app/dashboard.py`.
3. Deploy.

   * If `superstore.db` is present → instant startup.
   * If only `superstore_clean.csv` is present → the app auto-builds the DB on first run.

**Recommended pinned versions** (already in `requirements.txt`):

```
streamlit
pandas
numpy
altair
plotly
matplotlib
```

**Optional**:

* `runtime.txt` → `python-3.11.9`
* `.streamlit/config.toml` for theme:

  ```toml
  [server]
  headless = true
  runOnSave = true

  [theme]
  base = "dark"
  ```

---

##  How the dashboard works

* All charts/tables are driven by **saved SQL** in `app/sql_queries.py` (e.g., `MONTHLY_SALES_PROFIT`, `SEGMENT_RPM`, `REGION_PERF`, …).
* Sidebar filters build a `WHERE` clause and the app injects it with a **safe CTE wrapper**:

  ```sql
  WITH filtered_sales AS (
    SELECT * FROM sales
    WHERE date(order_date) BETWEEN :s AND :e
      AND segment IN (...)
      AND region  IN (...)
      AND category IN (...)
  )
  -- Your saved query runs with 'FROM sales' rewritten to 'FROM filtered_sales'
  ```
* This keeps queries reusable and filter-aware without editing each SQL.

---

##  What you’ll see in the app

* **KPIs**: Total Sales, Profit, Orders, Avg Discount
* **Time Series**: Monthly Sales & Profit, optional MoM %
* **Segments & Categories**: performance bars + tables
* **Geography**: Region performance, Top States, Loss-making states
* **Products**: Top by revenue/quantity, High sales but ≤0 profit
* **Shipping & Discounts**: Avg ship days by region, monthly avg discount, discount↔profit scatter

Each table comes with a **Download CSV** button.

---

##  Data prep (source of truth)

* Clean the raw CSV in `notebooks/data.ipynb` (or your preferred process).
  Typical steps:

  * normalize headers → snake\_case
  * trim strings, fix types
  * parse `order_date`, `ship_date` to `YYYY-MM-DD`
  * export **`data/superstore_clean.csv`**
* Build the DB with `scripts/create_sqlite_db.py`.

> We keep `queries/sql_eda.sql` (MySQL-style) for reference, but the app uses the **SQLite** equivalents in `app/sql_queries.py`.

---

##  Troubleshooting

* **“DB not found”**
  Ensure either `data/superstore.db` (recommended) or `data/superstore_clean.csv` (auto-build) is present.
* **Path issues on Cloud**
  Paths in `dashboard.py` are relative to the file: `../data/superstore.db`.
* **Window functions**
  The MoM query uses `LAG()`. Streamlit Cloud’s SQLite supports it; if your env doesn’t, replace with a self-join version.
* **Module conflicts**
  Don’t keep another `app/app.py` that imports MySQL secrets. Keep the Streamlit app at `app/dashboard.py` and SQL at `app/sql_queries.py`.

---

##  Extending the app

* Add/modify queries in `app/sql_queries.py` and reference them in `dashboard.py`.
* Create new tabs/sections with your queries (the filter wrapper will apply automatically).
* For heavy workloads, consider **pre-aggregated** tables or switching to **DuckDB**.

---

##  Contributing

PRs welcome! Please:

1. Keep SQL in `app/sql_queries.py` (SQLite syntax).
2. Add visuals in `app/dashboard.py` using the CTE wrapper.
3. Pin any new Python deps in `requirements.txt`.

---

