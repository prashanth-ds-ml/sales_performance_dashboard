# Sales_performance_dashboard

Here we work on superstore sales data with SQL and make an insightful dashboard with Streamlit

Dataset_link : https://www.kaggle.com/datasets/vivek468/superstore-dataset-final


## 📁 Project Structure

```
sales_performance_dashboard/
│
├── data/
│   ├── Sample - Superstore.csv         # Raw dataset
│   ├── superstore_clean.csv            # Cleaned dataset ready for SQL
│   └── superstore.db                   # (Optional) SQLite database
│
├── notebooks/
│   └── data.ipynb                      # Data cleaning and preparation notebook
│
├── queries/
│   └── sql_eda.sql                     # SQL EDA and profiling queries
│
├── app/
│   └── dashboard.py                    # Streamlit dashboard (to be developed)
│
└── README.md
```


## 📊 Data Preparation & Cleaning (`data.ipynb`)

This project uses a Jupyter notebook (`data.ipynb`) to prepare the Superstore dataset for SQL analysis and dashboarding.  
**Key steps performed:**

1. **Dataset Download & Extraction**
   - Downloaded the Superstore dataset from kaggle using `kagglehub`.
   - Copied the dataset into the `/data` directory.

2. **Data Loading**
   - Loaded the raw CSV (`Sample - Superstore.csv`) into a pandas DataFrame.
   - Handled encoding issues using `latin1`.

3. **Data Cleaning**
   - Stripped whitespace from column names, replaced spaces/dashes with underscores, and converted to lowercase.
   - Removed duplicate rows.
   - Filled missing (NaN) values with empty strings.
   - Stripped leading/trailing whitespace from all string columns.
   - Converted numeric columns to appropriate types.
   - Converted date columns (`order_date`, `ship_date`) to `YYYY-MM-DD` format for SQL compatibility.

4. **Export Cleaned Data**
   - Saved the cleaned DataFrame as `superstore_clean.csv` in the `/data` directory.

5. **Database Loading**
   - Connected to a local MySQL database using `mysql.connector`.
   - Created a `sales` table with appropriate column types.
   - Inserted data in batches for efficiency and reliability.

## 🧮 SQL EDA & Profiling (`queries/sql_eda.sql`)

The [`queries/sql_eda.sql`](queries/sql_eda.sql) file contains a comprehensive set of SQL queries for initial data exploration, validation, and profiling.  
These queries help ensure the data is loaded correctly, is clean, and is ready for deeper analysis and dashboarding.

**Key EDA steps and queries include:**

| Area                        | Example Queries & Insights                                                                                   |
|-----------------------------|-------------------------------------------------------------------------------------------------------------|
| **Database & Table Inspection** | - Use the correct database<br>- Describe the `Sales` table schema<br>- View first 10 records<br>- Count total rows |
| **Time Span & Completeness**    | - Find earliest and latest order dates<br>- Count total records for sanity check                           |
| **Null & Data Quality Checks**  | - Count NULLs in every column<br>- Validate column names and data types using `INFORMATION_SCHEMA`         |
| **Categorical Profiling**       | - List all categorical columns (e.g., `Segment`, `Region`, `Product Name`)<br>- Count distinct values in each categorical column |
| **Numerical Profiling**         | - List all numerical columns<br>- Calculate min, max, avg, stddev for sales, quantity, discount, profit    |
| **Segment & Category Analysis** | - Orders, sales, % contribution by `Segment` and `Category`                                               |
| **Region & State Analysis**     | - Orders, sales, profit, margin, avg discount by `Region` and `State`<br>- Top 5 states by revenue<br>- Loss-making states |
| **Shipping Mode Analysis**      | - Orders, sales, profit, margin, avg discount by `Ship Mode`                                              |

**Sample queries covered:**
- Table schema and row count
- Date range of sales data
- Null counts per column
- Distinct value counts for categorical columns
- Numeric column summaries (min, max, avg, stddev)
- Segment, category, region, state, and ship mode performance breakdowns
- Top and bottom performers (e.g., top 5 states by revenue, loss-making states)

> These queries are designed to be run sequentially for a full data health check and to generate summary tables for your dashboard.


## 🔍 SQL Analysis Plan

This section outlines all the key business questions and analytical tasks we aim to answer using SQL on the Superstore Sales dataset. Each task is categorized for better clarity and mapped to SQL techniques used.

---

### 🗂️ A. Database Setup

- **A1.** Create normalized tables from raw CSV
- **A2.** Insert and clean data into SQLite
- **A3.** Define relationships using foreign keys
- **A4.** Perform initial data validation (nulls, duplicates, types)

---

### 📅 B. Time-Based Sales Analysis

- **B1.** What is the monthly total sales and monthly total profit?
- **B2.** What is the month-over-month (MoM) growth in revenue?
- **B3.** What is the monthly average discount?
- **B4.** Which month had the highest profit?

---

### 🛍️ C. Product-Level Insights

- **C1.** What are the top 10 products by total revenue?
- **C2.** What are the top 10 products by quantity sold?
- **C3.** Which products have high sales but negative or low profit?
- **C4.** What’s the average discount per product category?

---

### 👥 D. Customer & Segment Analysis

- **D1.** What is the total revenue and profit per customer segment?
- **D2.** Who are the top 10 customers by lifetime revenue?
- **D3.** Which segment receives the highest average discount?
- **D4.** Which customers contributed to negative profit?

---

### 🌍 E. Geographic Analysis

- **E1.** What is the total sales by region?
- **E2.** What is the profit margin by region?
- **E3.** What are the top 5 states by revenue?
- **E4.** Which states generated losses (negative profit)?
- **E5.** What is the average shipping time per region?

---

### 🚚 F. Shipping & Operational Metrics

- **F1.** What is the average shipping delay per shipping mode?
- **F2.** What is the revenue and profit by shipping mode?
- **F3.** Which shipping mode is used most frequently?
- **F4.** Are faster shipping modes more profitable?

---

### 🧮 G. Discount & Profitability Insights

- **G1.** Is there a pattern between discount and profit across products?
- **G2.** Which categories give high discounts but low profit?
- **G3.** What is the profit margin per category?

---

### 🧠 H. Advanced (Optional)

- **H1.** Rank all customers by lifetime spend using window functions
- **H2.** Analyze monthly sales trend per product category
- **H3.** Identify returning vs new customers using cohort logic

---

👉 Each SQL query will be documented in the `/queries` folder and linked to the dashboard section it supports.
