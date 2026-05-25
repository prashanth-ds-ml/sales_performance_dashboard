-- Portfolio deep-dive queries for documented dashboard findings.
-- These are SQLite-compatible and use the `sales` table built by scripts/create_sqlite_db.py.

-- 1. Executive reconciliation
SELECT
  COUNT(*) AS order_lines,
  COUNT(DISTINCT order_id) AS distinct_orders,
  ROUND(SUM(sales), 2) AS total_sales,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(AVG(discount), 4) AS avg_discount,
  MIN(order_date) AS first_order_date,
  MAX(order_date) AS last_order_date
FROM sales;

-- 2. Category margin profile
SELECT
  category,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(100.0 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS margin_pct,
  ROUND(AVG(discount), 3) AS avg_discount
FROM sales
GROUP BY category
ORDER BY sales DESC;

-- 3. Loss-making states for exception review
SELECT
  state,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(100.0 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS margin_pct,
  ROUND(AVG(discount), 3) AS avg_discount
FROM sales
GROUP BY state
HAVING SUM(profit) < 0
ORDER BY profit ASC;

-- 4. High-sales products with non-positive profit
SELECT
  product_name,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(AVG(discount), 3) AS avg_discount
FROM sales
GROUP BY product_name
HAVING SUM(sales) > 10000
   AND SUM(profit) <= 0
ORDER BY sales DESC;

-- 5. Discount-band profitability
SELECT
  CASE
    WHEN discount = 0 THEN '0%'
    WHEN discount <= 0.10 THEN '0-10%'
    WHEN discount <= 0.20 THEN '10-20%'
    WHEN discount <= 0.40 THEN '20-40%'
    ELSE '40%+'
  END AS discount_band,
  COUNT(*) AS order_lines,
  ROUND(SUM(sales), 2) AS sales,
  ROUND(SUM(profit), 2) AS profit,
  ROUND(100.0 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS margin_pct
FROM sales
GROUP BY discount_band
ORDER BY MIN(discount);

-- 6. Regional shipping duration
SELECT
  region,
  ROUND(AVG(julianday(ship_date) - julianday(order_date)), 2) AS avg_ship_days,
  COUNT(*) AS order_lines
FROM sales
GROUP BY region
ORDER BY avg_ship_days DESC;
