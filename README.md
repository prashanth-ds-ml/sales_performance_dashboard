# Superstore Sales Performance Dashboard

SQL-first business intelligence dashboard for analyzing sales, profit, discounting, product performance, geography, and shipping trends from the Superstore dataset.

**Live app:** https://salesperformancedashboard.streamlit.app/

**Dataset:** https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

## Why This Project Matters

This project is built to show BI analyst skills that matter in real business work:

- Turn raw transactional data into a queryable analytics layer with SQLite.
- Write reusable SQL for KPIs, trend analysis, segmentation, loss detection, and product ranking.
- Build an interactive dashboard with date, segment, region, and category filters.
- Create downloadable tables so stakeholders can move from insight to action.
- Keep the app deployable without private credentials or external database setup.

## Business Questions Answered

- How are sales and profit trending month over month?
- Which customer segments, product categories, and regions drive the most revenue?
- Where are high sales failing to convert into profit?
- Which products and states are loss-making?
- How do discounts relate to profitability?
- Are shipping timelines different by region?

## Dashboard Features

- **Executive KPIs:** total sales, total profit, total orders, average discount.
- **Time series:** monthly sales/profit and month-over-month revenue change.
- **Segmentation:** performance by segment and category with margin analysis.
- **Geography:** region performance, top states, and loss-making states.
- **Products:** top products by revenue and quantity, plus high-sales/low-profit items.
- **Operations:** average shipping days and monthly discount trends.
- **Export:** CSV download buttons for analysis outputs.

## Technical Highlights

- **SQLite analytics layer:** `scripts/create_sqlite_db.py` builds `data/superstore.db` from cleaned CSV input.
- **Reusable SQL library:** all dashboard queries live in `app/sql_queries.py`.
- **Filter-aware SQL:** Streamlit sidebar filters are injected through a CTE wrapper, so saved SQL stays reusable.
- **Cloud-friendly deployment:** app works on Streamlit Cloud with committed SQLite data or by rebuilding from CSV.
- **Indexing:** the database build script creates indexes on date, segment, region, state, and category for common dashboard filters.

## Tech Stack

- Python
- SQL / SQLite
- Streamlit
- Pandas
- Altair
- Plotly
- Matplotlib

## Project Structure

```text
sales_performance_dashboard/
├── app/
│   ├── dashboard.py          # Streamlit BI dashboard
│   ├── sql_queries.py        # Reusable SQLite queries
│   └── map.py                # Column mapping reference
├── data/
│   ├── Sample - Superstore.csv
│   ├── superstore_clean.csv
│   └── superstore.db
├── notebooks/
│   └── data.ipynb            # Data cleaning notebook
├── queries/
│   └── sql_eda.sql           # Original SQL EDA reference
├── scripts/
│   └── create_sqlite_db.py   # CSV-to-SQLite build script
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── runtime.txt
```

## Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Build the SQLite database if needed:

```bash
python scripts/create_sqlite_db.py
```

3. Start the dashboard:

```bash
streamlit run app/dashboard.py
```

## Data Pipeline

1. Clean the raw Superstore CSV in `notebooks/data.ipynb`.
2. Export the cleaned file to `data/superstore_clean.csv`.
3. Run `scripts/create_sqlite_db.py`.
4. The script normalizes column names, coerces date and numeric fields, writes the `sales` table, and creates indexes.
5. The Streamlit app reads from `data/superstore.db`.

## SQL Design

The dashboard uses saved SQL queries instead of embedding analysis logic inside chart code. Filters are applied by wrapping saved queries with a `filtered_sales` CTE:

```sql
WITH filtered_sales AS (
  SELECT *
  FROM sales
  WHERE date(order_date) BETWEEN date(:s) AND date(:e)
)
SELECT ...
FROM filtered_sales;
```

This keeps query logic readable, testable, and easy to extend.

## Documentation

- [Business problem](docs/business_problem.md)
- [Data dictionary](docs/data_dictionary.md)
- [Metric definitions](docs/metric_definitions.md)
- [Data quality report](docs/data_quality_report.md)
- [EDA summary](docs/eda_summary.md)
- [Case study](docs/case_study.md)
- [Insights](docs/insights.md)
- [Recommendations](docs/recommendations.md)
- [Weekly review example](outputs/weekly_review/week_01_summary.md)
- [Portfolio deep-dive SQL](queries/portfolio_deep_dive.sql)

## Resume Version

See [RESUME.md](RESUME.md) for resume bullets, interview talking points, and a concise project summary.

