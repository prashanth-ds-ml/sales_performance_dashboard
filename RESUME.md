# Resume Notes

## Project Title

Superstore Sales Performance Dashboard | SQL, Python, Streamlit, SQLite

## Short Resume Description

Built an interactive BI dashboard using SQL, SQLite, Python, and Streamlit to analyze sales, profit, discounts, products, geography, and shipping performance from transactional retail data.

## Resume Bullets

- Built a SQL-first sales analytics dashboard in Streamlit to monitor revenue, profit, orders, average discount, monthly trends, segment performance, product rankings, and loss-making states.
- Designed a reusable SQLite analytics layer with saved SQL queries, indexed filter columns, and a CSV-to-database pipeline for repeatable dashboard refreshes.
- Implemented dynamic date, segment, region, and category filters using a CTE-based SQL wrapper, allowing one query library to power multiple filter-aware dashboard views.
- Added stakeholder-ready exports for dashboard tables, enabling follow-up analysis outside the web app.
- Deployed the dashboard to Streamlit Cloud with a zero-secrets setup using a local SQLite database and reproducible Python dependencies.

## Interview Talking Points

- **Problem:** Business users need a single view of sales performance, profitability, and operational risk across products, regions, and customer segments.
- **Data model:** Cleaned Superstore transactional data is loaded into a SQLite `sales` table with indexed columns for common BI filters.
- **SQL ownership:** KPIs, trend queries, ranking logic, discount analysis, and loss detection are stored in `app/sql_queries.py` instead of being hidden inside chart code.
- **Dashboard design:** The app separates executive KPIs, time series, segmentation, geography, products, and operations into focused tabs.
- **Tradeoff:** SQLite keeps the project simple and deployable for a portfolio app; DuckDB or a warehouse such as Redshift/BigQuery would be the next step for larger data.

## Amazon BI Alignment

This project maps well to BI Analyst expectations:

- SQL querying and aggregation
- Dashboard development
- KPI definition
- Data cleaning and validation
- Business performance analysis
- Stakeholder-friendly storytelling
- Self-service analytics exports

## GitHub Pin Description

SQL-first Streamlit BI dashboard analyzing sales, profit, discounts, product performance, geography, and shipping trends using SQLite and reusable saved queries.
