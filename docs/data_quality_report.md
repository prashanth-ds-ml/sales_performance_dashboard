# Data Quality Report

The project includes a SQLite build script that normalizes column names, coerces date fields, coerces numeric fields, and creates indexes for common dashboard filters.

Planned/expected checks:

| Check | Purpose |
|---|---|
| Missing order dates | Time-series accuracy |
| Missing sales/profit/discount | KPI reliability |
| Invalid numeric fields | Metric calculation accuracy |
| Duplicate order/product rows | Avoid double-counting |
| Missing category/segment/region | Filter completeness |
| Negative-profit products/states | Business issue detection |

Current source files:

- `data/Sample - Superstore.csv`
- `data/superstore_clean.csv`
- `data/superstore.db`

Cleaning/build script:

- `scripts/create_sqlite_db.py`

