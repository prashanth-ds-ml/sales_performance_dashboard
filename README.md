# Sales_performance_dashboard

Here we work on superstore sales data with SQL and make an insightful dashboard with Streamlit

Dataset_link : https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

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

For collaboration, each task will be tracked with ownership status in our task tracker.
