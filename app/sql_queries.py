# app/sql_queries.py
# All queries assume table name: sales (snake_case columns)

PRAGMA_SCHEMA = "PRAGMA table_info(sales);"

HEAD_10 = "SELECT * FROM sales LIMIT 10;"

COUNT_ROWS = "SELECT COUNT(*) AS total_rows FROM sales;"

SPAN_DATES = """
SELECT MIN(order_date) AS start_date,
       MAX(order_date) AS end_date
FROM sales;
"""

# NULL check (per column)
NULL_COUNTS = """
SELECT
  SUM(CASE WHEN row_id IS NULL THEN 1 ELSE 0 END) AS null_row_id,
  SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_id,
  SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS null_order_date,
  SUM(CASE WHEN ship_date IS NULL THEN 1 ELSE 0 END) AS null_ship_date,
  SUM(CASE WHEN ship_mode IS NULL THEN 1 ELSE 0 END) AS null_ship_mode,
  SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
  SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) AS null_customer_name,
  SUM(CASE WHEN segment IS NULL THEN 1 ELSE 0 END) AS null_segment,
  SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) AS null_country,
  SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) AS null_city,
  SUM(CASE WHEN state IS NULL THEN 1 ELSE 0 END) AS null_state,
  SUM(CASE WHEN postal_code IS NULL THEN 1 ELSE 0 END) AS null_postal_code,
  SUM(CASE WHEN region IS NULL THEN 1 ELSE 0 END) AS null_region,
  SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS null_product_id,
  SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) AS null_category,
  SUM(CASE WHEN sub_category IS NULL THEN 1 ELSE 0 END) AS null_sub_category,
  SUM(CASE WHEN product_name IS NULL THEN 1 ELSE 0 END) AS null_product_name,
  SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS null_sales,
  SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS null_quantity,
  SUM(CASE WHEN discount IS NULL THEN 1 ELSE 0 END) AS null_discount,
  SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END) AS null_profit
FROM sales;
"""

# Distinct counts for categoricals
DISTINCT_CATS = """
SELECT
  COUNT(DISTINCT order_id)       AS unique_order_ids,
  COUNT(DISTINCT ship_mode)      AS unique_ship_modes,
  COUNT(DISTINCT customer_id)    AS unique_customer_ids,
  COUNT(DISTINCT customer_name)  AS unique_customer_names,
  COUNT(DISTINCT segment)        AS unique_segments,
  COUNT(DISTINCT country)        AS unique_countries,
  COUNT(DISTINCT city)           AS unique_cities,
  COUNT(DISTINCT state)          AS unique_states,
  COUNT(DISTINCT postal_code)    AS unique_postal_codes,
  COUNT(DISTINCT region)         AS unique_regions,
  COUNT(DISTINCT product_id)     AS unique_product_ids,
  COUNT(DISTINCT product_name)   AS unique_product_names,
  COUNT(DISTINCT category)       AS unique_categories,
  COUNT(DISTINCT sub_category)   AS unique_subcategories
FROM sales;
"""

# Numeric summaries
NUM_SUMMARY_SALES = """
SELECT MIN(sales) AS min_sales, MAX(sales) AS max_sales,
       AVG(sales) AS avg_sales,  printf('%.6f', stdev) AS stddev_sales
FROM (
  SELECT sales, 
         -- SQLite: no STDDEV; approximate via sample stddev using window if needed.
         -- We'll compute stddev in Python if required. Here keep min/max/avg.
         0.0 as stdev
  FROM sales
) t;
"""
# (Recommendation: compute stddev in Python for any metric you display.)

NUM_SUMMARY_TEMPLATE = lambda col: f"""
SELECT MIN({col}) AS min_{col}, MAX({col}) AS max_{col},
       AVG({col}) AS avg_{col}
FROM sales;
"""

# Segment distribution
SEGMENT_DIST = """
SELECT
  segment,
  COUNT(*)                      AS orders,
  ROUND(SUM(sales), 2)          AS sales,
  ROUND(100.0 * COUNT(*) /(SELECT COUNT(*) FROM sales), 2)  AS pct_orders,
  ROUND(100.0 * SUM(sales)/(SELECT SUM(sales) FROM sales), 2) AS pct_sales
FROM sales
GROUP BY segment
ORDER BY sales DESC;
"""

# Category distribution (+profit, margins)
CATEGORY_DIST = """
SELECT
  category,
  COUNT(*)                                    AS orders,
  ROUND(SUM(sales), 2)                        AS sales,
  ROUND(SUM(profit), 2)                       AS profit,
  ROUND(100.0 * SUM(sales) /(SELECT SUM(sales)  FROM sales), 2) AS pct_sales,
  ROUND(100.0 * SUM(profit)/(SELECT SUM(profit) FROM sales), 2) AS pct_profit,
  ROUND(100.0 * SUM(profit) / NULLIF(SUM(sales), 0), 2)         AS margin_pct,
  ROUND(AVG(discount), 2)                      AS avg_discount
FROM sales
GROUP BY category
ORDER BY sales DESC;
"""

# Region performance
REGION_PERF = """
SELECT
  region,
  COUNT(*)                                   AS orders,
  ROUND(SUM(sales), 2)                       AS sales,
  ROUND(SUM(profit), 2)                      AS profit,
  ROUND(100.0 * SUM(sales)/(SELECT SUM(sales) FROM sales), 2)   AS pct_sales,
  ROUND(100.0 * SUM(profit)/(SELECT SUM(profit) FROM sales), 2) AS pct_profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2)            AS margin_pct,
  ROUND(AVG(discount), 2)                    AS avg_discount
FROM sales
GROUP BY region
ORDER BY sales DESC;
"""

# Ship mode
SHIPMODE_PERF = """
SELECT
  ship_mode,
  COUNT(*)                                   AS orders,
  ROUND(SUM(sales), 2)                       AS sales,
  ROUND(SUM(profit), 2)                      AS profit,
  ROUND(100.0 * SUM(sales)/(SELECT SUM(sales) FROM sales), 2)   AS pct_sales,
  ROUND(100.0 * SUM(profit)/(SELECT SUM(profit) FROM sales), 2) AS pct_profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2)            AS margin_pct,
  ROUND(AVG(discount), 2)                    AS avg_discount
FROM sales
GROUP BY ship_mode
ORDER BY sales DESC;
"""

# State leaderboard
STATE_SALES = """
SELECT
  state,
  COUNT(*)                      AS orders,
  ROUND(SUM(sales), 2)          AS sales,
  ROUND(SUM(profit), 2)         AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct,
  ROUND(AVG(discount), 2)       AS avg_discount
FROM sales
GROUP BY state
ORDER BY sales DESC;
"""

STATE_TOP5 = """
SELECT
  state,
  COUNT(*) AS orders,
  ROUND(SUM(sales), 2)  AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct
FROM sales
GROUP BY state
ORDER BY sales DESC
LIMIT 5;
"""

STATE_LOSS = """
SELECT
  state,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(SUM(sales), 2)  AS sales,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct
FROM sales
GROUP BY state
HAVING SUM(profit) < 0
ORDER BY profit ASC;
"""

# Shipping time (days) by region
SHIP_DAYS_BY_REGION = """
SELECT
  region,
  ROUND(AVG(julianday(ship_date) - julianday(order_date)), 2) AS avg_ship_days,
  COUNT(*)           AS orders,
  ROUND(SUM(sales),2)  AS sales,
  ROUND(SUM(profit),2) AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct
FROM sales
GROUP BY region
ORDER BY avg_ship_days;
"""

# Monthly B1/B2/B3/B4
MONTHLY_SALES_PROFIT = """
SELECT
  strftime('%Y-%m', order_date) AS month,
  ROUND(SUM(sales), 2)  AS sales,
  ROUND(SUM(profit), 2) AS profit
FROM sales
GROUP BY month
ORDER BY month;
"""

MOM_REVENUE = """
WITH m AS (
  SELECT strftime('%Y-%m', order_date) AS month,
         SUM(sales) AS sales
  FROM sales
  GROUP BY month
)
SELECT
  month,
  ROUND(sales, 2) AS sales,
  ROUND((sales - LAG(sales) OVER (ORDER BY month))
        / NULLIF(LAG(sales) OVER (ORDER BY month), 0) * 100.0, 2) AS mom_pct
FROM m
ORDER BY month;
"""

MONTHLY_AVG_DISCOUNT = """
SELECT
  strftime('%Y-%m', order_date) AS month,
  ROUND(AVG(discount), 3) AS avg_discount
FROM sales
GROUP BY month
ORDER BY month;
"""

TOP_PRODUCTS_BY_REVENUE = """
SELECT
  product_name,
  COUNT(*)                 AS order_lines,
  ROUND(SUM(sales), 2)     AS sales,
  ROUND(SUM(profit), 2)    AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct,
  ROUND(AVG(discount), 3)  AS avg_discount
FROM sales
GROUP BY product_name
ORDER BY sales DESC
LIMIT 10;
"""

TOP_PRODUCTS_BY_QTY = """
SELECT
  product_name,
  SUM(quantity)            AS qty,
  ROUND(SUM(sales), 2)     AS sales,
  ROUND(SUM(profit), 2)    AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct,
  ROUND(AVG(discount), 3)  AS avg_discount
FROM sales
GROUP BY product_name
ORDER BY qty DESC
LIMIT 10;
"""

HIGH_SALES_LOW_PROFIT = """
SELECT
  product_name,
  ROUND(SUM(sales), 2)   AS sales,
  ROUND(SUM(profit), 2)  AS profit,
  ROUND(AVG(discount),3) AS avg_discount
FROM sales
GROUP BY product_name
HAVING SUM(sales) > 10000 AND SUM(profit) <= 0
ORDER BY sales DESC;
"""

AVG_DISCOUNT_BY_CATEGORY = """
SELECT
  category,
  ROUND(AVG(discount), 3) AS avg_discount,
  ROUND(SUM(sales), 2)    AS sales,
  ROUND(SUM(profit), 2)   AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct
FROM sales
GROUP BY category
ORDER BY avg_discount DESC;
"""

AVG_DISCOUNT_BY_SUBCATEGORY = """
SELECT
  sub_category,
  ROUND(AVG(discount), 3) AS avg_discount,
  ROUND(SUM(sales), 2)    AS sales,
  ROUND(SUM(profit), 2)   AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct
FROM sales
GROUP BY sub_category
ORDER BY avg_discount DESC;
"""

BOTTOM10_BY_PROFIT = """
SELECT
  product_name,
  ROUND(SUM(sales), 2)  AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(AVG(discount),3) AS avg_discount
FROM sales
GROUP BY product_name
ORDER BY profit ASC
LIMIT 10;
"""

SEGMENT_RPM = """
SELECT
  segment,
  COUNT(*)                  AS orders,
  ROUND(SUM(sales), 2)      AS sales,
  ROUND(SUM(profit), 2)     AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct,
  ROUND(100.0 * SUM(sales) /(SELECT SUM(sales)  FROM sales), 2) AS pct_sales,
  ROUND(100.0 * SUM(profit)/(SELECT SUM(profit) FROM sales), 2) AS pct_profit,
  ROUND(AVG(discount), 3)   AS avg_discount
FROM sales
GROUP BY segment
ORDER BY sales DESC;
"""

TOP_CUSTOMERS = """
SELECT
  customer_id,
  customer_name,
  ROUND(SUM(sales), 2)   AS lifetime_sales,
  ROUND(SUM(profit), 2)  AS lifetime_profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct,
  COUNT(*)               AS order_lines
FROM sales
GROUP BY customer_id, customer_name
ORDER BY lifetime_sales DESC
LIMIT 10;
"""

AVG_DISCOUNT_BY_SEGMENT = """
SELECT
  segment,
  ROUND(AVG(discount), 3) AS avg_discount,
  ROUND(SUM(sales), 2)    AS sales,
  ROUND(SUM(profit), 2)   AS profit,
  ROUND(100.0 * SUM(profit)/NULLIF(SUM(sales),0), 2) AS margin_pct
FROM sales
GROUP BY segment
ORDER BY avg_discount DESC;
"""

NEGATIVE_PROFIT_CUSTOMERS = """
SELECT
  customer_id,
  customer_name,
  ROUND(SUM(sales), 2)  AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(AVG(discount),3) AS avg_discount,
  COUNT(*)              AS order_lines
FROM sales
GROUP BY customer_id, customer_name
HAVING SUM(profit) < 0
ORDER BY profit ASC;
"""

CUSTOMER_LIFETIME = """
SELECT
  customer_id,
  customer_name,
  MIN(order_date) AS first_order_date,
  MAX(order_date) AS last_order_date,
  CAST(julianday(MAX(order_date)) - julianday(MIN(order_date)) AS INT) AS tenure_days,
  ROUND(SUM(sales), 2)   AS lifetime_sales,
  ROUND(SUM(profit), 2)  AS lifetime_profit
FROM sales
GROUP BY customer_id, customer_name
ORDER BY lifetime_sales DESC;
"""
