
-- ========== --
-- 8 Aug 2025 --
-- ========== --

-- `use` command helps us in using the required database
use super_store_sales;

-- View schema of the 'Sales' table
DESCRIBE Sales;

-- View first 10 records to get a sense of the data
SELECT * FROM Sales LIMIT 10;

-- Total Number of rows
select count(*) as total_records from Sales; 

-- ===================================================================================
-- 🗓️ Query: Determine the Time Span of Sales Data
-- -----------------------------------------------------------------------------------
-- 🎯 Objective:
--     Identify the earliest and latest order dates in the dataset to understand
--     the full time range covered by the sales data.
--
-- 🧠 Why this matters:
--     - Helps define the analysis period for reports or dashboards
--     - Ensures no gaps exist in the historical or recent data
--     - Useful for analyzing trends, seasonality, and YOY growth
--
-- 🛠️ How the Query Works:
--     - The MIN() function returns the smallest value in a column, which for dates
--       means the earliest date.
--     - The MAX() function returns the largest value, or the most recent date.
--     - We apply these functions to the `Order Date` column from the `Sales` table.
--
-- 📊 Example Use Cases:
--     - Filtering dashboard visuals by date range
--     - Time-based aggregations (monthly sales, quarterly profit, etc.)
--     - Detecting anomalies like sudden sales drop or missing recent records
-- ===================================================================================

select 
	min(`order Date`) as start_date, 
    max(`order Date`) as end_date 
from 
	Sales;
    
-- ===================================================================================
-- 🔢 Query: Count Total Records in the Sales Table
-- -----------------------------------------------------------------------------------
-- 🎯 Objective:
--     Find out how many rows (i.e., individual sales transactions) are present 
--     in the `Sales` table.
--
-- 🧠 Why this matters:
--     - Acts as a quick sanity check to confirm successful data load
--     - Useful for performance monitoring and benchmarking
--     - Helps in data profiling and completeness analysis
--
-- 🛠️ How the Query Works:
--     - COUNT(*) counts all rows in the table, including those with NULLs
--     - The asterisk (*) tells SQL to count every row, regardless of column values
--
-- 📊 Example Use Cases:
--     - Validate data ingestion from CSV or external sources
--     - Measure dataset growth over time in production systems
-- ===================================================================================

select
	count(*) as total_rows
from
	Sales;
    
-- =============================================================================================
-- 🚨 Query: Check for NULLs in All Columns
-- ---------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Identify the number of NULL (missing) values in each column of the `Sales` table.
--
-- 🧠 Why this matters:
--     - NULLs indicate incomplete data, which can affect analysis and visualizations
--     - Helps prioritize which columns need cleaning, dropping, or imputing
--     - Essential for preparing clean datasets for dashboards or predictive modeling
--
-- 🛠️ How the Query Works:
--     - Uses `SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END)` for each column
--     - Wraps each in a COUNT logic to total how many nulls are present per field
--     - Each alias describes the meaning of the column it refers to
--
-- 📊 Example Use Cases:
--     - Data cleaning before uploading to Power BI / Tableau
--     - Preventing nulls from breaking joins or aggregations
-- =============================================================================================

SELECT
    SUM(CASE WHEN `Row ID` IS NULL THEN 1 ELSE 0 END) AS null_Row_ID,
    SUM(CASE WHEN `Order ID` IS NULL THEN 1 ELSE 0 END) AS null_Order_ID,
    SUM(CASE WHEN `Order Date` IS NULL THEN 1 ELSE 0 END) AS null_Order_Date,
    SUM(CASE WHEN `Ship Date` IS NULL THEN 1 ELSE 0 END) AS null_Ship_Date,
    SUM(CASE WHEN `Ship Mode` IS NULL THEN 1 ELSE 0 END) AS null_Ship_Mode,
    SUM(CASE WHEN `Customer ID` IS NULL THEN 1 ELSE 0 END) AS null_Customer_ID,
    SUM(CASE WHEN `Customer Name` IS NULL THEN 1 ELSE 0 END) AS null_Customer_Name,
    SUM(CASE WHEN `Segment` IS NULL THEN 1 ELSE 0 END) AS null_Segment,
    SUM(CASE WHEN `Country` IS NULL THEN 1 ELSE 0 END) AS null_Country,
    SUM(CASE WHEN `City` IS NULL THEN 1 ELSE 0 END) AS null_City,
    SUM(CASE WHEN `State` IS NULL THEN 1 ELSE 0 END) AS null_State,
    SUM(CASE WHEN `Postal Code` IS NULL THEN 1 ELSE 0 END) AS null_Postal_Code,
    SUM(CASE WHEN `Region` IS NULL THEN 1 ELSE 0 END) AS null_Region,
    SUM(CASE WHEN `Product ID` IS NULL THEN 1 ELSE 0 END) AS null_Product_ID,
    SUM(CASE WHEN `Category` IS NULL THEN 1 ELSE 0 END) AS null_Category,
    SUM(CASE WHEN `Sub-Category` IS NULL THEN 1 ELSE 0 END) AS null_Sub_Category,
    SUM(CASE WHEN `Product Name` IS NULL THEN 1 ELSE 0 END) AS null_Product_Name,
    SUM(CASE WHEN `Sales` IS NULL THEN 1 ELSE 0 END) AS null_Sales,
    SUM(CASE WHEN `Quantity` IS NULL THEN 1 ELSE 0 END) AS null_Quantity,
    SUM(CASE WHEN `Discount` IS NULL THEN 1 ELSE 0 END) AS null_Discount,
    SUM(CASE WHEN `Profit` IS NULL THEN 1 ELSE 0 END) AS null_Profit
FROM
    Sales;


-- ===================================================================================
-- 🧩 Query: Get column names and data types in the 'Sales' table
-- -----------------------------------------------------------------------------------
-- 🎯 Objective:
--     Understand the structure of the Sales table by listing all column names
--     along with their SQL data types.
--
-- 🛠️ How it Works:
--     - INFORMATION_SCHEMA.COLUMNS is a system view that stores metadata 
--       about all tables in the database.
--     - We filter it using TABLE_NAME = 'Sales' to focus only on our table.
--
-- 💡 Pro Tip:
--     Use this to decide which columns are numerical, categorical, or date-based
-- ===================================================================================

select 
	column_name,data_type
from
	information_schema.columns
where
	table_name = 'Sales' and table_schema = 'super_store_sales';
    
-- =================================================================================================
-- 📄 Query: Get Categorical Columns from the `Sales` Table
-- -------------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Automatically retrieve all column names in the `Sales` table that store *categorical/textual*
--     information. These are generally columns with data types like `VARCHAR`, `CHAR`, or `TEXT`.
--
-- 🧠 Why this matters:
--     - Helps in identifying variables to use for grouping, filtering, or aggregation
--     - Useful when building dashboards (filters, legends, dropdowns)
--     - Aids in dynamic query generation for profiling or distinct counts
--
-- 🛠️ How the Query Works:
--     - INFORMATION_SCHEMA.COLUMNS is a built-in system table in MySQL that holds metadata about 
--       all tables and their columns
--     - `TABLE_NAME = 'Sales'` ensures we are querying only the `Sales` table
--     - `TABLE_SCHEMA = 'super_store_sales'` restricts to our current database
--     - `DATA_TYPE IN (...)` filters for columns with textual/categorical types
--
-- 📊 Example Use Cases:
--     - Automatically loop through categorical columns in Python to get distinct values
--     - Filter out non-categorical fields for dashboards or ML encoding
-- =================================================================================================

select column_name
from information_schema.columns
where table_name = 'Sales'
	and table_schema = 'super_store_sales'
    and data_type in ('varchar','char','text');
    
-- =============================================================================================
-- 🔍 Query: Count Distinct Values in Categorical Columns
-- ---------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Get the number of unique entries in each categorical column.
--
-- 🧠 Why this matters:
--     - Helps understand cardinality (how many distinct items exist per column)
--     - Useful for spotting identifiers vs groupable categories
--     - Prepares for encoding, grouping, or aggregating data in reports/dashboards
--
-- 🛠️ How the Query Works:
--     - Uses COUNT(DISTINCT column) to calculate unique values
--     - Each line corresponds to one categorical field
--
-- 📊 Example Use Cases:
--     - Understand product diversity, customer base size, regional spread
--     - Tune dashboard filters or dropdowns for user selection
-- =============================================================================================

SELECT
    COUNT(DISTINCT `Order ID`) AS unique_order_ids,
    COUNT(DISTINCT `Ship Mode`) AS unique_ship_modes,
    COUNT(DISTINCT `Customer ID`) AS unique_customer_ids,
    COUNT(DISTINCT `Customer Name`) AS unique_customer_names,
    COUNT(DISTINCT `Segment`) AS unique_segments,
    COUNT(DISTINCT `Country`) AS unique_countries,
    COUNT(DISTINCT `City`) AS unique_cities,
    COUNT(DISTINCT `State`) AS unique_states,
    COUNT(DISTINCT `Postal Code`) AS unique_postal_codes,
    COUNT(DISTINCT `Region`) AS unique_regions,
    COUNT(DISTINCT `Product ID`) AS unique_product_ids,
    COUNT(DISTINCT `Product Name`) AS unique_product_names,
    COUNT(DISTINCT `Category`) AS unique_categories,
    COUNT(DISTINCT `Sub-Category`) AS unique_subcategories
FROM 
    Sales; 
    
    
-- =================================================================================================
-- 🔢 Query: Get Numerical Columns from the `Sales` Table
-- -------------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Automatically retrieve all numeric columns in the `Sales` table for statistical summaries,
--     aggregations, or trend visualizations.
--
-- 🧠 Why this matters:
--     - Enables programmatic selection of columns for metrics like SUM, AVG, MIN, MAX
--     - Helps in generating summary stats or feeding numeric features into ML models
--     - Reduces human error in hardcoding field names during EDA
--
-- 🛠️ How the Query Works:
--     - Like the previous query, we use `INFORMATION_SCHEMA.COLUMNS` to explore metadata
--     - We filter for numeric data types commonly used in MySQL:
--           `int`, `decimal`, `float`, `double`, `numeric`
--     - Adjust the list depending on your DB engine or custom types
--
-- 📊 Example Use Cases:
--     - Use these in Python to loop over numeric columns and calculate mean/median/std
--     - Automatically generate bar charts, histograms, or scatter plots
-- =================================================================================================

select column_name
from information_schema.columns
where table_name = 'Sales'
	and table_schema = 'super_store_sales'
    and data_type in ('int','decimal');


-- ========== --
-- 9 Aug 2025 --
-- ========== --

-- =====================================================================================================
-- 📊 Query: Numeric Column Summaries – Min, Max, Avg, StdDev
-- -----------------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Calculate basic statistical summaries (min, max, average, standard deviation) for each 
--     numeric column in the Sales dataset to understand the range and distribution of values.
--
-- 🧠 Why this matters:
--     - Useful for detecting outliers (e.g., high discounts or huge profits/losses)
--     - Helps in understanding variability and central tendency of key metrics
--     - Provides sanity check on data integrity (e.g., no negative sales unless refunds are tracked)
--
-- 🛠️ How the Query Works:
--     - `MIN()` and `MAX()` show the range of each metric
--     - `AVG()` calculates the mean value
--     - `STDDEV()` returns standard deviation (amount of variation)
--
-- 📊 Example Use Cases:
--     - Compare regions or categories against overall averages
--     - Identify unusual pricing, discounting, or profitability patterns
--     - Feed summary stats into reports or dashboards
-- =====================================================================================================

-- sales summary

select 
	min(Sales) as min_sales,
    max(Sales) as max_sales,
    avg(Sales) as avg_sales,
    stddev(Sales) as stddev_sales
from Sales;

-- Quantity summary

select 
	min(Quantity) as min_sales,
    max(Quantity) as max_sales,
    avg(Quantity) as avg_sales,
    stddev(Quantity) as stddev_sales
from Sales;

-- Discount summary

select 
	min(Discount) as min_sales,
    max(Discount) as max_sales,
    avg(Discount) as avg_sales,
    stddev(Discount) as stddev_sales
from Sales;

-- Profit Summary

select 
	min(Profit) as min_sales,
    max(Profit) as max_sales,
    avg(Profit) as avg_sales,
    stddev(Profit) as stddev_sales
from Sales;

-- ==========================================================================================
-- 🧩 Query: Segment Distribution (Counts, Sales, and % Contribution)
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Understand how orders and revenue are distributed across customer segments.
--
-- 🧠 Why this matters:
--     - Validates expected mix (e.g., Consumer vs Corporate)
--     - Helps prioritize segment-focused strategies in dashboards
--
-- 🛠️ How it works:
--     - GROUP BY Segment to aggregate rows
--     - COUNT(*) -> number of order lines in each segment
--     - SUM(Sales) -> total revenue per segment
--     - Percent of total is computed by dividing by overall totals via scalar subqueries
--       (keeps logic simple and MySQL-friendly)
-- ==========================================================================================


select 
	Segment,
    count(*) as orders,
    round(sum(Sales),2) as sales,
    -- % of total orders
    round(100 * count(*)/(select count(*) from Sales),2) as pct_orders,
    -- % of total sales
	round(100 * sum(Sales)/(select sum(Sales) from Sales),2) as pct_sales
from sales
group by Segment
order by sales desc;

-- ==========================================================================================
-- 🧩 Query: Category Distribution (Orders, Sales, Profit, % Share, Margin, Avg Discount)
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Understand performance by product Category: volume, revenue, profitability, and mix.
--
-- 🧠 Why this matters:
--     - Validates which categories drive revenue vs. profit
--     - Highlights categories with high discounts but weak margins
--     - Feeds category filter cards and KPI tiles in dashboards
--
-- 🛠️ How it works:
--     - GROUP BY Category to aggregate line items per category
--     - COUNT(*)            → number of order lines (volume proxy)
--     - SUM(Sales)/Profit   → totals by category
--     - % of total          → scalar subqueries divide by overall table totals
--     - Margin %            → (profit / sales) * 100 (NULLIF avoids divide-by-zero)
--     - AVG(Discount)       → average discount behavior by category
-- ==========================================================================================

select 
	category,
    count(*) as orders,
    round(sum(Sales),2) as sales,
    round(sum(Profit),2) as profit,
    round(100 * sum(Sales) / (select sum(Sales) from Sales),2) as pct_sales,
    round(100 * sum(Profit) / (select sum(Profit) from Sales), 2) as pct_profit,
    round(100 * sum(Profit) / nullif(sum(Sales),0),2) as margin_pct,
    round(avg(Discount),2) as avg_discount
from Sales
Group by Category
order by sales desc;

-- ==========================================================================================
-- 🧭 Query: Region Performance (Orders, Sales, Profit, % Shares, Margin %, Avg Discount)
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Evaluate how each Region contributes to volume, revenue, and profitability.
--
-- 🧠 Why this matters:
--     - Identifies high/low performing regions for targeting
--     - Useful for regional bar charts and geo maps
--     - Surfaces margin pressure via discounting behavior
--
-- 🛠️ How it works:
--     - GROUP BY Region aggregates line items to the regional level
--     - COUNT(*)                 → order-line volume proxy
--     - SUM(Sales), SUM(Profit)  → totals by region
--     - % shares                 → divide regional totals by overall totals (scalar subqueries)
--     - Margin %                 → (profit / sales) * 100 (NULLIF prevents divide-by-zero)
--     - AVG(Discount)            → average discount in that region
-- ==========================================================================================

select Region,
	count(*) as orders,
    round(sum(Sales),2) as sales,
    round(sum(Profit),2) as profit,
    round(100 * sum(Sales) / (select sum(Sales) from Sales), 2) as pct_sales,
    round(100 * sum(Profit) / (select sum(Profit) from Sales), 2) as pct_profit,
    round(100 * sum(profit) / nullif(sum(Sales), 0),2) as margin_pct,
    round(avg(Discount), 2) as avg_discount
from Sales
group by Region order by sales desc;

-- ==========================================================================================
-- 🚚 Query: Ship Mode Performance (Orders, Sales, Profit, % Shares, Margin %, Avg Discount)
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Understand how different shipping methods impact sales, profit, and discounting.
--
-- 🧠 Why this matters:
--     - Highlights costlier or less profitable shipping methods
--     - Informs decisions on promotional free-shipping offers
--     - Useful for operational efficiency dashboards
--
-- 🛠️ How it works:
--     - GROUP BY Ship Mode aggregates at the shipping method level
--     - COUNT(*)                 → number of order lines per ship mode
--     - SUM(Sales), SUM(Profit)  → revenue & profit per mode
--     - % shares                 → compares each ship mode to total sales/profit
--     - Margin %                 → profit-to-sales ratio per mode
--     - AVG(Discount)            → average discount offered per mode
-- ==========================================================================================

SELECT
  `Ship Mode`,
  COUNT(*)                                                        AS orders,
  ROUND(SUM(Sales), 2)                                            AS sales,
  ROUND(SUM(Profit), 2)                                           AS profit,
  ROUND(100 * SUM(Sales)  / (SELECT SUM(Sales)  FROM Sales), 2)   AS pct_sales,
  ROUND(100 * SUM(Profit) / (SELECT SUM(Profit) FROM Sales), 2)   AS pct_profit,
  ROUND(100 * SUM(Profit) / NULLIF(SUM(Sales), 0), 2)             AS margin_pct,
  ROUND(AVG(Discount), 2)                                         AS avg_discount
FROM Sales
GROUP BY `Ship Mode`
ORDER BY sales DESC;

-- ==========================================================================================
-- 🗺️ Query: State-Level Sales & Profit Analysis
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Identify top and bottom-performing states in terms of sales, profit, and margin.
--
-- 🧠 Why this matters:
--     - Highlights high-revenue states for targeted marketing
--     - Exposes loss-making regions that may need pricing or cost review
--     - Useful for building choropleth maps in dashboards
--
-- 🛠️ How it works:
--     - GROUP BY State aggregates data for each state
--     - COUNT(*)                 → number of order lines
--     - SUM(Sales), SUM(Profit)  → total revenue & profit per state
--     - Margin %                 → profitability per state
--     - AVG(Discount)            → average discount per state
-- ==========================================================================================

SELECT
  State,
  COUNT(*)                                                        AS orders,
  ROUND(SUM(Sales), 2)                                            AS sales,
  ROUND(SUM(Profit), 2)                                           AS profit,
  ROUND(100 * SUM(Profit) / NULLIF(SUM(Sales), 0), 2)             AS margin_pct,
  ROUND(AVG(Discount), 2)                                         AS avg_discount
FROM Sales
GROUP BY State
ORDER BY sales DESC;

-- ==========================================================================================
-- 🏔️ Query: Top 5 States by Revenue
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Identify the highest revenue-generating states to prioritize sales/marketing efforts.
--
-- 🧠 Why this matters:
--     - Quick shortlist for geo targeting and account focus
--     - Useful for leaderboard cards or bar charts in dashboards
--
-- 🛠️ How it works:
--     - GROUP BY State to aggregate order lines per state
--     - SUM(Sales), SUM(Profit) to compute totals
--     - Margin % = Profit / Sales (NULLIF avoids divide-by-zero)
-- ==========================================================================================

select 
	State,
	count(*) as orders,
    round(sum(Sales), 2) as sales,
    round(sum(Profit), 2) as profit,
    round(100 * sum(Profit) / nullif(sum(Sales), 0),2) as margin_pct
from Sales
group by State order by sales desc limit 5;

-- ==========================================================================================
-- 🧯 Query: Loss-Making States
-- ------------------------------------------------------------------------------------------
-- 🎯 Objective:
--     Surface states where total profit is negative (unprofitable overall).
--
-- 🧠 Why this matters:
--     - Flags pricing/discount/shipping issues by geography
--     - Guides corrective actions (pricing rules, logistics, promotions)
--
-- 🛠️ How it works:
--     - GROUP BY State and SUM(Profit)
--     - HAVING filters to only negative totals
-- ==========================================================================================

select State,
	round(sum(Profit), 2) as profit,
    round(sum(Sales), 2) as sales,
    round(100 * sum(Profit) / nullif(sum(Sales), 0), 2) as margin_pct
from Sales
group by State 
having sum(Profit) < 0
order by profit ASC;
    