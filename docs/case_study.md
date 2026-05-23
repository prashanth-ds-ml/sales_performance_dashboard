# Case Study

## Context

The Superstore dataset contains order-line retail transactions with sales, profit, discount, product, geography, customer segment, and shipping fields.

## Objective

Build a dashboard that helps stakeholders monitor performance and identify sales areas that do not translate into profit.

## Approach

1. Cleaned source data and created a SQLite database.
2. Stored reusable SQL queries in `app/sql_queries.py`.
3. Built a Streamlit dashboard with filters for date, segment, region, and category.
4. Used SQL outputs to power KPIs, trend charts, ranking tables, and diagnostic views.

## Business Value

The dashboard helps identify:

- revenue and profit trends,
- strong and weak categories,
- loss-making states,
- high-sales/low-profit products,
- discounting patterns,
- shipping performance differences.

