# Amazon Middle Mile Risk Specialist Alignment

This project is a general BI and SQL project, not a freight-risk project. Its value is showing the core analytics workflow required by the role.

## Relevant JD Requirements

| JD Requirement | Project Evidence |
|---|---|
| Write queries and generate reports | Reusable SQL query library in `app/sql_queries.py` |
| Build dashboards for end-user consumption | Streamlit dashboard with KPI cards, filters, visuals, and exports |
| Extract and combine data | CSV-to-SQLite pipeline with cleaned source data and database layer |
| Identify trends | Monthly sales/profit, MoM revenue, discount trend |
| Spot gaps and operational inefficiencies | Loss-making states, high-sales/low-profit products, discount vs profit analysis |
| Data quality control | typed date/numeric fields, normalized columns, documented data checks |
| Stakeholder reporting | exportable CSV tables and business-facing dashboard tabs |

## How To Explain In Interview

Use this positioning:

> I built this as a SQL-first BI dashboard. The dashboard itself is Streamlit, but the analysis layer is reusable SQL. I focused on KPI definitions, data quality, stakeholder filters, and diagnostic views such as loss-making states and high-sales/low-profit products. That maps to the reporting and deep-dive requirements in BI/risk operations roles.
